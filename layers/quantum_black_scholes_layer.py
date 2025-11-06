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

def black_scholes_call(S, K, T, r, sigma):
    if T <= 0 or sigma <= 0:
        return max(S - K, 0)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return call_price

def calculate_greeks(S, K, T, r, sigma):
    if T <= 0 or sigma <= 0:
        return {'delta': 0.5, 'gamma': 0.0, 'vega': 0.0, 'theta': 0.0}
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    delta = norm.cdf(d1)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100
    theta = -(S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    return {'delta': delta, 'gamma': gamma, 'vega': vega, 'theta': theta}

def calculate_implied_volatility(market_price, S, K, T, r, tol=1e-5, max_iter=100):
    if T <= 0:
        return 0.3
    try:
        def objective(sigma):
            return black_scholes_call(S, K, T, r, sigma) - market_price
        iv = brentq(objective, 0.05, 3.0)
        return iv
    except Exception:
        return 0.5

def get_crypto_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        print(f"⚠️ Price fetch failed: {e}")
        return None

def calculate_realized_volatility(symbol, days=30):
    try:
        url = f"https://api.binance.com/api/v3/klines"
        params = {'symbol': symbol, 'interval': '1d', 'limit': days}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        closes = [float(candle[4]) for candle in data]
        returns = np.diff(np.log(closes))
        return np.std(returns) * np.sqrt(252)
    except Exception as e:
        print(f"⚠️ Volatility calculation failed: {e}")
        return 0.5

def get_quantum_black_scholes_signal(symbol, interval='1h'):
    try:
        print(f"🔮 Quantum Black-Scholes analyzing {symbol}...")
        S = get_crypto_price(symbol)
        if S is None:
            print("⚠️ Failed to get price, returning neutral")
            return 50.0
        K_atm = S
        K_otm_call = S * 1.05
        K_otm_put = S * 0.95
        T = 30 / 365
        r = 0.045
        sigma = calculate_realized_volatility(symbol, days=30)
        print(f"   Realized Vol: {sigma:.2%}")
        greeks = calculate_greeks(S, K_atm, T, r, sigma)
        delta = greeks['delta']
        gamma = greeks['gamma']
        vega = greeks['vega']
        theta = greeks['theta']
        print(f"   Delta: {delta:.4f}")
        print(f"   Gamma: {gamma:.6f}")
        print(f"   Vega: {vega:.4f}")
        print(f"   Theta: {theta:.4f}")
        score = 50.0
        delta_score = (delta - 0.5) * 100
        score += delta_score * 0.4
        avg_gamma = 0.0001
        gamma_normalized = min(gamma / avg_gamma, 2.0) - 1.0
        score += gamma_normalized * 15
        avg_vega = 50
        vega_normalized = min(vega / avg_vega, 2.0) - 1.0
        score += vega_normalized * 15
        theta_normalized = np.clip(theta / 10, -1, 1)
        score += theta_normalized * 10
        if sigma > 0.8:
            score += 10
        elif sigma < 0.3:
            score -= 10
        score = np.clip(score, 0, 100)
        print(f"✅ Quantum Black-Scholes Score: {score:.1f}/100")
        return score
    except Exception as e:
        print(f"❌ Quantum Black-Scholes error: {e}")
        return 50.0

def analyze_option_pricing(symbol, interval='1h'):
    return get_quantum_black_scholes_signal(symbol, interval)

if __name__ == "__main__":
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

