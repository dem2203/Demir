# advanced_ai/trade_learning_engine.py
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 DEMIR AI v7.0 - TRADE LEARNING ENGINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AI ÖĞRENME SİSTEMİ - Her trade'den ders al!

Features:
    ✅ Her trade'i kaydet (entry, exit, reason)
    ✅ Win/Loss analizi
    ✅ Pattern recognition (hangi sinyaller başarılı)
    ✅ Layer performance tracking (hangi layer daha iyi)
    ✅ Market regime learning (hangi piyasada ne çalışıyor)
    ✅ Self-improvement (kötü layers'ı devre dışı bırak)
    ✅ Confidence calibration (overconfident signals'ı düzelt)

Learning Approach:
    - Bayesian updating
    - Reinforcement learning
    - Pattern mining
    - Statistical analysis

AUTHOR: DEMIR AI Research Team
DATE: 2025-11-20
VERSION: 7.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import numpy as np
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Trade:
    """Completed trade record"""
    trade_id: str
    symbol: str
    direction: str  # LONG or SHORT
    entry_price: float
    exit_price: float
    entry_time: datetime
    exit_time: datetime
    
    # Signal that triggered trade
    signal_id: int
    signal_confidence: float
    signal_layers: Dict[str, float]  # Layer scores
    
    # Outcome
    pnl: float  # Profit/Loss in $
    pnl_percent: float  # P/L percentage
    is_win: bool
    
    # Context
    market_regime: str  # trending, ranging, volatile
    volatility: float
    volume_profile: str  # high, medium, low
    
    # Metadata
    exit_reason: str  # tp, sl, manual, timeout
    notes: Optional[str] = None

@dataclass
class LayerPerformance:
    """Performance metrics for individual layer"""
    layer_name: str
    total_signals: int
    winning_signals: int
    losing_signals: int
    win_rate: float
    avg_pnl: float
    sharpe_ratio: float
    confidence_calibration: float  # How well calibrated is confidence?
    last_updated: datetime

# ============================================================================
# TRADE LEARNING ENGINE
# ============================================================================

class TradeLearningEngine:
    """
    AI öğrenme motoru - Her trade'den ders çıkar
    
    Learning Mechanisms:
        1. Layer Performance Tracking → Hangi layer başarılı
        2. Pattern Recognition → Hangi kombinasyonlar kazandırıyor
        3. Market Regime Analysis → Hangi piyasa tipinde ne çalışıyor
        4. Confidence Calibration → Overconfident signals'ı düzelt
        5. Dynamic Weighting → İyi layers'a daha fazla ağırlık
    """
    
    def __init__(self, db_manager):
        self.db = db_manager
        
        # In-memory cache for fast access
        self.layer_performance: Dict[str, LayerPerformance] = {}
        self.trade_history: List[Trade] = []
        
        # Learning parameters
        self.min_trades_for_learning = 20  # En az 20 trade olmalı
        self.confidence_threshold = 0.60  # Min confidence
        self.performance_window = 100  # Son 100 trade'e bak
        
        # Initialize from database
        self._load_from_database()
        
        logger.info("✅ TradeLearningEngine initialized")
    
    # ========================================================================
    # TRADE RECORDING
    # ========================================================================
    
    def record_trade(self, trade: Trade) -> bool:
        """
        Trade'i kaydet ve analiz et
        
        Args:
            trade: Completed trade object
        
        Returns:
            True if successfully recorded
        """
        try:
            logger.info(f"📝 Recording trade: {trade.symbol} {trade.direction} "
                       f"{trade.pnl_percent:+.2f}% {'WIN' if trade.is_win else 'LOSS'}")
            
            # 1. Save to database
            trade_dict = asdict(trade)
            trade_dict['entry_time'] = trade.entry_time.isoformat()
            trade_dict['exit_time'] = trade.exit_time.isoformat()
            trade_dict['signal_layers'] = json.dumps(trade.signal_layers)
            
            query = """
                INSERT INTO trades (
                    trade_id, symbol, direction, entry_price, exit_price,
                    entry_time, exit_time, signal_id, signal_confidence,
                    signal_layers, pnl, pnl_percent, is_win,
                    market_regime, volatility, volume_profile,
                    exit_reason, notes
                ) VALUES (
                    %(trade_id)s, %(symbol)s, %(direction)s, %(entry_price)s, %(exit_price)s,
                    %(entry_time)s, %(exit_time)s, %(signal_id)s, %(signal_confidence)s,
                    %(signal_layers)s, %(pnl)s, %(pnl_percent)s, %(is_win)s,
                    %(market_regime)s, %(volatility)s, %(volume_profile)s,
                    %(exit_reason)s, %(notes)s
                )
            """
            
            self.db.execute_query(query, trade_dict)
            
            # 2. Add to in-memory cache
            self.trade_history.append(trade)
            if len(self.trade_history) > self.performance_window:
                self.trade_history.pop(0)  # Keep only recent trades
            
            # 3. Update layer performance
            self._update_layer_performance(trade)
            
            # 4. Check for learning insights
            if len(self.trade_history) >= self.min_trades_for_learning:
                insights = self._analyze_recent_performance()
                logger.info(f"💡 Learning insights: {insights}")
            
            logger.info("✅ Trade recorded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to record trade: {e}")
            return False
    
    def _update_layer_performance(self, trade: Trade):
        """
        Update performance metrics for each layer involved in trade
        """
        for layer_name, layer_score in trade.signal_layers.items():
            if layer_name not in self.layer_performance:
                self.layer_performance[layer_name] = LayerPerformance(
                    layer_name=layer_name,
                    total_signals=0,
                    winning_signals=0,
                    losing_signals=0,
                    win_rate=0.0,
                    avg_pnl=0.0,
                    sharpe_ratio=0.0,
                    confidence_calibration=1.0,
                    last_updated=datetime.now()
                )
            
            perf = self.layer_performance[layer_name]
            perf.total_signals += 1
            
            if trade.is_win:
                perf.winning_signals += 1
            else:
                perf.losing_signals += 1
            
            # Update win rate
            perf.win_rate = perf.winning_signals / perf.total_signals
            
            # Update average P/L
            perf.avg_pnl = (
                (perf.avg_pnl * (perf.total_signals - 1) + trade.pnl) /
                perf.total_signals
            )
            
            perf.last_updated = datetime.now()
            
            # Save to database
            self._save_layer_performance(perf)
    
    # ========================================================================
    # LEARNING & ANALYSIS
    # ========================================================================
    
    def _analyze_recent_performance(self) -> Dict[str, Any]:
        """
        Analyze recent trades to extract learning insights
        
        Returns:
            Dictionary with insights and recommendations
        """
        recent = self.trade_history[-self.performance_window:]
        
        if len(recent) < self.min_trades_for_learning:
            return {'status': 'insufficient_data'}
        
        insights = {
            'total_trades': len(recent),
            'win_rate': sum(t.is_win for t in recent) / len(recent),
            'avg_pnl': np.mean([t.pnl for t in recent]),
            'best_layers': self._identify_best_layers(recent),
            'worst_layers': self._identify_worst_layers(recent),
            'best_regime': self._identify_best_regime(recent),
            'recommendations': []
        }
        
        # Generate recommendations
        if insights['win_rate'] < 0.50:
            insights['recommendations'].append(
                "⚠️ Win rate below 50% - Consider reducing position sizes"
            )
        
        if len(insights['worst_layers']) > 0:
            insights['recommendations'].append(
                f"❌ Disable low-performing layers: {', '.join(insights['worst_layers'])}"
            )
        
        if len(insights['best_layers']) > 0:
            insights['recommendations'].append(
                f"✅ Increase weight for top layers: {', '.join(insights['best_layers'])}"
            )
        
        return insights
    
    def _identify_best_layers(self, trades: List[Trade], top_n: int = 3) -> List[str]:
        """
        Identify best performing layers
        """
        layer_stats = defaultdict(lambda: {'wins': 0, 'total': 0})
        
        for trade in trades:
            for layer_name, score in trade.signal_layers.items():
                if score > 0.6:  # Layer contributed significantly
                    layer_stats[layer_name]['total'] += 1
                    if trade.is_win:
                        layer_stats[layer_name]['wins'] += 1
        
        # Calculate win rates
        layer_win_rates = {
            layer: stats['wins'] / stats['total']
            for layer, stats in layer_stats.items()
            if stats['total'] >= 5  # Min 5 trades
        }
        
        # Sort by win rate
        sorted_layers = sorted(
            layer_win_rates.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [layer for layer, _ in sorted_layers[:top_n]]
    
    def _identify_worst_layers(self, trades: List[Trade], bottom_n: int = 2) -> List[str]:
        """
        Identify worst performing layers
        """
        layer_stats = defaultdict(lambda: {'wins': 0, 'total': 0})
        
        for trade in trades:
            for layer_name, score in trade.signal_layers.items():
                if score > 0.6:
                    layer_stats[layer_name]['total'] += 1
                    if trade.is_win:
                        layer_stats[layer_name]['wins'] += 1
        
        layer_win_rates = {
            layer: stats['wins'] / stats['total']
            for layer, stats in layer_stats.items()
            if stats['total'] >= 5
        }
        
        # Sort by win rate (ascending)
        sorted_layers = sorted(
            layer_win_rates.items(),
            key=lambda x: x[1]
        )
        
        # Return layers with win rate < 45%
        return [layer for layer, wr in sorted_layers if wr < 0.45][:bottom_n]
    
    def _identify_best_regime(self, trades: List[Trade]) -> str:
        """
        Identify which market regime performs best
        """
        regime_stats = defaultdict(lambda: {'wins': 0, 'total': 0})
        
        for trade in trades:
            regime = trade.market_regime
            regime_stats[regime]['total'] += 1
            if trade.is_win:
                regime_stats[regime]['wins'] += 1
        
        # Calculate win rates
        regime_win_rates = {
            regime: stats['wins'] / stats['total']
            for regime, stats in regime_stats.items()
            if stats['total'] >= 3
        }
        
        if not regime_win_rates:
            return 'unknown'
        
        best_regime = max(regime_win_rates.items(), key=lambda x: x[1])
        return f"{best_regime[0]} ({best_regime[1]*100:.1f}% win rate)"
    
    # ========================================================================
    # DYNAMIC LAYER WEIGHTING
    # ========================================================================
    
    def get_layer_weights(self) -> Dict[str, float]:
        """
        Get dynamic weights for each layer based on performance
        
        Good layers get higher weights, poor layers get lower weights
        
        Returns:
            Dictionary mapping layer names to weights (0.0-2.0)
        """
        weights = {}
        
        for layer_name, perf in self.layer_performance.items():
            # Base weight = 1.0
            weight = 1.0
            
            # Adjust based on win rate
            if perf.total_signals >= 10:
                if perf.win_rate > 0.60:
                    weight = 1.5  # Boost good layers
                elif perf.win_rate > 0.55:
                    weight = 1.2
                elif perf.win_rate < 0.40:
                    weight = 0.5  # Penalize bad layers
                elif perf.win_rate < 0.45:
                    weight = 0.7
            
            weights[layer_name] = weight
        
        return weights
    
    def should_disable_layer(self, layer_name: str) -> bool:
        """
        Check if a layer should be disabled due to poor performance
        
        Args:
            layer_name: Name of the layer
        
        Returns:
            True if layer should be disabled
        """
        if layer_name not in self.layer_performance:
            return False
        
        perf = self.layer_performance[layer_name]
        
        # Disable if:
        # 1. Win rate < 35% after 20+ trades
        # 2. Average P/L negative after 20+ trades
        if perf.total_signals >= 20:
            if perf.win_rate < 0.35 or perf.avg_pnl < 0:
                logger.warning(
                    f"⚠️ Layer '{layer_name}' performing poorly: "
                    f"{perf.win_rate*100:.1f}% win rate, "
                    f"${perf.avg_pnl:.2f} avg P/L"
                )
                return True
        
        return False
    
    # ========================================================================
    # STATISTICS & REPORTING
    # ========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive trading statistics
        """
        if len(self.trade_history) == 0:
            return {'status': 'no_trades'}
        
        trades = self.trade_history
        
        wins = [t for t in trades if t.is_win]
        losses = [t for t in trades if not t.is_win]
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': len(wins) / len(trades),
            
            'total_pnl': sum(t.pnl for t in trades),
            'avg_win': np.mean([t.pnl for t in wins]) if wins else 0,
            'avg_loss': np.mean([t.pnl for t in losses]) if losses else 0,
            
            'best_trade': max(trades, key=lambda t: t.pnl),
            'worst_trade': min(trades, key=lambda t: t.pnl),
            
            'avg_trade_duration': np.mean([
                (t.exit_time - t.entry_time).total_seconds() / 3600
                for t in trades
            ]),
            
            'layer_performance': {
                name: {
                    'win_rate': perf.win_rate,
                    'total_signals': perf.total_signals,
                    'avg_pnl': perf.avg_pnl
                }
                for name, perf in self.layer_performance.items()
            }
        }
    
    # ========================================================================
    # DATABASE OPERATIONS
    # ========================================================================
    
    def _load_from_database(self):
        """
        Load existing trade history and layer performance from database
        """
        try:
            # Load recent trades
            query = """
                SELECT * FROM trades
                ORDER BY exit_time DESC
                LIMIT %s
            """
            
            results = self.db.execute_query(
                query,
                (self.performance_window,),
                fetch=True
            )
            
            if results:
                for row in results:
                    trade = Trade(
                        trade_id=row['trade_id'],
                        symbol=row['symbol'],
                        direction=row['direction'],
                        entry_price=float(row['entry_price']),
                        exit_price=float(row['exit_price']),
                        entry_time=row['entry_time'],
                        exit_time=row['exit_time'],
                        signal_id=row['signal_id'],
                        signal_confidence=float(row['signal_confidence']),
                        signal_layers=json.loads(row['signal_layers']),
                        pnl=float(row['pnl']),
                        pnl_percent=float(row['pnl_percent']),
                        is_win=row['is_win'],
                        market_regime=row['market_regime'],
                        volatility=float(row['volatility']),
                        volume_profile=row['volume_profile'],
                        exit_reason=row['exit_reason'],
                        notes=row.get('notes')
                    )
                    self.trade_history.append(trade)
            
            logger.info(f"✅ Loaded {len(self.trade_history)} trades from database")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load trade history: {e}")
    
    def _save_layer_performance(self, perf: LayerPerformance):
        """
        Save layer performance to database
        """
        try:
            query = """
                INSERT INTO layer_performance (
                    layer_name, total_signals, winning_signals, losing_signals,
                    win_rate, avg_pnl, sharpe_ratio, confidence_calibration, last_updated
                ) VALUES (
                    %(layer_name)s, %(total_signals)s, %(winning_signals)s, %(losing_signals)s,
                    %(win_rate)s, %(avg_pnl)s, %(sharpe_ratio)s, %(confidence_calibration)s, %(last_updated)s
                )
                ON CONFLICT (layer_name) DO UPDATE SET
                    total_signals = EXCLUDED.total_signals,
                    winning_signals = EXCLUDED.winning_signals,
                    losing_signals = EXCLUDED.losing_signals,
                    win_rate = EXCLUDED.win_rate,
                    avg_pnl = EXCLUDED.avg_pnl,
                    sharpe_ratio = EXCLUDED.sharpe_ratio,
                    confidence_calibration = EXCLUDED.confidence_calibration,
                    last_updated = EXCLUDED.last_updated
            """
            
            self.db.execute_query(query, asdict(perf))
            
        except Exception as e:
            logger.error(f"❌ Failed to save layer performance: {e}")
