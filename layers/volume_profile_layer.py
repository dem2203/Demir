"""
DEMIR AI Trading Bot - Volume Profile Layer (REAL DATA)
Binance API kullanarak GERÇEK hacim profili hesaplar
Tarih: 31 Ekim 2025

ÖZELLİKLER:
✅ Binance'den gerçek OHLCV verisi
✅ Volume dağılımı hesaplama
✅ POC, VAH, VAL, HVN, LVN tespiti
✅ Gerçek destek/direnç seviyeleri
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime

def get_binance_klines(symbol, interval='1h', limit=100):
    """
    Binance'den gerçek OHLCV verisi çeker
    """
    try:
        url = f"https://fapi.binance.com/fapi/v1/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert to numeric
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
        else:
            print(f"❌ Binance API error: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"❌ Binance connection error: {e}")
        return None


def calculate_volume_profile(df, num_bins=20):
    """
    OHLCV verisinden Volume Profile hesaplar
    
    Returns:
        dict: {
            'poc_price': float,
            'vah_price': float,
            'val_price': float,
            'volume_by_price': dict
        }
    """
    
    if df is None or len(df) == 0:
        return None
    
    # Fiyat aralığı
    price_min = df['low'].min()
    price_max = df['high'].max()
    
    # Fiyat bin'leri oluştur
    bins = np.linspace(price_min, price_max, num_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    # Her bin için hacim topla
    volume_by_bin = np.zeros(num_bins)
    
    for idx, row in df.iterrows():
        # Her mum için fiyat aralığındaki bin'lere hacim dağıt
        low, high, volume = row['low'], row['high'], row['volume']
        
        # Bu mumun hangi bin'lere düştüğünü bul
        for i in range(num_bins):
            bin_low = bins[i]
            bin_high = bins[i + 1]
            
            # Overlap kontrolü
            if low <= bin_high and high >= bin_low:
                # Overlap oranına göre hacim dağıt
                overlap_low = max(low, bin_low)
                overlap_high = min(high, bin_high)
                overlap_ratio = (overlap_high - overlap_low) / (high - low) if (high - low) > 0 else 1.0
                
                volume_by_bin[i] += volume * overlap_ratio
    
    # POC (Point of Control) - En yüksek hacimli fiyat
    poc_idx = np.argmax(volume_by_bin)
    poc_price = bin_centers[poc_idx]
    
    # Value Area (toplam hacmin %70'i)
    total_volume = volume_by_bin.sum()
    value_area_volume = total_volume * 0.70
    
    # POC'tan başlayarak value area genişlet
    value_area_bins = [poc_idx]
    current_volume = volume_by_bin[poc_idx]
    
    left_idx = poc_idx - 1
    right_idx = poc_idx + 1
    
    while current_volume < value_area_volume:
        left_vol = volume_by_bin[left_idx] if left_idx >= 0 else 0
        right_vol = volume_by_bin[right_idx] if right_idx < num_bins else 0
        
        if left_vol == 0 and right_vol == 0:
            break
        
        if left_vol >= right_vol and left_idx >= 0:
            value_area_bins.append(left_idx)
            current_volume += left_vol
            left_idx -= 1
        elif right_idx < num_bins:
            value_area_bins.append(right_idx)
            current_volume += right_vol
            right_idx += 1
        else:
            break
    
    # VAH ve VAL
    value_area_bins.sort()
    vah_price = bin_centers[value_area_bins[-1]]  # Value Area High
    val_price = bin_centers[value_area_bins[0]]   # Value Area Low
    
    # HVN (High Volume Node) ve LVN (Low Volume Node)
    volume_threshold_hvn = total_volume / num_bins * 1.5  # 1.5x ortalama
    volume_threshold_lvn = total_volume / num_bins * 0.5  # 0.5x ortalama
    
    hvn_prices = [bin_centers[i] for i in range(num_bins) if volume_by_bin[i] > volume_threshold_hvn]
    lvn_prices = [bin_centers[i] for i in range(num_bins) if volume_by_bin[i] < volume_threshold_lvn]
    
    # Volume by price dict
    volume_by_price = {round(bin_centers[i], 2): round(volume_by_bin[i], 2) for i in range(num_bins)}
    
    return {
        'poc_price': round(poc_price, 2),
        'vah_price': round(vah_price, 2),
        'val_price': round(val_price, 2),
        'hvn_prices': [round(p, 2) for p in hvn_prices],
        'lvn_prices': [round(p, 2) for p in lvn_prices],
        'volume_by_price': volume_by_price,
        'total_volume': round(total_volume, 2)
    }


def get_volume_profile_signal(symbol, interval='1h', lookback=100):
    """
    Volume Profile sinyali üretir (GERÇEK VERİ)
    
    Returns:
        dict: {
            'signal': 'LONG' | 'SHORT' | 'NEUTRAL',
            'zone': 'POC' | 'VAH' | 'VAL' | 'HVN' | 'LVN' | 'UNKNOWN',
            'strength': 0.0-1.0,
            'description': str,
            'available': bool
        }
    """
    
    print(f"\n🔍 Volume Profile: {symbol} {interval} (REAL DATA)")
    
    # Binance'den veri çek
    df = get_binance_klines(symbol, interval, lookback)
    
    if df is None or len(df) == 0:
        print(f"❌ No data available for {symbol}")
        return {
            'signal': 'NEUTRAL',
            'zone': 'UNKNOWN',
            'strength': 0.0,
            'description': f'No volume profile data available [{symbol}]',
            'available': False
        }
    
    # Volume Profile hesapla
    vp = calculate_volume_profile(df)
    
    if vp is None:
        return {
            'signal': 'NEUTRAL',
            'zone': 'UNKNOWN',
            'strength': 0.0,
            'description': 'Volume profile calculation failed',
            'available': False
        }
    
    # Güncel fiyat
    current_price = float(df.iloc[-1]['close'])
    
    # Hangi zone'dayız?
    poc = vp['poc_price']
    vah = vp['vah_price']
    val = vp['val_price']
    
    # Zone belirleme
    price_range = vah - val if (vah - val) > 0 else 1.0
    tolerance = price_range * 0.02  # %2 tolerance
    
    if abs(current_price - poc) < tolerance:
        zone = 'POC'
        strength = 0.9  # POC çok güçlü
        signal = 'NEUTRAL'  # POC'ta bekle
        description = f'Price at POC (${poc:,.2f}) - Strong support/resistance. Wait for breakout direction. [{symbol}][{interval}]'
    
    elif abs(current_price - vah) < tolerance:
        zone = 'VAH'
        strength = 0.8
        signal = 'SHORT'  # VAH = direnç
        description = f'Price at VAH (${vah:,.2f}) - Value Area High. Strong resistance, potential SHORT. [{symbol}][{interval}]'
    
    elif abs(current_price - val) < tolerance:
        zone = 'VAL'
        strength = 0.8
        signal = 'LONG'  # VAL = destek
        description = f'Price at VAL (${val:,.2f}) - Value Area Low. Strong support, potential LONG. [{symbol}][{interval}]'
    
    elif current_price > vah:
        # VAH üstünde - direnç kırıldı
        zone = 'ABOVE_VAH'
        distance = (current_price - vah) / price_range
        strength = min(0.7 + distance * 0.2, 1.0)
        signal = 'LONG'
        description = f'Price above VAH (${vah:,.2f}) - Bullish. Strong LONG signal. [{symbol}][{interval}]'
    
    elif current_price < val:
        # VAL altında - destek kırıldı
        zone = 'BELOW_VAL'
        distance = (val - current_price) / price_range
        strength = min(0.7 + distance * 0.2, 1.0)
        signal = 'SHORT'
        description = f'Price below VAL (${val:,.2f}) - Bearish. Strong SHORT signal. [{symbol}][{interval}]'
    
    else:
        # Value Area içinde
        # HVN veya LVN kontrolü
        is_hvn = any(abs(current_price - hvn) < tolerance for hvn in vp['hvn_prices'])
        is_lvn = any(abs(current_price - lvn) < tolerance for lvn in vp['lvn_prices'])
        
        if is_hvn:
            zone = 'HVN'
            strength = 0.6
            signal = 'NEUTRAL'
            description = f'Price at HVN (${current_price:,.2f}) - High volume consolidation. Neutral. [{symbol}][{interval}]'
        elif is_lvn:
            zone = 'LVN'
            strength = 0.7
            signal = 'LONG'  # LVN'de breakout potansiyeli
            description = f'Price at LVN (${current_price:,.2f}) - Low volume gap. Breakout potential. [{symbol}][{interval}]'
        else:
            zone = 'VALUE_AREA'
            strength = 0.5
            signal = 'NEUTRAL'
            description = f'Price in Value Area (${val:,.2f} - ${vah:,.2f}). Neutral. [{symbol}][{interval}]'
    
    print(f"✅ Zone: {zone}, Signal: {signal}, Strength: {strength:.2f}")
    
    return {
        'signal': signal,
        'zone': zone,
        'strength': round(strength, 2),
        'current_price': round(current_price, 2),
        'poc_price': poc,
        'vah_price': vah,
        'val_price': val,
        'description': description,
        'volume_profile_data': vp,
        'available': True,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# Test
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 Volume Profile Layer (REAL DATA) Test")
    print("=" * 80)
    
    symbols = ['BTCUSDT', 'ETHUSDT']
    
    for symbol in symbols:
        result = get_volume_profile_signal(symbol, '1h', lookback=100)
        
        if result['available']:
            print(f"\n✅ {symbol} Volume Profile:")
            print(f"   Zone: {result['zone']}")
            print(f"   Signal: {result['signal']}")
            print(f"   Strength: {result['strength']}")
            print(f"   Current: ${result['current_price']:,.2f}")
            print(f"   POC: ${result['poc_price']:,.2f}")
            print(f"   VAH: ${result['vah_price']:,.2f}")
            print(f"   VAL: ${result['val_price']:,.2f}")
        else:
            print(f"\n❌ {symbol}: Data unavailable")
    
    print("\n" + "=" * 80)
