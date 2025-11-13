"""
MOVING AVERAGE LAYER - v2.0
SMA/EMA with trend detection
"""

from utils.base_layer import BaseLayer
from datetime import datetime
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class MovingAverageLayer(BaseLayer):
    """Moving Average Layer"""
    
    def __init__(self, fast=20, slow=50):
        """Initialize
        
        Args:
            fast: Fast MA period (default 20)
            slow: Slow MA period (default 50)
        """
        super().__init__('MovingAverage_Layer')
        self.fast = fast
        self.slow = slow
    
    async def get_signal(self, prices):
        """Get MA signal"""
        return await self.execute_with_retry(
            self._calculate_ma,
            prices
        )
    
    async def _calculate_ma(self, prices):
        """Calculate Moving Averages"""
        if not prices or len(prices) < self.slow:
            raise ValueError("Insufficient data")
        
        try:
            series = pd.Series(prices)
            
            # Calculate MAs
            fast_ma = series.ewm(span=self.fast).mean()
            slow_ma = series.ewm(span=self.slow).mean()
            
            fast_current = fast_ma.iloc[-1]
            slow_current = slow_ma.iloc[-1]
            current_price = prices[-1]
            
            # Validate
            if np.isnan(fast_current) or np.isnan(slow_current):
                raise ValueError("Invalid MA values")
            
            # Signal
            if fast_current > slow_current and current_price > fast_current:
                signal = 'LONG'
                score = 75.0
            elif fast_current < slow_current and current_price < fast_current:
                signal = 'SHORT'
                score = 25.0
            else:
                signal = 'NEUTRAL'
                score = 50.0
            
            return {
                'signal': signal,
                'score': score,
                'fast_ma': float(fast_current),
                'slow_ma': float(slow_current),
                'current_price': float(current_price),
                'timestamp': datetime.now().isoformat(),
                'valid': True
            }
        
        except Exception as e:
            logger.error(f"MA error: {e}")
            raise ValueError(f"MA error: {e}")
