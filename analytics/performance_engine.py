# analytics/performance_engine.py
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 DEMIR AI v7.0 - PERFORMANCE ENGINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPREHENSIVE PERFORMANCE TRACKING & ANALYTICS

Features:
    ✅ Real-time performance metrics
    ✅ Signal accuracy tracking
    ✅ Win rate calculation
    ✅ Profit/Loss analysis
    ✅ Sharpe ratio computation
    ✅ Maximum drawdown tracking
    ✅ Group performance comparison
    ✅ Time-series analytics

Metrics Tracked:
    - Total signals generated
    - Win rate percentage
    - Average R:R achieved
    - Total P&L
    - Sharpe ratio
    - Maximum drawdown
    - Recovery factor
    - Profit factor

DEPLOYMENT: Railway Production
AUTHOR: DEMIR AI Research Team
DATE: 2025-11-19
VERSION: 7.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import deque, defaultdict
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ============================================================================
# PERFORMANCE METRICS DATA CLASSES
# ============================================================================

@dataclass
class TradeResult:
    """Individual trade result"""
    trade_id: str
    symbol: str
    direction: str
    entry_price: float
    exit_price: float
    pnl: float
    pnl_percent: float
    risk_reward_achieved: float
    entry_time: datetime
    exit_time: datetime
    duration_hours: float
    outcome: str  # 'WIN', 'LOSS', 'BREAKEVEN'
    signal_confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['entry_time'] = self.entry_time.isoformat()
        data['exit_time'] = self.exit_time.isoformat()
        return data

@dataclass
class PerformanceMetrics:
    """Overall performance metrics"""
    
    # Basic stats
    total_signals: int
    total_trades: int
    winning_trades: int
    losing_trades: int
    breakeven_trades: int
    
    # Win rate
    win_rate: float
    loss_rate: float
    
    # P&L
    total_pnl: float
    total_pnl_percent: float
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    
    # Risk metrics
    average_rr_achieved: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_percent: float
    recovery_factor: float
    
    # Timing
    average_trade_duration_hours: float
    total_trading_days: int
    
    # Accuracy by confidence
    high_confidence_accuracy: float  # >85%
    medium_confidence_accuracy: float  # 75-85%
    
    # Group performance
    tech_group_accuracy: float
    sentiment_group_accuracy: float
    ml_group_accuracy: float
    onchain_group_accuracy: float
    macro_risk_group_accuracy: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

# ============================================================================
# PERFORMANCE ENGINE
# ============================================================================

