"""
EXTERNAL DATA LAYER v3 - REEL VERİ İLE ÇALIŞ
==============================================
Date: 7 Kasım 2025, 19:55 CET
Version: 3.0 - Full Real Data Handling with Fallbacks
"""

import requests
import logging
import os
from typing import Dict, Any
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# FEAR & GREED INDEX (Alternative.me)
# ============================================

def get_fear_greed_index() -> Dict[str, Any]:
    """Crypto Fear & Greed Index - REEL VERİ"""
    try:
        url = 'https://api.alternative.me/fng/?limit=1'
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data and 'data' in data and len(data['data']) > 0:
            fng = data['data'][0]
            result = {
                'value': int(fng['value']),
                'classification': fng['value_classification'],
                'timestamp': fng['timestamp'],
                'source': 'REAL_API',
                'available': True
            }
            logger.info(f"✅ Fear & Greed: {result['value']} ({result['classification']})")
            return result
        else:
            logger.warning("⚠️ Fear & Greed empty response")
            return _fallback_fear_greed()
            
    except requests.exceptions.Timeout:
        logger.error("⚠️ Fear & Greed timeout")
        return _fallback_fear_greed()
    except Exception as e:
        logger.error(f"⚠️ Fear & Greed error: {str(e)[:60]}")
        return _fallback_fear_greed()

def _fallback_fear_greed() -> Dict[str, Any]:
    """Fallback for Fear & Greed"""
    return {
        'value': 50,
        'classification': 'Neutral',
        'timestamp': int(time.time()),
        'source': 'FALLBACK',
        'available': True
    }

# ============================================
# TRADITIONAL MARKETS (VIX, DXY, SPX)
# ============================================

def get_traditional_markets() -> Dict[str, Any]:
    """VIX, DXY, S&P500 - REEL VERİ"""
    symbols = {
        'VIX': '^VIX',      # Volatility Index
        'DXY': 'DX-Y.NYB',  # Dollar Index
        'SPX': '^GSPC'      # S&P 500
    }
    
    results = {}
    
    for name, symbol in symbols.items():
        try:
            logger.info(f" 📡 Fetching {name}...")
            url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
            params = {'interval': '1d', 'range': '5d'}
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart'] and len(data['chart']['result']) > 0:
                result = data['chart']['result'][0]
                meta = result.get('meta', {})
                
                price = meta.get('regularMarketPrice', 0)
                change = meta.get('regularMarketChangePercent', 0)
                
                results[name] = {
                    'price': round(price, 2),
                    'change': round(change, 2),
                    'source': 'REAL_API',
                    'available': True
                }
                logger.info(f" ✅ {name}: {price:.2f} ({change:+.2f}%)")
            else:
                logger.warning(f" ⚠️ {name}: No data in response")
                results[name] = _fallback_traditional_market(name)
                
        except requests.exceptions.Timeout:
            logger.error(f" ⚠️ {name}: Timeout")
            results[name] = _fallback_traditional_market(name)
        except Exception as e:
            logger.error(f" ⚠️ {name}: {str(e)[:50]}")
            results[name] = _fallback_traditional_market(name)
    
    return results

def _fallback_traditional_market(symbol: str) -> Dict[str, Any]:
    """Fallback for traditional markets"""
    fallbacks = {
        'VIX': {'price': 20.0, 'change': 0.0},
        'DXY': {'price': 104.0, 'change': 0.0},
        'SPX': {'price': 5800.0, 'change': 0.0}
    }
    fallback = fallbacks.get(symbol, {'price': 0, 'change': 0})
    fallback['source'] = 'FALLBACK'
    fallback['available'] = True
    return fallback

# ============================================
# FUNDING RATE (Binance)
# ============================================

