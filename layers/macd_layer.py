"""
MACD LAYER - v2.0
Moving Average Convergence Divergence
⚠️ NO MOCK DATA - Real price calculations only
"""

from utils.base_layer import BaseLayer
from datetime import datetime
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class MACDLayer(BaseLayer):
    """MACD Layer with error handling"""
    
    def __init__(self):
        """Initialize MACD Layer"""
        super().__init__('MACD_Layer')
    
    async def get_signal(self, prices):
        """Get MACD signal
        
        Args:
            prices: Real price list from BINANCE
        
        Returns:
            MACD analysis or ERROR (never mock!)
        """
        return await self.execute_with_retry(
            self._calculate_macd,
            prices
        )
    
    async def _calculate_macd(self, prices):
        """Calculate MACD - real calculation"""
        if not prices or len(prices) < 26:
            raise ValueError("Insufficient data for MACD")
        
        try:
            series = pd.Series(prices)
            
            # EMA calculations
            ema12 = series.ewm(span=12, adjust=False).mean()
            ema26 = series.ewm(span=26, adjust=False).mean()
            
            # MACD line and signal line
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            histogram = macd_line - signal_line
            
            # Current values
            current_macd = macd_line.iloc[-1]
            current_signal = signal_line.iloc[-1]
            current_hist = histogram.iloc[-1]
            
            # Validate
            if np.isnan(current_macd) or np.isnan(current_hist):
                raise ValueError("Invalid MACD values")
            
            # Signal
            if current_hist > 0 and current_macd > current_signal:
                signal = 'LONG'
                score = 75.0
            elif current_hist < 0 and current_macd < current_signal:
                signal = 'SHORT'
                score = 25.0
            else:
                signal = 'NEUTRAL'
                score = 50.0
            
            return {
                'signal': signal,
                'score': score,
                'macd': float(current_macd),
                'signal_line': float(current_signal),
                'histogram': float(current_hist),
                'timestamp': datetime.now().isoformat(),
                'valid': True
            }
        
        except Exception as e:
            logger.error(f"MACD calculation failed: {e}")
            raise ValueError(f"MACD error: {e}")
