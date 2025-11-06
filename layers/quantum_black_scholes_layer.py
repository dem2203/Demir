import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
import requests
from datetime import datetime

def black_scholes_call(S, K, T, r, sigma):
    if T <= 0 or sigma <= 0:
        return max(S - K, 0)
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def calculate_greeks(S, K, T, r, sigma):
    if T <= 0 or sigma <= 0:
        return {'delta': 0.5, 'gamma': 0.0, 'vega': 0.0, 'theta': 0.0}
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    delta = norm.cdf(d1)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100
    theta = -(S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    return {'delta': delta, 'gamma': gamma, 'vega': vega, 'theta': theta}


def calculate_realized_volatility(symbol, days=30):
    debug = {}
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {'symbol': symbol, 'interval': '1d', 'limit': days}
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            debug['http_error'] = f"HTTP status {resp.status_code}"
            return 0.5, debug
        data = resp.json()
        closes = [float(c[4]) for c in data]
        returns = np.diff(np.log(closes))
        vol = np.std(returns) * np.sqrt(252)
        return vol, debug
    except Exception as e:
        debug['exception'] = str(e)
        return 0.5, debug


def get_crypto_price(symbol):
    debug = {}
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            debug['http_error'] = f"HTTP status {resp.status_code}"
            return None, debug
        price = float(resp.json().get('price', 0))
        if price == 0:
            debug['error'] = "Price is zero"
        return price, debug
    except Exception as e:
        debug['exception'] = str(e)
        return None, debug


def get_quantum_black_scholes_signal(symbol, interval='1h'):
    debug = {}
    try:
        print(f"🔮 Quantum Black-Scholes analyzing {symbol}...")
        S, debug_price = get_crypto_price(symbol)
        debug.update(debug_price)
        if S is None:
            debug['error_message'] = "Failed to fetch price"
            return {'available': False, 'score': 50.0, 'signal': 'NEUTRAL', 'data_debug': debug}

        K_atm = S
        T = 30 / 365
        r = 0.045

        sigma, debug_vol = calculate_realized_volatility(symbol, days=30)
        debug.update(debug_vol)
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

        score = max(0, min(100, score))
        print(f"✅ Quantum Black-Scholes Score: {score:.1f}/100")

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
            'data_debug': debug
        }
    except Exception as e:
        print(f"❌ Quantum Black-Scholes error: {e}")
        return {
            'available': False,
            'score': 50.0,
            'signal': 'NEUTRAL',
            'error_message': str(e),
            'data_debug': debug
        }


if __name__ == "__main__":
    print("Testing quantum_black_scholes_layer.py")
    test_symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
    for symbol in test_symbols:
        result = get_quantum_black_scholes_signal(symbol)
        print(f"{symbol}: Score={result['score']}, Signal={result['signal']}")
        if 'data_debug' in result:
            print("Debug info:", result['data_debug'])
