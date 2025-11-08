"""
🔱 PHASE 23: SELF-LEARNING ENGINE
Dynamic Weight Recalibration + Market Regime Switching
"""
import logging
from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass, field
import numpy as np

logger = logging.getLogger(__name__)

# ============================================================================
# PHASE 23A: DYNAMIC WEIGHT RECALIBRATOR
# ============================================================================

@dataclass
class LayerPerformance:
    layer_name: str
    accuracy: float
    trades_count: int
    avg_return: float
    sharpe_ratio: float

class DynamicWeightRecalibrator:
    """Auto-adjust layer weights based on recent performance"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        # Initial equal weights
        self.layer_weights = {
            "traditional_markets": 1.0,
            "gann_levels": 1.0,
            "elliott_waves": 0.8,
            "wyckoff": 0.8,
            "whale_tracker": 1.2,
            "exchange_flows": 0.9,
            "twitter_sentiment": 0.7,
            "reddit_sentiment": 0.6,
            "liquidation_detector": 1.1,
            "flash_crash_detector": 1.3,
        }
        self.performance_history = {}
    
    def recalibrate_weights(self, performance_data: Dict) -> Dict:
        """Recalibrate weights based on layer performance"""
        try:
            # Calculate accuracy for each layer
            for layer_name, perf in performance_data.items():
                if layer_name not in self.performance_history:
                    self.performance_history[layer_name] = []
                
                self.performance_history[layer_name].append(perf)
                if len(self.performance_history[layer_name]) > 100:
                    self.performance_history[layer_name] = self.performance_history[layer_name][-100:]
            
            # Adjust weights: high performers get boosted, low performers suppressed
            for layer_name in self.layer_weights.keys():
                if layer_name not in performance_data:
                    continue
                
                perf = performance_data[layer_name]
                accuracy = perf.get("accuracy", 0.5)
                sharpe = perf.get("sharpe_ratio", 1.0)
                
                # Weight = base_weight * accuracy_multiplier * sharpe_multiplier
                accuracy_mult = accuracy / 0.5 if accuracy > 0 else 0.5  # 50% accuracy = 1x
                sharpe_mult = max(0.5, min(2.0, sharpe / 1.0))  # Sharpe ratio normalization
                
                self.layer_weights[layer_name] *= accuracy_mult * sharpe_mult
                # Prevent weights from going too extreme
                self.layer_weights[layer_name] = max(0.1, min(3.0, self.layer_weights[layer_name]))
            
            logger.info(f"Weights recalibrated: {self.layer_weights}")
            return self.layer_weights
            
        except Exception as e:
            logger.error(f"Weight recalibration error: {e}")
            return self.layer_weights
    
    def get_weighted_signal(self, signals: Dict) -> float:
        """Calculate weighted signal from all layers"""
        try:
            weighted_sum = 0
            weight_sum = 0
            
            for layer_name, signal in signals.items():
                if layer_name not in self.layer_weights:
                    continue
                
                weight = self.layer_weights[layer_name]
                # Assume signal is 0-1 (bullish) or -1-0 (bearish)
                weighted_sum += signal * weight
                weight_sum += weight
            
            final_signal = weighted_sum / weight_sum if weight_sum > 0 else 0
            return final_signal
            
        except Exception as e:
            logger.error(f"Signal weighting error: {e}")
            return 0.0

# ============================================================================
# PHASE 23B: MARKET REGIME SWITCHER
# ============================================================================

class MarketRegimeSwitcher:
    """Switch strategy and parameters based on market regime"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.current_regime = "normal"
        self.regimes = {
            "bull_market": {
                "aggressive": True,
                "position_size_mult": 1.5,
                "stop_loss_pct": 8,
            },
            "bear_market": {
                "aggressive": False,
                "position_size_mult": 0.5,
                "stop_loss_pct": 3,
            },
            "high_volatility": {
                "aggressive": False,
                "position_size_mult": 0.7,
                "stop_loss_pct": 5,
            },
            "low_volatility": {
                "aggressive": True,
                "position_size_mult": 1.2,
                "stop_loss_pct": 6,
            },
        }
    
    def switch_regime(self, market_analysis: Dict) -> Dict:
        """Determine current regime and return appropriate parameters"""
        try:
            vix = market_analysis.get("vix", 20)
            spx_trend = market_analysis.get("spx_trend", "sideways")
            btc_trend = market_analysis.get("btc_trend", "sideways")
            
            # Regime determination logic
            if spx_trend == "uptrend" and vix < 15 and btc_trend == "uptrend":
                regime = "bull_market"
            elif spx_trend == "downtrend" and vix > 30:
                regime = "bear_market"
            elif vix > 25:
                regime = "high_volatility"
            elif vix < 12:
                regime = "low_volatility"
            else:
                regime = "normal"
            
            self.current_regime = regime
            params = self.regimes.get(regime, {})
            
            return {
                "current_regime": regime,
                "parameters": params,
                "timestamp": datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Regime switching error: {e}")
            return {"current_regime": "normal", "parameters": {}}
    
    def get_position_size_multiplier(self) -> float:
        """Get position size multiplier for current regime"""
        params = self.regimes.get(self.current_regime, {})
        return params.get("position_size_mult", 1.0)
    
    def get_stop_loss_percent(self) -> float:
        """Get stop loss percent for current regime"""
        params = self.regimes.get(self.current_regime, {})
        return params.get("stop_loss_pct", 5.0)

# ============================================================================
# INTEGRATION
# ============================================================================

def integrate_learning_phase23(config: Dict, market_data: Dict) -> Dict:
    """Combined Phase 23 self-learning integration"""
    recalibrator = DynamicWeightRecalibrator(config)
    regime_switcher = MarketRegimeSwitcher(config)
    
    # Example performance data
    performance_data = {
        "traditional_markets": {"accuracy": 0.62, "sharpe_ratio": 1.5},
        "gann_levels": {"accuracy": 0.58, "sharpe_ratio": 1.2},
        "whale_tracker": {"accuracy": 0.71, "sharpe_ratio": 1.8},
    }
    
    weights = recalibrator.recalibrate_weights(performance_data)
    regime = regime_switcher.switch_regime(market_data)
    
    return {
        "weights": weights,
        "regime": regime,
        "position_size_mult": regime_switcher.get_position_size_multiplier(),
        "stop_loss_pct": regime_switcher.get_stop_loss_percent(),
        "timestamp": datetime.now().isoformat(),
    }

if __name__ == "__main__":
    print("✅ Phase 23: Self-Learning Engine (Weight Recalibration + Regime Switching) ready")
