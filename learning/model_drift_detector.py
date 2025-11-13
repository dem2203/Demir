"""
MODEL DRIFT DETECTION
Model'in performansı düştü mü?

⚠️ REAL DATA: Gerçek performance metrics
"""

from datetime import datetime, timedelta
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class ModelDriftDetector:
    """Model drift'i tespit et"""
    
    def __init__(self, reference_period_days: int = 30):
        self.reference_period = reference_period_days
        self.baseline_metrics = None
    
    def detect_drift(self, current_metrics: Dict) -> Dict:
        """
        Model drift tespiti
        
        Args:
            current_metrics: {
                'sharpe_ratio': 1.5,
                'win_rate': 0.55,
                'profit_factor': 1.8
            }
        
        Returns:
            Dict: Drift detection result
        """
        
        if self.baseline_metrics is None:
            self.baseline_metrics = current_metrics
            return {'drift_detected': False, 'reason': 'Baseline initialized'}
        
        # Sharpe ratio karşılaştır
        baseline_sharpe = self.baseline_metrics.get('sharpe_ratio', 0)
        current_sharpe = current_metrics.get('sharpe_ratio', 0)
        
        drift_score = 0
        drift_reasons = []
        
        # Sharpe drift (%20 üzerinde)
        if baseline_sharpe != 0:
            sharpe_change = abs(current_sharpe - baseline_sharpe) / abs(baseline_sharpe)
            if sharpe_change > 0.20:
                drift_score += 1
                drift_reasons.append(f"Sharpe degradation: {sharpe_change*100:.1f}%")
        
        # Win rate drift
        baseline_wr = self.baseline_metrics.get('win_rate', 0)
        current_wr = current_metrics.get('win_rate', 0)
        
        if baseline_wr != 0:
            wr_change = abs(current_wr - baseline_wr) / baseline_wr
            if wr_change > 0.15:
                drift_score += 1
                drift_reasons.append(f"Win rate drop: {wr_change*100:.1f}%")
        
        # Profit factor drift
        baseline_pf = self.baseline_metrics.get('profit_factor', 0)
        current_pf = current_metrics.get('profit_factor', 0)
        
        if baseline_pf != 0:
            pf_change = abs(current_pf - baseline_pf) / baseline_pf
            if pf_change > 0.25:
                drift_score += 1
                drift_reasons.append(f"Profit factor decline: {pf_change*100:.1f}%")
        
        drift_detected = drift_score >= 2
        
        return {
            'drift_detected': drift_detected,
            'drift_score': drift_score,
            'reasons': drift_reasons,
            'action': 'EMERGENCY_RETRAIN' if drift_detected else 'CONTINUE'
        }
