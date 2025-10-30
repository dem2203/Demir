"""
DEMIR - Database Layer
Trade History, Signal Performance, Learning Data
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
import json

# ============================================
# DATABASE INITIALIZATION
# ============================================

DB_FILE = 'demir_trading.db'

def init_database():
    """Veritabanını ve tabloları oluştur"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Signals tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            symbol TEXT NOT NULL,
            signal TEXT NOT NULL,
            confidence REAL,
            price REAL,
            factors TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Trades tablosu (gelecekte kullanım için)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signal_id INTEGER,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            entry_price REAL,
            exit_price REAL,
            quantity REAL,
            pnl REAL,
            status TEXT,
            opened_at TEXT,
            closed_at TEXT,
            FOREIGN KEY (signal_id) REFERENCES signals(id)
        )
    ''')
    
    # Performance tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            total_signals INTEGER,
            profitable_signals INTEGER,
            win_rate REAL,
            avg_confidence REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


# ============================================
# SIGNAL OPERATIONS
# ============================================

def save_signal(symbol: str, signal_data: Dict[str, Any]) -> int:
    """Sinyali veritabanına kaydet"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO signals (timestamp, symbol, signal, confidence, price, factors)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            symbol,
            signal_data.get('signal', 'HOLD'),
            signal_data.get('confidence', 0),
            signal_data.get('price', 0),
            json.dumps(signal_data.get('factors', {}))
        ))
        
        conn.commit()
        signal_id = cursor.lastrowid
        
    except Exception as e:
        print(f"Sinyal kaydetme hatası: {e}")
        signal_id = -1
    
    finally:
        conn.close()
    
    return signal_id


def get_recent_signals(symbol: str = None, limit: int = 10) -> pd.DataFrame:
    """Son sinyalleri getir"""
    conn = sqlite3.connect(DB_FILE)
    
    if symbol:
        query = f'''
            SELECT * FROM signals 
            WHERE symbol = '{symbol}'
            ORDER BY timestamp DESC 
            LIMIT {limit}
        '''
    else:
        query = f'''
            SELECT * FROM signals 
            ORDER BY timestamp DESC 
            LIMIT {limit}
        '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df


def get_signal_stats(symbol: str = None, days: int = 7) -> Dict[str, Any]:
    """Sinyal istatistikleri"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Son N günün sinyalleri
    date_filter = f"datetime('now', '-{days} days')"
    
    if symbol:
        query = f'''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN signal='BUY' THEN 1 ELSE 0 END) as buy_count,
                SUM(CASE WHEN signal='SELL' THEN 1 ELSE 0 END) as sell_count,
                AVG(confidence) as avg_confidence
            FROM signals
            WHERE symbol = '{symbol}' AND timestamp > {date_filter}
        '''
    else:
        query = f'''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN signal='BUY' THEN 1 ELSE 0 END) as buy_count,
                SUM(CASE WHEN signal='SELL' THEN 1 ELSE 0 END) as sell_count,
                AVG(confidence) as avg_confidence
            FROM signals
            WHERE timestamp > {date_filter}
        '''
    
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    
    return {
        'total_signals': result[0] if result else 0,
        'buy_signals': result[1] if result else 0,
        'sell_signals': result[2] if result else 0,
        'avg_confidence': result[3] if result else 0
    }


# ============================================
# TRADE OPERATIONS (Placeholder)
# ============================================

def save_trade(trade_data: Dict[str, Any]) -> int:
    """Trade'i kaydet (gelecekte kullanım)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO trades 
            (signal_id, symbol, side, entry_price, quantity, status, opened_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade_data.get('signal_id'),
            trade_data.get('symbol'),
            trade_data.get('side'),
            trade_data.get('entry_price'),
            trade_data.get('quantity'),
            'OPEN',
            datetime.now().isoformat()
        ))
        
        conn.commit()
        trade_id = cursor.lastrowid
        
    except Exception as e:
        print(f"Trade kaydetme hatası: {e}")
        trade_id = -1
    
    finally:
        conn.close()
    
    return trade_id


def close_trade(trade_id: int, exit_price: float, pnl: float) -> bool:
    """Trade'i kapat"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE trades
            SET exit_price = ?, pnl = ?, status = 'CLOSED', closed_at = ?
            WHERE id = ?
        ''', (exit_price, pnl, datetime.now().isoformat(), trade_id))
        
        conn.commit()
        success = True
        
    except Exception as e:
        print(f"Trade kapatma hatası: {e}")
        success = False
    
    finally:
        conn.close()
    
    return success


# ============================================
# INITIALIZATION
# ============================================

# İlk import'ta database'i oluştur
try:
    init_database()
except Exception as e:
    print(f"Database başlatma hatası: {e}")
