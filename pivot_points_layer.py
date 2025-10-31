"""
DEMIR AI Trading Bot - Pivot Points Layer
Phase 3A: Professional Support/Resistance Levels
Tarih: 31 Ekim 2025

Pivot Points - Üç farklı sistem:
1. CLASSIC (Floor Trader Pivots): Basit ortalamalara dayalı
2. CAMARILLA: Önceki günün range'ine dayalı (scalping için ideal)
3. WOODIE: Current candle ağırlıklı

Kullanım:
- R3/S3 → Extreme levels, reversal beklenir
- R2/S2 → Strong levels, take profit
- R1/S1 → Initial targets, trend devam sinyali
- PP → Pivot Point, trend belirleme (price > PP = bullish)
"""

import requests
from datetime import datetime, timedelta
from binance.client import Client
import os

# Binance API (optional)
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')

try:
    binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET) if BINANCE_API_KEY else None
except:
    binance_client = None


def get_previous_candle(symbol, interval='1d'):
    """
    Önceki mumu çeker (pivot hesaplaması için)
    
    Args:
        symbol (str): BTCUSDT, ETHUSDT
        interval (str): 1d (daily pivots), 1h, 4h
    
    Returns:
        dict: {'open': float, 'high': float, 'low': float, 'close': float}
    """
    try:
        if binance_client:
            klines = binance_client.futures_klines(
                symbol=symbol,
                interval=interval,
                limit=2  # Son 2 mum (önceki completed mum gerekli)
            )
        else:
            # Public API
            url = f"https://fapi.binance.com/fapi/v1/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': 2
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                klines = response.json()
            else:
                return None
        
        # Önceki mum (index -2, çünkü -1 current candle)
        prev_candle = klines[-2]
        
        return {
            'open': float(prev_candle[1]),
            'high': float(prev_candle[2]),
            'low': float(prev_candle[3]),
            'close': float(prev_candle[4])
        }
    
    except Exception as e:
        print(f"❌ Previous candle error: {e}")
        return None


def calculate_classic_pivots(high, low, close):
    """
    Classic Floor Trader Pivots
    
    Formulas:
        PP = (High + Low + Close) / 3
        R1 = 2*PP - Low
        R2 = PP + (High - Low)
        R3 = High + 2*(PP - Low)
        S1 = 2*PP - High
        S2 = PP - (High - Low)
        S3 = Low - 2*(High - PP)
    """
    
    pp = (high + low + close) / 3
    
    r1 = 2 * pp - low
    r2 = pp + (high - low)
    r3 = high + 2 * (pp - low)
    
    s1 = 2 * pp - high
    s2 = pp - (high - low)
    s3 = low - 2 * (high - pp)
    
    return {
        'method': 'Classic',
        'pp': round(pp, 2),
        'r1': round(r1, 2),
        'r2': round(r2, 2),
        'r3': round(r3, 2),
        's1': round(s1, 2),
        's2': round(s2, 2),
        's3': round(s3, 2)
    }


def calculate_camarilla_pivots(high, low, close):
    """
    Camarilla Pivots (Scalping için ideal)
    
    Formulas:
        R4 = Close + (High - Low) * 1.1/2
        R3 = Close + (High - Low) * 1.1/4
        R2 = Close + (High - Low) * 1.1/6
        R1 = Close + (High - Low) * 1.1/12
        PP = (High + Low + Close) / 3
        S1 = Close - (High - Low) * 1.1/12
        S2 = Close - (High - Low) * 1.1/6
        S3 = Close - (High - Low) * 1.1/4
        S4 = Close - (High - Low) * 1.1/2
    """
    
    range_val = high - low
    pp = (high + low + close) / 3
    
    r4 = close + (range_val * 1.1 / 2)
    r3 = close + (range_val * 1.1 / 4)
    r2 = close + (range_val * 1.1 / 6)
    r1 = close + (range_val * 1.1 / 12)
    
    s1 = close - (range_val * 1.1 / 12)
    s2 = close - (range_val * 1.1 / 6)
    s3 = close - (range_val * 1.1 / 4)
    s4 = close - (range_val * 1.1 / 2)
    
    return {
        'method': 'Camarilla',
        'pp': round(pp, 2),
        'r1': round(r1, 2),
        'r2': round(r2, 2),
        'r3': round(r3, 2),
        'r4': round(r4, 2),
        's1': round(s1, 2),
        's2': round(s2, 2),
        's3': round(s3, 2),
        's4': round(s4, 2)
    }


