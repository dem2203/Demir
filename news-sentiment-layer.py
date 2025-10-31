"""
DEMIR - News & Sentiment Layer
Real-time news and social sentiment analysis
"""

import requests
from typing import Dict, List, Any
from datetime import datetime, timedelta
import time


# ============================================
# NEWS FETCHER (CryptoPanic API)
# ============================================

def get_crypto_news(symbols: List[str] = None, limit: int = 10) -> Dict[str, Any]:
    """
    Fetch latest crypto news from CryptoPanic
    
    Args:
        symbols: List of symbols to filter (e.g., ['BTC', 'ETH'])
        limit: Number of news items to fetch
    
    Returns:
        {
            'news': [
                {
                    'title': str,
                    'published_at': str,
                    'source': str,
                    'sentiment': 'positive' | 'negative' | 'neutral',
                    'importance': 'high' | 'medium' | 'low'
                }
            ],
            'sentiment_score': float (-100 to 100),
            'news_count': int
        }
    """
    try:
        # CryptoPanic Free API (No key required for basic access)
        url = "https://cryptopanic.com/api/v1/posts/"
        
        params = {
            'public': 'true',
            'kind': 'news',  # Only news, not media
            'filter': 'important'  # Only important news
        }
        
        if symbols:
            params['currencies'] = ','.join(symbols)
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return {'news': [], 'sentiment_score': 0, 'news_count': 0}
        
        data = response.json()
        results = data.get('results', [])[:limit]
        
        news_items = []
        sentiment_total = 0
        
        for item in results:
            # Extract sentiment from votes
            votes = item.get('votes', {})
            positive = votes.get('positive', 0)
            negative = votes.get('negative', 0)
            important = votes.get('important', 0)
            
            # Calculate sentiment
            if positive > negative:
                sentiment = 'positive'
                sentiment_value = min(100, positive * 10)
            elif negative > positive:
                sentiment = 'negative'
                sentiment_value = -min(100, negative * 10)
            else:
                sentiment = 'neutral'
                sentiment_value = 0
            
            # Importance level
            if important > 10:
                importance = 'high'
            elif important > 5:
                importance = 'medium'
            else:
                importance = 'low'
            
            news_items.append({
                'title': item.get('title', 'No title'),
                'published_at': item.get('published_at', ''),
                'source': item.get('source', {}).get('title', 'Unknown'),
                'sentiment': sentiment,
                'sentiment_value': sentiment_value,
                'importance': importance,
                'url': item.get('url', '')
            })
            
            sentiment_total += sentiment_value
        
        # Average sentiment
        avg_sentiment = sentiment_total / len(news_items) if news_items else 0
        
        return {
            'news': news_items,
            'sentiment_score': avg_sentiment,
            'news_count': len(news_items),
            'last_update': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ News fetch error: {e}")
        return {'news': [], 'sentiment_score': 0, 'news_count': 0}


# ============================================
# SOCIAL SENTIMENT (Alternative sources)
# ============================================

def get_twitter_sentiment(symbol: str) -> Dict[str, Any]:
    """
    Get Twitter/X sentiment for a symbol
    
    Note: This is a placeholder. Real implementation would require:
    - Twitter API v2 credentials
    - Sentiment analysis model (e.g., VADER, TextBlob, or Hugging Face)
    
    For now, returns neutral sentiment
    """
    # TODO: Implement Twitter API integration
    return {
        'platform': 'twitter',
        'symbol': symbol,
        'sentiment_score': 0,  # -100 to 100
        'tweet_volume': 0,
        'trending': False
    }


def get_reddit_sentiment(symbol: str) -> Dict[str, Any]:
    """
    Get Reddit sentiment for a symbol
    
    Note: Placeholder - requires Reddit API credentials
    """
    # TODO: Implement Reddit API integration
    return {
        'platform': 'reddit',
        'symbol': symbol,
        'sentiment_score': 0,
        'post_count': 0,
        'comment_volume': 0
    }


# ============================================
# NEWS IMPACT SCORING
# ============================================

def calculate_news_impact(news_data: Dict) -> float:
    """
    Calculate overall news impact score
    
    Args:
        news_data: Output from get_crypto_news()
    
    Returns:
        Impact score (-100 to 100)
    """
    if not news_data or not news_data.get('news'):
        return 0
    
    sentiment_score = news_data.get('sentiment_score', 0)
    news_count = news_data.get('news_count', 0)
    
    # Count high-importance news
    high_importance = sum(
        1 for item in news_data['news'] 
        if item.get('importance') == 'high'
    )
    
    # Base score from sentiment
    impact = sentiment_score
    
    # Amplify if many high-importance news
    if high_importance > 3:
        impact *= 1.5
    elif high_importance > 1:
        impact *= 1.2
    
    # Recent news (last 1 hour) gets more weight
    recent_news = 0
    now = datetime.now()
    
    for item in news_data['news']:
        try:
            pub_time = datetime.fromisoformat(item['published_at'].replace('Z', '+00:00'))
            if (now - pub_time) < timedelta(hours=1):
                recent_news += 1
        except:
            pass
    
    if recent_news > 5:
        impact *= 1.3
    
    return max(-100, min(100, impact))


# ============================================
# AGGREGATE SENTIMENT
# ============================================

def get_aggregate_sentiment(symbol: str) -> Dict[str, Any]:
    """
    Aggregate sentiment from all sources
    
    Returns:
        {
            'symbol': str,
            'overall_sentiment': float (-100 to 100),
            'news_sentiment': float,
            'social_sentiment': float,
            'sources': {
                'news': dict,
                'twitter': dict,
                'reddit': dict
            }
        }
    """
    # Fetch news
    news_data = get_crypto_news([symbol], limit=20)
    news_impact = calculate_news_impact(news_data)
    
    # Fetch social sentiment (placeholder for now)
    twitter_data = get_twitter_sentiment(symbol)
    reddit_data = get_reddit_sentiment(symbol)
    
    # Weighted average
    news_weight = 0.7
    social_weight = 0.3
    
    social_avg = (
        twitter_data['sentiment_score'] + 
        reddit_data['sentiment_score']
    ) / 2
    
    overall = (news_impact * news_weight) + (social_avg * social_weight)
    
    return {
        'symbol': symbol,
        'overall_sentiment': overall,
        'news_sentiment': news_impact,
        'social_sentiment': social_avg,
        'sources': {
            'news': news_data,
            'twitter': twitter_data,
            'reddit': reddit_data
        },
        'timestamp': datetime.now().isoformat()
    }


# ============================================
# MARKET-MOVING NEWS DETECTION
# ============================================

def detect_market_moving_news(news_data: Dict) -> List[Dict]:
    """
    Detect potentially market-moving news
    
    Returns list of high-impact news items
    """
    if not news_data or not news_data.get('news'):
        return []
    
    market_moving = []
    
    for item in news_data['news']:
        # Check if news is important
        is_important = item.get('importance') == 'high'
        
        # Check if recent (last 30 minutes)
        try:
            pub_time = datetime.fromisoformat(item['published_at'].replace('Z', '+00:00'))
            is_recent = (datetime.now() - pub_time) < timedelta(minutes=30)
        except:
            is_recent = False
        
        # Check if strong sentiment
        sentiment_value = abs(item.get('sentiment_value', 0))
        is_strong = sentiment_value > 50
        
        if is_important and (is_recent or is_strong):
            market_moving.append({
                'title': item['title'],
                'sentiment': item['sentiment'],
                'importance': item['importance'],
                'published_at': item['published_at'],
                'url': item.get('url', '')
            })
    
    return market_moving


# ============================================
# EXPORT FUNCTION FOR EXTERNAL_DATA
# ============================================

def get_sentiment_data(symbol: str = 'BTC') -> Dict[str, Any]:
    """
    Main export function for external_data.py
    
    Returns complete sentiment analysis
    """
    sentiment = get_aggregate_sentiment(symbol)
    market_moving = detect_market_moving_news(sentiment['sources']['news'])
    
    return {
        'overall_score': sentiment['overall_sentiment'],
        'news_score': sentiment['news_sentiment'],
        'social_score': sentiment['social_sentiment'],
        'market_moving_news': market_moving,
        'news_count': sentiment['sources']['news'].get('news_count', 0),
        'timestamp': sentiment['timestamp']
    }


if __name__ == '__main__':
    # Test
    print("Testing News & Sentiment Layer...")
    result = get_sentiment_data('BTC')
    print(f"Overall Sentiment: {result['overall_score']:.2f}")
    print(f"News Count: {result['news_count']}")
    print(f"Market-Moving News: {len(result['market_moving_news'])}")
