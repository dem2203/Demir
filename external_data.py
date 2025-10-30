"""
DEMIR - External Data Layer
Fear & Greed, VIX, DXY, News, On-Chain Data
"""

import requests
from typing import Dict, Any
from datetime import datetime

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
        'VIX': '^VIX',      # Volatilite endeksi
        'DXY': 'DX-Y.NYB',  # Dolar endeksi
        'SPX': '^GSPC'      # S&P 500
    }
    
    results = {}
    
    for name, symbol in symbols.items():
        try:
            url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
            params = {'interval': '1d', 'range': '1d'}
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart']:
                result = data['chart']['result'][0]
                quote = result['indicators']['quote'][0]
                
                results[name] = {
                    'price': quote['close'][-1] if quote['close'] else None,
                    'change': quote['close'][-1] - quote['open'][0] if quote['close'] and quote['open'] else 0
                }
        except:
            results[name] = {'price': None, 'change': 0}
    
    return results


# ============================================
# CRYPTO NEWS (CryptoPanic)
# ============================================

def get_crypto_news(limit=5) -> list:
    """CryptoPanic API - Son haberler"""
    try:
        # Public endpoint (API key gerektirmez)
        url = 'https://cryptopanic.com/api/v1/posts/'
        params = {
            'auth_token': 'free',  # Free tier
            'currencies': 'BTC,ETH',
            'filter': 'important',
            'public': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'results' in data:
            news_list = []
            for item in data['results'][:limit]:
                news_list.append({
                    'title': item.get('title', ''),
                    'published_at': item.get('published_at', ''),
                    'url': item.get('url', ''),
                    'votes': item.get('votes', {}).get('positive', 0)
                })
            return news_list
            
    except:
        pass
    
    return []


# ============================================
# ON-CHAIN DATA (Placeholder - Glassnode gerektirir)
# ============================================

def get_onchain_metrics() -> Dict[str, Any]:
    """
    On-chain metrikler (Glassnode API gerekli)
    Şimdilik placeholder
    """
    return {
        'exchange_inflow': None,
        'exchange_outflow': None,
        'whale_transactions': None,
        'active_addresses': None
    }


# ============================================
# BİNANCE FUTURES DATA
# ============================================

def get_binance_funding_rate(symbol='BTCUSDT') -> float:
    """Binance Futures funding rate"""
    try:
        url = 'https://fapi.binance.com/fapi/v1/premiumIndex'
        params = {'symbol': symbol.upper()}
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        return float(data.get('lastFundingRate', 0)) * 100  # Yüzde olarak
        
    except:
        return 0.0


def get_binance_open_interest(symbol='BTCUSDT') -> float:
    """Binance Futures açık pozisyon (Open Interest)"""
    try:
        url = 'https://fapi.binance.com/fapi/v1/openInterest'
        params = {'symbol': symbol.upper()}
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        return float(data.get('openInterest', 0))
        
    except:
        return 0.0


# ============================================
# MAIN EXTERNAL DATA COLLECTOR
# ============================================

def get_all_external_data(symbol='BTCUSDT') -> Dict[str, Any]:
    """Tüm dış verileri topla"""
    
    return {
        'fear_greed': get_fear_greed_index(),
        'traditional_markets': get_traditional_markets(),
        'crypto_news': get_crypto_news(limit=5),
        'funding_rate': get_binance_funding_rate(symbol),
        'open_interest': get_binance_open_interest(symbol),
        'onchain': get_onchain_metrics(),
        'timestamp': datetime.now().isoformat()
    }
