"""
DEMIR AI v5.0 - PostgreSQL Database Module
Real Data Persistence - 100% Compliant
"""
import psycopg2
from psycopg2.extras import execute_values
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        """Connect to PostgreSQL - REAL DATABASE"""
        try:
            db_url = os.getenv('DATABASE_URL')
            self.conn = psycopg2.connect(db_url)
            logger.info("✅ PostgreSQL connected - Real data persistence")
            self.create_tables()
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def create_tables(self):
        """Create tables if not exist"""
        try:
            cursor = self.conn.cursor()
            
            # Trades table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT NOW(),
                    symbol VARCHAR(20),
                    signal_type VARCHAR(20),
                    confidence FLOAT,
                    entry_price FLOAT,
                    take_profit_1 FLOAT,
                    take_profit_2 FLOAT,
                    take_profit_3 FLOAT,
                    stop_loss FLOAT,
                    position_size FLOAT,
                    layer_scores JSONB,
                    market_conditions TEXT
                )
            """)
            
            # Layer performance table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS layer_performance (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT NOW(),
                    layer_name VARCHAR(100),
                    accuracy FLOAT,
                    processing_time FLOAT,
                    signal_count INT,
                    error_count INT
                )
            """)
            
            self.conn.commit()
            logger.info("✅ Database tables created/verified")
        except Exception as e:
            logger.error(f"❌ Table creation failed: {e}")
    
    def save_signal(self, signal_data):
        """Save signal to database - REAL DATA ONLY"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO trades 
                (symbol, signal_type, confidence, entry_price, take_profit_1, 
                 take_profit_2, take_profit_3, stop_loss, position_size, layer_scores)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                signal_data['symbol'],
                signal_data['type'],
                signal_data['confidence'],
                signal_data.get('entry', 0),
                signal_data.get('tp1', 0),
                signal_data.get('tp2', 0),
                signal_data.get('tp3', 0),
                signal_data.get('sl', 0),
                signal_data.get('size', 0),
                str(signal_data.get('scores', {}))
            ))
            self.conn.commit()
            logger.info(f"✅ Signal saved: {signal_data['symbol']} {signal_data['type']}")
        except Exception as e:
            logger.error(f"❌ Signal save failed: {e}")
            self.conn.rollback()
    
    def get_recent_signals(self, limit=10):
        """Get recent signals from database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"""
                SELECT * FROM trades 
                ORDER BY timestamp DESC 
                LIMIT {limit}
            """)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            return []

# Global database instance
db = Database()