def get_funding_rate(symbol: str = 'BTCUSDT') -> Dict[str, Any]:
    """Current funding rate from Binance Futures - REEL VERİ"""
    try:
        logger.info(f" 📡 Fetching funding rate for {symbol}...")
        url = 'https://fapi.binance.com/fapi/v1/premiumIndex'
        params = {'symbol': symbol.upper()}
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        funding_rate = float(data.get('lastFundingRate', 0))
        result = {
            'rate': round(funding_rate * 100, 4),  # Convert to percentage
            'source': 'REAL_API',
            'available': True,
            'symbol': symbol
        }
        logger.info(f" ✅ Funding rate: {result['rate']}%")
        return result
        
    except requests.exceptions.Timeout:
        logger.error(f" ⚠️ Funding rate timeout")
        return _fallback_funding_rate(symbol)
    except Exception as e:
        logger.error(f" ⚠️ Funding rate error: {str(e)[:50]}")
        return _fallback_funding_rate(symbol)

def _fallback_funding_rate(symbol: str) -> Dict[str, Any]:
    """Fallback for funding rate"""
    return {
        'rate': 0.01,
        'source': 'FALLBACK',
        'available': True,
        'symbol': symbol
    }

# ============================================
# BITCOIN DOMINANCE (CoinGecko)
# ============================================

def get_bitcoin_dominance() -> Dict[str, Any]:
    """Bitcoin dominance percentage - REEL VERİ"""
    try:
        logger.info(f" 📡 Fetching Bitcoin dominance...")
        url = 'https://api.coingecko.com/api/v3/global'
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data:
            btc_dom = data['data'].get('btc_market_cap_percentage', 0)
            result = {
                'dominance': round(btc_dom, 2),
                'source': 'REAL_API',
                'available': True
            }
            logger.info(f" ✅ Bitcoin dominance: {result['dominance']}%")
            return result
        else:
            return _fallback_bitcoin_dominance()
            
    except requests.exceptions.Timeout:
        logger.error(f" ⚠️ BTC dominance timeout")
        return _fallback_bitcoin_dominance()
    except Exception as e:
        logger.error(f" ⚠️ BTC dominance error: {str(e)[:50]}")
        return _fallback_bitcoin_dominance()

def _fallback_bitcoin_dominance() -> Dict[str, Any]:
    """Fallback for BTC dominance"""
    return {
        'dominance': 45.0,
        'source': 'FALLBACK',
        'available': True
    }

# ============================================
# ON-CHAIN METRICS
# ============================================

def get_onchain_metrics(symbol: str = 'BTC') -> Dict[str, Any]:
    """
    On-chain metrics (whale movements, exchange flows, etc.)
    NOTE: Requires premium APIs like Glassnode, CryptoQuant, Santiment
    For now, returns structure for future integration
    """
    return {
        'whale_movements': {'score': 50, 'trend': 'NEUTRAL'},
        'exchange_inflow': {'score': 50, 'trend': 'NEUTRAL'},
        'exchange_outflow': {'score': 50, 'trend': 'NEUTRAL'},
        'active_addresses': {'score': 50, 'trend': 'NEUTRAL'},
        'network_growth': {'score': 50, 'trend': 'NEUTRAL'},
        'source': 'PLACEHOLDER',
        'note': 'Requires premium API subscription'
    }

# ============================================
# NEWS SENTIMENT (NewsAPI)
# ============================================

