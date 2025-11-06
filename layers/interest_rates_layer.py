import os
import requests
import numpy as np
import yfinance as yf
from datetime import datetime

def get_interest_rates_fred_cached():
    debug = {}
    fred_api_key = os.getenv('FRED_API_KEY')
    if not fred_api_key:
        debug['error_message'] = 'No FRED API Key found; using yfinance fallback'
        return get_interest_rates_yfinance(debug=debug)
    try:
        base_url = "https://api.stlouisfed.org/fred/series/observations"
        fed_params = {'series_id': 'FEDFUNDS', 'api_key': fred_api_key,
                      'file_type': 'json', 'sort_order': 'desc', 'limit': 30}
        fed_resp = requests.get(base_url, params=fed_params, timeout=10)
        try:
            fed_resp.raise_for_status()
            fed_data = fed_resp.json()
        except Exception as e:
            debug['fed_api_error'] = str(e)
            return get_interest_rates_yfinance(debug=debug)
        if not fed_data.get('observations'):
            debug['error_message'] = 'No FRED FEDFUNDS observations - fallback'
            return get_interest_rates_yfinance(debug=debug)
        fed_obs = fed_data['observations']
        fed_current = float(fed_obs[0]['value'])
        fed_previous = float(fed_obs[1]['value']) if len(fed_obs) > 1 else fed_current
        fed_30d_ago = float(fed_obs[-1]['value']) if len(fed_obs) > 1 else fed_current
        fed_change = fed_current - fed_previous
        fed_change_30d = fed_current - fed_30d_ago

        treasury_params = {'series_id': 'DGS10', 'api_key': fred_api_key,
                          'file_type': 'json', 'sort_order': 'desc', 'limit': 30}
        treasury_resp = requests.get(base_url, params=treasury_params, timeout=10)
        try:
            treasury_resp.raise_for_status()
            treasury_data = treasury_resp.json()
        except Exception as e:
            debug['treasury_api_error'] = str(e)
            treasury_current = None
            treasury_previous = None
            treasury_30d_ago = None
            treasury_change = None
            treasury_change_30d = None
        if not treasury_data.get('observations'):
            debug['error_message'] = 'No FRED DGS10 observations'
            treasury_current = None
            treasury_previous = None
            treasury_30d_ago = None
            treasury_change = None
            treasury_change_30d = None
        else:
            treasury_obs = treasury_data['observations']
            try:
                treasury_current = float(treasury_obs[0]['value'])
                treasury_previous = float(treasury_obs[1]['value']) if len(treasury_obs) > 1 else treasury_current
                treasury_30d_ago = float(treasury_obs[-1]['value']) if len(treasury_obs) > 1 else treasury_current
                treasury_change = treasury_current - treasury_previous
                treasury_change_30d = treasury_current - treasury_30d_ago
            except Exception as e:
                debug['treasury_conversion_error'] = str(e)
                treasury_current = None
                treasury_previous = None
                treasury_30d_ago = None
                treasury_change = None
                treasury_change_30d = None

        return {
            'available': True,
            'source': 'FRED_API',
            'fed_funds_rate': fed_current,
            'fed_change': fed_change,
            'fed_change_30d': fed_change_30d,
            'treasury_10y': treasury_current,
            'treasury_change': treasury_change,
            'treasury_change_30d': treasury_change_30d,
            'timestamp': datetime.now().isoformat(),
            'data_debug': debug
        }
    except Exception as e:
        debug['fred_api_total_error'] = str(e)
        return get_interest_rates_yfinance(debug=debug)

def get_interest_rates_yfinance(debug=None):
    if debug is None:
        debug = {}
    try:
        treasury_ticker = yf.Ticker("^TNX")
        hist = treasury_ticker.history(period="1mo")
        if hist.empty:
            debug['error_message'] = 'YFinance returned empty history'
            return {'available': False, 'reason': 'No data', 'data_debug': debug}
        treasury_current = hist['Close'][-1]
        treasury_30d_ago = hist['Close'][0]
        treasury_change_30d = treasury_current - treasury_30d_ago
        fed_funds_rate = 5.33  # Placeholder or configurable

        return {
            'available': True,
            'source': 'yfinance_fallback',
            'fed_funds_rate': fed_funds_rate,
            'fed_change': 0,
            'fed_change_30d': 0,
            'treasury_10y': treasury_current,
            'treasury_change': 0,
            'treasury_change_30d': treasury_change_30d,
            'timestamp': datetime.now().isoformat(),
            'data_debug': debug
        }
    except Exception as e:
        debug['yfinance_error'] = str(e)
        return {'available': False, 'reason': str(e), 'data_debug': debug}

def calculate_rates_score(rates_data):
    debug = rates_data.get('data_debug', {})
    if not rates_data.get('available', False):
        return {'available': False, 'score': 50, 'signal': 'NEUTRAL', 'reason': rates_data.get('reason', ''), 'data_debug': debug}
    fed_rate = rates_data.get('fed_funds_rate')
    fed_change_30d = rates_data.get('fed_change_30d')
    treasury_10y = rates_data.get('treasury_10y')
    treasury_change_30d = rates_data.get('treasury_change_30d')

    # Eğer None var ise debug'a sebep info ilet
    if fed_rate is None or treasury_10y is None:
        debug['scoring_error'] = 'fed_rate or treasury_10y is None, using fallback score'
        return {'available': False, 'score': 50, 'signal': 'NEUTRAL', 'reason':'Missing critical rate', 'data_debug': debug}

    fed_score = 80 if fed_rate <= 1.5 else \
                65 if fed_rate <= 3.0 else \
                50 if fed_rate <= 4.5 else \
                35 if fed_rate <= 5.5 else 25
    treasury_score = 70 if treasury_10y <= 2.5 else \
                     55 if treasury_10y <= 3.5 else \
                     45 if treasury_10y <= 4.5 else 30
    base_score = fed_score * 0.6 + treasury_score * 0.4

    total_change = (fed_change_30d or 0) + (treasury_change_30d or 0)

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
        'fed_funds_rate': round(fed_rate, 2) if fed_rate is not None else None,
        'treasury_10y': round(treasury_10y, 2) if treasury_10y is not None else None,
        'fed_change_30d': round(fed_change_30d, 2) if fed_change_30d is not None else None,
        'treasury_change_30d': round(treasury_change_30d, 2) if treasury_change_30d is not None else None,
        'source': rates_data.get('source', 'unknown'),
        'timestamp': datetime.now().isoformat(),
        'data_debug': debug
    }

def get_rates_signal():
    try:
        rates_data = get_interest_rates_fred_cached()
        result = calculate_rates_score(rates_data)
        return result
    except Exception as e:
        return {
            'available': True,
            'score': 50,
            'signal': 'NEUTRAL',
            'error_message': str(e),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    print("Testing interest_rates_layer.py with debug:")
    results = get_rates_signal()
    print(results)
