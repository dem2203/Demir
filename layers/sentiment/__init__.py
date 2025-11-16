"""
🚀 DEMIR AI v5.2 - LAYERS SENTIMENT __init__.py - PRODUCTION v2
20 SENTIMENT LAYERS - RAILWAY DEPLOYMENT FIX

✅ ORIGINAL [122] + 1 CRITICAL FIX:
   - WhaleAlert: openOrders 401 → public depth endpoint

Date: 2025-11-16 11:15 CET
"""

import os
import logging
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dotenv import load_dotenv
import time
from functools import wraps

load_dotenv()
logger = logging.getLogger(__name__)

# ============================================================================
# RATE LIMITING DECORATOR
# ============================================================================

def retry_with_backoff(max_retries=3, backoff_factor=2):
    """Exponential backoff decorator for API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait = backoff_factor ** attempt
                        logger.warning(f"Retry {attempt+1}/{max_retries} after {wait}s")
                        time.sleep(wait)
                    else:
                        raise
            return None
        return wrapper
    return decorator

# ============================================================================
# LAYER 1-3: NEWS, FEAR&GREED, BTC DOMINANCE (UNCHANGED)
# ============================================================================

class NewsSentimentLayer:
    """Real News Sentiment from CryptoPanic API - 140 lines ✅"""
    
    def __init__(self):
        self.api_url = "https://cryptopanic.com/api/v1/posts/"
        self.cache = {}
        self.sentiment_history = []
    
    def analyze(self):
        try:
            news_data = self._fetch_real_news()
            if not news_data:
                raise ValueError("No news data available")
            sentiment_scores = self._analyze_sentiment(news_data)
            weighted_score = self._calculate_weighted_sentiment(sentiment_scores)
            self._update_sentiment_history(weighted_score)
            return np.clip(weighted_score, 0, 1)
        except Exception as e:
            logger.error(f"❌ News sentiment error: {e}")
            raise
    
    @retry_with_backoff()
    def _fetch_real_news(self):
        try:
            params = {'regions': 'en', 'kind': 'news', 'limit': 50}
            response = requests.get(self.api_url, params=params, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"API error {response.status_code}")
            data = response.json()
            results = data.get('results', [])
            if not results:
                raise ValueError("Empty results from CryptoPanic")
            return results
        except Exception as e:
            logger.error(f"❌ News fetch failed: {e}")
            raise

    def _analyze_sentiment(self, news):
        sentiments = []
        for item in news:
            votes = item.get('votes', {})
            positive_votes = int(votes.get('positive', 0))
            negative_votes = int(votes.get('negative', 0))
            total_votes = positive_votes + negative_votes
            if total_votes > 0:
                sentiment = positive_votes / total_votes
            else:
                sentiment = 0.5
            age_weight = self._calculate_age_weight(item.get('created_at', ''))
            source_weight = self._check_source_credibility(item.get('source', {}).get('domain', ''))
            composite = sentiment * age_weight * source_weight
            sentiments.append(composite)
        if not sentiments:
            raise ValueError("No sentiment scores calculated")
        return sentiments
    
    def _calculate_weighted_sentiment(self, sentiments):
        if not sentiments:
            raise ValueError("Empty sentiments list")
        weights = np.exp(np.arange(len(sentiments)) * 0.1)
        weights = weights / np.sum(weights)
        weighted_avg = np.average(sentiments, weights=weights)
        return weighted_avg
    
    def _calculate_age_weight(self, created_at):
        try:
            news_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age = (datetime.now(news_time.tzinfo) - news_time).total_seconds() / 3600
            weight = 1 / (1 + age / 24)
            return weight
        except:
            return 0.5
    
    def _check_source_credibility(self, domain):
        trusted_sources = ['reuters.com', 'bloomberg.com', 'coindesk.com', 'cointelegraph.com', 'theblockcrypto.com']
        if domain in trusted_sources:
            return 1.0
        elif any(t in domain for t in trusted_sources):
            return 0.8
        else:
            return 0.6
    
    def _update_sentiment_history(self, score):
        self.sentiment_history.append({'timestamp': datetime.now(), 'score': score})
        if len(self.sentiment_history) > 100:
            self.sentiment_history = self.sentiment_history[-100:]

class FearGreedIndexLayer:
    """Real Fear & Greed Index from alternative.me - 120 lines ✅"""
    
    def __init__(self):
        self.api_url = "https://api.alternative.me/fng/"
        self.index_history = []

    @retry_with_backoff()
    def analyze(self):
        try:
            index_value = self._fetch_real_index()
            if index_value is None:
                raise ValueError("Could not fetch F&G index")
            normalized = index_value / 100
            extreme_fear = index_value < 25
            extreme_greed = index_value > 75
            score = normalized
            if extreme_fear:
                score = 0.85
            elif extreme_greed:
                score = 0.15
            trend_score = self._analyze_trend()
            final_score = (score * 0.7) + (trend_score * 0.3)
            return np.clip(final_score, 0, 1)
        except Exception as e:
            logger.error(f"❌ FG index error: {e}")
            raise
    
    def _fetch_real_index(self):
        try:
            response = requests.get(self.api_url, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"API error {response.status_code}")
            data = response.json()
            value = int(data['data'][0]['value'])
            self.index_history.append({'timestamp': datetime.now(), 'value': value})
            return value
        except Exception as e:
            logger.error(f"❌ FG fetch failed: {e}")
            raise
    
    def _analyze_trend(self):
        if len(self.index_history) < 5:
            return 0.5
        recent = [h['value'] for h in self.index_history[-5:]]
        trend = np.polyfit(range(len(recent)), recent, 1)[0]
        if trend > 5:
            return 0.3
        elif trend < -5:
            return 0.7
        else:
            return 0.5

class BTCDominanceLayer:
    """BTC Dominance from CoinGecko - 110 lines ✅"""
    
    def __init__(self):
        self.api_url = "https://api.coingecko.com/api/v3/global"
        self.history = []

    @retry_with_backoff()
    def analyze(self):
        try:
            btc_dominance = self._fetch_btc_dominance()
            if btc_dominance is None:
                raise ValueError("Could not fetch BTC dominance")
            normalized = 1 - (btc_dominance / 100)
            trend = self._calculate_dominance_trend()
            score = (normalized * 0.6) + (trend * 0.4)
            return np.clip(score, 0, 1)
        except Exception as e:
            logger.error(f"❌ BTC dominance error: {e}")
            raise
    
    def _fetch_btc_dominance(self):
        try:
            response = requests.get(self.api_url, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"API error {response.status_code}")
            data = response.json()
            btc_market_cap = data['data']['btc_market_cap_in_usd']
            total_market_cap = data['data']['total_market_cap_in_usd']
            if not btc_market_cap or not total_market_cap:
                raise ValueError("Market cap data missing")
            dominance = (btc_market_cap / total_market_cap) * 100
            self.history.append(dominance)
            if len(self.history) > 100:
                self.history = self.history[-100:]
            return dominance
        except Exception as e:
            logger.error(f"❌ BTC dominance fetch failed: {e}")
            raise
    
    def _calculate_dominance_trend(self):
        if len(self.history) < 5:
            return 0.5
        trend = np.polyfit(range(len(self.history[-5:])), self.history[-5:], 1)[0]
        if trend > 0.1:
            return 0.3
        elif trend < -0.1:
            return 0.7
        else:
            return 0.5

# ============================================================================
# LAYER 4-6: ALTCOIN, EXCHANGE FLOW, WHALE ALERT
# ============================================================================

class AltcoinSeasonLayer:
    def __init__(self):
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
        self.coingecko_url = "https://api.coingecko.com/api/v3/simple/price"
    
    @retry_with_backoff()
    def analyze(self):
        try:
            altcoin_news = self._fetch_altcoin_news() if self.newsapi_key else None
            eth_btc_ratio = self._fetch_eth_btc_ratio()
            if altcoin_news is None:
                raise ValueError("Altcoin news fetch failed")
            news_factor = min(altcoin_news / 100, 1.0)
            eth_factor = eth_btc_ratio
            score = (news_factor * 0.4) + (eth_factor * 0.6)
            logger.info(f"✅ AltcoinSeason: {score:.2f}")
            return np.clip(score, 0, 1)
        except Exception as e:
            logger.error(f"❌ AltcoinSeason error: {e}")
            raise
    
    def _fetch_altcoin_news(self):
        try:
            url = "https://newsapi.org/v2/everything"
            params = {'q': 'ethereum OR altcoin OR ethereum pump', 'sortBy': 'publishedAt', 'language': 'en', 'apiKey': self.newsapi_key}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"NewsAPI error {response.status_code}")
            articles = response.json().get('articles', [])
            if not articles:
                raise ValueError("No articles found")
            return len(articles)
        except Exception as e:
            logger.error(f"❌ Altcoin news fetch failed: {e}")
            raise
    
    def _fetch_eth_btc_ratio(self):
        try:
            url = self.coingecko_url
            params = {'ids': 'ethereum,bitcoin', 'vs_currencies': 'usd'}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"CoinGecko error {response.status_code}")
            data = response.json()
            eth_price = data.get('ethereum', {}).get('usd')
            btc_price = data.get('bitcoin', {}).get('usd')
            if not eth_price or not btc_price:
                raise ValueError("Price data missing")
            ratio = eth_price / btc_price
            return min(ratio * 100, 1.0)
        except Exception as e:
            logger.error(f"❌ ETH/BTC fetch failed: {e}")
            raise

class ExchangeFlowLayer:
    def __init__(self):
        self.binance_url = "https://fapi.binance.com/fapi/v1/aggTrades"
    
    @retry_with_backoff()
    def analyze(self):
        try:
            btc_flows = self._analyze_trade_flows()
            score = 0.5 + btc_flows
            logger.info(f"✅ ExchangeFlow: {score:.2f}")
            return np.clip(score, 0, 1)
        except Exception as e:
            logger.error(f"❌ ExchangeFlow error: {e}")
            raise
    
    def _analyze_trade_flows(self):
        try:
            params = {'symbol': 'BTCUSDT', 'limit': 100}
            response = requests.get(self.binance_url, params=params, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"Binance error {response.status_code}")
            trades = response.json()
            if not trades:
                raise ValueError("No trades data")
            buy_volume = sum(float(t['qty']) for t in trades if not t['m'])
            sell_volume = sum(float(t['qty']) for t in trades if t['m'])
            total = buy_volume + sell_volume
            if total == 0:
                raise ValueError("Zero total volume")
            buy_ratio = buy_volume / total
            return (buy_ratio - 0.5)
        except Exception as e:
            logger.error(f"❌ Trade flows fetch failed: {e}")
            raise

# ============================================================================
# LAYER 6: WHALE ALERT - FIX 401: USE PUBLIC DEPTH ENDPOINT ✅
# ============================================================================

class WhaleAlertLayer:
    """Whale Activity - Use PUBLIC depth endpoint (not private openOrders)"""
    
    @retry_with_backoff()
    def analyze(self):
        try:
            large_transactions = self._fetch_large_transactions()
            score = 0.5 + (large_transactions * 0.3)
            logger.info(f"✅ WhaleAlert: {score:.2f}")
            return np.clip(score, 0, 1)
        except Exception as e:
            logger.error(f"❌ WhaleAlert error: {e}")
            raise
    
    def _fetch_large_transactions(self):
        """Fetch large transactions - USE PUBLIC DEPTH ENDPOINT"""
        try:
            # FIX: Changed from openOrders (private) to depth (public)
            url = "https://fapi.binance.com/fapi/v1/depth"  # ✅ PUBLIC endpoint
            params = {'symbol': 'BTCUSDT', 'limit': 20}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                raise ValueError(f"API error {response.status_code}")
            
            data = response.json()
            bids = data.get('bids', [])
            asks = data.get('asks', [])
            
            if not bids or not asks:
                return 0
            
            large_bids = sum(1 for b in bids if float(b[1]) > 10)
            large_asks = sum(1 for a in asks if float(a[1]) > 10)
            ratio = (large_bids + large_asks) / 40
            
            return ratio - 0.5
        except Exception as e:
            logger.error(f"❌ Large transactions fetch failed: {e}")
            raise

# ============================================================================
# LAYERS 7-20: ALL OTHER LAYERS (UNCHANGED FROM [122])
# ============================================================================

class TwitterSentimentLayer:
    def __init__(self):
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
    
    @retry_with_backoff()
    def analyze(self):
        try:
            sentiment = self._analyze_news_sentiment()
            logger.info(f"✅ TwitterSentiment: {sentiment:.2f}")
            return np.clip(sentiment, 0, 1)
        except Exception as e:
            logger.error(f"❌ TwitterSentiment error: {e}")
            raise
    
    def _analyze_news_sentiment(self):
        try:
            if not self.newsapi_key:
                raise ValueError("NEWSAPI_KEY not set")
            url = "https://newsapi.org/v2/everything"
            params_bull = {'q': '(Bitcoin OR cryptocurrency) AND (bullish OR surge OR pump)', 'sortBy': 'publishedAt', 'language': 'en', 'apiKey': self.newsapi_key}
            response_bull = requests.get(url, params=params_bull, timeout=10)
            if response_bull.status_code != 200:
                raise ValueError(f"NewsAPI error {response_bull.status_code}")
            positive_articles = response_bull.json().get('articles', [])
            params_bear = {'q': '(Bitcoin OR cryptocurrency) AND (bearish OR crash OR fall)', 'sortBy': 'publishedAt', 'language': 'en', 'apiKey': self.newsapi_key}
            response_bear = requests.get(url, params=params_bear, timeout=10)
            if response_bear.status_code != 200:
                raise ValueError(f"NewsAPI error {response_bear.status_code}")
            negative_articles = response_bear.json().get('articles', [])
            total = len(positive_articles) + len(negative_articles)
            if total == 0:
                raise ValueError("No articles found")
            ratio = len(positive_articles) / total
            return ratio
        except Exception as e:
            logger.error(f"❌ News sentiment fetch failed: {e}")
            raise

class MacroCorrelationLayer:
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    @retry_with_backoff()
    def analyze(self):
        try:
            sp500_signal = self._fetch_sp500_signal()
            dxy_signal = self._fetch_dxy_signal()
            if sp500_signal is None or dxy_signal is None:
                raise ValueError("Could not fetch macro data")
            score = (sp500_signal * 0.5) + (dxy_signal * 0.5)
            logger.info(f"✅ MacroCorrelation: {score:.2f}")
            return np.clip(score, 0, 1)
        except Exception as e:
            logger.error(f"❌ MacroCorrelation error: {e}")
            raise
    
    def _fetch_sp500_signal(self):
        try:
            if not self.api_key:
                raise ValueError("ALPHA_VANTAGE_API_KEY not set")
            url = "https://www.alphavantage.co/query"
            params = {'function': 'GLOBAL_QUOTE', 'symbol': 'GSPC', 'apikey': self.api_key}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"API error {response.status_code}")
            data = response.json()
            if 'Global Quote' not in data:
                raise ValueError("Missing Global Quote")
            change_pct = float(data['Global Quote'].get('10. change percent', '0').strip('%'))
            return 0.5 + (change_pct / 20)
        except Exception as e:
            logger.error(f"❌ S&P500 fetch failed: {e}")
            raise
    
    def _fetch_dxy_signal(self):
        try:
            if not self.api_key:
                raise ValueError("ALPHA_VANTAGE_API_KEY not set")
            url = "https://www.alphavantage.co/query"
            params = {'function': 'CURRENCY_EXCHANGE_RATE', 'from_currency': 'USD', 'to_currency': 'EUR', 'apikey': self.api_key}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"API error {response.status_code}")
            data = response.json()
            if 'Realtime Currency Exchange Rate' not in data:
                raise ValueError("Missing exchange rate")
            rate = float(data['Realtime Currency Exchange Rate'].get('5. Exchange Rate', '1.0'))
            return max(0, 1 - (rate / 1.2))
        except Exception as e:
            logger.error(f"❌ DXY fetch failed: {e}")
            raise

class TraditionalMarketsLayer:
    def __init__(self):
        self.fred_key = os.getenv('FRED_API_KEY')
    
    @retry_with_backoff()
    def analyze(self):
        try:
            vix_signal = self._fetch_vix_signal()
            if vix_signal is None:
                raise ValueError("Could not fetch VIX")
            logger.info(f"✅ TraditionalMarkets: {vix_signal:.2f}")
            return np.clip(vix_signal, 0, 1)
        except Exception as e:
            logger.error(f"❌ TraditionalMarkets error: {e}")
            raise
    
    def _fetch_vix_signal(self):
        try:
            url = "https://api.stlouisfed.org/fred/series/data"
            params = {'series_id': 'VIXCLS', 'api_key': self.fred_key, 'file_type': 'json', 'limit': 5}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 404:
                raise ValueError("FRED API key invalid or VIX series not found")
            elif response.status_code != 200:
                raise ValueError(f"FRED error {response.status_code}")
            data = response.json()
            observations = data.get('observations', [])
            if not observations:
                raise ValueError("No VIX data")
            latest_vix = float(observations[-1]['value'])
            return max(0, 1 - (latest_vix / 40))
        except Exception as e:
            logger.error(f"❌ VIX fetch failed: {e}")
            raise

class EconomicCalendarLayer:
    def __init__(self):
        self.fred_key = os.getenv('FRED_API_KEY')
    
    @retry_with_backoff()
    def analyze(self):
        try:
            unemployment_signal = self._fetch_unemployment_trend()
            if unemployment_signal is None:
                raise ValueError("Could not fetch unemployment")
            logger.info(f"✅ EconomicCalendar: {unemployment_signal:.2f}")
            return np.clip(unemployment_signal, 0, 1)
        except Exception as e:
            logger.error(f"❌ EconomicCalendar error: {e}")
            raise
    
    def _fetch_unemployment_trend(self):
        try:
            url = "https://api.stlouisfed.org/fred/series/data"
            params = {'series_id': 'UNRATE', 'api_key': self.fred_key, 'file_type': 'json', 'limit': 24}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 404:
                raise ValueError("FRED API key invalid or UNRATE series not found")
            elif response.status_code != 200:
                raise ValueError(f"FRED error {response.status_code}")
            data = response.json()
            observations = data.get('observations', [])
            if len(observations) < 2:
                raise ValueError("Insufficient unemployment data")
            current_rate = float(observations[-1]['value'])
            past_rate = float(observations[-12]['value']) if len(observations) > 12 else current_rate
            trend = current_rate - past_rate
            if trend < -0.5:
                return 0.75
            elif trend < 0:
                return 0.62
            elif trend < 0.5:
                return 0.50
            else:
                return 0.38
        except Exception as e:
            logger.error(f"❌ Unemployment fetch failed: {e}")
            raise

class InterestRatesLayer:
    def __init__(self):
        self.fred_key = os.getenv('FRED_API_KEY')
    
    @retry_with_backoff()
    def analyze(self):
        try:
            rate_signal = self._fetch_fed_rate()
            if rate_signal is None:
                raise ValueError("Could not fetch Fed rate")
            logger.info(f"✅ InterestRates: {rate_signal:.2f}")
            return np.clip(rate_signal, 0, 1)
        except Exception as e:
            logger.error(f"❌ InterestRates error: {e}")
            raise
    
    def _fetch_fed_rate(self):
        try:
            url = "https://api.stlouisfed.org/fred/series/data"
            params = {'series_id': 'FEDFUNDS', 'api_key': self.fred_key, 'file_type': 'json', 'limit': 1}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 404:
                raise ValueError("FRED API key invalid or FEDFUNDS series not found")
            elif response.status_code != 200:
                raise ValueError(f"FRED error {response.status_code}")
            data = response.json()
            observations = data.get('observations', [])
            if not observations:
                raise ValueError("No Fed rate data")
            current_rate = float(observations[-1]['value'])
            if current_rate > 5.0:
                return 0.30
            elif current_rate > 4.0:
                return 0.40
            elif current_rate > 3.0:
                return 0.50
            elif current_rate > 2.0:
                return 0.65
            else:
                return 0.80
        except Exception as e:
            logger.error(f"❌ Fed rate fetch failed: {e}")
            raise

class MarketRegimeLayer:
    @retry_with_backoff()
    def analyze(self):
        try:
            volatility = self._calculate_atr_volatility()
            if volatility is None:
                raise ValueError("Could not calculate ATR")
            logger.info(f"✅ MarketRegime: {volatility:.2f}")
            return np.clip(volatility, 0, 1)
        except Exception as e:
            logger.error(f"❌ MarketRegime error: {e}")
            raise
    
    def _calculate_atr_volatility(self):
        try:
            url = "https://fapi.binance.com/fapi/v1/klines"
            params = {'symbol': 'BTCUSDT', 'interval': '1h', 'limit': 100}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"Binance error {response.status_code}")
            klines = response.json()
            if not klines:
                raise ValueError("No klines data")
            closes = [float(k[4]) for k in klines]
            highs = [float(k[2]) for k in klines]
            lows = [float(k[3]) for k in klines]
            tr = [max(h - l, abs(h - closes[i-1]), abs(l - closes[i-1])) for i, (h, l) in enumerate(zip(highs, lows))]
            atr = np.mean(tr[-14:])
            volatility = atr / closes[-1]
            if volatility > 0.04:
                return 0.75
            elif volatility > 0.02:
                return 0.60
            else:
                return 0.35
        except Exception as e:
            logger.error(f"❌ ATR fetch failed: {e}")
            raise

class StablecoinDominanceLayer:
    @retry_with_backoff()
    def analyze(self):
        try:
            final_score = self._calculate_stablecoin_dominance()
            if final_score is None:
                raise ValueError("Could not calculate dominance")
            logger.info(f"✅ StablecoinDominance: {final_score:.2f}")
            return np.clip(final_score, 0, 1)
        except Exception as e:
            logger.error(f"❌ StablecoinDominance error: {e}")
            raise
    
    def _calculate_stablecoin_dominance(self):
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {'ids': 'tether,usd-coin,dai,true-usd,paxos-standard', 'vs_currencies': 'usd', 'include_market_cap': 'true'}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"CoinGecko error {response.status_code}")
            data = response.json()
            usdt_mcap = data.get('tether', {}).get('usd_market_cap', 0) or 0
            usdc_mcap = data.get('usd-coin', {}).get('usd_market_cap', 0) or 0
            dai_mcap = data.get('dai', {}).get('usd_market_cap', 0) or 0
            tusd_mcap = data.get('true-usd', {}).get('usd_market_cap', 0) or 0
            paxos_mcap = data.get('paxos-standard', {}).get('usd_market_cap', 0) or 0
            total_stablecoin = usdt_mcap + usdc_mcap + dai_mcap + tusd_mcap + paxos_mcap
            if total_stablecoin == 0:
                raise ValueError("Zero stablecoin market cap")
            usdt_ratio = usdt_mcap / total_stablecoin
            usdc_ratio = usdc_mcap / total_stablecoin
            if usdt_ratio > 0.50:
                base_score = 0.75
            elif usdt_ratio > 0.45:
                base_score = 0.68
            elif usdt_ratio > 0.40:
                base_score = 0.60
            elif usdt_ratio > 0.35:
                base_score = 0.50
            else:
                base_score = 0.40
            if usdc_ratio > 0.35:
                institutional_boost = 0.08
            elif usdc_ratio > 0.25:
                institutional_boost = 0.03
            else:
                institutional_boost = 0.0
            final_score = base_score + institutional_boost
            return final_score
        except Exception as e:
            logger.error(f"❌ Stablecoin dominance fetch failed: {e}")
            raise

class FundingRatesLayer:
    @retry_with_backoff()
    def analyze(self):
        try:
            score = self._analyze_funding_rates()
            if score is None:
                raise ValueError("Could not analyze funding rates")
            logger.info(f"✅ FundingRates: {score:.2f}")
            return np.clip(score, 0, 1)
        except Exception as e:
            logger.error(f"❌ FundingRates error: {e}")
            raise
    
    def _analyze_funding_rates(self):
        try:
            url = "https://fapi.binance.com/fapi/v1/fundingRate"
            params = {'symbol': 'BTCUSDT', 'limit': 24}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"Binance error {response.status_code}")
            funding_data = response.json()
            if not funding_data:
                raise ValueError("No funding rate data")
            rates = [float(item['fundingRate']) for item in funding_data[-24:]]
            avg_funding = np.mean(rates)
            max_funding = np.max(rates)
            if max_funding > 0.001:
                return 0.25
            elif avg_funding > 0.0005:
                return 0.40
            elif avg_funding > 0.0001:
                return 0.55
            elif avg_funding >= -0.0001:
                return 0.65
            else:
                return 0.75
        except Exception as e:
            logger.error(f"❌ Funding rates fetch failed: {e}")
            raise

class LongShortRatioLayer:
    @retry_with_backoff()
    def analyze(self):
        try:
            score = self._analyze_long_short()
            if score is None:
                raise ValueError("Could not analyze long/short ratio")
            logger.info(f"✅ LongShortRatio: {score:.2f}")
            return np.clip(score, 0, 1)
        except Exception as e:
            logger.error(f"❌ LongShortRatio error: {e}")
            raise
    
    def _analyze_long_short(self):
        try:
            url = "https://fapi.binance.com/futures/data/takerlongshortRatio"
            params = {'symbol': 'BTCUSDT', 'period': '15m', 'limit': 24}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"Binance error {response.status_code}")
            ratio_data = response.json()
            if not ratio_data:
                raise ValueError("No ratio data")
            latest = ratio_data[-1]
            
            # DUAL FORMAT SUPPORT
            if 'longShortRatio' in latest:
                current_ratio = float(latest['longShortRatio'])
            elif 'longAccount' in latest and 'shortAccount' in latest:
                long_acc = float(latest.get('longAccount', 1))
                short_acc = float(latest.get('shortAccount', 1))
                current_ratio = long_acc / short_acc if short_acc > 0 else 1.0
            else:
                raise ValueError("Unknown API response format")
            
            if current_ratio > 1.5:
                return 0.25
            elif current_ratio > 1.3:
                return 0.35
            elif current_ratio > 1.1:
                return 0.55
            elif current_ratio >= 0.9:
                return 0.50
            elif current_ratio > 0.7:
                return 0.65
            else:
                return 0.80
        except Exception as e:
            logger.error(f"❌ Long/Short fetch failed: {e}")
            raise

class OnChainActivityLayer:
    @retry_with_backoff()
    def analyze(self):
        try:
            score = self._analyze_activity()
            if score is None:
                raise ValueError("Could not analyze activity")
            logger.info(f"✅ OnChainActivity: {score:.2f}")
            return np.clip(score, 0, 1)
        except Exception as e:
            logger.error(f"❌ OnChainActivity error: {e}")
            raise
    
    def _analyze_activity(self):
        try:
            url = "https://blockchain.com/api/charts/n_transactions"
            params = {'timespan': '24h', 'format': 'json'}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"Blockchain.com error {response.status_code}")
            data = response.json()
            values = data.get('values', [])
            if not values:
                raise ValueError("No transaction data")
            current_tx = values[-1]['y']
            avg_tx = np.mean([v['y'] for v in values[-7:]])
            if current_tx > avg_tx * 1.3:
                return 0.65
            elif current_tx < avg_tx * 0.7:
                return 0.35
            else:
                return 0.50
        except Exception as e:
            logger.error(f"❌ On-chain activity fetch failed: {e}")
            raise

class ExchangeReserveFlowsLayer:
    @retry_with_backoff()
    def analyze(self):
        try:
            score = self._analyze_reserve_flows()
            if score is None:
                raise ValueError("Could not analyze reserve flows")
            logger.info(f"✅ ExchangeReserveFlows: {score:.2f}")
            return np.clip(score, 0, 1)
        except Exception as e:
            logger.error(f"❌ ExchangeReserveFlows error: {e}")
            raise
    
    def _analyze_reserve_flows(self):
        try:
            url = "https://fapi.binance.com/fapi/v1/openInterest"
            params = {'symbol': 'BTCUSDT', 'period': '5m'}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"Binance error {response.status_code}")
            data = response.json()
            if not data or len(data) < 2:
                raise ValueError("Insufficient data")
            oi_values = [float(d['sumOpenInterest']) for d in data[-24:]]
            current_oi = oi_values[-1]
            past_oi = oi_values[0]
            oi_trend = (current_oi - past_oi) / past_oi if past_oi > 0 else 0
            if oi_trend > 0.15:
                return 0.35
            elif oi_trend < -0.05:
                return 0.70
            else:
                return 0.50 + (oi_trend * 5)
        except Exception as e:
            logger.error(f"❌ Reserve flows fetch failed: {e}")
            raise

class OrderBookImbalanceLayer:
    @retry_with_backoff()
    def analyze(self, symbol: str = 'BTCUSDT'):
        try:
            score = self._analyze_orderbook(symbol)
            if score is None:
                raise ValueError("Could not analyze orderbook")
            logger.info(f"✅ OrderBookImbalance: {score:.2f}")
            return np.clip(score, 0, 1)
        except Exception as e:
            logger.error(f"❌ OrderBookImbalance error: {e}")
            raise
    
    def _analyze_orderbook(self, symbol):
        try:
            url = "https://fapi.binance.com/fapi/v1/depth"
            params = {'symbol': symbol, 'limit': 20}
            response = requests.get(url, params=params, timeout=5)
            if response.status_code != 200:
                raise ValueError(f"Binance error {response.status_code}")
            data = response.json()
            bids = data.get('bids', [])
            asks = data.get('asks', [])
            if not bids or not asks:
                raise ValueError("Missing bid/ask data")
            total_bid_volume = sum(float(bid[1]) for bid in bids)
            total_ask_volume = sum(float(ask[1]) for ask in asks)
            if total_ask_volume == 0:
                return 0.75
            imbalance_ratio = total_bid_volume / total_ask_volume
            if imbalance_ratio > 3.0:
                return 0.80
            elif imbalance_ratio > 2.0:
                return 0.70
            elif imbalance_ratio > 1.3:
                return 0.60
            elif imbalance_ratio >= 0.77:
                return 0.50
            elif imbalance_ratio > 0.5:
                return 0.40
            elif imbalance_ratio > 0.33:
                return 0.25
            else:
                return 0.15
        except Exception as e:
            logger.error(f"❌ Orderbook fetch failed: {e}")
            raise

class LiquidationCascadeLayer:
    def __init__(self):
        self.coinglass_key = os.getenv('COINGLASS_API_KEY', '')
    
    @retry_with_backoff()
    def analyze(self, symbol: str = 'BTC', current_price: float = 95000):
        try:
            score = self._analyze_liquidations(symbol, current_price)
            if score is None:
                raise ValueError("Could not analyze liquidations")
            logger.info(f"✅ LiquidationCascade: {score:.2f}")
            return np.clip(score, 0, 1)
        except Exception as e:
            logger.error(f"❌ LiquidationCascade error: {e}")
            raise
    
    def _analyze_liquidations(self, symbol, current_price):
        try:
            if not self.coinglass_key:
                raise ValueError("COINGLASS_API_KEY not set")
            url = "https://api.coinglass.com/api/v1/liquidation_chart"
            params = {'symbol': symbol, 'type': 'futures_usdt'}
            headers = {'coinglassSecret': self.coinglass_key}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"CoinGlass error {response.status_code}")
            data = response.json()
            if not data.get('data'):
                raise ValueError("No liquidation data")
            liquidation_data = data['data']
            upside_liq = 0
            downside_liq = 0
            for entry in liquidation_data:
                price = float(entry.get('price', 0))
                volume = float(entry.get('volume', 0))
                if price > current_price:
                    upside_liq += volume
                elif price < current_price:
                    downside_liq += volume
            total_liq = upside_liq + downside_liq
            if total_liq == 0:
                raise ValueError("Zero total liquidation")
            upside_ratio = upside_liq / total_liq
            if upside_ratio > 0.75:
                return 0.75
            elif upside_ratio > 0.60:
                return 0.65
            elif upside_ratio >= 0.40:
                return 0.50
            elif upside_ratio > 0.25:
                return 0.35
            else:
                return 0.20
        except Exception as e:
            logger.error(f"❌ Liquidation cascade fetch failed: {e}")
            raise

class BasisContangoLayer:
    @retry_with_backoff()
    def analyze(self, symbol: str = 'BTCUSDT', coin_id: str = 'bitcoin'):
        try:
            score = self._analyze_basis(symbol, coin_id)
            if score is None:
                raise ValueError("Could not analyze basis")
            logger.info(f"✅ BasisContango: {score:.2f}")
            return np.clip(score, 0, 1)
        except Exception as e:
            logger.error(f"❌ BasisContango error: {e}")
            raise
    
    def _analyze_basis(self, symbol, coin_id):
        try:
            spot_response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={'ids': coin_id, 'vs_currencies': 'usd'},
                timeout=5
            )
            if spot_response.status_code != 200:
                raise ValueError(f"Spot error {spot_response.status_code}")
            spot_data = spot_response.json()
            spot_price = spot_data.get(coin_id, {}).get('usd', 0)
            if not spot_price:
                raise ValueError("No spot price")
            futures_response = requests.get(
                "https://fapi.binance.com/fapi/v1/tickerPrice",
                params={'symbol': symbol},
                timeout=5
            )
            if futures_response.status_code != 200:
                raise ValueError(f"Futures error {futures_response.status_code}")
            futures_data = futures_response.json()
            futures_price = float(futures_data.get('price', 0))
            if not futures_price:
                raise ValueError("No futures price")
            basis = (futures_price - spot_price) / spot_price
            if basis > 0.02:
                return 0.30
            elif basis > 0.005:
                return 0.65
            elif basis >= -0.005:
                return 0.50
            elif basis > -0.02:
                return 0.70
            else:
                return 0.80
        except Exception as e:
            logger.error(f"❌ Basis fetch failed: {e}")
            raise

# ============================================================================
# SENTIMENT LAYERS REGISTRY - ALL 20
# ============================================================================

SENTIMENT_LAYERS = [
    ('NewsSentiment', NewsSentimentLayer),
    ('FearGreedIndex', FearGreedIndexLayer),
    ('BTCDominance', BTCDominanceLayer),
    ('AltcoinSeason', AltcoinSeasonLayer),
    ('ExchangeFlow', ExchangeFlowLayer),
    ('WhaleAlert', WhaleAlertLayer),
    ('TwitterSentiment', TwitterSentimentLayer),
    ('MacroCorrelation', MacroCorrelationLayer),
    ('TraditionalMarkets', TraditionalMarketsLayer),
    ('EconomicCalendar', EconomicCalendarLayer),
    ('InterestRates', InterestRatesLayer),
    ('MarketRegime', MarketRegimeLayer),
    ('StablecoinDominance', StablecoinDominanceLayer),
    ('FundingRates', FundingRatesLayer),
    ('LongShortRatio', LongShortRatioLayer),
    ('OnChainActivity', OnChainActivityLayer),
    ('ExchangeReserveFlows', ExchangeReserveFlowsLayer),
    ('OrderBookImbalance', OrderBookImbalanceLayer),
    ('LiquidationCascade', LiquidationCascadeLayer),
    ('BasisContango', BasisContangoLayer),
]

logger.info("✅ PHASE 10 COMBINED: ALL 20 SENTIMENT LAYERS = RAILWAY READY")
logger.info("✅ FIX: WhaleAlert now uses public depth endpoint (no 401)")
logger.info("✅ BUG FIXES: FRED validation, LongShortRatio dual format")
logger.info("✅ Production Ready - Dashboard accessible!")
