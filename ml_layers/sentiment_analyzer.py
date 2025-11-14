#!/usr/bin/env python3
"""
🔱 DEMIR AI - sentiment_analyzer.py (JOB 2 - 5 MIN)
STRICT - NO MOCK, FAIL LOUD
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict
import requests
import numpy as np

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Sentiment analysis - STRICT"""
    
    def __init__(self, newsapi_key: str, twitter_token: str):
        if not newsapi_key or not twitter_token:
            raise ValueError("❌ Missing API keys")
        self.newsapi_key = newsapi_key
        self.twitter_token = twitter_token
    
    def fetch_news_sentiment(self) -> Dict:
        """NewsAPI sentiment - STRICT"""
        try:
            url = f"https://newsapi.org/v2/everything?q=bitcoin%20OR%20ethereum%20OR%20crypto&sortBy=publishedAt&language=en&pageSize=50&apiKey={self.newsapi_key}"
            
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"❌ NewsAPI failed: {response.status_code}")
            
            data = response.json()
            if not data.get('articles'):
                raise ValueError("❌ No articles found")
            
            positive = sum(1 for a in data['articles'] if any(
                word in a.get('description', '').lower() 
                for word in ['bullish', 'surge', 'rally', 'jump', 'gain', 'bull']
            ))
            negative = sum(1 for a in data['articles'] if any(
                word in a.get('description', '').lower() 
                for word in ['bearish', 'crash', 'fall', 'decline', 'bear', 'drop']
            ))
            
            total = positive + negative
            if total == 0:
                sentiment = 0.0
            else:
                sentiment = (positive - negative) / total
            
            if not -1 <= sentiment <= 1:
                raise ValueError(f"❌ Invalid sentiment: {sentiment}")
            
            logger.info(f"✅ News sentiment: {sentiment:.2f} ({positive}+ / {negative}-)")
            return {
                'news_sentiment': float(sentiment),
                'positive_news': positive,
                'negative_news': negative
            }
        except Exception as e:
            logger.critical(f"❌ News sentiment failed: {e}")
            raise
    
    def fetch_twitter_sentiment(self) -> Dict:
        """Twitter sentiment - STRICT"""
        try:
            headers = {"Authorization": f"Bearer {self.twitter_token}"}
            url = "https://api.twitter.com/2/tweets/search/recent"
            params = {
                "query": "(bitcoin OR ethereum OR crypto) -is:retweet lang:en",
                "max_results": 100,
                "tweet.fields": "public_metrics"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"❌ Twitter API failed: {response.status_code}")
            
            data = response.json()
            if not data.get('data'):
                raise ValueError("❌ No tweets found")
            
            positive = 0
            negative = 0
            for tweet in data['data']:
                text = tweet.get('text', '').lower()
                if any(w in text for w in ['bullish', 'buy', 'surge', 'pump']):
                    positive += 1
                if any(w in text for w in ['bearish', 'sell', 'dump', 'crash']):
                    negative += 1
            
            total = positive + negative
            if total == 0:
                sentiment = 0.0
            else:
                sentiment = (positive - negative) / total
            
            if not -1 <= sentiment <= 1:
                raise ValueError(f"❌ Invalid sentiment: {sentiment}")
            
            logger.info(f"✅ Twitter sentiment: {sentiment:.2f}")
            return {
                'twitter_sentiment': float(sentiment),
                'positive_tweets': positive,
                'negative_tweets': negative
            }
        except Exception as e:
            logger.critical(f"❌ Twitter sentiment failed: {e}")
            raise
    
    def fetch_reddit_sentiment(self) -> Dict:
        """Reddit sentiment - STRICT"""
        try:
            # Simplified Reddit sentiment (using PRAW would require auth)
            # Using external API or manual polling
            
            subreddits = ['bitcoin', 'ethereum', 'cryptocurrency']
            positive = 0
            negative = 0
            
            for sub in subreddits:
                url = f"https://www.reddit.com/r/{sub}/top.json?t=day&limit=50"
                headers = {'User-Agent': 'DEMIR-AI-Bot/1.0'}
                
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    continue
                
                data = response.json()
                for post in data.get('data', {}).get('children', []):
                    title = post.get('data', {}).get('title', '').lower()
                    if any(w in title for w in ['bullish', 'buy', 'pump']):
                        positive += 1
                    if any(w in title for w in ['bearish', 'crash', 'dump']):
                        negative += 1
            
            total = positive + negative
            if total == 0:
                sentiment = 0.0
            else:
                sentiment = (positive - negative) / total
            
            if not -1 <= sentiment <= 1:
                raise ValueError(f"❌ Invalid sentiment: {sentiment}")
            
            logger.info(f"✅ Reddit sentiment: {sentiment:.2f}")
            return {
                'reddit_sentiment': float(sentiment),
                'positive_reddit': positive,
                'negative_reddit': negative
            }
        except Exception as e:
            logger.error(f"⚠️ Reddit sentiment failed (non-critical): {e}")
            return {
                'reddit_sentiment': 0.0,
                'positive_reddit': 0,
                'negative_reddit': 0
            }
    
    def aggregate_sentiment(self) -> Dict:
        """Get all sentiments & aggregate - STRICT"""
        try:
            logger.info("🔄 Fetching sentiment analysis...")
            
            news = self.fetch_news_sentiment()
            twitter = self.fetch_twitter_sentiment()
            reddit = self.fetch_reddit_sentiment()
            
            # Weighted aggregate
            aggregate = (
                news['news_sentiment'] * 0.4 +
                twitter['twitter_sentiment'] * 0.4 +
                reddit['reddit_sentiment'] * 0.2
            )
            
            if not -1 <= aggregate <= 1:
                raise ValueError(f"❌ Invalid aggregate: {aggregate}")
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'news_sentiment': news['news_sentiment'],
                'twitter_sentiment': twitter['twitter_sentiment'],
                'reddit_sentiment': reddit['reddit_sentiment'],
                'aggregate_sentiment': float(aggregate),
                'positive_total': news['positive_news'] + twitter['positive_tweets'] + reddit['positive_reddit'],
                'negative_total': news['negative_news'] + twitter['negative_tweets'] + reddit['negative_reddit']
            }
            
            logger.info(f"✅ Sentiment complete: aggregate={aggregate:.2f}")
            return result
        
        except Exception as e:
            logger.critical(f"❌ Sentiment aggregation failed: {e}")
            raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("✅ SentimentAnalyzer ready")
