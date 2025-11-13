"""
VOLUME LAYER - v2.0
Volume analysis with BaseLayer
"""

from utils.base_layer import BaseLayer
from datetime import datetime
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class VolumeLayer(BaseLayer):
    """Volume Analysis Layer"""
    
    def __init__(self, period=20):
        """Initialize"""
        super().__init__('Volume_Layer')
        self.period = period
    
    async def get_signal(self, prices, volumes):
        """Get volume signal
        
        Args:
            prices: Price list
            volumes: Volume list (REAL volumes from BINANCE)
        """
        return await self.execute_with_retry(
            self._analyze_volume,
            prices,
            volumes
        )
    
    async def _analyze_volume(self, prices, volumes):
        """Analyze volume"""
        if not volumes or len(volumes) < self.period:
            raise ValueError("Insufficient volume data")
        
        try:
            vol_series = pd.Series(volumes)
            avg_volume = vol_series.rolling(self.period).mean().iloc[-1]
            current_volume = volumes[-1]
            current_price = prices[-1]
            prev_price = prices[-2] if len(prices) > 1 else prices[-1]
            
            # Volume ratio
            vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Price direction
            price_up = current_price > prev_price
            
            # Signal
            if vol_ratio > 1.5 and price_up:
                signal = 'LONG'
                score = 70.0
            elif vol_ratio > 1.5 and not price_up:
                signal = 'SHORT'
                score = 30.0
            else:
                signal = 'NEUTRAL'
                score = 50.0
            
            return {
                'signal': signal,
                'score': score,
                'current_volume': float(current_volume),
                'avg_volume': float(avg_volume),
                'volume_ratio': float(vol_ratio),
                'timestamp': datetime.now().isoformat(),
                'valid': True
            }
        
        except Exception as e:
            logger.error(f"Volume error: {e}")
            raise ValueError(f"Volume error: {e}")