def get_news_sentiment(symbol: str = 'BTC') -> Dict[str, Any]:
    """Get news and sentiment data - REEL VERİ"""
    try:
        newsapi_key = os.getenv('NEWSAPI_KEY')
        if not newsapi_key:
            logger.warning("⚠️ NEWSAPI_KEY not set")
            return _fallback_news_sentiment(symbol)
        
        logger.info(f" 📡 Fetching news for {symbol}...")
        
        # Try to get crypto news
        query = f"{symbol} cryptocurrency OR Bitcoin OR crypto"
        url = 'https://newsapi.org/v2/everything'
        params = {
            'q': query,
            'sortBy': 'publishedAt',
            'language': 'en',
            'pageSize': 10,
            'apiKey': newsapi_key
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        articles = data.get('articles', [])
        
        # Simple sentiment scoring (can be enhanced with NLP)
        positive_keywords = ['surge', 'rally', 'gain', 'bull', 'soar', 'jump']
        negative_keywords = ['crash', 'fall', 'dump', 'bear', 'decline', 'loss']
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for article in articles:
            title_lower = article.get('title', '').lower()
            
            if any(keyword in title_lower for keyword in positive_keywords):
                positive_count += 1
            elif any(keyword in title_lower for keyword in negative_keywords):
                negative_count += 1
            else:
                neutral_count += 1
        
        total = len(articles)
        if total > 0:
            sentiment_score = ((positive_count - negative_count) / total) * 50 + 50
        else:
            sentiment_score = 50
        
        result = {
            'overall_score': round(sentiment_score, 2),
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count,
            'total_articles': total,
            'source': 'REAL_API',
            'available': True
        }
        
        logger.info(f" ✅ News sentiment: {result['overall_score']:.2f}/100 ({total} articles)")
        return result
        
    except Exception as e:
        logger.error(f" ⚠️ News sentiment error: {str(e)[:50]}")
        return _fallback_news_sentiment(symbol)

def _fallback_news_sentiment(symbol: str) -> Dict[str, Any]:
    """Fallback for news sentiment"""
    return {
        'overall_score': 50.0,
        'positive': 0,
        'negative': 0,
        'neutral': 0,
        'total_articles': 0,
        'source': 'FALLBACK',
        'available': True
    }

# ============================================
# AGGREGATE ALL EXTERNAL DATA
# ============================================

def get_all_external_data(symbol: str = 'BTCUSDT') -> Dict[str, Any]:
    """
    Aggregate all external data sources
    Returns: Comprehensive market analysis data
    """
    
    logger.info(f"\n{'='*70}")
    logger.info(f"📊 GATHERING EXTERNAL DATA FOR {symbol}")
    logger.info(f"{'='*70}")
    
    # Extract base symbol for news
    news_symbol = symbol.replace('USDT', '').replace('USD', '').replace('T', '')
    
    # Gather all data
    fear_greed = get_fear_greed_index()
    trad_markets = get_traditional_markets()
    funding = get_funding_rate(symbol)
    btc_dom = get_bitcoin_dominance()
    onchain = get_onchain_metrics(news_symbol)
    news = get_news_sentiment(news_symbol)
    
    result = {
        'fear_greed': fear_greed,
        'traditional_markets': trad_markets,
        'funding_rate': funding,
        'bitcoin_dominance': btc_dom,
        'onchain': onchain,
        'news_sentiment': news,
        'timestamp': datetime.now().isoformat(),
        'symbol': symbol,
        'data_quality': {
            'real_sources': sum(1 for x in [
                fear_greed.get('source') == 'REAL_API',
                funding.get('source') == 'REAL_API',
                btc_dom.get('source') == 'REAL_API',
                news.get('source') == 'REAL_API'
            ] if x),
            'fallback_sources': sum(1 for x in [
                fear_greed.get('source') == 'FALLBACK',
                funding.get('source') == 'FALLBACK',
                btc_dom.get('source') == 'FALLBACK',
                news.get('source') == 'FALLBACK'
            ] if x)
        }
    }
    
    logger.info(f"\n✅ External data collection complete")
    logger.info(f" Real sources: {result['data_quality']['real_sources']}")
    logger.info(f" Fallback sources: {result['data_quality']['fallback_sources']}")
    
    return result

# ============================================
# TEST
# ============================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🔄 EXTERNAL DATA LAYER v3 - REAL DATA TEST")
    print("="*70)
    
    data = get_all_external_data('BTCUSDT')
    
    print(f"\n📊 Fear & Greed: {data['fear_greed']['value']} ({data['fear_greed']['classification']})")
    print(f"💵 Funding Rate: {data['funding_rate']['rate']}%")
    print(f"📈 Bitcoin Dominance: {data['bitcoin_dominance']['dominance']}%")
    print(f"📰 News Sentiment: {data['news_sentiment']['overall_score']:.2f}/100")
    print(f"📡 VIX: {data['traditional_markets']['VIX']['price']:.2f}")
    print(f"📡 SPX: ${data['traditional_markets']['SPX']['price']:,.2f}")
    print(f"\n✅ Data Quality: {data['data_quality']['real_sources']} real, {data['data_quality']['fallback_sources']} fallback")
    print("="*70)
