"""
STOCHASTIC LAYER - v2.0
Stochastic Oscillator with BaseLayer
"""

from utils.base_layer import BaseLayer
from datetime import datetime
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class StochasticLayer(BaseLayer):
    """Stochastic Oscillator Layer"""
    
    def __init__(self, period=14, k_period=3, d_period=3):
        """Initialize"""
        super().__init__('Stochastic_Layer')
        self.period = period
        self.k_period = k_period
        self.d_period = d_period
    
    async def get_signal(self, prices):
        """Get stochastic signal"""
        return await self.execute_with_retry(
            self._calculate_stochastic,
            prices
        )
    
    async def _calculate_stochastic(self, prices):
        """Calculate Stochastic Oscillator"""
        if not prices or len(prices) < self.period + self.d_period:
            raise ValueError("Insufficient data")
        
        try:
            # Get highs and lows (simple: use price ranges)
            series = pd.Series(prices)
            lowest_low = series.rolling(self.period).min()
            highest_high = series.rolling(self.period).max()
            
            # %K calculation
            k_line = 100 * (prices[-1] - lowest_low.iloc[-1]) / \
                     (highest_high.iloc[-1] - lowest_low.iloc[-1])
            
            # %D calculation (SMA of %K)
            k_values = 100 * (series - lowest_low) / (highest_high - lowest_low)
            d_line = k_values.ewm(span=self.d_period).mean().iloc[-1]
            
            # Validate
            if np.isnan(k_line) or np.isnan(d_line):
                raise ValueError("Invalid stochastic values")
            
            # Signal
            if k_line < 20:
                signal = 'OVERSOLD'
                score = 75.0
            elif k_line > 80:
                signal = 'OVERBOUGHT'
                score = 25.0
            else:
                signal = 'NEUTRAL'
                score = 50.0
            
            return {
                'signal': signal,
                'score': score,
                'k_line': float(k_line),
                'd_line': float(d_line),
                'timestamp': datetime.now().isoformat(),
                'valid': True
            }
        
        except Exception as e:
            logger.error(f"Stochastic error: {e}")
            raise ValueError(f"Stochastic error: {e}")
