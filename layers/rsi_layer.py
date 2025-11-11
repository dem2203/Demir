# ============================================================================
# LAYER 1: RSI_LAYER.PY (COPY-PASTE to Demir/layers/rsi_layer.py)
# ============================================================================

import numpy as np
import logging

logger = logging.getLogger(__name__)

class RSILayer:
    def __init__(self, period=14):
        self.period = period
        logger.info(f"✅ RSI Layer initialized")
    
    def analyze(self, prices):
        if len(prices) < self.period + 1:
            return {'rsi': 50, 'signal': 'NEUTRAL', 'score': 50}
        
        deltas = np.diff(prices)
        seed = deltas[:self.period+1]
        up = seed[seed >= 0].sum() / self.period
        down = -seed[seed < 0].sum() / self.period
        
        rs = up / down if down != 0 else 0
        rsi = np.zeros_like(prices)
        rsi[:self.period] = 100. - 100. / (1. + rs)
        
        for i in range(self.period, len(prices)):
            delta = deltas[i-1]
            up = (up * (self.period - 1) + (delta if delta > 0 else 0)) / self.period
            down = (down * (self.period - 1) + (-delta if delta < 0 else 0)) / self.period
            rs = up / down if down != 0 else 1
            rsi[i] = 100. - 100. / (1. + rs)
        
        current_rsi = rsi[-1]
        
        if current_rsi < 30:
            signal = 'OVERSOLD'
            score = 75
        elif current_rsi > 70:
            signal = 'OVERBOUGHT'
            score = 25
        else:
            signal = 'NEUTRAL'
            score = 50
        
        return {'rsi': current_rsi, 'signal': signal, 'score': score}
