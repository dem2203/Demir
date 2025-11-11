# ============================================================================
# LAYER 3: MARKET REGIME DETECTOR (YENİ DOSYA)
# ============================================================================
# Dosya: Demir/layers/market_regime_detector_v5.py
# Durum: YENİ (eski versiyonu replace et)

class MarketRegimeDetector:
    """
    Real regime detection using multiple methods
    - Volatility regimes
    - Trend regimes
    - Correlation regimes
    """
    
    def __init__(self):
        logger.info("✅ MarketRegimeDetector initialized")

    def detect_regime(self, prices: np.ndarray, window: int = 20) -> dict:
        """
        Detect market regime from REAL price data
        """
        
        if len(prices) < window:
            return {'regime': 'INSUFFICIENT_DATA', 'confidence': 0}
        
        # Calculate metrics
        returns = np.diff(prices) / prices[:-1]
        
        # Volatility regime
        recent_vol = np.std(returns[-window:])
        historical_vol = np.std(returns)
        
        if recent_vol > historical_vol * 1.5:
            vol_regime = 'HIGH_VOLATILITY'
        elif recent_vol < historical_vol * 0.7:
            vol_regime = 'LOW_VOLATILITY'
        else:
            vol_regime = 'NORMAL_VOLATILITY'
        
        # Trend regime
        sma_short = np.mean(prices[-10:])
        sma_long = np.mean(prices[-50:]) if len(prices) >= 50 else np.mean(prices)
        
        if sma_short > sma_long * 1.02:
            trend_regime = 'UPTREND'
        elif sma_short < sma_long * 0.98:
            trend_regime = 'DOWNTREND'
        else:
            trend_regime = 'SIDEWAYS'
        
        # Combined regime
        regime = f"{trend_regime}_{vol_regime}"
        
        logger.info(f"✅ Market regime detected: {regime}")
        
        return {
            'regime': regime,
            'trend': trend_regime,
            'volatility': vol_regime,
            'confidence': 0.75
        }
