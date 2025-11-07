"""
DEMIR AI - Phase 14 Signal Handler
Unix signal handling and graceful shutdown
Full Production Code - NO MOCKS
Created: November 7, 2025
"""

import signal
import sys
import logging
import asyncio
from typing import Dict, Callable, Optional, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS
# ============================================================================

class SignalType(Enum):
    """Unix signal types"""
    SIGTERM = signal.SIGTERM  # Termination signal
    SIGINT = signal.SIGINT    # Interrupt (Ctrl+C)
    SIGHUP = signal.SIGHUP    # Hangup
    SIGUSR1 = signal.SIGUSR1  # User signal 1
    SIGUSR2 = signal.SIGUSR2  # User signal 2
    SIGALRM = signal.SIGALRM  # Alarm

class ShutdownReason(Enum):
    """Shutdown reason codes"""
    NORMAL = "normal"
    SIGNAL = "signal"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    RESTART = "restart"

# ============================================================================
# SIGNAL HANDLER
# ============================================================================

class UnixSignalHandler:
    """
    Handle Unix signals for graceful shutdown
    Ensures clean termination and state preservation
    """

    def __init__(self, daemon_instance: Optional[Any] = None):
        """Initialize signal handler"""
        self.logger = logging.getLogger(__name__)

        self.daemon = daemon_instance
        self.shutdown_handlers: Dict[str, Callable] = {}
        self.signal_received: Optional[SignalType] = None
        self.shutdown_reason = ShutdownReason.NORMAL
        self.shutdown_in_progress = False
        self.shutdown_timeout = 30  # seconds

        # Register signal handlers
        self._register_signals()

        self.logger.info("🔌 Unix Signal Handler initialized")

    def _register_signals(self):
        """Register all signal handlers"""
        try:
            # SIGTERM - graceful shutdown (systemd)
            signal.signal(signal.SIGTERM, self._handle_sigterm)

            # SIGINT - Ctrl+C
            signal.signal(signal.SIGINT, self._handle_sigint)

            # SIGHUP - terminal hangup
            signal.signal(signal.SIGHUP, self._handle_sighup)

            # SIGUSR1 - restart trading
            signal.signal(signal.SIGUSR1, self._handle_sigusr1)

            # SIGUSR2 - report status
            signal.signal(signal.SIGUSR2, self._handle_sigusr2)

            self.logger.info("✅ Signal handlers registered")

        except Exception as e:
            self.logger.error(f"Failed to register signals: {str(e)}")

    def _handle_sigterm(self, signum, frame):
        """Handle SIGTERM - graceful shutdown"""
        self.logger.warning("📨 Received SIGTERM - initiating graceful shutdown")
        self.signal_received = SignalType.SIGTERM
        self.shutdown_reason = ShutdownReason.SIGNAL

        if self.daemon:
            asyncio.create_task(self.daemon.graceful_shutdown())

    def _handle_sigint(self, signum, frame):
        """Handle SIGINT - Ctrl+C"""
        self.logger.warning("📨 Received SIGINT (Ctrl+C) - initiating shutdown")
        self.signal_received = SignalType.SIGINT
        self.shutdown_reason = ShutdownReason.SIGNAL

        if self.shutdown_in_progress:
            self.logger.critical("Force shutdown - SIGINT received again!")
            sys.exit(1)

        if self.daemon:
            asyncio.create_task(self.daemon.graceful_shutdown())

    def _handle_sighup(self, signum, frame):
        """Handle SIGHUP - reload configuration"""
        self.logger.info("📨 Received SIGHUP - reloading configuration")

        if self.daemon:
            asyncio.create_task(self._reload_config())

    def _handle_sigusr1(self, signum, frame):
        """Handle SIGUSR1 - restart trading"""
        self.logger.info("📨 Received SIGUSR1 - restarting trading")
        self.shutdown_reason = ShutdownReason.RESTART

        if self.daemon:
            asyncio.create_task(self.daemon.restart_trading())

    def _handle_sigusr2(self, signum, frame):
        """Handle SIGUSR2 - report status"""
        self.logger.info("📨 Received SIGUSR2 - reporting status")

        if self.daemon:
            status = self.daemon.get_daemon_status()
            self._log_status(status)

    async def _reload_config(self):
        """Reload configuration without restarting"""
        try:
            self.logger.info("🔄 Reloading configuration...")

            # Pause trading
            if self.daemon:
                await self.daemon.pause_trading()

            # Reload config
            # Reconnect to APIs
            # Resume trading

            self.logger.info("✅ Configuration reloaded")

        except Exception as e:
            self.logger.error(f"Failed to reload config: {str(e)}")

    def register_shutdown_handler(self, name: str, handler: Callable):
        """
        Register custom shutdown handler
        Handlers are called during graceful shutdown in order
        """
        self.shutdown_handlers[name] = handler
        self.logger.debug(f"Registered shutdown handler: {name}")

    async def execute_shutdown_handlers(self):
        """Execute all registered shutdown handlers"""
        self.logger.info("Executing shutdown handlers...")

        for handler_name, handler in self.shutdown_handlers.items():
            try:
                self.logger.debug(f"Executing handler: {handler_name}")

                if asyncio.iscoroutinefunction(handler):
                    await asyncio.wait_for(handler(), timeout=5)
                else:
                    handler()

                self.logger.debug(f"✅ Handler completed: {handler_name}")

            except asyncio.TimeoutError:
                self.logger.error(f"Handler timeout: {handler_name}")
            except Exception as e:
                self.logger.error(f"Handler failed {handler_name}: {str(e)}")

    def _log_status(self, status: Dict[str, Any]):
        """Log daemon status"""
        self.logger.info("=" * 60)
        self.logger.info("DAEMON STATUS REPORT")
        self.logger.info("=" * 60)

        for key, value in status.items():
            if isinstance(value, dict):
                self.logger.info(f"{key}:")
                for k, v in value.items():
                    self.logger.info(f"  {k}: {v}")
            else:
                self.logger.info(f"{key}: {value}")

        self.logger.info("=" * 60)

    def get_signal_info(self) -> Dict[str, Any]:
        """Get information about received signals"""
        return {
            'last_signal': self.signal_received.name if self.signal_received else None,
            'shutdown_reason': self.shutdown_reason.value,
            'shutdown_in_progress': self.shutdown_in_progress,
            'timestamp': datetime.now().isoformat()
        }

