# trade_analyzer.py - Trade Analysis

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class TradeAnalyzer:
    """Analyze trading performance"""
    
    def __init__(self):
        self.trades_df = None
    
    def load_trades(self, trades_list):
        """Load trades for analysis"""
        self.trades_df = pd.DataFrame(trades_list)
    
    def analyze_by_symbol(self):
        """Analyze performance by symbol"""
        if self.trades_df is None or self.trades_df.empty:
            return {}
        
        analysis = {}
        for symbol in self.trades_df['symbol'].unique():
            symbol_trades = self.trades_df[self.trades_df['symbol'] == symbol]
            
            analysis[symbol] = {
                'count': len(symbol_trades),
                'win_rate': len(symbol_trades[symbol_trades['pnl'] > 0]) / len(symbol_trades),
                'avg_pnl': symbol_trades['pnl'].mean(),
                'total_pnl': symbol_trades['pnl'].sum()
            }
        
        return analysis
    
    def analyze_by_time(self, period='H'):
        """Analyze performance by time period"""
        if self.trades_df is None or self.trades_df.empty:
            return {}
        
        self.trades_df['time_period'] = pd.to_datetime(self.trades_df['timestamp']).dt.floor(period)
        
        return self.trades_df.groupby('time_period').agg({
            'pnl': ['sum', 'mean', 'count']
        }).to_dict()
