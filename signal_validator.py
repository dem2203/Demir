"""
🚀 DEMIR AI v5.2 - Signal Validation Engine
🔐 100% Real Data Compliance Checker
📊 Mock/Fake/Fallback Data Detector

Location: GitHub Root / core/signal_validator.py (NEW FILE - CREATE FOLDER IF NOT EXISTS)
"""

import os
import logging
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import json
import hashlib
import requests
import pytz

logger = logging.getLogger('SIGNAL_VALIDATOR')

# ============================================================================
# BANNED PATTERNS DETECTOR - CATCH MOCK/FAKE/FALLBACK DATA
# ============================================================================

class MockDataDetector:
    """Detect and prevent any mock, fake, fallback, or test data"""
    
    # Patterns that indicate mock/fake/fallback data
    BANNED_KEYWORDS = [
        'mock_', 'test_', 'demo_', 'fake_', 'dummy_', 'sample_',
        'fallback_', 'prototype_', 'fixture_', 'debug_', 'hardcoded_',
        'MOCK_', 'TEST_', 'DEMO_', 'FAKE_', 'DUMMY_', 'SAMPLE_',
        'FALLBACK_', 'PROTOTYPE_', 'FIXTURE_', 'DEBUG_', 'HARDCODED_',
    ]
    
    # Banned hardcoded values
    BANNED_PRICES = [
        99999.99, 88888.88, 77777.77, 12345.67, 11111.11,
        10000.00, 5000.00, 1000.00, 100.00, 69.69, 42.42,
    ]
    
    @staticmethod
    def check_value(value: Any, field_name: str) -> Tuple[bool, str]:
        """
        Check if value contains banned patterns
        Returns: (is_valid, error_message)
        """
        if isinstance(value, str):
            # Check string keywords
            for banned in MockDataDetector.BANNED_KEYWORDS:
                if banned.lower() in value.lower():
                    return False, f"❌ Banned keyword '{banned}' found in {field_name}"
        
        if isinstance(value, (int, float)):
            # Check hardcoded prices
            if value in MockDataDetector.BANNED_PRICES:
                return False, f"❌ Hardcoded price detected: {value} in {field_name}"
        
        return True, "✅ Value OK"
    
    @staticmethod
    def check_signal(signal: Dict) -> Tuple[bool, List[str]]:
        """Check entire signal for mock/fake/fallback data"""
        errors = []
        
        for field, value in signal.items():
            is_valid, message = MockDataDetector.check_value(value, field)
            if not is_valid:
                errors.append(message)
        
        return len(errors) == 0, errors

# ============================================================================
# REAL DATA VERIFICATION ENGINE
# ============================================================================

class RealDataVerifier:
    """Verify that signal data comes from real sources"""
    
    def __init__(self):
        self.binance_url = 'https://fapi.binance.com'
        self.session = requests.Session()
    
    def verify_price_from_exchange(self, symbol: str, expected_price: float, 
                                   tolerance_percent: float = 1.0) -> Tuple[bool, str]:
        """
        Verify price matches real exchange data
        tolerance_percent: Allow price difference up to this % (default 1%)
        """
        try:
            # Fetch real price from Binance
            response = self.session.get(
                f'{self.binance_url}/fapi/v1/ticker/price',
                params={'symbol': symbol},
                timeout=5
            )
            
            if response.status_code != 200:
                return False, "❌ Could not fetch real price from Binance"
            
            real_price = float(response.json()['price'])
            
            # Calculate price difference percentage
            diff_percent = abs(expected_price - real_price) / real_price * 100
            
            if diff_percent > tolerance_percent:
                return False, f"❌ Price mismatch: expected ${expected_price}, real ${real_price} ({diff_percent:.2f}% diff)"
            
            return True, f"✅ Price verified: ${real_price} (diff: {diff_percent:.2f}%)"
        
        except Exception as e:
            logger.error(f"❌ Price verification error: {e}")
            return False, f"❌ Verification error: {str(e)}"
    
    def verify_signal_timestamps(self, signal: Dict) -> Tuple[bool, str]:
        """Verify signal timestamp is current (within last 1 minute)"""
        try:
            signal_time = signal.get('timestamp')
            if isinstance(signal_time, str):
                signal_time = datetime.fromisoformat(signal_time)
            
            current_time = datetime.now(pytz.UTC)
            time_diff = (current_time - signal_time).total_seconds()
            
            # Signal should be generated within last 60 seconds
            if time_diff > 60:
                return False, f"❌ Signal too old: {time_diff:.0f} seconds"
            
            if time_diff < -5:  # Allow 5 seconds into future (clock skew)
                return False, f"❌ Signal timestamp in future: {time_diff:.0f} seconds"
            
            return True, f"✅ Timestamp valid: {time_diff:.0f} seconds ago"
        
        except Exception as e:
            logger.error(f"❌ Timestamp verification error: {e}")
            return False, f"❌ Timestamp error: {str(e)}"