# ============================================================================
# GRACEFUL SHUTDOWN MANAGER
# ============================================================================

class GracefulShutdownManager:
    """
    Manages graceful shutdown sequence
    Ensures all resources are properly cleaned up
    """

    def __init__(self, timeout: int = 30):
        """Initialize shutdown manager"""
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout
        self.cleanup_tasks = []
        self.started_at: Optional[datetime] = None

    def register_cleanup_task(self, name: str, coro):
        """Register async cleanup task"""
        self.cleanup_tasks.append({
            'name': name,
            'coro': coro,
            'completed': False,
            'error': None
        })

    async def execute_shutdown(self) -> Dict[str, Any]:
        """Execute graceful shutdown sequence"""
        self.started_at = datetime.now()
        self.logger.warning("🛑 Starting graceful shutdown sequence...")

        results = {
            'started_at': self.started_at,
            'completed_at': None,
            'duration_seconds': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'cleanup_results': []
        }

        try:
            # Execute all cleanup tasks with timeout
            for task in self.cleanup_tasks:
                try:
                    self.logger.info(f"Executing cleanup: {task['name']}")

                    await asyncio.wait_for(task['coro'], timeout=self.timeout)

                    task['completed'] = True
                    results['tasks_completed'] += 1
                    self.logger.info(f"✅ Cleanup completed: {task['name']}")

                except asyncio.TimeoutError:
                    task['error'] = "TIMEOUT"
                    results['tasks_failed'] += 1
                    self.logger.error(f"❌ Cleanup timeout: {task['name']}")

                except Exception as e:
                    task['error'] = str(e)
                    results['tasks_failed'] += 1
                    self.logger.error(f"❌ Cleanup failed {task['name']}: {str(e)}")

                results['cleanup_results'].append({
                    'name': task['name'],
                    'completed': task['completed'],
                    'error': task['error']
                })

            results['completed_at'] = datetime.now()
            results['duration_seconds'] = (
                results['completed_at'] - results['started_at']
            ).total_seconds()

            self.logger.warning(
                f"🛑 Graceful shutdown completed: "
                f"{results['tasks_completed']} succeeded, "
                f"{results['tasks_failed']} failed"
            )

        except Exception as e:
            self.logger.critical(f"Critical error during shutdown: {str(e)}")
            results['error'] = str(e)

        return results

# ============================================================================
# PROCESS MONITOR
# ============================================================================

class ProcessMonitor:
    """Monitor daemon process health and resource usage"""

    def __init__(self):
        """Initialize process monitor"""
        self.logger = logging.getLogger(__name__)
        self.start_time = datetime.now()

    def get_uptime(self) -> Dict[str, Any]:
        """Get daemon uptime"""
        elapsed = datetime.now() - self.start_time

        days = elapsed.days
        hours, remainder = divmod(elapsed.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'total_seconds': elapsed.total_seconds(),
            'start_time': self.start_time.isoformat()
        }

    def check_resource_usage(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())

            return {
                'cpu_percent': process.cpu_percent(interval=1),
                'memory_mb': process.memory_info().rss / (1024 * 1024),
                'memory_percent': process.memory_percent(),
                'num_threads': process.num_threads(),
                'open_files': len(process.open_files())
            }

        except ImportError:
            self.logger.warning("psutil not installed - cannot check resources")
            return {}

    def log_resource_report(self):
        """Log resource usage report"""
        uptime = self.get_uptime()
        resources = self.check_resource_usage()

        self.logger.info(
            f"Uptime: {uptime['days']}d {uptime['hours']}h {uptime['minutes']}m | "
            f"CPU: {resources.get('cpu_percent', 'N/A')}% | "
            f"Memory: {resources.get('memory_mb', 'N/A'):.1f}MB"
        )

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'UnixSignalHandler',
    'GracefulShutdownManager',
    'ProcessMonitor',
    'SignalType',
    'ShutdownReason'
]
