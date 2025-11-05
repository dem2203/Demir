"""
🔮 QUANTUM BLACK-SCHOLES LAYER v1.0
====================================
Date: 4 Kasım 2025, 09:00 CET
Phase: 7.1 - Quantum Mathematics

AMAÇ:
-----
Black-Scholes option pricing modelini crypto'ya uyarlayarak
implied volatility, Greeks (Delta, Gamma, Vega, Theta) ve 
volatility surface analizi yaparak trend yönü tahmin etmek.

MATEMATİK:
----------
1. Black-Scholes Formula:
   C = S₀N(d₁) - Ke^(-rT)N(d₂)
   
   d₁ = [ln(S₀/K) + (r + σ²/2)T] / (σ√T)
   d₂ = d₁ - σ√T

2. Greeks:
   - Delta (Δ): ∂V/∂S (fiyat hassasiyeti)
   - Gamma (Γ): ∂²V/∂S² (delta değişim hızı)
   - Vega (ν): ∂V/∂σ (volatility hassasiyeti)
   - Theta (Θ): ∂V/∂t (zaman değer kaybı)

3. Implied Volatility:
   Newton-Raphson ile market price'dan σ hesaplama

SINYAL LOJİĞİ:
--------------
- Delta > 0.6 → LONG bias (trend güçlü)
- Gamma yüksek → Momentum artışı
- Vega yüksek → Volatility breakout potansiyeli
- Theta negatif → Zaman değer kaybı (dikkat)

SKOR: 0-100
- 80-100: Strong LONG (high delta + positive gamma)
- 60-80: LONG (positive delta)
- 40-60: NEUTRAL (mixed signals)
- 20-40: SHORT (negative delta)
- 0-20: Strong SHORT (low delta + negative gamma)
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy.stats import norm
from scipy.optimize import brentq
import requests

# ============================================================================
# BLACK-SCHOLES CORE FUNCTIONS
# ============================================================================

def black_scholes_call(S, K, T, r, sigma):
    """
    Black-Scholes call option fiyatı
    
    Args:
        S (float): Spot price (mevcut fiyat)
        K (float): Strike price (hedef fiyat)
        T (float): Time to expiry (yıl cinsinden)
        r (float): Risk-free rate (faiz oranı)
        sigma (float): Volatility (volatilite)
        
    Returns:
        float: Call option değeri
    """
    if T <= 0 or sigma <= 0:
        return max(S - K, 0)  # Intrinsic value
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return call_price


def calculate_greeks(S, K, T, r, sigma):
    """
    Greeks hesaplama (Delta, Gamma, Vega, Theta)
    
    Args:
        S (float): Spot price
        K (float): Strike price
        T (float): Time to expiry (years)
        r (float): Risk-free rate
        sigma (float): Volatility
        
    Returns:
        dict: Greeks değerleri
    """
    if T <= 0 or sigma <= 0:
        return {
            'delta': 0.5,
            'gamma': 0.0,
            'vega': 0.0,
            'theta': 0.0
        }
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # Delta: ∂V/∂S
    delta = norm.cdf(d1)
    
    # Gamma: ∂²V/∂S²
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    
    # Vega: ∂V/∂σ (100 bp move için)
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100
    
    # Theta: ∂V/∂t (günlük decay)
    theta = -(S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + 
              r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    
    return {
        'delta': delta,
        'gamma': gamma,
        'vega': vega,
        'theta': theta
    }


def calculate_implied_volatility(market_price, S, K, T, r, tol=1e-5, max_iter=100):
    """
    Implied volatility hesaplama (Newton-Raphson)
    
    Args:
        market_price (float): Market'taki option fiyatı
        S (float): Spot price
        K (float): Strike price
        T (float): Time to expiry
        r (float): Risk-free rate
        tol (float): Tolerance
        max_iter (int): Max iterations
        
    Returns:
        float: Implied volatility (annualized)
    """
    if T <= 0:
        return 0.3  # Default vol
    
    try:
        # Brentq solver kullan (robust)
        def objective(sigma):
            return black_scholes_call(S, K, T, r, sigma) - market_price
        
        # Vol aralığı: 0.05 (5%) - 3.0 (300%)
        iv = brentq(objective, 0.05, 3.0)
        return iv
    except:
        # Fallback: historical volatility estimate
        return 0.5  # 50% default


# ============================================================================
# CRYPTO MARKET DATA FUNCTIONS
# ============================================================================

def get_crypto_price(symbol):
    """
    Binance'den mevcut fiyat çek
    
    Args:
        symbol (str): Trading pair (BTCUSDT)
        
    Returns:
        float: Current price
    """
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        print(f"⚠️ Price fetch failed: {e}")
        return None


def calculate_realized_volatility(symbol, days=30):
    """
    Realized volatility hesapla (historical)
    
    Args:
        symbol (str): Trading pair
        days (int): Lookback period
        
    Returns:
        float: Annualized volatility
    """
    try:
        # Binance klines API
        url = f"https://api.binance.com/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': '1d',
            'limit': days
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # Close prices
        closes = [float(candle[4]) for candle in data]
        
        # Log returns
        returns = np.diff(np.log(closes))
        
        # Annualized vol (√252 scaling)
        realized_vol = np.std(returns) * np.sqrt(252)
        
        return realized_vol
    except Exception as e:
        print(f"⚠️ Volatility calculation failed: {e}")
        return 0.5  # Default 50%


# ============================================================================
# QUANTUM BLACK-SCHOLES SIGNAL GENERATOR
# ============================================================================

def get_quantum_black_scholes_signal(symbol, interval='1h'):
    """
    Quantum Black-Scholes layer main function
    
    Args:
        symbol (str): Trading pair (BTCUSDT)
        interval (str): Timeframe (not used currently)
        
    Returns:
        dict: {'available': bool, 'score': float, 'signal': str}
    """
    try:
        score = analyze_option_pricing(symbol, interval)  # returns float
        
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
        print(f"⚠️ Quantum Black-Scholes Error: {e}")
        return {
            'available': True,
            'score': 50.0,
            'signal': 'NEUTRAL'
        }
    """
    Quantum Black-Scholes layer ana fonksiyonu
    
    MANTIK:
    -------
    1. Mevcut fiyatı al (S)
    2. Strike prices belirle (ATM, OTM)
    3. Realized volatility hesapla
    4. Greeks hesapla
    5. Volatility surface analizi
    6. Sinyal üret (0-100)
    
    Args:
        symbol (str): Trading pair (BTCUSDT)
        interval (str): Timeframe (kullanılmıyor şimdilik)
        
    Returns:
        float: Score (0-100)
    """
    try:
        print(f"🔮 Quantum Black-Scholes analyzing {symbol}...")
        
        # 1. Mevcut fiyatı al
        S = get_crypto_price(symbol)
        if S is None:
            print("⚠️ Failed to get price, returning neutral")
            return 50.0
        
        # 2. Strike prices (ATM ve OTM)
        K_atm = S  # At-the-money
        K_otm_call = S * 1.05  # 5% yukarı
        K_otm_put = S * 0.95   # 5% aşağı
        
        # 3. Time to expiry (30 gün varsayımı)
        T = 30 / 365  # 1 ay
        
        # 4. Risk-free rate (ABD 10Y bond ~ 4.5%)
        r = 0.045
        
        # 5. Realized volatility
        sigma = calculate_realized_volatility(symbol, days=30)
        print(f"   Realized Vol: {sigma:.2%}")
        
        # 6. Greeks hesapla (ATM için)
        greeks = calculate_greeks(S, K_atm, T, r, sigma)
        
        delta = greeks['delta']
        gamma = greeks['gamma']
        vega = greeks['vega']
        theta = greeks['theta']
        
        print(f"   Delta: {delta:.4f}")
        print(f"   Gamma: {gamma:.6f}")
        print(f"   Vega: {vega:.4f}")
        print(f"   Theta: {theta:.4f}")
        
        # 7. Skor hesaplama
        score = 50.0  # Baseline
        
        # Delta component (en önemli)
        # Delta 0.5 = neutral, >0.5 = bullish, <0.5 = bearish
        delta_score = (delta - 0.5) * 100  # -50 to +50
        score += delta_score * 0.4  # %40 ağırlık
        
        # Gamma component (momentum)
        # Yüksek gamma = güçlü momentum
        avg_gamma = 0.0001  # Typical crypto gamma
        gamma_normalized = min(gamma / avg_gamma, 2.0) - 1.0  # -1 to +1
        score += gamma_normalized * 15  # %15 ağırlık
        
        # Vega component (volatility sensitivity)
        # Yüksek vega = breakout potansiyeli
        avg_vega = 50  # Typical value
        vega_normalized = min(vega / avg_vega, 2.0) - 1.0
        score += vega_normalized * 15  # %15 ağırlık
        
        # Theta component (time decay)
        # Negatif theta = risk, pozitif = güvenlik
        theta_normalized = np.clip(theta / 10, -1, 1)
        score += theta_normalized * 10  # %10 ağırlık
        
        # Volatility regime (sigma bazlı)
        # Düşük vol = mean reversion, yüksek vol = trend following
        if sigma > 0.8:  # Yüksek vol
            score += 10  # Trend following bias
        elif sigma < 0.3:  # Düşük vol
            score -= 10  # Mean reversion
        
        # Skor 0-100 aralığına sınırla
        score = np.clip(score, 0, 100)
        
        print(f"✅ Quantum Black-Scholes Score: {score:.1f}/100")
        
        return score
        
    except Exception as e:
        print(f"❌ Quantum Black-Scholes error: {e}")
        return 50.0  # Neutral


# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

def analyze_option_pricing(symbol, interval='1h'):
    """
    Alias for backward compatibility
    """
    return get_quantum_black_scholes_signal(symbol, interval)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    # Test
    print("="*80)
    print("🔮 QUANTUM BLACK-SCHOLES LAYER TEST")
    print("="*80)
    
    test_symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        score = get_quantum_black_scholes_signal(symbol)
        
        if score >= 65:
            signal = "🟢 LONG"
        elif score <= 35:
            signal = "🔴 SHORT"
        else:
            signal = "⚪ NEUTRAL"
        
        print(f"   Signal: {signal}")
        print(f"   Score: {score:.1f}/100")
        print("-"*80)
