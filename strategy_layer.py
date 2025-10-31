"""
DEMIR AI Trading Bot - Strategy Layer v3 DEBUG
Phase 3A: Complete Integration with DEBUG output
Tarih: 31 Ekim 2025

ENTEGRASYON:
- Phase 1: Technical Indicators
- Phase 2: News Sentiment
- Phase 3A: Volume Profile, Pivot Points, Fibonacci, VWAP

GEÇICI: Mock data aktif (test için)
"""

from datetime import datetime

# Phase 3A imports
try:
    import volume_profile_layer as vp
    VP_AVAILABLE = True
    print("✅ DEBUG: volume_profile_layer imported successfully")
except Exception as e:
    VP_AVAILABLE = False
    print(f"⚠️ DEBUG: volume_profile_layer import failed: {e}")

try:
    import pivot_points_layer as pp
    PP_AVAILABLE = True
    print("✅ DEBUG: pivot_points_layer imported successfully")
except Exception as e:
    PP_AVAILABLE = False
    print(f"⚠️ DEBUG: pivot_points_layer import failed: {e}")

try:
    import fibonacci_layer as fib
    FIB_AVAILABLE = True
    print("✅ DEBUG: fibonacci_layer imported successfully")
except Exception as e:
    FIB_AVAILABLE = False
    print(f"⚠️ DEBUG: fibonacci_layer import failed: {e}")

try:
    import vwap_layer as vwap
    VWAP_AVAILABLE = True
    print("✅ DEBUG: vwap_layer imported successfully")
except Exception as e:
    VWAP_AVAILABLE = False
    print(f"⚠️ DEBUG: vwap_layer import failed: {e}")

try:
    import news_sentiment_layer as news
    NEWS_AVAILABLE = True
    print("✅ DEBUG: news_sentiment_layer imported successfully")
except Exception as e:
    NEWS_AVAILABLE = False
    print(f"⚠️ DEBUG: news_sentiment_layer import failed: {e}")


def calculate_volume_profile_score(symbol, interval='1h'):
    """Volume Profile sinyalini 0-100 score'a çevirir"""
    print(f"🔍 DEBUG: VP Score starting for {symbol} {interval}")
    
    # GEÇICI: Mock data for testing
    print("⚠️ DEBUG: Using MOCK DATA for Volume Profile")
    return {
        'score': 65,
        'signal': 'LONG',
        'zone': 'VAH',
        'strength': 0.75,
        'description': f'Price at Value Area High ($69,500) - Resistance zone',
        'available': True
    }
    
    # GERÇEK KOD (mock data kaldırınca aktif olacak):
    """
    if not VP_AVAILABLE:
        print(f"⚠️ DEBUG: VP not available - module not imported")
        return {'score': 50, 'signal': 'NEUTRAL', 'available': False}
    
    try:
        print(f"🔍 DEBUG: Calling vp.get_volume_profile_signal...")
        vp_signal = vp.get_volume_profile_signal(symbol, interval)
        
        if not vp_signal:
            print(f"⚠️ DEBUG: VP signal returned None")
            return {'score': 50, 'signal': 'NEUTRAL', 'available': False}
        
        print(f"✅ DEBUG: VP signal received: {vp_signal['signal']}")
        
        if vp_signal['signal'] == 'LONG':
            base_score = 70
        elif vp_signal['signal'] == 'SHORT':
            base_score = 30
        else:
            base_score = 50
        
        strength = vp_signal['strength']
        score = base_score + ((strength - 0.5) * 40)
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
        print(f"❌ DEBUG: VP Score error: {e}")
        import traceback
        traceback.print_exc()
        return {'score': 50, 'signal': 'NEUTRAL', 'available': False}
    """


def calculate_pivot_score(symbol, interval='1d', method='classic'):
    """Pivot Points sinyalini 0-100 score'a çevirir"""
    print(f"🔍 DEBUG: Pivot Score starting for {symbol} {interval} {method}")
    
    # GEÇICI: Mock data for testing
    print("⚠️ DEBUG: Using MOCK DATA for Pivot Points")
    return {
        'score': 70,
        'signal': 'SHORT',
        'zone': 'R2',
        'strength': 0.80,
        'description': f'Near R2 (Classic) ($69,450) - Strong resistance',
        'available': True
    }


