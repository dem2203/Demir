"""
LIQUIDATION CASCADE DETECTION
Massive liquidations = market crash risk

⚠️ REAL DATA: Binance Liquidation API'dan gerçek veri
"""

from datetime import datetime, timedelta
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class LiquidationCascadeDetector:
    """
    Liquidation cascade tespiti
    REAL Binance liquidation data'sı kullan
    """
    
    def __init__(self):
        self.liquidation_threshold = 10_000_000  # $10M
        self.cascade_threshold = 3  # 3+ exchange'de eş zamanlı
        self.history = []
    
    async def detect_liquidation_cascade(self, liquidations: List[Dict]) -> Dict:
        """
        Liquidation cascade tespiti
        
        Args:
            liquidations: REAL Binance liquidation data
                [{
                    'symbol': 'BTCUSDT',
                    'side': 'BUY',
                    'price': 45000,
                    'quantity': 1.5,
                    'amount': 67500,
                    'timestamp': datetime
                }, ...]
        
        Returns:
            Dict: Cascade detection result
        """
        
        try:
            if not liquidations:
                return {'cascade_detected': False, 'reason': 'No liquidations'}
            
            # Toplam liquidation miktarı
            total_liquidated = sum(l.get('amount', 0) for l in liquidations)
            
            # History'ye ekle
            self.history.append({
                'timestamp': datetime.now(),
                'total_amount': total_liquidated,
                'count': len(liquidations),
                'data': liquidations
            })
            
            # Son 1 saati kontrol et
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent = [h for h in self.history if h['timestamp'] > one_hour_ago]
            
            # Cascade tespiti
            if total_liquidated > self.liquidation_threshold:
                return {
                    'cascade_detected': True,
                    'severity': 'CRITICAL' if total_liquidated > self.liquidation_threshold * 2 else 'WARNING',
                    'total_liquidated': total_liquidated,
                    'liquidation_count': len(liquidations),
                    'action': 'STOP_TRADING' if total_liquidated > self.liquidation_threshold * 2 else 'REDUCE_POSITION',
                    'reason': f'Large liquidation cascade: ${total_liquidated:,.0f}'
                }
            
            # Seri cascade kontrol
            if len(recent) >= self.cascade_threshold:
                recent_total = sum(h['total_amount'] for h in recent)
                
                if recent_total > self.liquidation_threshold * 3:
                    return {
                        'cascade_detected': True,
                        'severity': 'CRITICAL',
                        'recent_total_1h': recent_total,
                        'events': len(recent),
                        'action': 'EMERGENCY_CLOSE',
                        'reason': f'Cascading liquidations in last hour: ${recent_total:,.0f}'
                    }
            
            return {
                'cascade_detected': False,
                'recent_liquidations': total_liquidated,
                'status': 'NORMAL'
            }
        
        except Exception as e:
            logger.error(f"❌ Cascade detection failed: {e}")
            return {'cascade_detected': False, 'error': str(e)}
