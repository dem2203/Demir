# utils/signal_validator_comprehensive.py
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✔️  DEMIR AI v7.0 - COMPREHENSIVE SIGNAL VALIDATOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRITICAL SIGNAL VALIDATION SYSTEM

Features:
    ✅ Multi-layer signal validation
    ✅ Real data source verification
    ✅ Price logic validation (SL/TP vs Entry)
    ✅ Risk/Reward ratio checks
    ✅ Confidence score validation
    ✅ Timestamp freshness
    ✅ Group score consistency
    ✅ Multi-timeframe agreement

Enforcement:
    - Rejects ANY non-real data
    - Validates price from exchange APIs
    - Checks signal integrity
    - Ensures profitable R:R ratios

DEPLOYMENT: Railway Production
AUTHOR: DEMIR AI Research Team
DATE: 2025-11-19
VERSION: 7.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from collections import deque
import numpy as np

# Import real data verifier
from utils.real_data_verifier_pro import RealDataVerifier

logger = logging.getLogger(__name__)

# ============================================================================
# VALIDATION THRESHOLDS
# ============================================================================

# Minimum acceptable values
MIN_CONFIDENCE = 0.50           # 50% minimum confidence
MIN_RISK_REWARD_RATIO = 1.5     # 1:1.5 minimum R:R
MAX_RISK_PERCENT = 5.0          # 5% max risk per trade
MIN_PRICE_MOVEMENT = 0.001      # 0.1% minimum movement

# Data freshness
MAX_DATA_AGE_SECONDS = 60       # 60 seconds max age

# Group score thresholds
MIN_GROUP_SCORE = 0.30          # 30% minimum per group
MAX_GROUP_SCORE = 1.00          # 100% maximum per group

# ============================================================================
# SIGNAL VALIDATOR
# ============================================================================

