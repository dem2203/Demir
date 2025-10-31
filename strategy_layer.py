"""
DEMIR AI Trading Bot - Strategy Layer v3 DYNAMIC MOCK DATA
Phase 3A: Symbol-Aware Mock Data
Tarih: 31 Ekim 2025

FİX: Artık her coin için farklı mock değerler!
"""

from datetime import datetime
import requests


def get_current_price(symbol):
    """Binance'den güncel fiyat çek"""
    try:
        url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return float(response.json()['price'])
    except:
        pass
    
    # Fallback prices
    fallbacks = {
        'BTCUSDT': 69500.0,
        'ETHUSDT': 3850.0,
        'LTCUSDT': 85.0,
        'SOLUSDT': 195.0,
        'BNBUSDT': 625.0
    }
    return fallbacks.get(symbol, 1000.0)


def calculate_volume_profile_score(symbol, interval='1h'):
    """Volume Profile - DYNAMIC MOCK DATA"""
    print(f"✅ VP Score: Returning DYNAMIC MOCK DATA for {symbol} {interval}")
    
    # Güncel fiyat al
    current_price = get_current_price(symbol)
    
    # Dinamik değerler
    vah_price = current_price * 1.005  # %0.5 üst
    val_price = current_price * 0.995  # %0.5 alt
    poc_price = current_price * 1.002  # %0.2 üst
    
    return {
        'score': 65,
        'signal': 'LONG',
        'zone': 'VAH',
        'strength': 0.75,
        'description': f'Price at Value Area High (${vah_price:,.2f}) - Resistance zone [{symbol}][{interval}]',
        'available': True,
        'vah': vah_price,
        'val': val_price,
        'poc': poc_price
    }


def calculate_pivot_score(symbol, interval='1d', method='classic'):
    """Pivot Points - DYNAMIC MOCK DATA"""
    print(f"✅ Pivot Score: Returning DYNAMIC MOCK DATA for {symbol} {interval}")
    
    current_price = get_current_price(symbol)
    
    # Dinamik pivot levels
    pp = current_price
    r1 = current_price * 1.015
    r2 = current_price * 1.03
    r3 = current_price * 1.045
    s1 = current_price * 0.985
    s2 = current_price * 0.97
    s3 = current_price * 0.955
    
    return {
        'score': 70,
        'signal': 'SHORT',
        'zone': 'R2',
        'strength': 0.80,
        'description': f'Near R2 ({method.title()}) (${r2:,.2f}) - Strong resistance [{symbol}][{interval}]',
        'available': True,
        'pp': pp,
        'r1': r1,
        'r2': r2,
        'r3': r3,
        's1': s1,
        's2': s2,
        's3': s3
    }


def calculate_fibonacci_score(symbol, interval='1h', lookback=50):
    """Fibonacci - DYNAMIC MOCK DATA"""
    print(f"✅ Fibonacci Score: Returning DYNAMIC MOCK DATA for {symbol} {interval}")
    
    current_price = get_current_price(symbol)
    
    # Dinamik fibonacci levels
    fib_618 = current_price * 0.995
    fib_50 = current_price * 1.0
    fib_382 = current_price * 1.005
    
    return {
        'score': 75,
        'signal': 'LONG',
        'level': 'FIB_0.618',
        'strength': 0.85,
        'description': f'At 0.618 Golden Ratio (${fib_618:,.2f}) - Ideal entry [{symbol}][{interval}][LB:{lookback}]',
        'available': True,
        'fib_618': fib_618,
        'fib_50': fib_50,
        'fib_382': fib_382
    }


def calculate_vwap_score(symbol, interval='5m', lookback=100):
    """VWAP - DYNAMIC MOCK DATA"""
    print(f"✅ VWAP Score: Returning DYNAMIC MOCK DATA for {symbol} {interval}")
    
    current_price = get_current_price(symbol)
    
    # Dinamik VWAP bands
    vwap = current_price * 0.998
    upper_2std = current_price * 1.008
    lower_2std = current_price * 0.988
    
    return {
        'score': 35,
        'signal': 'SHORT',
        'zone': '+2STD',
        'strength': 0.70,
        'description': f'Price above +2σ (${upper_2std:,.2f}) - Overbought [{symbol}][{interval}][LB:{lookback}]',
        'available': True,
        'vwap': vwap,
        'upper_2std': upper_2std,
        'lower_2std': lower_2std
    }


