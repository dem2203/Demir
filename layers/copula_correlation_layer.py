"""
🔮 COPULA CORRELATION LAYER v1.0
================================
Date: 4 Kasım 2025, 09:20 CET
Phase: 7.5 - Quantum Mathematics

AMAÇ:
-----
Copula theory kullanarak asset'ler arasındaki tail dependencies
ve extreme event correlations tespit etmek. Normal correlation'ın
yakalayamadığı non-linear dependencies'i modellemek.

MATEMATİK:
----------
1. Gaussian Copula:
   C(u,v) = Φ_ρ(Φ^(-1)(u), Φ^(-1)(v))
   
2. t-Copula (heavy tails):
   Extreme events için daha robust

3. Tail Dependence:
   λ_U = lim P(Y>y|X>x) as x,y→∞ (upper tail)
   λ_L = lim P(Y<y|X<x) as x,y→-∞ (lower tail)

4. Portfolio Risk:
   Copula-based VaR ve CVaR

SINYAL LOJİĞİ:
--------------
- Positive tail dependency + BTC up → LONG (65-85)
- Negative tail dependency + BTC down → SHORT (15-35)
- Decoupling detected → Independent signal (40-60)

SKOR: 0-100
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import requests
from scipy.stats import norm, kendalltau, spearmanr

# ============================================================================
# COPULA FUNCTIONS
# ============================================================================

def gaussian_copula_density(u, v, rho):
    """
    Gaussian copula density
    
    Args:
        u, v (float): Uniform marginals [0,1]
        rho (float): Correlation parameter
        
    Returns:
        float: Copula density
    """
    try:
        x = norm.ppf(u)
        y = norm.ppf(v)
        
        exponent = (x**2 + y**2 - 2*rho*x*y) / (2*(1-rho**2))
        density = np.exp(-exponent) / np.sqrt(1-rho**2)
        
        return density
    except:
        return 1.0


def estimate_copula_parameter(returns_x, returns_y):
    """
    Copula parameter estimate (Kendall's tau method)
    
    Args:
        returns_x, returns_y (array): Return series
        
    Returns:
        float: Copula correlation parameter
    """
    try:
        # Kendall's tau
        tau, _ = kendalltau(returns_x, returns_y)
        
        # Convert to copula parameter (Gaussian)
        rho = np.sin(tau * np.pi / 2)
        
        return rho
    except:
        return 0.0


def calculate_tail_dependence(returns_x, returns_y, threshold=0.95):
    """
    Upper and lower tail dependencies
    
    Args:
        returns_x, returns_y (array): Return series
        threshold (float): Tail threshold (0.95 = top/bottom 5%)
        
    Returns:
        dict: {'upper': λ_U, 'lower': λ_L}
    """
    try:
        n = len(returns_x)
        
        # Upper tail (extreme positive)
        upper_thresh_x = np.percentile(returns_x, threshold * 100)
        upper_thresh_y = np.percentile(returns_y, threshold * 100)
        
        upper_x = returns_x > upper_thresh_x
        upper_y = returns_y > upper_thresh_y
        upper_both = upper_x & upper_y
        
        lambda_upper = np.sum(upper_both) / np.sum(upper_x) if np.sum(upper_x) > 0 else 0
        
        # Lower tail (extreme negative)
        lower_thresh_x = np.percentile(returns_x, (1 - threshold) * 100)
        lower_thresh_y = np.percentile(returns_y, (1 - threshold) * 100)
        
        lower_x = returns_x < lower_thresh_x
        lower_y = returns_y < lower_thresh_y
        lower_both = lower_x & lower_y
        
        lambda_lower = np.sum(lower_both) / np.sum(lower_x) if np.sum(lower_x) > 0 else 0
        
        return {
            'upper': lambda_upper,
            'lower': lambda_lower
        }
    except:
        return {'upper': 0.0, 'lower': 0.0}


# ============================================================================
# DATA FETCHING
# ============================================================================

def get_historical_data(symbol, interval='1h', limit=200):
    """Binance historical data"""
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        df['close'] = df['close'].astype(float)
        return df
    except:
        return None


# ============================================================================
# COPULA CORRELATION SIGNAL
# ============================================================================

def get_copula_correlation_signal(symbol, interval='1h'):
    """
    Copula Correlation layer ana fonksiyonu
    
    MANTIK:
    1. Target coin + BTC data çek
    2. Returns hesapla
    3. Copula parameter estimate
    4. Tail dependencies hesapla
    5. BTC direction + tail dependency → signal
    
    Args:
        symbol (str): Trading pair (ETHUSDT, SOLUSDT etc.)
        interval (str): Timeframe
        
    Returns:
        float: Score (0-100)
    """
    try:
        print(f"🔮 Copula Correlation analyzing {symbol}...")
        
        # 1. Target coin data
        df_target = get_historical_data(symbol, interval, limit=200)
        if df_target is None or len(df_target) < 100:
            print("⚠️ Target data failed")
            return 50.0
        
        # 2. BTC data (reference asset)
        df_btc = get_historical_data('BTCUSDT', interval, limit=200)
        if df_btc is None or len(df_btc) < 100:
            print("⚠️ BTC data failed")
            return 50.0
        
        # Align lengths
        min_len = min(len(df_target), len(df_btc))
        prices_target = df_target['close'].values[-min_len:]
        prices_btc = df_btc['close'].values[-min_len:]
        
        # 3. Returns
        returns_target = np.diff(prices_target) / prices_target[:-1]
        returns_btc = np.diff(prices_btc) / prices_btc[:-1]
        
        # 4. Copula parameter
        rho = estimate_copula_parameter(returns_target, returns_btc)
        print(f"   Copula Parameter (ρ): {rho:.3f}")
        
        # 5. Tail dependencies
        tails = calculate_tail_dependence(returns_target, returns_btc)
        lambda_upper = tails['upper']
        lambda_lower = tails['lower']
        
        print(f"   Upper Tail Dependency: {lambda_upper:.3f}")
        print(f"   Lower Tail Dependency: {lambda_lower:.3f}")
        
        # 6. BTC direction (recent trend)
        btc_trend = np.mean(returns_btc[-20:])  # Last 20 candles
        btc_direction = 1 if btc_trend > 0 else -1
        
        print(f"   BTC Trend: {'UP' if btc_direction > 0 else 'DOWN'}")
        
        # 7. Score hesapla
        score = 50.0
        
        # Correlation component
        correlation_strength = abs(rho)
        
        if rho > 0.3:  # Positive correlation
            # Follow BTC
            score += btc_direction * correlation_strength * 30
            print("   ✅ Positive correlation - following BTC")
        
        elif rho < -0.3:  # Negative correlation
            # Inverse to BTC
            score -= btc_direction * correlation_strength * 30
            print("   ⚠️ Negative correlation - inverse to BTC")
        
        else:  # Low correlation
            # Independent signal
            target_trend = np.mean(returns_target[-20:])
            score += (1 if target_trend > 0 else -1) * 15
            print("   📊 Low correlation - independent")
        
        # Tail dependency boost
        if btc_direction > 0 and lambda_upper > 0.5:
            # Strong upper tail → amplify LONG
            score += 15
            print("   🚀 Strong upper tail dependency")
        
        if btc_direction < 0 and lambda_lower > 0.5:
            # Strong lower tail → amplify SHORT
            score -= 15
            print("   ⚠️ Strong lower tail dependency")
        
        # Clip 0-100
        score = np.clip(score, 0, 100)
        
        print(f"✅ Copula Correlation Score: {score:.1f}/100")
        
        return score
        
    except Exception as e:
        print(f"❌ Copula Correlation error: {e}")
        return 50.0


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("🔮 COPULA CORRELATION LAYER TEST")
    print("="*80)
    
    test_symbols = ['ETHUSDT', 'SOLUSDT']
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        score = get_copula_correlation_signal(symbol)
        
        if score >= 65:
            signal = "🟢 LONG"
        elif score <= 35:
            signal = "🔴 SHORT"
        else:
            signal = "⚪ NEUTRAL"
        
        print(f"   Signal: {signal}")
        print(f"   Score: {score:.1f}/100")
        print("-"*80)
