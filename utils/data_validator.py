"""
DATA VALIDATOR
Gelen verilerin kalitesini kontrol et
REAL veri doğrulaması

⚠️ GOLDEN RULE:
- ASLA mock veri kabul etme
- Null/NaN/Inf kontrol
- Outlier tespiti
- Extreme spike kontrol
"""

import numpy as np
import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Validasyon sonucu"""
    is_valid: bool
    quality_score: float  # 0-100
    issues: List[str]
    recommendation: str  # 'USE', 'USE_WITH_CAUTION', 'SKIP'
    details: Dict


class DataValidator:
    """Veri validasyonu - REAL data only"""
    
    @staticmethod
    def validate_price_data(prices: Dict[str, float]) -> ValidationResult:
        """
        Fiyat verisinin kalitesini kontrol et
        
        ⚠️ REAL DATA kontrolleri:
        - Kripto fiyatlar ASLA negatif olmaz
        - NULL/NaN olamaz
        - Extreme spike'lar = veri hatası
        - Duplicate fiyatlar = veri hatası
        
        Args:
            prices: {'BTC': 45000, 'ETH': 2500, 'SOL': 120, ...}
        
        Returns:
            ValidationResult: Validasyon sonucu
        """
        
        issues = []
        
        if not prices:
            return ValidationResult(
                is_valid=False,
                quality_score=0,
                issues=['EMPTY_PRICES'],
                recommendation='SKIP',
                details={}
            )
        
        # 1. NULL/NaN kontrol
        null_count = 0
        for symbol, price in prices.items():
            if price is None or (isinstance(price, float) and np.isnan(price)):
                null_count += 1
                issues.append(f"NULL_PRICE: {symbol}")
        
        # 2. Negatif fiyat kontrol (kripto asla negatif olmaz!)
        negative_count = 0
        for symbol, price in prices.items():
            if isinstance(price, (int, float)) and price < 0:
                negative_count += 1
                issues.append(f"NEGATIVE_PRICE: {symbol}")
        
        # 3. Zero fiyat kontrol (dead coin?)
        zero_count = 0
        for symbol, price in prices.items():
            if isinstance(price, (int, float)) and price == 0:
                zero_count += 1
                issues.append(f"ZERO_PRICE: {symbol}")
        
        # 4. Outlier tespiti (IQR method)
        valid_prices = [p for p in prices.values() 
                       if isinstance(p, (int, float)) and p > 0]
        
        outlier_count = 0
        if len(valid_prices) > 3:
            q1 = np.percentile(valid_prices, 25)
            q3 = np.percentile(valid_prices, 75)
            iqr = q3 - q1
            
            for symbol, price in prices.items():
                if isinstance(price, (int, float)):
                    if price < q1 - 1.5*iqr or price > q3 + 1.5*iqr:
                        outlier_count += 1
                        issues.append(f"OUTLIER: {symbol} = {price}")
        
        # 5. Duplicate price kontrol
        unique_prices = len(set(p for p in prices.values() 
                               if isinstance(p, (int, float))))
        if unique_prices < len(prices) / 2:
            issues.append("DUPLICATE_PRICES_DETECTED")
        
        # 6. Extreme fluctuation (spike) kontrol
        sorted_prices = sorted([p for p in prices.values() 
                               if isinstance(p, (int, float))])
        if len(sorted_prices) > 1:
            min_price = sorted_prices
            max_price = sorted_prices[-1]
            if max_price / min_price > 2.0:  # 2x difference = spike
                issues.append(f"EXTREME_SPIKE: {max_price/min_price:.1f}x")
        
        # Kalite skoru
        problem_count = (null_count + negative_count + 
                        zero_count + outlier_count)
        
        quality_score = 100.0 - (problem_count * 15)
        quality_score = max(0, min(quality_score, 100))
        
        # Recommendation
        if quality_score >= 90:
            recommendation = 'USE'
        elif quality_score >= 60:
            recommendation = 'USE_WITH_CAUTION'
        else:
            recommendation = 'SKIP'
        
        return ValidationResult(
            is_valid=quality_score >= 80,
            quality_score=quality_score,
            issues=issues,
            recommendation=recommendation,
            details={
                'null_count': null_count,
                'negative_count': negative_count,
                'zero_count': zero_count,
                'outlier_count': outlier_count,
                'total_symbols': len(prices),
                'unique_prices': unique_prices
            }
        )
    
    @staticmethod
    def validate_signal(signal: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        AI sinyalinin geçerli olduğunu kontrol et
        
        Args:
            signal: AI sinyali
        
        Returns:
            (bool, List[str]): (Geçerli mi?, Sorunlar)
        """
        
        required_fields = {
            'signal': (str, ['LONG', 'SHORT', 'NEUTRAL']),
            'confidence': (float, [0, 100]),
            'symbol': str,
            'entry': float,
            'tp': float,
            'sl': float,
            'timestamp': str
        }
        
        issues = []
        
        for field, spec in required_fields.items():
            if field not in signal:
                issues.append(f"MISSING_FIELD: {field}")
                continue
            
            value = signal[field]
            
            # Type check
            if isinstance(spec, tuple):
                field_type, valid_range = spec
                
                if not isinstance(value, field_type):
                    issues.append(f"WRONG_TYPE: {field}")
                    continue
                
                # Range check
                if isinstance(valid_range, list) and len(valid_range) == 2:
                    min_val, max_val = valid_range
                    if not (min_val <= value <= max_val):
                        issues.append(f"OUT_OF_RANGE: {field} = {value}")
                
                elif isinstance(valid_range, list):
                    if value not in valid_range:
                        issues.append(f"INVALID_VALUE: {field}")
            
            else:
                if not isinstance(value, spec):
                    issues.append(f"WRONG_TYPE: {field}")
        
        # TP/SL logic kontrol
        if 'entry' in signal and 'tp' in signal and 'sl' in signal:
            entry = signal['entry']
            tp = signal['tp']
            sl = signal['sl']
            
            if tp <= entry:
                issues.append("TP_MUST_BE_ABOVE_ENTRY")
            if sl >= entry:
                issues.append("SL_MUST_BE_BELOW_ENTRY")
            
            # Risk/Reward ratio
            risk = abs(entry - sl)
            reward = abs(tp - entry)
            
            if reward / risk < 1.0:
                issues.append("REWARD_LESS_THAN_RISK")
        
        return (len(issues) == 0, issues)
    
    @staticmethod
    def validate_timeseries(data: List[float]) -> Dict:
        """
        Time series veri validasyonu
        
        Args:
            data: ['12.5', '12.3', '12.8', ...]
        
        Returns:
            Dict: Validasyon sonucu
        """
        
        issues = []
        
        if not data or len(data) < 2:
            return {'valid': False, 'issues': ['INSUFFICIENT_DATA']}
        
        try:
            numeric_data = [float(x) for x in data]
        except (ValueError, TypeError):
            return {'valid': False, 'issues': ['NON_NUMERIC_DATA']}
        
        # NaN kontrol
        nan_count = sum(1 for x in numeric_data if np.isnan(x))
        if nan_count > 0:
            issues.append(f"NaN_VALUES: {nan_count}")
        
        # Inf kontrol
        inf_count = sum(1 for x in numeric_data if np.isinf(x))
        if inf_count > 0:
            issues.append(f"INF_VALUES: {inf_count}")
        
        # Negativity check
        negative_count = sum(1 for x in numeric_data if x < 0)
        if negative_count > len(numeric_data) * 0.1:
            issues.append(f"NEGATIVE_VALUES: {negative_count}")
        
        # Stationarity check
        std = np.std(numeric_data)
        mean = np.mean(numeric_data)
        
        cv = (std / mean) if mean != 0 else 0
        if cv > 5.0:
            issues.append("HIGH_VOLATILITY")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'stats': {
                'count': len(numeric_data),
                'mean': mean,
                'std': std,
                'min': min(numeric_data),
                'max': max(numeric_data),
                'nan_count': nan_count,
                'inf_count': inf_count
            }
        }
