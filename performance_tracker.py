#!/usr/bin/env python3
"""
🔱 DEMIR AI - Performance Tracker v1.0
HAFTA 12: Daily Metrics + Live Dashboard Data

KURALLAR:
✅ Daily P&L tracking
✅ Real-time performance metrics
✅ Monthly/Weekly summaries
✅ Win rate + trade statistics
✅ Database metrics update
✅ Streaming to dashboard
✅ Error loud - all metrics logged
"""

import os
import psycopg2
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL')
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']

# ============================================================================
# PERFORMANCE CALCULATOR
# ============================================================================

class PerformanceCalculator:
    """Calculate real-time performance metrics"""
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
    
    def get_daily_pnl(self) -> Dict:
        """Get today's P&L"""
        try:
            query = """
                SELECT 
                    COALESCE(SUM(pnl), 0) as total_pnl,
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades
                FROM manual_trades
                WHERE DATE(exit_time) = CURRENT_DATE
                AND exit_time IS NOT NULL
            """
            
            df = pd.read_sql_query(query, self.db_conn)
            
            row = df.iloc[0]
            total_pnl = row['total_pnl']
            total_trades = row['total_trades']
            winning_trades = row['winning_trades']
            losing_trades = row['losing_trades']
            
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            result = {
                'date': datetime.now().date(),
                'total_pnl': float(total_pnl),
                'total_trades': int(total_trades),
                'winning_trades': int(winning_trades),
                'losing_trades': int(losing_trades),
                'win_rate': float(win_rate)
            }
            
            logger.info(f"✅ Daily metrics: P&L=${total_pnl:.2f}, {total_trades} trades, WR={win_rate:.1%}")
            return result
        
        except Exception as e:
            logger.error(f"❌ Daily P&L calculation failed: {e}")
            return {}
    
    def get_weekly_pnl(self) -> Dict:
        """Get this week's P&L"""
        try:
            query = """
                SELECT 
                    COALESCE(SUM(pnl), 0) as total_pnl,
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                    MIN(pnl) as max_loss,
                    MAX(pnl) as max_win
                FROM manual_trades
                WHERE DATE(exit_time) >= DATE_TRUNC('week', CURRENT_DATE)
                AND exit_time IS NOT NULL
            """
            
            df = pd.read_sql_query(query, self.db_conn)
            row = df.iloc[0]
            
            total_trades = row['total_trades']
            win_rate = row['winning_trades'] / total_trades if total_trades > 0 else 0
            
            result = {
                'period': 'WEEKLY',
                'total_pnl': float(row['total_pnl']),
                'total_trades': int(total_trades),
                'winning_trades': int(row['winning_trades']),
                'win_rate': float(win_rate),
                'max_win': float(row['max_win']),
                'max_loss': float(row['max_loss'])
            }
            
            logger.info(f"✅ Weekly metrics: P&L=${row['total_pnl']:.2f}, WR={win_rate:.1%}")
            return result
        
        except Exception as e:
            logger.error(f"❌ Weekly P&L calculation failed: {e}")
            return {}
    
    def get_monthly_pnl(self) -> Dict:
        """Get this month's P&L"""
        try:
            query = """
                SELECT 
                    COALESCE(SUM(pnl), 0) as total_pnl,
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                    AVG(pnl) as avg_pnl,
                    MAX(pnl) as max_win,
                    MIN(pnl) as max_loss
                FROM manual_trades
                WHERE DATE_TRUNC('month', exit_time) = DATE_TRUNC('month', CURRENT_DATE)
                AND exit_time IS NOT NULL
            """
            
            df = pd.read_sql_query(query, self.db_conn)
            row = df.iloc[0]
            
            total_trades = row['total_trades']
            win_rate = row['winning_trades'] / total_trades if total_trades > 0 else 0
            
            result = {
                'period': 'MONTHLY',
                'total_pnl': float(row['total_pnl']),
                'total_trades': int(total_trades),
                'winning_trades': int(row['winning_trades']),
                'win_rate': float(win_rate),
                'avg_pnl': float(row['avg_pnl']),
                'max_win': float(row['max_win']),
                'max_loss': float(row['max_loss'])
            }
            
            logger.info(f"✅ Monthly metrics: P&L=${row['total_pnl']:.2f}, Trades={total_trades}")
            return result
        
        except Exception as e:
            logger.error(f"❌ Monthly P&L calculation failed: {e}")
            return {}
    
    def get_symbol_performance(self) -> Dict:
        """Get per-symbol performance"""
        try:
            query = """
                SELECT 
                    symbol,
                    COUNT(*) as total_trades,
                    COALESCE(SUM(pnl), 0) as total_pnl,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                    AVG(pnl) as avg_pnl,
                    MAX(pnl) as max_win
                FROM manual_trades
                WHERE exit_time IS NOT NULL
                GROUP BY symbol
                ORDER BY total_pnl DESC
            """
            
            df = pd.read_sql_query(query, self.db_conn)
            
            results = []
            for _, row in df.iterrows():
                total_trades = row['total_trades']
                win_rate = row['winning_trades'] / total_trades if total_trades > 0 else 0
                
                results.append({
                    'symbol': row['symbol'],
                    'total_trades': int(total_trades),
                    'total_pnl': float(row['total_pnl']),
                    'win_rate': float(win_rate),
                    'avg_pnl': float(row['avg_pnl']),
                    'max_win': float(row['max_win'])
                })
            
            logger.info(f"✅ Symbol performance calculated for {len(results)} symbols")
            return results
        
        except Exception as e:
            logger.error(f"❌ Symbol performance calculation failed: {e}")
            return []

