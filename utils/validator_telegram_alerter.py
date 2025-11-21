#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📢 DEMIR AI v8.0 - VALIDATOR TELEGRAM ALERTER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REAL-TIME VALIDATOR ALERT SYSTEM

Integrates with all data validators to provide instant notifications:
    ✅ Mock data detection alerts
    ✅ Validation failure notifications
    ✅ Cross-validation error alerts
    ✅ Severity-based message routing
    ✅ Rate limiting to prevent spam
    ✅ Professional message formatting
    ✅ Integration with existing Telegram infrastructure

ALERT SEVERITY LEVELS:
    🚨 CRITICAL  - Mock data detected, system integrity violated
    ⚠️  WARNING   - Validation warnings, high volatility
    ℹ️  INFO      - Successful validations, statistics

FEATURES:
    - Smart rate limiting (max 1 alert per minute per type)
    - Detailed validation context in messages
    - Statistics and trends reporting
    - Integration with GlobalState validator metrics
    - Professional Telegram message formatting

DEPLOYMENT: Railway Production
AUTHOR: DEMIR AI Research Team
DATE: 2025-11-21
VERSION: 8.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================================================
# ALERT SEVERITY ENUM
# ============================================================================

class AlertSeverity(Enum):
    """Alert severity levels for validation events"""
    CRITICAL = "CRITICAL"  # Mock data, system integrity violations
    WARNING = "WARNING"    # Validation warnings, anomalies
    INFO = "INFO"          # Successful validations, statistics
    DEBUG = "DEBUG"        # Detailed debugging information

# ============================================================================
# VALIDATOR TELEGRAM ALERTER
# ============================================================================

