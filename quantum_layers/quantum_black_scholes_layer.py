"""
🔮 QUANTUM BLACK-SCHOLES LAYER v16.5
====================================

Date: 7 Kasım 2025, 14:45 CET
Phase: 7+8 - Quantum Trading AI - COMPATIBLE v16.4

AMAÇ:
-----
Black-Scholes option pricing model ile REAL market volatility
ve implied price movements kullanarak option value hesapla.

MATHEMATIK:
-----------
C = S*N(d1) - K*e^(-rT)*N(d2)
d1 = [ln(S/K) + (r + σ²/2)*T] / (σ*√T)
d2 = d1 - σ*√T
"""

import numpy as np
import requests
from scipy.stats import norm
from datetime import datetime

def get_crypto_price(symbol):
    """Real price from Binance"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return None
        return float(resp.json()['price'])
    except:
        return None

def calculate_realized_volatility(symbol, days=30):
    """Historical volatility from real market data"""
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {'symbol': symbol, 'interval': '1d', 'limit': days}
        resp = requests.get(url, params=params, timeout=10)
        
        if resp.status_code != 200:
            return 0.5
        
        data = resp.json()
        closes = np.array([float(c[4]) for c in data])
        returns = np.diff(np.log(closes))
        vol = np.std(returns) * np.sqrt(252)
        
        return max(vol, 0.01)
    except:
        return 0.5

def black_scholes_call(S, K, T, r, sigma):
    """Black-Scholes formula for call option"""
    if T <= 0 or sigma <= 0:
        return max(S - K, 0)
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

def calculate_greeks(S, K, T, r, sigma):
    """Calculate option Greeks"""
    if T <= 0 or sigma <= 0:
        return {'delta': 0.5, 'gamma': 0.0, 'vega': 0.0, 'theta': 0.0}
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    delta = norm.cdf(d1)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100
    theta = -(S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    
    return {'delta': delta, 'gamma': gamma, 'vega': vega, 'theta': theta}

def calculate_option_price(symbol='BTCUSDT'):
    """
    MAIN FUNCTION - Compatible with ai_brain.py
    Black-Scholes with REAL market data
    
    Args:
        symbol (str): Trading pair
        
    Returns:
        dict: {'score': float, 'signal': str, 'available': bool}
    """
    debug = {}
    
    try:
        # Get REAL price
        S = get_crypto_price(symbol)
        if S is None:
            debug['error'] = "Price fetch failed"
            return {
                'available': False,
                'score': 50.0,
                'signal': 'NEUTRAL',
                'data_debug': debug
            }
        
        # Get REAL volatility
        sigma = calculate_realized_volatility(symbol, days=30)
        
        # Parameters
        K_atm = S
        T = 30 / 365
        r = 0.045
        
        # Calculate
        call_price = black_scholes_call(S, K_atm, T, r, sigma)
        greeks = calculate_greeks(S, K_atm, T, r, sigma)
        
        # Score
        score = 50.0
        delta = greeks['delta']
        gamma = greeks['gamma']
        vega = greeks['vega']
        
        # Delta component
        delta_score = (delta - 0.5) * 100
        score += delta_score * 0.4
        
        # Gamma component
        avg_gamma = 0.0001
        gamma_normalized = min(gamma / avg_gamma, 2.0) - 1.0
        score += gamma_normalized * 15
        
        # Vega component
        avg_vega = 50
        vega_normalized = min(vega / avg_vega, 2.0) - 1.0
        score += vega_normalized * 15
        
        # Volatility regime
        if sigma > 0.8:
            score += 10
        elif sigma < 0.3:
            score -= 10
        
        score = max(0, min(100, score))
        
        signal = "LONG" if score >= 65 else ("SHORT" if score <= 35 else "NEUTRAL")
        
        return {
            'available': True,
            'score': round(score, 2),
            'signal': signal,
            'data_debug': debug
        }
        
    except Exception as e:
        debug['exception'] = str(e)
        return {
            'available': False,
            'score': 50.0,
            'signal': 'NEUTRAL',
            'error': str(e),
            'data_debug': debug
        }
