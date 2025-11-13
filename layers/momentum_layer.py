"""
MOMENTUM LAYER - v2.0
Rate of price change
"""

from utils.base_layer import BaseLayer
from datetime import datetime
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class MomentumLayer(BaseLayer):
    """Momentum Layer"""
    
    def __init__(self, period=12):
        """Initialize"""
        super().__init__('Momentum_Layer')
        self.period = period
    
    async def get_signal(self, prices):
        """Get momentum signal"""
        return await self.execute_with_retry(
            self._calculate_momentum,
            prices
        )
    
    async def _calculate_momentum(self, prices):
        """Calculate Momentum"""
        if not prices or len(prices) < self.period:
            raise ValueError("Insufficient data")
        
        try:
            series = pd.Series(prices)
            momentum = series.diff(self.period)
            
            current_momentum = momentum.iloc[-1]
            avg_momentum = momentum.mean()
            
            # Signal
            if current_momentum > avg_momentum and current_momentum > 0:
                signal = 'LONG'
                score = 70.0
            elif current_momentum < avg_momentum and current_momentum < 0:
                signal = 'SHORT'
                score = 30.0
            else:
                signal = 'NEUTRAL'
                score = 50.0
            
            return {
                'signal': signal,
                'score': score,
                'momentum': float(current_momentum),
                'avg_momentum': float(avg_momentum),
                'timestamp': datetime.now().isoformat(),
                'valid': True
            }
        
        except Exception as e:
            logger.error(f"Momentum error: {e}")
            raise ValueError(f"Momentum error: {e}")
