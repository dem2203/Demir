"""
🔮 FRACTAL CHAOS LAYER v16.5
============================

Date: 7 Kasım 2025, 14:27 CET
Phase: 7+8 - Quantum Trading AI

AMAÇ:
-----
Hurst exponent, Lyapunov exponent, self-similarity ile
fractal structure ve chaos tespit etmek. REAL market data.

MATHEMATIK:
-----------
Hurst Exponent: H = log(τ) / log(lag)  (0.5 = random, >0.5 = trending)
Lyapunov Exponent: λ = lim(1/n)Σln|dX/dt|  (>0 = chaos)
Fractal Dimension: D = 2 - H
"""

import numpy as np
import requests
import pandas as pd
from datetime import datetime

def get_historical_data(symbol, interval='1h', limit=200):
    """Fetch REAL historical data from Binance"""
    debug = {}
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            debug['http_error'] = f"HTTP {response.status_code}"
            return None, debug
        
        data = response.json()
        df = pd.DataFrame(data, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
            'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        
        df['close'] = df['close'].astype(float)
        debug['info'] = f"Fetched {len(df)} real candles"
        return df, debug
        
    except Exception as e:
        debug['exception'] = str(e)
        return None, debug

def calculate_hurst_exponent(prices, max_lag=20):
    """
    Calculate Hurst exponent for trend strength
    H > 0.5 = trending, H < 0.5 = mean reverting, H = 0.5 = random
    """
    try:
        lags = range(2, max_lag)
        tau = []
        
        for lag in lags:
            pp = np.array([prices[i:i+lag] for i in range(0, len(prices), lag) 
                          if len(prices[i:i+lag]) == lag])
            if len(pp) == 0:
                continue
            
            m = np.mean(pp, axis=1)
            r = np.array([np.max(np.cumsum(pp[i] - m[i])) - np.min(np.cumsum(pp[i] - m[i])) 
                         for i in range(len(pp))])
            s = np.std(pp, axis=1)
            s[s == 0] = 1e-10
            
            rs = r / s
            tau.append(np.mean(rs))
        
        if len(tau) < 2:
            return 0.5
        
        lags_used = list(lags)[:len(tau)]
        poly = np.polyfit(np.log(lags_used), np.log(tau), 1)
        hurst = poly[0]
        
        return max(0, min(1, hurst))
    except:
        return 0.5

def calculate_lyapunov_exponent(prices, lag=1):
    """Lyapunov exponent - chaos indicator"""
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
    except:
        return 0.0

def detect_self_similarity(prices, scales=[5, 10, 20, 40]):
    """Detect self-similarity across scales"""
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
                mean_ret = np.mean(returns)
                var_ret = np.var(returns)
                
                if var_ret > 1e-10:
                    autocorr = np.correlate(returns - mean_ret, returns - mean_ret, 
                                           mode='valid')[0] / var_ret
                    correlations.append(abs(autocorr))
        
        if len(correlations) == 0:
            return 0.5
        
        return max(0, min(1, np.mean(correlations)))
    except:
        return 0.5

def get_fractal_chaos_signal(symbol, interval='1h'):
    """
    Fractal Chaos Layer ana fonksiyonu
    
    MANTIK:
    1. Get REAL market data
    2. Calculate Hurst (trending vs mean revert)
    3. Calculate Lyapunov (chaos level)
    4. Calculate fractal dimension
    5. Detect self-similarity
    6. Generate score (0-100)
    """
    debug = {}
    
    try:
        print(f"🔮 Fractal Chaos analyzing {symbol}...")
        
        # 1. Get REAL data
        df, fetch_debug = get_historical_data(symbol, interval, limit=200)
        debug.update(fetch_debug)
        
        if df is None or len(df) < 100:
            print(f"❌ Data fetch failed")
            return {
                'available': False,
                'score': 50.0,
                'signal': 'NEUTRAL',
                'error_message': 'Insufficient fractal data',
                'data_debug': debug
            }
        
        prices = df['close'].values
        print(f" 📊 Real prices: {len(prices)} candles")
        
        # 2. Hurst exponent
        hurst = calculate_hurst_exponent(prices, max_lag=min(30, len(prices)//5))
        fractal_dim = 2.0 - hurst
        
        print(f" 📈 Hurst Exponent: {hurst:.3f}")
        print(f" 🔷 Fractal Dimension: {fractal_dim:.3f}")
        
        # 3. Lyapunov (chaos)
        lyapunov = calculate_lyapunov_exponent(prices)
        print(f" 🌪️  Lyapunov Exponent: {lyapunov:.4f}")
        
        # 4. Self-similarity
        similarity = detect_self_similarity(prices)
        print(f" 🔄 Self-Similarity: {similarity:.3f}")
        
        # 5. Recent trend
        x = np.arange(len(prices[-50:]))
        coeffs = np.polyfit(x, prices[-50:], 1)
        slope = coeffs[0]
        trend_direction = 1 if slope > 0 else -1
        print(f" 📊 Trend: {'UP' if trend_direction > 0 else 'DOWN'}")
        
        # 6. Score calculation
        score = 50.0
        
        # Hurst component
        if hurst > 0.6:
            hurst_strength = (hurst - 0.6) / 0.4
            score += trend_direction * hurst_strength * 35
            print(f" ✅ Strong trending (Hurst > 0.6)")
        elif hurst < 0.4:
            hurst_strength = (0.4 - hurst) / 0.4
            score -= trend_direction * hurst_strength * 20
            print(f" 🔄 Mean revert (Hurst < 0.4)")
        
        # Lyapunov component (chaos penalty)
        if lyapunov > 0.1:
            chaos_penalty = min(lyapunov * 50, 15)
            score = score * (1 - chaos_penalty/100) + 50 * (chaos_penalty/100)
            print(f" ⚠️  Chaos detected ({chaos_penalty:.1f} penalty)")
        
        # Self-similarity component
        if similarity > 0.7:
            score += (score - 50) * 0.2
            print(f" 🔄 High self-similarity (+boost)")
        
        # Fractal dimension component
        if fractal_dim < 1.4:
            score += (score - 50) * 0.1
            print(f" 🔷 Dense fractal structure (+boost)")
        elif fractal_dim > 1.6:
            score = score * 0.9 + 50 * 0.1
            print(f" 🔷 Sparse fractal structure (-penalty)")
        
        score = max(0, min(100, score))
        
        print(f"✅ Fractal Chaos Score: {score:.1f}/100")
        
        # Signal
        if score >= 65:
            signal = "LONG"
        elif score <= 35:
            signal = "SHORT"
        else:
            signal = "NEUTRAL"
        
        return {
            'available': True,
            'score': round(score, 2),
            'signal': signal,
            'hurst': round(hurst, 3),
            'fractal_dimension': round(fractal_dim, 3),
            'lyapunov': round(lyapunov, 4),
            'self_similarity': round(similarity, 3),
            'timestamp': datetime.now().isoformat(),
            'data_debug': debug
        }
        
    except Exception as e:
        print(f"❌ Fractal Chaos error: {e}")
        debug['exception'] = str(e)
        return {
            'available': False,
            'score': 50.0,
            'signal': 'NEUTRAL',
            'error_message': str(e),
            'data_debug': debug
        }


if __name__ == "__main__":
    print("="*80)
    print("🔮 FRACTAL CHAOS LAYER TEST")
    print("="*80)
    
    test_symbols = ['BTCUSDT', 'ETHUSDT']
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        result = get_fractal_chaos_signal(symbol)
        print(f" Score: {result['score']}, Signal: {result['signal']}\n")
