"""
=============================================================================
DEMIR AI v27 - MARKET REGIME DETECTION & ADAPTIVE STRATEGY
=============================================================================
Purpose: Piyasa modunun otomatik tanınması ve uygun strateji seçimi
Location: /layers/ klasörü
Phase: 27 (Market Regime)
=============================================================================
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Optional, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketRegime(Enum):
    """5 Piyasa Modu"""
    BULL_TREND = "BULL_TREND"          # 🟢 Yükselen trend
    BEAR_TREND = "BEAR_TREND"          # 🔴 Düşen trend
    RANGE_BOUND = "RANGE_BOUND"        # 🟡 Yatay hareket
    HIGH_VOLATILITY = "HIGH_VOLATILITY"# 🟠 Yüksek oynaklık
    REVERSAL = "REVERSAL"              # 🟣 Dönüş noktası


@dataclass
class RegimeAnalysis:
    """Piyasa modu analizi"""
    regime: MarketRegime
    confidence: float  # 0-100
    volatility: float  # Annualized %
    trend_strength: float  # -1 to +1
    support_level: float
    resistance_level: float
    recommended_strategy: str
    position_size_multiplier: float  # 0.5-2.0
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class MarketRegimeDetector:
    """
    Piyasa Modu Detectoru
    
    Features:
    - 5 different regime types
    - Volatility calculation
    - Trend strength measurement
    - Support/resistance identification
    - Adaptive strategy suggestion
    """
    
    def __init__(self, lookback_period: int = 100):
        self.lookback_period = lookback_period
        self.regime_history: List[RegimeAnalysis] = []
    
    # ========================================================================
    # CALCULATIONS
    # ========================================================================
    
    def calculate_trend(self, prices: np.ndarray) -> float:
        """
        Trend gücünü hesapla (-1 to +1)
        -1: güçlü düşen
        0: nötr
        +1: güçlü yükselen
        """
        if len(prices) < 2:
            return 0
        
        # Simple linear regression trend
        x = np.arange(len(prices))
        coeffs = np.polyfit(x, prices, 1)
        trend_line = coeffs[0] * x + coeffs[1]
        
        # Trend strength (R-squared)
        ss_res = np.sum((prices - trend_line) ** 2)
        ss_tot = np.sum((prices - np.mean(prices)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Direction
        direction = 1 if coeffs[0] > 0 else -1
        
        return direction * r_squared
    
    def calculate_volatility(self, prices: np.ndarray) -> float:
        """Yıllık oynaklık hesapla (%)"""
        if len(prices) < 2:
            return 0
        
        returns = np.diff(prices) / prices[:-1]
        daily_vol = np.std(returns)
        annual_vol = daily_vol * np.sqrt(252) * 100  # Annualized
        
        return annual_vol
    
    def calculate_support_resistance(self, prices: np.ndarray) -> tuple:
        """Destek ve direnç seviyeleri hesapla"""
        support = np.min(prices[-20:])  # Last 20 candles
        resistance = np.max(prices[-20:])
        
        return support, resistance
    
    # ========================================================================
    # REGIME DETECTION
    # ========================================================================
    
    def detect_regime(self, price_data: pd.DataFrame) -> Optional[RegimeAnalysis]:
        """Piyasa modunu algıla"""
        try:
            prices = price_data['close'].values[-self.lookback_period:]
            
            if len(prices) < 20:
                logger.warning("⚠️ Insufficient data for regime detection")
                return None
            
            # Calculate metrics
            trend = self.calculate_trend(prices)
            volatility = self.calculate_volatility(prices)
            support, resistance = self.calculate_support_resistance(prices)
            
            current_price = prices[-1]
            price_range = resistance - support
            price_position = (current_price - support) / price_range if price_range > 0 else 0.5
            
            # Determine regime
            if volatility > 50:  # High volatility
                regime = MarketRegime.HIGH_VOLATILITY
                confidence = 70
                strategy = "Range Trading / Scalping"
                position_mult = 0.5  # Smaller positions in high vol
            
            elif abs(trend) < 0.3:  # Weak trend
                if 0.2 < price_position < 0.8:  # Middle of range
                    regime = MarketRegime.RANGE_BOUND
                    confidence = 75
                    strategy = "Mean Reversion"
                    position_mult = 0.8
                else:
                    regime = MarketRegime.REVERSAL
                    confidence = 60
                    strategy = "Breakout / Reversal"
                    position_mult = 1.2
            
            elif trend > 0.5:  # Strong uptrend
                regime = MarketRegime.BULL_TREND
                confidence = 85
                strategy = "Trend Following (Long)"
                position_mult = 1.5
            
            elif trend < -0.5:  # Strong downtrend
                regime = MarketRegime.BEAR_TREND
                confidence = 85
                strategy = "Trend Following (Short)"
                position_mult = 1.5
            
            else:  # Weak trends
                regime = MarketRegime.RANGE_BOUND
                confidence = 65
                strategy = "Range Trading"
                position_mult = 1.0
            
            analysis = RegimeAnalysis(
                regime=regime,
                confidence=confidence,
                volatility=volatility,
                trend_strength=trend,
                support_level=support,
                resistance_level=resistance,
                recommended_strategy=strategy,
                position_size_multiplier=position_mult
            )
            
            self.regime_history.append(analysis)
            
            logger.info(f"✅ Regime: {regime.value} ({confidence}% confidence)")
            logger.info(f"   Strategy: {strategy}")
            logger.info(f"   Volatility: {volatility:.1f}%")
            logger.info(f"   Position multiplier: {position_mult:.1f}x")
            
            return analysis
        
        except Exception as e:
            logger.error(f"❌ Regime detection error: {e}")
            return None
    
    # ========================================================================
    # ADAPTIVE STRATEGY SELECTOR
    # ========================================================================
    
    def get_regime_parameters(self, regime: MarketRegime) -> Dict:
        """Piyasa moduna göre trade parametrelerini al"""
        parameters = {
            MarketRegime.BULL_TREND: {
                "tp_percent": [3, 7, 15],  # TP1, 2, 3
                "sl_percent": 2.5,
                "bias": "LONG",
                "entry_signal": "Moving Average Crossover (Bullish)"
            },
            MarketRegime.BEAR_TREND: {
                "tp_percent": [3, 7, 15],
                "sl_percent": 2.5,
                "bias": "SHORT",
                "entry_signal": "Moving Average Crossover (Bearish)"
            },
            MarketRegime.RANGE_BOUND: {
                "tp_percent": [1.5, 3, 5],
                "sl_percent": 1.0,
                "bias": "NEUTRAL",
                "entry_signal": "Support/Resistance Bounce"
            },
            MarketRegime.HIGH_VOLATILITY: {
                "tp_percent": [2, 4, 8],
                "sl_percent": 1.5,
                "bias": "NEUTRAL",
                "entry_signal": "Breakout (wider stops)"
            },
            MarketRegime.REVERSAL: {
                "tp_percent": [4, 10, 20],
                "sl_percent": 3.0,
                "bias": "MIXED",
                "entry_signal": "Reversal Pattern"
            }
        }
        
        return parameters.get(regime, parameters[MarketRegime.RANGE_BOUND])
    
    def get_current_regime(self) -> Optional[RegimeAnalysis]:
        """Mevcut piyasa modunu al"""
        return self.regime_history[-1] if self.regime_history else None


class AdaptiveStrategySelector:
    """Piyasa moduna göre strateji seç"""
    
    def __init__(self):
        self.regime_detector = MarketRegimeDetector()
        self.active_strategies = {}
    
    def select_strategy(self, price_data: pd.DataFrame, symbol: str) -> Optional[Dict]:
        """Uygun stratejiyi seç ve parametrelerini döndür"""
        
        # Detect regime
        analysis = self.regime_detector.detect_regime(price_data)
        
        if not analysis:
            return None
        
        # Get strategy parameters
        params = self.regime_detector.get_regime_parameters(analysis.regime)
        
        # Adjust for position size multiplier
        params['position_multiplier'] = analysis.position_size_multiplier
        params['regime'] = analysis.regime.value
        params['confidence'] = analysis.confidence
        
        self.active_strategies[symbol] = params
        
        return params


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    detector = MarketRegimeDetector()
    selector = AdaptiveStrategySelector()
    
    # Mock price data
    dates = pd.date_range(start='2025-01-01', periods=100, freq='1h')
    prices = np.cumsum(np.random.randn(100)) + 50000
    
    price_data = pd.DataFrame({
        'close': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'volume': np.random.uniform(100, 1000, 100)
    }, index=dates)
    
    # Detect regime
    analysis = detector.detect_regime(price_data)
    if analysis:
        print(f"\n📊 Market Regime Analysis:")
        print(f"   Regime: {analysis.regime.value}")
        print(f"   Confidence: {analysis.confidence}%")
        print(f"   Volatility: {analysis.volatility:.1f}%")
        print(f"   Strategy: {analysis.recommended_strategy}")
    
    # Select strategy
    strategy = selector.select_strategy(price_data, "BTCUSDT")
    if strategy:
        print(f"\n🎯 Selected Strategy:")
        for key, value in strategy.items():
            print(f"   {key}: {value}")
