# ============================================================================
# LAYER 2: MACD_LAYER.PY (COPY-PASTE to Demir/layers/macd_layer.py)
# ============================================================================

import pandas as pd

class MACDLayer:
    def __init__(self):
        logger.info("✅ MACD Layer initialized")
    
    def analyze(self, prices):
        if len(prices) < 26:
            return {'macd': 0, 'signal': 'NEUTRAL', 'score': 50}
        
        series = pd.Series(prices)
        ema12 = series.ewm(span=12, adjust=False).mean()
        ema26 = series.ewm(span=26, adjust=False).mean()
        
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line
        
        current_hist = histogram.iloc[-1]
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        
        if current_hist > 0 and current_macd > current_signal:
            signal = 'BULLISH'
            score = 70
        elif current_hist < 0 and current_macd < current_signal:
            signal = 'BEARISH'
            score = 30
        else:
            signal = 'NEUTRAL'
            score = 50
        
        return {'macd': current_macd, 'histogram': current_hist, 'signal': signal, 'score': score}