class PerformanceEngine:
    """
    Comprehensive performance tracking and analytics engine
    
    Tracks:
        - All signals generated
        - Trade outcomes
        - Win/loss rates
        - P&L metrics
        - Risk-adjusted returns
        - Group-level performance
    """
    
    def __init__(self, db_manager):
        """
        Initialize performance engine
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        
        # Trade history
        self.trade_results: List[TradeResult] = []
        self.trade_history = deque(maxlen=10000)
        
        # Running totals
        self.running_pnl = 0.0
        self.peak_balance = 0.0
        self.current_drawdown = 0.0
        self.max_drawdown = 0.0
        
        # Group performance tracking
        self.group_predictions: Dict[str, List[bool]] = defaultdict(list)
        
        # Time series data
        self.equity_curve: List[Tuple[datetime, float]] = []
        
        # Statistics
        self.stats = {
            'total_signals_generated': 0,
            'total_trades_executed': 0,
            'last_update': None
        }
        
        logger.info("✅ PerformanceEngine initialized")
    
    # ========================================================================
    # TRADE RECORDING
    # ========================================================================
    
    def record_trade(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        exit_price: float,
        entry_time: datetime,
        exit_time: datetime,
        signal_confidence: float,
        signal_data: Optional[Dict[str, Any]] = None
    ) -> TradeResult:
        """
        Record a completed trade
        
        Args:
            symbol: Trading pair
            direction: 'LONG' or 'SHORT'
            entry_price: Entry price
            exit_price: Exit price
            entry_time: Entry timestamp
            exit_time: Exit timestamp
            signal_confidence: Original signal confidence
            signal_data: Full signal data (optional)
        
        Returns:
            TradeResult object
        """
        # Calculate P&L
        if direction == 'LONG':
            pnl = exit_price - entry_price
        else:  # SHORT
            pnl = entry_price - exit_price
        
        pnl_percent = (pnl / entry_price) * 100
        
        # Determine outcome
        if pnl > 0:
            outcome = 'WIN'
        elif pnl < 0:
            outcome = 'LOSS'
        else:
            outcome = 'BREAKEVEN'
        
        # Calculate duration
        duration = (exit_time - entry_time).total_seconds() / 3600  # hours
        
        # Calculate risk/reward achieved (if signal data available)
        rr_achieved = 0.0
        if signal_data and 'sl' in signal_data:
            risk = abs(entry_price - signal_data['sl'])
            if risk > 0:
                rr_achieved = abs(pnl) / risk
        
        # Create trade result
        trade = TradeResult(
            trade_id=f"{symbol}_{int(entry_time.timestamp())}",
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            exit_price=exit_price,
            pnl=pnl,
            pnl_percent=pnl_percent,
            risk_reward_achieved=rr_achieved,
            entry_time=entry_time,
            exit_time=exit_time,
            duration_hours=duration,
            outcome=outcome,
            signal_confidence=signal_confidence
        )
        
        # Update running metrics
        self.trade_results.append(trade)
        self.trade_history.append(trade)
        self.running_pnl += pnl
        
        # Update drawdown tracking
        self._update_drawdown()
        
        # Update equity curve
        self.equity_curve.append((exit_time, self.running_pnl))
        
        # Track group performance if data available
        if signal_data:
            self._track_group_performance(signal_data, outcome)
        
        self.stats['total_trades_executed'] += 1
        self.stats['last_update'] = datetime.now()
        
        logger.info(
            f"Trade recorded: {symbol} {direction} | "
            f"P&L: ${pnl:.2f} ({pnl_percent:+.2f}%) | "
            f"Outcome: {outcome}"
        )
        
        return trade
    
    def record_signal_generated(self, signal: Dict[str, Any]):
        """Record that a signal was generated"""
        self.stats['total_signals_generated'] += 1
    
    # ========================================================================
    # METRICS CALCULATION
    # ========================================================================
    
    def calculate_metrics(self) -> PerformanceMetrics:
        """
        Calculate comprehensive performance metrics
        
        Returns:
            PerformanceMetrics object
        """
        if not self.trade_results:
            return self._empty_metrics()
        
        trades = self.trade_results
        
        # Basic counts
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.outcome == 'WIN')
        losing_trades = sum(1 for t in trades if t.outcome == 'LOSS')
        breakeven_trades = sum(1 for t in trades if t.outcome == 'BREAKEVEN')
        
        # Win rates
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        loss_rate = (losing_trades / total_trades * 100) if total_trades > 0 else 0
        
        # P&L metrics
        total_pnl = sum(t.pnl for t in trades)
        total_pnl_percent = sum(t.pnl_percent for t in trades)
        
        wins = [t.pnl for t in trades if t.outcome == 'WIN']
        losses = [abs(t.pnl) for t in trades if t.outcome == 'LOSS']
        
        average_win = np.mean(wins) if wins else 0
        average_loss = np.mean(losses) if losses else 0
        largest_win = max(wins) if wins else 0
        largest_loss = max(losses) if losses else 0
        
        # Risk metrics
        average_rr = np.mean([t.risk_reward_achieved for t in trades if t.risk_reward_achieved > 0])
        average_rr = average_rr if not np.isnan(average_rr) else 0
        
        # Profit factor
        total_wins = sum(wins)
        total_losses = sum(losses)
        profit_factor = (total_wins / total_losses) if total_losses > 0 else 0
        
        # Sharpe ratio
        sharpe_ratio = self._calculate_sharpe_ratio(trades)
        
        # Drawdown
        max_dd_percent = (self.max_drawdown / max(self.peak_balance, 1)) * 100
        
        # Recovery factor
        recovery_factor = (total_pnl / abs(self.max_drawdown)) if self.max_drawdown != 0 else 0
        
        # Average trade duration
        avg_duration = np.mean([t.duration_hours for t in trades])
        
        # Trading days
        if trades:
            first_trade = min(t.entry_time for t in trades)
            last_trade = max(t.exit_time for t in trades)
            trading_days = (last_trade - first_trade).days + 1
        else:
            trading_days = 0
        
        # Confidence-based accuracy
        high_conf_trades = [t for t in trades if t.signal_confidence >= 0.85]
        medium_conf_trades = [t for t in trades if 0.75 <= t.signal_confidence < 0.85]
        
        high_conf_accuracy = (
            sum(1 for t in high_conf_trades if t.outcome == 'WIN') / 
            len(high_conf_trades) * 100
        ) if high_conf_trades else 0
        
        medium_conf_accuracy = (
            sum(1 for t in medium_conf_trades if t.outcome == 'WIN') / 
            len(medium_conf_trades) * 100
        ) if medium_conf_trades else 0
        
        # Group accuracies
        group_accuracies = self._calculate_group_accuracies()
        
        return PerformanceMetrics(
            total_signals=self.stats['total_signals_generated'],
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            breakeven_trades=breakeven_trades,
            win_rate=win_rate,
            loss_rate=loss_rate,
            total_pnl=total_pnl,
            total_pnl_percent=total_pnl_percent,
            average_win=average_win,
            average_loss=average_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            average_rr_achieved=average_rr,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=self.max_drawdown,
            max_drawdown_percent=max_dd_percent,
            recovery_factor=recovery_factor,
            average_trade_duration_hours=avg_duration,
            total_trading_days=trading_days,
            high_confidence_accuracy=high_conf_accuracy,
            medium_confidence_accuracy=medium_conf_accuracy,
            tech_group_accuracy=group_accuracies['technical'],
            sentiment_group_accuracy=group_accuracies['sentiment'],
            ml_group_accuracy=group_accuracies['ml'],
            onchain_group_accuracy=group_accuracies['onchain'],
            macro_risk_group_accuracy=group_accuracies['macro_risk']
        )
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics as dictionary"""
        metrics = self.calculate_metrics()
        return metrics.to_dict()
    
    def update_metrics(self) -> Dict[str, Any]:
        """Update and return current metrics"""
        return self.get_current_metrics()
    
    def _empty_metrics(self) -> PerformanceMetrics:
        """Return empty metrics object"""
        return PerformanceMetrics(
            total_signals=self.stats['total_signals_generated'],
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            breakeven_trades=0,
            win_rate=0.0,
            loss_rate=0.0,
            total_pnl=0.0,
            total_pnl_percent=0.0,
            average_win=0.0,
            average_loss=0.0,
            largest_win=0.0,
            largest_loss=0.0,
            average_rr_achieved=0.0,
            profit_factor=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            max_drawdown_percent=0.0,
            recovery_factor=0.0,
            average_trade_duration_hours=0.0,
            total_trading_days=0,
            high_confidence_accuracy=0.0,
            medium_confidence_accuracy=0.0,
            tech_group_accuracy=0.0,
            sentiment_group_accuracy=0.0,
            ml_group_accuracy=0.0,
            onchain_group_accuracy=0.0,
            macro_risk_group_accuracy=0.0
        )
    
    # ========================================================================
    # ADVANCED METRICS
    # ========================================================================
    
    def _calculate_sharpe_ratio(self, trades: List[TradeResult]) -> float:
        """
        Calculate Sharpe ratio
        
        Sharpe Ratio = (Average Return - Risk-Free Rate) / Standard Deviation
        Assuming risk-free rate = 0 for simplicity
        """
        if not trades or len(trades) < 2:
            return 0.0
        
        returns = [t.pnl_percent for t in trades]
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        # Annualize (assuming 365 trading days)
        sharpe = (avg_return / std_return) * np.sqrt(365)
        
        return sharpe
    
    def _update_drawdown(self):
        """Update drawdown tracking"""
        # Update peak balance
        if self.running_pnl > self.peak_balance:
            self.peak_balance = self.running_pnl
        
        # Calculate current drawdown
        self.current_drawdown = self.peak_balance - self.running_pnl
        
        # Update max drawdown
        if self.current_drawdown > self.max_drawdown:
            self.max_drawdown = self.current_drawdown
    
    def _track_group_performance(self, signal_data: Dict[str, Any], outcome: str):
        """Track individual group performance"""
        is_win = (outcome == 'WIN')
        
        groups = [
            'tech_group_score',
            'sentiment_group_score',
            'ml_group_score',
            'onchain_group_score',
            'macro_risk_group_score'
        ]
        
        for group in groups:
            if group in signal_data:
                score = signal_data[group]
                # If group predicted correctly (high score and win, or low score and loss)
                predicted_correctly = (score > 0.55 and is_win) or (score < 0.45 and not is_win)
                self.group_predictions[group].append(predicted_correctly)
    
    def _calculate_group_accuracies(self) -> Dict[str, float]:
        """Calculate accuracy for each group"""
        accuracies = {}
        
        group_mapping = {
            'tech_group_score': 'technical',
            'sentiment_group_score': 'sentiment',
            'ml_group_score': 'ml',
            'onchain_group_score': 'onchain',
            'macro_risk_group_score': 'macro_risk'
        }
        
        for group_key, group_name in group_mapping.items():
            predictions = self.group_predictions.get(group_key, [])
            if predictions:
                accuracy = sum(predictions) / len(predictions) * 100
            else:
                accuracy = 0.0
            accuracies[group_name] = accuracy
        
        return accuracies
    
    # ========================================================================
    # TIME-SERIES ANALYTICS
    # ========================================================================
    
    def get_equity_curve(self) -> pd.DataFrame:
        """
        Get equity curve as DataFrame
        
        Returns:
            DataFrame with timestamp and equity columns
        """
        if not self.equity_curve:
            return pd.DataFrame(columns=['timestamp', 'equity'])
        
        df = pd.DataFrame(self.equity_curve, columns=['timestamp', 'equity'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        return df
    
    def get_returns_distribution(self) -> Dict[str, Any]:
        """Get returns distribution statistics"""
        if not self.trade_results:
            return {}
        
        returns = [t.pnl_percent for t in self.trade_results]
        
        return {
            'mean': np.mean(returns),
            'median': np.median(returns),
            'std': np.std(returns),
            'min': np.min(returns),
            'max': np.max(returns),
            'percentile_25': np.percentile(returns, 25),
            'percentile_75': np.percentile(returns, 75),
            'skewness': float(pd.Series(returns).skew()),
            'kurtosis': float(pd.Series(returns).kurtosis())
        }
    
    def get_monthly_performance(self) -> pd.DataFrame:
        """Get monthly performance breakdown"""
        if not self.trade_results:
            return pd.DataFrame()
        
        # Create DataFrame from trades
        trades_data = [
            {
                'date': t.exit_time,
                'pnl': t.pnl,
                'pnl_percent': t.pnl_percent,
                'outcome': t.outcome
            }
            for t in self.trade_results
        ]
        
        df = pd.DataFrame(trades_data)
        df['date'] = pd.to_datetime(df['date'])
        df['year_month'] = df['date'].dt.to_period('M')
        
        # Group by month
        monthly = df.groupby('year_month').agg({
            'pnl': 'sum',
            'pnl_percent': 'sum',
            'outcome': 'count'
        }).rename(columns={'outcome': 'trades'})
        
        # Calculate win rate per month
        wins_per_month = df[df['outcome'] == 'WIN'].groupby('year_month').size()
        monthly['win_rate'] = (wins_per_month / monthly['trades'] * 100).fillna(0)
        
        return monthly
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def generate_performance_report(self) -> str:
        """Generate comprehensive performance report"""
        metrics = self.calculate_metrics()
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      DEMIR AI PERFORMANCE REPORT                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  📊 TRADING STATISTICS                                                       ║
║  ═══════════════════                                                         ║
║  Total Signals:          {metrics.total_signals:>10,}                                    ║
║  Total Trades:           {metrics.total_trades:>10,}                                    ║
║  Winning Trades:         {metrics.winning_trades:>10,}  ({metrics.win_rate:>5.1f}%)                    ║
║  Losing Trades:          {metrics.losing_trades:>10,}  ({metrics.loss_rate:>5.1f}%)                    ║
║                                                                              ║
║  💰 PROFIT & LOSS                                                            ║
║  ════════════════                                                            ║
║  Total P&L:              ${metrics.total_pnl:>10,.2f}                                  ║
║  Total P&L %:            {metrics.total_pnl_percent:>10.2f}%                                  ║
║  Average Win:            ${metrics.average_win:>10,.2f}                                  ║
║  Average Loss:           ${metrics.average_loss:>10,.2f}                                  ║
║  Largest Win:            ${metrics.largest_win:>10,.2f}                                  ║
║  Largest Loss:           ${metrics.largest_loss:>10,.2f}                                  ║
║                                                                              ║
║  📈 RISK METRICS                                                             ║
║  ═══════════════                                                             ║
║  Avg R:R Achieved:       {metrics.average_rr_achieved:>10.2f}                                    ║
║  Profit Factor:          {metrics.profit_factor:>10.2f}                                    ║
║  Sharpe Ratio:           {metrics.sharpe_ratio:>10.2f}                                    ║
║  Max Drawdown:           ${metrics.max_drawdown:>10,.2f}  ({metrics.max_drawdown_percent:>5.1f}%)                ║
║  Recovery Factor:        {metrics.recovery_factor:>10.2f}                                    ║
║                                                                              ║
║  🎯 ACCURACY BY CONFIDENCE                                                   ║
║  ═════════════════════                                                       ║
║  High Confidence (>85%): {metrics.high_confidence_accuracy:>10.1f}%                                  ║
║  Medium Conf (75-85%):   {metrics.medium_confidence_accuracy:>10.1f}%                                  ║
║                                                                              ║
║  🧠 GROUP PERFORMANCE                                                        ║
║  ════════════════════                                                        ║
║  Technical Analysis:     {metrics.tech_group_accuracy:>10.1f}%                                  ║
║  Sentiment Analysis:     {metrics.sentiment_group_accuracy:>10.1f}%                                  ║
║  ML Models:              {metrics.ml_group_accuracy:>10.1f}%                                  ║
║  On-Chain Data:          {metrics.onchain_group_accuracy:>10.1f}%                                  ║
║  Macro/Risk:             {metrics.macro_risk_group_accuracy:>10.1f}%                                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        return report
    
    # ========================================================================
    # DATA EXPORT
    # ========================================================================
    
    def export_trades_csv(self, filename: str = 'trades_export.csv'):
        """Export all trades to CSV"""
        if not self.trade_results:
            logger.warning("No trades to export")
            return
        
        df = pd.DataFrame([t.to_dict() for t in self.trade_results])
        df.to_csv(filename, index=False)
        logger.info(f"Exported {len(df)} trades to {filename}")
    
    def get_trade_history(
        self,
        limit: int = 100,
        symbol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get trade history
        
        Args:
            limit: Maximum trades to return
            symbol: Filter by symbol (optional)
        
        Returns:
            List of trade dictionaries
        """
        trades = self.trade_results
        
        # Filter by symbol if specified
        if symbol:
            trades = [t for t in trades if t.symbol == symbol]
        
        # Sort by exit time (most recent first)
        trades = sorted(trades, key=lambda t: t.exit_time, reverse=True)
        
        # Limit
        trades = trades[:limit]
        
        return [t.to_dict() for t in trades]
