"""
ATR LAYER - v1.0
Average True Range for volatility
"""

from utils.base_layer import BaseLayer
from datetime import datetime
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ATRLayer(BaseLayer):
    """Average True Range Layer"""
    
    def __init__(self, period=14):
        """Initialize"""
        super().__init__('ATR_Layer')
        self.period = period
    
    async def get_signal(self, high_prices, low_prices, close_prices):
        """Get ATR signal"""
        return await self.execute_with_retry(
            self._calculate_atr,
            high_prices,
            low_prices,
            close_prices
        )
    
    async def _calculate_atr(self, high_prices, low_prices, close_prices):
        """Calculate ATR"""
        if not close_prices or len(close_prices) < self.period:
            raise ValueError("Insufficient data")
        
        try:
            # True Range calculation
            tr_values = []
            for i in range(1, len(close_prices)):
                tr = max(
                    high_prices[i] - low_prices[i],
                    abs(high_prices[i] - close_prices[i-1]),
                    abs(low_prices[i] - close_prices[i-1])
                )
                tr_values.append(tr)
            
            # ATR
            atr_series = pd.Series(tr_values).rolling(self.period).mean()
            atr = atr_series.iloc[-1]
            
            # Volatility level
            avg_atr = atr_series.mean()
            volatility_ratio = atr / avg_atr if avg_atr > 0 else 1.0
            
            # Signal
            if volatility_ratio > 1.5:
                signal = 'HIGH_VOLATILITY'
                score = 30.0
            elif volatility_ratio < 0.7:
                signal = 'LOW_VOLATILITY'
                score = 70.0
            else:
                signal = 'NORMAL'
                score = 50.0
            
            return {
                'signal': signal,
                'score': score,
                'atr': float(atr),
                'volatility_ratio': float(volatility_ratio),
                'timestamp': datetime.now().isoformat(),
                'valid': True
            }
        
        except Exception as e:
            logger.error(f"ATR error: {e}")
            raise ValueError(f"ATR error: {e}")
