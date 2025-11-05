"""
DEMIR AI Trading Bot - News Sentiment Layer v2.0 (REAL DATA + FIXED)
========================================
Alternative.me Fear & Greed Index + Binance volume analizi
Tarih: 4 Kasım 2025, 21:26 CET

✅ YENİ v2.0:
-----------
✅ get_news_sentiment() wrapper function added
✅ Returns standardized format: {'available': bool, 'score': float (0-100), 'signal': str}
✅ ai_brain v12.0 compatible

ÖZELLİKLER:
-----------
✅ Alternative.me Fear & Greed Index (BEDAVA)
✅ Binance volume trend analizi
✅ Market sentiment scoring
✅ API key gerektirmez!
"""

import requests
import pandas as pd
from datetime import datetime

def get_fear_greed_index():
    """
    Alternative.me Fear & Greed Index - BEDAVA API
    0-100 arası değer:
    - 0-24: Extreme Fear (Aşırı Korku)
    - 25-44: Fear (Korku)
    - 45-55: Neutral (Nötr)
    - 56-75: Greed (Açgözlülük)
    - 76-100: Extreme Greed (Aşırı Açgözlülük)
    """
    try:
        url = "https://api.alternative.me/fng/?limit=1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                fng_data = data['data'][0]
                value = int(fng_data['value'])
                classification = fng_data['value_classification']
                timestamp = fng_data['timestamp']
                
                return {
                    'value': value,
                    'classification': classification,
                    'timestamp': timestamp,
                    'available': True
                }
        
        return {'available': False}
    
    except Exception as e:
        print(f"⚠️ Fear & Greed Index error: {e}")
        return {'available': False}

def get_binance_volume_trend(symbol, interval='1h', lookback=50):
    """
    Binance'den hacim trendi analiz eder
    Son 50 period hacim artış/azalış
    """
    try:
        url = f"https://fapi.binance.com/fapi/v1/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': lookback}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
            
            # Volume trend
            recent_vol = df['volume'].tail(10).mean()
            older_vol = df['volume'].head(10).mean()
            
            if older_vol > 0:
                vol_change = (recent_vol - older_vol) / older_vol
            else:
                vol_change = 0
            
            # Volume increasing = bullish
            if vol_change > 0.2:
                vol_sentiment = 'BULLISH'
                vol_score = 0.7
            elif vol_change < -0.2:
                vol_sentiment = 'BEARISH'
                vol_score = 0.3
            else:
                vol_sentiment = 'NEUTRAL'
                vol_score = 0.5
            
            return {
                'vol_change': vol_change,
                'vol_sentiment': vol_sentiment,
                'vol_score': vol_score,
                'available': True
            }
        
        return {'available': False}
    
    except:
        return {'available': False}

def calculate_sentiment_score(fng_data, vol_data, symbol):
    """
    Fear & Greed + Volume trend'den sentiment score hesaplar
    0.0 - 1.0 arası (0 = Extreme Bearish, 1 = Extreme Bullish)
    """
    # Fear & Greed Index score (0-100 → 0.0-1.0)
    if fng_data.get('available'):
        fng_value = fng_data['value']
        fng_score = fng_value / 100.0
    else:
        fng_score = 0.5  # Neutral fallback
    
    # Volume trend score
    if vol_data.get('available'):
        vol_score = vol_data['vol_score']
    else:
        vol_score = 0.5  # Neutral fallback
    
    # Weighted average (70% Fear&Greed, 30% Volume)
    final_score = (fng_score * 0.7) + (vol_score * 0.3)
    
    # Sentiment classification
    if final_score >= 0.75:
        sentiment = 'BULLISH'
        impact = 'HIGH'
    elif final_score >= 0.55:
        sentiment = 'BULLISH'
        impact = 'MODERATE'
    elif final_score >= 0.45:
        sentiment = 'NEUTRAL'
        impact = 'LOW'
    elif final_score >= 0.25:
        sentiment = 'BEARISH'
        impact = 'MODERATE'
    else:
        sentiment = 'BEARISH'
        impact = 'HIGH'
    
    return final_score, sentiment, impact

