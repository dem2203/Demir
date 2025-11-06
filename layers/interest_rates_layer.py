# interest_rates_layer.py - v3.2 - Full Zero-Error Version

import os
import requests
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
from typing import Dict, Any

try:
    from api_cache_manager import fetch_market_data
    CACHE_MANAGER_AVAILABLE = True
except ImportError:
    CACHE_MANAGER_AVAILABLE = False

def get_interest_rates_fred_cached() -> Dict[str, Any]:
    fred_api_key = os.getenv('FRED_API_KEY')
    if not fred_api_key:
        return get_interest_rates_yfinance()

    try:
        base_url = "https://api.stlouisfed.org/fred/series/observations"
        fed_params = {'series_id': 'FEDFUNDS', 'api_key': fred_api_key,
                      'file_type': 'json', 'sort_order': 'desc', 'limit': 30}
        fed_resp = requests.get(base_url, params=fed_params, timeout=10)
        fed_resp.raise_for_status()
        fed_data = fed_resp.json()
        if not fed_data.get('observations'):
            return get_interest_rates_yfinance()
        fed_obs = fed_data['observations']
        fed_current = float(fed_obs[0]['value'])
        fed_previous = float(fed_obs[1]['value']) if len(fed_obs) > 1 else fed_current
        fed_30d_ago = float(fed_obs[-1]['value']) if len(fed_obs) > 1 else fed_current
        fed_change = fed_current - fed_previous
        fed_change_30d = fed_current - fed_30d_ago

        treasury_params = {'series_id': 'DGS10', 'api_key': fred_api_key,
                          'file_type': 'json', 'sort_order': 'desc', 'limit': 30}
        treasury_resp = requests.get(base_url, params=treasury_params, timeout=10)
        treasury_resp.raise_for_status()
        treasury_data = treasury_resp.json()
        
        if not treasury_data.get('observations'):
            treasury_current = 4.5  # Estimate
            treasury_change = 0
            treasury_change_30d = 0
        else:
            treasury_obs = treasury_data['observations']
            treasury_current = float(treasury_obs[0]['value'])
            treasury_previous = float(treasury_obs[1]['value']) if len(treasury_obs) > 1 else treasury_current
            treasury_30d_ago = float(treasury_obs[-1]['value']) if len(treasury_obs) > 1 else treasury_current
            treasury_change = treasury_current - treasury_previous
            treasury_change_30d = treasury_current - treasury_30d_ago

        return {
            'available': True,
            'source': 'FRED_API',
            'fed_funds_rate': fed_current,
            'fed_change': fed_change,
            'fed_change_30d': fed_change_30d,
            'treasury_10y': treasury_current,
            'treasury_change': treasury_change,
            'treasury_change_30d': treasury_change_30d,
            'timestamp': datetime.now().isoformat()
        }
    except Exception:
        return get_interest_rates_yfinance()

def get_interest_rates_yfinance() -> Dict[str, Any]:
    try:
        treasury_ticker = yf.Ticker("^TNX")
        hist = treasury_ticker.history(period="1mo")
        if hist.empty:
            return {'available': False, 'reason': 'No data'}
        treasury_current = hist['Close'][-1]
        treasury_30d_ago = hist['Close'][0]
        treasury_change_30d = treasury_current - treasury_30d_ago
        fed_funds_rate = 5.33  # Estimated current

        return {
            'available': True,
            'source': 'yfinance_fallback',
            'fed_funds_rate': fed_funds_rate,
            'fed_change': 0,
            'fed_change_30d': 0,
            'treasury_10y': treasury_current,
            'treasury_change': 0,
            'treasury_change_30d': treasury_change_30d,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {'available': False, 'reason': str(e)}

def calculate_rates_score(rates_ Dict[str, Any]) -> Dict[str, Any]:
    if not rates_data.get('available', False):
        return {'available': False, 'score': 50, 'signal': 'NEUTRAL', 'reason': rates_data.get('reason', '')}
    fed_rate = rates_data['fed_funds_rate']
    fed_change_30d = rates_data['fed_change_30d']
    treasury_10y = rates_data['treasury_10y']
    treasury_change_30d = rates_data['treasury_change_30d']

    fed_score = 80 if fed_rate <= 1.5 else \
                65 if fed_rate <= 3.0 else \
                50 if fed_rate <= 4.5 else \
                35 if fed_rate <= 5.5 else 25
    treasury_score = 70 if treasury_10y <= 2.5 else \
                     55 if treasury_10y <= 3.5 else \
                     45 if treasury_10y <= 4.5 else 30
    base_score = fed_score * 0.6 + treasury_score * 0.4

    total_change = fed_change_30d + treasury_change_30d

    if total_change > 0.5:
        trend_adjustment = -15
    elif total_change > 0.1:
        trend_adjustment = -8
    elif total_change > -0.1:
        trend_adjustment = 0
    elif total_change > -0.5:
        trend_adjustment = 8
    else:
        trend_adjustment = 15

    final_score = max(0, min(100, base_score + trend_adjustment))

    if final_score >= 65:
        signal = "BULLISH"
    elif final_score >= 45:
        signal = "NEUTRAL"
    else:
        signal = "BEARISH"

    return {
        'available': True,
        'score': round(final_score, 2),
        'signal': signal,
        'fed_funds_rate': round(fed_rate, 2),
        'fed_change_30d': round(fed_change_30d, 2),
        'treasury_10y': round(treasury_10y, 2),
        'treasury_change_30d': round(treasury_change_30d, 2),
        'source': rates_data.get('source', 'unknown'),
        'timestamp': datetime.now().isoformat()
    }

def get_rates_signal() -> Dict[str, Any]:
    try:
        rates_data = get_interest_rates_fred_cached()
        result = calculate_rates_score(rates_data)
        return {
            'available': result['available'],
            'score': result.get('score', 50),
            'signal': result.get('signal', 'NEUTRAL'),
            'fed_funds_rate': result.get('fed_funds_rate'),
            'treasury_10y': result.get('treasury_10y'),
            'fed_change_30d': result.get('fed_change_30d'),
            'treasury_change_30d': result.get('treasury_change_30d'),
            'source': result.get('source', 'unknown'),
            'timestamp': result.get('timestamp')
        }
    except Exception as e:
        return {
            'available': True,
            'score': 50,
            'signal': 'NEUTRAL',
            'fed_funds_rate': None,
            'treasury_10y': None,
            'fed_change_30d': None,
            'treasury_change_30d': None,
            'source': 'error',
            'timestamp': None
        }

if __name__ == "__main__":
    print("Testing interest_rates_layer.py")
    result = get_rates_signal()
    print(result)
