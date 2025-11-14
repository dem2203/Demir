# backtest_engine.py - Backtesting Engine

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BacktestEngine:
    """Backtest trading strategies on historical data"""
    
    def __init__(self, starting_capital=10000, commission=0.001):
        self.capital = starting_capital
        self.starting_capital = starting_capital
        self.commission = commission
        self.trades = []
        self.portfolio_history = []
    
    def simulate_trade(self, entry_price, exit_price, quantity, trade_type='LONG'):
        """Simulate single trade"""
        try:
            if trade_type == 'LONG':
                pnl = (exit_price - entry_price) * quantity
            else:
                pnl = (entry_price - exit_price) * quantity
            
            commission = (entry_price * quantity + exit_price * quantity) * self.commission
            net_pnl = pnl - commission
            
            self.capital += net_pnl
            
            self.trades.append({
                'entry': entry_price,
                'exit': exit_price,
                'quantity': quantity,
                'type': trade_type,
                'pnl': net_pnl
            })
            
            return net_pnl
        
        except Exception as e:
            logger.error(f"Simulation error: {e}")
            return 0
    
    def get_results(self):
        """Get backtest results"""
        total_return = (self.capital - self.starting_capital) / self.starting_capital
        win_rate = len([t for t in self.trades if t['pnl'] > 0]) / len(self.trades) if self.trades else 0
        
        return {
            'total_capital': self.capital,
            'total_return': total_return,
            'win_rate': win_rate,
            'total_trades': len(self.trades),
            'total_pnl': sum([t['pnl'] for t in self.trades])
        }
