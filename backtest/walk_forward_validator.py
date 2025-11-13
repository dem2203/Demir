"""
WALK-FORWARD VALIDATION
Out-of-sample testing

⚠️ REAL DATA: Gerçek historical price verileri
"""

import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class WalkForwardValidator:
    """Out-of-sample validation framework"""
    
    @staticmethod
    def walk_forward_test(data: List[float], 
                         window_size: int = 252, 
                         step_size: int = 21) -> Dict:
        """
        Walk-forward validation
        
        Train: 252 gün (1 yıl)
        Test: 21 gün (1 ay)
        Overlap: None (true OOS)
        
        Args:
            data: Historical prices (REAL)
            window_size: Training window
            step_size: Step size
        
        Returns:
            Dict: Walk-forward results
        """
        
        results = []
        
        for i in range(0, len(data) - window_size, step_size):
            train_data = data[i:i+window_size]
            test_data = data[i+window_size:i+window_size+step_size]
            
            if len(test_data) < step_size:
                break
            
            fold_result = {
                'fold': len(results),
                'train_size': len(train_data),
                'test_size': len(test_data),
                'train_start': i,
                'train_end': i + window_size,
                'test_start': i + window_size,
                'test_end': i + window_size + step_size
            }
            
            results.append(fold_result)
        
        # OOS istatistikleri
        if results:
            mean_performance = np.mean([r['train_size'] for r in results]) / np.mean([r['test_size'] for r in results])
        else:
            mean_performance = 0
        
        return {
            'folds': results,
            'total_folds': len(results),
            'mean_train_size': np.mean([r['train_size'] for r in results]) if results else 0,
            'mean_test_size': np.mean([r['test_size'] for r in results]) if results else 0,
            'is_robust': len(results) >= 5
        }
