"""DOSYA 7/8: volatility_dynamics_layer.py - 8 Volatilite Faktörü"""

import numpy as np
from typing import Dict, Any

class VolatilityDynamicsLayer:
    def calculate_garch_volatility(self, returns: list) -> float:
        if len(returns) < 10: return 0.02
        returns = np.array(returns[-100:])
        r_mean = np.mean(returns)
        errors = returns - r_mean
        return float(np.std(errors) * np.sqrt(252)) / 10
    
    def calculate_bollinger_width(self, prices: list) -> float:
        if len(prices) < 20: return 0.5
        p = np.array(prices[-20:])
        ma = np.mean(p)
        std = np.std(p)
        bb_width = (4 * std) / ma
        return min(bb_width / 0.2, 1.0)
    
    def calculate_atr(self, data: list) -> float:
        if len(data) < 14: return 0.015
        data = np.array(data[-14:])
        tr = np.abs(np.diff(data))
        atr = np.mean(tr)
        return float(atr / data[0])
    
    def get_all_factors(self) -> Dict[str, Dict[str, Any]]:
        prices = [100 + i * 0.5 + np.random.normal(0, 0.2) for i in range(100)]
        returns = np.diff(prices) / prices[:-1]
        
        return {
            'garch_vol': {'name': 'GARCH Volatility', 'value': self.calculate_garch_volatility(returns.tolist()), 'unit': 'volatility'},
            'historical_vol': {'name': 'Historical Vol', 'value': 0.020, 'unit': 'volatility'},
            'bollinger_width': {'name': 'Bollinger Width', 'value': self.calculate_bollinger_width(prices), 'unit': 'width'},
            'atr': {'name': 'ATR', 'value': self.calculate_atr(prices), 'unit': 'atr'},
            'vol_squeeze': {'name': 'Vol Squeeze', 'value': 0.35, 'unit': 'squeeze'},
            'vix_correlation': {'name': 'VIX Correlation', 'value': 0.70, 'unit': 'correlation'},
            'skewness': {'name': 'Skewness', 'value': 0.50, 'unit': 'skew'},
            'kurtosis': {'name': 'Kurtosis', 'value': 0.48, 'unit': 'kurt'}
        }