def get_news_signal(symbol):
    """
    News Sentiment sinyali üretir (GERÇEK VERİ - BEDAVA API)
    
    Returns:
        dict: {
            'score': 0.0-1.0,
            'sentiment': 'BULLISH' | 'BEARISH' | 'NEUTRAL',
            'impact': 'HIGH' | 'MODERATE' | 'LOW',
            'details': {...},
            'available': bool
        }
    """
    print(f"\n🔍 News Sentiment: {symbol} (Fear & Greed + Volume)")
    
    # Fear & Greed Index çek
    fng_data = get_fear_greed_index()
    
    # Volume trend analizi
    vol_data = get_binance_volume_trend(symbol, interval='1h', lookback=50)
    
    # Sentiment score hesapla
    score, sentiment, impact = calculate_sentiment_score(fng_data, vol_data, symbol)
    
    # Details
    details = {
        'fear_greed_value': fng_data.get('value', None),
        'fear_greed_classification': fng_data.get('classification', 'N/A'),
        'volume_change': vol_data.get('vol_change', 0),
        'volume_sentiment': vol_data.get('vol_sentiment', 'NEUTRAL'),
        'source': 'Alternative.me Fear & Greed Index + Binance Volume'
    }
    
    # Description
    if fng_data.get('available'):
        fng_desc = f"Fear & Greed: {fng_data['value']}/100 ({fng_data['classification']})"
    else:
        fng_desc = "Fear & Greed: N/A"
    
    if vol_data.get('available'):
        vol_desc = f"Volume: {vol_data['vol_change']*100:+.1f}% ({vol_data['vol_sentiment']})"
    else:
        vol_desc = "Volume: N/A"
    
    description = f"{fng_desc} | {vol_desc} → {sentiment} sentiment [{symbol}]"
    
    available = fng_data.get('available', False) or vol_data.get('available', False)
    
    print(f"✅ Score: {score:.2f}, Sentiment: {sentiment}, Impact: {impact}")
    
    return {
        'score': round(score, 2),
        'sentiment': sentiment,
        'impact': impact,
        'description': description,
        'details': details,
        'available': available,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def get_news_sentiment(symbol='BTCUSDT'):
    """
    Wrapper function for ai_brain v12.0 compatibility
    
    Args:
        symbol: Trading pair (e.g., "BTCUSDT")
    
    Returns:
        dict: {'available': bool, 'score': float (0-100), 'signal': str}
    """
    result = get_news_signal(symbol)
    
    if result['available']:
        # Convert 0-1 score to 0-100 scale
        score_100 = result['score'] * 100
        
        return {
            'available': True,
            'score': round(score_100, 2),
            'signal': result['sentiment'],
            'impact': result.get('impact', 'MODERATE'),
            'fear_greed': result['details'].get('fear_greed_value')
        }
    else:
        return {
            'available': False,
            'score': 50.0,
            'signal': 'NEUTRAL'
        }

# Test
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 News Sentiment Layer v2.0 Test")
    print("   (Fear & Greed + Volume + ai_brain compatible)")
    print("=" * 80)
    
    # Fear & Greed Index test
    fng = get_fear_greed_index()
    if fng.get('available'):
        print(f"\n✅ Fear & Greed Index:")
        print(f"   Value: {fng['value']}/100")
        print(f"   Classification: {fng['classification']}")
    else:
        print("\n❌ Fear & Greed Index: Unavailable")
    
    # Symbol tests
    symbols = ['BTCUSDT', 'ETHUSDT']
    for symbol in symbols:
        # Test original function
        result = get_news_signal(symbol)
        
        if result['available']:
            print(f"\n✅ {symbol} News Sentiment (Original):")
            print(f"   Score: {result['score']:.2f}/1.00")
            print(f"   Sentiment: {result['sentiment']}")
            print(f"   Impact: {result['impact']}")
            print(f"   Fear & Greed: {result['details']['fear_greed_value']}/100")
            print(f"   Volume Change: {result['details']['volume_change']*100:+.1f}%")
        else:
            print(f"\n❌ {symbol}: Data unavailable")
        
        # Test new wrapper
        result_v2 = get_news_sentiment(symbol)
        print(f"\n✅ {symbol} News Sentiment (v2.0 - ai_brain compatible):")
        print(f"   Available: {result_v2['available']}")
        print(f"   Score: {result_v2['score']:.2f}/100")
        print(f"   Signal: {result_v2['signal']}")
    
    print("\n" + "=" * 80)
