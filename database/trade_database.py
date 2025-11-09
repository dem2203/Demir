"""
=============================================================================
DEMIR AI v25.0 - TRADE DATABASE LAYER (SQLite/JSON)
=============================================================================
Purpose: Tüm trade, signal ve işlem geçmişi kalıcı olarak kaydedilir
Location: /database/ klasörü - NEW
Integrations: streamlit_app.py, trade_entry_calculator.py, daemon_uptime_monitor.py
Language: English (technical) + Turkish (descriptions)
=============================================================================
"""

import sqlite3
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradeStatus(Enum):
    """Trade durumu"""
    PENDING = "PENDING"      # Beklemede
    OPEN = "OPEN"            # Açık
    TP1_HIT = "TP1_HIT"      # TP1 tetiklendi
    TP2_HIT = "TP2_HIT"      # TP2 tetiklendi
    TP3_HIT = "TP3_HIT"      # TP3 tetiklendi (kapalı)
    SL_HIT = "SL_HIT"        # SL tetiklendi (kapalı)
    CANCELED = "CANCELED"    # İptal edildi
    CLOSED = "CLOSED"        # Kapalı


@dataclass
class TradeRecord:
    """Trade kaydı"""
    trade_id: str
    symbol: str
    signal_type: str  # LONG/SHORT
    entry_price: float
    entry_qty: float
    
    tp1_price: float
    tp2_price: float
    tp3_price: float
    sl_price: float
    
    current_status: str
    confidence: float
    
    created_at: str
    opened_at: Optional[str] = None
    closed_at: Optional[str] = None
    
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None  # TP1/TP2/TP3/SL/Manual
    
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    
    notes: Optional[str] = None


