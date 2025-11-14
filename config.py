# config.py - Configuration Management
"""System configuration and settings"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# DATABASE
# ============================================================================
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/demir_ai')

# ============================================================================
# TRADING CONFIG
# ============================================================================
TRADING_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
SIGNAL_INTERVAL = 5  # seconds
CONFIDENCE_THRESHOLD = 0.65  # 65% minimum confidence

# ============================================================================
# TELEGRAM
# ============================================================================
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL = 'INFO'
LOG_FILE = 'demir_ai.log'

# ============================================================================
# AI CONFIG
# ============================================================================
LAYER_COUNT = 62
ENSEMBLE_WEIGHTS = {
    'technical': 0.25,
    'ml': 0.25,
    'sentiment': 0.15,
    'onchain': 0.10,
    'risk': 0.15,
    'execution': 0.05,
    'database': 0.05
}

# ---

# database.py - PostgreSQL Management
"""Database operations and persistence"""

import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import json
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manage PostgreSQL operations"""
    
    def __init__(self, connection_string):
        self.conn_string = connection_string
        self.connection = None
        self.connect()
    
    def connect(self):
        """Connect to PostgreSQL"""
        try:
            self.connection = psycopg2.connect(self.conn_string)
            logger.info("✅ PostgreSQL connected")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def create_tables(self):
        """Create tables if not exist"""
        try:
            cursor = self.connection.cursor()
            
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
                    layer_scores JSONB
                )
            """)
            
            self.connection.commit()
            logger.info("✅ Tables created")
            return True
        except Exception as e:
            logger.error(f"Table creation error: {e}")
            self.connection.rollback()
            return False
    
    def save_signal(self, signal):
        """Save signal to database"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO trades 
                (symbol, signal_type, confidence, entry_price, 
                 take_profit_1, take_profit_2, take_profit_3, 
                 stop_loss, layer_scores)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                signal['symbol'],
                signal['type'],
                signal['confidence'],
                signal['entry'],
                signal['tp1'],
                signal['tp2'],
                signal['tp3'],
                signal['sl'],
                json.dumps(signal.get('layer_scores', {}))
            ))
            
            trade_id = cursor.fetchone()[0]
            self.connection.commit()
            
            logger.info(f"✅ Signal saved (ID: {trade_id})")
            return trade_id
        except Exception as e:
            logger.error(f"Save signal error: {e}")
            self.connection.rollback()
            return None
    
    def get_recent_signals(self, limit=50):
        """Get recent signals"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM trades 
                ORDER BY timestamp DESC 
                LIMIT %s
            """, (limit,))
            
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Get signals error: {e}")
            return []
    
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()

# Initialize database
db = DatabaseManager(os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/demir_ai'))
db.create_tables()
