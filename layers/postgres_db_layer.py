# ============================================================================
# LAYER 6: POSTGRESQL DATABASE LAYER (YENİ DOSYA)
# ============================================================================
# Dosya: Demir/layers/postgres_db_layer.py
# Durum: YENİ (eski mock versiyonunu replace et)

import psycopg2
from psycopg2.pool import SimpleConnectionPool
import logging
from datetime import datetime
from typing import Dict, List, Any
import os
import json

logger = logging.getLogger(__name__)

class PostgreSQLDatabaseLayer:
    """
    Real PostgreSQL database layer
    - Connection pooling
    - Real persistent storage
    - Trade history tracking
    - Performance metrics
    - ZERO mock data!
    """
    
    def __init__(self):
        """Initialize real PostgreSQL connection pool"""
        
        try:
            # Get DB config from environment
            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = int(os.getenv('DB_PORT', 5432))
            db_name = os.getenv('DB_NAME', 'demir_ai')
            db_user = os.getenv('DB_USER', 'postgres')
            db_password = os.getenv('DB_PASSWORD', '')
            
            # Create connection pool
            self.pool = SimpleConnectionPool(
                1, 20,
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )
            
            logger.info(f"✅ PostgreSQL connection pool created: {db_host}:{db_port}/{db_name}")
            
            # Initialize tables
            self._init_tables()
            
        except Exception as e:
            error = f"CRITICAL: PostgreSQL connection failed: {e}"
            logger.error(error)
            raise RuntimeError(error)
    
    def _init_tables(self):
        """Create tables if not exist - REAL schema"""
        
        conn = self.pool.getconn()
        try:
            cursor = conn.cursor()
            
            # Trades table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    side VARCHAR(10) NOT NULL,
                    quantity DECIMAL(18, 8) NOT NULL,
                    entry_price DECIMAL(18, 8) NOT NULL,
                    exit_price DECIMAL(18, 8),
                    tp_target DECIMAL(18, 8),
                    sl_stop DECIMAL(18, 8),
                    ai_signal VARCHAR(50),
                    confidence DECIMAL(5, 2),
                    status VARCHAR(20),
                    pnl DECIMAL(18, 8),
                    created_at TIMESTAMP DEFAULT NOW(),
                    closed_at TIMESTAMP,
                    layer_scores JSONB
                )
            """)
            
            # Layer performance table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS layer_performance (
                    id SERIAL PRIMARY KEY,
                    layer_name VARCHAR(100) NOT NULL,
                    prediction VARCHAR(50),
                    actual_outcome VARCHAR(50),
                    accuracy DECIMAL(5, 2),
                    latency_ms DECIMAL(10, 2),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # System metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT NOW(),
                    active_layers INT,
                    system_health DECIMAL(5, 2),
                    memory_usage DECIMAL(10, 2),
                    cpu_usage DECIMAL(5, 2),
                    uptime_seconds INT
                )
            """)
            
            conn.commit()
            logger.info("✅ Database tables initialized")
            
        except Exception as e:
            logger.error(f"Table initialization error: {e}")
            conn.rollback()
            raise
        finally:
            self.pool.putconn(conn)
    
    def save_trade(self, trade_data: Dict[str, Any]) -> int:
        """
        Save REAL trade to database
        - NOT mock entry!
        - Persistent storage
        """
        
        conn = self.pool.getconn()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO trades (
                    symbol, side, quantity, entry_price, tp_target, 
                    sl_stop, ai_signal, confidence, status, layer_scores
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                trade_data['symbol'],
                trade_data['side'],
                trade_data['quantity'],
                trade_data['entry_price'],
                trade_data.get('tp_target'),
                trade_data.get('sl_stop'),
                trade_data.get('signal'),
                trade_data.get('confidence'),
                'OPEN',
                json.dumps(trade_data.get('layer_scores', {}))
            ))
            
            trade_id = cursor.fetchone()[0]
            conn.commit()
            
            logger.info(f"✅ Trade saved to DB: ID={trade_id}")
            return trade_id
            
        except Exception as e:
            logger.error(f"Trade save failed: {e}")
            conn.rollback()
            raise
        finally:
            self.pool.putconn(conn)
    
    def close_trade(self, trade_id: int, exit_price: float, pnl: float):
        """Close REAL trade in database"""
        
        conn = self.pool.getconn()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE trades 
                SET exit_price = %s, pnl = %s, status = 'CLOSED', closed_at = NOW()
                WHERE id = %s
            """, (exit_price, pnl, trade_id))
            
            conn.commit()
            logger.info(f"✅ Trade closed: ID={trade_id}, PnL={pnl}")
            
        except Exception as e:
            logger.error(f"Trade close failed: {e}")
            conn.rollback()
            raise
        finally:
            self.pool.putconn(conn)
    
    def get_trade_history(self, symbol: str = None, limit: int = 100) -> List[Dict]:
        """Get REAL trade history from database"""
        
        conn = self.pool.getconn()
        try:
            cursor = conn.cursor()
            
            if symbol:
                cursor.execute("""
                    SELECT id, symbol, side, quantity, entry_price, exit_price, 
                           pnl, status, created_at, closed_at
                    FROM trades
                    WHERE symbol = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (symbol, limit))
            else:
                cursor.execute("""
                    SELECT id, symbol, side, quantity, entry_price, exit_price, 
                           pnl, status, created_at, closed_at
                    FROM trades
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (limit,))
            
            columns = ['id', 'symbol', 'side', 'quantity', 'entry_price', 
                      'exit_price', 'pnl', 'status', 'created_at', 'closed_at']
            
            trades = [dict(zip(columns, row)) for row in cursor.fetchall()]
            logger.info(f"✅ Retrieved {len(trades)} trades from DB")
            
            return trades
            
        except Exception as e:
            logger.error(f"Trade history fetch failed: {e}")
            raise
        finally:
            self.pool.putconn(conn)

