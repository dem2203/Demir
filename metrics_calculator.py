#!/usr/bin/env python3
"""
🔱 DEMIR AI - Metrics Calculator v1.0
HAFTA 11-12: Advanced Performance Metrics Calculation

KURALLAR:
✅ Sharpe ratio, Sortino ratio calculation
✅ Max drawdown, recovery time
✅ Profit factor, expectancy
✅ Risk-adjusted returns
✅ Real-time calculations
✅ Error loud - all metrics logged
"""

import os
import psycopg2
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL')
RISK_FREE_RATE = 0.02  # 2% annual
TRADING_DAYS = 252

# ============================================================================
# RETURN METRICS
# ============================================================================

class ReturnMetrics:
    """Calculate return-based metrics"""
    
    @staticmethod
    def calculate_cumulative_return(trades: List[float]) -> float:
        """Calculate cumulative return"""
        if not trades or len(trades) == 0:
            return 0
        
        cumulative = np.prod(1 + np.array(trades))
        return cumulative - 1
    
    @staticmethod
    def calculate_cagr(trades: List[float], years: float) -> float:
        """Calculate Compound Annual Growth Rate"""
        if years <= 0 or not trades:
            return 0
        
        cumulative_return = np.prod(1 + np.array(trades))
        cagr = (cumulative_return ** (1 / years)) - 1
        
        return cagr
    
    @staticmethod
    def calculate_total_return_pct(pnl_list: List[float], initial_capital: float = 10000) -> float:
        """Calculate total return percentage"""
        total_pnl = sum(pnl_list)
        return (total_pnl / initial_capital) * 100

# ============================================================================
# RISK METRICS
# ============================================================================

class RiskMetrics:
    """Calculate risk-adjusted metrics"""
    
    @staticmethod
    def calculate_sharpe_ratio(returns: np.ndarray, risk_free_rate: float = RISK_FREE_RATE) -> float:
        """Calculate Sharpe Ratio"""
        if len(returns) == 0:
            return 0
        
        excess_returns = returns - (risk_free_rate / TRADING_DAYS)
        sharpe = np.mean(excess_returns) / (np.std(excess_returns) + 1e-10)
        sharpe_annualized = sharpe * np.sqrt(TRADING_DAYS)
        
        logger.info(f"📊 Sharpe Ratio: {sharpe_annualized:.2f}")
        return sharpe_annualized
    
    @staticmethod
    def calculate_sortino_ratio(returns: np.ndarray, risk_free_rate: float = RISK_FREE_RATE) -> float:
        """Calculate Sortino Ratio"""
        if len(returns) == 0:
            return 0
        
        excess_returns = returns - (risk_free_rate / TRADING_DAYS)
        downside_returns = excess_returns[excess_returns < 0]
        
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
        sortino = np.mean(excess_returns) / (downside_std + 1e-10)
        sortino_annualized = sortino * np.sqrt(TRADING_DAYS)
        
        logger.info(f"📊 Sortino Ratio: {sortino_annualized:.2f}")
        return sortino_annualized
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: np.ndarray) -> Tuple[float, int]:
        """Calculate max drawdown and recovery days"""
        if len(equity_curve) == 0:
            return 0, 0
        
        running_max = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - running_max) / running_max
        
        max_drawdown = np.min(drawdown)
        max_drawdown_idx = np.argmin(drawdown)
        
        # Recovery time
        recovery_idx = None
        for i in range(max_drawdown_idx + 1, len(equity_curve)):
            if equity_curve[i] >= running_max[max_drawdown_idx]:
                recovery_idx = i
                break
        
        recovery_days = recovery_idx - max_drawdown_idx if recovery_idx else 0
        
        logger.info(f"📊 Max Drawdown: {max_drawdown*100:.2f}% | Recovery: {recovery_days} days")
        return max_drawdown, recovery_days
    
    @staticmethod
    def calculate_calmar_ratio(cagr: float, max_drawdown: float) -> float:
        """Calculate Calmar Ratio"""
        if max_drawdown == 0:
            return 0
        
        calmar = cagr / abs(max_drawdown)
        logger.info(f"📊 Calmar Ratio: {calmar:.2f}")
        return calmar

