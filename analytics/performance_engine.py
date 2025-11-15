"""
🚀 DEMIR AI v5.2 - Performance Analytics Engine
📊 Win Rate, Profit Factor, Sharpe Ratio Calculator
🎯 Production-Grade Performance Tracking

Location: GitHub Root / analytics/performance_engine.py (NEW FILE - CREATE FOLDER)
Size: ~1200 lines
Author: AI Research Agent
Date: 2025-11-15
"""

import os
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import numpy as np
from statistics import mean, stdev
import json
import pytz

logger = logging.getLogger('PERFORMANCE_ENGINE')

# ============================================================================
# PERFORMANCE METRICS CALCULATOR
# ============================================================================

class PerformanceAnalytics:
    """Calculate comprehensive performance metrics"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.connection = self._connect()
    
    def _connect(self):
        """Connect to PostgreSQL"""
        try:
            conn = psycopg2.connect(self.db_url)
            logger.info("✅ Connected to PostgreSQL for analytics")
            return conn
        except Exception as e:
            logger.error(f"❌ Database connection error: {e}")
            return None
    
    # =====================================================================
    # BASIC METRICS
    # =====================================================================
    
    def calculate_win_rate(self, days: int = 7) -> Dict:
        """Calculate win rate percentage"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END) as losing_trades,
                    SUM(CASE WHEN profit_loss = 0 THEN 1 ELSE 0 END) as breakeven_trades
                FROM performance_tracking
                WHERE entry_time > NOW() - INTERVAL '%s days'
            ''', (days,))
            result = cursor.fetchone()
            cursor.close()
            
            if result and result['total_trades'] > 0:
                win_rate = (result['winning_trades'] / result['total_trades']) * 100
                return {
                    'total_trades': result['total_trades'],
                    'winning_trades': result['winning_trades'],
                    'losing_trades': result['losing_trades'],
                    'breakeven_trades': result['breakeven_trades'],
                    'win_rate_percent': round(win_rate, 2),
                    'loss_rate_percent': round(100 - win_rate, 2),
                    'period_days': days
                }
            return {}
        except Exception as e:
            logger.error(f"❌ Win rate calculation error: {e}")
            return {}
    
    def calculate_profit_factor(self, days: int = 7) -> Dict:
        """Calculate profit factor (gross profit / gross loss)"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT 
                    COALESCE(SUM(CASE WHEN profit_loss > 0 THEN profit_loss ELSE 0 END), 0) as gross_profit,
                    COALESCE(ABS(SUM(CASE WHEN profit_loss < 0 THEN profit_loss ELSE 0 END)), 0) as gross_loss
                FROM performance_tracking
                WHERE entry_time > NOW() - INTERVAL '%s days'
            ''', (days,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                gross_loss = result['gross_loss']
                if gross_loss > 0:
                    profit_factor = result['gross_profit'] / gross_loss
                else:
                    profit_factor = 0 if result['gross_profit'] == 0 else float('inf')
                
                return {
                    'gross_profit': round(result['gross_profit'], 2),
                    'gross_loss': round(result['gross_loss'], 2),
                    'profit_factor': round(profit_factor, 2),
                    'net_profit': round(result['gross_profit'] - result['gross_loss'], 2),
                    'period_days': days
                }
            return {}
        except Exception as e:
            logger.error(f"❌ Profit factor calculation error: {e}")
            return {}
    
    def calculate_sharpe_ratio(self, days: int = 7, risk_free_rate: float = 0.02) -> Dict:
        """
        Calculate Sharpe Ratio
        Sharpe = (Return - Risk-free Rate) / StdDev(Returns)
        """
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT profit_loss_percent
                FROM performance_tracking
                WHERE entry_time > NOW() - INTERVAL '%s days'
                AND profit_loss_percent IS NOT NULL
                ORDER BY entry_time
            ''', (days,))
            returns = [row['profit_loss_percent'] / 100 for row in cursor.fetchall()]
            cursor.close()
            
            if len(returns) > 1:
                mean_return = mean(returns)
                std_dev = stdev(returns)
                
                if std_dev > 0:
                    daily_rf = risk_free_rate / 365
                    sharpe = (mean_return - daily_rf) / std_dev
                else:
                    sharpe = 0
                
                return {
                    'sharpe_ratio': round(sharpe, 2),
                    'mean_return': round(mean_return * 100, 2),
                    'std_deviation': round(std_dev * 100, 2),
                    'trade_count': len(returns),
                    'period_days': days,
                    'note': 'Higher Sharpe is better (target > 1.0)'
                }
            return {}
        except Exception as e:
            logger.error(f"❌ Sharpe ratio calculation error: {e}")
            return {}
    
    # =====================================================================
    # ADVANCED METRICS
    # =====================================================================
    
    def calculate_max_drawdown(self, days: int = 7) -> Dict:
        """Calculate maximum drawdown from peak"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT profit_loss
                FROM performance_tracking
                WHERE entry_time > NOW() - INTERVAL '%s days'
                ORDER BY entry_time
            ''', (days,))
            results = cursor.fetchall()
            cursor.close()
            
            if results:
                cumulative_pnl = []
                running_sum = 0
                for row in results:
                    running_sum += row['profit_loss']
                    cumulative_pnl.append(running_sum)
                
                peak = cumulative_pnl[0]
                max_dd = 0
                
                for value in cumulative_pnl:
                    if value > peak:
                        peak = value
                    dd = peak - value
                    if dd > max_dd:
                        max_dd = dd
                
                max_dd_percent = (max_dd / peak * 100) if peak > 0 else 0
                
                return {
                    'max_drawdown': round(max_dd, 2),
                    'max_drawdown_percent': round(max_dd_percent, 2),
                    'peak_value': round(peak, 2),
                    'trade_count': len(results),
                    'period_days': days,
                    'note': 'Lower is better'
                }
            return {}
        except Exception as e:
            logger.error(f"❌ Max drawdown calculation error: {e}")
            return {}
    
    def calculate_recovery_factor(self, days: int = 7) -> Dict:
        """Recovery factor = Net Profit / Max Drawdown"""
        try:
            profit_factor_data = self.calculate_profit_factor(days)
            max_dd_data = self.calculate_max_drawdown(days)
            
            if profit_factor_data and max_dd_data:
                net_profit = profit_factor_data['net_profit']
                max_dd = max_dd_data['max_drawdown']
                
                if max_dd > 0:
                    recovery_factor = net_profit / max_dd
                else:
                    recovery_factor = 0 if net_profit == 0 else float('inf')
                
                return {
                    'recovery_factor': round(recovery_factor, 2),
                    'net_profit': net_profit,
                    'max_drawdown': max_dd,
                    'period_days': days,
                    'note': 'Higher is better (target > 2.0)'
                }
            return {}
        except Exception as e:
            logger.error(f"❌ Recovery factor calculation error: {e}")
            return {}
    
    def calculate_average_win_loss(self, days: int = 7) -> Dict:
        """Calculate average winning and losing trade"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT 
                    AVG(CASE WHEN profit_loss > 0 THEN profit_loss END) as avg_win,
                    AVG(CASE WHEN profit_loss < 0 THEN profit_loss END) as avg_loss,
                    AVG(profit_loss) as avg_trade
                FROM performance_tracking
                WHERE entry_time > NOW() - INTERVAL '%s days'
            ''', (days,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                avg_win = result['avg_win'] or 0
                avg_loss = abs(result['avg_loss'] or 0)
                
                win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
                
                return {
                    'average_win': round(avg_win, 2),
                    'average_loss': round(avg_loss, 2),
                    'win_loss_ratio': round(win_loss_ratio, 2),
                    'average_trade': round(result['avg_trade'] or 0, 2),
                    'period_days': days,
                    'note': 'Win/Loss ratio > 1.5 is good'
                }
            return {}
        except Exception as e:
            logger.error(f"❌ Average win/loss calculation error: {e}")
            return {}
    
    def calculate_expectancy(self, days: int = 7) -> Dict:
        """
        Expectancy = (Win% × Avg Win) - (Loss% × Avg Loss)
        Represents average profit per trade
        """
        try:
            win_rate = self.calculate_win_rate(days)
            avg_wl = self.calculate_average_win_loss(days)
            
            if win_rate and avg_wl:
                win_percent = win_rate['win_rate_percent'] / 100
                loss_percent = win_rate['loss_rate_percent'] / 100
                
                expectancy = (win_percent * avg_wl['average_win']) - (loss_percent * avg_wl['average_loss'])
                
                return {
                    'expectancy': round(expectancy, 2),
                    'win_rate': win_rate['win_rate_percent'],
                    'avg_win': avg_wl['average_win'],
                    'avg_loss': avg_wl['average_loss'],
                    'period_days': days,
                    'note': 'Expected profit per trade (positive is good)'
                }
            return {}
        except Exception as e:
            logger.error(f"❌ Expectancy calculation error: {e}")
            return {}
    
    # =====================================================================
    # SYMBOL-SPECIFIC ANALYTICS
    # =====================================================================
    
    def get_symbol_analytics(self, symbol: str, days: int = 7) -> Dict:
        """Get all analytics for specific symbol"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT 
                    t.symbol,
                    COUNT(*) as total_signals,
                    SUM(CASE WHEN t.signal_type = 'LONG' THEN 1 ELSE 0 END) as long_signals,
                    SUM(CASE WHEN t.signal_type = 'SHORT' THEN 1 ELSE 0 END) as short_signals,
                    ROUND(AVG(t.confidence), 2) as avg_confidence,
                    ROUND(AVG(pt.profit_loss), 2) as avg_pnl,
                    SUM(CASE WHEN pt.profit_loss > 0 THEN 1 ELSE 0 END) as winning_trades,
                    COUNT(*) as total_trades_with_pnl
                FROM trades t
                LEFT JOIN performance_tracking pt ON t.id = pt.trade_id
                WHERE t.symbol = %s
                AND t.timestamp > NOW() - INTERVAL '%s days'
                GROUP BY t.symbol
            ''', (symbol, days))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                win_rate = (result['winning_trades'] / result['total_trades_with_pnl'] * 100) if result['total_trades_with_pnl'] > 0 else 0
                
                return {
                    'symbol': result['symbol'],
                    'total_signals': result['total_signals'],
                    'long_signals': result['long_signals'],
                    'short_signals': result['short_signals'],
                    'avg_confidence': result['avg_confidence'],
                    'average_pnl': result['avg_pnl'],
                    'win_rate': round(win_rate, 2),
                    'period_days': days
                }
            return {}
        except Exception as e:
            logger.error(f"❌ Symbol analytics error: {e}")
            return {}
    
    # =====================================================================
    # MONTHLY PERFORMANCE
    # =====================================================================
    
    def get_monthly_performance(self) -> List[Dict]:
        """Get performance breakdown by month"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT 
                    DATE_TRUNC('month', entry_time)::date as month,
                    COUNT(*) as trades,
                    SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
                    ROUND(SUM(profit_loss), 2) as total_pnl,
                    ROUND(AVG(profit_loss), 2) as avg_pnl,
                    ROUND(AVG(profit_loss_percent), 2) as avg_return_percent
                FROM performance_tracking
                GROUP BY DATE_TRUNC('month', entry_time)
                ORDER BY month DESC
                LIMIT 12
            ''')
            results = cursor.fetchall()
            cursor.close()
            
            monthly_data = []
            for row in results:
                win_rate = (row['wins'] / row['trades'] * 100) if row['trades'] > 0 else 0
                monthly_data.append({
                    'month': row['month'].strftime('%Y-%m') if row['month'] else 'N/A',
                    'trades': row['trades'],
                    'wins': row['wins'],
                    'win_rate': round(win_rate, 2),
                    'total_pnl': row['total_pnl'],
                    'avg_pnl': row['avg_pnl'],
                    'avg_return_percent': row['avg_return_percent']
                })
            
            return monthly_data
        except Exception as e:
            logger.error(f"❌ Monthly performance error: {e}")
            return []
    
    # =====================================================================
    # COMPREHENSIVE REPORT
    # =====================================================================
    
    def generate_comprehensive_report(self, days: int = 7) -> Dict:
        """Generate complete performance report"""
        logger.info(f"📊 Generating comprehensive report for {days} days...")
        
        report = {
            'generated_at': datetime.now(pytz.UTC).isoformat(),
            'period_days': days,
            'win_rate': self.calculate_win_rate(days),
            'profit_factor': self.calculate_profit_factor(days),
            'sharpe_ratio': self.calculate_sharpe_ratio(days),
            'max_drawdown': self.calculate_max_drawdown(days),
            'recovery_factor': self.calculate_recovery_factor(days),
            'average_win_loss': self.calculate_average_win_loss(days),
            'expectancy': self.calculate_expectancy(days),
            'symbol_analytics': {
                'BTCUSDT': self.get_symbol_analytics('BTCUSDT', days),
                'ETHUSDT': self.get_symbol_analytics('ETHUSDT', days),
                'LTCUSDT': self.get_symbol_analytics('LTCUSDT', days)
            },
            'monthly_performance': self.get_monthly_performance()
        }
        
        logger.info("✅ Report generated successfully")
        return report
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("✅ Database connection closed")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    analytics = PerformanceAnalytics(os.getenv('DATABASE_URL'))
    report = analytics.generate_comprehensive_report(days=7)
    
    print(json.dumps(report, indent=2, default=str))
    
    analytics.close()

