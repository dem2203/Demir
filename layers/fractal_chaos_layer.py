"""🔮 FRACTAL CHAOS - v16.5 COMPATIBLE"""
import numpy as np
import requests
import pandas as pd

def get_historical_data(symbol, interval='1h', limit=200):
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        df = pd.DataFrame(data, columns=['ot','o','h','l','c','v','ct','qv','t','tbb','tbq','ig'])
        df['close'] = df['c'].astype(float)
        return df
    except:
        return None

def calculate_hurst_exponent(prices, max_lag=20):
    try:
        lags = range(2, max_lag)
        tau = []
        for lag in lags:
            pp = np.array([prices[i:i+lag] for i in range(0, len(prices), lag) if len(prices[i:i+lag]) == lag])
            if len(pp) == 0: continue
            m = np.mean(pp, axis=1)
            r = np.array([np.max(np.cumsum(pp[i] - m[i])) - np.min(np.cumsum(pp[i] - m[i])) for i in range(len(pp))])
            s = np.std(pp, axis=1)
            s[s == 0] = 1e-10
            rs = r / s
            tau.append(np.mean(rs))
        if len(tau) < 2: return 0.5
        lags_used = list(lags)[:len(tau)]
        poly = np.polyfit(np.log(lags_used), np.log(tau), 1)
        return max(0, min(1, poly[0]))
    except:
        return 0.5

def calculate_lyapunov_exponent(prices, lag=1):
    try:
        if len(prices) < lag + 10: return 0.0
        log_returns = np.diff(np.log(prices))
        distances = []
        for i in range(len(log_returns) - lag):
            d0 = abs(log_returns[i])
            d1 = abs(log_returns[i + lag])
            if d0 > 1e-10:
                distances.append(np.log(d1 / d0))
        if len(distances) == 0: return 0.0
        return np.mean(distances) / lag
    except:
        return 0.0

def analyze_fractal_dimension(symbol='BTCUSDT'):
    """COMPATIBLE FUNCTION"""
    try:
        df = get_historical_data(symbol, '1h', 200)
        if df is None or len(df) < 100:
            return {'available': False, 'score': 50.0, 'signal': 'NEUTRAL'}
        
        prices = df['close'].values
        hurst = calculate_hurst_exponent(prices, max_lag=min(30, len(prices)//5))
        lyapunov = calculate_lyapunov_exponent(prices)
        
        # Trend
        x = np.arange(len(prices[-50:]))
        coeffs = np.polyfit(x, prices[-50:], 1)
        trend_dir = 1 if coeffs[0] > 0 else -1
        
        score = 50.0
        if hurst > 0.6:
            hurst_strength = (hurst - 0.6) / 0.4
            score += trend_dir * hurst_strength * 35
        elif hurst < 0.4:
            hurst_strength = (0.4 - hurst) / 0.4
            score -= trend_dir * hurst_strength * 20
        
        if lyapunov > 0.1:
            chaos_penalty = min(lyapunov * 50, 15)
            score = score * (1 - chaos_penalty/100) + 50 * (chaos_penalty/100)
        
        score = max(0, min(100, score))
        signal = "LONG" if score >= 65 else ("SHORT" if score <= 35 else "NEUTRAL")
        
        return {'available': True, 'score': round(score, 2), 'signal': signal}
    except:
        return {'available': False, 'score': 50.0, 'signal': 'NEUTRAL'}
