"""
MODEL DRIFT DETECTION
Model'in performansı düştü mü?
"""

from datetime import datetime, timedelta

class ModelDriftDetector:
    
    def __init__(self, reference_period_days=30):
        self.reference_period = reference_period_days
        self.baseline_metrics = None
    
    def detect_drift(self, current_metrics: Dict) -> Dict:
        """Model drift'i tespit et"""
        
        if self.baseline_metrics is None:
            self.baseline_metrics = current_metrics
            return {'drift_detected': False}
        
        baseline_sharpe = self.baseline_metrics.get('sharpe_ratio', 0)
        current_sharpe = current_metrics.get('sharpe_ratio', 0)
        
        if baseline_sharpe != 0:
            sharpe_change = abs(current_sharpe - baseline_sharpe) / abs(baseline_sharpe)
            
            if sharpe_change > 0.20:  # %20'den fazla düşüş
                return {
                    'drift_detected': True,
                    'reason': f'Sharpe ratio declined {sharpe_change*100:.1f}%',
                    'action': 'RETRAIN_MODEL'
                }
        
        return {'drift_detected': False}
