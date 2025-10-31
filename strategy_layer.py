"""
DEMIR AI Trading Bot - Strategy Layer v3
Phase 3A: Complete Integration
Tarih: 31 Ekim 2025

ENTEGRASYON:
- Phase 1: Technical Indicators (RSI, MACD, BB, EMA, ATR, ADX)
- Phase 2: News Sentiment (CryptoPanic)
- Phase 3A: Volume Profile, Pivot Points, Fibonacci, VWAP

Multi-Factor Scoring System:
- Technical Score (0-100)
- News Sentiment Score (0-100)
- Volume Profile Score (0-100)
- Pivot Points Score (0-100)
- Fibonacci Score (0-100)
- VWAP Score (0-100)
- FINAL SCORE: Weighted Average
"""

from datetime import datetime

# Phase 3A imports
try:
    import volume_profile_layer as vp
    VP_AVAILABLE = True
except:
    VP_AVAILABLE = False

try:
    import pivot_points_layer as pp
    PP_AVAILABLE = True
except:
    PP_AVAILABLE = False

try:
    import fibonacci_layer as fib
    FIB_AVAILABLE = True
except:
    FIB_AVAILABLE = False

try:
    import vwap_layer as vwap
    VWAP_AVAILABLE = True
except:
    VWAP_AVAILABLE = False

# Phase 1 & 2 (varsayalım ki var)
try:
    import analysis_layer
    ANALYSIS_AVAILABLE = True
except:
    ANALYSIS_AVAILABLE = False

try:
    import news_sentiment_layer as news
    NEWS_AVAILABLE = True
except:
    NEWS_AVAILABLE = False


def calculate_volume_profile_score(symbol, interval='1h'):
    """Volume Profile sinyalini 0-100 score'a çevirir"""
    if not VP_AVAILABLE:
        return {'score': 50, 'signal': 'NEUTRAL', 'available': False}
    
    try:
        vp_signal = vp.get_volume_profile_signal(symbol, interval)
        if not vp_signal:
            return {'score': 50, 'signal': 'NEUTRAL', 'available': False}
        
        # Signal to score mapping
        if vp_signal['signal'] == 'LONG':
            base_score = 70
        elif vp_signal['signal'] == 'SHORT':
            base_score = 30
        else:
            base_score = 50
        
        # Strength adjustment
        strength = vp_signal['strength']
        score = base_score + ((strength - 0.5) * 40)  # ±20 points based on strength
        score = max(0, min(100, score))
        
        return {
            'score': round(score, 2),
            'signal': vp_signal['signal'],
            'zone': vp_signal['zone'],
            'strength': strength,
            'description': vp_signal['description'],
            'available': True
        }
    
    except Exception as e:
        print(f"❌ VP Score error: {e}")
        return {'score': 50, 'signal': 'NEUTRAL', 'available': False}


def calculate_pivot_score(symbol, interval='1d', method='classic'):
    """Pivot Points sinyalini 0-100 score'a çevirir"""
    if not PP_AVAILABLE:
        return {'score': 50, 'signal': 'NEUTRAL', 'available': False}
    
    try:
        pp_signal = pp.get_pivot_signal(symbol, interval, method=method)
        if not pp_signal:
            return {'score': 50, 'signal': 'NEUTRAL', 'available': False}
        
        # Signal to score
        if pp_signal['signal'] == 'LONG':
            base_score = 70
        elif pp_signal['signal'] == 'SHORT':
            base_score = 30
        else:
            base_score = 50
        
        strength = pp_signal['strength']
        score = base_score + ((strength - 0.5) * 40)
        score = max(0, min(100, score))
        
        return {
            'score': round(score, 2),
            'signal': pp_signal['signal'],
            'zone': pp_signal['zone'],
            'strength': strength,
            'description': pp_signal['description'],
            'available': True
        }
    
    except Exception as e:
        print(f"❌ PP Score error: {e}")
        return {'score': 50, 'signal': 'NEUTRAL', 'available': False}


def calculate_fibonacci_score(symbol, interval='1h', lookback=50):
    """Fibonacci sinyalini 0-100 score'a çevirir"""
    if not FIB_AVAILABLE:
        return {'score': 50, 'signal': 'NEUTRAL', 'available': False}
    
    try:
        fib_signal = fib.get_fibonacci_signal(symbol, interval, lookback=lookback)
        if not fib_signal:
            return {'score': 50, 'signal': 'NEUTRAL', 'available': False}
        
        # Signal to score
        if fib_signal['signal'] == 'LONG':
            base_score = 70
        elif fib_signal['signal'] == 'SHORT':
            base_score = 30
        elif fib_signal['signal'] == 'TAKE_PROFIT':
            base_score = 90  # Güçlü sinyal
        else:
            base_score = 50
        
        strength = fib_signal['strength']
        score = base_score + ((strength - 0.5) * 40)
        score = max(0, min(100, score))
        
        return {
            'score': round(score, 2),
            'signal': fib_signal['signal'],
            'level': fib_signal['level'],
            'strength': strength,
            'description': fib_signal['description'],
            'available': True
        }
    
    except Exception as e:
        print(f"❌ Fib Score error: {e}")
        return {'score': 50, 'signal': 'NEUTRAL', 'available': False}


