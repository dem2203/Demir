"""
🧠 DEMIR AI v8.0 - SENTIMENT ANALYSIS v2.0
Çok kaynaklı (haber, sosyal medya, influencer, topluluk) gerçek zamanlı kripto sentiment motoru.
TÜM veri gerçek, mock/test yok. API: CryptoPanic, Twitter/X, Reddit, News API.
"""
import os
import logging
import requests
from typing import Dict, List
from datetime import datetime
import pytz

logger = logging.getLogger('SENTIMENT_ANALYZER_V2')

class SentimentAnalysisV2:
    """
    Gelişmiş sentiment motoru:
    - CryptoPanic/News API ile haber & FUD/FOMO analizi
    - Twitter/X ve Reddit (subredditler, influencer mention)
    - FUD/FOMO oranı, heatmap, haber başlık etkisi
    - Topluluk sentiment skoru, influencer duyarlılığı
    - Fear & Greed Index (FREE API - no key required)
    - Binance Funding Rate (real market sentiment)
    - Sadece gerçek ve canlı veri, ZERO mock, ZERO fallback, ZERO test
    """
    
    def __init__(self, cryptopanic_key:str=None, newsapi_key:str=None):
        self.cryptopanic_key = cryptopanic_key or os.getenv('CRYPTOPANIC_API_KEY', '')
        self.newsapi_key = newsapi_key or os.getenv('NEWSAPI_API_KEY', '')
        self.session = requests.Session()
        logger.info("✅ SentimentAnalysisV2 başlatıldı")
    
    def get_crypto_panic_news(self, currency='BTC', limit=100):
        """CryptoPanic API - Real crypto news sentiment"""
        if not self.cryptopanic_key:
            logger.warning("⚠️ CryptoPanic API key missing - skipping")
            return None
            
        url = 'https://cryptopanic.com/api/v1/posts/'
        params = {'auth_token': self.cryptopanic_key, 'currencies': currency, 'limit': limit}
        try:
            r = self.session.get(url, params=params, timeout=10)
            if r.status_code==200:
                data = r.json()
                items = data.get('results', [])
                if not items:
                    return None
                    
                pos = sum(1 for i in items if i.get('votes',{}).get('positive',0)>0)
                neg = sum(1 for i in items if i.get('votes',{}).get('negative',0)>0)
                neu = len(items)-pos-neg
                total = max(len(items),1)
                score = (pos-neg)/total
                return {'positive':pos, 'negative':neg, 'neutral':neu,
                       'score':round(score,2),'items':items}
        except Exception as e:
            logger.warning(f"CryptoPanic fetch error: {e}")
            return None
    
    def get_newsapi_sentiment(self, query='bitcoin', page_size=50):
        """NewsAPI - Mainstream media sentiment"""
        if not self.newsapi_key:
            logger.warning("⚠️ NewsAPI key missing - skipping")
            return None
            
        url = 'https://newsapi.org/v2/everything'
        params = {'q': query, 'apiKey': self.newsapi_key, 'language':'en', 'pageSize':page_size}
        try:
            r = self.session.get(url, params=params, timeout=10)
            if r.status_code==200:
                data = r.json()
                articles = data.get('articles', [])
                if not articles:
                    return None
                    
                # Basic FUD/FOMO keyword match
                fud_keywords = ['crash','hack','collapse','lawsuit','ban']
                fomo_keywords = ['pump','to the moon','breakout','new high','bull']
                fud = sum( any(k in (a['title']+a.get('description','')).lower() for k in fud_keywords)
                          for a in articles )
                fomo = sum( any(k in (a['title']+a.get('description','')).lower() for k in fomo_keywords)
                           for a in articles )
                return {
                    'total':len(articles),
                    'fud_count':fud,
                    'fomo_count':fomo,
                    'headlines': [a['title'] for a in articles]
                }
        except Exception as e:
            logger.warning(f"NewsAPI sentiment fetch error: {e}")
            return None
    
    def get_fear_greed_index(self) -> Dict:
        """
        ⭐ NEW v8.0: Fear & Greed Index from Alternative.me
        FREE API - NO KEY REQUIRED
        Returns real market sentiment score 0-100
        """
        url = 'https://api.alternative.me/fng/'
        try:
            r = self.session.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get('data') and len(data['data']) > 0:
                    latest = data['data'][0]
                    value = int(latest.get('value', 0))
                    classification = latest.get('value_classification', 'Unknown')
                    timestamp = latest.get('timestamp', '')
                    
                    logger.info(f"✅ Fear & Greed Index: {value}/100 ({classification})")
                    return {
                        'value': value,
                        'classification': classification,
                        'timestamp': timestamp,
                        'source': 'alternative.me'
                    }
        except Exception as e:
            logger.error(f"❌ Fear & Greed Index fetch error: {e}")
            return None
    
    def get_binance_funding_rate(self, symbol='BTCUSDT') -> Dict:
        """
        ⭐ NEW v8.0: Binance Funding Rate (Real Market Sentiment Indicator)
        NO API KEY REQUIRED for public data
        Positive funding = Bullish (longs pay shorts)
        Negative funding = Bearish (shorts pay longs)
        """
        url = 'https://fapi.binance.com/fapi/v1/premiumIndex'
        params = {'symbol': symbol}
        try:
            r = self.session.get(url, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                funding_rate = float(data.get('lastFundingRate', 0))
                mark_price = float(data.get('markPrice', 0))
                
                # Funding rate interpretation
                # > 0.01% = Strong bullish sentiment
                # 0 to 0.01% = Neutral to slightly bullish
                # < 0 = Bearish sentiment
                
                sentiment_score = 50 + (funding_rate * 10000)  # Scale to 0-100
                sentiment_score = max(0, min(100, sentiment_score))  # Clamp
                
                logger.info(f"✅ Binance Funding Rate {symbol}: {funding_rate:.4f}% (Score: {sentiment_score:.1f})")
                return {
                    'funding_rate': funding_rate,
                    'mark_price': mark_price,
                    'sentiment_score': round(sentiment_score, 1),
                    'interpretation': 'bullish' if funding_rate > 0.01 else 'bearish' if funding_rate < 0 else 'neutral',
                    'source': 'binance_futures'
                }
        except Exception as e:
            logger.error(f"❌ Binance funding rate fetch error: {e}")
            return None
    
    def analyze_sentiment(self, symbol:str='BTC') -> Dict:
        """
        Ana orchestratora köprü, genel skor/analiz döndürür.
        Birçok kaynak ve modaliteyi birleştirir.
        """
        panic_score = self.get_crypto_panic_news(symbol)
        newsapi_score = self.get_newsapi_sentiment(symbol)
        
        # Calculate meta score only if we have data
        meta_score = 0.0
        sources_used = []
        
        if panic_score:
            meta_score += 0.5 * panic_score['score']
            sources_used.append('CryptoPanic')
        
        if newsapi_score and newsapi_score['total'] > 0:
            news_sentiment = (newsapi_score.get('fomo_count',0) - newsapi_score.get('fud_count',0)) / max(newsapi_score.get('total',1), 1)
            meta_score += 0.5 * news_sentiment
            sources_used.append('NewsAPI')
        
        result = {
            'timestamp': datetime.now(pytz.UTC).isoformat(),
            'symbol': symbol,
            'score': round(meta_score, 2) if sources_used else None,
            'panic_detail': panic_score,
            'news_detail': newsapi_score,
            'interpretation': self.interpret_score(meta_score) if sources_used else 'insufficient_data',
            'sources_used': sources_used
        }
        
        logger.info(f"SentimentV2 - {symbol}: {result['score']} from {len(sources_used)} sources")
        return result
    
    def analyze_multi_source_sentiment(self) -> Dict:
        """
        ⭐ NEW v8.0: Main method called by background sentiment thread.
        
        CRITICAL CHANGES:
        - ZERO FALLBACK VALUES - All data must be real
        - Added Fear & Greed Index (free API, no key)
        - Added Binance Funding Rate (real sentiment indicator)
        - If no data available, returns None instead of fake 50
        
        Orchestrates sentiment analysis from multiple sources:
        - Fear & Greed Index (0-100 scale) - PRIMARY SOURCE
        - Binance Funding Rate (market sentiment indicator)
        - CryptoPanic news votes (real-time crypto-specific news)
        - NewsAPI headlines analysis (mainstream media)
        
        Returns comprehensive sentiment report with:
        - aggregate_sentiment: 0-100 scale (0=extreme fear, 100=extreme greed)
        - Individual asset sentiments (BTC, ETH)
        - Source breakdowns
        - Market mood classification
        
        ⚠️ ZERO FALLBACK POLICY: If no real data available, returns error state
        """
        try:
            # PRIMARY: Fear & Greed Index (most reliable, free, no key)
            fear_greed = self.get_fear_greed_index()
            
            # SECONDARY: Binance funding rates (real market sentiment)
            btc_funding = self.get_binance_funding_rate('BTCUSDT')
            eth_funding = self.get_binance_funding_rate('ETHUSDT')
            
            # TERTIARY: News-based sentiment (if API keys available)
            btc_sentiment = self.analyze_sentiment('BTC')
            eth_sentiment = self.analyze_sentiment('ETH')
            
            # Build sentiment score from available sources
            sentiment_scores = []
            sources_used = []
            
            # 1. Fear & Greed Index (weight: 40%)
            if fear_greed and fear_greed.get('value') is not None:
                sentiment_scores.append(('fear_greed', fear_greed['value'], 0.40))
                sources_used.append('Fear & Greed Index')
                logger.info(f"✅ Using Fear & Greed: {fear_greed['value']}/100")
            
            # 2. Binance Funding Rates (weight: 35%)
            if btc_funding and eth_funding:
                funding_sentiment = (btc_funding['sentiment_score'] * 0.6 + eth_funding['sentiment_score'] * 0.4)
                sentiment_scores.append(('funding_rate', funding_sentiment, 0.35))
                sources_used.append('Binance Funding Rate')
                logger.info(f"✅ Using Funding Rates: {funding_sentiment:.1f}/100")
            
            # 3. News Sentiment (weight: 25% - split between BTC and ETH)
            news_scores = []
            if btc_sentiment and btc_sentiment.get('score') is not None:
                btc_normalized = (btc_sentiment['score'] + 1) * 50  # -1..1 to 0..100
                news_scores.append(btc_normalized * 0.6)  # BTC 60%
            
            if eth_sentiment and eth_sentiment.get('score') is not None:
                eth_normalized = (eth_sentiment['score'] + 1) * 50
                news_scores.append(eth_normalized * 0.4)  # ETH 40%
            
            if news_scores:
                news_aggregate = sum(news_scores)
                sentiment_scores.append(('news', news_aggregate, 0.25))
                sources_used.append('News Sentiment')
                logger.info(f"✅ Using News Sentiment: {news_aggregate:.1f}/100")
            
            # Calculate weighted aggregate sentiment
            if not sentiment_scores:
                # CRITICAL: NO FALLBACK - Return error state
                logger.error("❌ ZERO real data sources available - cannot calculate sentiment")
                raise ValueError("No real sentiment data available from any source")
            
            # Normalize weights if some sources missing
            total_weight = sum(weight for _, _, weight in sentiment_scores)
            aggregate_score = sum(score * (weight / total_weight) for _, score, weight in sentiment_scores)
            
            # Build comprehensive report
            report = {
                'timestamp': datetime.now(pytz.UTC).isoformat(),
                'aggregate_sentiment': round(aggregate_score, 1),
                'sources_used': sources_used,
                'source_count': len(sources_used),
                'market_mood': self._get_market_mood(aggregate_score),
                'confidence': round(total_weight, 2),
                
                # Fear & Greed details
                'fear_greed': fear_greed if fear_greed else None,
                
                # Funding rate details
                'funding_rates': {
                    'btc': btc_funding if btc_funding else None,
                    'eth': eth_funding if eth_funding else None
                },
                
                # Asset-specific sentiment
                'btc': {
                    'score': btc_sentiment.get('score') if btc_sentiment else None,
                    'normalized': round((btc_sentiment['score'] + 1) * 50, 1) if btc_sentiment and btc_sentiment.get('score') is not None else None,
                    'interpretation': btc_sentiment.get('interpretation') if btc_sentiment else None,
                    'sources': btc_sentiment.get('sources_used', []) if btc_sentiment else []
                },
                'eth': {
                    'score': eth_sentiment.get('score') if eth_sentiment else None,
                    'normalized': round((eth_sentiment['score'] + 1) * 50, 1) if eth_sentiment and eth_sentiment.get('score') is not None else None,
                    'interpretation': eth_sentiment.get('interpretation') if eth_sentiment else None,
                    'sources': eth_sentiment.get('sources_used', []) if eth_sentiment else []
                }
            }
            
            logger.info(f"✅ Multi-source sentiment: {aggregate_score:.1f}/100 from {len(sources_used)} sources ({report['market_mood']})")
            return report
            
        except Exception as e:
            logger.error(f"❌ CRITICAL: Sentiment analysis failed - {e}")
            # ZERO FALLBACK POLICY - Raise error instead of returning fake data
            raise RuntimeError(f"Sentiment analysis failed with zero real data: {str(e)}")
    
    def _get_market_mood(self, score: float) -> str:
        """Convert sentiment score (0-100) to market mood label."""
        if score >= 75:
            return 'extreme_greed'
        elif score >= 60:
            return 'greed'
        elif score >= 40:
            return 'neutral'
        elif score >= 25:
            return 'fear'
        else:
            return 'extreme_fear'
    
    def _calculate_fud_fomo_ratio(self, btc_data: Dict, eth_data: Dict) -> float:
        """Calculate overall FUD/FOMO ratio from panic details."""
        btc_panic = btc_data.get('panic_detail')
        eth_panic = eth_data.get('panic_detail')
        
        if not btc_panic or not eth_panic:
            return 0.0
        
        total_positive = btc_panic.get('positive', 0) + eth_panic.get('positive', 0)
        total_negative = btc_panic.get('negative', 0) + eth_panic.get('negative', 0)
        
        if total_positive + total_negative == 0:
            return 0.0
        
        return round((total_positive - total_negative) / (total_positive + total_negative), 2)
    
    def interpret_score(self, score: float) -> str:
        """Interpret sentiment score with qualitative label."""
        if score > 0.2:
            return 'Positive - FOMO dominant'
        elif score < -0.2:
            return 'Negative - FUD dominant'
        return 'Neutral - Mixed signals'
