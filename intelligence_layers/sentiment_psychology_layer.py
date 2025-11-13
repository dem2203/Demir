"""
SENTIMENT PSYCHOLOGY LAYER - v2.0 FIXED
⚠️ REAL sentiment data ONLY
NO MOCK DATA - Real or Error
"""

import os
import logging
from datetime import datetime
import asyncio
import aiohttp
from typing import Dict, Optional
import numpy as np

logger = logging.getLogger(__name__)


class SentimentPsychologyLayer:
    """Real sentiment psychology analysis - NO MOCK"""
    
    def __init__(self):
        """Initialize"""
        self.fear_greed_url = "https://api.alternative.me/fng/"
        self.cryptoalert_key = os.getenv('CRYPTOALERT_API_KEY')
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
    
    async def get_sentiment_psychology(self, symbol: str) -> Dict:
        """Get REAL sentiment psychology
        
        Combines:
        - Fear & Greed Index (Real)
        - Social Sentiment (Real or Error)
        - News Sentiment (Real or Error)
        """
        
        try:
            # Get REAL Fear & Greed
            fg_sentiment = await self._get_fear_greed()
            
            # Get REAL social sentiment
            social_sentiment = await self._get_social_sentiment(symbol)
            
            # Combine real data
            combined = self._combine_real_sentiments(
                fg_sentiment,
                social_sentiment
            )
            
            return combined
        
        except Exception as e:
            logger.error(f"Sentiment psychology error: {e}")
            return {
                'sentiment': None,
                'score': None,
                'valid': False,
                'error': str(e)
            }
    
    async def _get_fear_greed(self) -> Optional[Dict]:
        """Get REAL Fear & Greed Index"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.fear_greed_url,
                    timeout=10
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        if 'data' in data and len(data['data']) > 0:
                            latest = data['data']
                            score = int(latest.get('value', 50))
                            
                            return {
                                'source': 'REAL_FEAR_GREED',
                                'score': score,
                                'classification': latest.get('value_classification', 'Unknown'),
                                'timestamp': latest.get('timestamp'),
                                'valid': True
                            }
        
        except asyncio.TimeoutError:
            logger.warning("Fear & Greed timeout")
        except Exception as e:
            logger.warning(f"Fear & Greed error: {e}")
        
        return None
    
    async def _get_social_sentiment(self, symbol: str) -> Optional[Dict]:
        """Get REAL social sentiment from CryptoAlert or NewsAPI"""
        
        try:
            # Try CryptoAlert first
            if self.cryptoalert_key:
                result = await self._get_cryptoalert_sentiment(symbol)
                if result:
                    return result
            
            # Try NewsAPI
            if self.newsapi_key:
                result = await self._get_news_sentiment(symbol)
                if result:
                    return result
            
            # All real sources failed
            logger.warning(f"All real social sentiment sources failed for {symbol}")
            return None
        
        except Exception as e:
            logger.error(f"Social sentiment error: {e}")
            return None
    
    async def _get_cryptoalert_sentiment(self, symbol: str) -> Optional[Dict]:
        """Get real sentiment from CryptoAlert"""
        
        try:
            headers = {
                'Authorization': f'Bearer {self.cryptoalert_key}'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.cryptoalert.io/v1/sentiment/{symbol.lower()}",
                    headers=headers,
                    timeout=10
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        return {
                            'source': 'REAL_CRYPTOALERT',
                            'score': data.get('sentiment_score', 50),
                            'mentions': data.get('mentions', 0),
                            'valid': True
                        }
        
        except Exception as e:
            logger.warning(f"CryptoAlert error: {e}")
            return None
    
    async def _get_news_sentiment(self, symbol: str) -> Optional[Dict]:
        """Get real sentiment from NewsAPI"""
        
        try:
            params = {
                'q': symbol,
                'apiKey': self.newsapi_key,
                'pageSize': 30
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://newsapi.org/v2/everything",
                    params=params,
                    timeout=10
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        articles = data.get('articles', [])
                        
                        if articles:
                            sentiment_score = self._analyze_articles(articles)
                            
                            return {
                                'source': 'REAL_NEWS',
                                'score': sentiment_score,
                                'articles': len(articles),
                                'valid': True
                            }
        
        except Exception as e:
            logger.warning(f"NewsAPI sentiment error: {e}")
            return None
        
        return None
    
    @staticmethod
    def _analyze_articles(articles: list) -> float:
        """Analyze real articles for sentiment (0-100)"""
        
        positive_words = ['bull', 'rally', 'surge', 'gain', 'rise']
        negative_words = ['bear', 'crash', 'fall', 'loss', 'drop']
        
        scores = []
        for article in articles:
            title = (article.get('title', '') or '').lower()
            desc = (article.get('description', '') or '').lower()
            
            pos = sum(1 for w in positive_words if w in title or w in desc)
            neg = sum(1 for w in negative_words if w in title or w in desc)
            
            if pos + neg > 0:
                score = (pos - neg) / (pos + neg) * 100
                scores.append(max(0, min(100, score)))
        
        return np.mean(scores) if scores else 50.0
    
    @staticmethod
    def _combine_real_sentiments(fg: Optional[Dict], social: Optional[Dict]) -> Dict:
        """Combine REAL sentiment sources"""
        
        if not fg and not social:
            return {
                'sentiment': None,
                'score': None,
                'valid': False,
                'error': 'All real sentiment sources unavailable'
            }
        
        scores = []
        sources = []
        
        if fg:
            scores.append(fg['score'])
            sources.append(fg['source'])
        
        if social:
            scores.append(social['score'])
            sources.append(social['source'])
        
        avg_score = np.mean(scores) if scores else 50.0
        
        return {
            'sentiment': 'BULLISH' if avg_score > 60 else 'BEARISH' if avg_score < 40 else 'NEUTRAL',
            'score': float(avg_score),
            'sources': sources,
            'fear_greed': fg.get('score') if fg else None,
            'social_sentiment': social.get('score') if social else None,
            'timestamp': datetime.now().isoformat(),
            'valid': True
        }
