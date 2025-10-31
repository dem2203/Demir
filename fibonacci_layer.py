"""
DEMIR AI Trading Bot - Fibonacci Layer
Phase 3A: Golden Ratio Support/Resistance
Tarih: 31 Ekim 2025

Fibonacci Levels:
- Retracement: 0.236, 0.382, 0.500, 0.618, 0.786
- Extension: 1.272, 1.414, 1.618, 2.000, 2.618

Kullanım:
- Fib 0.382 → Weak retracement, trend güçlü (al)
- Fib 0.618 → Golden ratio, ideal entry (al)
- Fib 0.786 → Last chance, stop-loss yakın (dikkatli al)
- Breaks Fib 1.000 → Trend bozuldu (pozisyon kapat)
- Extension 1.618 → Golden extension, take profit target
"""

import requests
from datetime import datetime
from binance.client import Client
import os

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')

try:
    binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET) if BINANCE_API_KEY else None
except:
    binance_client = None


def find_swing_points(symbol, interval='1h', lookback=50):
    """
    Swing High ve Swing Low bulur
    
    Returns:
        dict: {'swing_high': float, 'swing_low': float}
    """
    try:
        if binance_client:
            klines = binance_client.futures_klines(
                symbol=symbol,
                interval=interval,
                limit=lookback
            )
        else:
            url = f"https://fapi.binance.com/fapi/v1/klines"
            params = {'symbol': symbol, 'interval': interval, 'limit': lookback}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                klines = response.json()
            else:
                return None
        
        highs = [float(k[2]) for k in klines]
        lows = [float(k[3]) for k in klines]
        
        return {
            'swing_high': max(highs),
            'swing_low': min(lows)
        }
    
    except Exception as e:
        print(f"❌ Swing points error: {e}")
        return None


def calculate_fibonacci_retracement(swing_high, swing_low):
    """Fibonacci Retracement seviyeleri"""
    diff = swing_high - swing_low
    
    return {
        'type': 'retracement',
        'swing_high': round(swing_high, 2),
        'swing_low': round(swing_low, 2),
        'fib_0': round(swing_high, 2),          # 0% (Swing High)
        'fib_236': round(swing_high - (diff * 0.236), 2),
        'fib_382': round(swing_high - (diff * 0.382), 2),
        'fib_500': round(swing_high - (diff * 0.500), 2),
        'fib_618': round(swing_high - (diff * 0.618), 2),  # Golden Ratio
        'fib_786': round(swing_high - (diff * 0.786), 2),
        'fib_1000': round(swing_low, 2)         # 100% (Swing Low)
    }


def calculate_fibonacci_extension(swing_high, swing_low):
    """Fibonacci Extension seviyeleri (take profit targets)"""
    diff = swing_high - swing_low
    
    return {
        'type': 'extension',
        'swing_high': round(swing_high, 2),
        'swing_low': round(swing_low, 2),
        'ext_1272': round(swing_high + (diff * 0.272), 2),
        'ext_1414': round(swing_high + (diff * 0.414), 2),
        'ext_1618': round(swing_high + (diff * 0.618), 2),  # Golden Extension
        'ext_2000': round(swing_high + (diff * 1.000), 2),
        'ext_2618': round(swing_high + (diff * 1.618), 2)
    }


