"""
💾 PHASE 9.3 - STATE MANAGER (HYBRID MODE)
===========================================

Path: phase_9/state_manager.py
Date: 7 Kasım 2025, 15:50 CET

Manages bot state: Remembers history, tracks trends, makes decisions
Persistent state - survives restarts
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class StateManager:
    """Persistent state manager with history tracking"""
    
    def __init__(self, db_path='phase_9/data/state.db'):
        """
        Initialize state manager
        
        Args:
            db_path: SQLite database path
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Analyses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    score REAL,
                    signal TEXT,
                    confidence REAL,
                    layer_scores TEXT,
                    json_data TEXT
                )
            ''')
            
            # Trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY,
                    entry_time TEXT,
                    entry_price REAL,
                    signal TEXT,
                    status TEXT,
                    exit_time TEXT,
                    exit_price REAL,
                    pnl_percent REAL,
                    user_confirmed INTEGER
                )
            ''')
            
            # Alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    alert_type TEXT,
                    message TEXT,
                    user_action TEXT
                )
            ''')
            
            # Bot state table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_state (
                    id INTEGER PRIMARY KEY,
                    key TEXT UNIQUE,
                    value TEXT,
                    updated_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Database initialized")
            
        except Exception as e:
            logger.error(f"Database init error: {e}")
    
    def record_analysis(self, score: float, signal: str, confidence: float, 
                       layer_scores: Dict, full_data: Dict):
        """
        Record analysis result
        
        Args:
            score: Final score (0-100)
            signal: Signal (LONG/SHORT/NEUTRAL)
            confidence: Confidence level (0-1)
            layer_scores: Individual layer scores
            full_data: Complete analysis data
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            layer_scores_json = json.dumps(layer_scores)
            full_data_json = json.dumps(full_data)
            
            cursor.execute('''
                INSERT INTO analyses 
                (timestamp, score, signal, confidence, layer_scores, json_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, score, signal, confidence, layer_scores_json, full_data_json))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"✅ Analysis recorded: {signal} @ {score}")
            
        except Exception as e:
            logger.error(f"Record analysis error: {e}")
    
    def get_trend(self, hours: int = 1) -> Dict:
        """
        Analyze recent trend (up/down/stable)
        
        Args:
            hours: Look back N hours
        
        Returns:
            Trend analysis
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT timestamp, score FROM analyses
                WHERE timestamp > ?
                ORDER BY timestamp ASC
            ''', (cutoff.isoformat(),))
            
            results = cursor.fetchall()
            conn.close()
            
            if len(results) < 2:
                return {'trend': 'INSUFFICIENT_DATA', 'direction': None}
            
            # Calculate trend
            first_score = results[0][1]
            last_score = results[-1][1]
            change = last_score - first_score
            percent_change = (change / first_score) * 100 if first_score != 0 else 0
            
            if change > 5:
                direction = 'UP'
            elif change < -5:
                direction = 'DOWN'
            else:
                direction = 'STABLE'
            
            return {
                'trend': direction,
                'change': round(change, 2),
                'percent_change': round(percent_change, 2),
                'first_score': first_score,
                'last_score': last_score,
                'samples': len(results)
            }
            
        except Exception as e:
            logger.error(f"Trend analysis error: {e}")
            return {'trend': 'ERROR'}
    
    def record_trade(self, signal: str, entry_price: float, 
                    user_confirmed: bool = False):
        """
        Record trade entry
        
        Args:
            signal: Signal (LONG/SHORT)
            entry_price: Entry price
            user_confirmed: Was trade confirmed by user?
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO trades
                (entry_time, entry_price, signal, status, user_confirmed)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, entry_price, signal, 'OPEN', 1 if user_confirmed else 0))
            
            trade_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"📈 Trade recorded: {signal} @ {entry_price}")
            return trade_id
            
        except Exception as e:
            logger.error(f"Record trade error: {e}")
            return None
    
    def close_trade(self, trade_id: int, exit_price: float):
        """
        Close trade and calculate P&L
        
        Args:
            trade_id: Trade ID
            exit_price: Exit price
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get entry trade
            cursor.execute('SELECT entry_price, signal FROM trades WHERE id = ?', (trade_id,))
            result = cursor.fetchone()
            
            if not result:
                logger.error(f"Trade {trade_id} not found")
                return
            
            entry_price, signal = result
            
            # Calculate P&L
            if signal == 'LONG':
                pnl_percent = ((exit_price - entry_price) / entry_price) * 100
            else:  # SHORT
                pnl_percent = ((entry_price - exit_price) / entry_price) * 100
            
            # Update trade
            timestamp = datetime.now().isoformat()
            cursor.execute('''
                UPDATE trades
                SET exit_time = ?, exit_price = ?, pnl_percent = ?, status = ?
                WHERE id = ?
            ''', (timestamp, exit_price, pnl_percent, 'CLOSED', trade_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"📊 Trade closed: P&L = {pnl_percent:.2f}%")
            
        except Exception as e:
            logger.error(f"Close trade error: {e}")
    
    def get_trade_history(self, days: int = 7) -> List[Dict]:
        """
        Get trade history
        
        Args:
            days: Last N days
        
        Returns:
            List of trades
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                SELECT * FROM trades
                WHERE entry_time > ?
                ORDER BY entry_time DESC
            ''', (cutoff.isoformat(),))
            
            columns = [desc[0] for desc in cursor.description]
            trades = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return trades
            
        except Exception as e:
            logger.error(f"Get trades error: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get trading statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count trades
            cursor.execute('SELECT COUNT(*) FROM trades WHERE status = ?', ('CLOSED',))
            total_trades = cursor.fetchone()[0]
            
            # Winning trades
            cursor.execute('SELECT COUNT(*) FROM trades WHERE status = ? AND pnl_percent > 0', ('CLOSED',))
            winning_trades = cursor.fetchone()[0]
            
            # Average P&L
            cursor.execute('SELECT AVG(pnl_percent) FROM trades WHERE status = ?', ('CLOSED',))
            avg_pnl = cursor.fetchone()[0] or 0
            
            # Max P&L
            cursor.execute('SELECT MAX(pnl_percent) FROM trades WHERE status = ?', ('CLOSED',))
            max_pnl = cursor.fetchone()[0] or 0
            
            # Min P&L
            cursor.execute('SELECT MIN(pnl_percent) FROM trades WHERE status = ?', ('CLOSED',))
            min_pnl = cursor.fetchone()[0] or 0
            
            conn.close()
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': round(win_rate, 2),
                'avg_pnl': round(avg_pnl, 2),
                'max_pnl': round(max_pnl, 2),
                'min_pnl': round(min_pnl, 2)
            }
            
        except Exception as e:
            logger.error(f"Statistics error: {e}")
            return {}
    
    def set_state(self, key: str, value: str):
        """Set bot state variable"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO bot_state (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, value, timestamp))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Set state error: {e}")
    
    def get_state(self, key: str) -> Optional[str]:
        """Get bot state variable"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM bot_state WHERE key = ?', (key,))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Get state error: {e}")
            return None


if __name__ == "__main__":
    manager = StateManager()
    
    # Example usage
    manager.record_analysis(75, 'LONG', 0.85, {}, {})
    print("✅ Analysis recorded")
    
    trend = manager.get_trend(hours=24)
    print(f"Trend: {trend}")
    
    stats = manager.get_statistics()
    print(f"Stats: {stats}")
