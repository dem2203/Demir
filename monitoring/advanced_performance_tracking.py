```python
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging
from datetime import datetime, timedelta
import sqlite3

logger = logging.getLogger(__name__)

class AdvancedPerformanceTracker:
    """
    Professional trading performance tracking
    Risk metrics, attribution, drawdown analysis
    """
    
    def __init__(self, db_path: str = "performance.db"):
        self.db_path = db_path
        self.trades = []
        self.daily_performance = {}
        self.risk_metrics = {}
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for trades"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME,
                symbol TEXT,
                side TEXT,
                entry_price REAL,
                exit_price REAL,
                quantity REAL,
                pnl REAL,
                pnl_percent REAL,
                duration_seconds INTEGER,
                risk_reward_ratio REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_trade(self, symbol: str, side: str, entry: float, 
                    exit: float, qty: float, duration: int):
        """Record REAL trade with all metrics"""
        
        pnl = (exit - entry) * qty if side == 'LONG' else (entry - exit) * qty
        pnl_percent = (exit - entry) / entry * 100 if side == 'LONG' else (entry - exit) / entry * 100
        
        trade = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'side': side,
            'entry': entry,
            'exit': exit,
            'qty': qty,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'duration': duration
        }
        
        self.trades.append(trade)
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO trades VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade['timestamp'], trade['symbol'], trade['side'],
            trade['entry'], trade['exit'], trade['qty'],
            trade['pnl'], trade['pnl_percent'], trade['duration'], 0
        ))
        conn.commit()
        conn.close()
    
    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if not self.trades:
            return 0.0
        
        returns = np.array([t['pnl_percent']/100 for t in self.trades])
        
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        sharpe = (avg_return - risk_free_rate/252) / std_return * np.sqrt(252)
        
        return sharpe
    
    def calculate_sortino_ratio(self, target_return: float = 0.0) -> float:
        """Calculate Sortino ratio"""
        if not self.trades:
            return 0.0
        
        returns = np.array([t['pnl_percent']/100 for t in self.trades])
        
        excess_returns = returns - target_return
        downside_deviation = np.sqrt(np.mean(np.minimum(excess_returns, 0)**2))
        
        if downside_deviation == 0:
            return 0.0
        
        sortino = np.mean(excess_returns) / downside_deviation * np.sqrt(252)
        
        return sortino
    
    def calculate_max_drawdown(self) -> Tuple[float, int, int]:
        """Calculate maximum drawdown"""
        if not self.trades:
            return 0.0, 0, 0
        
        cumulative_returns = []
        cumsum = 0
        
        for trade in self.trades:
            cumsum += trade['pnl']
            cumulative_returns.append(cumsum)
        
        cumulative_returns = np.array(cumulative_returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / (running_max + 1e-9)
        
        max_dd_idx = np.argmin(drawdown)
        max_dd = abs(drawdown[max_dd_idx])
        
        return max_dd, max_dd_idx, len(self.trades)
    
    def calculate_profit_factor(self) -> float:
        """Calculate profit factor"""
        if not self.trades:
            return 0.0
        
        wins = sum([t['pnl'] for t in self.trades if t['pnl'] > 0])
        losses = abs(sum([t['pnl'] for t in self.trades if t['pnl'] < 0]))
        
        if losses == 0:
            return 0.0
        
        return wins / losses
    
    def get_comprehensive_stats(self) -> Dict:
        """Get all performance metrics"""
        
        if not self.trades:
            return {}
        
        wins = len([t for t in self.trades if t['pnl'] > 0])
        losses = len([t for t in self.trades if t['pnl'] < 0])
        total = len(self.trades)
        
        return {
            'total_trades': total,
            'winning_trades': wins,
            'losing_trades': losses,
            'win_rate': wins / total * 100,
            'gross_profit': sum([t['pnl'] for t in self.trades if t['pnl'] > 0]),
            'gross_loss': sum([t['pnl'] for t in self.trades if t['pnl'] < 0]),
            'net_profit': sum([t['pnl'] for t in self.trades]),
            'avg_trade_pnl': np.mean([t['pnl'] for t in self.trades]),
            'sharpe_ratio': self.calculate_sharpe_ratio(),
            'sortino_ratio': self.calculate_sortino_ratio(),
            'profit_factor': self.calculate_profit_factor(),
            'max_drawdown': self.calculate_max_drawdown()[0]
        }
