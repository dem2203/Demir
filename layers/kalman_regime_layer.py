"""🔮 KALMAN REGIME - v16.5 COMPATIBLE"""
import numpy as np
import requests
import pandas as pd

def fetch_ohlcv(symbol, interval='1h', limit=200):
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        df = pd.DataFrame(data, columns=['t','o','h','l','c','v','ct','qv','t2','tbb','tbq','ig'])
        df['close'] = df['c'].astype(float)
        df['high'] = df['h'].astype(float)
        df['low'] = df['l'].astype(float)
        return df
    except:
        return None

def calculate_atr(df, length=14):
    try:
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        close = df['close'].astype(float)
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=length).mean()
        return atr.iloc[-1] if len(atr) > 0 else 1.0
    except:
        return 1.0

def kalman_filter(prices):
    try:
        Q, R = 1e-5, 0.01
        xhat = prices[0]
        P = 1.0
        filtered = []
        for z in prices:
            P = P + Q
            K = P / (P + R)
            xhat = xhat + K * (z - xhat)
            P = (1 - K) * P
            filtered.append(xhat)
        return filtered[-1]
    except:
        return np.mean(prices)

def analyze_kalman_regime(symbol='BTCUSDT'):
    """COMPATIBLE: analyze_kalman_regime or kalman_filter_analysis"""
    try:
        df = fetch_ohlcv(symbol, '1h', 200)
        if df is None or len(df) < 100:
            return {'available': False, 'score': 50.0, 'signal': 'NEUTRAL'}
        
        prices = df['close'].values
        atr = calculate_atr(df, 14)
        kalman_val = kalman_filter(prices)
        latest = prices[-1]
        distance = latest - kalman_val
        rel_dist = distance / atr if atr > 0 else 0
        
        score = 50.0
        if latest > kalman_val + atr:
            score = min(90, 50 + abs(rel_dist) * 20)
            signal = "BULLISH"
        elif latest < kalman_val - atr:
            score = max(10, 50 - abs(rel_dist) * 20)
            signal = "BEARISH"
        else:
            score = 50 + rel_dist * 10
            signal = "NEUTRAL"
        
        return {
            'available': True,
            'score': round(max(0, min(100, score)), 2),
            'signal': signal
        }
    except:
        return {'available': False, 'score': 50.0, 'signal': 'NEUTRAL'}

# COMPATIBLE NAMES
kalman_filter_analysis = analyze_kalman_regime
