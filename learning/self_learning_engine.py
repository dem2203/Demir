"""
🧬 DEMIR AI - PHASE 12: SELF-LEARNING ENGINE - Main Orchestrator
=================================================================
AI that learns from trades, adapts to markets, improves over time
Date: 8 November 2025
Version: 1.0 - Production Ready
=================================================================
"""

import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class TradeResult:
    """Result of a completed trade"""
    entry_price: float
    exit_price: float
    profit_loss_percent: float
    regime_at_entry: str
    signal_confidence: float
    time_held_hours: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class LearningSession:
    """Single learning iteration"""
    timestamp: datetime
    trades_analyzed: int
    improvement_percent: float
    regime_adaptations: int
    parameters_adjusted: Dict[str, float]
    new_accuracy: float

# ============================================================================
# SELF-LEARNING ENGINE
# ============================================================================

class SelfLearningEngine:
    """
    AI system that continuously learns from trading results
    Adapts strategies to market regimes
    Improves accuracy over time
    """
    
    def __init__(self):
        """Initialize self-learning engine"""
        self.logger = logging.getLogger(__name__)
        
        # Trade tracking
        self.completed_trades: List[TradeResult] = []
        self.win_rate = 0.5
        self.avg_profit = 0.0
        self.avg_loss = 0.0
        
        # Regime adaptations
        self.regime_strategies: Dict[str, Dict] = {
            'TREND': {'entry_threshold': 65, 'tp_percent': 2.5, 'sl_percent': 1.5},
            'RANGE': {'entry_threshold': 55, 'tp_percent': 1.5, 'sl_percent': 1.0},
            'VOLATILE': {'entry_threshold': 75, 'tp_percent': 1.0, 'sl_percent': 0.5}
        }
        
        # Learning history
        self.learning_sessions: List[LearningSession] = []
        
        # Model performance
        self.accuracy_by_regime: Dict[str, float] = {}
        self.accuracy_by_timeframe: Dict[str, float] = {}
        
        self.logger.info("✅ SelfLearningEngine initialized")
    
    def record_trade_result(self, entry: float, exit: float, regime: str, 
                           confidence: float, time_held: float):
        """Record completed trade for learning"""
        
        pnl_percent = ((exit - entry) / entry) * 100
        
        trade = TradeResult(
            entry_price=entry,
            exit_price=exit,
            profit_loss_percent=pnl_percent,
            regime_at_entry=regime,
            signal_confidence=confidence,
            time_held_hours=time_held
        )
        
        self.completed_trades.append(trade)
        
        # Update statistics
        self._update_statistics()
        
        self.logger.debug(f"Trade recorded: {regime} @ {entry} → {exit} ({pnl_percent:+.2f}%)")
    
    def _update_statistics(self):
        """Update win rate and P&L statistics"""
        
        if not self.completed_trades:
            return
        
        pnls = [t.profit_loss_percent for t in self.completed_trades]
        
        # Win rate
        wins = sum(1 for pnl in pnls if pnl > 0)
        self.win_rate = wins / len(pnls)
        
        # Average profit/loss
        profits = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]
        
        self.avg_profit = np.mean(profits) if profits else 0
        self.avg_loss = np.mean(losses) if losses else 0
        
        # By regime
        for regime in ['TREND', 'RANGE', 'VOLATILE']:
            regime_trades = [t for t in self.completed_trades if t.regime_at_entry == regime]
            if regime_trades:
                regime_wins = sum(1 for t in regime_trades if t.profit_loss_percent > 0)
                self.accuracy_by_regime[regime] = regime_wins / len(regime_trades)
    
    def adapt_to_regime(self, regime: str, current_accuracy: float):
        """Adapt strategy parameters to market regime"""
        
        if regime not in self.regime_strategies:
            return
        
        strategy = self.regime_strategies[regime]
        
        # If accuracy is low in this regime, adjust thresholds
        if current_accuracy < 0.45:
            # Be more selective (higher entry threshold)
            strategy['entry_threshold'] = min(
                strategy['entry_threshold'] + 3, 85
            )
            self.logger.warning(
                f"Lowering entry frequency for {regime} "
                f"(accuracy: {current_accuracy:.0%})"
            )
        
        elif current_accuracy > 0.60:
            # Be more aggressive (lower entry threshold)
            strategy['entry_threshold'] = max(
                strategy['entry_threshold'] - 2, 45
            )
            self.logger.info(
                f"Increasing entry frequency for {regime} "
                f"(accuracy: {current_accuracy:.0%})"
            )
        
        # Adjust TP/SL based on profit factor
        if self.avg_profit > 0:
            profit_factor = abs(self.avg_profit / self.avg_loss) if self.avg_loss else 1
            
            if profit_factor > 2:
                # Good ratio, keep it
                pass
            elif profit_factor < 1:
                # Losses are bigger than profits, tighter SL
                strategy['sl_percent'] = max(
                    strategy['sl_percent'] * 0.9, 0.3
                )
    
    def learning_iteration(self, lookback_trades: int = 20) -> LearningSession:
        """Run one learning iteration"""
        
        if len(self.completed_trades) < lookback_trades:
            return None
        
        # Analyze recent trades
        recent_trades = self.completed_trades[-lookback_trades:]
        
        # Calculate current accuracy
        current_wins = sum(1 for t in recent_trades if t.profit_loss_percent > 0)
        current_accuracy = current_wins / len(recent_trades)
        
        # Previous accuracy (from trades before that)
        if len(self.completed_trades) > lookback_trades * 2:
            previous_trades = self.completed_trades[-lookback_trades*2:-lookback_trades]
            previous_wins = sum(1 for t in previous_trades if t.profit_loss_percent > 0)
            previous_accuracy = previous_wins / len(previous_trades)
        else:
            previous_accuracy = 0.5
        
        improvement = (current_accuracy - previous_accuracy) * 100
        
        # Adapt to regimes
        regime_adaptations = 0
        parameters_adjusted = {}
        
        for regime in ['TREND', 'RANGE', 'VOLATILE']:
            regime_accuracy = self.accuracy_by_regime.get(regime, 0.5)
            self.adapt_to_regime(regime, regime_accuracy)
            
            if regime_accuracy != self.accuracy_by_regime.get(regime, 0.5):
                regime_adaptations += 1
                parameters_adjusted[regime] = self.regime_strategies[regime]
        
        # Create session
        session = LearningSession(
            timestamp=datetime.now(),
            trades_analyzed=lookback_trades,
            improvement_percent=improvement,
            regime_adaptations=regime_adaptations,
            parameters_adjusted=parameters_adjusted,
            new_accuracy=current_accuracy
        )
        
        self.learning_sessions.append(session)
        
        self.logger.info(
            f"Learning iteration: accuracy {previous_accuracy:.0%} → "
            f"{current_accuracy:.0%} ({improvement:+.1f}%) | "
            f"{regime_adaptations} regime adaptations"
        )
        
        return session
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning status"""
        
        return {
            'total_trades_analyzed': len(self.completed_trades),
            'win_rate': self.win_rate,
            'avg_profit_percent': self.avg_profit,
            'avg_loss_percent': self.avg_loss,
            'accuracy_by_regime': self.accuracy_by_regime,
            'learning_sessions_completed': len(self.learning_sessions),
            'current_regime_strategies': self.regime_strategies,
            'timestamp': datetime.now().isoformat()
        }

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'SelfLearningEngine',
    'TradeResult',
    'LearningSession'
]
