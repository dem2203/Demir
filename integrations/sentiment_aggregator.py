# sentiment_aggregator.py - Real Sentiment Aggregation

import requests
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NewsAPIIntegration:
    """Real NewsAPI data"""
    
    def __init__(self):
        self.api_key = os.getenv('NEWSAPI_KEY', '')
        self.base_url = "https://newsapi.org/v2"
    
    def get_crypto_news(self, query='bitcoin', limit=50):
        """Get REAL crypto news"""
        try:
            params = {
                'q': query,
                'sortBy': 'publishedAt',
                'apiKey': self.api_key,
                'pageSize': limit
            }
            
            response = requests.get(f"{self.base_url}/everything", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                logger.info(f"✅ NewsAPI: Found {len(articles)} articles")
                return articles
            
            return []
        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
            return []

class TwitterSentiment:
    """Real Twitter sentiment analysis"""
    
    def __init__(self):
        self.api_key = os.getenv('TWITTER_API_KEY', '')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN', '')
    
    def get_crypto_tweets(self, query='Bitcoin OR Ethereum', max_results=100):
        """Get REAL crypto tweets"""
        try:
            headers = {
                "Authorization": f"Bearer {self.bearer_token}"
            }
            
            params = {
                'query': query,
                'max_results': max_results,
                'tweet.fields': 'created_at,public_metrics'
            }
            
            response = requests.get(
                "https://api.twitter.com/2/tweets/search/recent",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                tweets = data.get('data', [])
                logger.info(f"✅ Twitter: Found {len(tweets)} tweets")
                return tweets
            
            return []
        except Exception as e:
            logger.error(f"Twitter error: {e}")
            return []

class CMCIntegration:
    """CoinMarketCap - Real market sentiment"""
    
    def __init__(self):
        self.api_key = os.getenv('CMC_API_KEY', '')
        self.base_url = "https://pro-api.coinmarketcap.com/v1"
    
    def get_market_data(self):
        """Get REAL market cap data"""
        try:
            headers = {
                'X-CMC_PRO_API_KEY': self.api_key
            }
            
            params = {
                'limit': 10,
                'convert': 'USD'
            }
            
            response = requests.get(
                f"{self.base_url}/cryptocurrency/listings/latest",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ CMC: Got market data")
                return data['data']
            
            return []
        except Exception as e:
            logger.error(f"CMC error: {e}")
            return []

class SentimentAggregator:
    """Aggregate sentiment from all sources"""
    
    def __init__(self):
        self.news = NewsAPIIntegration()
        self.twitter = TwitterSentiment()
        self.cmc = CMCIntegration()
    
    def calculate_sentiment_score(self, text):
        """Calculate REAL sentiment score - NO FALLBACK"""
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            return (polarity + 1) / 2  # Convert to 0-1
        except Exception as e:
            logger.error(f"❌ TextBlob sentiment calculation failed: {e}")
            # ❌ NEVER return fallback 0.5 - return None to enforce real data
            return None
    
    def get_overall_sentiment(self):
        """Get REAL overall market sentiment - NO FALLBACK"""
        try:
            news = self.news.get_crypto_news()
            tweets = self.twitter.get_crypto_tweets()
            
            all_texts = []
            all_texts.extend([a['title'] + ' ' + a.get('description', '') for a in news if a.get('title')])
            all_texts.extend([t['text'] for t in tweets if t.get('text')])
            
            if not all_texts:
                logger.warning("❌ No sentiment data available")
                return None  # ❌ NO FALLBACK - return None if no data
            
            sentiments = [self.calculate_sentiment_score(t) for t in all_texts]
            # Filter out None values
            sentiments = [s for s in sentiments if s is not None]
            
            if not sentiments:
                logger.warning("❌ All sentiment calculations failed")
                return None  # ❌ NO FALLBACK - return None if all failed
            
            avg_sentiment = sum(sentiments) / len(sentiments)
            
            logger.info(f"✅ Overall Sentiment: {avg_sentiment:.2f} (from {len(sentiments)} sources)")
            return avg_sentiment
        
        except Exception as e:
            logger.error(f"❌ Sentiment aggregation error: {e}")
            # ❌ CRITICAL: NEVER return 0.5 fallback - return None to enforce real data policy
            return None
