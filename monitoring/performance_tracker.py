"""
Performance Tracking
REAL metrics collection
REAL-time monitoring - 100% Policy
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PerformanceTracker:
    """Track performance REAL-TIME"""
    
    def __init__(self):
        self.trades = []
        self.signals = []
    
    def record_signal(self, signal):
        """Record signal"""
        try:
            self.signals.append({
                'timestamp': datetime.now(),
                'symbol': signal['symbol'],
                'type': signal['type'],
                'confidence': signal['confidence']
            })
            logger.info(f"✅ Signal recorded: {signal['symbol']}")
        except Exception as e:
            logger.error(f"Record error: {e}")
    
    def record_trade(self, trade):
        """Record trade"""
        try:
            self.trades.append({
                'timestamp': datetime.now(),
                'symbol': trade['symbol'],
                'pnl': trade.get('pnl', 0)
            })
        except Exception as e:
            logger.error(f"Trade error: {e}")
    
    def get_win_rate(self):
        """Calculate win rate"""
        try:
            if not self.trades:
                return 0.0
            wins = len([t for t in self.trades if t['pnl'] > 0])
            return (wins / len(self.trades)) * 100
        except:
            return 0.0
    
    def get_metrics(self):
        """Get ALL metrics"""
        return {
            'signals': len(self.signals),
            'trades': len(self.trades),
            'win_rate': self.get_win_rate()
        }

