"""
DEMIR AI BOT - Data Detector Advanced
Mock/fake/fallback data detection engine
Comprehensive anomaly detection for data integrity

v8.0 Enhancement: Advanced Logging & Real-time Alerting
- Detailed detection event logging
- Pattern matching comprehensive tracking
- Telegram alert integration hooks
- Validation failure context logging
- Enterprise-grade monitoring support
"""

import logging
from typing import Any, Dict, List, Tuple, Optional
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Create specialized logger for mock data detection events
mock_detection_logger = logging.getLogger('MOCK_DATA_DETECTOR')
mock_detection_logger.setLevel(logging.INFO)


class DataDetector:
    """Detects mock, fake, fallback, and test data patterns."""

    MOCK_PATTERNS = [
        r'^mock',
        r'test_',
        r'_test$',
        r'^fake',
        r'placeholder',
        r'sample_',
        r'^dummy',
        r'lorem_ipsum',
        r'example\.com',
        r'\$\{.*?\}',  # Template variables
    ]

    FALLBACK_INDICATORS = [
        'fallback',
        'default_value',
        'na_value',
        'null_value',
        'undefined',
        'pending',
        'not_available',
    ]

    SUSPICIOUS_VALUES = [
        0,
        '0.0',
        -1,
        99999,
        999999,
        1.0,
        '1.0',
    ]

    def __init__(self):
        """Initialize data detector with enhanced logging."""
        self.detected_issues: List[str] = []
        self.detection_count = {
            'mock': 0,
            'fake': 0,
            'fallback': 0,
            'test': 0,
            'hardcoded': 0,
            'suspicious': 0
        }
        self.validation_history: List[Dict[str, Any]] = []
        
        mock_detection_logger.info(
            "✅ DataDetector initialized with enhanced logging | "
            f"Patterns: {len(self.MOCK_PATTERNS)} mock, {len(self.FALLBACK_INDICATORS)} fallback, "
            f"{len(self.SUSPICIOUS_VALUES)} suspicious values"
        )

    def is_mock_data(self, value: Any) -> bool:
        """Check if value appears to be mock data."""
        if not isinstance(value, str):
            return False

        value_lower = value.lower()

        for pattern in self.MOCK_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                self.detection_count['mock'] += 1
                mock_detection_logger.warning(
                    f"🚨 MOCK DATA DETECTED | "
                    f"Pattern: '{pattern}' | "
                    f"Value: '{value[:50]}...' | "
                    f"Total mock detections: {self.detection_count['mock']}"
                )
                
                # Record detection event
                self._record_detection_event(
                    detection_type='MOCK_DATA',
                    pattern=pattern,
                    value=value,
                    severity='HIGH'
                )
                
                return True

        return False

    def is_fallback_data(self, value: Any) -> bool:
        """Check if value appears to be fallback data."""
        if not isinstance(value, str):
            return False

        value_lower = value.lower()

        for indicator in self.FALLBACK_INDICATORS:
            if indicator in value_lower:
                self.detection_count['fallback'] += 1
                mock_detection_logger.warning(
                    f"⚠️  FALLBACK DATA DETECTED | "
                    f"Indicator: '{indicator}' | "
                    f"Value: '{value[:50]}...' | "
                    f"Total fallback detections: {self.detection_count['fallback']}"
                )
                
                # Record detection event
                self._record_detection_event(
                    detection_type='FALLBACK_DATA',
                    pattern=indicator,
                    value=value,
                    severity='MEDIUM'
                )
                
                return True

        return False

    def is_test_data(self, value: Any) -> bool:
        """Check if value appears to be test data."""
        if isinstance(value, str):
            if 'test' in value.lower():
                self.detection_count['test'] += 1
                mock_detection_logger.warning(
                    f"🧪 TEST DATA DETECTED | "
                    f"Value: '{value[:50]}...' | "
                    f"Total test detections: {self.detection_count['test']}"
                )
                
                # Record detection event
                self._record_detection_event(
                    detection_type='TEST_DATA',
                    pattern='test keyword',
                    value=value,
                    severity='HIGH'
                )
                
                return True
        return False

    def is_hardcoded_data(self, value: Any, context: Optional[str] = None) -> bool:
        """Check if value appears to be hardcoded."""
        if not isinstance(value, (str, int, float)):
            return False

        if isinstance(value, str):
            # Check for hardcoded patterns
            if value in ['0', '-1', '999999', '1.0']:
                self.detection_count['hardcoded'] += 1
                mock_detection_logger.warning(
                    f"🔒 HARDCODED DATA DETECTED | "
                    f"Value: '{value}' | "
                    f"Context: {context or 'None'} | "
                    f"Total hardcoded detections: {self.detection_count['hardcoded']}"
                )
                
                # Record detection event
                self._record_detection_event(
                    detection_type='HARDCODED_DATA',
                    pattern='suspicious constant',
                    value=value,
                    severity='MEDIUM',
                    context=context
                )
                
                return True
            if len(value) > 100:  # Likely real data
                return False
            if context and 'hardcoded' in context.lower():
                self.detection_count['hardcoded'] += 1
                mock_detection_logger.warning(
                    f"🔒 HARDCODED DATA (context) | Value: '{value[:30]}...' | Context: {context}"
                )
                return True

        return False

    def detect_suspicious_patterns(self, data: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Detect suspicious patterns in data dictionary."""
        issues = []
        
        mock_detection_logger.info(
            f"🔍 Starting suspicious pattern detection | Fields: {len(data)} | "
            f"Timestamp: {datetime.now().isoformat()}"
        )

        for key, value in data.items():
            # Check each field for indicators
            if self.is_mock_data(value):
                issue = (key, "Mock data detected")
                issues.append(issue)
                mock_detection_logger.error(
                    f"❌ MOCK DATA IN FIELD | Field: '{key}' | Value: '{str(value)[:50]}...'"
                )

            if self.is_fallback_data(value):
                issue = (key, "Fallback data detected")
                issues.append(issue)
                mock_detection_logger.warning(
                    f"⚠️  FALLBACK DATA IN FIELD | Field: '{key}' | Value: '{str(value)[:50]}...'"
                )

            if self.is_test_data(value):
                issue = (key, "Test data detected")
                issues.append(issue)
                mock_detection_logger.error(
                    f"❌ TEST DATA IN FIELD | Field: '{key}' | Value: '{str(value)[:50]}...'"
                )

            if self.is_hardcoded_data(value, context=key):
                issue = (key, "Hardcoded data detected")
                issues.append(issue)
        
        # Log summary
        if issues:
            self.detection_count['suspicious'] += len(issues)
            mock_detection_logger.error(
                f"🚨 SUSPICIOUS PATTERNS SUMMARY | "
                f"Total issues: {len(issues)} | "
                f"Fields affected: {[issue[0] for issue in issues]} | "
                f"Types: {[issue[1] for issue in issues]}"
            )
        else:
            mock_detection_logger.info(
                f"✅ No suspicious patterns detected | Fields checked: {len(data)}"
            )

        return issues

    def verify_price_sanity(self, price: float, symbol: str) -> Tuple[bool, str]:
        """Verify price sanity (not obviously fake)."""
        mock_detection_logger.debug(
            f"🔍 Price sanity check | Symbol: {symbol} | Price: {price}"
        )
        
        if price <= 0:
            mock_detection_logger.error(
                f"❌ INVALID PRICE | Symbol: {symbol} | Price: {price} | Reason: Non-positive value"
            )
            return False, "Price must be positive"

        if price > 1_000_000:
            # Check if it's a real altcoin with decimals
            if symbol.upper() in ['SHIB', 'DOGE', 'PEPE']:
                mock_detection_logger.debug(
                    f"✅ High price OK for micro-cap | Symbol: {symbol} | Price: {price}"
                )
                return True, "OK"
            
            mock_detection_logger.error(
                f"❌ UNREALISTIC PRICE | Symbol: {symbol} | Price: {price} | "
                f"Reason: Exceeds 1,000,000 (not a known micro-cap)"
            )
            return False, "Price seems unrealistically high"

        if symbol.upper() in ['BTC', 'ETH'] and price < 100:
            mock_detection_logger.error(
                f"❌ UNREALISTIC PRICE | Symbol: {symbol} | Price: {price} | "
                f"Reason: BTC/ETH cannot be below $100"
            )
            return False, "BTC/ETH prices are unrealistically low"
        
        mock_detection_logger.debug(
            f"✅ Price sanity verified | Symbol: {symbol} | Price: {price}"
        )
        return True, "OK"

    def verify_timestamp_sanity(self, timestamp: float) -> Tuple[bool, str]:
        """Verify timestamp is recent and reasonable."""
        now = datetime.now().timestamp()
        timestamp_dt = datetime.fromtimestamp(timestamp)
        
        mock_detection_logger.debug(
            f"🔍 Timestamp sanity check | "
            f"Timestamp: {timestamp_dt.isoformat()} | "
            f"Age: {(now - timestamp):.2f}s"
        )

        # Check if timestamp is in future
        if timestamp > now:
            age_future = timestamp - now
            mock_detection_logger.error(
                f"❌ FUTURE TIMESTAMP | "
                f"Timestamp: {timestamp_dt.isoformat()} | "
                f"Current time: {datetime.now().isoformat()} | "
                f"Difference: +{age_future:.2f}s in future"
            )
            return False, "Timestamp is in the future"

        # Check if timestamp is more than 1 year old (for active trading)
        one_year_ago = now - (365 * 24 * 3600)
        if timestamp < one_year_ago:
            age_days = (now - timestamp) / (24 * 3600)
            mock_detection_logger.warning(
                f"⚠️  OLD TIMESTAMP | "
                f"Timestamp: {timestamp_dt.isoformat()} | "
                f"Age: {age_days:.1f} days | "
                f"Threshold: 365 days"
            )
            return False, "Timestamp is older than 1 year"
        
        # Log successful validation
        age_seconds = now - timestamp
        mock_detection_logger.debug(
            f"✅ Timestamp sanity verified | "
            f"Timestamp: {timestamp_dt.isoformat()} | "
            f"Age: {age_seconds:.2f}s | "
            f"Status: Recent & valid"
        )
        
        return True, "OK"

    def check_data_completeness(
        self,
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> Tuple[bool, List[str]]:
        """Check if data has all required fields."""
        mock_detection_logger.debug(
            f"🔍 Data completeness check | "
            f"Required fields: {len(required_fields)} | "
            f"Provided fields: {len(data)}"
        )
        
        missing = []

        for field in required_fields:
            if field not in data or data[field] is None:
                missing.append(field)

        if missing:
            mock_detection_logger.error(
                f"❌ INCOMPLETE DATA | "
                f"Missing fields: {missing} | "
                f"Required: {required_fields} | "
                f"Provided: {list(data.keys())}"
            )
            return False, missing
        
        mock_detection_logger.debug(
            f"✅ Data completeness verified | All {len(required_fields)} required fields present"
        )
        return True, []

    def detect_all_issues(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive data quality check with detailed logging."""
        check_start_time = datetime.now()
        
        mock_detection_logger.info(
            f"🔍 COMPREHENSIVE DATA QUALITY CHECK STARTED | "
            f"Fields: {len(data)} | "
            f"Timestamp: {check_start_time.isoformat()}"
        )
        
        issues = {
            "mock_data_found": False,
            "fallback_data_found": False,
            "test_data_found": False,
            "suspicious_patterns": [],
            "missing_fields": [],
            "anomalies": []
        }

        suspicious = self.detect_suspicious_patterns(data)
        issues["suspicious_patterns"] = suspicious

        for field, message in suspicious:
            if "mock" in message.lower():
                issues["mock_data_found"] = True
            if "fallback" in message.lower():
                issues["fallback_data_found"] = True
            if "test" in message.lower():
                issues["test_data_found"] = True
        
        # Calculate check duration
        check_duration = (datetime.now() - check_start_time).total_seconds() * 1000
        
        # Log comprehensive summary
        if any([issues["mock_data_found"], issues["fallback_data_found"], issues["test_data_found"]]):
            mock_detection_logger.error(
                f"🚨 DATA QUALITY CHECK FAILED | "
                f"Mock: {issues['mock_data_found']} | "
                f"Fallback: {issues['fallback_data_found']} | "
                f"Test: {issues['test_data_found']} | "
                f"Suspicious patterns: {len(suspicious)} | "
                f"Duration: {check_duration:.2f}ms | "
                f"ZERO MOCK DATA POLICY VIOLATED"
            )
            
            # Record detailed validation failure
            self._record_detection_event(
                detection_type='VALIDATION_FAILED',
                pattern='comprehensive_check',
                value=str(issues),
                severity='CRITICAL',
                context=f"Duration: {check_duration:.2f}ms, Fields: {len(data)}"
            )
        else:
            mock_detection_logger.info(
                f"✅ DATA QUALITY CHECK PASSED | "
                f"Fields validated: {len(data)} | "
                f"Duration: {check_duration:.2f}ms | "
                f"Status: Clean"
            )

        return issues
    
    def _record_detection_event(
        self,
        detection_type: str,
        pattern: str,
        value: Any,
        severity: str,
        context: Optional[str] = None
    ) -> None:
        """Record a detection event for historical tracking (NEW v8.0)."""
        event = {
            'type': detection_type,
            'pattern': pattern,
            'value': str(value)[:100],  # Truncate long values
            'severity': severity,
            'context': context,
            'timestamp': datetime.now(),
            'detection_counts': dict(self.detection_count)
        }
        
        self.validation_history.append(event)
        
        # Keep only last 1000 events
        if len(self.validation_history) > 1000:
            self.validation_history = self.validation_history[-1000:]
        
        # Log to file for audit trail
        mock_detection_logger.debug(
            f"📝 Detection event recorded | "
            f"Type: {detection_type} | "
            f"Severity: {severity} | "
            f"Pattern: {pattern} | "
            f"History size: {len(self.validation_history)}"
        )
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get comprehensive detection statistics (NEW v8.0)."""
        return {
            'detection_counts': dict(self.detection_count),
            'total_detections': sum(self.detection_count.values()),
            'validation_history_size': len(self.validation_history),
            'recent_events': self.validation_history[-10:] if self.validation_history else [],
            'timestamp': datetime.now().isoformat()
        }
    
    def reset_stats(self) -> None:
        """Reset detection statistics (NEW v8.0)."""
        mock_detection_logger.info(
            f"🔄 Resetting detection statistics | "
            f"Previous totals: {self.detection_count} | "
            f"History events: {len(self.validation_history)}"
        )
        
        self.detection_count = {
            'mock': 0,
            'fake': 0,
            'fallback': 0,
            'test': 0,
            'hardcoded': 0,
            'suspicious': 0
        }
        self.validation_history = []
        self.detected_issues = []
        
        mock_detection_logger.info("✅ Detection statistics reset complete")


class MockDataDetector(DataDetector):
    """Alias for DataDetector to maintain backward compatibility."""
    pass
