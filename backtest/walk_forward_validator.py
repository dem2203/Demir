"""
WALK-FORWARD VALIDATION
Out-of-sample testing için
"""

import numpy as np

class WalkForwardValidator:
    
    @staticmethod
    def walk_forward_test(data, window_size=252, step_size=21):
        """
        Train: 252 gün
        Test: 21 gün
        Overlap: None
        """
        
        results = []
        
        for i in range(0, len(data) - window_size, step_size):
            train_data = data[i:i+window_size]
            test_data = data[i+window_size:i+window_size+step_size]
            
            # Model'i train data'da eğit
            # Test data'da test et
            # Sonuç kaydet
            
            fold_result = {
                'fold': len(results),
                'train_size': len(train_data),
                'test_size': len(test_data),
                'performance': 0.0  # Gerçek test results burada
            }
            
            results.append(fold_result)
        
        # OOS stats
        mean_performance = np.mean([r['performance'] for r in results])
        std_performance = np.std([r['performance'] for r in results])
        
        return {
            'results': results,
            'mean_performance': mean_performance,
            'std_performance': std_performance,
            'is_robust': std_performance < 0.15  # Consistent mi?
        }