class TradeDatabase:
    """
    Trade ve signal veritabanı yöneticisi
    
    Features:
    - SQLite persistent storage
    - CRUD operations
    - Filter & search
    - Performance analytics
    - Export/Import
    """
    
    def __init__(self, db_file: str = "database/trades.db"):
        self.db_file = db_file
        self._ensure_db_dir()
        self._init_db()
        logger.info(f"✅ Trade database initialized: {db_file}")
    
    # ========================================================================
    # DATABASE INITIALIZATION
    # ========================================================================
    
    def _ensure_db_dir(self):
        """Veritabanı dizinini oluştur"""
        Path(self.db_file).parent.mkdir(parents=True, exist_ok=True)
    
    def _init_db(self):
        """Veritabanı tabloları oluştur"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Trades table - Tüm işlemler
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    trade_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    entry_qty REAL NOT NULL,
                    
                    tp1_price REAL,
                    tp2_price REAL,
                    tp3_price REAL,
                    sl_price REAL,
                    
                    current_status TEXT NOT NULL,
                    confidence REAL,
                    
                    created_at TEXT NOT NULL,
                    opened_at TEXT,
                    closed_at TEXT,
                    
                    exit_price REAL,
                    exit_reason TEXT,
                    
                    pnl REAL,
                    pnl_percent REAL,
                    
                    notes TEXT,
                    
                    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Signals table - Tüm sinyaller
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    signal_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    price REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    source TEXT,
                    parameters TEXT,
                    
                    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Performance metrics table - Performans metrikleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance (
                    metric_id TEXT PRIMARY KEY,
                    date TEXT NOT NULL,
                    total_signals INTEGER,
                    win_count INTEGER,
                    loss_count INTEGER,
                    win_rate REAL,
                    total_pnl REAL,
                    avg_confidence REAL,
                    sharpe_ratio REAL,
                    max_drawdown REAL,
                    
                    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("✅ Database tables created")
    
    # ========================================================================
    # TRADE OPERATIONS
    # ========================================================================
    
    def create_trade(self, trade_record: TradeRecord) -> bool:
        """Trade kaydı oluştur"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO trades VALUES (
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?,
                        ?, ?, ?,
                        ?, ?,
                        ?, ?,
                        ?
                    )
                """, (
                    trade_record.trade_id,
                    trade_record.symbol,
                    trade_record.signal_type,
                    trade_record.entry_price,
                    trade_record.entry_qty,
                    
                    trade_record.tp1_price,
                    trade_record.tp2_price,
                    trade_record.tp3_price,
                    trade_record.sl_price,
                    
                    trade_record.current_status,
                    trade_record.confidence,
                    
                    trade_record.created_at,
                    trade_record.opened_at,
                    trade_record.closed_at,
                    
                    trade_record.exit_price,
                    trade_record.exit_reason,
                    
                    trade_record.pnl,
                    trade_record.pnl_percent,
                    
                    trade_record.notes
                ))
                conn.commit()
            
            logger.info(f"✅ Trade created: {trade_record.trade_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error creating trade: {e}")
            return False
    
    def get_trade(self, trade_id: str) -> Optional[Dict]:
        """Trade kaydı al"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM trades WHERE trade_id = ?", (trade_id,))
                row = cursor.fetchone()
                
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
            
            return None
        
        except Exception as e:
            logger.error(f"❌ Error fetching trade: {e}")
            return None
    
    def update_trade_status(self, trade_id: str, status: str, exit_price: Optional[float] = None, 
                           exit_reason: Optional[str] = None, pnl: Optional[float] = None) -> bool:
        """Trade durumunu güncelle"""
        try:
            closed_at = datetime.now().isoformat() if status in [TradeStatus.TP1_HIT.value, 
                                                                  TradeStatus.TP2_HIT.value,
                                                                  TradeStatus.TP3_HIT.value,
                                                                  TradeStatus.SL_HIT.value] else None
            
            pnl_percent = None
            if exit_price and pnl:
                original_trade = self.get_trade(trade_id)
                if original_trade:
                    entry_price = original_trade['entry_price']
                    if original_trade['signal_type'] == 'LONG':
                        pnl_percent = ((exit_price - entry_price) / entry_price * 100)
                    else:
                        pnl_percent = ((entry_price - exit_price) / entry_price * 100)
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE trades 
                    SET current_status = ?, closed_at = ?, exit_price = ?, exit_reason = ?, pnl = ?, pnl_percent = ?
                    WHERE trade_id = ?
                """, (status, closed_at, exit_price, exit_reason, pnl, pnl_percent, trade_id))
                conn.commit()
            
            logger.info(f"✅ Trade {trade_id} status updated to {status}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error updating trade: {e}")
            return False
    
    def get_trades_by_symbol(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Symbol'e göre trade'leri al"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM trades WHERE symbol = ? ORDER BY created_at DESC LIMIT ?",
                    (symbol, limit)
                )
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
        
        except Exception as e:
            logger.error(f"❌ Error fetching trades: {e}")
            return []
    
    def get_all_trades(self, limit: int = 500, offset: int = 0) -> List[Dict]:
        """Tüm trade'leri al"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM trades ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (limit, offset)
                )
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
        
        except Exception as e:
            logger.error(f"❌ Error fetching trades: {e}")
            return []
    
    # ========================================================================
    # SIGNAL OPERATIONS
    # ========================================================================
    
    def log_signal(self, symbol: str, signal_type: str, confidence: float, price: float,
                  source: str = "AI", parameters: Optional[Dict] = None) -> bool:
        """Sinyal kaydını logla"""
        try:
            signal_id = f"{symbol}_{datetime.now().timestamp()}"
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO signals (signal_id, symbol, signal_type, confidence, price, timestamp, source, parameters)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    signal_id,
                    symbol,
                    signal_type,
                    confidence,
                    price,
                    datetime.now().isoformat(),
                    source,
                    json.dumps(parameters) if parameters else None
                ))
                conn.commit()
            
            logger.info(f"✅ Signal logged: {signal_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error logging signal: {e}")
            return False
    
    def get_signals_by_symbol(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Symbol'e göre sinyalleri al"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM signals WHERE symbol = ? ORDER BY timestamp DESC LIMIT ?",
                    (symbol, limit)
                )
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
        
        except Exception as e:
            logger.error(f"❌ Error fetching signals: {e}")
            return []
    
    # ========================================================================
    # ANALYTICS
    # ========================================================================
    
    def calculate_performance_metrics(self, days: int = 1) -> Optional[Dict]:
        """Performans metriklerini hesapla"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Get closed trades from last N days
                cursor.execute("""
                    SELECT * FROM trades 
                    WHERE current_status IN ('TP1_HIT', 'TP2_HIT', 'TP3_HIT', 'SL_HIT')
                    AND closed_at > datetime('now', '-' || ? || ' days')
                """, (days,))
                
                closed_trades = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                trades = [dict(zip(columns, row)) for row in closed_trades]
                
                if not trades:
                    return None
                
                total = len(trades)
                wins = sum(1 for t in trades if t['pnl'] and t['pnl'] > 0)
                losses = total - wins
                
                total_pnl = sum(t['pnl'] for t in trades if t['pnl'])
                avg_confidence = sum(t['confidence'] for t in trades if t['confidence']) / total if total > 0 else 0
                
                # Simple Sharpe ratio estimation
                pnl_values = [t['pnl'] for t in trades if t['pnl']]
                if pnl_values and len(pnl_values) > 1:
                    import numpy as np
                    returns = np.array(pnl_values)
                    sharpe = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
                else:
                    sharpe = 0
                
                # Max drawdown (simplified)
                cumulative = np.cumsum([t['pnl'] for t in trades if t['pnl']])
                running_max = np.maximum.accumulate(cumulative)
                drawdown = cumulative - running_max
                max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0
                
                metrics = {
                    "date": datetime.now().isoformat()[:10],
                    "total_signals": total,
                    "win_count": wins,
                    "loss_count": losses,
                    "win_rate": (wins / total * 100) if total > 0 else 0,
                    "total_pnl": round(total_pnl, 2),
                    "avg_confidence": round(avg_confidence, 2),
                    "sharpe_ratio": round(sharpe, 2),
                    "max_drawdown": round(max_drawdown, 2)
                }
                
                return metrics
        
        except Exception as e:
            logger.error(f"❌ Error calculating metrics: {e}")
            return None
    
    def get_win_rate(self, symbol: Optional[str] = None, days: int = 7) -> float:
        """Kazanma oranını hesapla"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                if symbol:
                    cursor.execute("""
                        SELECT COUNT(*) as total,
                               SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins
                        FROM trades
                        WHERE symbol = ? AND current_status IN ('TP1_HIT', 'TP2_HIT', 'TP3_HIT', 'SL_HIT')
                        AND closed_at > datetime('now', '-' || ? || ' days')
                    """, (symbol, days))
                else:
                    cursor.execute("""
                        SELECT COUNT(*) as total,
                               SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins
                        FROM trades
                        WHERE current_status IN ('TP1_HIT', 'TP2_HIT', 'TP3_HIT', 'SL_HIT')
                        AND closed_at > datetime('now', '-' || ? || ' days')
                    """, (days,))
                
                total, wins = cursor.fetchone()
                return (wins / total * 100) if total > 0 else 0
        
        except Exception as e:
            logger.error(f"❌ Error calculating win rate: {e}")
            return 0
    
    def get_total_pnl(self, symbol: Optional[str] = None, days: int = 7) -> float:
        """Toplam PnL'i al"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                if symbol:
                    cursor.execute("""
                        SELECT SUM(pnl) FROM trades
                        WHERE symbol = ? AND current_status IN ('TP1_HIT', 'TP2_HIT', 'TP3_HIT', 'SL_HIT')
                        AND closed_at > datetime('now', '-' || ? || ' days')
                    """, (symbol, days))
                else:
                    cursor.execute("""
                        SELECT SUM(pnl) FROM trades
                        WHERE current_status IN ('TP1_HIT', 'TP2_HIT', 'TP3_HIT', 'SL_HIT')
                        AND closed_at > datetime('now', '-' || ? || ' days')
                    """, (days,))
                
                result = cursor.fetchone()[0]
                return round(result, 2) if result else 0
        
        except Exception as e:
            logger.error(f"❌ Error calculating PnL: {e}")
            return 0
    
    # ========================================================================
    # EXPORT/IMPORT
    # ========================================================================
    
    def export_trades_csv(self, output_file: str = "trades_export.csv") -> bool:
        """Trade'leri CSV'ye aktar"""
        try:
            trades = self.get_all_trades(limit=10000)
            if not trades:
                return False
            
            import csv
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=trades[0].keys())
                writer.writeheader()
                writer.writerows(trades)
            
            logger.info(f"✅ Trades exported to {output_file}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error exporting trades: {e}")
            return False
    
    def export_trades_json(self, output_file: str = "trades_export.json") -> bool:
        """Trade'leri JSON'a aktar"""
        try:
            trades = self.get_all_trades(limit=10000)
            with open(output_file, 'w') as f:
                json.dump(trades, f, indent=2, default=str)
            
            logger.info(f"✅ Trades exported to {output_file}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error exporting trades: {e}")
            return False


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    db = TradeDatabase()
    
    # Test trade creation
    trade = TradeRecord(
        trade_id="TEST_1",
        symbol="BTCUSDT",
        signal_type="LONG",
        entry_price=50000,
        entry_qty=1.0,
        tp1_price=51500,
        tp2_price=53000,
        tp3_price=55000,
        sl_price=48500,
        current_status="OPEN",
        confidence=85.0,
        created_at=datetime.now().isoformat()
    )
    
    success = db.create_trade(trade)
    print(f"✅ Trade created: {success}")
    
    # Test retrieval
    fetched = db.get_trade("TEST_1")
    print(f"✅ Trade retrieved: {fetched['symbol']}")
    
    # Test status update
    db.update_trade_status("TEST_1", "TP1_HIT", exit_price=51500, exit_reason="TP1", pnl=1500)
    print("✅ Trade status updated")
    
    # Test metrics
    metrics = db.calculate_performance_metrics(days=30)
    if metrics:
        print(f"✅ Performance metrics: {metrics}")