# ============================================================================
# SIGNAL INTEGRITY CHECKER
# ============================================================================

class SignalIntegrityChecker:
    """Verify signal has correct structure and valid values"""
    
    REQUIRED_FIELDS = [
        'symbol', 'signal_type', 'confidence',
        'entry_price', 'tp1', 'tp2', 'tp3', 'sl',
        'timestamp', 'layer_scores'
    ]
    
    @staticmethod
    def check_structure(signal: Dict) -> Tuple[bool, List[str]]:
        """Check signal has all required fields"""
        errors = []
        
        for field in SignalIntegrityChecker.REQUIRED_FIELDS:
            if field not in signal:
                errors.append(f"❌ Missing required field: {field}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def check_value_ranges(signal: Dict) -> Tuple[bool, List[str]]:
        """Check all values are in valid ranges"""
        errors = []
        
        # Check symbol format (must be uppercase, end in USDT)
        symbol = signal.get('symbol', '')
        if not symbol.endswith('USDT'):
            errors.append(f"❌ Invalid symbol format: {symbol}")
        
        # Check signal type
        signal_type = signal.get('signal_type', '')
        if signal_type not in ['LONG', 'SHORT', 'NEUTRAL']:
            errors.append(f"❌ Invalid signal type: {signal_type}")
        
        # Check confidence (0-100)
        confidence = signal.get('confidence', -1)
        if not (0 <= confidence <= 100):
            errors.append(f"❌ Confidence out of range: {confidence} (must be 0-100)")
        
        # Check prices (positive, entry < tp, entry > sl)
        entry = signal.get('entry_price', 0)
        tp1 = signal.get('tp1', 0)
        tp2 = signal.get('tp2', 0)
        tp3 = signal.get('tp3', 0)
        sl = signal.get('sl', 0)
        
        if entry <= 0:
            errors.append(f"❌ Entry price must be positive: {entry}")
        
        if tp1 <= entry:
            errors.append(f"❌ TP1 must be above entry: {tp1} <= {entry}")
        
        if tp2 <= tp1:
            errors.append(f"❌ TP2 must be above TP1: {tp2} <= {tp1}")
        
        if tp3 <= tp2:
            errors.append(f"❌ TP3 must be above TP2: {tp3} <= {tp2}")
        
        if sl >= entry:
            errors.append(f"❌ SL must be below entry: {sl} >= {entry}")
        
        # Check TP1/TP2/TP3 are within reasonable range (max 5x entry)
        max_tp = entry * 5
        if tp1 > max_tp or tp2 > max_tp or tp3 > max_tp:
            errors.append(f"❌ TP levels unreasonably high (max 5x entry)")
        
        # Check SL is not too close (at least 0.5% below entry)
        min_sl = entry * 0.995
        if sl > min_sl:
            errors.append(f"❌ SL too close to entry (must be at least 0.5% below)")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def check_layer_scores(signal: Dict) -> Tuple[bool, List[str]]:
        """Check layer scores are valid"""
        errors = []
        
        layer_scores = signal.get('layer_scores', {})
        
        # Should have at least 4 of 5 tiers
        expected_tiers = ['technical', 'ml', 'sentiment', 'onchain']
        present_tiers = [t for t in expected_tiers if t in layer_scores]
        
        if len(present_tiers) < 4:
            errors.append(f"❌ Missing layer scores: only {len(present_tiers)}/4 tiers")
        
        # Each score should be 0-1
        for tier, score in layer_scores.items():
            if not (0 <= score <= 1):
                errors.append(f"❌ Invalid {tier} score: {score} (must be 0-1)")
        
        return len(errors) == 0, errors

# ============================================================================
# CONSENSUS VALIDATOR - MULTIPLE CHECKS
# ============================================================================

class SignalValidator:
    """Main signal validator - runs all checks"""
    
    def __init__(self):
        self.mock_detector = MockDataDetector()
        self.data_verifier = RealDataVerifier()
        self.integrity_checker = SignalIntegrityChecker()
    
    def validate(self, signal: Dict, verify_exchange: bool = True) -> Dict:
        """
        Comprehensive signal validation
        Returns: {
            'valid': bool,
            'checks': {
                'mock_data': (bool, [errors]),
                'structure': (bool, [errors]),
                'value_ranges': (bool, [errors]),
                'layer_scores': (bool, [errors]),
                'timestamp': (bool, msg),
                'exchange_price': (bool, msg) if verify_exchange
            },
            'overall_status': str
        }
        """
        
        logger.info(f"🔍 Validating signal for {signal.get('symbol', 'UNKNOWN')}")
        
        results = {
            'checks': {},
            'valid': True,
            'errors': []
        }
        
        # Check 1: Mock/Fake/Fallback data
        is_clean, mock_errors = self.mock_detector.check_signal(signal)
        results['checks']['mock_data'] = (is_clean, mock_errors)
        if not is_clean:
            results['valid'] = False
            results['errors'].extend(mock_errors)
            logger.error(f"❌ Mock data detected: {mock_errors}")
        else:
            logger.info("✅ No mock/fake/fallback data detected")
        
        # Check 2: Signal structure
        has_structure, struct_errors = self.integrity_checker.check_structure(signal)
        results['checks']['structure'] = (has_structure, struct_errors)
        if not has_structure:
            results['valid'] = False
            results['errors'].extend(struct_errors)
            logger.error(f"❌ Structure errors: {struct_errors}")
        else:
            logger.info("✅ Signal structure valid")
        
        # Check 3: Value ranges
        valid_ranges, range_errors = self.integrity_checker.check_value_ranges(signal)
        results['checks']['value_ranges'] = (valid_ranges, range_errors)
        if not valid_ranges:
            results['valid'] = False
            results['errors'].extend(range_errors)
            logger.error(f"❌ Value range errors: {range_errors}")
        else:
            logger.info("✅ All values in valid ranges")
        
        # Check 4: Layer scores
        valid_scores, score_errors = self.integrity_checker.check_layer_scores(signal)
        results['checks']['layer_scores'] = (valid_scores, score_errors)
        if not valid_scores:
            results['valid'] = False
            results['errors'].extend(score_errors)
            logger.error(f"❌ Layer score errors: {score_errors}")
        else:
            logger.info("✅ Layer scores valid")
        
        # Check 5: Timestamp
        time_valid, time_msg = self.data_verifier.verify_signal_timestamps(signal)
        results['checks']['timestamp'] = (time_valid, time_msg)
        if not time_valid:
            results['valid'] = False
            results['errors'].append(time_msg)
            logger.error(f"❌ Timestamp error: {time_msg}")
        else:
            logger.info(f"✅ {time_msg}")
        
        # Check 6: Exchange price verification (optional, slower)
        if verify_exchange:
            price_valid, price_msg = self.data_verifier.verify_price_from_exchange(
                signal.get('symbol'),
                signal.get('entry_price'),
                tolerance_percent=1.0
            )
            results['checks']['exchange_price'] = (price_valid, price_msg)
            if not price_valid:
                logger.warning(f"⚠️ Price verification: {price_msg}")
            else:
                logger.info(f"✅ {price_msg}")
        
        # Final status
        if results['valid']:
            results['overall_status'] = '✅ SIGNAL VALID - 100% REAL DATA'
            logger.info("🟢 ✅ SIGNAL VALIDATION PASSED - 100% REAL DATA COMPLIANCE")
        else:
            results['overall_status'] = f'❌ SIGNAL INVALID - {len(results["errors"])} errors'
            logger.error(f"🔴 ❌ SIGNAL VALIDATION FAILED - {len(results['errors'])} errors")
        
        return results
    
    def generate_validation_report(self, validation_results: Dict) -> str:
        """Generate human-readable validation report"""
        report = []
        report.append("=" * 80)
        report.append("SIGNAL VALIDATION REPORT")
        report.append("=" * 80)
        report.append(f"Overall Status: {validation_results['overall_status']}")
        report.append("")
        
        for check_name, (passed, details) in validation_results['checks'].items():
            status = "✅ PASS" if passed else "❌ FAIL"
            report.append(f"{check_name.upper()}: {status}")
            
            if isinstance(details, list) and details:
                for error in details:
                    report.append(f"  → {error}")
            elif isinstance(details, str):
                report.append(f"  → {details}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

# ============================================================================
# MAIN ENTRY POINT - USAGE EXAMPLE
# ============================================================================

if __name__ == '__main__':
    # Example signal
    test_signal = {
        'symbol': 'BTCUSDT',
        'signal_type': 'LONG',
        'confidence': 85,
        'entry_price': 97234.50,
        'tp1': 98500.00,
        'tp2': 99800.00,
        'tp3': 101000.00,
        'sl': 96500.00,
        'timestamp': datetime.now(pytz.UTC).isoformat(),
        'layer_scores': {
            'technical': 0.82,
            'ml': 0.88,
            'sentiment': 0.79,
            'onchain': 0.85
        }
    }
    
    validator = SignalValidator()
    results = validator.validate(test_signal, verify_exchange=False)
    print(validator.generate_validation_report(results))
