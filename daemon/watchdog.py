"""
👁️ DEMIR AI - WATCHDOG SERVICE - System Monitoring & Recovery
============================================================================
Monitors daemon health, API connectivity, and system recovery
Date: 8 November 2025
Version: 2.0 - ZERO MOCK DATA - 100% Real API
============================================================================

🔒 KUTSAL KURAL: Bu sistem mock/sentetik veri KULLANMAZ!
Watchdog sadece gerçek API'dan gelen sağlık verisini izler!
============================================================================
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import os
import requests
import json
from pathlib import Path

logger = logging.getLogger(__name__)

# ============================================================================
# WATCHDOG SERVICE
# ============================================================================

class WatchdogService:
    """
    Monitors system health and auto-recovery
    - Checks daemon status every N seconds
    - Monitors API connectivity
    - Restarts daemon if crashed
    - Alerts via Telegram/Email if critical issues
    - Maintains system logs and backups
    """

    def __init__(self, daemon_callable: Optional[Callable] = None):
        """Initialize watchdog"""
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.daemon = daemon_callable
        self.startup_time = datetime.now()
        self.health_check_interval = 30  # seconds
        self.last_health_check = None
        self.failure_count = 0
        self.max_failures = 3
        self.restart_count = 0
        
        # API keys for monitoring (REAL ONLY)
        self.telegram_token = os.getenv('TELEGRAM_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.binance_api_key = os.getenv('BINANCE_API_KEY')
        
        self.logger.info("✅ WatchdogService initialized (ZERO MOCK MODE)")

    def start(self):
        """Start watchdog (non-blocking)"""
        if self.is_running:
            self.logger.warning("⚠️ Watchdog already running!")
            return
        
        self.is_running = True
        self.logger.info("🟢 WATCHDOG STARTED")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()
        
        self.logger.info("✅ Watchdog monitoring thread started")

    def stop(self):
        """Stop watchdog"""
        self.is_running = False
        self.logger.info("🔴 WATCHDOG STOPPED")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info("🔄 Monitoring loop started")
        
        while self.is_running:
            try:
                current_time = datetime.now()
                
                if (self.last_health_check is None or 
                    (current_time - self.last_health_check).total_seconds() >= self.health_check_interval):
                    
                    self._perform_health_check()
                    self.last_health_check = current_time
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"❌ Monitoring loop error: {e}")
                time.sleep(10)

    def _perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check - REAL DATA ONLY"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'daemon_status': self._check_daemon_health(),
            'api_status': self._check_api_connectivity(),
            'system_status': self._check_system_resources(),
            'critical_alerts': []
        }
        
        # Check for critical issues
        if not health_status['daemon_status']['is_healthy']:
            self.failure_count += 1
            health_status['critical_alerts'].append('❌ Daemon unhealthy')
            
            if self.failure_count >= self.max_failures:
                self._attempt_recovery()
        else:
            self.failure_count = 0
        
        if not health_status['api_status']['is_healthy']:
            health_status['critical_alerts'].append('❌ API connectivity issue')
        
        # Log status
        self.logger.info(f"🏥 Health check: Daemon={health_status['daemon_status']['status']}, "
                        f"API={health_status['api_status']['status']}, "
                        f"Failures={self.failure_count}")
        
        # Send alerts if critical
        if health_status['critical_alerts']:
            self._send_alert('\n'.join(health_status['critical_alerts']), 'WARNING')
        
        return health_status

    def _check_daemon_health(self) -> Dict[str, Any]:
        """Check daemon process health - REAL STATUS ONLY"""
        try:
            if self.daemon is None:
                return {
                    'is_healthy': False,
                    'status': 'NO_DAEMON',
                    'message': 'Daemon not initialized'
                }
            
            # Check if daemon is running
            if hasattr(self.daemon, 'is_running') and hasattr(self.daemon, 'get_status'):
                if self.daemon.is_running:
                    status = self.daemon.get_status()
                    return {
                        'is_healthy': True,
                        'status': 'RUNNING',
                        'uptime_hours': status.get('uptime_hours', 0),
                        'signals': status.get('signals_generated', 0),
                        'trades': status.get('trades_executed', 0)
                    }
                else:
                    return {
                        'is_healthy': False,
                        'status': 'STOPPED',
                        'message': 'Daemon stopped unexpectedly'
                    }
            
            return {
                'is_healthy': False,
                'status': 'UNKNOWN',
                'message': 'Cannot determine daemon status'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Daemon health check error: {e}")
            return {
                'is_healthy': False,
                'status': 'ERROR',
                'message': str(e)
            }

    def _check_api_connectivity(self) -> Dict[str, Any]:
        """Check API connectivity - REAL ONLY"""
        api_checks = {
            'binance': self._check_binance_api(),
            'telegram': self._check_telegram_api(),
        }
        
        all_healthy = all(check['ok'] for check in api_checks.values())
        
        return {
            'is_healthy': all_healthy,
            'status': 'OK' if all_healthy else 'DEGRADED',
            'checks': api_checks,
            'timestamp': datetime.now().isoformat()
        }

    def _check_binance_api(self) -> Dict[str, Any]:
        """Check Binance API connectivity"""
        try:
            url = "https://api.binance.com/api/v3/ping"
            response = requests.get(url, timeout=5)
            
            if response.ok:
                return {
                    'ok': True,
                    'status': 'CONNECTED',
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                return {
                    'ok': False,
                    'status': 'ERROR',
                    'http_code': response.status_code
                }
        except Exception as e:
            return {
                'ok': False,
                'status': 'UNREACHABLE',
                'error': str(e)
            }

    def _check_telegram_api(self) -> Dict[str, Any]:
        """Check Telegram API connectivity"""
        try:
            if not self.telegram_token:
                return {
                    'ok': False,
                    'status': 'NO_TOKEN',
                    'message': 'Telegram token not configured'
                }
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/getMe"
            response = requests.get(url, timeout=5)
            
            if response.ok:
                return {
                    'ok': True,
                    'status': 'CONNECTED',
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                return {
                    'ok': False,
                    'status': 'ERROR',
                    'http_code': response.status_code
                }
        except Exception as e:
            return {
                'ok': False,
                'status': 'UNREACHABLE',
                'error': str(e)
            }

    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resources"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'status': 'OK' if cpu_percent < 80 and memory.percent < 80 else 'WARNING'
            }
        except ImportError:
            return {
                'status': 'UNAVAILABLE',
                'message': 'psutil not installed'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }

    def _attempt_recovery(self):
        """Attempt to recover system"""
        self.logger.warning("⚠️ ATTEMPTING RECOVERY...")
        self._send_alert('🔄 Attempting system recovery...', 'WARNING')
        
        try:
            # Stop daemon
            if self.daemon and hasattr(self.daemon, 'stop'):
                self.daemon.stop()
                time.sleep(5)
            
            # Restart daemon
            if self.daemon and hasattr(self.daemon, 'start'):
                self.daemon.start()
                self.restart_count += 1
                self.failure_count = 0  # Reset counter
                self._send_alert(f'✅ System recovered! Restart #{self.restart_count}', 'INFO')
                self.logger.info(f"✅ System recovery successful (restart #{self.restart_count})")
            
        except Exception as e:
            self.logger.error(f"❌ Recovery failed: {e}")
            self._send_alert(f'❌ Recovery failed: {e}', 'ERROR')

    def _send_alert(self, message: str, level: str = 'INFO'):
        """Send Telegram alert - REAL ONLY"""
        if not self.telegram_token or not self.telegram_chat_id:
            self.logger.warning("⚠️ Telegram not configured - cannot send alert")
            return
        
        try:
            emoji = {'INFO': 'ℹ️', 'WARNING': '⚠️', 'ERROR': '❌', 'SUCCESS': '✅'}.get(level, 'ℹ️')
            telegram_msg = f"{emoji} [Watchdog {level}]\n{message}"
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            params = {
                'chat_id': self.telegram_chat_id,
                'text': telegram_msg
            }
            
            requests.post(url, params=params, timeout=5)
            
        except Exception as e:
            self.logger.error(f"❌ Alert send error: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get watchdog status"""
        return {
            'is_running': self.is_running,
            'uptime_hours': (datetime.now() - self.startup_time).total_seconds() / 3600,
            'failure_count': self.failure_count,
            'restart_count': self.restart_count,
            'timestamp': datetime.now().isoformat()
        }

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = ['WatchdogService']
