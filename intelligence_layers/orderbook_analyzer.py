"""
ORDER BOOK ANALYZER
Buyer/Seller imbalance tespiti

⚠️ REAL DATA: Binance order book
"""

from typing import Dict
import logging

logger = logging.getLogger(__name__)


class OrderBookAnalyzer:
    """Order book analizi"""
    
    @staticmethod
    def analyze_imbalance(bid_volume: float, 
                         ask_volume: float) -> Dict:
        """
        Bid/Ask imbalance analiz et
        
        bid_volume > ask_volume = Buyer demand (LONG)
        ask_volume > bid_volume = Seller pressure (SHORT)
        
        Args:
            bid_volume: Total bid volume (REAL)
            ask_volume: Total ask volume (REAL)
        
        Returns:
            Dict: Imbalance analysis
        """
        
        total_volume = bid_volume + ask_volume
        
        if total_volume == 0:
            return {
                'imbalance': 0,
                'signal': 'NEUTRAL',
                'status': 'NO_VOLUME'
            }
        
        imbalance = (bid_volume - ask_volume) / total_volume
        
        if imbalance > 0.3:
            signal = 'STRONG_BUY'
            severity = 'HIGH'
        elif imbalance > 0.1:
            signal = 'BUY'
            severity = 'MEDIUM'
        elif imbalance < -0.3:
            signal = 'STRONG_SELL'
            severity = 'HIGH'
        elif imbalance < -0.1:
            signal = 'SELL'
            severity = 'MEDIUM'
        else:
            signal = 'NEUTRAL'
            severity = 'LOW'
        
        return {
            'imbalance': imbalance,
            'imbalance_percent': imbalance * 100,
            'signal': signal,
            'severity': severity,
            'bid_volume': bid_volume,
            'ask_volume': ask_volume,
            'total_volume': total_volume
        }
