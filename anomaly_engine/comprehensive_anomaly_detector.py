"""
COMPREHENSIVE ANOMALY DETECTION
Flash crash, liquidation, extreme volatility

⚠️ REAL DATA: Gerçek market data
"""

from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Çok yönlü anomali tespiti"""
    
    @staticmethod
    def detect_price_spike(current_price: float, 
                          prev_price: float, 
                          threshold: float = 0.10) -> Dict:
        """
        Fiyat spike tespiti (>10% değişim)
        
        Args:
            current_price: Mevcut fiyat (REAL)
            prev_price: Önceki fiyat (REAL)
            threshold: Spike threshold (%)
        
        Returns:
            Dict: Anomaly result
        """
        
        if prev_price == 0:
            return {'anomaly': False}
        
        change = abs(current_price - prev_price) / prev_price
        
        if change > threshold:
            return {
                'anomaly': True,
                'type': 'PRICE_SPIKE',
                'change_percent': change * 100,
                'severity': 'CRITICAL' if change > 0.20 else 'WARNING',
                'action': 'PAUSE_TRADING'
            }
        
        return {'anomaly': False}
    
    @staticmethod
    def detect_volume_spike(current_volume: float, 
                           avg_volume: float, 
                           threshold: float = 3.0) -> Dict:
        """Volume spike tespiti"""
        
        if avg_volume == 0:
            return {'anomaly': False}
        
        ratio = current_volume / avg_volume
        
        if ratio > threshold:
            return {
                'anomaly': True,
                'type': 'VOLUME_SPIKE',
                'volume_ratio': ratio,
                'action': 'CHECK_NEWS'
            }
        
        return {'anomaly': False}
    
    @staticmethod
    def detect_volatility_explosion(recent_vol: float, 
                                   historical_vol: float, 
                                   threshold: float = 2.0) -> Dict:
        """Volatility explosion tespiti"""
        
        if historical_vol == 0:
            return {'anomaly': False}
        
        ratio = recent_vol / historical_vol
        
        if ratio > threshold:
            return {
                'anomaly': True,
                'type': 'VOLATILITY_EXPLOSION',
                'vol_ratio': ratio,
                'action': 'REDUCE_POSITION'
            }
        
        return {'anomaly': False}
