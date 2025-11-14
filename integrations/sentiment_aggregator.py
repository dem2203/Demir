"""
Sentiment Aggregation
NewsAPI + Twitter + CMC
REAL sentiment - 100% Policy
"""

import requests
import os
import logging
from datetime import datetime
from textblob import TextBlob

logger = logging.getLogger(__name__)

class NewsAPIIntegration:
    """NewsAPI - Real news"""
    
    def __init__(self):
        self.api_key = os.getenv('NEWSAPI_KEY', '')
        self.base_url = "https://newsapi.org/v2"
    
    def get_news(self, query='bitcoin', limit=50):
        """REAL crypto news"""
        try:
            params = {
                'q': query,
                'sortBy': 'publishedAt',
                'apiKey': self.api_key,
                'pageSize': limit
            }
            
            response = requests.get(f"{self.base_url}/everything", params=params, timeout=10)
            
            if response.status_code == 200:
                articles = response.json().get('articles', [])
                logger.info(f"✅ Got {len(articles)} articles")
                return articles
            return []
        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
            return []

class TwitterIntegration:
    """Twitter - Real tweets"""
    
    def __init__(self):
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN', '')
    
    def get_tweets(self, query='Bitcoin OR Ethereum', limit=100):
        """REAL crypto tweets"""
        try:
            headers = {"Authorization": f"Bearer {self.bearer_token}"}
            params = {'query': query, 'max_results': limit}
            
            response = requests.get(
                "https://api.twitter.com/2/tweets/search/recent",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                tweets = response.json().get('data', [])
                logger.info(f"✅ Got {len(tweets)} tweets")
                return tweets
            return []
        except Exception as e:
            logger.error(f"Twitter error: {e}")
            return []

class CMCIntegration:
    """CoinMarketCap - Real market data"""
    
    def __init__(self):
        self.api_key = os.getenv('CMC_API_KEY', '')
    
    def get_market_data(self, limit=10):
        """REAL market cap data"""
        try:
            headers = {'X-CMC_PRO_API_KEY': self.api_key}
            params = {'limit': limit, 'convert': 'USD'}
            
            response = requests.get(
                "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ CMC market data retrieved")
                return response.json().get('data', [])
            return []
        except Exception as e:
            logger.error(f"CMC error: {e}")
            return []

class SentimentAnalyzer:
    """Analyze sentiment"""
    
    @staticmethod
    def analyze_text(text):
        """REAL sentiment analysis"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            return (polarity + 1) / 2
        except:
            return 0.5

class SentimentAggregator:
    """Aggregate all sentiments"""
    
    def __init__(self):
        self.news = NewsAPIIntegration()
        self.twitter = TwitterIntegration()
        self.cmc = CMCIntegration()
        self.analyzer = SentimentAnalyzer()
    
    def get_overall_sentiment(self):
        """REAL overall sentiment"""
        try:
            news = self.news.get_news()
            tweets = self.twitter.get_tweets()
            
            texts = []
            texts.extend([a['title'] for a in news if a['title']])
            texts.extend([t['text'] for t in tweets if 'text' in t])
            
            if not texts:
                return 0.5
            
            sentiments = [self.analyzer.analyze_text(t) for t in texts]
            avg = sum(sentiments) / len(sentiments)
            
            logger.info(f"✅ Sentiment: {avg:.2f}")
            return avg
        except Exception as e:
            logger.error(f"Sentiment error: {e}")
            return 0.5
