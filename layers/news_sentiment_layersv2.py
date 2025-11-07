# ===========================================
# news_sentiment_layer.py v2.0 - CRYPTOPANIC API
# ===========================================
# âœ… CryptoPanic API for real crypto news
# âœ… Sentiment analysis (positive/negative/neutral)
# âœ… Importance filtering
# âœ… Multi-coin support
# ===========================================

"""
ğŸ”± DEMIR AI TRADING BOT - News Sentiment Layer v2.0
====================================================================
Tarih: 3 KasÄ±m 2025, 22:25 CET
Versiyon: 2.0 - REAL CRYPTOPANIC DATA + SENTIMENT ANALYSIS

YENÄ° v2.0:
----------
âœ… CryptoPanic API integration
âœ… Real-time crypto news
âœ… Sentiment classification (positive/negative/neutral)
âœ… Importance weighting (hot/important/regular)
âœ… Multi-coin filtering (BTC, ETH, LTC)
âœ… Time-decay scoring

DATA SOURCE:
------------
- CryptoPanic API (CRYPTOPANIC_KEY)
- Free tier: 60 requests/hour
- News from 300+ sources
- Sentiment pre-classified

SCORING LOGIC:
--------------
Positive sentiment â†’ 60-80 (bullish)
Negative sentiment â†’ 20-40 (bearish)
Neutral/Mixed â†’ 45-55 (neutral)

Importance multiplier:
- Hot news: 2x weight
- Important news: 1.5x weight
- Regular news: 1x weight

Time decay:
- Last 6 hours: 100% weight
- 6-12 hours: 75% weight
- 12-24 hours: 50% weight
- >24 hours: 25% weight
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List

# ============================================================================
# CRYPTOPANIC API FUNCTIONS
# ============================================================================

def get_cryptopanic_news(currency: str = 'BTC', filter_type: str = 'rising') -> List[Dict[str, Any]]:
    """
    Fetch news from CryptoPanic API
    
    Args:
        currency: Coin symbol (BTC, ETH, LTC)
        filter_type: News filter (rising, hot, bullish, bearish, important, saved, lol)
    
    Returns:
        List of news articles
    """
    api_key = os.getenv('CRYPTOPANIC_KEY')
    
    if not api_key:
        print("âš ï¸ CRYPTOPANIC_KEY not set in environment")
        return []
    
    try:
        url = "https://cryptopanic.com/api/v1/posts/"
        params = {
            'auth_token': api_key,
            'currencies': currency,
            'filter': filter_type,
            'public': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'results' in data:
            news_list = data['results']
            print(f"âœ… CryptoPanic: {len(news_list)} news articles fetched ({currency})")
            return news_list
        else:
            print("âš ï¸ CryptoPanic: No results in response")
            return []
        
    except Exception as e:
        print(f"âŒ CryptoPanic API error: {e}")
        return []


def classify_sentiment(news_item: Dict[str, Any]) -> str:
    """
    Classify news sentiment
    
    CryptoPanic provides votes: positive, negative, neutral
    
    Returns:
        'positive', 'negative', or 'neutral'
    """
    try:
        votes = news_item.get('votes', {})
        
        positive = votes.get('positive', 0)
        negative = votes.get('negative', 0)
        neutral = votes.get('liked', 0)  # CryptoPanic uses 'liked' for neutral
        
        # Determine sentiment based on votes
        if positive > negative and positive > neutral:
            return 'positive'
        elif negative > positive and negative > neutral:
            return 'negative'
        else:
            return 'neutral'
        
    except Exception as e:
        print(f"âŒ Sentiment classification error: {e}")
        return 'neutral'


def get_news_importance(news_item: Dict[str, Any]) -> str:
    """
    Get news importance level
    
    Returns:
        'hot', 'important', or 'regular'
    """
    try:
        # CryptoPanic marks important/hot news
        metadata = news_item.get('metadata', {})
        
        if metadata.get('hot', False):
            return 'hot'
        elif metadata.get('important', False):
            return 'important'
        else:
            return 'regular'
        
    except Exception as e:
        return 'regular'


def calculate_time_decay(published_at: str) -> float:
    """
    Calculate time decay weight
    
    Args:
        published_at: ISO timestamp string
    
    Returns:
        float: Time decay multiplier (0.25 to 1.0)
    """
    try:
        published_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        now = datetime.now(published_time.tzinfo)
        
        hours_ago = (now - published_time).total_seconds() / 3600
        
        if hours_ago < 6:
            return 1.0  # Full weight
        elif hours_ago < 12:
            return 0.75
        elif hours_ago < 24:
            return 0.50
        else:
            return 0.25
        
    except Exception as e:
        print(f"âŒ Time decay error: {e}")
        return 0.5


# ============================================================================
# SCORING FUNCTIONS
# ============================================================================

def score_sentiment(sentiment: str) -> float:
    """
    Base score based on sentiment
    
    Returns:
        float: Base score (0-100)
    """
    if sentiment == 'positive':
        return 70
    elif sentiment == 'negative':
        return 30
    else:
        return 50


def get_importance_weight(importance: str) -> float:
    """
    Get importance multiplier
    
    Returns:
        float: Weight multiplier
    """
    if importance == 'hot':
        return 2.0
    elif importance == 'important':
        return 1.5
    else:
        return 1.0


def calculate_weighted_sentiment(news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate weighted sentiment score from multiple news articles
    
    Returns:
        dict: Aggregated sentiment metrics
    """
    if not news_list:
        return {
            'score': 50,
            'sentiment': 'neutral',
            'article_count': 0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0
        }
    
    weighted_scores = []
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    
    for news in news_list[:20]:  # Limit to most recent 20
        try:
            # Get sentiment
            sentiment = classify_sentiment(news)
            sentiment_counts[sentiment] += 1
            
            # Get base score
            base_score = score_sentiment(sentiment)
            
            # Get importance weight
            importance = get_news_importance(news)
            importance_weight = get_importance_weight(importance)
            
            # Get time decay
            published_at = news.get('published_at', '')
            time_decay = calculate_time_decay(published_at) if published_at else 0.5
            
            # Calculate weighted score
            weighted_score = base_score * importance_weight * time_decay
            weighted_scores.append(weighted_score)
            
        except Exception as e:
            print(f"âŒ News scoring error: {e}")
            continue
    
    # Calculate final score
    if weighted_scores:
        final_score = sum(weighted_scores) / len(weighted_scores)
    else:
        final_score = 50
    
    # Determine overall sentiment
    if final_score >= 60:
        overall_sentiment = 'positive'
    elif final_score <= 40:
        overall_sentiment = 'negative'
    else:
        overall_sentiment = 'neutral'
    
    return {
        'score': round(final_score, 2),
        'sentiment': overall_sentiment,
        'article_count': len(news_list),
        'positive_count': sentiment_counts['positive'],
        'negative_count': sentiment_counts['negative'],
        'neutral_count': sentiment_counts['neutral']
    }


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def analyze_news_sentiment(symbol: str = 'BTCUSDT') -> Dict[str, Any]:
    """
    Complete news sentiment analysis
    
    Args:
        symbol: Trading pair (BTCUSDT, ETHUSDT, LTCUSDT)
    
    Returns:
        dict with score, signal, and sentiment details
    """
    print(f"\n{'='*80}")
    print(f"ğŸ“° NEWS SENTIMENT LAYER v2.0 - CRYPTOPANIC ANALYSIS")
    print(f"   Symbol: {symbol}")
    print(f"{'='*80}\n")
    
    # Convert symbol to currency code
    currency_map = {
        'BTCUSDT': 'BTC',
        'ETHUSDT': 'ETH',
        'LTCUSDT': 'LTC'
    }
    
    currency = currency_map.get(symbol, 'BTC')
    
    # Fetch news
    news_list = get_cryptopanic_news(currency, filter_type='rising')
    
    if not news_list:
        print("âŒ News Sentiment: No news available")
        return {
            'available': False,
            'score': 50,
            'signal': 'NEUTRAL',
            'reason': 'No news data from CryptoPanic'
        }
    
    try:
        # Calculate weighted sentiment
        sentiment_result = calculate_weighted_sentiment(news_list)
        
        score = sentiment_result['score']
        sentiment = sentiment_result['sentiment']
        
        # Determine signal
        if score >= 60:
            signal = 'BULLISH'
        elif score <= 40:
            signal = 'BEARISH'
        else:
            signal = 'NEUTRAL'
        
        # Print results
        print(f"ğŸ“Š NEWS ANALYSIS:")
        print(f"   Total Articles: {sentiment_result['article_count']}")
        print(f"   Positive: {sentiment_result['positive_count']}")
        print(f"   Negative: {sentiment_result['negative_count']}")
        print(f"   Neutral: {sentiment_result['neutral_count']}")
        
        print(f"\n{'='*80}")
        print(f"âœ… NEWS SENTIMENT ANALYSIS COMPLETE!")
        print(f"   Score: {score:.1f}/100")
        print(f"   Overall Sentiment: {sentiment.upper()}")
        print(f"   Signal: {signal}")
        print(f"{'='*80}\n")
        
        return {
            'available': True,
            'score': score,
            'signal': signal,
            'sentiment': sentiment,
            'article_count': sentiment_result['article_count'],
            'positive_count': sentiment_result['positive_count'],
            'negative_count': sentiment_result['negative_count'],
            'neutral_count': sentiment_result['neutral_count'],
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"âŒ News sentiment analysis error: {e}")
        return {
            'available': False,
            'score': 50,
            'signal': 'NEUTRAL',
            'reason': str(e)
        }