# ============================================================================
# METRICS STORAGE
# ============================================================================

class MetricsStorage:
    """Store metrics for dashboard"""
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
    
    def save_daily_metrics(self, metrics: Dict):
        """Save daily metrics"""
        try:
            cur = self.db_conn.cursor()
            
            insert_query = """
                INSERT INTO trading_stats 
                (date, symbol, daily_pnl, total_trades, win_rate, winning_trades)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (date, symbol) DO UPDATE SET
                daily_pnl = EXCLUDED.daily_pnl,
                total_trades = EXCLUDED.total_trades,
                win_rate = EXCLUDED.win_rate
            """
            
            cur.execute(insert_query, (
                metrics['date'],
                'PORTFOLIO',
                metrics['total_pnl'],
                metrics['total_trades'],
                metrics['win_rate'],
                metrics['winning_trades']
            ))
            
            self.db_conn.commit()
            logger.info(f"💾 Daily metrics saved")
            cur.close()
        
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"❌ Failed to save daily metrics: {e}")
    
    def save_performance_metrics(self, symbol: str, metrics: Dict):
        """Save performance metrics"""
        try:
            cur = self.db_conn.cursor()
            
            insert_query = """
                INSERT INTO performance_metrics 
                (timestamp, symbol, total_pnl, win_rate, sharpe_ratio, max_drawdown)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cur.execute(insert_query, (
                datetime.now(),
                symbol,
                metrics.get('total_pnl', 0),
                metrics.get('win_rate', 0),
                metrics.get('sharpe_ratio', 0),
                metrics.get('max_drawdown', 0)
            ))
            
            self.db_conn.commit()
            logger.info(f"💾 Performance metrics saved for {symbol}")
            cur.close()
        
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"❌ Failed to save performance metrics: {e}")

# ============================================================================
# DASHBOARD DATA GENERATOR
# ============================================================================

class DashboardDataGenerator:
    """Generate data for Streamlit dashboard"""
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self.calculator = PerformanceCalculator(db_conn)
        self.storage = MetricsStorage(db_conn)
    
    def generate_dashboard_data(self) -> Dict:
        """Generate all dashboard data"""
        try:
            logger.info("📊 Generating dashboard data...")
            
            # Get metrics
            daily = self.calculator.get_daily_pnl()
            weekly = self.calculator.get_weekly_pnl()
            monthly = self.calculator.get_monthly_pnl()
            symbol_perf = self.calculator.get_symbol_performance()
            
            # Save metrics
            if daily:
                self.storage.save_daily_metrics(daily)
            
            dashboard_data = {
                'timestamp': datetime.now().isoformat(),
                'daily': daily,
                'weekly': weekly,
                'monthly': monthly,
                'by_symbol': symbol_perf
            }
            
            logger.info("✅ Dashboard data generated")
            return dashboard_data
        
        except Exception as e:
            logger.error(f"❌ Dashboard data generation failed: {e}")
            return {}

# ============================================================================
# ALERTS & NOTIFICATIONS
# ============================================================================

class PerformanceAlerts:
    """Generate performance alerts"""
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
    
    def check_performance_thresholds(self) -> List[str]:
        """Check if performance exceeds thresholds"""
        alerts = []
        
        try:
            calculator = PerformanceCalculator(self.db_conn)
            
            # Check daily loss
            daily = calculator.get_daily_pnl()
            if daily and daily['total_pnl'] < -500:
                alerts.append(f"⚠️ Daily loss limit reached: ${daily['total_pnl']:.2f}")
            
            # Check win rate
            if daily and daily['win_rate'] < 0.45:
                alerts.append(f"⚠️ Win rate below threshold: {daily['win_rate']:.1%}")
            
            # Check consecutive losses
            query = """
                SELECT COUNT(*) as consecutive_losses
                FROM manual_trades
                WHERE pnl < 0
                AND exit_time >= NOW() - INTERVAL '1 day'
            """
            
            df = pd.read_sql_query(query, self.db_conn)
            if df.iloc[0]['consecutive_losses'] > 5:
                alerts.append(f"⚠️ Multiple consecutive losses detected")
            
            if alerts:
                logger.warning(f"🚨 Performance alerts: {alerts}")
            
            return alerts
        
        except Exception as e:
            logger.error(f"❌ Alert check failed: {e}")
            return []

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    try:
        logger.info("=" * 80)
        logger.info("🚀 DEMIR AI - PERFORMANCE TRACKER (HAFTA 12)")
        logger.info("=" * 80)
        
        db_conn = psycopg2.connect(DATABASE_URL)
        
        # Generate dashboard data
        generator = DashboardDataGenerator(db_conn)
        dashboard_data = generator.generate_dashboard_data()
        
        logger.info(f"📊 Dashboard data: {dashboard_data}")
        
        # Check alerts
        alerts = PerformanceAlerts(db_conn).check_performance_thresholds()
        
        if alerts:
            for alert in alerts:
                logger.warning(alert)
        
        logger.info("=" * 80)
        logger.info("✅ PERFORMANCE TRACKER COMPLETED")
        logger.info("=" * 80)
        
        db_conn.close()
    
    except Exception as e:
        logger.critical(f"❌ FATAL ERROR: {e}")
        raise

if __name__ == "__main__":
    main()
