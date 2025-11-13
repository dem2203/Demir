"""
DATABASE PERSISTENCE LAYER
Trade history, AI decisions, performance metrics
REAL veri depolama

⚠️ REAL DATA: Gerçek trade/analysis data'sı kaydet
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Veritabanı bağlantısını seç: SQLite (simple), PostgreSQL (production)
try:
    import asyncpg
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False

import sqlite3
import json


class PersistenceLayer:
    """
    Database persistence management
    Tüm önemli veri'yi kaydet
    """
    
    def __init__(self, db_type: str = 'sqlite', db_url: str = 'demir_ai.db'):
        """
        Initialize database
        
        Args:
            db_type: 'sqlite' or 'postgresql'
            db_url: Database URL or file path
        """
        
        self.db_type = db_type
        self.db_url = db_url
        self.connection = None
        
        if db_type == 'sqlite':
            self._init_sqlite()
        elif db_type == 'postgresql' and HAS_ASYNCPG:
            # Async init gerekli
            logger.info("PostgreSQL akan initialize asynchronously")
    
    def _init_sqlite(self):
        """SQLite database initialize"""
        
        try:
            self.connection = sqlite3.connect(self.db_url, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            # Create tables
            self._create_tables()
            
            logger.info(f"✅ SQLite database initialized: {self.db_url}")
        
        except Exception as e:
            logger.error(f"❌ SQLite initialization failed: {e}")
    
    def _create_tables(self):
        """Create necessary tables"""
        
        if self.db_type != 'sqlite':
            return
        
        cursor = self.connection.cursor()
        
        # Trades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_price REAL,
                exit_price REAL,
                quantity REAL,
                pnl REAL,
                pnl_percent REAL,
                entry_time TIMESTAMP,
                exit_time TIMESTAMP,
                status TEXT,
                signal_source TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # AI Signals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                signal TEXT NOT NULL,
                confidence REAL,
                entry REAL,
                tp REAL,
                sl REAL,
                timeframe TEXT,
                layers_used INTEGER,
                quality_score REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Performance metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period TEXT,
                total_trades INTEGER,
                wins INTEGER,
                losses INTEGER,
                win_rate REAL,
                total_pnl REAL,
                roi REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # System logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT,
                component TEXT,
                message TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.connection.commit()
        logger.info("✅ Database tables created/verified")
    
    async def save_trade(self, trade: Dict) -> bool:
        """
        Trade'i veritabanına kaydet
        
        Args:
            trade: Trade data
        
        Returns:
            bool: Success
        """
        
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO trades 
                (symbol, side, entry_price, exit_price, quantity, pnl, pnl_percent, 
                 entry_time, exit_time, status, signal_source, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade.get('symbol'),
                trade.get('side'),
                trade.get('entry_price'),
                trade.get('exit_price'),
                trade.get('quantity'),
                trade.get('pnl'),
                trade.get('pnl_percent'),
                trade.get('entry_time'),
                trade.get('exit_time'),
                trade.get('status'),
                trade.get('signal_source'),
                trade.get('confidence')
            ))
            
            self.connection.commit()
            logger.info(f"✅ Trade saved: {trade['symbol']}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to save trade: {e}")
            return False
    
    async def save_signal(self, signal: Dict) -> bool:
        """AI signal'ını kaydet"""
        
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO ai_signals
                (symbol, signal, confidence, entry, tp, sl, timeframe, layers_used, quality_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                signal.get('symbol'),
                signal.get('signal'),
                signal.get('confidence'),
                signal.get('entry'),
                signal.get('tp'),
                signal.get('sl'),
                signal.get('timeframe'),
                signal.get('layers_used'),
                signal.get('quality_score')
            ))
            
            self.connection.commit()
            logger.info(f"✅ Signal saved: {signal['symbol']}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to save signal: {e}")
            return False
    
    async def save_performance(self, metrics: Dict) -> bool:
        """Performance metriklerini kaydet"""
        
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO performance_metrics
                (period, total_trades, wins, losses, win_rate, total_pnl, roi, sharpe_ratio, max_drawdown)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.get('period'),
                metrics.get('total_trades'),
                metrics.get('wins'),
                metrics.get('losses'),
                metrics.get('win_rate'),
                metrics.get('total_pnl'),
                metrics.get('roi'),
                metrics.get('sharpe_ratio'),
                metrics.get('max_drawdown')
            ))
            
            self.connection.commit()
            logger.info(f"✅ Performance metrics saved")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to save performance: {e}")
            return False
    
    async def get_recent_trades(self, limit: int = 100) -> List[Dict]:
        """Son trade'leri al"""
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM trades 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"❌ Failed to fetch trades: {e}")
            return []
    
    async def get_performance_summary(self, days: int = 7) -> Dict:
        """Performance özeti al"""
        
        try:
            cursor = self.connection.cursor()
            
            # Son N gün
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses,
                    SUM(pnl) as total_pnl,
                    AVG(pnl_percent) as avg_return
                FROM trades
                WHERE created_at > ?
            """, (cutoff_date,))
            
            row = cursor.fetchone()
            
            if row:
                total = row['total'] or 0
                wins = row['wins'] or 0
                
                return {
                    'period_days': days,
                    'total_trades': total,
                    'wins': wins,
                    'losses': row['losses'] or 0,
                    'win_rate': (wins / total * 100) if total > 0 else 0,
                    'total_pnl': row['total_pnl'] or 0,
                    'avg_return_percent': row['avg_return'] or 0
                }
        
        except Exception as e:
            logger.error(f"❌ Failed to get performance summary: {e}")
        
        return {}
    
    async def close(self):
        """Database bağlantısını kapat"""
        
        try:
            if self.connection:
                self.connection.close()
            logger.info("✅ Database connection closed")
        
        except Exception as e:
            logger.error(f"Failed to close database: {e}")
