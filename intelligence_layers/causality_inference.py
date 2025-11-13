"""
CAUSALITY INFERENCE - Granger test
Sebep-sonuç ilişkilerini bul
"""

from statsmodels.tsa.api import grangercausalitytests
import numpy as np

class CausalityInference:
    
    @staticmethod
    def detect_causality(source_data: list, target_data: list, max_lag: int = 5) -> Dict:
        """
        Granger Causality Test
        H0: source → target sebep değil
        H1: source → target sebep
        """
        
        try:
            if len(source_data) < max_lag + 10:
                return {'causality_detected': False}
            
            data = np.column_stack([source_data, target_data])
            
            # Granger test
            result = grangercausalitytests(data, max_lag, verbose=False)
            
            best_pvalue = 1.0
            best_lag = 0
            
            for lag in range(1, max_lag + 1):
                try:
                    pvalue = result[lag]['ssr_ftest']
                    if pvalue < best_pvalue:
                        best_pvalue = pvalue
                        best_lag = lag
                except:
                    pass
            
            causality_detected = best_pvalue < 0.05
            
            return {
                'causality_detected': causality_detected,
                'pvalue': best_pvalue,
                'best_lag': best_lag,
                'strength': 1 - best_pvalue if causality_detected else 0
            }
        
        except:
            return {'causality_detected': False}