# ============================================================================
# TRADE METRICS
# ============================================================================

class TradeMetrics:
    """Calculate trade-based metrics"""
    
    @staticmethod
    def calculate_win_metrics(trades: List[Dict]) -> Dict:
        """Calculate win/loss metrics"""
        if not trades or len(trades) == 0:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'largest_win': 0,
                'largest_loss': 0
            }
        
        pnls = [t['pnl'] for t in trades if 'pnl' in t]
        
        winning_trades = len([p for p in pnls if p > 0])
        losing_trades = len([p for p in pnls if p < 0])
        total_trades = len(pnls)
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        winning_pnls = [p for p in pnls if p > 0]
        losing_pnls = [p for p in pnls if p < 0]
        
        avg_win = np.mean(winning_pnls) if winning_pnls else 0
        avg_loss = np.mean(losing_pnls) if losing_pnls else 0
        
        largest_win = max(pnls) if pnls else 0
        largest_loss = min(pnls) if pnls else 0
        
        metrics = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': abs(avg_loss),
            'largest_win': largest_win,
            'largest_loss': largest_loss
        }
        
        logger.info(f"📊 Trade Metrics: {total_trades} trades, WR={win_rate:.1%}")
        return metrics
    
    @staticmethod
    def calculate_profit_factor(trades: List[Dict]) -> float:
        """Calculate profit factor"""
        if not trades or len(trades) == 0:
            return 0
        
        pnls = [t['pnl'] for t in trades if 'pnl' in t]
        
        gross_profit = sum([p for p in pnls if p > 0])
        gross_loss = abs(sum([p for p in pnls if p < 0]))
        
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        logger.info(f"📊 Profit Factor: {profit_factor:.2f}")
        return profit_factor
    
    @staticmethod
    def calculate_expectancy(trades: List[Dict]) -> float:
        """Calculate mathematical expectancy per trade"""
        if not trades or len(trades) == 0:
            return 0
        
        pnls = [t['pnl'] for t in trades if 'pnl' in t]
        expectancy = np.mean(pnls)
        
        logger.info(f"📊 Expectancy per trade: ${expectancy:.2f}")
        return expectancy

# ============================================================================
# DATABASE METRICS STORAGE
# ============================================================================

class MetricsCalculationEngine:
    """Main metrics calculation engine"""
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
    
    def calculate_all_metrics(self) -> Dict:
        """Calculate all metrics"""
        try:
            logger.info("=" * 80)
            logger.info("🧮 CALCULATING ALL METRICS")
            logger.info("=" * 80)
            
            # Fetch all closed trades
            query = """
                SELECT pnl FROM manual_trades
                WHERE exit_time IS NOT NULL
                ORDER BY exit_time ASC
            """
            
            df = pd.read_sql_query(query, self.db_conn)
            
            if df.empty:
                logger.warning("⚠️ No closed trades")
                return {}
            
            trades = [{'pnl': float(p)} for p in df['pnl'].values]
            
            # Calculate returns
            pnls = [t['pnl'] for t in trades]
            equity_curve = np.cumsum(pnls)
            returns = np.array(pnls) / 10000  # Normalize by initial capital
            
            # Calculate metrics
            metrics = {}
            
            # Return metrics
            metrics['cumulative_return'] = ReturnMetrics.calculate_cumulative_return(returns)
            metrics['cagr'] = ReturnMetrics.calculate_cagr(returns, 1)  # 1 year approx
            metrics['total_return_pct'] = ReturnMetrics.calculate_total_return_pct(pnls)
            
            # Risk metrics
            metrics['sharpe_ratio'] = RiskMetrics.calculate_sharpe_ratio(returns)
            metrics['sortino_ratio'] = RiskMetrics.calculate_sortino_ratio(returns)
            max_dd, recovery = RiskMetrics.calculate_max_drawdown(equity_curve)
            metrics['max_drawdown'] = max_dd
            metrics['recovery_days'] = recovery
            metrics['calmar_ratio'] = RiskMetrics.calculate_calmar_ratio(metrics['cagr'], max_dd)
            
            # Trade metrics
            trade_metrics = TradeMetrics.calculate_win_metrics(trades)
            metrics.update(trade_metrics)
            
            metrics['profit_factor'] = TradeMetrics.calculate_profit_factor(trades)
            metrics['expectancy'] = TradeMetrics.calculate_expectancy(trades)
            
            logger.info("\n" + "=" * 80)
            logger.info("✅ METRICS CALCULATION COMPLETED")
            logger.info("=" * 80)
            
            return metrics
        
        except Exception as e:
            logger.error(f"❌ Metrics calculation failed: {e}")
            return {}
    
    def save_metrics(self, metrics: Dict):
        """Save metrics to database"""
        try:
            cur = self.db_conn.cursor()
            
            insert_query = """
                INSERT INTO performance_metrics_calculated
                (timestamp, metric_name, metric_value)
                VALUES (%s, %s, %s)
            """
            
            for metric_name, metric_value in metrics.items():
                cur.execute(insert_query, (
                    datetime.now(),
                    metric_name,
                    float(metric_value) if isinstance(metric_value, (int, float)) else metric_value
                ))
            
            self.db_conn.commit()
            logger.info(f"💾 Saved {len(metrics)} metrics")
            cur.close()
        
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"❌ Failed to save metrics: {e}")

