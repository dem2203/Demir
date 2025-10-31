"""
DEMIR AI Trading Bot - Pivot Points Layer FIX
Float conversion issue fixed
Tarih: 31 Ekim 2025
"""

import requests
from datetime import datetime

def get_binance_price(symbol):
    """Binance'den güncel fiyat çek - FLOAT olarak dön"""
    try:
        url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return float(response.json()['price'])  # ✅ FLOAT conversion
    except:
        pass
    return None


def get_previous_candle(symbol, interval='1d'):
    """Önceki mumu çeker (pivot hesaplaması için)"""
    try:
        url = f"https://fapi.binance.com/fapi/v1/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': 2}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            klines = response.json()
            prev_candle = klines[-2]  # Önceki completed mum
            
            return {
                'open': float(prev_candle[1]),
                'high': float(prev_candle[2]),
                'low': float(prev_candle[3]),
                'close': float(prev_candle[4])
            }
    except Exception as e:
        print(f"⚠️ Previous candle error: {e}")
    
    return None


def calculate_classic_pivots(high, low, close):
    """Classic Floor Trader Pivots"""
    pp = (high + low + close) / 3
    r1 = (2 * pp) - low
    r2 = pp + (high - low)
    r3 = high + 2 * (pp - low)
    s1 = (2 * pp) - high
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


def get_pivot_signal(symbol, interval='1d', method='classic'):
    """
    Pivot Points sinyali üretir (FLOAT HATASI DÜZELTİLDİ)
    
    Returns:
        dict: {
            'signal': 'LONG' | 'SHORT' | 'NEUTRAL',
            'strength': 0.0-1.0,
            'zone': str,
            'description': str,
            'available': bool
        }
    """
    
    print(f"\n🔍 Pivot Points: {symbol} {interval}")
    
    # Önceki mumu çek
    candle = get_previous_candle(symbol, interval)
    
    if not candle:
        return {
            'signal': 'NEUTRAL',
            'strength': 0.0,
            'zone': 'UNKNOWN',
            'description': f'Previous candle data unavailable [{symbol}]',
            'available': False
        }
    
    # Pivot hesapla
    pivots = calculate_classic_pivots(candle['high'], candle['low'], candle['close'])
    
    # Güncel fiyat çek - ✅ FLOAT olarak
    current_price = get_binance_price(symbol)
    
    if current_price is None:
        return {
            'signal': 'NEUTRAL',
            'strength': 0.0,
            'zone': 'UNKNOWN',
            'description': 'Current price unavailable',
            'available': False
        }
    
    # ✅ current_price artık float - hata yok!
    pp = pivots['pp']
    
    # Zone detection
    tolerance = current_price * 0.01  # %1 tolerance
    
    if abs(current_price - pivots['r3']) < tolerance:
        zone = 'R3'
        signal = 'SHORT'
        strength = 0.9
        description = f"Near R3 ({method}) (${pivots['r3']:,.2f}) - Extreme resistance [{symbol}][{interval}]"
    
    elif abs(current_price - pivots['r2']) < tolerance:
        zone = 'R2'
        signal = 'SHORT'
        strength = 0.8
        description = f"Near R2 ({method}) (${pivots['r2']:,.2f}) - Strong resistance [{symbol}][{interval}]"
    
    elif abs(current_price - pivots['r1']) < tolerance:
        zone = 'R1'
        signal = 'NEUTRAL'
        strength = 0.6
        description = f"Near R1 ({method}) (${pivots['r1']:,.2f}) - First resistance [{symbol}][{interval}]"
    
    elif abs(current_price - pp) < tolerance:
        zone = 'PP'
        signal = 'NEUTRAL'
        strength = 0.5
        description = f"At Pivot Point ({method}) (${pp:,.2f}) - Trend determining [{symbol}][{interval}]"
    
    elif abs(current_price - pivots['s1']) < tolerance:
        zone = 'S1'
        signal = 'NEUTRAL'
        strength = 0.6
        description = f"Near S1 ({method}) (${pivots['s1']:,.2f}) - First support [{symbol}][{interval}]"
    
    elif abs(current_price - pivots['s2']) < tolerance:
        zone = 'S2'
        signal = 'LONG'
        strength = 0.8
        description = f"Near S2 ({method}) (${pivots['s2']:,.2f}) - Strong support [{symbol}][{interval}]"
    
    elif abs(current_price - pivots['s3']) < tolerance:
        zone = 'S3'
        signal = 'LONG'
        strength = 0.9
        description = f"Near S3 ({method}) (${pivots['s3']:,.2f}) - Extreme support [{symbol}][{interval}]"
    
    elif current_price > pp:
        zone = 'ABOVE_PP'
        signal = 'LONG'
        strength = 0.6
        description = f"Above Pivot Point ({method}) (${pp:,.2f}) - Bullish bias [{symbol}][{interval}]"
    
    else:
        zone = 'BELOW_PP'
        signal = 'SHORT'
        strength = 0.6
        description = f"Below Pivot Point ({method}) (${pp:,.2f}) - Bearish bias [{symbol}][{interval}]"
    
    print(f"✅ Zone: {zone}, Signal: {signal}, Strength: {strength:.2f}")
    
    return {
        'signal': signal,
        'strength': round(strength, 2),
        'zone': zone,
        'description': description,
        'current_price': round(current_price, 2),
        'pivot_data': pivots,
        'available': True,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# Test
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 Pivot Points Layer FIX Test")
    print("=" * 80)
    
    result = get_pivot_signal('BTCUSDT', '1d', 'classic')
    
    if result['available']:
        print(f"\n✅ BTCUSDT Pivot:")
        print(f"   Zone: {result['zone']}")
        print(f"   Signal: {result['signal']}")
        print(f"   Strength: {result['strength']}")
        print(f"   Current: ${result['current_price']:,.2f}")
    else:
        print("\n❌ Pivot calculation failed")
    
    print("\n" + "=" * 80)
