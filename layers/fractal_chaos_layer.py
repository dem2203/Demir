"""
🔮 FRACTAL CHAOS LAYER v1.0
===========================
Date: 4 Kasım 2025, 09:10 CET
Phase: 7.3 - Quantum Mathematics

AMAÇ:
-----
Mandelbrot fractals, Hurst exponent ve Chaos theory kullanarak
self-similarity patterns ve long-term memory tespit etmek.
Market'ın fractal yapısını analiz ederek trend persistence ölçmek.

MATEMATİK:
----------
1. Hurst Exponent (H):
   - H = 0.5: Random walk (Brownian motion)
   - H > 0.5: Persistent (trending), long-term memory
   - H < 0.5: Anti-persistent (mean-reverting)
   
   R/S Analysis: H = log(R/S) / log(n)

2. Fractal Dimension (D):
   - D = 2 - H
   - D < 1.5: Smooth trend
   - D > 1.5: Noisy, choppy

3. Lyapunov Exponent (λ):
   - λ > 0: Chaotic
   - λ = 0: Periodic
   - λ < 0: Stable

SINYAL LOJİĞİ:
--------------
- H > 0.6 + pozitif trend → Strong LONG (75-90)
- H > 0.6 + negatif trend → Strong SHORT (10-25)
- H < 0.4 → Mean reversion, NEUTRAL (45-55)
- 0.4 < H < 0.6 → Random walk, low confidence (40-60)

SKOR: 0-100
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import requests
from scipy import stats

# ============================================================================
# HURST EXPONENT CALCULATION (R/S Analysis)
# ============================================================================

def calculate_hurst_exponent(prices, max_lag=20):
    """
    Hurst exponent hesapla (Rescaled Range Analysis)
    
    H > 0.5: Persistent (trending)
    H = 0.5: Random walk
    H < 0.5: Anti-persistent (mean-reverting)
    
    Args:
        prices (array): Price series
        max_lag (int): Maximum lag for R/S calculation
        
    Returns:
        float: Hurst exponent (0-1)
    """
    try:
        lags = range(2, max_lag)
        tau = []
        
        for lag in lags:
            # Divide series into subseries of length 'lag'
            pp = np.array([prices[i:i+lag] for i in range(0, len(prices), lag) if len(prices[i:i+lag]) == lag])
            
            if len(pp) == 0:
                continue
            
            # Calculate mean for each subseries
            m = np.mean(pp, axis=1)
            
            # Calculate cumulative deviations
            r = np.array([np.max(np.cumsum(pp[i] - m[i])) - np.min(np.cumsum(pp[i] - m[i])) 
                          for i in range(len(pp))])
            
            # Calculate standard deviation for each subseries
            s = np.std(pp, axis=1)
            
            # Avoid division by zero
            s[s == 0] = 1e-10
            
            # Calculate R/S
            rs = r / s
            
            # Mean R/S for this lag
            tau.append(np.mean(rs))
        
        if len(tau) < 2:
            return 0.5  # Default: random walk
        
        # Linear regression: log(tau) vs log(lags)
        lags_used = list(lags)[:len(tau)]
        
        # Hurst = slope of log-log plot
        poly = np.polyfit(np.log(lags_used), np.log(tau), 1)
        hurst = poly[0]
        
        # Clamp to valid range
        hurst = np.clip(hurst, 0.0, 1.0)
        
        return hurst
        
    except Exception as e:
        print(f"⚠️ Hurst calculation error: {e}")
        return 0.5  # Default


def calculate_fractal_dimension(hurst):
    """
    Fractal dimension hesapla
    
    D = 2 - H
    
    Args:
        hurst (float): Hurst exponent
        
    Returns:
        float: Fractal dimension
    """
    return 2.0 - hurst


# ============================================================================
# LYAPUNOV EXPONENT (Chaos Measure)
# ============================================================================

def calculate_lyapunov_exponent(prices, lag=1):
    """
    Simplified Lyapunov exponent (chaos indicator)
    
    λ > 0: Chaotic behavior
    λ = 0: Periodic
    λ < 0: Stable
    
    Args:
        prices (array): Price series
        lag (int): Time lag
        
    Returns:
        float: Lyapunov exponent estimate
    """
    try:
        if len(prices) < lag + 10:
            return 0.0
        
        # Calculate log price returns
        log_returns = np.diff(np.log(prices))
        
        # Estimate divergence rate
        distances = []
        
        for i in range(len(log_returns) - lag):
            # Initial distance
            d0 = abs(log_returns[i])
            
            # Distance after lag steps
            d1 = abs(log_returns[i + lag])
            
            if d0 > 1e-10:
                distances.append(np.log(d1 / d0))
        
        if len(distances) == 0:
            return 0.0
        
        # Mean divergence rate
        lyapunov = np.mean(distances) / lag
        
        return lyapunov
        
    except Exception as e:
        print(f"⚠️ Lyapunov calculation error: {e}")
        return 0.0


# ============================================================================
# SELF-SIMILARITY DETECTION
# ============================================================================

def detect_self_similarity(prices, scales=[5, 10, 20, 40]):
    """
    Multi-scale analysis for fractal patterns
    
    Args:
        prices (array): Price series
        scales (list): Time scales to analyze
        
    Returns:
        float: Self-similarity score (0-1)
    """
    try:
        correlations = []
        
        for scale in scales:
            if len(prices) < scale * 2:
                continue
            
            # Downsample to different scales
            downsampled = prices[::scale]
            
            if len(downsampled) < 3:
                continue
            
            # Calculate returns at this scale
            returns = np.diff(downsampled) / downsampled[:-1]
            
            # Autocorrelation
            if len(returns) > 1:
                mean_return = np.mean(returns)
                var_return = np.var(returns)
                
                if var_return > 1e-10:
                    autocorr = np.correlate(returns - mean_return, returns - mean_return, mode='valid')[0] / var_return
                    correlations.append(abs(autocorr))
        
        if len(correlations) == 0:
            return 0.5
        
        # High correlation across scales = high self-similarity
        similarity_score = np.mean(correlations)
        
        return np.clip(similarity_score, 0, 1)
        
    except Exception as e:
        print(f"⚠️ Self-similarity error: {e}")
        return 0.5


# ============================================================================
# DATA FETCHING
# ============================================================================

def get_historical_data(symbol, interval='1h', limit=200):
    """
    Binance'den historical data çek
    """
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        df['close'] = df['close'].astype(float)
        
        return df
    except Exception as e:
        print(f"⚠️ Data fetch failed: {e}")
        return None


# ============================================================================
# FRACTAL CHAOS SIGNAL GENERATOR
# ============================================================================

def get_fractal_chaos_signal(symbol, interval='1h'):
    """
    Fractal Chaos layer main function
    
    Args:
        symbol (str): Trading pair
        interval (str): Timeframe
        
    Returns:
        dict: {'available': bool, 'score': float, 'signal': str}
    """
    try:
        score = analyze_fractals(symbol, interval)  # returns float
        
        # Convert score to signal
        if score >= 65:
            signal = 'LONG'
        elif score <= 35:
            signal = 'SHORT'
        else:
            signal = 'NEUTRAL'
        
        return {
            'available': True,
            'score': round(score, 2),
            'signal': signal
        }
    except Exception as e:
        print(f"⚠️ Fractal Chaos Error: {e}")
        return {
            'available': True,
            'score': 50.0,
            'signal': 'NEUTRAL'
        }
    """
    Fractal Chaos layer ana fonksiyonu
    
    MANTIK:
    -------
    1. Historical data çek (200 candle)
    2. Hurst exponent hesapla (trend persistence)
    3. Fractal dimension hesapla
    4. Lyapunov exponent (chaos measure)
    5. Self-similarity tespit et
    6. Trend direction + Hurst'e göre skor
    
    Args:
        symbol (str): Trading pair
        interval (str): Timeframe
        
    Returns:
        float: Score (0-100)
    """
    try:
        print(f"🔮 Fractal Chaos analyzing {symbol}...")
        
        # 1. Data çek
        df = get_historical_data(symbol, interval, limit=200)
        if df is None or len(df) < 100:
            print("⚠️ Insufficient data")
            return 50.0
        
        prices = df['close'].values
        
        # 2. Hurst exponent hesapla
        hurst = calculate_hurst_exponent(prices, max_lag=min(30, len(prices)//5))
        print(f"   Hurst Exponent: {hurst:.3f}")
        
        # Hurst interpretation
        if hurst > 0.6:
            persistence = "PERSISTENT (Trending)"
        elif hurst < 0.4:
            persistence = "ANTI-PERSISTENT (Mean-reverting)"
        else:
            persistence = "RANDOM WALK"
        print(f"   Behavior: {persistence}")
        
        # 3. Fractal dimension
        fractal_dim = calculate_fractal_dimension(hurst)
        print(f"   Fractal Dimension: {fractal_dim:.3f}")
        
        # 4. Lyapunov exponent
        lyapunov = calculate_lyapunov_exponent(prices)
        print(f"   Lyapunov: {lyapunov:.4f}")
        
        if lyapunov > 0:
            chaos_state = "CHAOTIC"
        else:
            chaos_state = "STABLE"
        print(f"   State: {chaos_state}")
        
        # 5. Self-similarity
        similarity = detect_self_similarity(prices)
        print(f"   Self-Similarity: {similarity:.3f}")
        
        # 6. Trend direction (simple linear regression)
        x = np.arange(len(prices[-50:]))
        coeffs = np.polyfit(x, prices[-50:], 1)
        slope = coeffs[0]
        trend_direction = 1 if slope > 0 else -1
        
        # 7. Skor hesapla
        score = 50.0  # Baseline
        
        # Hurst component (ana sinyal)
        if hurst > 0.6:
            # Persistent: trend following
            hurst_strength = (hurst - 0.6) / 0.4  # 0-1
            score += trend_direction * hurst_strength * 35  # ±35 points
            print(f"   🎯 Persistent trend detected")
        
        elif hurst < 0.4:
            # Anti-persistent: mean reversion (inverse signal)
            hurst_strength = (0.4 - hurst) / 0.4
            score -= trend_direction * hurst_strength * 20  # Opposite direction
            print(f"   ⚠️ Mean reversion expected")
        
        else:
            # Random walk: low confidence
            score = 50.0
            print(f"   📊 Random walk - neutral")
        
        # Chaos penalty (chaotic = unreliable)
        if lyapunov > 0.1:
            chaos_penalty = min(lyapunov * 50, 15)
            score = score * (1 - chaos_penalty/100) + 50 * (chaos_penalty/100)
            print(f"   ⚠️ Chaos detected - reducing confidence")
        
        # Self-similarity boost
        if similarity > 0.7:
            score += (score - 50) * 0.2  # Amplify signal 20%
            print(f"   ✨ High self-similarity - boosting signal")
        
        # Fractal dimension adjustment
        if fractal_dim < 1.4:  # Smooth trend
            score += (score - 50) * 0.1
        elif fractal_dim > 1.6:  # Choppy
            score = score * 0.9 + 50 * 0.1
        
        # Skor 0-100 aralığına sınırla
        score = np.clip(score, 0, 100)
        
        print(f"✅ Fractal Chaos Score: {score:.1f}/100")
        
        return score
        
    except Exception as e:
        print(f"❌ Fractal Chaos error: {e}")
        return 50.0


# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

def analyze_fractals(symbol, interval='1h'):
    """
    Alias for backward compatibility
    """
    return get_fractal_chaos_signal(symbol, interval)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("🔮 FRACTAL CHAOS LAYER TEST")
    print("="*80)
    
    test_symbols = ['BTCUSDT', 'ETHUSDT']
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        score = get_fractal_chaos_signal(symbol)
        
        if score >= 65:
            signal = "🟢 LONG"
        elif score <= 35:
            signal = "🔴 SHORT"
        else:
            signal = "⚪ NEUTRAL"
        
        print(f"   Signal: {signal}")
        print(f"   Score: {score:.1f}/100")
        print("-"*80)