# ============================================================================
# REPORT GENERATOR
# ============================================================================

class MetricsReport:
    """Generate metrics report"""
    
    @staticmethod
    def generate_report(metrics: Dict) -> str:
        """Generate text report"""
        report = []
        report.append("\n" + "=" * 80)
        report.append("🔱 DEMIR AI - PERFORMANCE METRICS REPORT")
        report.append("=" * 80 + "\n")
        
        # Return metrics
        report.append("📊 RETURN METRICS:")
        report.append(f"  Cumulative Return: {metrics.get('cumulative_return', 0)*100:.2f}%")
        report.append(f"  Total Return: {metrics.get('total_return_pct', 0):.2f}%")
        report.append(f"  CAGR: {metrics.get('cagr', 0)*100:.2f}%\n")
        
        # Risk metrics
        report.append("⚠️ RISK METRICS:")
        report.append(f"  Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
        report.append(f"  Sortino Ratio: {metrics.get('sortino_ratio', 0):.2f}")
        report.append(f"  Max Drawdown: {metrics.get('max_drawdown', 0)*100:.2f}%")
        report.append(f"  Recovery Days: {metrics.get('recovery_days', 0)}")
        report.append(f"  Calmar Ratio: {metrics.get('calmar_ratio', 0):.2f}\n")
        
        # Trade metrics
        report.append("📈 TRADE METRICS:")
        report.append(f"  Total Trades: {metrics.get('total_trades', 0)}")
        report.append(f"  Win Rate: {metrics.get('win_rate', 0)*100:.1f}%")
        report.append(f"  Avg Win: ${metrics.get('avg_win', 0):.2f}")
        report.append(f"  Avg Loss: ${metrics.get('avg_loss', 0):.2f}")
        report.append(f"  Largest Win: ${metrics.get('largest_win', 0):.2f}")
        report.append(f"  Largest Loss: ${metrics.get('largest_loss', 0):.2f}\n")
        
        # Efficiency metrics
        report.append("🎯 EFFICIENCY METRICS:")
        report.append(f"  Profit Factor: {metrics.get('profit_factor', 0):.2f}")
        report.append(f"  Expectancy: ${metrics.get('expectancy', 0):.2f} per trade\n")
        
        report.append("=" * 80)
        
        return "\n".join(report)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    try:
        logger.info("=" * 80)
        logger.info("🚀 DEMIR AI - METRICS CALCULATOR (HAFTA 11-12)")
        logger.info("=" * 80)
        
        db_conn = psycopg2.connect(DATABASE_URL)
        
        engine = MetricsCalculationEngine(db_conn)
        metrics = engine.calculate_all_metrics()
        
        if metrics:
            engine.save_metrics(metrics)
            
            # Generate report
            report = MetricsReport.generate_report(metrics)
            logger.info(report)
        
        logger.info("\n✅ METRICS CALCULATION COMPLETED")
        
        db_conn.close()
    
    except Exception as e:
        logger.critical(f"❌ FATAL ERROR: {e}")
        raise

if __name__ == "__main__":
    main()
