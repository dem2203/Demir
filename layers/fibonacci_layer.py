"""
FIBONACCI LAYER - v2.0
Fibonacci retracement levels
"""

from utils.base_layer import BaseLayer
from datetime import datetime
import numpy as np
import logging

logger = logging.getLogger(__name__)


class FibonacciLayer(BaseLayer):
    """Fibonacci Retracement Layer"""
    
    def __init__(self, lookback=100):
        """Initialize"""
        super().__init__('Fibonacci_Layer')
        self.lookback = lookback
    
    async def get_signal(self, prices):
        """Get Fibonacci levels"""
        return await self.execute_with_retry(
            self._calculate_fibonacci,
            prices
        )
    
    async def _calculate_fibonacci(self, prices):
        """Calculate Fibonacci levels"""
        if not prices or len(prices) < self.lookback:
            raise ValueError("Insufficient data")
        
        try:
            lookback_prices = prices[-self.lookback:]
            high = max(lookback_prices)
            low = min(lookback_prices)
            
            diff = high - low
            
            # Fibonacci levels
            fib_levels = {
                '0.0': low,
                '0.236': low + diff * 0.236,
                '0.382': low + diff * 0.382,
                '0.5': low + diff * 0.5,
                '0.618': low + diff * 0.618,
                '0.786': low + diff * 0.786,
                '1.0': high,
            }
            
            current_price = prices[-1]
            
            # Find nearest level
            nearest_level = min(fib_levels.items(), 
                              key=lambda x: abs(x - current_price))
            
            # Signal based on proximity
            if current_price < low + diff * 0.382:
                signal = 'SUPPORT'
                score = 70.0
            elif current_price > high - diff * 0.382:
                signal = 'RESISTANCE'
                score = 30.0
            else:
                signal = 'NEUTRAL'
                score = 50.0
            
            return {
                'signal': signal,
                'score': score,
                'current_price': float(current_price),
                'fib_levels': {k: float(v) for k, v in fib_levels.items()},
                'nearest_level': nearest_level,
                'timestamp': datetime.now().isoformat(),
                'valid': True
            }
        
        except Exception as e:
            logger.error(f"Fibonacci error: {e}")
            raise ValueError(f"Fibonacci error: {e}")