def calculate_fibonacci_score(symbol, interval='1h', lookback=50):
    """Fibonacci sinyalini 0-100 score'a çevirir"""
    print(f"🔍 DEBUG: Fibonacci Score starting for {symbol} {interval}")
    
    # GEÇICI: Mock data for testing
    print("⚠️ DEBUG: Using MOCK DATA for Fibonacci")
    return {
        'score': 75,
        'signal': 'LONG',
        'level': 'FIB_0.618',
        'strength': 0.85,
        'description': f'At 0.618 Golden Ratio ($69,200) - Ideal entry point',
        'available': True
    }


def calculate_vwap_score(symbol, interval='5m', lookback=100):
    """VWAP sinyalini 0-100 score'a çevirir"""
    print(f"🔍 DEBUG: VWAP Score starting for {symbol} {interval}")
    
    # GEÇICI: Mock data for testing
    print("⚠️ DEBUG: Using MOCK DATA for VWAP")
    return {
        'score': 35,
        'signal': 'SHORT',
        'zone': '+2STD',
        'strength': 0.70,
        'description': f'Price above +2σ ($69,800) - Overbought, mean reversion expected',
        'available': True
    }


def calculate_news_score(symbol):
    """News sentiment 0-100 score'a çevirir"""
    print(f"🔍 DEBUG: News Score starting for {symbol}")
    
    if not NEWS_AVAILABLE:
        print(f"⚠️ DEBUG: News not available - module not imported")
        return {'score': 50, 'sentiment': 'NEUTRAL', 'available': False}
    
    try:
        print(f"🔍 DEBUG: Calling news.get_news_signal...")
        news_data = news.get_news_signal(symbol)
        
        if not news_data:
            print(f"⚠️ DEBUG: News signal returned None")
            return {'score': 50, 'sentiment': 'NEUTRAL', 'available': False}
        
        print(f"✅ DEBUG: News signal received: {news_data['sentiment']}")
        
        sentiment_score = news_data['score']
        score = sentiment_score * 100
        
        return {
            'score': round(score, 2),
            'sentiment': news_data['sentiment'],
            'impact': news_data['impact'],
            'details': news_data['details'],
            'available': True
        }
    
    except Exception as e:
        print(f"❌ DEBUG: News Score error: {e}")
        import traceback
        traceback.print_exc()
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
    
    print(f"\n🎯 DEBUG: Comprehensive Score starting for {symbol} {interval}")
    
    # Tüm skorları hesapla
    vp_score = calculate_volume_profile_score(symbol, interval)
    pp_score = calculate_pivot_score(symbol, '1d', 'classic')
    fib_score = calculate_fibonacci_score(symbol, interval, 50)
    vwap_score = calculate_vwap_score(symbol, '5m', 100)
    news_score = calculate_news_score(symbol)
    
    # Weights (toplam 100%)
    weights = {
        'volume_profile': 0.25,
        'pivot_points': 0.20,
        'fibonacci': 0.20,
        'vwap': 0.20,
        'news': 0.15
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
    
    print(f"\n📊 DEBUG: Component Scores:")
    for key, component in components.items():
        available = component.get('available', False)
        score = component.get('score', 50)
        print(f"   {key}: score={score}, available={available}")
        
        if available:
            total_score += score * weights[key]
            total_weight += weights[key]
    
    # Normalize score
    if total_weight > 0:
        final_score = total_score / total_weight
    else:
        final_score = 50
    
    print(f"\n✅ DEBUG: Final Score Calculation:")
    print(f"   Total Score: {total_score:.2f}")
    print(f"   Total Weight: {total_weight:.2f}")
    print(f"   Final Score: {final_score:.2f}")
    
    # Signal belirleme
    if final_score >= 65:
        signal = 'LONG'
        confidence = (final_score - 50) / 50
    elif final_score <= 35:
        signal = 'SHORT'
        confidence = (50 - final_score) / 50
    else:
        signal = 'NEUTRAL'
        confidence = 1.0 - (abs(final_score - 50) / 15)
    
    print(f"   Signal: {signal}")
    print(f"   Confidence: {confidence:.2f}\n")
    
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
    print("🔱 DEMIR AI - Strategy Layer v3 DEBUG Test")
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
        status = "✅" if data.get('available') else "❌"
        print(f"   {status} {component.replace('_', ' ').title()}: {data.get('score', 0)}/100")
    
    print("\n" + "=" * 80)