def calculate_vwap_score(symbol, interval='5m', lookback=100):
    """VWAP sinyalini 0-100 score'a çevirir"""
    if not VWAP_AVAILABLE:
        return {'score': 50, 'signal': 'NEUTRAL', 'available': False}
    
    try:
        vwap_signal = vwap.get_vwap_signal(symbol, interval, lookback=lookback)
        if not vwap_signal:
            return {'score': 50, 'signal': 'NEUTRAL', 'available': False}
        
        # Signal to score
        if vwap_signal['signal'] == 'LONG':
            base_score = 70
        elif vwap_signal['signal'] == 'SHORT':
            base_score = 30
        else:
            base_score = 50
        
        strength = vwap_signal['strength']
        score = base_score + ((strength - 0.5) * 40)
        score = max(0, min(100, score))
        
        return {
            'score': round(score, 2),
            'signal': vwap_signal['signal'],
            'zone': vwap_signal['zone'],
            'strength': strength,
            'description': vwap_signal['description'],
            'available': True
        }
    
    except Exception as e:
        print(f"❌ VWAP Score error: {e}")
        return {'score': 50, 'signal': 'NEUTRAL', 'available': False}


def calculate_news_score(symbol):
    """News sentiment 0-100 score'a çevirir"""
    if not NEWS_AVAILABLE:
        return {'score': 50, 'sentiment': 'NEUTRAL', 'available': False}
    
    try:
        news_data = news.get_news_signal(symbol)
        if not news_data:
            return {'score': 50, 'sentiment': 'NEUTRAL', 'available': False}
        
        # Sentiment to score
        sentiment_score = news_data['score']  # 0.0-1.0
        score = sentiment_score * 100
        
        return {
            'score': round(score, 2),
            'sentiment': news_data['sentiment'],
            'impact': news_data['impact'],
            'details': news_data['details'],
            'available': True
        }
    
    except Exception as e:
        print(f"❌ News Score error: {e}")
        return {'score': 50, 'sentiment': 'NEUTRAL', 'available': False}


def calculate_comprehensive_score(symbol, interval='1h'):
    """
    Tüm Phase'lerin weighted average score'u
    
    Returns:
        dict: {
            'final_score': 0-100,
            'signal': 'LONG' | 'SHORT' | 'NEUTRAL',
            'confidence': 0.0-1.0,
            'components': {...}
        }
    """
    
    # Tüm skorları hesapla
    vp_score = calculate_volume_profile_score(symbol, interval)
    pp_score = calculate_pivot_score(symbol, '1d', 'classic')
    fib_score = calculate_fibonacci_score(symbol, interval, 50)
    vwap_score = calculate_vwap_score(symbol, '5m', 100)
    news_score = calculate_news_score(symbol)
    
    # Weights (toplam 100%)
    weights = {
        'volume_profile': 0.25,  # %25
        'pivot_points': 0.20,    # %20
        'fibonacci': 0.20,       # %20
        'vwap': 0.20,            # %20
        'news': 0.15             # %15
    }
    
    # Weighted score hesapla
    total_score = 0
    total_weight = 0
    
    components = {
        'volume_profile': vp_score,
        'pivot_points': pp_score,
        'fibonacci': fib_score,
        'vwap': vwap_score,
        'news_sentiment': news_score
    }
    
    for key, component in components.items():
        if component['available']:
            total_score += component['score'] * weights[key]
            total_weight += weights[key]
    
    # Normalize score
    if total_weight > 0:
        final_score = total_score / total_weight
    else:
        final_score = 50  # Neutral if nothing available
    
    # Signal belirleme
    if final_score >= 65:
        signal = 'LONG'
        confidence = (final_score - 50) / 50  # 0.3-1.0
    elif final_score <= 35:
        signal = 'SHORT'
        confidence = (50 - final_score) / 50  # 0.3-1.0
    else:
        signal = 'NEUTRAL'
        confidence = 1.0 - (abs(final_score - 50) / 15)  # 0.0-1.0
    
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


# Test fonksiyonu
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 DEMIR AI - Strategy Layer v3 Test")
    print("=" * 80)
    
    symbol = 'BTCUSDT'
    interval = '1h'
    
    print(f"\n📊 Calculating Comprehensive Score for {symbol}...")
    
    result = calculate_comprehensive_score(symbol, interval)
    
    print(f"\n✅ FINAL RESULTS:")
    print(f"   Final Score: {result['final_score']}/100")
    print(f"   Signal: {result['signal']}")
    print(f"   Confidence: {result['confidence']*100:.0f}%")
    
    print(f"\n📋 COMPONENT SCORES:")
    for component, data in result['components'].items():
        status = "✅" if data['available'] else "❌"
        print(f"   {status} {component.replace('_', ' ').title()}: {data['score']}/100")
        if data['available'] and 'signal' in data:
            print(f"      Signal: {data['signal']}")
    
    print(f"\n⚖️ WEIGHTS:")
    for component, weight in result['weights'].items():
        print(f"   {component.replace('_', ' ').title()}: {weight*100}%")
    
    print("\n" + "=" * 80)
