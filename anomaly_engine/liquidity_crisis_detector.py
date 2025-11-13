"""
LIQUIDITY CRISIS DETECTION
Exchange'den para çıkışı = Panic = Satış baskısı
REAL on-chain veri analizi
"""

from datetime import datetime, timedelta
from typing import Dict, List
import asyncio

logger = __import__('logging').getLogger(__name__)


class LiquidityCrisisDetector:
    """
    Likidite kriziş tespiti
    REAL on-chain verileri analiz et
    """
    
    def __init__(self):
        self.crisis_threshold = 0.7  # %70 para çıkışı
        self.warning_threshold = 0.5  # %50 = warning
        self.history = []
        self.max_history = 1000
    
    async def analyze_exchange_flows(self, exchange_data: Dict) -> Dict:
        """
        Exchange inflows/outflows analiz et
        
        Args:
            exchange_data: {
                'exchange': 'Binance',
                'inflow': 1000000,  # Real BTC/USD value
                'outflow': 3000000,  # Real BTC/USD value
                'timestamp': datetime
            }
        
        Returns:
            Dict: Crisis detection result
            
        ⚠️ REAL DATA: Glassnode/Nansen API'dan gerçek on-chain veri
        """
        
        try:
            inflow = float(exchange_data.get('inflow', 0))
            outflow = float(exchange_data.get('outflow', 0))
            total_flow = inflow + outflow
            
            if total_flow == 0:
                return {'crisis': False, 'reason': 'No significant flow'}
            
            outflow_ratio = outflow / total_flow
            
            # Record'u history'ye ekle
            self.history.append({
                'timestamp': datetime.now(),
                'exchange': exchange_data.get('exchange'),
                'inflow': inflow,
                'outflow': outflow,
                'ratio': outflow_ratio
            })
            
            if len(self.history) > self.max_history:
                self.history = self.history[-self.max_history:]
            
            # Kriziş detekt et
            if outflow_ratio >= self.crisis_threshold:
                return {
                    'crisis': True,
                    'severity': 'CRITICAL',
                    'outflow_ratio': outflow_ratio,
                    'outflow_amount': outflow,
                    'exchange': exchange_data.get('exchange'),
                    'action': 'STOP_TRADING',
                    'reason': f'CRITICAL liquidity drain: {outflow_ratio*100:.1f}% outflow'
                }
            
            elif outflow_ratio >= self.warning_threshold:
                return {
                    'crisis': True,
                    'severity': 'WARNING',
                    'outflow_ratio': outflow_ratio,
                    'outflow_amount': outflow,
                    'action': 'REDUCE_RISK',
                    'reason': f'WARNING: Significant outflow detected {outflow_ratio*100:.1f}%'
                }
            
            else:
                return {
                    'crisis': False,
                    'outflow_ratio': outflow_ratio,
                    'status': 'NORMAL'
                }
        
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return {'crisis': False, 'error': str(e)}
    
    async def detect_cascade_effect(self) -> Dict:
        """
        Cascade effect tespiti
        Eğer exchange'lerde eş zamanlı outflow varsa = panic
        """
        
        if len(self.history) < 2:
            return {'cascade_detected': False}
        
        recent = self.history[-10:]  # Son 10 record
        
        crisis_count = sum(1 for r in recent if r['ratio'] > self.warning_threshold)
        
        if crisis_count >= 3:  # 3+ exchange'de eş zamanlı sorun
            return {
                'cascade_detected': True,
                'severity': 'CRITICAL',
                'affected_exchanges': crisis_count,
                'action': 'EMERGENCY_CLOSE_ALL_POSITIONS',
                'reason': 'Cascading liquidity crisis detected'
            }
        
        return {'cascade_detected': False}
    
    def get_liquidity_score(self) -> float:
        """
        Genel likidite skoru (0-100)
        Düşük = risky, Yüksek = safe
        """
        
        if not self.history:
            return 100.0  # Safe by default
        
        recent = self.history[-20:]
        avg_outflow_ratio = sum(r['ratio'] for r in recent) / len(recent)
        
        # Score: 100 = no outflow, 0 = total outflow
        score = max(0, (1 - avg_outflow_ratio) * 100)
        
        return score
