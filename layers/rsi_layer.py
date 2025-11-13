"""
RSI LAYER - v2.0
Relative Strength Index with BaseLayer inheritance
⚠️ NO MOCK DATA - Uses real BINANCE prices
"""

from utils.base_layer import BaseLayer
from datetime import datetime
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class RSILayer(BaseLayer):
    """RSI Layer with real data fallback and error handling"""
    
    def __init__(self, period=14):
        """Initialize RSI Layer
        
        Args:
            period: RSI period (default 14)
        """
        super().__init__('RSI_Layer')
        self.period = period
    
    async def get_signal(self, prices):
        """Get RSI signal with auto-retry
        
        Args:
            prices: List of real prices from BINANCE API
        
        Returns:
            Dict with signal, score, timestamp
            If all real sources fail: returns NEUTRAL (not fake!)
        """
        return await self.execute_with_retry(
            self._calculate_rsi,
            prices
        )
    
    async def _calculate_rsi(self, prices):
        """Calculate RSI - actual logic
        
        ⚠️ All calculations on REAL prices
        """
        if not prices or len(prices) < self.period + 1:
            raise ValueError("Insufficient price data")
        
        try:
            series = pd.Series(prices)
            delta = series.diff()
            
            # Gains and losses
            gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
            
            # RSI calculation
            rs = gain / loss if loss.iloc[-1] != 0 else np.inf
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = rsi.iloc[-1]
            
            # Validate result
            if np.isnan(current_rsi) or np.isinf(current_rsi):
                raise ValueError("Invalid RSI calculation")
            
            # Signal generation
            if current_rsi < 30:
                signal = 'LONG'
                score = 75.0
            elif current_rsi > 70:
                signal = 'SHORT'
                score = 25.0
            else:
                signal = 'NEUTRAL'
                score = 50.0
            
            return {
                'signal': signal,
                'score': score,
                'rsi': float(current_rsi),
                'timestamp': datetime.now().isoformat(),
                'valid': True
            }
        
        except Exception as e:
            logger.error(f"RSI calculation failed: {e}")
            raise ValueError(f"RSI error: {e}")
