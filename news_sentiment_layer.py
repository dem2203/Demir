"""
DEMIR AI Trading Bot - News Sentiment Layer
Phase 2: CryptoPanic API Integration
Tarih: 31 Ekim 2025

Bu modül CryptoPanic API'den crypto haberleri çeker ve sentiment analizi yapar.
"""

import requests
import os
from datetime import datetime, timedelta

# API Key - Render.com Environment Variable'dan gelecek
CRYPTOPANIC_API_KEY = os.getenv('CRYPTOPANIC_API_KEY', 'c3f29e41eb58dbe0fa64667f35a3134bb4f4fe22')

# API Endpoint
CRYPTOPANIC_BASE_URL = "https://cryptopanic.com/api/v1/posts/"


def fetch_news(currencies='BTC,ETH', filter_type='hot', limit=20):
    """
    CryptoPanic API'den haber çeker
    
    Args:
        currencies (str): Para birimleri (örn: 'BTC,ETH,SOL')
        filter_type (str): 'hot', 'rising', 'bullish', 'bearish', 'important'
        limit (int): Kaç haber çekilecek (max 50)
    
    Returns:
        list: Haber listesi
    """
    
    try:
        params = {
            'auth_token': CRYPTOPANIC_API_KEY,
            'currencies': currencies,
            'filter': filter_type,
            'public': 'true'
        }
        
        response = requests.get(CRYPTOPANIC_BASE_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            # Limit uygula
            return results[:limit]
        else:
            print(f"⚠️ CryptoPanic API Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error fetching news: {str(e)}")
        return []


def analyze_sentiment(news_list):
    """
    Haber listesinin sentiment analizini yapar
    
    Args:
        news_list (list): fetch_news() sonucu
    
    Returns:
        dict: {
            'sentiment': 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL',
            'score': 0.0-1.0,
            'bullish_count': int,
            'bearish_count': int,
            'neutral_count': int,
            'total_news': int
        }
    """
    
    if not news_list:
        return {
            'sentiment': 'NEUTRAL',
            'score': 0.5,
            'bullish_count': 0,
            'bearish_count': 0,
            'neutral_count': 0,
            'total_news': 0
        }
    
    bullish_count = 0
    bearish_count = 0
    neutral_count = 0
    
    for news in news_list:
        votes = news.get('votes', {})
        
        # Bullish votes
        positive = votes.get('positive', 0)
        # Bearish votes
        negative = votes.get('negative', 0)
        # Important votes
        important = votes.get('important', 0)
        
        # Sentiment belirleme
        if positive > negative:
            bullish_count += 1
        elif negative > positive:
            bearish_count += 1
        else:
            neutral_count += 1
    
    total = len(news_list)
    
    # Genel sentiment hesapla
    bullish_ratio = bullish_count / total
    bearish_ratio = bearish_count / total
    
    # Sentiment score (0.0 = Very Bearish, 0.5 = Neutral, 1.0 = Very Bullish)
    sentiment_score = (bullish_ratio - bearish_ratio + 1) / 2
    
    # Kategorize et
    if sentiment_score > 0.6:
        sentiment = 'POSITIVE'
    elif sentiment_score < 0.4:
        sentiment = 'NEGATIVE'
    else:
        sentiment = 'NEUTRAL'
    
    return {
        'sentiment': sentiment,
        'score': sentiment_score,
        'bullish_count': bullish_count,
        'bearish_count': bearish_count,
        'neutral_count': neutral_count,
        'total_news': total
    }


def get_news_signal(symbol='BTC'):
    """
    Belirli bir coin için news sentiment sinyali döner
    
    Args:
        symbol (str): Coin sembolü (örn: 'BTC', 'ETH', 'SOL')
    
    Returns:
        dict: {
            'symbol': str,
            'sentiment': 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL',
            'score': float,
            'impact': 'HIGH' | 'MEDIUM' | 'LOW',
            'details': dict,
            'timestamp': str
        }
    """
    
    # Symbol'den coin kodu çıkar (BTCUSDT -> BTC)
    coin = symbol.replace('USDT', '').replace('BUSD', '')
    
    # Haberleri çek
    news_list = fetch_news(currencies=coin, filter_type='hot', limit=20)
    
    # Sentiment analizi yap
    analysis = analyze_sentiment(news_list)
    
    # Impact seviyesi belirle
    score = analysis['score']
    if score > 0.7 or score < 0.3:
        impact = 'HIGH'
    elif score > 0.6 or score < 0.4:
        impact = 'MEDIUM'
    else:
        impact = 'LOW'
    
    return {
        'symbol': symbol,
        'sentiment': analysis['sentiment'],
        'score': round(analysis['score'], 2),
        'impact': impact,
        'details': {
            'bullish_news': analysis['bullish_count'],
            'bearish_news': analysis['bearish_count'],
            'neutral_news': analysis['neutral_count'],
            'total_news': analysis['total_news']
        },
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# Test fonksiyonu
if __name__ == "__main__":
    print("=" * 60)
    print("🔱 DEMIR AI - News Sentiment Layer Test")
    print("=" * 60)
    
    # BTC için test
    print("\n📰 Fetching BTC news...")
    btc_signal = get_news_signal('BTCUSDT')
    
    print(f"\n✅ News Signal for {btc_signal['symbol']}:")
    print(f"   Sentiment: {btc_signal['sentiment']}")
    print(f"   Score: {btc_signal['score']}")
    print(f"   Impact: {btc_signal['impact']}")
    print(f"   Details: {btc_signal['details']}")
    print(f"   Timestamp: {btc_signal['timestamp']}")
    
    print("\n" + "=" * 60)
