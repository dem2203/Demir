"""
ğŸ”® MARKET REGIME ANALYZER v1.0
==============================

Date: 7 KasÄ±m 2025, 14:52 CET
Phase: 8.1 - Adaptive Weighting System

AMAÃ‡:
-----
VIX + Volatility kombinasyonu ile market rejimini tespit et
ve layer weight'lerini dinamik olarak adjust et.

Regimler:
- LOW: Calm market (VIX < 12)
- NORMAL: Neutral (12 <= VIX < 18)
- HIGH: Elevated (18 <= VIX < 25)
- EXTREME: Crisis (VIX >= 25)
"""

import requests
import numpy as np

def get_vix():
    """Get real VIX from Yahoo/API"""
    try:
        # CBOE VIX endpoint (alternative)
        url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=%5EVIX"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        vix = data['quoteResponse']['result'][0]['regularMarketPrice']
        return vix
    except:
        return None

def get_market_volatility(symbol='BTCUSDT'):
    """Get actual market volatility"""
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {'symbol': symbol, 'interval': '1h', 'limit': 24}
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        closes = np.array([float(k[4]) for k in data])
        returns = np.diff(np.log(closes))
        volatility = np.std(returns) * np.sqrt(252)  # Annualized
        return volatility
    except:
        return 0.5

def detect_market_regime():
    """
    Main function: detect regime from VIX and volatility
    
    Returns:
        dict: {
            'regime': 'LOW'|'NORMAL'|'HIGH'|'EXTREME',
            'vix': float,
            'volatility': float,
            'confidence': float (0-1)
        }
    """
    try:
        vix = get_vix()
        vol = get_market_volatility()
        
        # If VIX not available, use volatility
        if vix is None:
            vix = vol * 100  # Rough proxy
        
        # Regime detection
        if vix >= 25:
            regime = 'EXTREME'
            confidence = 0.95
        elif vix >= 18:
            regime = 'HIGH'
            confidence = 0.90
        elif vix >= 12:
            regime = 'NORMAL'
            confidence = 0.85
        else:
            regime = 'LOW'
            confidence = 0.80
        
        return {
            'available': True,
            'regime': regime,
            'vix': round(vix, 2) if vix else None,
            'volatility': round(vol, 4),
            'confidence': confidence
        }
    except Exception as e:
        return {
            'available': False,
            'regime': 'NORMAL',
            'vix': None,
            'volatility': None,
            'confidence': 0.5,
            'error': str(e)
        }

def get_regime_weights():
    """
    Get layer weights based on market regime
    
    Returns adaptive weights for each layer
    Higher score layers get MORE weight in certain regimes
    """
    regime_info = detect_market_regime()
    regime = regime_info['regime']
    
    # Default weights (equal)
    base_weights = {
        'strategy': 0.067,
        'kelly': 0.067,
        'macro': 0.067,
        'gold': 0.067,
        'cross_asset': 0.067,
        'vix': 0.067,
        'monte_carlo': 0.067,
        'news': 0.067,
        'trad_markets': 0.067,
        'black_scholes': 0.067,
        'kalman': 0.067,
        'fractal': 0.067,
        'fourier': 0.067,
        'copula': 0.067,
        'rates': 0.067,
    }
    
    # Regime-based adjustments
    if regime == 'EXTREME':
        # In crisis: favor volatility/risk layers
        adjustments = {
            'vix': 1.5,           # +50%
            'kelly': 0.5,         # -50%
            'kalman': 1.3,        # +30%
            'copula': 1.2,        # +20%
            'monte_carlo': 0.7,   # -30%
        }
    elif regime == 'HIGH':
        # High vol: favor vol-sensitive layers
        adjustments = {
            'kalman': 1.2,
            'vix': 1.15,
            'kelly': 0.8,
            'monte_carlo': 0.9,
        }
    elif regime == 'NORMAL':
        # Normal: all equal (or slight tweaks)
        adjustments = {
            'cross_asset': 1.1,   # Cross-asset matters
            'black_scholes': 0.95,
        }
    else:  # LOW
        # Low vol: favor trend/momentum layers
        adjustments = {
            'fourier': 1.2,
            'fractal': 1.15,
            'kalman': 1.1,
            'vix': 0.5,
        }
    
    # Apply adjustments
    adjusted_weights = base_weights.copy()
    for layer, factor in adjustments.items():
        if layer in adjusted_weights:
            adjusted_weights[layer] *= factor
    
    # Normalize to sum = 1.0
    total = sum(adjusted_weights.values())
    normalized = {k: v/total for k, v in adjusted_weights.items()}
    
    return {
        'weights': normalized,
        'regime': regime,
        'regime_info': regime_info
    }


if __name__ == "__main__":
    print("ğŸ”® MARKET REGIME ANALYZER TEST")
    print("="*50)
    
    regime_data = detect_market_regime()
    print(f"\nRegime: {regime_data['regime']}")
    print(f"VIX: {regime_data['vix']}")
    print(f"Volatility: {regime_data['volatility']}")
    
    weights = get_regime_weights()
    print(f"\nTop 5 Weighted Layers:")
    sorted_weights = sorted(weights['weights'].items(), key=lambda x: x[1], reverse=True)
    for layer, weight in sorted_weights[:5]:
        print(f"  {layer}: {weight:.3f} ({weight*100:.1f}%)")
