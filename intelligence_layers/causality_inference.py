"""
CAUSALITY INFERENCE
Granger Causality Test ile sebep-sonuç bulma
Korelasyon ≠ Causality

⚠️ REAL DATA: Gerçek price time series
"""

try:
    from statsmodels.tsa.api import grangercausalitytests
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class CausalityInference:
    """
    Granger Causality testi
    Sebep-sonuç ilişkilerini bul
    """
    
    @staticmethod
    def detect_causality(source_data: list, 
                        target_data: list, 
                        max_lag: int = 7) -> Dict:
        """
        Granger Causality Test
        
        H0: source SEBEP DEĞİL target için
        H1: source SEBEP target için
        
        p-value < 0.05 = istatistiksel olarak significant causality
        
        Args:
            source_data: Source time series (gerçek prices)
            target_data: Target time series (gerçek prices)
            max_lag: Maximum lag değeri
        
        Returns:
            Dict: Causality test results
        """
        
        if not HAS_STATSMODELS:
            logger.warning("⚠️ Statsmodels not installed - using fallback")
            return {'causality_detected': False, 'method': 'FALLBACK'}
        
        try:
            if len(source_data) < max_lag + 10:
                return {'causality_detected': False, 'reason': 'Insufficient data'}
            
            # Veri hazırla
            data = np.column_stack([source_data, target_data])
            
            # Granger test çalıştır
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
                'strength': 1 - best_pvalue if causality_detected else 0,
                'significance': 'p < 0.05' if causality_detected else f'p = {best_pvalue:.4f}',
                'interpretation': 'Source CAUSES target (Granger sense)' if causality_detected else 'No causality detected'
            }
        
        except Exception as e:
            logger.error(f"Causality test failed: {e}")
            return {'causality_detected': False, 'error': str(e)}
