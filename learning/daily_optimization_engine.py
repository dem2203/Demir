"""
=============================================================================
DEMIR AI v28 - SELF-LEARNING & DAILY OPTIMIZATION ENGINE
=============================================================================
Location: /learning/ klasörü | Phase: 28
=============================================================================
"""

import logging
import json
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Optimizasyon sonuçları"""
    date: str
    win_rate_before: float
    win_rate_after: float
    total_trades: int
    avg_confidence_improvement: float
    layer_weights_optimized: Dict
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class DailyOptimizationEngine:
    """
    Günlük Optimizasyon Motoru
    
    Features:
    - Daily performance analysis
    - Layer weight adjustment (genetic algorithm)
    - Parameter tuning
    - Win rate improvement tracking
    """
    
    def __init__(self):
        self.layer_weights = {
            "technical": 0.25,
            "onchain": 0.20,
            "sentiment": 0.15,
            "anomaly": 0.20,
            "regime": 0.20
        }
        self.optimization_history: List[OptimizationResult] = []
        self.performance_log = []
    
    def analyze_daily_performance(self, trades: List[Dict]) -> Dict:
        """Günlük performansı analiz et"""
        if not trades:
            return {"error": "No trades"}
        
        total = len(trades)
        wins = sum(1 for t in trades if t.get('pnl', 0) > 0)
        
        return {
            "total_trades": total,
            "win_rate": (wins / total * 100) if total > 0 else 0,
            "total_pnl": sum(t.get('pnl', 0) for t in trades),
            "avg_confidence": np.mean([t.get('confidence', 50) for t in trades])
        }
    
    def optimize_layer_weights(self, performance_data: List[Dict]) -> Dict:
        """Layer ağırlıklarını optimize et (GA)"""
        logger.info("🔄 Starting daily layer weight optimization...")
        
        best_weights = self.layer_weights.copy()
        best_score = 0
        
        # Simple genetic algorithm (3 iterations)
        for iteration in range(3):
            candidate_weights = {}
            total_weight = 0
            
            for layer, weight in best_weights.items():
                # Small random adjustment
                adjustment = np.random.uniform(-0.05, 0.05)
                new_weight = max(0.05, weight + adjustment)
                candidate_weights[layer] = new_weight
                total_weight += new_weight
            
            # Normalize
            for layer in candidate_weights:
                candidate_weights[layer] /= total_weight
            
            # Simulate score (in real: backtest with new weights)
            score = np.random.uniform(60, 85)
            
            if score > best_score:
                best_score = score
                best_weights = candidate_weights
        
        self.layer_weights = best_weights
        logger.info(f"✅ Weights optimized: {best_weights}")
        return best_weights
    
    def run_daily_optimization(self, closed_trades: List[Dict]) -> Optional[OptimizationResult]:
        """Günlük optimizasyonu çalıştır"""
        perf_before = self.analyze_daily_performance(closed_trades)
        
        if perf_before.get("error"):
            return None
        
        # Optimize
        new_weights = self.optimize_layer_weights(closed_trades)
        
        # Simulate after performance (in real: wait for next day trades)
        perf_after = {
            "win_rate": perf_before["win_rate"] * np.random.uniform(0.98, 1.05)
        }
        
        result = OptimizationResult(
            date=datetime.now().isoformat()[:10],
            win_rate_before=perf_before["win_rate"],
            win_rate_after=perf_after["win_rate"],
            total_trades=perf_before["total_trades"],
            avg_confidence_improvement=2.5,  # Mock
            layer_weights_optimized=new_weights
        )
        
        self.optimization_history.append(result)
        return result


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    engine = DailyOptimizationEngine()
    
    # Mock trades
    trades = [
        {"pnl": 150, "confidence": 85},
        {"pnl": -50, "confidence": 60},
        {"pnl": 200, "confidence": 90},
        {"pnl": -100, "confidence": 70},
    ]
    
    result = engine.run_daily_optimization(trades)
    if result:
        print(f"📊 Optimization Result:")
        print(f"   Win Rate: {result.win_rate_before:.1f}% → {result.win_rate_after:.1f}%")
        print(f"   New Weights: {result.layer_weights_optimized}")
