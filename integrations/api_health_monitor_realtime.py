"""
DEMIR AI BOT - API Health Monitor Real-time
Monitor API uptime and health status
Track failures and recovery automatically
"""

import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import time

logger = logging.getLogger(__name__)


class APIHealth:
    """API health tracking and monitoring."""

    def __init__(self, window_seconds: int = 3600):
        """Initialize health monitor."""
        self.window_seconds = window_seconds
        self.api_calls: Dict[str, List[Tuple[float, bool]]] = defaultdict(list)
        self.failures: Dict[str, int] = defaultdict(int)
        self.last_failure: Dict[str, float] = defaultdict(float)

    def record_call(self, api_name: str, success: bool, response_time_ms: float = 0):
        """Record API call result."""
        timestamp = time.time()
        self.api_calls[api_name].append((timestamp, success))

        if not success:
            self.failures[api_name] += 1
            self.last_failure[api_name] = timestamp
            logger.warning(f"API '{api_name}' call failed at {timestamp}")

        # Cleanup old entries
        self._cleanup_old_entries(api_name)

    def _cleanup_old_entries(self, api_name: str):
        """Remove entries older than window."""
        now = time.time()
        cutoff = now - self.window_seconds

        if api_name in self.api_calls:
            self.api_calls[api_name] = [
                (ts, success) for ts, success in self.api_calls[api_name]
                if ts >= cutoff
            ]

    def get_uptime_percentage(self, api_name: str) -> float:
        """Calculate uptime percentage for API."""
        if api_name not in self.api_calls:
            return 100.0

        calls = self.api_calls[api_name]
        if not calls:
            return 100.0

        successful = sum(1 for _, success in calls if success)
        return (successful / len(calls)) * 100

    def get_failure_rate(self, api_name: str) -> float:
        """Get failure rate (0-1)."""
        return 100 - self.get_uptime_percentage(api_name)

    def is_api_healthy(self, api_name: str, min_uptime: float = 95.0) -> bool:
        """Check if API is healthy."""
        return self.get_uptime_percentage(api_name) >= min_uptime

    def get_status_summary(self) -> Dict[str, Dict[str, any]]:
        """Get health status for all APIs."""
        summary = {}

        for api_name in self.api_calls.keys():
            uptime = self.get_uptime_percentage(api_name)
            is_healthy = self.is_api_healthy(api_name)

            summary[api_name] = {
                'uptime_percentage': uptime,
                'is_healthy': is_healthy,
                'failure_count': self.failures.get(api_name, 0),
                'last_failure': self.last_failure.get(api_name, None),
                'total_calls': len(self.api_calls.get(api_name, []))
            }

        return summary

    def get_degraded_apis(self, threshold: float = 90.0) -> List[str]:
        """Get list of APIs with uptime below threshold."""
        degraded = []

        for api_name in self.api_calls.keys():
            if self.get_uptime_percentage(api_name) < threshold:
                degraded.append(api_name)

        return degraded

    def alert_on_failure_spike(self, api_name: str, max_failures: int = 5) -> Tuple[bool, str]:
        """Alert if too many failures in short time."""
        failures = self.failures.get(api_name, 0)

        if failures >= max_failures:
            msg = f"ALERT: API '{api_name}' has {failures} failures"
            logger.error(msg)
            return True, msg

        return False, ""
