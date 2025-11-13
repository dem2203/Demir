"""
VWAP LAYER - v2.0
Volume Weighted Average Price
"""

from utils.base_layer import BaseLayer
from datetime import datetime
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class VWAPLayer(BaseLayer):
    """Volume Weighted Average Price Layer"""
    
    def __init__(self):
        """Initialize"""
        super().__init__('VWAP_Layer')
    
    async def get_signal(self, prices, volumes):
        """Get VWAP signal"""
        return await self.execute_with_retry(
            self._calculate_vwap,
            prices,
            volumes
        )
    
    async def _calculate_vwap(self, prices, volumes):
        """Calculate VWAP"""
        if not prices or not volumes or len(prices) != len(volumes):
            raise ValueError("Price/volume mismatch")
        
        try:
            # VWAP calculation
            tp = np.array(prices)  # Typical Price
            vol = np.array(volumes)
            
            cumul_tp_vol = np.cumsum(tp * vol)
            cumul_vol = np.cumsum(vol)
            
            vwap = cumul_tp_vol[-1] / cumul_vol[-1] if cumul_vol[-1] > 0 else prices[-1]
            current_price = prices[-1]
            
            # Signal
            if current_price < vwap:
                signal = 'UNDERVALUED'
                score = 70.0
            elif current_price > vwap:
                signal = 'OVERVALUED'
                score = 30.0
            else:
                signal = 'FAIR'
                score = 50.0
            
            return {
                'signal': signal,
                'score': score,
                'current_price': float(current_price),
                'vwap': float(vwap),
                'difference_pct': float((current_price - vwap) / vwap * 100),
                'timestamp': datetime.now().isoformat(),
                'valid': True
            }
        
        except Exception as e:
            logger.error(f"VWAP error: {e}")
            raise ValueError(f"VWAP error: {e}")
