"""
DEMIR AI Trading Bot - Volume Profile Layer
Phase 3A: Advanced Market Structure Analysis
Tarih: 31 Ekim 2025

Volume Profile (VPVR - Volume Profile Visible Range):
- PoC (Point of Control): En yüksek volume seviyesi
- VAH (Value Area High): %70 volume'ün üst sınırı
- VAL (Value Area Low): %70 volume'ün alt sınırı
- HVN (High Volume Nodes): Destek/Direnç seviyeleri
- LVN (Low Volume Nodes): Breakout potansiyeli

Kullanım Senaryoları:
1. Price at PoC → Yüksek likidite, reversal beklenir
2. Price at VAH → Resistance zone, short fırsatı
3. Price at VAL → Support zone, long fırsatı
4. Price in LVN → Hızlı hareket beklenir (breakout/breakdown)
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from binance.client import Client
import requests
import os

# Binance API (optional - public data yeterli)
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')

try:
    binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET) if BINANCE_API_KEY else None
except:
    binance_client = None


def get_ohlcv_data(symbol, interval='1h', lookback=100):
    """
    Binance'den OHLCV (fiyat + volume) data çeker
    
    Args:
        symbol (str): BTCUSDT, ETHUSDT, etc.
        interval (str): 1h, 4h, 1d
        lookback (int): Kaç mum geriye gidilecek
    
    Returns:
        pd.DataFrame: [timestamp, open, high, low, close, volume]
    """
    try:
        # Interval mapping
        interval_map = {
            '1h': Client.KLINE_INTERVAL_1HOUR if binance_client else '1h',
            '4h': Client.KLINE_INTERVAL_4HOUR if binance_client else '4h',
            '1d': Client.KLINE_INTERVAL_1DAY if binance_client else '1d'
        }
        
        if binance_client:
            # Authenticated API
            klines = binance_client.futures_klines(
                symbol=symbol,
                interval=interval_map[interval],
                limit=lookback
            )
        else:
            # Public API fallback
            url = f"https://fapi.binance.com/fapi/v1/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': lookback
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                klines = response.json()
            else:
                return None
        
        # Parse data
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # Convert to numeric
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    
    except Exception as e:
        print(f"❌ OHLCV data error: {e}")
        return None


def calculate_volume_profile(symbol, interval='1h', lookback=100, price_bins=50):
    """
    Volume Profile (VPVR) hesaplar
    
    Args:
        symbol (str): BTCUSDT, ETHUSDT
        interval (str): Timeframe (1h, 4h, 1d)
        lookback (int): Kaç mum analiz edilecek
        price_bins (int): Fiyat aralıklarının sayısı (default: 50)
    
    Returns:
        dict: {
            'poc': float,           # Point of Control (en yüksek volume)
            'vah': float,           # Value Area High (%70 volume üst sınır)
            'val': float,           # Value Area Low (%70 volume alt sınır)
            'hvn_zones': list,      # High Volume Nodes (destek/direnç)
            'lvn_zones': list,      # Low Volume Nodes (breakout zones)
            'price_levels': list,   # Tüm fiyat seviyeleri
            'volume_dist': list     # Her fiyat seviyesindeki volume
        }
    """
    
    # 1. OHLCV data çek
    df = get_ohlcv_data(symbol, interval, lookback)
    if df is None or df.empty:
        return None
    
    # 2. Fiyat aralığı belirle
    price_min = df['low'].min()
    price_max = df['high'].max()
    
    # Fiyat binleri oluştur (50 adet)
    price_bins_array = np.linspace(price_min, price_max, price_bins + 1)
    price_levels = (price_bins_array[:-1] + price_bins_array[1:]) / 2  # Orta noktalar
    
    # 3. Her fiyat seviyesinde volume hesapla
    volume_at_price = np.zeros(price_bins)
    
    for idx, row in df.iterrows():
        # Her mum için: open, high, low, close arasındaki volume dağılımı
        candle_range = row['high'] - row['low']
        if candle_range == 0:
            continue
        
        # Volume'ü mum içindeki fiyat seviyelerine dağıt
        for i, price_level in enumerate(price_levels):
            if row['low'] <= price_level <= row['high']:
                # Triangular distribution (mumun ortasına daha fazla volume)
                distance_from_center = abs(price_level - (row['open'] + row['close']) / 2)
                weight = max(0, 1 - (distance_from_center / (candle_range / 2)))
                volume_at_price[i] += row['volume'] * weight
    
    # 4. PoC (Point of Control) - En yüksek volume seviyesi
    poc_index = np.argmax(volume_at_price)
    poc = price_levels[poc_index]
    
    # 5. Value Area (VA) - %70 volume'ün bulunduğu aralık
    total_volume = volume_at_price.sum()
    target_volume = total_volume * 0.70
    
    # PoC'tan başlayarak yukarı/aşağı genişle
    cumulative_volume = volume_at_price[poc_index]
    upper_idx = poc_index
    lower_idx = poc_index
    
    while cumulative_volume < target_volume:
        # Yukarı ve aşağı volume karşılaştır
        upper_volume = volume_at_price[upper_idx + 1] if upper_idx + 1 < len(volume_at_price) else 0
        lower_volume = volume_at_price[lower_idx - 1] if lower_idx - 1 >= 0 else 0
        
        if upper_volume > lower_volume:
            upper_idx += 1
            cumulative_volume += upper_volume
        elif lower_volume > 0:
            lower_idx -= 1
            cumulative_volume += lower_volume
        else:
            break
    
    vah = price_levels[upper_idx]
    val = price_levels[lower_idx]
    
    # 6. High Volume Nodes (HVN) - Volume > %80 of max volume
    hvn_threshold = volume_at_price.max() * 0.80
    hvn_zones = []
    for i, vol in enumerate(volume_at_price):
        if vol >= hvn_threshold:
            hvn_zones.append(price_levels[i])
    
    # 7. Low Volume Nodes (LVN) - Volume < %20 of max volume
    lvn_threshold = volume_at_price.max() * 0.20
    lvn_zones = []
    for i, vol in enumerate(volume_at_price):
        if vol <= lvn_threshold and vol > 0:
            lvn_zones.append(price_levels[i])
    
    return {
        'symbol': symbol,
        'interval': interval,
        'lookback': lookback,
        'poc': round(poc, 2),
        'vah': round(vah, 2),
        'val': round(val, 2),
        'hvn_zones': [round(x, 2) for x in hvn_zones],
        'lvn_zones': [round(x, 2) for x in lvn_zones],
        'price_levels': price_levels.tolist(),
        'volume_dist': volume_at_price.tolist(),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def get_volume_profile_signal(symbol, interval='1h', current_price=None):
    """
    Mevcut fiyata göre volume profile sinyali üretir
    
    Args:
        symbol (str): BTCUSDT, ETHUSDT
        interval (str): Timeframe
        current_price (float): Güncel fiyat (None ise API'den çekilir)
    
    Returns:
        dict: {
            'signal': 'LONG' | 'SHORT' | 'NEUTRAL',
            'strength': 0.0-1.0,
            'zone': 'POC' | 'VAH' | 'VAL' | 'HVN' | 'LVN' | 'OUTSIDE',
            'description': str
        }
    """
    
    vp = calculate_volume_profile(symbol, interval)
    if not vp:
        return None
    
    # Current price al
    if current_price is None:
        try:
            url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                current_price = float(response.json()['price'])
        except:
            return None
    
    # Fiyatın hangi zoneda olduğunu belirle
    poc = vp['poc']
    vah = vp['vah']
    val = vp['val']
    
    # Zone detection
    zone = 'OUTSIDE'
    signal = 'NEUTRAL'
    strength = 0.5
    description = ""
    
    # Price at PoC
    if abs(current_price - poc) / poc < 0.01:  # %1 tolerance
        zone = 'POC'
        signal = 'NEUTRAL'
        strength = 0.5
        description = f"Fiyat PoC seviyesinde ({poc}). Yüksek likidite, reversal beklenir."
    
    # Price at VAH (resistance)
    elif abs(current_price - vah) / vah < 0.01:
        zone = 'VAH'
        signal = 'SHORT'
        strength = 0.7
        description = f"Fiyat VAH seviyesinde ({vah}). Resistance zone, short fırsatı."
    
    # Price at VAL (support)
    elif abs(current_price - val) / val < 0.01:
        zone = 'VAL'
        signal = 'LONG'
        strength = 0.7
        description = f"Fiyat VAL seviyesinde ({val}). Support zone, long fırsatı."
    
    # Price above VAH
    elif current_price > vah:
        zone = 'ABOVE_VAH'
        signal = 'LONG'
        strength = 0.6
        description = f"Fiyat VAH üzerinde ({current_price} > {vah}). Güçlü trend, long devam."
    
    # Price below VAL
    elif current_price < val:
        zone = 'BELOW_VAL'
        signal = 'SHORT'
        strength = 0.6
        description = f"Fiyat VAL altında ({current_price} < {val}). Zayıf trend, short devam."
    
    # Price in Value Area (between VAL and VAH)
    else:
        zone = 'VALUE_AREA'
        signal = 'NEUTRAL'
        strength = 0.4
        description = f"Fiyat Value Area içinde ({val} - {vah}). Konsolidasyon."
    
    # LVN check (breakout potential)
    for lvn in vp['lvn_zones']:
        if abs(current_price - lvn) / current_price < 0.01:
            zone = 'LVN'
            strength = 0.8
            description += f" | LVN zone ({lvn}) - Hızlı hareket beklenir!"
            break
    
    return {
        'symbol': symbol,
        'signal': signal,
        'strength': strength,
        'zone': zone,
        'description': description,
        'current_price': current_price,
        'vp_data': vp,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# Test fonksiyonu
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 DEMIR AI - Volume Profile Layer Test")
    print("=" * 80)
    
    # BTC test
    print("\n📊 Calculating Volume Profile for BTCUSDT...")
    vp = calculate_volume_profile('BTCUSDT', interval='1h', lookback=100)
    
    if vp:
        print(f"\n✅ Volume Profile Results:")
        print(f"   PoC (Point of Control): ${vp['poc']:,.2f}")
        print(f"   VAH (Value Area High):  ${vp['vah']:,.2f}")
        print(f"   VAL (Value Area Low):   ${vp['val']:,.2f}")
        print(f"   HVN Zones: {len(vp['hvn_zones'])} zones")
        print(f"   LVN Zones: {len(vp['lvn_zones'])} zones")
        
        # Signal test
        signal = get_volume_profile_signal('BTCUSDT', interval='1h')
        if signal:
            print(f"\n🎯 Trading Signal:")
            print(f"   Signal: {signal['signal']}")
            print(f"   Strength: {signal['strength']:.2f}")
            print(f"   Zone: {signal['zone']}")
            print(f"   Description: {signal['description']}")
    else:
        print("❌ Volume Profile calculation failed")
    
    print("\n" + "=" * 80)