class SignalValidator:
    """
    Comprehensive signal validation system
    
    Validates:
        1. Data source (must be real exchange)
        2. Price integrity (via RealDataVerifier)
        3. Signal structure (all required fields)
        4. Price logic (SL/TP positioning)
        5. Risk/Reward ratios
        6. Confidence scores
        7. Timestamp freshness
        8. Group score consistency
    """
    
    def __init__(self, min_confidence: float = MIN_CONFIDENCE):
        """
        Initialize validator
        
        Args:
            min_confidence: Minimum acceptable confidence (0.0 to 1.0)
        """
        self.min_confidence = min_confidence
        
        # Initialize real data verifier
        self.real_data_verifier = RealDataVerifier()
        
        # Validation history
        self.validation_history = deque(maxlen=1000)
        
        # Statistics
        self.stats = {
            'total_validations': 0,
            'passed': 0,
            'failed': 0,
            'pass_rate': 100.0
        }
        
        logger.info(f"✅ SignalValidator initialized (min_confidence: {min_confidence})")
    
    # ========================================================================
    # MAIN VALIDATION METHOD
    # ========================================================================
    
    def validate(self, signal: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Comprehensive signal validation
        
        Args:
            signal: Signal dictionary with all fields
        
        Returns:
            (is_valid, list_of_issues)
        """
        self.stats['total_validations'] += 1
        issues = []
        
        try:
            # 1. Validate structure (required fields)
            structure_issues = self._validate_structure(signal)
            issues.extend(structure_issues)
            
            if structure_issues:
                # If structure invalid, don't continue
                self._record_failure(signal, issues)
                return False, issues
            
            # 2. Validate data source (CRITICAL - must be real exchange)
            source_issues = self._validate_data_source(signal)
            issues.extend(source_issues)
            
            # 3. Validate price data (via RealDataVerifier)
            price_issues = self._validate_price_data(signal)
            issues.extend(price_issues)
            
            # 4. Validate price logic (SL/TP positioning)
            logic_issues = self._validate_price_logic(signal)
            issues.extend(logic_issues)
            
            # 5. Validate risk/reward ratio
            rr_issues = self._validate_risk_reward(signal)
            issues.extend(rr_issues)
            
            # 6. Validate confidence and scores
            score_issues = self._validate_scores(signal)
            issues.extend(score_issues)
            
            # 7. Validate timestamp freshness
            time_issues = self._validate_timestamp(signal)
            issues.extend(time_issues)
            
            # 8. Validate group scores consistency
            group_issues = self._validate_group_scores(signal)
            issues.extend(group_issues)
            
            # 9. Validate multi-timeframe agreement (if present)
            if any(key.startswith('tf_') for key in signal.keys()):
                tf_issues = self._validate_timeframe_agreement(signal)
                issues.extend(tf_issues)
            
            # Final verdict
            if issues:
                self._record_failure(signal, issues)
                return False, issues
            else:
                self._record_success(signal)
                return True, []
        
        except Exception as e:
            logger.error(f"Validation error: {e}")
            issues.append(f"Validation exception: {e}")
            self._record_failure(signal, issues)
            return False, issues
    
    # ========================================================================
    # VALIDATION METHODS
    # ========================================================================
    
    def _validate_structure(self, signal: Dict[str, Any]) -> List[str]:
        """Validate signal structure and required fields"""
        issues = []
        
        # Required fields
        required_fields = [
            'symbol',
            'direction',
            'entry_price',
            'sl',
            'tp1',
            'timestamp',
            'confidence',
            'data_source'
        ]
        
        for field in required_fields:
            if field not in signal:
                issues.append(f"Missing required field: {field}")
        
        # Check field types
        if 'symbol' in signal and not isinstance(signal['symbol'], str):
            issues.append(f"Invalid symbol type: {type(signal['symbol'])}")
        
        if 'direction' in signal:
            direction = signal['direction'].upper() if isinstance(signal['direction'], str) else ''
            if direction not in ['LONG', 'SHORT']:
                issues.append(f"Invalid direction: {signal['direction']}")
        
        # Numeric fields
        numeric_fields = ['entry_price', 'sl', 'tp1', 'confidence']
        for field in numeric_fields:
            if field in signal and not isinstance(signal[field], (int, float)):
                issues.append(f"Invalid {field} type: {type(signal[field])}")
        
        return issues
    
    def _validate_data_source(self, signal: Dict[str, Any]) -> List[str]:
        """Validate data source is from real exchange"""
        issues = []
        
        data_source = signal.get('data_source', '').upper()
        
        # Must contain real exchange name
        real_exchanges = ['BINANCE', 'BYBIT', 'COINBASE']
        
        has_real_source = any(exchange in data_source for exchange in real_exchanges)
        
        if not has_real_source:
            issues.append(
                f"Invalid data source: {data_source}. "
                f"Must be from BINANCE, BYBIT, or COINBASE"
            )
        
        # Check for non-real indicators (detection only)
        non_real_indicators = ['mock', 'fake', 'test', 'hardcoded', 'fallback']
        source_lower = data_source.lower()
        
        for indicator in non_real_indicators:
            if indicator in source_lower:
                issues.append(
                    f"Data source contains non-real indicator: '{indicator}'. "
                    f"Only real exchange data accepted."
                )
        
        return issues
    
    def _validate_price_data(self, signal: Dict[str, Any]) -> List[str]:
        """Validate price data using RealDataVerifier"""
        issues = []
        
        symbol = signal.get('symbol', '')
        entry_price = signal.get('entry_price', 0)
        data_source = signal.get('data_source', 'UNKNOWN')
        timestamp = signal.get('timestamp')
        
        # Extract exchange name
        exchange = data_source.upper()
        if '(' in exchange:
            exchange = exchange.split('(')[1].split(')')[0]
        
        # Verify with RealDataVerifier
        is_valid, reason = self.real_data_verifier.verify_price(
            symbol=symbol,
            price=entry_price,
            exchange=exchange,
            timestamp=timestamp
        )
        
        if not is_valid:
            issues.append(f"Price verification failed: {reason}")
        
        return issues
    
    def _validate_price_logic(self, signal: Dict[str, Any]) -> List[str]:
        """Validate SL/TP positioning logic"""
        issues = []
        
        direction = signal.get('direction', '').upper()
        entry_price = signal.get('entry_price', 0)
        sl = signal.get('sl', 0)
        tp1 = signal.get('tp1', 0)
        
        if direction == 'LONG':
            # LONG: SL < Entry < TP
            if sl >= entry_price:
                issues.append(
                    f"LONG position logic error: "
                    f"SL ({sl}) must be < Entry ({entry_price})"
                )
            
            if tp1 <= entry_price:
                issues.append(
                    f"LONG position logic error: "
                    f"TP1 ({tp1}) must be > Entry ({entry_price})"
                )
        
        elif direction == 'SHORT':
            # SHORT: TP < Entry < SL
            if sl <= entry_price:
                issues.append(
                    f"SHORT position logic error: "
                    f"SL ({sl}) must be > Entry ({entry_price})"
                )
            
            if tp1 >= entry_price:
                issues.append(
                    f"SHORT position logic error: "
                    f"TP1 ({tp1}) must be < Entry ({entry_price})"
                )
        
        # Validate TP2, TP3 if present
        if 'tp2' in signal:
            tp2 = signal['tp2']
            if direction == 'LONG' and tp2 <= tp1:
                issues.append(f"LONG: TP2 ({tp2}) must be > TP1 ({tp1})")
            elif direction == 'SHORT' and tp2 >= tp1:
                issues.append(f"SHORT: TP2 ({tp2}) must be < TP1 ({tp1})")
        
        if 'tp3' in signal:
            tp3 = signal['tp3']
            tp2 = signal.get('tp2', tp1)
            if direction == 'LONG' and tp3 <= tp2:
                issues.append(f"LONG: TP3 ({tp3}) must be > TP2 ({tp2})")
            elif direction == 'SHORT' and tp3 >= tp2:
                issues.append(f"SHORT: TP3 ({tp3}) must be < TP2 ({tp2})")
        
        return issues
    
    def _validate_risk_reward(self, signal: Dict[str, Any]) -> List[str]:
        """Validate risk/reward ratio"""
        issues = []
        
        entry_price = signal.get('entry_price', 0)
        sl = signal.get('sl', 0)
        tp1 = signal.get('tp1', 0)
        
        # Calculate risk and reward
        risk = abs(entry_price - sl)
        reward = abs(tp1 - entry_price)
        
        if risk <= 0:
            issues.append(f"Invalid risk calculation: {risk}")
            return issues
        
        # Calculate R:R ratio
        rr_ratio = reward / risk
        
        if rr_ratio < MIN_RISK_REWARD_RATIO:
            issues.append(
                f"Poor risk/reward ratio: {rr_ratio:.2f} "
                f"(minimum: {MIN_RISK_REWARD_RATIO})"
            )
        
        # Check if in signal
        if 'risk_reward_ratio' in signal:
            signal_rr = signal['risk_reward_ratio']
            # Allow 5% deviation
            if abs(signal_rr - rr_ratio) > (rr_ratio * 0.05):
                issues.append(
                    f"R:R ratio mismatch: signal={signal_rr:.2f}, "
                    f"calculated={rr_ratio:.2f}"
                )
        
        return issues
    
    def _validate_scores(self, signal: Dict[str, Any]) -> List[str]:
        """Validate confidence and other scores"""
        issues = []
        
        # Confidence validation
        confidence = signal.get('confidence', 0)
        
        if not (0 <= confidence <= 1):
            issues.append(f"Confidence out of range [0,1]: {confidence}")
        
        if confidence < self.min_confidence:
            issues.append(
                f"Confidence too low: {confidence} "
                f"(minimum: {self.min_confidence})"
            )
        
        # Ensemble score validation
        if 'ensemble_score' in signal:
            ensemble = signal['ensemble_score']
            if not (0 <= ensemble <= 1):
                issues.append(f"Ensemble score out of range: {ensemble}")
        
        return issues
    
    def _validate_timestamp(self, signal: Dict[str, Any]) -> List[str]:
        """Validate timestamp freshness"""
        issues = []
        
        timestamp = signal.get('timestamp')
        
        if timestamp is None:
            issues.append("Timestamp is missing")
            return issues
        
        # Convert to float if datetime
        if isinstance(timestamp, datetime):
            ts = timestamp.timestamp()
        else:
            ts = float(timestamp)
        
        current_time = time.time()
        age = current_time - ts
        
        # Check if in future
        if age < -60:  # 1 minute tolerance
            issues.append(f"Future timestamp: {-age:.0f}s ahead")
        
        # Check if too old
        if age > MAX_DATA_AGE_SECONDS:
            issues.append(
                f"Stale signal: {age:.0f}s old "
                f"(max: {MAX_DATA_AGE_SECONDS}s)"
            )
        
        return issues
    
    def _validate_group_scores(self, signal: Dict[str, Any]) -> List[str]:
        """Validate group scores consistency"""
        issues = []
        
        group_fields = [
            'tech_group_score',
            'sentiment_group_score',
            'ml_group_score',
            'onchain_group_score',
            'macro_risk_group_score'
        ]
        
        group_scores = []
        
        for field in group_fields:
            if field in signal:
                score = signal[field]
                
                # Range check
                if not (0 <= score <= 1):
                    issues.append(f"{field} out of range: {score}")
                
                group_scores.append(score)
        
        # If we have group scores, check ensemble consistency
        if group_scores and 'ensemble_score' in signal:
            calculated_ensemble = np.mean(group_scores)
            signal_ensemble = signal['ensemble_score']
            
            # Allow 5% deviation
            if abs(calculated_ensemble - signal_ensemble) > 0.05:
                issues.append(
                    f"Ensemble score mismatch: "
                    f"signal={signal_ensemble:.3f}, "
                    f"calculated={calculated_ensemble:.3f}"
                )
        
        return issues
    
    def _validate_timeframe_agreement(self, signal: Dict[str, Any]) -> List[str]:
        """Validate multi-timeframe agreement"""
        issues = []
        
        tf_fields = ['tf_15m_direction', 'tf_1h_direction', 'tf_4h_direction', 'tf_1d_direction']
        
        directions = []
        for field in tf_fields:
            if field in signal and signal[field]:
                directions.append(signal[field].upper())
        
        if len(directions) >= 2:
            # Count agreement
            long_count = directions.count('LONG')
            short_count = directions.count('SHORT')
            
            # At least 50% should agree
            total = len(directions)
            max_agreement = max(long_count, short_count)
            
            if max_agreement < (total * 0.5):
                issues.append(
                    f"Weak timeframe agreement: "
                    f"{long_count} LONG, {short_count} SHORT"
                )
        
        return issues
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def _record_success(self, signal: Dict[str, Any]):
        """Record successful validation"""
        self.stats['passed'] += 1
        
        self.validation_history.append({
            'symbol': signal.get('symbol'),
            'direction': signal.get('direction'),
            'confidence': signal.get('confidence'),
            'timestamp': time.time(),
            'result': 'PASSED'
        })
        
        # Update pass rate
        total = self.stats['total_validations']
        passed = self.stats['passed']
        self.stats['pass_rate'] = (passed / total * 100) if total > 0 else 100.0
    
    def _record_failure(self, signal: Dict[str, Any], issues: List[str]):
        """Record failed validation"""
        self.stats['failed'] += 1
        
        self.validation_history.append({
            'symbol': signal.get('symbol'),
            'direction': signal.get('direction'),
            'confidence': signal.get('confidence'),
            'timestamp': time.time(),
            'result': 'FAILED',
            'issues': issues
        })
        
        # Update pass rate
        total = self.stats['total_validations']
        passed = self.stats['passed']
        self.stats['pass_rate'] = (passed / total * 100) if total > 0 else 100.0
        
        # Log failures
        logger.error(f"❌ Signal validation FAILED: {signal.get('symbol')}")
        for issue in issues:
            logger.error(f"   - {issue}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return {
            'total_validations': self.stats['total_validations'],
            'passed': self.stats['passed'],
            'failed': self.stats['failed'],
            'pass_rate': self.stats['pass_rate'],
            'recent_validations': list(self.validation_history)[-10:]
        }
    
    def reset_statistics(self):
        """Reset statistics"""
        self.stats = {
            'total_validations': 0,
            'passed': 0,
            'failed': 0,
            'pass_rate': 100.0
        }
        self.validation_history.clear()
        logger.info("Validation statistics reset")

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_global_validator = None

def get_validator() -> SignalValidator:
    """Get global validator instance"""
    global _global_validator
    if _global_validator is None:
        _global_validator = SignalValidator()
    return _global_validator

def validate_signal(signal: Dict[str, Any]) -> bool:
    """Quick signal validation"""
    validator = get_validator()
    is_valid, _ = validator.validate(signal)
    return is_valid
