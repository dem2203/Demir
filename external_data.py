"""
DEMIR - External Data Layer v2
Fear & Greed, VIX, DXY, News, Sentiment Integration
"""

import requests
from typing import Dict, Any
from datetime import datetime

# Import news sentiment layer
try:
    from news_sentiment_layer import get_sentiment_data
    NEWS_AVAILABLE = True
except:
    NEWS_AVAILABLE = False


# ============================================
# FEAR & GREED INDEX
# ============================================

def get_fear_greed_index() -> Dict[str, Any]:
    """Crypto Fear & Greed Index (Alternative.me)"""
    try:
        url = 'https://api.alternative.me/fng/?limit=1'
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data and 'data' in data:
            fng = data['data'][0]
            return {
                'value': int(fng['value']),
                'classification': fng['value_classification'],
                'timestamp': fng['timestamp']
            }
    except:
        pass
    
    return {'value': 50, 'classification': 'Neutral', 'timestamp': None}


# ============================================
# TRADITIONAL MARKETS (VIX, DXY, SPX)
# ============================================

def get_traditional_markets() -> Dict[str, Any]:
    """VIX, DXY, S&P500 (Yahoo Finance proxy)"""
    symbols = {
        'VIX': '^VIX',      # Volatility Index
        'DXY': 'DX-Y.NYB',  # Dollar Index
        'SPX': '^GSPC'      # S&P 500
    }
    
    results = {}
    
    for name, symbol in symbols.items():
        try:
            # Yahoo Finance API (indirect)
            url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
            params = {'interval': '1d', 'range': '1d'}
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart']:
                result = data['chart']['result'][0]
                meta = result.get('meta', {})
                
                results[name] = {
                    'price': meta.get('regularMarketPrice', 0),
                    'change': meta.get('regularMarketChangePercent', 0)
                }
        except:
            results[name] = {'price': 0, 'change': 0}
    
    return results


# ============================================
# FUNDING RATE (Binance)
# ============================================

def get_funding_rate(symbol: str = 'BTCUSDT') -> float:
    """Current funding rate from Binance Futures"""
    try:
        url = 'https://fapi.binance.com/fapi/v1/premiumIndex'
        params = {'symbol': symbol.upper()}
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        return float(data.get('lastFundingRate', 0))
    except:
        return 0.0


# ============================================
# ON-CHAIN METRICS (Placeholder)
# ============================================

def get_onchain_metrics(symbol: str = 'BTC') -> Dict[str, Any]:
    """
    On-chain metrics (whale movements, exchange flows, etc.)
    
    NOTE: This requires premium APIs like:
    - Glassnode
    - CryptoQuant
    - Santiment
    
    For now, returns placeholders
    """
    # TODO: Integrate on-chain data APIs
    return {
        'whale_movements': 0,
        'exchange_inflow': 0,
        'exchange_outflow': 0,
        'active_addresses': 0,
        'network_growth': 0
    }


# ============================================
# NEWS & SENTIMENT INTEGRATION
# ============================================

def get_news_sentiment(symbol: str = 'BTC') -> Dict[str, Any]:
    """Get news and sentiment data"""
    if not NEWS_AVAILABLE:
        return {
            'overall_score': 0,
            'news_score': 0,
            'social_score': 0,
            'market_moving_news': [],
            'news_count': 0
        }
    
    try:
        return get_sentiment_data(symbol)
    except Exception as e:
        print(f"❌ Sentiment fetch error: {e}")
        return {
            'overall_score': 0,
            'news_score': 0,
            'social_score': 0,
            'market_moving_news': [],
            'news_count': 0
        }


# ============================================
# AGGREGATE ALL EXTERNAL DATA
# ============================================

def get_all_external_data(symbol: str = 'BTCUSDT') -> Dict[str, Any]:
    """
    Aggregate all external data sources
    
    Returns:
        {
            'fear_greed': {...},
            'traditional_markets': {...},
            'funding_rate': float,
            'onchain': {...},
            'news_sentiment': {...},
            'timestamp': str
        }
    """
    # Extract symbol for news (BTC from BTCUSDT)
    news_symbol = symbol.replace('USDT', '').replace('USD', '')
    
    return {
        'fear_greed': get_fear_greed_index(),
        'traditional_markets': get_traditional_markets(),
        'funding_rate': get_funding_rate(symbol),
        'onchain': get_onchain_metrics(news_symbol),
        'news_sentiment': get_news_sentiment(news_symbol),
        'timestamp': datetime.now().isoformat()
    }


if __name__ == '__main__':
    # Test
    print("Testing External Data Layer v2...")
    data = get_all_external_data('BTCUSDT')
    
    print(f"\n📊 Fear & Greed: {data['fear_greed']['value']} ({data['fear_greed']['classification']})")
    print(f"💵 Funding Rate: {data['funding_rate']:.4f}%")
    print(f"📰 News Sentiment: {data['news_sentiment']['overall_score']:.2f}")
    print(f"📈 News Count: {data['news_sentiment']['news_count']}")
    print(f"🚨 Market-Moving: {len(data['news_sentiment']['market_moving_news'])}")
