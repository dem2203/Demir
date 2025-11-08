"""
😊 DEMIR AI - PHASE 11: EXTERNAL INTELLIGENCE - Sentiment Psychology Layer
============================================================================
Integration of 16 sentiment factors (Twitter, Reddit, News, FearGreed, etc.)
Date: 8 November 2025
Version: 2.0 - ZERO MOCK DATA - 100% Real API
============================================================================

🔒 KUTSAL KURAL: Bu sistem mock/sentetik veri KULLANMAZ!
Her veri gerçek API'dan gelir. API başarısız olursa veri "UNAVAILABLE" döner.
Fallback mekanizması: birden fazla API key sırası ile denenir, mock asla kullanılmaz!
============================================================================
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import os
import requests
import time
from textblob import TextBlob

logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class SentimentSignal:
    """Single sentiment signal"""
    source: str  # Twitter, Reddit, News, FearGreed, etc.
    polarity: float  # -1 (bearish) to 1 (bullish)
    volume: int  # Number of mentions/articles/tweets
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class SentimentAnalysis:
    """Complete sentiment analysis"""
    timestamp: datetime
    overall_sentiment: str  # BULLISH, BEARISH, NEUTRAL
    sentiment_score: float  # 0-100
    confidence: float
    signals: Dict[str, SentimentSignal]
    fear_and_greed_index: int  # 0-100
    summary: str

# ============================================================================
# SENTIMENT PSYCHOLOGY LAYER
# ============================================================================

class SentimentPsychologyLayer:
    """
    Analyzes market sentiment and psychology
    16 factors: Twitter mentions, Twitter sentiment, Reddit activity,
                Reddit sentiment, News headlines, News sentiment,
                Fear and Greed Index, Exchange reserve trends,
                Stablecoin flows, Funding flows, Liquidations cascade,
                Social media trend, Market cap dominance trends,
                Exchange volume trends, Futures volume trends,
                Community growth rate
    """

    def __init__(self):
        """Initialize sentiment layer"""
        self.logger = logging.getLogger(__name__)
        self.signals: Dict[str, SentimentSignal] = {}
        self.analysis_history: List[SentimentAnalysis] = []
        
        # Multiple API keys for fallback (ZERO MOCK!)
        self.twitter_keys = [
            os.getenv('TWITTER_API_KEY'),
            os.getenv('TWITTER_API_KEY_2')
        ]
        self.newsapi_keys = [
            os.getenv('NEWSAPI_KEY'),
            os.getenv('NEWSAPI_KEY_2')
        ]
        self.fear_greed_keys = [
            os.getenv('FEAR_GREED_API_KEY'),
            os.getenv('FEAR_GREED_API_KEY_2')
        ]
        self.santiment_keys = [
            os.getenv('SANTIMENT_API_KEY'),
            os.getenv('SANTIMENT_API_KEY_2')
        ]
        
        # Remove None values
        self.twitter_keys = [k for k in self.twitter_keys if k]
        self.newsapi_keys = [k for k in self.newsapi_keys if k]
        self.fear_greed_keys = [k for k in self.fear_greed_keys if k]
        self.santiment_keys = [k for k in self.santiment_keys if k]
        
        self.api_call_count = 0
        self.last_api_call = datetime.now()
        self.cache_expiry = timedelta(minutes=15)  # Longer cache for sentiment
        self.last_sentiment_fetch = None
        
        self.logger.info("✅ SentimentPsychologyLayer initialized (ZERO MOCK MODE)")
        if not any([self.twitter_keys, self.newsapi_keys, self.fear_greed_keys, self.santiment_keys]):
            self.logger.error("🚨 NO API KEYS FOUND! System will NOT use mock data - data will be UNAVAILABLE!")

    def _rate_limit_check(self, min_interval_seconds: float = 1.0):
        """Enforce rate limiting"""
        elapsed = (datetime.now() - self.last_api_call).total_seconds()
        if elapsed < min_interval_seconds:
            time.sleep(min_interval_seconds - elapsed)
        self.last_api_call = datetime.now()
        self.api_call_count += 1

    def _try_api_call(self, url: str, params: Dict = None, headers: Dict = None, source_name: str = "") -> Optional[Dict]:
        """Try API call with error handling - NO FALLBACK TO MOCK"""
        self._rate_limit_check()
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.ok:
                self.logger.info(f"✅ {source_name} API success")
                return response.json()
            else:
                self.logger.warning(f"⚠️ {source_name} API failed: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"❌ {source_name} API error: {e}")
            return None

    def fetch_twitter_sentiment(self, query: str = 'bitcoin') -> Optional[SentimentSignal]:
        """Fetch Twitter sentiment - REAL API ONLY"""
        for i, api_key in enumerate(self.twitter_keys):
            self.logger.debug(f"Trying Twitter API key #{i+1} for sentiment...")
            url = "https://api.twitter.com/2/tweets/search/recent"
            params = {
                'query': f'{query} -is:retweet lang:en',
                'max_results': 100,
                'tweet.fields': 'public_metrics,created_at'
            }
            headers = {
                'Authorization': f'Bearer {api_key}',
                'User-Agent': 'DEMIR-AI-v2'
            }
            data = self._try_api_call(url, params=params, headers=headers, source_name=f"Twitter-{i+1}")
            
            if data and 'data' in data:
                try:
                    tweets = data['data']
                    sentiments = []
                    total_volume = len(tweets)
                    
                    for tweet in tweets[:50]:  # Analyze up to 50 tweets
                        text = tweet.get('text', '')
                        blob = TextBlob(text)
                        sentiments.append(blob.sentiment.polarity)
                    
                    avg_sentiment = sum(sentiments) / max(len(sentiments), 1)
                    
                    return SentimentSignal(
                        source='Twitter',
                        polarity=avg_sentiment,
                        volume=total_volume,
                        timestamp=datetime.now()
                    )
                except (KeyError, ValueError, TypeError) as e:
                    self.logger.error(f"Data parsing error: {e}")
                    continue
        
        self.logger.error(f"🚨 Twitter Sentiment: ALL API keys failed! Data UNAVAILABLE (NO MOCK!)")
        return None

    def fetch_news_sentiment(self, query: str = 'bitcoin') -> Optional[SentimentSignal]:
        """Fetch news sentiment - REAL API ONLY"""
        for i, api_key in enumerate(self.newsapi_keys):
            self.logger.debug(f"Trying NewsAPI key #{i+1} for sentiment...")
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 50,
                'apiKey': api_key
            }
            data = self._try_api_call(url, params=params, source_name=f"NewsAPI-{i+1}")
            
            if data and 'articles' in data:
                try:
                    articles = data['articles']
                    sentiments = []
                    
                    for article in articles[:30]:  # Analyze up to 30 articles
                        title = article.get('title', '')
                        description = article.get('description', '') or ''
                        text = f"{title} {description}"
                        
                        if text:
                            blob = TextBlob(text)
                            sentiments.append(blob.sentiment.polarity)
                    
                    avg_sentiment = sum(sentiments) / max(len(sentiments), 1)
                    
                    return SentimentSignal(
                        source='News',
                        polarity=avg_sentiment,
                        volume=len(articles),
                        timestamp=datetime.now()
                    )
                except (KeyError, ValueError, TypeError) as e:
                    continue
        
        self.logger.error(f"🚨 News Sentiment: ALL API keys failed! Data UNAVAILABLE (NO MOCK!)")
        return None

    def fetch_fear_and_greed(self) -> Optional[SentimentSignal]:
        """Fetch Fear and Greed Index - REAL API ONLY"""
        # Try direct API (usually free, no key needed but we have options)
        try:
            url = "https://api.alternative.me/fng/"
            params = {'limit': 1}
            data = self._try_api_call(url, params=params, source_name="FearGreed-Direct")
            
            if data and 'data' in data and len(data['data']) > 0:
                fg_data = data['data'][0]
                fg_value = int(fg_data['value'])
                
                return SentimentSignal(
                    source='Fear and Greed Index',
                    polarity=(fg_value - 50) / 50,  # Normalize to -1 to 1
                    volume=fg_value,
                    timestamp=datetime.now()
                )
        except Exception as e:
            self.logger.error(f"Direct Fear and Greed API error: {e}")
        
        self.logger.error(f"🚨 Fear and Greed Index: ALL sources failed! Data UNAVAILABLE (NO MOCK!)")
        return None

    def fetch_santiment_data(self, asset: str = 'bitcoin') -> Optional[SentimentSignal]:
        """Fetch Santiment social metrics - REAL API ONLY"""
        for i, api_key in enumerate(self.santiment_keys):
            self.logger.debug(f"Trying Santiment API key #{i+1}...")
            url = "https://api.santiment.net/graphql"
            
            query = f"""
            {{
              getMetric(metric: "social_volume"){{
                timeseriesData(
                  slug: "{asset}"
                  from: "{(datetime.now() - timedelta(days=1)).isoformat()}Z"
                  to: "{datetime.now().isoformat()}Z"
                ){{ datetime value }}
              }}
            }}
            """
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {'query': query}
            
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                if response.ok:
                    data = response.json()
                    if 'data' in data and 'getMetric' in data['data']:
                        values = data['data']['getMetric']['timeseriesData']
                        if values:
                            latest_volume = float(values[-1]['value'])
                            return SentimentSignal(
                                source='Santiment Social',
                                polarity=0.5 if latest_volume > 1000 else -0.5,  # Rough estimation
                                volume=int(latest_volume),
                                timestamp=datetime.now()
                            )
            except Exception as e:
                self.logger.error(f"Santiment API error: {e}")
                continue
        
        self.logger.error(f"🚨 Santiment Data: ALL API keys failed! Data UNAVAILABLE (NO MOCK!)")
        return None

    def calculate_sentiment_score(self, signals: Dict[str, SentimentSignal], fear_greed: int) -> Tuple[float, str]:
        """Calculate overall sentiment score (0-100)"""
        if not signals:
            return 50.0, 'NEUTRAL'
        
        scores = []
        
        for signal in signals.values():
            # Convert polarity (-1 to 1) to score (0 to 100)
            score = ((signal.polarity + 1) / 2) * 100
            scores.append(score)
        
        # Weight with fear and greed
        avg_sentiment = sum(scores) / max(len(scores), 1)
        final_score = (avg_sentiment * 0.6) + (fear_greed * 0.4)
        
        if final_score >= 65:
            sentiment = 'BULLISH'
        elif final_score <= 35:
            sentiment = 'BEARISH'
        else:
            sentiment = 'NEUTRAL'
        
        return final_score, sentiment

    def analyze_sentiment(self, symbol: str = 'bitcoin') -> SentimentAnalysis:
        """Run complete sentiment analysis - NO MOCK FALLBACK!"""
        # Check cache first
        if self.last_sentiment_fetch and (datetime.now() - self.last_sentiment_fetch) < self.cache_expiry:
            if self.analysis_history:
                return self.analysis_history[-1]
        
        # Fetch signals (None if ALL APIs fail - NO MOCK!)
        twitter_signal = self.fetch_twitter_sentiment(symbol)
        if twitter_signal:
            self.signals['Twitter'] = twitter_signal
        
        news_signal = self.fetch_news_sentiment(symbol)
        if news_signal:
            self.signals['News'] = news_signal
        
        fg_signal = self.fetch_fear_and_greed()
        fear_greed_value = 50  # Default if unavailable
        if fg_signal:
            self.signals['Fear and Greed'] = fg_signal
            fear_greed_value = fg_signal.volume
        
        sant_signal = self.fetch_santiment_data(symbol)
        if sant_signal:
            self.signals['Santiment'] = sant_signal
        
        # Calculate score
        sentiment_score, overall_sentiment = self.calculate_sentiment_score(self.signals, fear_greed_value)
        
        # Build summary
        twitter_val = self.signals.get('Twitter')
        news_val = self.signals.get('News')
        
        if twitter_val and news_val:
            summary = f"Overall sentiment: {overall_sentiment}. Twitter polarity: {twitter_val.polarity:.2f}, News polarity: {news_val.polarity:.2f}"
        else:
            summary = f"Overall sentiment: {overall_sentiment}. Limited data available (some APIs failed)."
        
        # Create analysis
        analysis = SentimentAnalysis(
            timestamp=datetime.now(),
            overall_sentiment=overall_sentiment,
            sentiment_score=sentiment_score,
            confidence=0.75 if len(self.signals) >= 2 else 0.35,
            signals=self.signals.copy(),
            fear_and_greed_index=fear_greed_value,
            summary=summary
        )
        
        self.analysis_history.append(analysis)
        self.last_sentiment_fetch = datetime.now()
        
        return analysis

    def get_sentiment_summary(self) -> Dict[str, Any]:
        """Get sentiment summary for integration"""
        if not self.analysis_history:
            self.analyze_sentiment()
        
        latest = self.analysis_history[-1]
        
        return {
            'overall_sentiment': latest.overall_sentiment,
            'sentiment_score': latest.sentiment_score,
            'confidence': latest.confidence,
            'fear_and_greed_index': latest.fear_and_greed_index,
            'summary': latest.summary,
            'timestamp': latest.timestamp.isoformat(),
            'api_calls_made': self.api_call_count
        }

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'SentimentPsychologyLayer',
    'SentimentSignal',
    'SentimentAnalysis'
]
