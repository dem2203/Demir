# ============================================================================
# DEMIR AI - SCHEDULER DAEMON & STATE MANAGER (Phase 8/9)
# ============================================================================
# Date: November 10, 2025
# Purpose: 7/24 aktif, her 5 dakikada analiz, saatlik sinyal kontrol
#
# 🔒 KURALLAR:
# - Arka planda daemon thread'de çalış
# - SQLite'a tüm analiz/signal/trade history kaydet
# - Gerçek verilerle çalış, mock data YOK
# - Sinyal değiştiğinde hemen Telegram alert gönder
# ============================================================================

import threading
import time
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# STATE MANAGER - Signal & Trade History Veritabanı
# ============================================================================

class SignalState(Enum):
    """Signal durumları"""
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"

@dataclass
class SignalRecord:
    """Signal kaydı"""
    timestamp: str
    symbol: str
    signal: str
    score: float
    confidence: float
    active_layers: int
    details: str

class StateManager:
    """
    Tüm trading durumunu SQLite'da yönet
    (Manage all trading state in SQLite)
    """
    
    def __init__(self, db_path: str = 'data/demir_ai.db'):
        """Initialize state manager (Durum yöneticisini başlat)"""
        self.db_path = db_path
        self.init_database()
        logger.info(f"✅ State Manager initialized: {db_path}")
    
    def init_database(self):
        """Veritabanını hazırla (Initialize database)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Signals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT NOT NULL,
                    signal TEXT NOT NULL,
                    score REAL,
                    confidence REAL,
                    active_layers INTEGER,
                    details TEXT,
                    UNIQUE(timestamp, symbol)
                )
            """)
            
            # Trades table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_time DATETIME,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price REAL,
                    quantity REAL,
                    exit_price REAL,
                    exit_time DATETIME,
                    pnl REAL,
                    status TEXT,
                    notes TEXT
                )
            """)
            
            # Analysis history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT,
                    analysis_data TEXT,
                    layers_count INTEGER,
                    avg_score REAL
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ Database tables initialized")
            
        except Exception as e:
            logger.error(f"Database init hatası: {e}")
    
    def save_signal(self, signal_record: SignalRecord):
        """Sinyali veritabanına kaydet (Save signal to database)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO signals 
                (timestamp, symbol, signal, score, confidence, active_layers, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                signal_record.timestamp,
                signal_record.symbol,
                signal_record.signal,
                signal_record.score,
                signal_record.confidence,
                signal_record.active_layers,
                signal_record.details
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Signal saved: {signal_record.signal} @ {signal_record.timestamp}")
            
        except Exception as e:
            logger.error(f"Signal save hatası: {e}")
    
    def get_last_signal(self, symbol: str = 'BTCUSDT') -> Optional[SignalRecord]:
        """Son sinyali al (Get last signal)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, symbol, signal, score, confidence, active_layers, details
                FROM signals
                WHERE symbol = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (symbol,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return SignalRecord(*row)
            return None
            
        except Exception as e:
            logger.error(f"Get last signal hatası: {e}")
            return None
    
    def get_signal_history(self, symbol: str = 'BTCUSDT', hours: int = 24) -> List[SignalRecord]:
        """Signal geçmişini al (Get signal history)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute("""
                SELECT timestamp, symbol, signal, score, confidence, active_layers, details
                FROM signals
                WHERE symbol = ? AND timestamp > ?
                ORDER BY timestamp DESC
            """, (symbol, since))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [SignalRecord(*row) for row in rows]
            
        except Exception as e:
            logger.error(f"Get signal history hatası: {e}")
            return []

# ============================================================================
# SCHEDULER DAEMON - 7/24 Analiz & Alert
# ============================================================================

class SchedulerDaemon:
    """
    7/24 Scheduler daemon - Her 5 dakikada analiz, sinyal değişimine alert
    (24/7 scheduler daemon - Run analysis every 5 minutes)
    """
    
    def __init__(self, analysis_interval: int = 300):
        """
        Initialize scheduler
        
        Args:
            analysis_interval: Saniye cinsinden analiz aralığı (Analysis interval in seconds)
        """
        self.is_running = False
        self.analysis_interval = analysis_interval
        self.state_manager = StateManager()
        self.last_signal = {}
        self.threads: List[threading.Thread] = []
        
        logger.info(f"✅ SchedulerDaemon initialized (interval: {analysis_interval}s)")
    
    def start(self):
        """Daemon başlat (Start daemon)"""
        if self.is_running:
            logger.warning("⚠️ Daemon zaten çalışıyor")
            return
        
        self.is_running = True
        
        # Analysis thread
        analysis_thread = threading.Thread(
            target=self._analysis_loop,
            daemon=True,
            name='analysis_daemon'
        )
        analysis_thread.start()
        self.threads.append(analysis_thread)
        
        logger.info(f"🟢 SchedulerDaemon başlatıldı - {len(self.threads)} thread(s)")
    
    def stop(self):
        """Daemon durdur (Stop daemon)"""
        self.is_running = False
        logger.info("🔴 SchedulerDaemon durduruldu")
    
    def _analysis_loop(self):
        """Analiz loop - Her 5 dakikada çalış (Analysis loop - runs every 5 min)"""
        logger.info("🔄 Analysis loop başladı")
        
        while self.is_running:
            try:
                # AI analizi çalıştır (uyarlanacak senin aibrain.py'den)
                logger.info("📊 Analiz başlıyor...")
                
                # Placeholder: Gerçek AI analizi buraya gelecek
                # from aibrain import AIBrain
                # ai_brain = AIBrain()
                # signal = ai_brain.analyze(market_data)
                
                # Signal değişmişse Telegram alert gönder
                # self._check_signal_change(signal)
                
                time.sleep(self.analysis_interval)
                
            except Exception as e:
                logger.error(f"Analysis loop hatası: {e}")
                time.sleep(60)
    
    def _check_signal_change(self, new_signal: Dict[str, Any]):
        """
        Signal değişip değişmediğini kontrol et
        (Check if signal changed and send alert)
        """
        symbol = new_signal.get('symbol', 'BTCUSDT')
        new_signal_type = new_signal.get('signal')
        
        old_signal_type = self.last_signal.get(symbol, 'NEUTRAL')
        
        # Signal değişti mi?
        if old_signal_type != new_signal_type:
            logger.info(f"📢 SIGNAL DEĞİŞTİ: {old_signal_type} → {new_signal_type}")
            
            # Telegram alert gönder
            # Bu kısım telegramAlertSystem ile entegre olur
            # telegram.queue_alert(
            #     f"🚨 SIGNAL CHANGE\\n{symbol}: {new_signal_type}\\nScore: {new_signal['score']:.1f}",
            #     AlertSeverity.SIGNAL
            # )
            
            # Veritabanına kaydet
            record = SignalRecord(
                timestamp=datetime.now().isoformat(),
                symbol=symbol,
                signal=new_signal_type,
                score=new_signal.get('overall_score', 50),
                confidence=new_signal.get('confidence', 0),
                active_layers=new_signal.get('active_layers', 0),
                details=json.dumps(new_signal)
            )
            
            self.state_manager.save_signal(record)
            self.last_signal[symbol] = new_signal_type

# ============================================================================
# WATCHDOG MONITOR - Daemon Health Check
# ============================================================================

class WatchdogMonitor:
    """
    Daemon sağlık kontrolü - çökmesi halinde otomatik restart
    (Watchdog monitor - auto-restart if daemon crashes)
    """
    
    def __init__(self, daemon: SchedulerDaemon, check_interval: int = 30):
        """Initialize watchdog (Watchdog'u başlat)"""
        self.daemon = daemon
        self.check_interval = check_interval
        self.is_running = False
        self.restart_count = 0
        
        logger.info(f"✅ Watchdog initialized (check every {check_interval}s)")
    
    def start(self):
        """Watchdog başlat (Start watchdog)"""
        self.is_running = True
        watchdog_thread = threading.Thread(
            target=self._watchdog_loop,
            daemon=True,
            name='watchdog'
        )
        watchdog_thread.start()
        logger.info("🟢 Watchdog started")
    
    def stop(self):
        """Watchdog durdur (Stop watchdog)"""
        self.is_running = False
        logger.info("🔴 Watchdog stopped")
    
    def _watchdog_loop(self):
        """Watchdog kontrol loop (Watchdog monitoring loop)"""
        logger.info("🔄 Watchdog loop başladı")
        
        while self.is_running:
            try:
                # Daemon çalışıyor mu kontrol et
                if not self.daemon.is_running:
                    logger.warning("⚠️ Daemon çöktü! Yeniden başlatılıyor...")
                    self.restart_count += 1
                    self.daemon.start()
                    logger.info(f"✅ Daemon restarted (count: {self.restart_count})")
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Watchdog loop hatası: {e}")
                time.sleep(self.check_interval)

# ============================================================================
# COMPLETE SYSTEM
# ============================================================================

class DEMIR_Phase9_System:
    """
    Tüm Phase 8/9 sistemi - Daemon + State Manager + Watchdog
    (Complete Phase 9 system integration)
    """
    
    def __init__(self):
        """Initialize complete system"""
        self.daemon = SchedulerDaemon(analysis_interval=300)  # 5 minutes
        self.watchdog = WatchdogMonitor(self.daemon, check_interval=30)
        self.state_manager = StateManager()
        
        logger.info("✅ DEMIR Phase 9 System initialized")
    
    def start(self):
        """Tüm sistemi başlat (Start entire system)"""
        self.daemon.start()
        self.watchdog.start()
        logger.info("🟢 DEMIR Phase 9 System STARTED")
    
    def stop(self):
        """Sistemi durdur (Stop system)"""
        self.watchdog.stop()
        self.daemon.stop()
        logger.info("🔴 DEMIR Phase 9 System STOPPED")
    
    def get_status(self) -> Dict[str, Any]:
        """Sistem durumunu al (Get system status)"""
        return {
            'timestamp': datetime.now().isoformat(),
            'daemon_running': self.daemon.is_running,
            'watchdog_running': self.watchdog.is_running,
            'daemon_restarts': self.watchdog.restart_count,
            'last_signals': self.daemon.last_signal
        }

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'SchedulerDaemon',
    'StateManager',
    'WatchdogMonitor',
    'DEMIR_Phase9_System',
    'SignalRecord',
    'SignalState'
]

# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    # Initialize system
    system = DEMIR_Phase9_System()
    
    # Start
    system.start()
    
    print("✅ Phase 9 System Running")
    print(f"Status: {system.get_status()}")
    
    # Keep running for 10 seconds (test)
    try:
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        system.stop()
        print("✅ System shutdown complete")
