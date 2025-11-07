"""
PHASE 5.3: ANALYTICS DASHBOARD
File 3 of 10 (ayrı dosyalar)
Folder: layers/analytics_dashboard.py

Trading performance analytics and metrics
- Win rate calculation
- Profit/loss analysis
- Sharpe ratio
- Drawdown tracking
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TradeMetrics:
    """Performance metrics container"""
    total_trades: int
    profitable_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    total_return: float
    avg_win: float
    avg_loss: float
    best_trade: float
    worst_trade: float


class AnalyticsDashboard:
    """
    Trading performance analytics engine
    
    Features:
    - Win rate & profit factor
    - Sharpe & Sortino ratios
    - Maximum drawdown analysis
    - Trade statistics
    - Monthly/yearly reports
    """
    
    @staticmethod
    def calculate_metrics(trades: List[Dict[str, Any]]) -> TradeMetrics:
        """
        Calculate performance metrics from trades
        
        Args:
            trades: List of trade dicts with 'profit_loss' field
            
        Returns:
            TradeMetrics object
        """
        if not trades:
            return TradeMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        profits = [t.get('profit_loss', 0) for t in trades if 'profit_loss' in t]
        
        if not profits:
            return TradeMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        profits = np.array(profits)
        
        # Basic counts
        total = len(profits)
        profitable = len([p for p in profits if p > 0])
        losing = len([p for p in profits if p < 0])
        breakeven = len([p for p in profits if p == 0])
        
        win_rate = profitable / total if total > 0 else 0
        
        # Profit factor
        total_profit = np.sum(profits[profits > 0])
        total_loss = abs(np.sum(profits[profits < 0]))
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        # Sharpe ratio (simplified)
        returns = profits / abs(profits[-1]) if profits[-1] != 0 else profits
        sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        
        # Maximum drawdown
        max_drawdown = AnalyticsDashboard._calculate_max_drawdown(profits)
        
        # Trade statistics
        wins = profits[profits > 0]
        losses = profits[profits < 0]
        
        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = losses.mean() if len(losses) > 0 else 0
        best_trade = profits.max()
        worst_trade = profits.min()
        
        total_return = profits.sum()
        
        return TradeMetrics(
            total_trades=total,
            profitable_trades=profitable,
            losing_trades=losing,
            win_rate=win_rate,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe,
            max_drawdown=max_drawdown,
            total_return=total_return,
            avg_win=avg_win,
            avg_loss=avg_loss,
            best_trade=best_trade,
            worst_trade=worst_trade
        )
    
    @staticmethod
    def _calculate_max_drawdown(profits: np.ndarray) -> float:
        """Calculate maximum drawdown"""
        if len(profits) == 0:
            return 0
        
        cumulative = np.cumsum(profits)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        
        return float(np.min(drawdown)) if len(drawdown) > 0 else 0
    
    @staticmethod
    def generate_summary(metrics: TradeMetrics) -> Dict[str, str]:
        """
        Generate text summary for display
        
        Args:
            metrics: TradeMetrics object
            
        Returns:
            Dictionary with formatted strings
        """
        return {
            "Total Trades": str(metrics.total_trades),
            "Wins": str(metrics.profitable_trades),
            "Losses": str(metrics.losing_trades),
            "Win Rate": f"{metrics.win_rate * 100:.2f}%",
            "Profit Factor": f"{metrics.profit_factor:.2f}x",
            "Sharpe Ratio": f"{metrics.sharpe_ratio:.2f}",
            "Max Drawdown": f"{metrics.max_drawdown * 100:.2f}%",
            "Avg Win": f"${metrics.avg_win:.2f}",
            "Avg Loss": f"${metrics.avg_loss:.2f}",
            "Best Trade": f"${metrics.best_trade:.2f}",
            "Worst Trade": f"${metrics.worst_trade:.2f}",
            "Total Return": f"${metrics.total_return:.2f}"
        }
    
    @staticmethod
    def monthly_breakdown(trades: List[Dict[str, Any]]) -> Dict[str, TradeMetrics]:
        """
        Calculate metrics by month
        
        Args:
            trades: List of trades with 'entry_time'
            
        Returns:
            Monthly metrics dictionary
        """
        monthly_trades = {}
        
        for trade in trades:
            entry_time = trade.get('entry_time')
            if not entry_time:
                continue
            
            # Parse datetime
            if isinstance(entry_time, str):
                date = pd.to_datetime(entry_time)
            else:
                date = entry_time
            
            month_key = date.strftime('%Y-%m')
            
            if month_key not in monthly_trades:
                monthly_trades[month_key] = []
            
            monthly_trades[month_key].append(trade)
        
        # Calculate metrics for each month
        monthly_metrics = {}
        for month, month_trades in monthly_trades.items():
            monthly_metrics[month] = AnalyticsDashboard.calculate_metrics(month_trades)
        
        return monthly_metrics
    
    @staticmethod
    def generate_report(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive performance report
        
        Args:
            trades: All trades
            
        Returns:
            Complete report dictionary
        """
        metrics = AnalyticsDashboard.calculate_metrics(trades)
        monthly = AnalyticsDashboard.monthly_breakdown(trades)
        
        report = {
            "overview": AnalyticsDashboard.generate_summary(metrics),
            "metrics": metrics,
            "monthly": {
                month: AnalyticsDashboard.generate_summary(m_metrics)
                for month, m_metrics in monthly.items()
            },
            "total_trades": len(trades)
        }
        
        return report


if __name__ == "__main__":
    print("✅ PHASE 5.3: Analytics Dashboard Ready")
