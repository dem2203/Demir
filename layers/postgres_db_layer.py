"""
PHASE 5.1: POSTGRESQL DATABASE LAYER
Cloud database management for trade history and metrics

Folder: layers/postgres_db_layer.py
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Trade record"""
    trade_id: str
    symbol: str
    side: str  # BUY/SELL
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    entry_time: datetime
    exit_time: Optional[datetime]
    profit_loss: Optional[float]
    status: str  # OPEN/CLOSED
    strategy: str
    metadata: Dict[str, Any]


class PostgresDBLayer:
    """
    PostgreSQL database layer for Render Cloud
    
    Features:
    - Trade history storage
    - Performance metrics
    - Connection pooling
    - Auto-migration
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize database connection
        
        Args:
            connection_string: DATABASE_URL from environment
        """
        self.connection_string = connection_string or os.getenv('DATABASE_URL')
        
        if not self.connection_string:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.conn = None
        self._connect()
        self._init_tables()
    
    def _connect(self) -> None:
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def _init_tables(self) -> None:
        """Create tables if they don't exist"""
        try:
            cursor = self.conn.cursor()
            
            # Trades table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    trade_id VARCHAR(50) PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    side VARCHAR(10) NOT NULL,
                    entry_price DECIMAL(18, 8) NOT NULL,
                    exit_price DECIMAL(18, 8),
                    quantity DECIMAL(18, 8) NOT NULL,
                    entry_time TIMESTAMP NOT NULL,
                    exit_time TIMESTAMP,
                    profit_loss DECIMAL(18, 8),
                    status VARCHAR(20) NOT NULL,
                    strategy VARCHAR(100),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL,
                    win_rate DECIMAL(5, 2),
                    total_trades INT,
                    profitable_trades INT,
                    total_profit_loss DECIMAL(18, 8),
                    max_drawdown DECIMAL(5, 2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_date ON trades(entry_time)")
            
            self.conn.commit()
            logger.info("Database tables initialized")
            
        except Exception as e:
            logger.error(f"Table initialization failed: {e}")
            self.conn.rollback()
    
    def save_trade(self, trade: Trade) -> bool:
        """
        Save trade to database
        
        Args:
            trade: Trade object
            
        Returns:
            Success status
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                INSERT INTO trades 
                (trade_id, symbol, side, entry_price, exit_price, quantity, 
                 entry_time, exit_time, profit_loss, status, strategy, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (trade_id) DO UPDATE SET
                exit_price = EXCLUDED.exit_price,
                exit_time = EXCLUDED.exit_time,
                profit_loss = EXCLUDED.profit_loss,
                status = EXCLUDED.status,
                metadata = EXCLUDED.metadata
            """, (
                trade.trade_id, trade.symbol, trade.side,
                trade.entry_price, trade.exit_price, trade.quantity,
                trade.entry_time, trade.exit_time, trade.profit_loss,
                trade.status, trade.strategy, json.dumps(trade.metadata)
            ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Save trade failed: {e}")
            self.conn.rollback()
            return False
    
    def get_trades(self, symbol: Optional[str] = None, limit: int = 100) -> List[Trade]:
        """
        Get trades from database
        
        Args:
            symbol: Filter by symbol
            limit: Maximum records to return
            
        Returns:
            List of Trade objects
        """
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            
            if symbol:
                cursor.execute(
                    "SELECT * FROM trades WHERE symbol = %s ORDER BY entry_time DESC LIMIT %s",
                    (symbol, limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM trades ORDER BY entry_time DESC LIMIT %s",
                    (limit,)
                )
            
            rows = cursor.fetchall()
            trades = [Trade(**row) for row in rows]
            
            return trades
            
        except Exception as e:
            logger.error(f"Get trades failed: {e}")
            return []
    
    def save_metrics(self, date: datetime, metrics: Dict[str, Any]) -> bool:
        """Save daily performance metrics"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                INSERT INTO metrics (date, win_rate, total_trades, profitable_trades, 
                                    total_profit_loss, max_drawdown)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                date.date(),
                metrics.get('win_rate'),
                metrics.get('total_trades'),
                metrics.get('profitable_trades'),
                metrics.get('total_profit_loss'),
                metrics.get('max_drawdown')
            ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Save metrics failed: {e}")
            self.conn.rollback()
            return False
    
    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("PostgreSQL DB Layer initialized")
