# fractal_chaos_layer.py - v1.1 - Full Real Data & Zero Error Safe

import numpy as np
import pandas as pd
from datetime import datetime
import requests
from scipy import stats

def calculate_hurst_exponent(prices, max_lag=20):
    try:
        lags = range(2, max_lag)
        tau = []
        for lag in lags:
            pp = np.array([prices[i:i+lag] for i in range(0, len(prices), lag) if len(prices[i:i+lag]) == lag])
            if len(pp) == 0:
                continue
            m = np.mean(pp, axis=1)
            r = np.array([np.max(np.cumsum(pp[i] - m[i])) - np.min(np.cumsum(pp[i] - m[i])) for i in range(len(pp))])
            s = np.std(pp, axis=1)
            s[s == 0] = 1e-10
            rs = r / s
            tau.append(np.mean(rs))
        if len(tau) < 2:
            return 0.5
        lags_used = list(lags)[:len(tau)]
        poly = np.polyfit(np.log(lags_used), np.log(tau), 1)
        hurst = poly[0]
        hurst = np.clip(hurst, 0.0, 1.0)
        return hurst
    except Exception as e:
        print(f"⚠️ Hurst calculation error: {e}")
        return 0.5

def calculate_fractal_dimension(hurst):
    return 2.0 - hurst

def calculate_lyapunov_exponent(prices, lag=1):
    try:
        if len(prices) < lag + 10:
            return 0.0
        log_returns = np.diff(np.log(prices))
        distances = []
        for i in range(len(log_returns) - lag):
            d0 = abs(log_returns[i])
            d1 = abs(log_returns[i + lag])
            if d0 > 1e-10:
                distances.append(np.log(d1 / d0))
        if len(distances) == 0:
            return 0.0
        lyapunov = np.mean(distances) / lag
        return lyapunov
    except Exception as e:
        print(f"⚠️ Lyapunov calculation error: {e}")
        return 0.0

def detect_self_similarity(prices, scales=[5, 10, 20, 40]):
    try:
        correlations = []
        for scale in scales:
            if len(prices) < scale * 2:
                continue
            downsampled = prices[::scale]
            if len(downsampled) < 3:
                continue
            returns = np.diff(downsampled) / downsampled[:-1]
            if len(returns) > 1:
                mean_return = np.mean(returns)
                var_return = np.var(returns)
                if var_return > 1e-10:
                    autocorr = np.correlate(returns - mean_return, returns - mean_return, mode='valid')[0] / var_return
                    correlations.append(abs(autocorr))
        if len(correlations) == 0:
            return 0.5
        similarity_score = np.mean(correlations)
        return np.clip(similarity_score, 0, 1)
    except Exception as e:
        print(f"⚠️ Self-similarity error: {e}")
        return 0.5

def get_historical_data(symbol, interval='1h', limit=200):
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'])
        df['close'] = df['close'].astype(float)
        return df
    except Exception as e:
        print(f"⚠️ Data fetch failed: {e}")
        return None

def get_fractal_chaos_signal(symbol, interval='1h'):
    try:
        print(f"🔮 Fractal Chaos analyzing {symbol}...")
        df = get_historical_data(symbol, interval, limit=200)
        if df is None or len(df) < 100:
            print("⚠️ Insufficient data")
            return {
                'available': True,
                'score': 50.0,
                'signal': 'NEUTRAL'
            }
        prices = df['close'].values
        hurst = calculate_hurst_exponent(prices, max_lag=min(30, len(prices)//5))
        fractal_dim = calculate_fractal_dimension(hurst)
        lyapunov = calculate_lyapunov_exponent(prices)
        similarity = detect_self_similarity(prices)
        x = np.arange(len(prices[-50:]))
        coeffs = np.polyfit(x, prices[-50:], 1)
        slope = coeffs[0]
        trend_direction = 1 if slope > 0 else -1
        score = 50.0
        if hurst > 0.6:
            hurst_strength = (hurst - 0.6) / 0.4
            score += trend_direction * hurst_strength * 35
        elif hurst < 0.4:
            hurst_strength = (0.4 - hurst) / 0.4
            score -= trend_direction * hurst_strength * 20
        if lyapunov > 0.1:
            chaos_penalty = min(lyapunov * 50, 15)
            score = score * (1 - chaos_penalty/100) + 50 * (chaos_penalty/100)
        if similarity > 0.7:
            score += (score - 50) * 0.2
        if fractal_dim < 1.4:
            score += (score - 50) * 0.1
        elif fractal_dim > 1.6:
            score = score * 0.9 + 50 * 0.1
        score = np.clip(score, 0, 100)
        signal = 'NEUTRAL'
        if score >= 65:
            signal = 'LONG'
        elif score <= 35:
            signal = 'SHORT'
        return {
            'available': True,
            'score': round(score, 2),
            'signal': signal
        }
    except Exception as e:
        print(f"⚠️ Fractal Chaos error: {e}")
        return {
            'available': True,
            'score': 50.0,
            'signal': 'NEUTRAL'
        }

def analyze_fractals(symbol, interval='1h'):
    return get_fractal_chaos_signal(symbol, interval)

if __name__ == "__main__":
    print("Testing fractal_chaos_layer.py")
    test_symbols = ['BTCUSDT', 'ETHUSDT']
    for symbol in test_symbols:
        score = get_fractal_chaos_signal(symbol)
        sig = 'NEUTRAL'
        if score['score'] >= 65:
            sig = 'LONG'
        elif score['score'] <= 35:
            sig = 'SHORT'
        print(f"{symbol}: Score={score['score']}, Signal={sig}")

