"""
BOLLINGER BANDS LAYER - v2.0
Volatility indicator with real price data
"""

from utils.base_layer import BaseLayer
from datetime import datetime
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class BollingerBandsLayer(BaseLayer):
    """Bollinger Bands Layer"""
    
    def __init__(self, period=20, stddev=2):
        """Initialize
        
        Args:
            period: Moving average period (default 20)
            stddev: Standard deviations (default 2)
        """
        super().__init__('BollingerBands_Layer')
        self.period = period
        self.stddev = stddev
    
    async def get_signal(self, prices):
        """Get Bollinger Bands signal"""
        return await self.execute_with_retry(
            self._calculate_bands,
            prices
        )
    
    async def _calculate_bands(self, prices):
        """Calculate Bollinger Bands"""
        if not prices or len(prices) < self.period:
            raise ValueError("Insufficient data")
        
        try:
            series = pd.Series(prices)
            sma = series.rolling(self.period).mean()
            std = series.rolling(self.period).std()
            
            upper_band = sma + (std * self.stddev)
            lower_band = sma - (std * self.stddev)
            
            current_price = prices[-1]
            current_upper = upper_band.iloc[-1]
            current_lower = lower_band.iloc[-1]
            current_sma = sma.iloc[-1]
            
            # Validate
            if np.isnan(current_upper) or np.isnan(current_lower):
                raise ValueError("Invalid bands")
            
            # Signal
            if current_price > current_upper:
                signal = 'OVERBOUGHT'
                score = 25.0
            elif current_price < current_lower:
                signal = 'OVERSOLD'
                score = 75.0
            else:
                signal = 'NEUTRAL'
                score = 50.0
            
            return {
                'signal': signal,
                'score': score,
                'upper_band': float(current_upper),
                'lower_band': float(current_lower),
                'sma': float(current_sma),
                'current_price': float(current_price),
                'timestamp': datetime.now().isoformat(),
                'valid': True
            }
        
        except Exception as e:
            logger.error(f"Bollinger Bands error: {e}")
            raise ValueError(f"BB error: {e}")
