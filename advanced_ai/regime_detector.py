"""
Market Regime Detection
Bull / Bear / Sideways
REAL statistical analysis - 100% Policy
"""

import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class RegimeDetector:
    """Detect market regimes"""
    
    def __init__(self):
        self.current_regime = None
    
    def detect(self, returns):
        """REAL regime detection"""
        try:
            if len(returns) < 60:
                return 'unknown'
            
            rolling_mean = pd.Series(returns).rolling(20).mean()
            rolling_std = pd.Series(returns).rolling(20).std()
            
            mean = rolling_mean.iloc[-1]
            std = rolling_std.iloc[-1]
            
            if mean > std:
                regime = 'bull'
            elif mean < -std:
                regime = 'bear'
            else:
                regime = 'sideways'
            
            self.current_regime = regime
            logger.info(f"✅ Regime: {regime.upper()}")
            return regime
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return 'unknown'
