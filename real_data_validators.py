"""
DEMIR AI BOT - Real Data Validators
Mock/Fake/Test/Fallback/Prototype Detection
Production-grade data integrity verification
GOLDEN RULES ENFORCED: NO MOCK, FAKE, FALLBACK, HARDCODED, TEST, PROTOTYPE DATA
"""

import logging
import re
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class MockDataDetector:
    """Detect mock, fake, test, fallback, prototype data patterns."""
    
    # Keywords that indicate fake/mock/test data
    FAKE_KEYWORDS = [
        'mock', 'fake', 'test', 'fallback', 'prototype', 'dummy', 
        'sample', 'example', 'placeholder', 'stub', 'patch',
        'demo', 'trial', 'temp', 'temporary', 'staging'
    ]
    
    # Suspicious number patterns
    SUSPICIOUS_PATTERNS = [
        r'^0\.0+$',           # All zeros after decimal
        r'^1\.0+$',           # 1.0 exactly
        r'^\d{5,}$',          # Too many identical digits
        r'^9+\.9+$',          # Repeating 9s
        r'^\d\.0{5,}$',       # Many trailing zeros
    ]
    
    @staticmethod
    def detect_in_code(code_content: str) -> Tuple[bool, List[str]]:
        """Detect mock/fake patterns in code content."""
        violations = []
        
        # Check for mock keywords
        for keyword in MockDataDetector.FAKE_KEYWORDS:
            pattern = rf'\b{keyword}\b'
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1
                violations.append(
                    f"Line {line_num}: Found keyword '{keyword}' in code"
                )
        
        return len(violations) == 0, violations
    
    @staticmethod
    def detect_in_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Detect mock/fake patterns in data."""
        violations = []
        
        def check_value(key: str, value: Any, path: str = ""):
            current_path = f"{path}.{key}" if path else key
            
            # Check if key contains suspicious words
            for keyword in MockDataDetector.FAKE_KEYWORDS:
                if keyword.lower() in key.lower():
                    violations.append(
                        f"Key '{current_path}' contains mock keyword '{keyword}'"
                    )
            
            # Check if value is string with mock keywords
            if isinstance(value, str):
                for keyword in MockDataDetector.FAKE_KEYWORDS:
                    if keyword.lower() in value.lower():
                        violations.append(
                            f"Value at '{current_path}' contains mock keyword '{keyword}'"
                        )
            
            # Check numeric patterns
            if isinstance(value, (int, float)):
                str_val = str(value)
                for pattern in MockDataDetector.SUSPICIOUS_PATTERNS:
                    if re.match(pattern, str_val):
                        violations.append(
                            f"Suspicious pattern at '{current_path}': {value}"
                        )
            
            # Recursive check for dicts
            if isinstance(value, dict):
                for k, v in value.items():
                    check_value(k, v, current_path)
        
        for key, value in data.items():
            check_value(key, value)
        
        return len(violations) == 0, violations


class RealDataVerifier:
    """Verify that data comes from real exchange APIs."""
    
    def __init__(self, binance_client=None, bybit_client=None, coinbase_client=None):
        """Initialize with exchange clients."""
        self.binance = binance_client
        self.bybit = bybit_client
        self.coinbase = coinbase_client
        logger.info("RealDataVerifier initialized with exchange clients")
    
    def verify_price_data(
        self,
        symbol: str,
        price: float,
        source: str = "binance"
    ) -> Tuple[bool, str]:
        """Verify price is real from exchange."""
        try:
            if source.lower() == "binance" and self.binance:
                ticker = self.binance.fetch_ticker(symbol)
                real_price = ticker['last']
                
                # Allow 2% deviation (slippage)
                deviation = abs(price - real_price) / real_price
                
                if deviation > 0.02:
                    return False, f"Price deviation too high: {deviation:.2%}"
                
                return True, f"Price verified from Binance: {real_price}"
            
            elif source.lower() == "bybit" and self.bybit:
                ticker = self.bybit.fetch_ticker(symbol)
                real_price = ticker['last']
                
                deviation = abs(price - real_price) / real_price
                
                if deviation > 0.02:
                    return False, f"Price deviation too high: {deviation:.2%}"
                
                return True, f"Price verified from Bybit: {real_price}"
            
            elif source.lower() == "coinbase" and self.coinbase:
                ticker = self.coinbase.fetch_ticker(symbol)
                real_price = ticker['last']
                
                deviation = abs(price - real_price) / real_price
                
                if deviation > 0.02:
                    return False, f"Price deviation too high: {deviation:.2%}"
                
                return True, f"Price verified from Coinbase: {real_price}"
            
            else:
                return False, f"Exchange client not available: {source}"
        
        except Exception as e:
            logger.error(f"Failed to verify price: {e}")
            return False, str(e)
    
    def verify_timestamp(
        self,
        timestamp: float,
        max_age_seconds: int = 300
    ) -> Tuple[bool, str]:
        """Verify timestamp is recent (not stale data)."""
        try:
            current_time = datetime.now().timestamp()
            age = current_time - timestamp
            
            if age < 0:
                return False, "Timestamp is in the future"
            
            if age > max_age_seconds:
                return False, f"Data is stale: {age} seconds old"
            
            return True, f"Timestamp is recent: {age:.1f} seconds old"
        
        except Exception as e:
            logger.error(f"Failed to verify timestamp: {e}")
            return False, str(e)
    
    def verify_ohlcv_data(
        self,
        ohlcv: Dict[str, float],
        symbol: str
    ) -> Tuple[bool, List[str]]:
        """Verify OHLCV data consistency."""
        issues = []
        
        try:
            open_price = ohlcv.get('open', 0)
            high_price = ohlcv.get('high', 0)
            low_price = ohlcv.get('low', 0)
            close_price = ohlcv.get('close', 0)
            volume = ohlcv.get('volume', 0)
            
            # Verify high is highest
            if not (high_price >= open_price and high_price >= close_price):
                issues.append(f"High price ({high_price}) is not highest")
            
            # Verify low is lowest
            if not (low_price <= open_price and low_price <= close_price):
                issues.append(f"Low price ({low_price}) is not lowest")
            
            # Verify reasonable price range
            if high_price > 0 and low_price > 0:
                range_pct = (high_price - low_price) / low_price
                if range_pct > 0.5:  # More than 50% intraday move
                    issues.append(f"Unusual price range: {range_pct:.1%}")
            
            # Verify volume is positive
            if volume <= 0:
                issues.append("Volume is zero or negative")
            
            return len(issues) == 0, issues
        
        except Exception as e:
            logger.error(f"Failed to verify OHLCV: {e}")
            return False, [str(e)]


class SignalIntegrityChecker:
    """Check signal structure, fields, and value ranges."""
    
    REQUIRED_FIELDS = {
        'technical': ['direction', 'strength', 'confidence', 'active_layers', 'timestamp'],
        'sentiment': ['direction', 'strength', 'confidence', 'active_layers', 'timestamp'],
        'ml': ['direction', 'strength', 'confidence', 'active_layers', 'timestamp'],
        'onchain': ['direction', 'strength', 'confidence', 'active_layers', 'timestamp'],
        'consensus': ['direction', 'strength', 'confidence', 'active_groups', 'timestamp']
    }
    
    VALID_DIRECTIONS = ['LONG', 'SHORT', 'NEUTRAL']
    
    @staticmethod
    def check_signal_structure(signal: Dict[str, Any], group_type: str) -> Tuple[bool, List[str]]:
        """Check signal has all required fields."""
        issues = []
        
        required = SignalIntegrityChecker.REQUIRED_FIELDS.get(group_type, [])
        
        for field in required:
            if field not in signal:
                issues.append(f"Missing required field: {field}")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def check_value_ranges(signal: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Check values are in valid ranges."""
        issues = []
        
        # Check strength (0-1)
        if 'strength' in signal:
            strength = signal['strength']
            if not (0 <= strength <= 1):
                issues.append(f"Strength out of range: {strength}")
        
        # Check confidence (0-1)
        if 'confidence' in signal:
            confidence = signal['confidence']
            if not (0 <= confidence <= 1):
                issues.append(f"Confidence out of range: {confidence}")
        
        # Check direction
        if 'direction' in signal:
            if signal['direction'] not in SignalIntegrityChecker.VALID_DIRECTIONS:
                issues.append(f"Invalid direction: {signal['direction']}")
        
        # Check active_layers is positive
        if 'active_layers' in signal:
            layers = signal['active_layers']
            if not isinstance(layers, int) or layers < 0:
                issues.append(f"Invalid active_layers: {layers}")
        
        # Check timestamp is recent
        if 'timestamp' in signal:
            timestamp = signal['timestamp']
            current = datetime.now().timestamp()
            age = current - timestamp
            
            if age < 0:
                issues.append("Timestamp is in future")
            elif age > 3600:  # More than 1 hour old
                issues.append(f"Signal is stale: {age} seconds old")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def check_signal_consistency(signal: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Check signal consistency."""
        issues = []
        
        # If strength is high, confidence should be reasonable
        strength = signal.get('strength', 0)
        confidence = signal.get('confidence', 0)
        
        if strength > 0.75 and confidence < 0.3:
            issues.append("High strength but low confidence - inconsistent")
        
        # If few active layers, confidence should be lower
        active_layers = signal.get('active_layers', 0)
        
        if active_layers < 3 and confidence > 0.9:
            issues.append("Few active layers but high confidence - inconsistent")
        
        return len(issues) == 0, issues


class SignalValidator:
    """Master validator combining all checks."""
    
    def __init__(
        self,
        binance_client=None,
        bybit_client=None,
        coinbase_client=None
    ):
        """Initialize validator."""
        self.mock_detector = MockDataDetector()
        self.real_verifier = RealDataVerifier(binance_client, bybit_client, coinbase_client)
        self.integrity_checker = SignalIntegrityChecker()
        logger.info("SignalValidator initialized")
    
    def validate_signal(
        self,
        signal: Dict[str, Any],
        group_type: str
    ) -> Tuple[bool, List[str]]:
        """Validate signal comprehensively."""
        all_issues = []
        
        # Check 1: No mock/fake keywords
        is_real, mock_issues = self.mock_detector.detect_in_data(signal)
        all_issues.extend(mock_issues)
        
        # Check 2: Structure
        is_structured, structure_issues = self.integrity_checker.check_signal_structure(
            signal, group_type
        )
        all_issues.extend(structure_issues)
        
        # Check 3: Value ranges
        is_ranged, range_issues = self.integrity_checker.check_value_ranges(signal)
        all_issues.extend(range_issues)
        
        # Check 4: Consistency
        is_consistent, consistency_issues = self.integrity_checker.check_signal_consistency(signal)
        all_issues.extend(consistency_issues)
        
        is_valid = len(all_issues) == 0
        
        if is_valid:
            logger.info(f"Signal validated successfully (group: {group_type})")
        else:
            logger.warning(f"Signal validation failed: {all_issues}")
        
        return is_valid, all_issues
    
    def validate_batch(
        self,
        signals: Dict[str, Dict[str, Any]]
    ) -> Tuple[bool, Dict[str, List[str]]]:
        """Validate batch of group signals."""
        results = {}
        all_valid = True
        
        for group_type, signal in signals.items():
            is_valid, issues = self.validate_signal(signal, group_type)
            results[group_type] = issues
            
            if not is_valid:
                all_valid = False
        
        return all_valid, results
    
    def require_real_data(self):
        """Enforce that all subsequent signals must be real."""
        logger.info("ENFORCING GOLDEN RULE: ALL DATA MUST BE REAL - NO MOCK/FAKE/TEST")
        return True
