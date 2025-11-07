"""🔮 COPULA CORRELATION - v16.5 COMPATIBLE"""
import numpy as np
import requests
import pandas as pd

def fetch_pair_data(symbol, interval='1h', limit=200):
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200: return None
        data = response.json()
        df = pd.DataFrame(data, columns=['t','o','h','l','c','v','ct','qv','tr','tbb','tbq','ig'])
        df['close'] = df['c'].astype(float)
        return df
    except: return None

def calculate_tail_dependence(returns_x, returns_y, threshold=0.1):
    try:
        upper_thresh_x = np.percentile(returns_x, (1 - threshold) * 100)
        upper_thresh_y = np.percentile(returns_y, (1 - threshold) * 100)
        upper_x = returns_x > upper_thresh_x
        upper_y = returns_y > upper_thresh_y
        upper_both = upper_x & upper_y
        lambda_upper = np.sum(upper_both) / max(np.sum(upper_x), 1) if np.sum(upper_x) > 0 else 0
        
        lower_thresh_x = np.percentile(returns_x, (1 - threshold) * 100)
        lower_thresh_y = np.percentile(returns_y, (1 - threshold) * 100)
        lower_x = returns_x < lower_thresh_x
        lower_y = returns_y < lower_thresh_y
        lower_both = lower_x & lower_y
        lambda_lower = np.sum(lower_both) / max(np.sum(lower_x), 1) if np.sum(lower_x) > 0 else 0
        
        return {'lambda_upper': lambda_upper, 'lambda_lower': lambda_lower}
    except:
        return {'lambda_upper': 0.5, 'lambda_lower': 0.5}

def analyze_copula_correlation(symbol_1='BTCUSDT', symbol_2='ETHUSDT'):
    """COMPATIBLE FUNCTION"""
    try:
        df1 = fetch_pair_data(symbol_1, '1h', 200)
        df2 = fetch_pair_data(symbol_2, '1h', 200)
        
        if df1 is None or df2 is None:
            return {'available': False, 'score': 50.0, 'signal': 'NEUTRAL'}
        
        prices_1 = df1['close'].values
        prices_2 = df2['close'].values
        
        returns_1 = np.diff(np.log(prices_1))
        returns_2 = np.diff(np.log(prices_2))
        
        corr_pearson = np.corrcoef(returns_1, returns_2)[0, 1]
        tails = calculate_tail_dependence(returns_1, returns_2, threshold=0.1)
        lambda_upper = tails['lambda_upper']
        lambda_lower = tails['lambda_lower']
        
        asymmetry = abs(lambda_upper - lambda_lower)
        
        rank_1 = np.argsort(np.argsort(returns_1))
        rank_2 = np.argsort(np.argsort(returns_2))
        corr_rank = np.corrcoef(rank_1, rank_2)[0, 1]
        
        score = 50.0
        if abs(corr_pearson) < 0.3:
            score += 20
            correlation_signal = "DIVERSIFY"
        elif abs(corr_pearson) > 0.8:
            score -= 20
            correlation_signal = "AVOID"
        else:
            correlation_signal = "MONITOR"
        
        if lambda_upper > 0.3:
            score -= min(lambda_upper * 20, 15)
        if lambda_lower > 0.3:
            score -= min(lambda_lower * 20, 15)
        if asymmetry > 0.3:
            score = score * 0.9 + 50 * 0.1
        
        copula_distortion = abs(corr_rank - corr_pearson)
        if copula_distortion > 0.2:
            score += 10
        
        score = max(0, min(100, score))
        signal = "DIVERSIFY" if score >= 65 else ("AVOID" if score <= 35 else "MONITOR")
        
        return {'available': True, 'score': round(score, 2), 'signal': signal}
    except:
        return {'available': False, 'score': 50.0, 'signal': 'NEUTRAL'}
