"""
=============================================================================
DEMIR AI v25.0 - DAEMON UPTIME MONITOR & INTERVAL PINGER
=============================================================================
Purpose: 7/24 bot çalışma durumu, daemon log, interval Telegram bildirimleri
Location: /daemon/ klasörü - UPDATE & NEW
Integrations: daemon_core.py, telegram_alert_system.py, streamlit_app.py
=============================================================================
"""

import logging
import time
import threading
import psutil
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class DaemonStatus:
    """Daemon durumu snapshot'ı"""
    status: str  # "RUNNING", "STOPPED", "ERROR"
    uptime_seconds: float
    last_heartbeat: str
    cpu_usage: float  # %
    memory_usage: float  # %
    active_trades: int
    last_signal_time: str
    error_count: int
    restart_count: int
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class DaemonHealthMonitor:
    """
    Daemon sağlık ve uptime takibi
    
    Features:
    - 7/24 bot çalışma durumu
    - CPU/Memory monitoring
    - Otomatik restart logic
    - Interval ping
    - Activity log
    """
    
    def __init__(self, log_file: str = "logs/daemon_status.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Daemon metrics
        self.start_time = datetime.now()
        self.heartbeat_time = datetime.now()
        self.error_count = 0
        self.restart_count = 0
        self.active_trades = 0
        self.last_signal_time = datetime.now()
        
        # Status history
        self.status_history: List[DaemonStatus] = []
        self.max_history = 1000
        
        # Configuration
        self.ping_interval = 3600  # 1 hour (seconds)
        self.health_check_interval = 300  # 5 minutes (seconds)
        self.error_threshold = 10
        self.restart_on_error = True
        
        # Load history
        self._load_status_history()
        logger.info("✅ DaemonHealthMonitor initialized")
    
    # ========================================================================
    # HEARTBEAT & STATUS
    # ========================================================================
    
    def heartbeat(self, error: Optional[str] = None) -> DaemonStatus:
        """
        Daemon heartbeat - 5 saniyede bir çağrılmalı
        
        Args:
            error: Hata mesajı (varsa)
        
        Returns:
            Current DaemonStatus
        """
        self.heartbeat_time = datetime.now()
        
        if error:
            self.error_count += 1
            logger.error(f"❌ Daemon error: {error} (Count: {self.error_count})")
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_info = psutil.virtual_memory()
        
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        status = DaemonStatus(
            status="RUNNING" if self.error_count < self.error_threshold else "ERROR",
            uptime_seconds=uptime,
            last_heartbeat=self.heartbeat_time.isoformat(),
            cpu_usage=cpu_percent,
            memory_usage=memory_info.percent,
            active_trades=self.active_trades,
            last_signal_time=self.last_signal_time.isoformat(),
            error_count=self.error_count,
            restart_count=self.restart_count
        )
        
        # Store in history
        self.status_history.append(status)
        if len(self.status_history) > self.max_history:
            self.status_history.pop(0)
        
        return status
    
    def get_current_status(self) -> DaemonStatus:
        """Mevcut daemon durumunu al"""
        return self.heartbeat() if self.status_history else None
    
    def should_restart(self) -> bool:
        """Daemon restart edilmeli mi?"""
        if not self.restart_on_error:
            return False
        
        return self.error_count >= self.error_threshold
    
    def restart(self):
        """Daemon restart"""
        logger.warning("🔄 RESTARTING DAEMON...")
        self.restart_count += 1
        self.error_count = 0
        self.start_time = datetime.now()
        self.heartbeat_time = datetime.now()
        logger.info(f"✅ Daemon restarted (Count: {self.restart_count})")
    
    # ========================================================================
    # PING & NOTIFICATIONS
    # ========================================================================
    
    def should_send_interval_ping(self) -> bool:
        """Interval ping gönderilmeli mi? (örn: her saat)"""
        if not self.status_history:
            return False
        
        last_status = self.status_history[-1]
        last_ping = datetime.fromisoformat(last_status.last_heartbeat)
        
        return (datetime.now() - last_ping).total_seconds() >= self.ping_interval
    
    def get_ping_message(self) -> str:
        """Interval ping mesajı oluştur"""
        status = self.get_current_status()
        uptime_hours = status.uptime_seconds / 3600
        
        message = f"""
🤖 **DEMIR AI BOT STATUS PING** 🟢
━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ Uptime: {uptime_hours:.2f} hours ({status.restart_count} restarts)
📊 CPU: {status.cpu_usage:.1f}% | RAM: {status.memory_usage:.1f}%
📈 Active Trades: {status.active_trades}
🔴 Errors: {status.error_count}
⏰ Last Signal: {status.last_signal_time[11:19]}
🟢 Status: {status.status}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Bot is working 24/7
Time: {status.timestamp[:19]} CET
        """.strip()
        
        return message
    
    # ========================================================================
    # ACTIVITY LOG
    # ========================================================================
    
    def log_trade_opened(self, symbol: str, entry_price: float, qty: float):
        """Trade açıldı logla"""
        self.active_trades += 1
        self.last_signal_time = datetime.now()
        logger.info(f"📈 TRADE OPENED: {symbol} @ {entry_price} x{qty}")
    
    def log_trade_closed(self, symbol: str, pnl: float, reason: str):
        """Trade kapatıldı logla"""
        self.active_trades = max(0, self.active_trades - 1)
        pnl_sign = "✅" if pnl >= 0 else "❌"
        logger.info(f"{pnl_sign} TRADE CLOSED: {symbol} | PnL: {pnl} | Reason: {reason}")
    
    def log_signal(self, signal_type: str, confidence: float, message: str):
        """Trade sinyal logla"""
        self.last_signal_time = datetime.now()
        logger.info(f"📊 SIGNAL: {signal_type} ({confidence}%) - {message}")
    
    def log_error(self, error_message: str):
        """Hata logla"""
        self.error_count += 1
        logger.error(f"🔴 ERROR #{self.error_count}: {error_message}")
    
    # ========================================================================
    # PERSISTENCE
    # ========================================================================
    
    def _save_status_history(self):
        """Status history'yi kaydet"""
        try:
            data = [asdict(s) for s in self.status_history[-100:]]  # Last 100
            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save status history: {e}")
    
    def _load_status_history(self):
        """Status history'yi yükle"""
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.status_history = [DaemonStatus(**s) for s in data]
                    logger.info(f"✅ Loaded {len(self.status_history)} status records")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load status history: {e}")
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def get_health_report(self) -> Dict:
        """Health raporu"""
        status = self.get_current_status()
        
        # Calculate stats
        errors_24h = sum(1 for s in self.status_history[-288:] if s.error_count > 0)  # 24h = 288 * 5min
        avg_cpu = sum(s.cpu_usage for s in self.status_history) / len(self.status_history) if self.status_history else 0
        avg_memory = sum(s.memory_usage for s in self.status_history) / len(self.status_history) if self.status_history else 0
        
        return {
            "status": status.status,
            "uptime_hours": round(status.uptime_seconds / 3600, 2),
            "restarts": status.restart_count,
            "errors": status.error_count,
            "errors_24h": errors_24h,
            "avg_cpu": round(avg_cpu, 1),
            "avg_memory": round(avg_memory, 1),
            "current_cpu": round(status.cpu_usage, 1),
            "current_memory": round(status.memory_usage, 1),
            "active_trades": status.active_trades,
            "last_signal": status.last_signal_time
        }
    
    def get_status_table(self) -> List[Dict]:
        """GUI için status tabı"""
        if not self.status_history:
            return []
        
        # Last 10 statuses
        recent = self.status_history[-10:]
        return [
            {
                "Time": s.timestamp[11:19],
                "Status": s.status,
                "CPU": f"{s.cpu_usage:.1f}%",
                "Memory": f"{s.memory_usage:.1f}%",
                "Trades": s.active_trades,
                "Errors": s.error_count,
                "Uptime": f"{s.uptime_seconds/3600:.1f}h"
            }
            for s in recent
        ]


class DaemonPinger:
    """
    Interval ping sistemi - Telegram'a saatlik bildirim
    
    Features:
    - Scheduled pings
    - Customizable intervals
    - Telegram integration
    """
    
    def __init__(self, monitor: DaemonHealthMonitor, interval_seconds: int = 3600):
        self.monitor = monitor
        self.interval = interval_seconds
        self.last_ping_time = datetime.now()
        self.ping_thread = None
        self.is_running = False
    
    def start_pinger(self):
        """Pinger thread başlat"""
        self.is_running = True
        self.ping_thread = threading.Thread(target=self._ping_loop, daemon=True)
        self.ping_thread.start()
        logger.info(f"✅ Daemon pinger started (interval: {self.interval}s)")
    
    def stop_pinger(self):
        """Pinger thread durdur"""
        self.is_running = False
        logger.info("⏸️ Daemon pinger stopped")
    
    def _ping_loop(self):
        """Ping döngüsü"""
        while self.is_running:
            if self.monitor.should_send_interval_ping():
                message = self.monitor.get_ping_message()
                logger.info(f"\n{message}\n")
                self.last_ping_time = datetime.now()
                
                # TODO: Send to Telegram
                # await telegram_send_message(message, chat_id="YOUR_CHAT_ID")
            
            time.sleep(60)  # Check every minute


# ============================================================================
# TEST & USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize
    monitor = DaemonHealthMonitor()
    pinger = DaemonPinger(monitor, interval_seconds=60)  # Every minute for testing
    
    # Simulate daemon operation
    print("\n📊 Simulating daemon operation...")
    
    for i in range(10):
        # Heartbeat
        status = monitor.heartbeat()
        
        # Simulate activity
        if i % 3 == 0:
            monitor.log_trade_opened("BTCUSDT", 50000, 1.0)
        if i % 5 == 0:
            monitor.log_signal("LONG", 85.0, "Strong uptrend detected")
        
        # Simulate occasional errors
        if i == 7:
            monitor.log_error("API timeout")
        
        print(f"\n[{i+1}] Status: {status.status} | CPU: {status.cpu_usage:.1f}% | Errors: {status.error_count}")
        time.sleep(1)
    
    # Print report
    print(f"\n📋 Health Report:")
    for key, value in monitor.get_health_report().items():
        print(f"  {key}: {value}")
    
    # Print status table
    print(f"\n📊 Status Table:")
    for row in monitor.get_status_table():
        print(f"  {row}")
    
    # Get ping message
    print(f"\n🔔 Ping Message:")
    print(monitor.get_ping_message())
