"""
FRACTAL CHAOS LAYER - v2.0
Fractal analysis and chaos indicators
"""

from utils.base_layer import BaseLayer
from datetime import datetime
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class FractalChaosLayer(BaseLayer):
    """Fractal and Chaos Analysis Layer"""
    
    def __init__(self, max_lag=30):
        """Initialize"""
        super().__init__('FractalChaos_Layer')
        self.max_lag = max_lag
    
    async def get_signal(self, prices):
        """Get fractal chaos signal"""
        return await self.execute_with_retry(
            self._analyze_chaos,
            prices
        )
    
    async def _analyze_chaos(self, prices):
        """Analyze chaos indicators"""
        if not prices or len(prices) < 50:
            raise ValueError("Insufficient data")
        
        try:
            # Hurst Exponent
            hurst = self._calculate_hurst_exponent(prices)
            
            # Lyapunov Exponent
            lyapunov = self._calculate_lyapunov_exponent(prices)
            
            # Trend
            series = pd.Series(prices)
            coeffs = np.polyfit(range(len(prices[-50:])), prices[-50:], 1)
            trend = coeffs
            
            # Signal
            if hurst > 0.6 and trend > 0:
                signal = 'TRENDING_UP'
                score = 75.0
            elif hurst < 0.4 and trend < 0:
                signal = 'TRENDING_DOWN'
                score = 25.0
            elif lyapunov > 0.1:
                signal = 'CHAOTIC'
                score = 50.0
            else:
                signal = 'NEUTRAL'
                score = 50.0
            
            return {
                'signal': signal,
                'score': score,
                'hurst': float(hurst),
                'lyapunov': float(lyapunov),
                'trend': float(trend),
                'timestamp': datetime.now().isoformat(),
                'valid': True
            }
        
        except Exception as e:
            logger.error(f"Fractal chaos error: {e}")
            raise ValueError(f"Chaos error: {e}")
    
    def _calculate_hurst_exponent(self, prices):
        """Calculate Hurst Exponent"""
        try:
            series = np.array(prices)
            tau = []
            
            for lag in range(2, self.max_lag):
                pp = np.array([series[i:i+lag] for i in range(0, len(series), lag)])
                
                if len(pp) == 0:
                    continue
                
                m = np.mean(pp, axis=1)
                r = np.array([
                    np.max(np.cumsum(pp[i] - m[i])) - np.min(np.cumsum(pp[i] - m[i]))
                    for i in range(len(pp))
                ])
                s = np.std(pp, axis=1)
                s[s == 0] = 1e-10
                rs = r / s
                tau.append(np.mean(rs))
            
            if len(tau) > 1:
                poly = np.polyfit(np.log(range(2, len(tau) + 2)), np.log(tau), 1)
                return max(0, min(1, poly))
            
            return 0.5
        
        except Exception as e:
            logger.warning(f"Hurst calculation failed: {e}")
            return 0.5
    
    def _calculate_lyapunov_exponent(self, prices, lag=1):
        """Calculate Lyapunov Exponent"""
        try:
            log_returns = np.diff(np.log(prices))
            
            if len(log_returns) < lag + 10:
                return 0.0
            
            distances = []
            
            for i in range(len(log_returns) - lag):
                d0 = abs(log_returns[i])
                d1 = abs(log_returns[i + lag])
                
                if d0 > 1e-10:
                    distances.append(np.log(d1 / d0))
            
            if len(distances) > 0:
                return np.mean(distances) / lag
            
            return 0.0
        
        except Exception as e:
            logger.warning(f"Lyapunov calculation failed: {e}")
            return 0.0