def calculate_news_score(symbol):
    """News Sentiment - MOCK DATA"""
    print(f"✅ News Score: Returning MOCK DATA for {symbol}")
    return {
        'score': 50,
        'sentiment': 'NEUTRAL',
        'impact': 'LOW',
        'details': {'bullish_news': 0, 'bearish_news': 0, 'neutral_news': 0, 'total_news': 0},
        'available': True
    }


def calculate_comprehensive_score(symbol, interval='1h'):
    """
    COMPREHENSIVE SCORE - DYNAMIC MOCK DATA VERSION
    """
    
    print(f"\n" + "=" * 80)
    print(f"🎯 COMPREHENSIVE SCORE FOR {symbol} {interval}")
    print(f"   VERSION: DYNAMIC MOCK DATA")
    print("=" * 80)
    
    # Dinamik skorları hesapla (symbol ve interval parametreleri geçiliyor!)
    vp_score = calculate_volume_profile_score(symbol, interval)
    pp_score = calculate_pivot_score(symbol, interval, 'classic')
    fib_score = calculate_fibonacci_score(symbol, interval, 50)
    vwap_score = calculate_vwap_score(symbol, interval, 100)
    news_score = calculate_news_score(symbol)
    
    print(f"\n📊 ALL COMPONENTS LOADED (DYNAMIC MOCK):")
    print(f"   VP: {vp_score['available']} - {symbol}")
    print(f"   Pivot: {pp_score['available']} - {symbol}")
    print(f"   Fib: {fib_score['available']} - {symbol}")
    print(f"   VWAP: {vwap_score['available']} - {symbol}")
    print(f"   News: {news_score['available']} - {symbol}")
    
    # Weights
    weights = {
        'volume_profile': 0.25,
        'pivot_points': 0.20,
        'fibonacci': 0.20,
        'vwap': 0.20,
        'news': 0.15
    }
    
    # Calculate weighted score
    total_score = (
        vp_score['score'] * weights['volume_profile'] +
        pp_score['score'] * weights['pivot_points'] +
        fib_score['score'] * weights['fibonacci'] +
        vwap_score['score'] * weights['vwap'] +
        news_score['score'] * weights['news']
    )
    
    final_score = total_score
    
    print(f"\n✅ FINAL SCORE CALCULATION:")
    print(f"   VP: {vp_score['score']} * {weights['volume_profile']} = {vp_score['score'] * weights['volume_profile']}")
    print(f"   Pivot: {pp_score['score']} * {weights['pivot_points']} = {pp_score['score'] * weights['pivot_points']}")
    print(f"   Fib: {fib_score['score']} * {weights['fibonacci']} = {fib_score['score'] * weights['fibonacci']}")
    print(f"   VWAP: {vwap_score['score']} * {weights['vwap']} = {vwap_score['score'] * weights['vwap']}")
    print(f"   News: {news_score['score']} * {weights['news']} = {news_score['score'] * weights['news']}")
    print(f"   TOTAL: {final_score}")
    
    # Signal
    if final_score >= 65:
        signal = 'LONG'
        confidence = (final_score - 50) / 50
    elif final_score <= 35:
        signal = 'SHORT'
        confidence = (50 - final_score) / 50
    else:
        signal = 'NEUTRAL'
        confidence = 1.0 - (abs(final_score - 50) / 15)
    
    print(f"   SIGNAL: {signal}")
    print(f"   CONFIDENCE: {confidence:.2f}")
    print("=" * 80 + "\n")
    
    components = {
        'volume_profile': vp_score,
        'pivot_points': pp_score,
        'fibonacci': fib_score,
        'vwap': vwap_score,
        'news_sentiment': news_score
    }
    
    return {
        'symbol': symbol,
        'interval': interval,
        'final_score': round(final_score, 2),
        'signal': signal,
        'confidence': round(confidence, 2),
        'components': components,
        'weights': weights,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# Test
if __name__ == "__main__":
    print("\n🔱 TESTING DYNAMIC MOCK DATA VERSION\n")
    
    for symbol in ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']:
        result = calculate_comprehensive_score(symbol, '1h')
        
        print(f"\n✅ TEST RESULTS for {symbol}:")
        print(f"   Final Score: {result['final_score']}")
        print(f"   Signal: {result['signal']}")
        print(f"   Confidence: {result['confidence']}")