def calculate_all_fibonacci(symbol, interval='1h', lookback=50):
    """Tüm Fibonacci seviyelerini hesaplar"""
    swings = find_swing_points(symbol, interval, lookback)
    if not swings:
        return None
    
    swing_high = swings['swing_high']
    swing_low = swings['swing_low']
    
    retracement = calculate_fibonacci_retracement(swing_high, swing_low)
    extension = calculate_fibonacci_extension(swing_high, swing_low)
    
    return {
        'symbol': symbol,
        'interval': interval,
        'lookback': lookback,
        'retracement': retracement,
        'extension': extension,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def get_fibonacci_signal(symbol, interval='1h', current_price=None, lookback=50):
    """Fibonacci sinyali üretir"""
    fib = calculate_all_fibonacci(symbol, interval, lookback)
    if not fib:
        return None
    
    if current_price is None:
        try:
            url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                current_price = float(response.json()['price'])
        except:
            return None
    
    ret = fib['retracement']
    signal = 'NEUTRAL'
    strength = 0.5
    level = 'NONE'
    description = ""
    
    # Fib 0.382 (weak retracement)
    if abs(current_price - ret['fib_382']) / current_price < 0.01:
        level = 'FIB_0.382'
        signal = 'LONG'
        strength = 0.7
        description = f"Fiyat Fib 0.382 seviyesinde ({ret['fib_382']}). Weak retracement, trend güçlü - long fırsatı."
    
    # Fib 0.618 (golden ratio)
    elif abs(current_price - ret['fib_618']) / current_price < 0.01:
        level = 'FIB_0.618'
        signal = 'LONG'
        strength = 0.9
        description = f"Fiyat Fib 0.618 (Golden Ratio) seviyesinde ({ret['fib_618']}). İdeal entry point - güçlü long sinyali."
    
    # Fib 0.786 (last chance)
    elif abs(current_price - ret['fib_786']) / current_price < 0.01:
        level = 'FIB_0.786'
        signal = 'LONG'
        strength = 0.6
        description = f"Fiyat Fib 0.786 seviyesinde ({ret['fib_786']}). Last chance - stop-loss yakın olmalı."
    
    # Below Fib 1.000 (trend broken)
    elif current_price < ret['fib_1000']:
        level = 'BELOW_FIB_1.0'
        signal = 'SHORT'
        strength = 0.8
        description = f"Fiyat Fib 1.000 altında ({current_price} < {ret['fib_1000']}). Trend bozuldu - short sinyali."
    
    # Above swing high (extension targets)
    elif current_price > ret['fib_0']:
        ext = fib['extension']
        if abs(current_price - ext['ext_1618']) / current_price < 0.01:
            level = 'EXT_1.618'
            signal = 'TAKE_PROFIT'
            strength = 0.9
            description = f"Fiyat Extension 1.618 (Golden) seviyesinde ({ext['ext_1618']}). Take profit!"
        else:
            level = 'ABOVE_SWING_HIGH'
            signal = 'LONG'
            strength = 0.7
            description = f"Fiyat swing high üzerinde ({current_price} > {ret['fib_0']}). Strong uptrend."
    
    else:
        level = 'IN_RANGE'
        signal = 'NEUTRAL'
        strength = 0.5
        description = f"Fiyat Fibonacci aralığında. {ret['fib_1000']} - {ret['fib_0']}"
    
    return {
        'symbol': symbol,
        'signal': signal,
        'strength': strength,
        'level': level,
        'description': description,
        'current_price': current_price,
        'fib_data': fib,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


if __name__ == "__main__":
    print("=" * 80)
    print("🔱 DEMIR AI - Fibonacci Layer Test")
    print("=" * 80)
    
    print("\n📐 Calculating Fibonacci for BTCUSDT...")
    fib = calculate_all_fibonacci('BTCUSDT', interval='1h', lookback=50)
    
    if fib:
        ret = fib['retracement']
        ext = fib['extension']
        
        print(f"\n✅ Fibonacci Retracement:")
        print(f"   0.0%: ${ret['fib_0']:,.2f} (Swing High)")
        print(f"  23.6%: ${ret['fib_236']:,.2f}")
        print(f"  38.2%: ${ret['fib_382']:,.2f}")
        print(f"  50.0%: ${ret['fib_500']:,.2f}")
        print(f"  61.8%: ${ret['fib_618']:,.2f} ⭐ (Golden Ratio)")
        print(f"  78.6%: ${ret['fib_786']:,.2f}")
        print(f" 100.0%: ${ret['fib_1000']:,.2f} (Swing Low)")
        
        print(f"\n✅ Fibonacci Extension:")
        print(f" 127.2%: ${ext['ext_1272']:,.2f}")
        print(f" 141.4%: ${ext['ext_1414']:,.2f}")
        print(f" 161.8%: ${ext['ext_1618']:,.2f} ⭐ (Golden Extension)")
        print(f" 200.0%: ${ext['ext_2000']:,.2f}")
        print(f" 261.8%: ${ext['ext_2618']:,.2f}")
        
        signal = get_fibonacci_signal('BTCUSDT', interval='1h')
        if signal:
            print(f"\n🎯 Trading Signal:")
            print(f"   Signal: {signal['signal']}")
            print(f"   Strength: {signal['strength']:.2f}")
            print(f"   Level: {signal['level']}")
            print(f"   Description: {signal['description']}")
    else:
        print("❌ Fibonacci calculation failed")
    
    print("\n" + "=" * 80)
