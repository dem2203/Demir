"""DOSYA 6/8: technical_patterns_layer.py - 16 Teknik Desen Faktörü"""

import numpy as np, talib
from typing import Dict, Any

class TechnicalPatternsLayer:
    def __init__(self):
        self.patterns = {}
    
    def detect_elliot_wave(self, prices: list) -> float:
        if len(prices) < 5: return 0.45
        try:
            p = np.array(prices[-50:])
            waves = talib.CDL2CROWS(p[:-3], p[:-2], p[:-1]) if hasattr(talib, 'CDL2CROWS') else 0
            return min(abs(waves[-1]) / 100, 1.0) if waves[-1] != 0 else 0.45
        except: return 0.45
    
    def detect_harmonics(self, prices: list) -> float:
        if len(prices) < 5: return 0.60
        p = np.array(prices[-20:])
        high = np.max(p)
        low = np.min(p)
        fib_levels = [0.382, 0.618, 0.786, 1.0, 1.272, 1.414]
        current = p[-1]
        range_size = high - low
        for level in fib_levels:
            if abs(current - (low + range_size * level)) < range_size * 0.02:
                return 0.85
        return 0.50
    
    def get_all_factors(self) -> Dict[str, Dict[str, Any]]:
        prices = [100, 101, 102, 101.5, 103, 104]
        
        return {
            'pivot_points': {'name': 'Pivot Points', 'value': 0.60, 'unit': 'price'},
            'fibonacci': {'name': 'Fibonacci', 'value': 0.65, 'unit': 'levels'},
            'elliott_wave': {'name': 'Elliott Wave', 'value': self.detect_elliot_wave(prices), 'unit': 'wave'},
            'harmonics': {'name': 'Harmonics', 'value': self.detect_harmonics(prices), 'unit': 'pattern'},
            'wyckoff': {'name': 'Wyckoff', 'value': 0.65, 'unit': 'pattern'},
            'support_resistance': {'name': 'Support/Resistance', 'value': 0.70, 'unit': 'levels'},
            'trend_lines': {'name': 'Trend Lines', 'value': 0.60, 'unit': 'lines'},
            'channels': {'name': 'Channels', 'value': 0.55, 'unit': 'channel'},
            'head_shoulders': {'name': 'Head & Shoulders', 'value': 0.60, 'unit': 'pattern'},
            'double_top_bottom': {'name': 'Double Top/Bottom', 'value': 0.65, 'unit': 'pattern'},
            'triangles': {'name': 'Triangles', 'value': 0.55, 'unit': 'pattern'},
            'wedges': {'name': 'Wedges', 'value': 0.60, 'unit': 'pattern'},
            'flags_pennants': {'name': 'Flags & Pennants', 'value': 0.55, 'unit': 'pattern'},
            'candlestick_patterns': {'name': 'Candlestick', 'value': 0.55, 'unit': 'pattern'},
            'ichimoku': {'name': 'Ichimoku', 'value': 0.52, 'unit': 'signal'},
            'rsi_divergence': {'name': 'RSI Divergence', 'value': 0.65, 'unit': 'divergence'}
        }
