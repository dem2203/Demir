# ============================================================================
# LAYER 3: BOLLINGER_BANDS_LAYER.PY
# ============================================================================

class BollingerBandsLayer:
    def __init__(self, period=20, std_dev=2):
        self.period = period
        self.std_dev = std_dev
        logger.info("✅ Bollinger Bands Layer initialized")
    
    def analyze(self, prices):
        if len(prices) < self.period:
            return {'signal': 'NEUTRAL', 'score': 50}
        
        series = pd.Series(prices)
        sma = series.rolling(self.period).mean()
        std = series.rolling(self.period).std()
        
        upper_band = sma + (std * self.std_dev)
        lower_band = sma - (std * self.std_dev)
        
        current_price = prices[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        
        if current_price > current_upper:
            signal = 'OVERBOUGHT'
            score = 25
        elif current_price < current_lower:
            signal = 'OVERSOLD'
            score = 75
        else:
            signal = 'NEUTRAL'
            score = 50
        
        return {'upper': current_upper, 'lower': current_lower, 'signal': signal, 'score': score}