def calculate_woodie_pivots(open_price, high, low, close):
    """
    Woodie Pivots (Current candle ağırlıklı)
    
    Formulas:
        PP = (High + Low + 2*Open) / 4
        R1 = 2*PP - Low
        R2 = PP + (High - Low)
        S1 = 2*PP - High
        S2 = PP - (High - Low)
    """
    
    pp = (high + low + 2 * open_price) / 4
    
    r1 = 2 * pp - low
    r2 = pp + (high - low)
    
    s1 = 2 * pp - high
    s2 = pp - (high - low)
    
    return {
        'method': 'Woodie',
        'pp': round(pp, 2),
        'r1': round(r1, 2),
        'r2': round(r2, 2),
        's1': round(s1, 2),
        's2': round(s2, 2)
    }


def calculate_all_pivots(symbol, interval='1d'):
    """
    Tüm pivot sistemlerini hesaplar
    
    Args:
        symbol (str): BTCUSDT, ETHUSDT
        interval (str): 1d (daily), 1h, 4h
    
    Returns:
        dict: {
            'classic': {...},
            'camarilla': {...},
            'woodie': {...},
            'timestamp': str
        }
    """
    
    # Önceki mumu çek
    candle = get_previous_candle(symbol, interval)
    if not candle:
        return None
    
    open_price = candle['open']
    high = candle['high']
    low = candle['low']
    close = candle['close']
    
    # 3 sistemi hesapla
    classic = calculate_classic_pivots(high, low, close)
    camarilla = calculate_camarilla_pivots(high, low, close)
    woodie = calculate_woodie_pivots(open_price, high, low, close)
    
    return {
        'symbol': symbol,
        'interval': interval,
        'classic': classic,
        'camarilla': camarilla,
        'woodie': woodie,
        'previous_candle': {
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2)
        },
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def get_pivot_signal(symbol, interval='1d', current_price=None, method='classic'):
    """
    Mevcut fiyata göre pivot sinyali üretir
    
    Args:
        symbol (str): BTCUSDT, ETHUSDT
        interval (str): Timeframe
        current_price (float): Güncel fiyat
        method (str): 'classic', 'camarilla', 'woodie'
    
    Returns:
        dict: {
            'signal': 'LONG' | 'SHORT' | 'NEUTRAL',
            'strength': 0.0-1.0,
            'zone': 'R3' | 'R2' | 'R1' | 'PP' | 'S1' | 'S2' | 'S3',
            'description': str
        }
    """
    
    pivots = calculate_all_pivots(symbol, interval)
    if not pivots:
        return None
    
    # Current price
    if current_price is None:
        try:
            url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                current_price = float(response.json()['price'])
        except:
            return None
    
    # Seçilen metodu al
    pivot_data = pivots[method]
    pp = pivot_data['pp']
    
    # Zone detection
    signal = 'NEUTRAL'
    strength = 0.5
    zone = 'UNKNOWN'
    description = ""
    
    # R3 zone (extreme resistance)
    if 'r3' in pivot_data and abs(current_price - pivot_data['r3']) / current_price < 0.01:
        zone = 'R3'
        signal = 'SHORT'
        strength = 0.9
        description = f"Fiyat R3 seviyesinde ({pivot_data['r3']}). Extreme resistance - güçlü short sinyali."
    
    # R2 zone
    elif 'r2' in pivot_data and abs(current_price - pivot_data['r2']) / current_price < 0.01:
        zone = 'R2'
        signal = 'SHORT'
        strength = 0.7
        description = f"Fiyat R2 seviyesinde ({pivot_data['r2']}). Strong resistance - take profit."
    
    # R1 zone
    elif 'r1' in pivot_data and abs(current_price - pivot_data['r1']) / current_price < 0.01:
        zone = 'R1'
        signal = 'NEUTRAL'
        strength = 0.6
        description = f"Fiyat R1 seviyesinde ({pivot_data['r1']}). İlk resistance - trend devam edebilir."
    
    # PP zone (pivot point)
    elif abs(current_price - pp) / current_price < 0.01:
        zone = 'PP'
        signal = 'NEUTRAL'
        strength = 0.5
        description = f"Fiyat Pivot Point'te ({pp}). Trend belirleniyor."
    
    # S1 zone
    elif 's1' in pivot_data and abs(current_price - pivot_data['s1']) / current_price < 0.01:
        zone = 'S1'
        signal = 'NEUTRAL'
        strength = 0.6
        description = f"Fiyat S1 seviyesinde ({pivot_data['s1']}). İlk support - trend devam edebilir."
    
    # S2 zone
    elif 's2' in pivot_data and abs(current_price - pivot_data['s2']) / current_price < 0.01:
        zone = 'S2'
        signal = 'LONG'
        strength = 0.7
        description = f"Fiyat S2 seviyesinde ({pivot_data['s2']}). Strong support - long fırsatı."
    
    # S3 zone (extreme support)
    elif 's3' in pivot_data and abs(current_price - pivot_data['s3']) / current_price < 0.01:
        zone = 'S3'
        signal = 'LONG'
        strength = 0.9
        description = f"Fiyat S3 seviyesinde ({pivot_data['s3']}). Extreme support - güçlü long sinyali."
    
    # Price above PP
    elif current_price > pp:
        zone = 'ABOVE_PP'
        signal = 'LONG'
        strength = 0.6
        description = f"Fiyat Pivot Point üzerinde ({current_price} > {pp}). Bullish bias."
    
    # Price below PP
    else:
        zone = 'BELOW_PP'
        signal = 'SHORT'
        strength = 0.6
        description = f"Fiyat Pivot Point altında ({current_price} < {pp}). Bearish bias."
    
    return {
        'symbol': symbol,
        'method': method,
        'signal': signal,
        'strength': strength,
        'zone': zone,
        'description': description,
        'current_price': current_price,
        'pivot_data': pivot_data,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# Test fonksiyonu
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 DEMIR AI - Pivot Points Layer Test")
    print("=" * 80)
    
    # BTC test
    print("\n📍 Calculating Pivot Points for BTCUSDT...")
    pivots = calculate_all_pivots('BTCUSDT', interval='1d')
    
    if pivots:
        print(f"\n✅ CLASSIC Pivots:")
        classic = pivots['classic']
        print(f"   R3: ${classic['r3']:,.2f}")
        print(f"   R2: ${classic['r2']:,.2f}")
        print(f"   R1: ${classic['r1']:,.2f}")
        print(f"   PP: ${classic['pp']:,.2f}")
        print(f"   S1: ${classic['s1']:,.2f}")
        print(f"   S2: ${classic['s2']:,.2f}")
        print(f"   S3: ${classic['s3']:,.2f}")
        
        print(f"\n✅ CAMARILLA Pivots:")
        cam = pivots['camarilla']
        print(f"   R4: ${cam['r4']:,.2f}")
        print(f"   R3: ${cam['r3']:,.2f}")
        print(f"   R2: ${cam['r2']:,.2f}")
        print(f"   R1: ${cam['r1']:,.2f}")
        print(f"   PP: ${cam['pp']:,.2f}")
        print(f"   S1: ${cam['s1']:,.2f}")
        print(f"   S2: ${cam['s2']:,.2f}")
        print(f"   S3: ${cam['s3']:,.2f}")
        print(f"   S4: ${cam['s4']:,.2f}")
        
        # Signal test
        signal = get_pivot_signal('BTCUSDT', interval='1d', method='classic')
        if signal:
            print(f"\n🎯 Trading Signal (Classic):")
            print(f"   Signal: {signal['signal']}")
            print(f"   Strength: {signal['strength']:.2f}")
            print(f"   Zone: {signal['zone']}")
            print(f"   Description: {signal['description']}")
    else:
        print("❌ Pivot calculation failed")
    
    print("\n" + "=" * 80)
