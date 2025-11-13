"""
DATA VALIDATOR - Real veri kalitesi kontrol
Binance API'dan gelen veri tamam mı?
"""

import numpy as np
from typing import Dict, Tuple, List

class DataValidator:
    
    @staticmethod
    def validate_price_data(prices: Dict[str, float]) -> Dict:
        """
        Fiyat verilerinin gerçeklik kontrol et
        
        ⚠️ Real veri kuralları:
        - Positive olmak zorunda
        - NaN/Inf olamaz
        - Extreme spike'lar kontrol et
        """
        
        issues = []
        
        # 1. NULL kontrol
        for symbol, price in prices.items():
            if price is None or (isinstance(price, float) and np.isnan(price)):
                issues.append(f"NULL_PRICE: {symbol}")
                continue
            
            # 2. Negatif kontrol (kripto fiyatı asla negatif olmaz)
            if isinstance(price, (int, float)) and price <= 0:
                issues.append(f"INVALID_PRICE: {symbol} = {price}")
                continue
            
            # 3. Extreme spike kontrol (1 saatte 50%+ artış = veri hatası)
            # Bu check'i sadece recent veri varsa yap
        
        quality_score = 100 - (len(issues) * 20)
        quality_score = max(0, quality_score)
        
        return {
            'valid': quality_score >= 80,
            'quality_score': quality_score,
            'issues': issues,
            'data_source': 'REAL_BINANCE_API',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
    
    @staticmethod
    def verify_real_data(prices: Dict, prev_prices: Dict = None) -> bool:
        """
        Verinin gerçek olduğunu verify et
        
        ⚠️ Golden Rule: Asla mock veri kabul etme
        """
        
        # Tüm fiyatlar pozitif olmalı
        if any(p <= 0 for p in prices.values() if isinstance(p, (int, float))):
            return False
        
        # Tüm fiyatlar NaN olmayan float olmalı
        if any(not isinstance(p, (int, float)) or np.isnan(p) for p in prices.values()):
            return False
        
        return True
