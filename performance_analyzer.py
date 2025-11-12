"""
FILE 3: performance_analyzer.py - PHASE 2.1
Trade Takip + AI Accuracy + Gelişme Önerileri
%100 Real Data - PostgreSQL Database Integration
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from sqlalchemy import create_engine, Column, String, Float, DateTime, Boolean, func, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)
Base = declarative_base()


class TradeModel(Base):
    """Trade database model"""
    __tablename__ = 'trades'
    
    id = Column(String, primary_key=True)
    symbol = Column(String, nullable=False)
    direction = Column(String, nullable=False)  # LONG, SHORT
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime)
    position_size = Column(Float, nullable=False)
    tp1 = Column(Float)
    tp2 = Column(Float)
    sl = Column(Float)
    tp_distance = Column(Float)
    risk_reward = Column(Float)
    pnl = Column(Float)
    pnl_percent = Column(Float)
    status = Column(String, nullable=False)
    signal_type = Column(String)
    confidence = Column(Float)


class PerformanceAnalyzer:
    """Performance Analytics Engine - Production Ready"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL not configured")
        
        self.engine = create_engine(self.database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_trade_statistics(self, days: int = 7) -> Dict:
        """Get trade statistics (Win/Loss, P&L, etc.)"""
        try:
            session = self.Session()
            cutoff_date = datetime.now() - timedelta(days=days)
            
            trades = session.query(TradeModel).filter(
                TradeModel.exit_time >= cutoff_date
            ).all()
            
            if not trades:
                return self._empty_stats()
            
            closed_trades = [t for t in trades if t.status in ['TP1_HIT', 'TP2_HIT', 'SL_HIT']]
            wins = [t for t in closed_trades if t.pnl > 0]
            losses = [t for t in closed_trades if t.pnl < 0]
            
            total_wins = sum(t.pnl for t in wins)
            total_losses = abs(sum(t.pnl for t in losses))
            
            session.close()
            
            return {
                'total_trades': len(closed_trades),
                'win_trades': len(wins),
                'loss_trades': len(losses),
                'win_rate_percent': (len(wins) / len(closed_trades) * 100) if closed_trades else 0,
                'total_pnl': total_wins - total_losses,
                'avg_pnl': (total_wins - total_losses) / len(closed_trades) if closed_trades else 0,
                'best_trade': max([t.pnl for t in closed_trades]) if closed_trades else 0,
                'worst_trade': min([t.pnl for t in closed_trades]) if closed_trades else 0,
                'profit_factor': total_wins / total_losses if total_losses > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return self._empty_stats()
    
    def get_open_trades(self) -> List[Dict]:
        """Get all open trades"""
        try:
            session = self.Session()
            trades = session.query(TradeModel).filter(TradeModel.status == 'OPEN').all()
            
            result = []
            for trade in trades:
                result.append({
                    'id': trade.id,
                    'symbol': trade.symbol,
                    'direction': trade.direction,
                    'entry_price': trade.entry_price,
                    'tp1': trade.tp1,
                    'tp2': trade.tp2,
                    'sl': trade.sl,
                    'position_size': trade.position_size,
                    'entry_time': trade.entry_time.isoformat()
                })
            
            session.close()
            return result
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return []
    
    def get_signal_accuracy(self, days: int = 7) -> Dict:
        """Get AI signal accuracy"""
        try:
            session = self.Session()
            cutoff = datetime.now() - timedelta(days=days)
            
            trades = session.query(TradeModel).filter(
                TradeModel.exit_time >= cutoff
            ).all()
            
            if not trades:
                return {'accuracy': 0, 'total_signals': 0}
            
            correct = len([t for t in trades if t.pnl > 0])
            accuracy = (correct / len(trades) * 100) if trades else 0
            
            session.close()
            
            return {
                'total_signals': len(trades),
                'correct_signals': correct,
                'incorrect_signals': len(trades) - correct,
                'accuracy_percent': accuracy
            }
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return {}
    
    def get_best_performing_crypto(self, days: int = 7) -> str:
        """Get best performing crypto"""
        try:
            session = self.Session()
            cutoff = datetime.now() - timedelta(days=days)
            
            trades = session.query(TradeModel).filter(
                TradeModel.exit_time >= cutoff
            ).all()
            
            by_crypto = {}
            for trade in trades:
                crypto = trade.symbol.replace('USDT', '')
                if crypto not in by_crypto:
                    by_crypto[crypto] = 0
                by_crypto[crypto] += trade.pnl
            
            if not by_crypto:
                return 'N/A'
            
            best = max(by_crypto.items(), key=lambda x: x[1])
            session.close()
            
            return best[0]
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return 'N/A'
    
    def get_improvement_suggestions(self) -> List[str]:
        """AI-generated improvement suggestions"""
        try:
            session = self.Session()
            suggestions = []
            
            trades = session.query(TradeModel).all()
            
            if not trades:
                return suggestions
            
            # Check confidence
            high_conf = [t for t in trades if t.confidence > 75 and t.pnl > 0]
            if high_conf:
                accuracy = len(high_conf) / len([t for t in trades if t.confidence > 75]) * 100
                suggestions.append(f"Confidence > 75 signals {accuracy:.1f}% accurate - INCREASE threshold")
            
            # Check TP distance
            avg_tp_dist = np.mean([t.tp_distance for t in trades if t.tp_distance])
            if avg_tp_dist and avg_tp_dist < 0.5:
                suggestions.append(f"TP distance {avg_tp_dist:.2f}% - consider raising to 0.5-1.0%")
            
            # Direction bias
            long_trades = [t for t in trades if t.direction == 'LONG']
            short_trades = [t for t in trades if t.direction == 'SHORT']
            
            if long_trades and short_trades:
                long_acc = len([t for t in long_trades if t.pnl > 0]) / len(long_trades) * 100
                short_acc = len([t for t in short_trades if t.pnl > 0]) / len(short_trades) * 100
                
                if abs(long_acc - short_acc) > 15:
                    worse = 'SHORT' if short_acc < long_acc else 'LONG'
                    suggestions.append(f"{worse} signals {abs(long_acc - short_acc):.1f}% weaker - reduce bias")
            
            session.close()
            return suggestions
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return []
    
    def _empty_stats(self) -> Dict:
        """Return empty statistics"""
        return {
            'total_trades': 0,
            'win_trades': 0,
            'loss_trades': 0,
            'win_rate_percent': 0,
            'total_pnl': 0,
            'avg_pnl': 0,
            'best_trade': 0,
            'worst_trade': 0,
            'profit_factor': 0
        }


if __name__ == "__main__":
    analyzer = PerformanceAnalyzer()
    print("✅ PerformanceAnalyzer initialized")