def get_news_signal(symbol: str = 'BTCUSDT') -> Dict[str, Any]:
    """
    Main function called by ai_brain.py
    
    Returns:
        dict: {'available': bool, 'score': float, 'signal': str}
    """
    result = analyze_news_sentiment(symbol)
    
    return {
        'available': result['available'],
        'score': result.get('score', 50),
        'signal': result.get('signal', 'NEUTRAL'),
        'sentiment': result.get('sentiment', 'neutral'),
        'article_count': result.get('article_count', 0)
    }


# ============================================================================
# STANDALONE TESTING
# ============================================================================
if __name__ == "__main__":
    print("="*80)
    print("ğŸ”± NEWS SENTIMENT LAYER v2.0 TEST")
    print("   CRYPTOPANIC API INTEGRATION")
    print("="*80)
    
    # Test with BTCUSDT
    result = get_news_signal('BTCUSDT')
    
    print("\n" + "="*80)
    print("ğŸ“Š NEWS SENTIMENT TEST RESULTS:")
    print(f"   Available: {result['available']}")
    print(f"   Score: {result.get('score', 'N/A')}/100")
    print(f"   Signal: {result.get('signal', 'N/A')}")
    print(f"   Overall Sentiment: {result.get('sentiment', 'N/A')}")
    print(f"   Article Count: {result.get('article_count', 'N/A')}")
    print("="*80)
