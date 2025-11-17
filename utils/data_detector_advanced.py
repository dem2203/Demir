"""
DEMIR AI BOT - Data Detector Advanced
Mock/fake/fallback data detection engine
Comprehensive anomaly detection for data integrity
"""

import logging
from typing import Any, Dict, List, Tuple, Optional
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


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
        """Initialize data detector."""
        self.detected_issues: List[str] = []

    def is_mock_data(self, value: Any) -> bool:
        """Check if value appears to be mock data."""
        if not isinstance(value, str):
            return False

        value_lower = value.lower()

        for pattern in self.MOCK_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True

        return False

    def is_fallback_data(self, value: Any) -> bool:
        """Check if value appears to be fallback data."""
        if not isinstance(value, str):
            return False

        value_lower = value.lower()

        for indicator in self.FALLBACK_INDICATORS:
            if indicator in value_lower:
                return True

        return False

    def is_test_data(self, value: Any) -> bool:
        """Check if value appears to be test data."""
        if isinstance(value, str):
            return 'test' in value.lower()
        return False

    def is_hardcoded_data(self, value: Any, context: Optional[str] = None) -> bool:
        """Check if value appears to be hardcoded."""
        if not isinstance(value, (str, int, float)):
            return False

        if isinstance(value, str):
            # Check for hardcoded patterns
            if value in ['0', '-1', '999999', '1.0']:
                return True
            if len(value) > 100:  # Likely real data
                return False
            if context and 'hardcoded' in context.lower():
                return True

        return False

    def detect_suspicious_patterns(self, data: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Detect suspicious patterns in data dictionary."""
        issues = []

        for key, value in data.items():
            # Check each field for indicators
            if self.is_mock_data(value):
                issues.append((key, "Mock data detected"))

            if self.is_fallback_data(value):
                issues.append((key, "Fallback data detected"))

            if self.is_test_data(value):
                issues.append((key, "Test data detected"))

            if self.is_hardcoded_data(value):
                issues.append((key, "Hardcoded data detected"))

        return issues

    def verify_price_sanity(self, price: float, symbol: str) -> Tuple[bool, str]:
        """Verify price sanity (not obviously fake)."""
        if price <= 0:
            return False, "Price must be positive"

        if price > 1_000_000:
            # Check if it's a real altcoin with decimals
            if symbol.upper() in ['SHIB', 'DOGE', 'PEPE']:
                return True, "OK"
            return False, "Price seems unrealistically high"

        if symbol.upper() in ['BTC', 'ETH'] and price < 100:
            return False, "BTC/ETH prices are unrealistically low"

        return True, "OK"

    def verify_timestamp_sanity(self, timestamp: float) -> Tuple[bool, str]:
        """Verify timestamp is recent and reasonable."""
        now = datetime.now().timestamp()

        # Check if timestamp is in future
        if timestamp > now:
            return False, "Timestamp is in the future"

        # Check if timestamp is more than 1 year old (for active trading)
        one_year_ago = now - (365 * 24 * 3600)
        if timestamp < one_year_ago:
            return False, "Timestamp is older than 1 year"

        return True, "OK"

    def check_data_completeness(
        self,
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> Tuple[bool, List[str]]:
        """Check if data has all required fields."""
        missing = []

        for field in required_fields:
            if field not in data or data[field] is None:
                missing.append(field)

        if missing:
            return False, missing

        return True, []

    def detect_all_issues(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive data quality check."""
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

        return issues
