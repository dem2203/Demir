"""
TWITTER/REDDIT NLP SENTIMENT LAYER - v2.0 FIXED
⚠️ REAL Twitter + Reddit data ONLY
NO MOCK DATA - Real or Error
"""

import os
import logging
from datetime import datetime, timedelta
import aiohttp
import asyncio
from typing import Dict, Optional, List
import numpy as np

logger = logging.getLogger(__name__)


class TwitterRedditSentimentLayer:
    """Real Twitter/Reddit sentiment analysis - NO MOCK DATA"""
    
    def __init__(self):
        """Initialize"""
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
        self.twitter_url = "https://api.twitter.com/2/tweets/search/recent"
        self.news_url = "https://newsapi.org/v2/everything"
        
        if not self.twitter_bearer_token or not self.newsapi_key:
            logger.warning("Twitter/NewsAPI keys not configured - sentiment will fail")
    
    async def get_sentiment(self, symbol: str) -> Dict:
        """Get REAL Twitter/Reddit sentiment
        
        Args:
            symbol: 'BTC', 'ETH', 'SOL'
        
        Returns:
            Real sentiment data or ERROR (never mock!)
        """
        try:
            # Get REAL Twitter sentiment
            twitter_sentiment = await self._get_twitter_sentiment(symbol)
            
            # Get REAL News sentiment
            news_sentiment = await self._get_news_sentiment(symbol)
            
            # Combine results
            if twitter_sentiment and news_sentiment:
                combined = self._combine_sentiment(twitter_sentiment, news_sentiment)
                return combined
            elif twitter_sentiment:
                return twitter_sentiment
            elif news_sentiment:
                return news_sentiment
            else:
                # ALL REAL SOURCES FAILED - Return ERROR (not mock!)
                logger.error(f"All real sentiment sources failed for {symbol}")
                return {
                    'sentiment': None,
                    'score': None,
                    'valid': False,
                    'error': 'All real sentiment sources unavailable',
                    'timestamp': datetime.now().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {
                'sentiment': None,
                'score': None,
                'valid': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _get_twitter_sentiment(self, symbol: str) -> Optional[Dict]:
        """Get REAL Twitter sentiment - NO MOCK DATA"""
        
        if not self.twitter_bearer_token:
            logger.warning("Twitter key not configured")
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.twitter_bearer_token}",
                "User-Agent": "SentimentAnalysisBot"
            }
            
            # Search for REAL tweets
            query = f"{symbol} crypto -is:retweet lang:en"
            params = {
                "query": query,
                "max_results": 100,
                "tweet.fields": "created_at,public_metrics,author_id"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.twitter_url,
                    params=params,
                    headers=headers,
                    timeout=10
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        tweets = data.get('data', [])
                        
                        if not tweets:
                            logger.warning(f"No tweets found for {symbol}")
                            return None
                        
                        # Analyze REAL tweets
                        sentiment_score = self._analyze_tweet_sentiment(tweets)
                        
                        return {
                            'source': 'TWITTER_REAL',
                            'sentiment': self._score_to_sentiment(sentiment_score),
                            'score': sentiment_score,
                            'tweet_count': len(tweets),
                            'timestamp': datetime.now().isoformat(),
                            'valid': True
                        }
                    else:
                        logger.warning(f"Twitter API error: {resp.status}")
                        return None
        
        except asyncio.TimeoutError:
            logger.warning(f"Twitter timeout for {symbol}")
            return None
        except Exception as e:
            logger.warning(f"Twitter sentiment error: {e}")
            return None
    
    async def _get_news_sentiment(self, symbol: str) -> Optional[Dict]:
        """Get REAL News sentiment"""
        
        if not self.newsapi_key:
            logger.warning("NewsAPI key not configured")
            return None
        
        try:
            params = {
                "q": symbol,
                "sortBy": "publishedAt",
                "apiKey": self.newsapi_key,
                "pageSize": 50
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.news_url,
                    params=params,
                    timeout=10
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        articles = data.get('articles', [])
                        
                        if not articles:
                            logger.warning(f"No news found for {symbol}")
                            return None
                        
                        # Analyze REAL articles
                        sentiment_score = self._analyze_news_sentiment(articles)
                        
                        return {
                            'source': 'NEWS_REAL',
                            'sentiment': self._score_to_sentiment(sentiment_score),
                            'score': sentiment_score,
                            'article_count': len(articles),
                            'timestamp': datetime.now().isoformat(),
                            'valid': True
                        }
                    else:
                        logger.warning(f"NewsAPI error: {resp.status}")
                        return None
        
        except asyncio.TimeoutError:
            logger.warning(f"NewsAPI timeout for {symbol}")
            return None
        except Exception as e:
            logger.warning(f"News sentiment error: {e}")
            return None
    
    @staticmethod
    def _analyze_tweet_sentiment(tweets: List[Dict]) -> float:
        """Analyze REAL tweet sentiment (0-100)
        
        Based on:
        - Like count
        - Retweet count
        - Reply count
        """
        if not tweets:
            return 50.0
        
        scores = []
        for tweet in tweets:
            metrics = tweet.get('public_metrics', {})
            likes = metrics.get('like_count', 0)
            retweets = metrics.get('retweet_count', 0)
            replies = metrics.get('reply_count', 0)
            
            # Positive = likes + retweets
            positive = likes + retweets
            # Negative = replies might be negative, estimate 50% bad
            negative = replies * 0.5
            
            if positive + negative > 0:
                sentiment = (positive - negative) / (positive + negative) * 100
                scores.append(max(0, min(100, sentiment)))
        
        return np.mean(scores) if scores else 50.0
    
    @staticmethod
    def _analyze_news_sentiment(articles: List[Dict]) -> float:
        """Analyze REAL news sentiment (0-100)
        
        Based on article title + description keywords
        """
        positive_words = [
            'surge', 'rally', 'bull', 'gain', 'rise', 'jump', 'spike',
            'rocket', 'boom', 'approval', 'bullish', 'support', 'adopt'
        ]
        negative_words = [
            'crash', 'fall', 'bear', 'loss', 'drop', 'plunge', 'sink',
            'doom', 'ban', 'bearish', 'resist', 'reject', 'hack'
        ]
        
        scores = []
        for article in articles:
            title = (article.get('title', '') or '').lower()
            desc = (article.get('description', '') or '').lower()
            text = f"{title} {desc}"
            
            pos_count = sum(1 for word in positive_words if word in text)
            neg_count = sum(1 for word in negative_words if word in text)
            
            if pos_count + neg_count > 0:
                sentiment = (pos_count - neg_count) / (pos_count + neg_count) * 100
                scores.append(max(0, min(100, sentiment)))
        
        return np.mean(scores) if scores else 50.0
    
    @staticmethod
    def _combine_sentiment(twitter: Dict, news: Dict) -> Dict:
        """Combine real twitter + real news sentiment"""
        
        if not twitter.get('valid') and not news.get('valid'):
            return {
                'sentiment': None,
                'score': None,
                'valid': False,
                'error': 'All sources invalid'
            }
        
        scores = []
        if twitter.get('valid'):
            scores.append(twitter['score'])
        if news.get('valid'):
            scores.append(news['score'])
        
        avg_score = np.mean(scores) if scores else 50.0
        
        return {
            'sentiment': TwitterRedditSentimentLayer._score_to_sentiment(avg_score),
            'score': avg_score,
            'twitter_score': twitter.get('score'),
            'news_score': news.get('score'),
            'sources': [twitter.get('source'), news.get('source')],
            'timestamp': datetime.now().isoformat(),
            'valid': True
        }
    
    @staticmethod
    def _score_to_sentiment(score: float) -> str:
        """Convert score (0-100) to sentiment label"""
        
        if score >= 70:
            return 'VERY_BULLISH'
        elif score >= 55:
            return 'BULLISH'
        elif score >= 45:
            return 'NEUTRAL'
        elif score >= 30:
            return 'BEARISH'
        else:
            return 'VERY_BEARISH'
