#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
🗄️  DEMIR AI v5.1 - DATABASE SETUP (MUST RUN FIRST!)
═══════════════════════════════════════════════════════════════════════════════

Creates ALL tables for production database:
✅ trading_signals (all AI signals)
✅ executed_trades (completed trades)
✅ sentiment_signals (news/twitter)
✅ macro_indicators (VIX, etc)

Run ONCE before deploying main.py or streamlit_app.py!
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Create ALL required tables"""
    
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        logger.info("🗄️  Creating tables...")
        
        # TABLE 1: trading_signals (ALL signals from AI)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_signals (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                signal_type VARCHAR(10) NOT NULL,
                entry_price FLOAT NOT NULL,
                tp1 FLOAT,
                tp2 FLOAT,
                sl FLOAT,
                confidence FLOAT NOT NULL,
                source VARCHAR(30),
                created_at TIMESTAMP DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_signals_symbol ON trading_signals(symbol);
            CREATE INDEX IF NOT EXISTS idx_signals_created ON trading_signals(created_at);
        """)
        logger.info("✅ trading_signals table created")
        
        # TABLE 2: executed_trades (actual trades executed)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS executed_trades (
                id SERIAL PRIMARY KEY,
                signal_id INT REFERENCES trading_signals(id),
                symbol VARCHAR(20) NOT NULL,
                entry_price FLOAT NOT NULL,
                exit_price FLOAT,
                profit FLOAT,
                profit_pct FLOAT,
                opened_at TIMESTAMP NOT NULL,
                closed_at TIMESTAMP,
                status VARCHAR(20) DEFAULT 'OPEN'
            );
            
            CREATE INDEX IF NOT EXISTS idx_trades_symbol ON executed_trades(symbol);
            CREATE INDEX IF NOT EXISTS idx_trades_status ON executed_trades(status);
        """)
        logger.info("✅ executed_trades table created")
        
        # TABLE 3: sentiment_signals (from news, twitter, etc)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sentiment_signals (
                id SERIAL PRIMARY KEY,
                source VARCHAR(30),
                sentiment FLOAT,
                impact_symbols TEXT[],
                created_at TIMESTAMP DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_sentiment_created ON sentiment_signals(created_at);
        """)
        logger.info("✅ sentiment_signals table created")
        
        # TABLE 4: macro_indicators (VIX, Fear index, etc)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS macro_indicators (
                id SERIAL PRIMARY KEY,
                indicator VARCHAR(30),
                value FLOAT,
                impact VARCHAR(10),
                created_at TIMESTAMP DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_macro_indicator ON macro_indicators(indicator);
        """)
        logger.info("✅ macro_indicators table created")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ ALL TABLES CREATED SUCCESSFULLY!")
        logger.info("=" * 80)
        logger.info("Database is ready for production!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Database setup error: {e}")
        raise

if __name__ == "__main__":
    setup_database()