class ValidatorTelegramAlerter:
    """
    Enterprise-grade Telegram alerting system for data validators
    
    Features:
    - Real-time validation failure alerts
    - Mock data detection notifications
    - Smart rate limiting (prevents spam)
    - Severity-based message formatting
    - Statistics reporting
    - Integration with existing Telegram infrastructure
    """
    
    def __init__(
        self,
        telegram_bot_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None,
        enabled: bool = True
    ):
        """
        Initialize Telegram alerter
        
        Args:
            telegram_bot_token: Telegram bot token (from env or param)
            telegram_chat_id: Telegram chat ID (from env or param)
            enabled: Enable/disable alerts
        """
        self.enabled = enabled and bool(os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true')
        
        self.bot_token = telegram_bot_token or os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = telegram_chat_id or os.getenv('TELEGRAM_CHAT_ID', '')
        
        # Rate limiting configuration
        self.rate_limit_window = 60  # seconds
        self.max_alerts_per_window = 5
        self.alert_timestamps: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Alert statistics
        self.stats = {
            'total_alerts_sent': 0,
            'alerts_by_severity': {
                'CRITICAL': 0,
                'WARNING': 0,
                'INFO': 0,
                'DEBUG': 0
            },
            'rate_limited_alerts': 0,
            'failed_sends': 0
        }
        
        # Alert history
        self.alert_history = deque(maxlen=1000)
        
        if self.enabled and self.bot_token and self.chat_id:
            logger.info(
                f"✅ ValidatorTelegramAlerter initialized | "
                f"Status: ENABLED | "
                f"Rate limit: {self.max_alerts_per_window} per {self.rate_limit_window}s"
            )
        else:
            logger.info(
                f"⚠️  ValidatorTelegramAlerter initialized | "
                f"Status: DISABLED | "
                f"Reason: {'Not enabled' if not self.enabled else 'Missing credentials'}"
            )
    
    def send_mock_data_alert(
        self,
        validator_name: str,
        detection_details: Dict[str, Any]
    ) -> bool:
        """
        Send alert for mock data detection (CRITICAL)
        
        Args:
            validator_name: Name of validator that detected mock data
            detection_details: Details about detection (pattern, value, etc.)
        
        Returns:
            True if sent successfully
        """
        message = self._format_mock_data_alert(validator_name, detection_details)
        return self._send_alert(
            message=message,
            severity=AlertSeverity.CRITICAL,
            alert_type='mock_data_detected'
        )
    
    def send_validation_failure_alert(
        self,
        validator_name: str,
        symbol: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send alert for validation failure
        
        Args:
            validator_name: Name of validator
            symbol: Trading symbol
            reason: Failure reason
            details: Additional details
        
        Returns:
            True if sent successfully
        """
        message = self._format_validation_failure_alert(
            validator_name, symbol, reason, details
        )
        return self._send_alert(
            message=message,
            severity=AlertSeverity.WARNING,
            alert_type='validation_failure'
        )
    
    def send_cross_validation_failure_alert(
        self,
        symbol: str,
        reported_price: float,
        live_price: float,
        deviation: float,
        exchange: str
    ) -> bool:
        """
        Send alert for cross-validation failure
        
        Args:
            symbol: Trading symbol
            reported_price: Price from data source
            live_price: Price from exchange API
            deviation: Percentage deviation
            exchange: Exchange name
        
        Returns:
            True if sent successfully
        """
        message = (
            f"🚨 CROSS-VALIDATION FAILURE\n\n"
            f"📊 Symbol: {symbol}\n"
            f"💰 Reported: ${reported_price:.2f}\n"
            f"✅ Live ({exchange}): ${live_price:.2f}\n"
            f"⚠️  Deviation: {deviation*100:.2f}%\n"
            f"🔒 Status: DATA REJECTED\n"
            f"🕔 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        return self._send_alert(
            message=message,
            severity=AlertSeverity.CRITICAL,
            alert_type='cross_validation_failure'
        )
    
    def send_statistics_report(
        self,
        validator_stats: Dict[str, Any]
    ) -> bool:
        """
        Send periodic statistics report
        
        Args:
            validator_stats: Statistics from GlobalState
        
        Returns:
            True if sent successfully
        """
        message = self._format_statistics_report(validator_stats)
        return self._send_alert(
            message=message,
            severity=AlertSeverity.INFO,
            alert_type='statistics_report',
            skip_rate_limit=False  # Allow rate limiting for stats
        )
    
    def _send_alert(
        self,
        message: str,
        severity: AlertSeverity,
        alert_type: str,
        skip_rate_limit: bool = False
    ) -> bool:
        """
        Send Telegram alert with rate limiting
        
        Args:
            message: Alert message
            severity: Alert severity
            alert_type: Type of alert (for rate limiting)
            skip_rate_limit: Skip rate limiting check (for critical alerts)
        
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            logger.debug(f"Telegram alerts disabled - skipping {alert_type} alert")
            return False
        
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials missing - cannot send alert")
            return False
        
        # Check rate limiting (unless skipped for critical alerts)
        if not skip_rate_limit and severity != AlertSeverity.CRITICAL:
            if self._is_rate_limited(alert_type):
                self.stats['rate_limited_alerts'] += 1
                logger.debug(
                    f"Alert rate limited | Type: {alert_type} | "
                    f"Limit: {self.max_alerts_per_window} per {self.rate_limit_window}s"
                )
                return False
        
        # Send to Telegram
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                self.stats['total_alerts_sent'] += 1
                self.stats['alerts_by_severity'][severity.value] += 1
                
                # Record alert
                self.alert_history.append({
                    'type': alert_type,
                    'severity': severity.value,
                    'message_preview': message[:100],
                    'timestamp': datetime.now(),
                    'status': 'sent'
                })
                
                # Update rate limiting tracker
                self.alert_timestamps[alert_type].append(time.time())
                
                logger.info(
                    f"✅ Telegram alert sent | "
                    f"Type: {alert_type} | "
                    f"Severity: {severity.value} | "
                    f"Total sent: {self.stats['total_alerts_sent']}"
                )
                return True
            else:
                self.stats['failed_sends'] += 1
                logger.error(
                    f"❌ Telegram send failed | "
                    f"Status: {response.status_code} | "
                    f"Response: {response.text[:100]}"
                )
                return False
                
        except Exception as e:
            self.stats['failed_sends'] += 1
            logger.error(f"❌ Telegram alert exception: {e}")
            return False
    
    def _is_rate_limited(self, alert_type: str) -> bool:
        """
        Check if alert type is rate limited
        
        Args:
            alert_type: Type of alert
        
        Returns:
            True if rate limited
        """
        current_time = time.time()
        
        # Clean old timestamps outside window
        self.alert_timestamps[alert_type] = deque(
            (ts for ts in self.alert_timestamps[alert_type] 
             if current_time - ts < self.rate_limit_window),
            maxlen=100
        )
        
        # Check if we've hit the limit
        return len(self.alert_timestamps[alert_type]) >= self.max_alerts_per_window
    
    def _format_mock_data_alert(
        self,
        validator_name: str,
        details: Dict[str, Any]
    ) -> str:
        """
        Format mock data detection alert message
        
        Args:
            validator_name: Validator name
            details: Detection details
        
        Returns:
            Formatted message
        """
        pattern = details.get('pattern', 'unknown')
        value = str(details.get('value', ''))[:50]
        source = details.get('source', 'unknown')
        total_detections = details.get('total_detections', 0)
        
        message = (
            f"🚨 <b>MOCK DATA DETECTED</b> 🚨\n\n"
            f"🔍 <b>Validator:</b> {validator_name}\n"
            f"🎯 <b>Pattern:</b> {pattern}\n"
            f"📝 <b>Value:</b> {value}...\n"
            f"🌐 <b>Source:</b> {source}\n"
            f"📈 <b>Total Detections:</b> {total_detections}\n\n"
            f"❌ <b>Action:</b> DATA REJECTED\n"
            f"🔒 <b>Policy:</b> ZERO MOCK DATA ENFORCEMENT\n"
            f"🕔 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        
        return message
    
    def _format_validation_failure_alert(
        self,
        validator_name: str,
        symbol: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format validation failure alert message
        
        Args:
            validator_name: Validator name
            symbol: Trading symbol
            reason: Failure reason
            details: Additional details
        
        Returns:
            Formatted message
        """
        message = (
            f"⚠️  <b>VALIDATION FAILURE</b>\n\n"
            f"🔍 <b>Validator:</b> {validator_name}\n"
            f"📊 <b>Symbol:</b> {symbol}\n"
            f"❌ <b>Reason:</b> {reason}\n"
        )
        
        if details:
            price = details.get('price')
            exchange = details.get('exchange')
            
            if price:
                message += f"💰 <b>Price:</b> ${price:.2f}\n"
            if exchange:
                message += f"🌐 <b>Exchange:</b> {exchange}\n"
        
        message += f"\n🕔 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        
        return message
    
    def _format_statistics_report(self, stats: Dict[str, Any]) -> str:
        """
        Format statistics report message
        
        Args:
            stats: Validator statistics from GlobalState
        
        Returns:
            Formatted message
        """
        overall = stats.get('overall', {})
        validators = stats.get('validators', {})
        
        message = (
            f"📈 <b>VALIDATOR STATISTICS REPORT</b>\n\n"
            f"📊 <b>Overall Performance:</b>\n"
            f"  • Total Checks: {overall.get('total_checks', 0):,}\n"
            f"  • Passed: {overall.get('passed_checks', 0):,}\n"
            f"  • Failed: {overall.get('failed_checks', 0):,}\n"
            f"  • Success Rate: {overall.get('average_success_rate', 0):.2f}%\n"
            f"  • Mock Detected: {overall.get('mock_detected_total', 0)}\n\n"
        )
        
        # Add top 3 validators
        message += f"🏆 <b>Top Validators:</b>\n"
        sorted_validators = sorted(
            validators.items(),
            key=lambda x: x[1].get('total_checks', 0),
            reverse=True
        )[:3]
        
        for idx, (name, v_stats) in enumerate(sorted_validators, 1):
            status_emoji = "✅" if v_stats.get('status') == 'healthy' else "⚠️ "
            message += (
                f"  {idx}. {status_emoji} {name}: "
                f"{v_stats.get('success_rate', 0):.1f}% "
                f"({v_stats.get('total_checks', 0):,} checks)\n"
            )
        
        message += f"\n🕔 {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        
        return message
    
    def get_alerter_statistics(self) -> Dict[str, Any]:
        """
        Get alerter statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            'enabled': self.enabled,
            'stats': dict(self.stats),
            'recent_alerts': [
                {
                    'type': alert['type'],
                    'severity': alert['severity'],
                    'timestamp': alert['timestamp'].isoformat() if isinstance(alert['timestamp'], datetime) else alert['timestamp'],
                    'status': alert['status']
                }
                for alert in list(self.alert_history)[-20:]
            ],
            'rate_limit_config': {
                'window_seconds': self.rate_limit_window,
                'max_alerts_per_window': self.max_alerts_per_window
            }
        }

# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_global_alerter = None

def get_alerter() -> ValidatorTelegramAlerter:
    """Get global alerter instance (singleton pattern)"""
    global _global_alerter
    if _global_alerter is None:
        _global_alerter = ValidatorTelegramAlerter()
        logger.info("✅ Global ValidatorTelegramAlerter instance created (singleton)")
    return _global_alerter

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def alert_mock_data_detected(
    validator_name: str,
    detection_details: Dict[str, Any]
) -> bool:
    """Quick function to send mock data alert"""
    alerter = get_alerter()
    return alerter.send_mock_data_alert(validator_name, detection_details)

def alert_validation_failure(
    validator_name: str,
    symbol: str,
    reason: str,
    details: Optional[Dict[str, Any]] = None
) -> bool:
    """Quick function to send validation failure alert"""
    alerter = get_alerter()
    return alerter.send_validation_failure_alert(validator_name, symbol, reason, details)

def alert_cross_validation_failure(
    symbol: str,
    reported_price: float,
    live_price: float,
    deviation: float,
    exchange: str
) -> bool:
    """Quick function to send cross-validation failure alert"""
    alerter = get_alerter()
    return alerter.send_cross_validation_failure_alert(
        symbol, reported_price, live_price, deviation, exchange
    )
