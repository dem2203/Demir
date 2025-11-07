"""
🔮 QUANTUM BLACK-SCHOLES LAYER v16.5
====================================

Date: 7 Kasım 2025, 14:26 CET
Phase: 7+8 - Quantum Trading AI

AMAÇ:
-----
Black-Scholes option pricing model ile REAL market volatility
ve implied price movements kullanarak option value hesapla.

MATHEMATIK:
-----------
C = S*N(d1) - K*e^(-rT)*N(d2)
d1 = [ln(S/K) + (r + σ²/2)*T] / (σ*√T)
d2 = d1 - σ*√T

N(x) = Cumulative standard normal distribution
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

def get_quantum_black_scholes_signal(symbol, interval='1h'):
    """
    Quantum Black-Scholes ana fonksiyonu
    
    MANTIK:
    -------
    1. Spot price from Binance (REAL)
    2. Historical volatility (REAL)
    3. Black-Scholes formula apply
    4. Greeks hesapla
    5. Score generate (0-100)
    
    Args:
        symbol (str): Trading pair (BTCUSDT, ETHUSDT)
        interval (str): Timeframe
        
    Returns:
        dict: {'available': bool, 'score': float, 'signal': str, ...}
    """
    debug = {}
    
    try:
        print(f"🔮 Quantum Black-Scholes analyzing {symbol}...")
        
        # 1. Get REAL price
        S = get_crypto_price(symbol)
        if S is None:
            print(f"❌ Price fetch failed for {symbol}")
            debug['error'] = "Price fetch failed"
            return {
                'available': False,
                'score': 50.0,
                'signal': 'NEUTRAL',
                'data_debug': debug
            }
        
        print(f" 💰 Spot Price: ${S:.2f}")
        
        # 2. Get REAL volatility
        sigma = calculate_realized_volatility(symbol, days=30)
        print(f" 📊 Realized Volatility: {sigma:.2%}")
        
        # 3. Black-Scholes parameters
        K_atm = S  # At-the-money
        T = 30 / 365  # 30 days to expiry
        r = 0.045  # Risk-free rate
        
        # 4. Calculate call option price
        call_price = black_scholes_call(S, K_atm, T, r, sigma)
        print(f" 📈 Call Option Price: ${call_price:.4f}")
        
        # 5. Greeks
        greeks = calculate_greeks(S, K_atm, T, r, sigma)
        delta = greeks['delta']
        gamma = greeks['gamma']
        vega = greeks['vega']
        theta = greeks['theta']
        
        print(f" Δ (Delta): {delta:.4f}")
        print(f" Γ (Gamma): {gamma:.6f}")
        print(f" ν (Vega): {vega:.4f}")
        print(f" Θ (Theta): {theta:.4f}")
        
        # 6. Score calculation
        score = 50.0
        
        # Delta component (bullish if > 0.5)
        delta_score = (delta - 0.5) * 100
        score += delta_score * 0.4
        
        # Gamma component (convexity)
        avg_gamma = 0.0001
        gamma_normalized = min(gamma / avg_gamma, 2.0) - 1.0
        score += gamma_normalized * 15
        
        # Vega component (volatility sensitivity)
        avg_vega = 50
        vega_normalized = min(vega / avg_vega, 2.0) - 1.0
        score += vega_normalized * 15
        
        # Theta component (time decay)
        theta_normalized = np.clip(theta / 10, -1, 1)
        score += theta_normalized * 10
        
        # Volatility regime
        if sigma > 0.8:
            score += 10
            print(f" ⚠️ High volatility regime (+10)")
        elif sigma < 0.3:
            score -= 10
            print(f" ✅ Low volatility regime (-10)")
        
        score = max(0, min(100, score))
        
        print(f"✅ Black-Scholes Score: {score:.1f}/100")
        
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
            'delta': round(delta, 4),
            'gamma': round(gamma, 6),
            'vega': round(vega, 4),
            'theta': round(theta, 4),
            'volatility': round(sigma, 4),
            'timestamp': datetime.now().isoformat(),
            'data_debug': debug
        }
        
    except Exception as e:
        print(f"❌ Quantum Black-Scholes error: {e}")
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
    print("🔮 QUANTUM BLACK-SCHOLES LAYER TEST")
    print("="*80)
    
    test_symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        result = get_quantum_black_scholes_signal(symbol)
        print(f" Score: {result['score']}, Signal: {result['signal']}")
        if 'data_debug' in result:
            print(f" Debug: {result['data_debug']}\n")
