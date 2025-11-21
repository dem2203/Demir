"""
Market Regime Detection
Bull / Bear / Sideways
REAL statistical analysis - 100% Policy
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List
from datetime import datetime
import pytz
import requests

logger = logging.getLogger(__name__)

class RegimeDetector:
    """Detect market regimes"""
    
    def __init__(self):
        self.current_regime = None
        self.session = requests.Session()
    
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
    
    def detect_current_regime(self) -> Dict:
        """
        ⭐ NEW v8.0: Main method called by background regime detection thread.
        
        Analyzes current market regime:
        - Fetches BTC price history from Binance
        - Calculates returns and statistical metrics
        - Determines bull/bear/sideways regime
        - Provides regime confidence and duration
        
        Returns comprehensive regime report with trading implications.
        """
        try:
            # Fetch BTC price history from Binance (90 days)
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': 'BTCUSDT',
                'interval': '1d',
                'limit': 90
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"❌ Binance API error: {response.status_code}")
                return {
                    'timestamp': datetime.now(pytz.UTC).isoformat(),
                    'regime': 'unknown',
                    'confidence': 0.0,
                    'error': 'Failed to fetch price data'
                }
            
            # Extract closing prices
            klines = response.json()
            closes = [float(k[4]) for k in klines]
            
            # Calculate returns
            returns = np.diff(closes) / closes[:-1]
            
            # Detect regime
            regime = self.detect(returns)
            
            # Calculate regime metrics
            recent_returns = returns[-20:]  # Last 20 days
            mean_return = np.mean(recent_returns)
            volatility = np.std(recent_returns)
            
            # Confidence based on consistency
            if regime == 'bull':
                positive_days = sum(1 for r in recent_returns if r > 0)
                confidence = (positive_days / len(recent_returns)) * 100
            elif regime == 'bear':
                negative_days = sum(1 for r in recent_returns if r < 0)
                confidence = (negative_days / len(recent_returns)) * 100
            else:  # sideways
                # Low volatility = high sideways confidence
                avg_volatility = 0.03  # Typical crypto daily volatility
                confidence = max(0, 100 - (volatility / avg_volatility * 100))
            
            # Build comprehensive report
            report = {
                'timestamp': datetime.now(pytz.UTC).isoformat(),
                'regime': regime,
                'confidence': round(confidence, 1),
                'metrics': {
                    'mean_return_20d': round(mean_return * 100, 2),  # As percentage
                    'volatility_20d': round(volatility * 100, 2),
                    'current_price': closes[-1]
                },
                'interpretation': self._interpret_regime(regime, confidence),
                'trading_recommendation': self._get_regime_recommendation(regime, confidence),
                'data_quality': 'REAL',
                'analysis_complete': True
            }
            
            logger.info(f"✅ Regime detected: {regime.upper()} (confidence: {confidence:.1f}%)")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error in detect_current_regime: {e}")
            return {
                'timestamp': datetime.now(pytz.UTC).isoformat(),
                'regime': 'unknown',
                'confidence': 0.0,
                'error': str(e),
                'analysis_complete': False
            }
    
    def _interpret_regime(self, regime: str, confidence: float) -> str:
        """Interpret regime with confidence level."""
        if regime == 'bull':
            if confidence > 70:
                return 'Strong bullish trend - Sustained upward momentum'
            elif confidence > 50:
                return 'Moderate bullish trend - Cautious optimism'
            else:
                return 'Weak bullish trend - Unstable momentum'
        elif regime == 'bear':
            if confidence > 70:
                return 'Strong bearish trend - Sustained downward pressure'
            elif confidence > 50:
                return 'Moderate bearish trend - Cautious pessimism'
            else:
                return 'Weak bearish trend - Unstable momentum'
        else:  # sideways
            if confidence > 60:
                return 'Strong sideways range - Low volatility consolidation'
            else:
                return 'Weak sideways range - Potential breakout soon'
    
    def _get_regime_recommendation(self, regime: str, confidence: float) -> str:
        """Get trading recommendation based on regime."""
        if regime == 'bull' and confidence > 60:
            return 'LONG bias - Follow trend, use pullbacks as entries'
        elif regime == 'bear' and confidence > 60:
            return 'SHORT bias - Avoid longs, wait for reversal confirmation'
        elif regime == 'sideways':
            return 'RANGE trading - Buy support, sell resistance, use tight stops'
        else:
            return 'NEUTRAL - Wait for clearer regime signal'

# ============================================================================
# BACKWARD COMPATIBILITY ALIAS
# ============================================================================

# main.py'de "from advanced_ai.regime_detector import MarketRegimeDetector" kullanıldığı için
MarketRegimeDetector = RegimeDetector

__all__ = ['RegimeDetector', 'MarketRegimeDetector']