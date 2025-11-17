"""
DEMIR AI BOT - Group Signal Engine
Separate signal generation for each group
Technical, Sentiment, ML, OnChain, Risk signals
Professional group-based architecture
"""

import logging
from typing import Dict, Any, List, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum
import time

logger = logging.getLogger(__name__)


class SignalDirection(Enum):
    """Signal direction enum."""
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"


@dataclass
class GroupSignal:
    """Single group signal output."""
    group_name: str
    direction: SignalDirection
    strength: float  # 0-1
    confidence: float  # 0-1
    active_layers: int
    layer_details: Dict[str, float]
    timestamp: float


class GroupSignalEngine:
    """Generate signals grouped by category."""
    
    # Layer groupings
    TECHNICAL_LAYERS = [
        'RSI', 'MACD', 'BollingerBands', 'ATR', 'Stochastic',
        'CCI', 'WilliamsR', 'MFI', 'Ichimoku', 'Fibonacci',
        'PivotPoints', 'VWAP', 'MovingAverage', 'Momentum',
        'Volatility', 'ElliottWave', 'Fourier', 'Fractal',
        'KalmanFilter', 'MarkovRegime', 'MultiTF_1m',
        'MultiTF_5m', 'MultiTF_15m', 'MultiTF_1h',
        'Harmonic_Crab', 'Harmonic_Gartley', 'Harmonic_Butterfly',
        'CandlestickPattern'
    ]
    
    SENTIMENT_LAYERS = [
        'NewsSentiment', 'FearGreedIndex', 'BTCDominance',
        'AltcoinSeason', 'ExchangeFlow', 'WhaleAlert',
        'TwitterSentiment', 'MacroCorrelation', 'TraditionalMarkets',
        'EconomicCalendar', 'InterestRates', 'MarketRegime',
        'StablecoinDominance', 'FundingRates', 'LongShortRatio',
        'OnChainActivity', 'ExchangeReserves', 'OrderBook',
        'LiquidationCascade', 'BasisContango'
    ]
    
    ML_LAYERS = [
        'LSTM', 'XGBoost', 'RandomForest', 'SVM',
        'GradientBoosting', 'NeuralNetwork', 'AdaBoost',
        'IsolationForest', 'KMeans', 'EnsembleVoting'
    ]
    
    ONCHAIN_LAYERS = [
        'WhaleWatcher', 'NetworkActivity', 'MinerBehavior',
        'TokenFlow', 'DeFiMetrics', 'GasFeeTrend'
    ]
    
    RISK_LAYERS = [
        'GarchVolatility', 'HistoricalVol', 'MonteCarlo',
        'ValueAtRisk', 'KellyOptimization'
    ]
    
    def __init__(self):
        """Initialize group signal engine."""
        self.groups = {
            'technical': self.TECHNICAL_LAYERS,
            'sentiment': self.SENTIMENT_LAYERS,
            'ml': self.ML_LAYERS,
            'onchain': self.ONCHAIN_LAYERS,
            'risk': self.RISK_LAYERS
        }
        logger.info("GroupSignalEngine initialized with 5 groups")
    
    def generate_technical_signal(
        self,
        symbol: str,
        technical_scores: Dict[str, float],
        timestamp: float = None
    ) -> GroupSignal:
        """Generate technical layer signal."""
        
        if timestamp is None:
            timestamp = time.time()
        
        # Validate and filter scores
        valid_scores = {
            k: v for k, v in technical_scores.items()
            if k in self.TECHNICAL_LAYERS and 0 <= v <= 1
        }
        
        if not valid_scores:
            logger.warning(f"No valid technical scores for {symbol}")
            return GroupSignal(
                group_name='technical',
                direction=SignalDirection.NEUTRAL,
                strength=0.5,
                confidence=0.0,
                active_layers=0,
                layer_details={},
                timestamp=timestamp
            )
        
        # Calculate metrics
        strength = float(np.mean(list(valid_scores.values())))
        variance = float(np.var(list(valid_scores.values())))
        confidence = float(max(0.0, min(1.0, 1.0 - variance)))
        
        # Determine direction
        if strength >= 0.65:
            direction = SignalDirection.LONG
        elif strength <= 0.35:
            direction = SignalDirection.SHORT
        else:
            direction = SignalDirection.NEUTRAL
        
        logger.info(
            f"Technical signal generated: {symbol} {direction.value} "
            f"(strength={strength:.2f}, confidence={confidence:.2f})"
        )
        
        return GroupSignal(
            group_name='technical',
            direction=direction,
            strength=strength,
            confidence=confidence,
            active_layers=len(valid_scores),
            layer_details=valid_scores,
            timestamp=timestamp
        )
    
    def generate_sentiment_signal(
        self,
        symbol: str,
        sentiment_scores: Dict[str, float],
        timestamp: float = None
    ) -> GroupSignal:
        """Generate sentiment layer signal."""
        
        if timestamp is None:
            timestamp = time.time()
        
        valid_scores = {
            k: v for k, v in sentiment_scores.items()
            if k in self.SENTIMENT_LAYERS and 0 <= v <= 1
        }
        
        if not valid_scores:
            logger.warning(f"No valid sentiment scores for {symbol}")
            return GroupSignal(
                group_name='sentiment',
                direction=SignalDirection.NEUTRAL,
                strength=0.5,
                confidence=0.0,
                active_layers=0,
                layer_details={},
                timestamp=timestamp
            )
        
        strength = float(np.mean(list(valid_scores.values())))
        variance = float(np.var(list(valid_scores.values())))
        confidence = float(max(0.0, min(1.0, 1.0 - variance)))
        
        if strength >= 0.65:
            direction = SignalDirection.LONG
        elif strength <= 0.35:
            direction = SignalDirection.SHORT
        else:
            direction = SignalDirection.NEUTRAL
        
        logger.info(
            f"Sentiment signal generated: {symbol} {direction.value} "
            f"(strength={strength:.2f}, confidence={confidence:.2f})"
        )
        
        return GroupSignal(
            group_name='sentiment',
            direction=direction,
            strength=strength,
            confidence=confidence,
            active_layers=len(valid_scores),
            layer_details=valid_scores,
            timestamp=timestamp
        )
    
    def generate_ml_signal(
        self,
        symbol: str,
        ml_scores: Dict[str, float],
        timestamp: float = None
    ) -> GroupSignal:
        """Generate ML layer signal."""
        
        if timestamp is None:
            timestamp = time.time()
        
        valid_scores = {
            k: v for k, v in ml_scores.items()
            if k in self.ML_LAYERS and 0 <= v <= 1
        }
        
        if not valid_scores:
            logger.warning(f"No valid ML scores for {symbol}")
            return GroupSignal(
                group_name='ml',
                direction=SignalDirection.NEUTRAL,
                strength=0.5,
                confidence=0.0,
                active_layers=0,
                layer_details={},
                timestamp=timestamp
            )
        
        strength = float(np.mean(list(valid_scores.values())))
        variance = float(np.var(list(valid_scores.values())))
        confidence = float(max(0.0, min(1.0, 1.0 - variance)))
        
        if strength >= 0.65:
            direction = SignalDirection.LONG
        elif strength <= 0.35:
            direction = SignalDirection.SHORT
        else:
            direction = SignalDirection.NEUTRAL
        
        logger.info(
            f"ML signal generated: {symbol} {direction.value} "
            f"(strength={strength:.2f}, confidence={confidence:.2f})"
        )
        
        return GroupSignal(
            group_name='ml',
            direction=direction,
            strength=strength,
            confidence=confidence,
            active_layers=len(valid_scores),
            layer_details=valid_scores,
            timestamp=timestamp
        )
    
    def generate_onchain_signal(
        self,
        symbol: str,
        onchain_scores: Dict[str, float],
        timestamp: float = None
    ) -> GroupSignal:
        """Generate OnChain layer signal."""
        
        if timestamp is None:
            timestamp = time.time()
        
        valid_scores = {
            k: v for k, v in onchain_scores.items()
            if k in self.ONCHAIN_LAYERS and 0 <= v <= 1
        }
        
        if not valid_scores:
            logger.warning(f"No valid OnChain scores for {symbol}")
            return GroupSignal(
                group_name='onchain',
                direction=SignalDirection.NEUTRAL,
                strength=0.5,
                confidence=0.0,
                active_layers=0,
                layer_details={},
                timestamp=timestamp
            )
        
        strength = float(np.mean(list(valid_scores.values())))
        variance = float(np.var(list(valid_scores.values())))
        confidence = float(max(0.0, min(1.0, 1.0 - variance)))
        
        if strength >= 0.65:
            direction = SignalDirection.LONG
        elif strength <= 0.35:
            direction = SignalDirection.SHORT
        else:
            direction = SignalDirection.NEUTRAL
        
        logger.info(
            f"OnChain signal generated: {symbol} {direction.value} "
            f"(strength={strength:.2f}, confidence={confidence:.2f})"
        )
        
        return GroupSignal(
            group_name='onchain',
            direction=direction,
            strength=strength,
            confidence=confidence,
            active_layers=len(valid_scores),
            layer_details=valid_scores,
            timestamp=timestamp
        )
    
    def generate_risk_assessment(
        self,
        symbol: str,
        risk_scores: Dict[str, float],
        timestamp: float = None
    ) -> Dict[str, Any]:
        """Generate risk assessment (not a buy/sell signal)."""
        
        if timestamp is None:
            timestamp = time.time()
        
        valid_scores = {
            k: v for k, v in risk_scores.items()
            if k in self.RISK_LAYERS and 0 <= v <= 1
        }
        
        if not valid_scores:
            logger.warning(f"No valid risk scores for {symbol}")
            return {
                'group': 'risk',
                'volatility_score': 0.5,
                'max_loss_exposure': 'N/A',
                'kelly_fraction': 0.1,
                'confidence': 0.0,
                'timestamp': timestamp
            }
        
        volatility = float(np.mean(list(valid_scores.values())))
        
        # Kelly criterion calculation
        kelly_fraction = float(max(0.05, min(0.3, 0.25 * (volatility - 0.5))))
        max_loss = kelly_fraction * 100
        
        logger.info(f"Risk assessment: {symbol} volatility={volatility:.2f}")
        
        return {
            'group': 'risk',
            'volatility_score': volatility,
            'max_loss_exposure': f"{max_loss:.1f}%",
            'kelly_fraction': kelly_fraction,
            'confidence': 1.0 if valid_scores else 0.0,
            'active_layers': len(valid_scores),
            'timestamp': timestamp
        }
    
    def detect_group_conflicts(
        self,
        signals: Dict[str, GroupSignal]
    ) -> Tuple[bool, List[str]]:
        """Detect conflicts between groups."""
        
        conflicts = []
        
        directions = {
            name: sig.direction for name, sig in signals.items()
            if sig.active_layers > 0
        }
        
        if not directions:
            return False, []
        
        # Check for conflicts
        long_groups = [
            name for name, direction in directions.items()
            if direction == SignalDirection.LONG
        ]
        short_groups = [
            name for name, direction in directions.items()
            if direction == SignalDirection.SHORT
        ]
        
        if long_groups and short_groups:
            conflict_msg = f"Conflict: {long_groups} LONG vs {short_groups} SHORT"
            conflicts.append(conflict_msg)
            logger.warning(conflict_msg)
        
        return len(conflicts) > 0, conflicts
    
    def calculate_consensus(
        self,
        signals: Dict[str, GroupSignal]
    ) -> Dict[str, Any]:
        """Calculate consensus from all groups."""
        
        valid_signals = {
            name: sig for name, sig in signals.items()
            if sig.active_layers > 0
        }
        
        if not valid_signals:
            return {
                'direction': SignalDirection.NEUTRAL.value,
                'strength': 0.5,
                'confidence': 0.0,
                'conflict_detected': False,
                'active_groups': 0
            }
        
        # Weighted consensus
        total_weight = sum(
            sig.confidence * sig.active_layers
            for sig in valid_signals.values()
        )
        
        if total_weight > 0:
            weighted_strength = sum(
                sig.strength * sig.confidence * sig.active_layers
                for sig in valid_signals.values()
            ) / total_weight
        else:
            weighted_strength = 0.5
        
        avg_confidence = float(np.mean([
            sig.confidence for sig in valid_signals.values()
        ]))
        
        if weighted_strength >= 0.65:
            direction = SignalDirection.LONG
        elif weighted_strength <= 0.35:
            direction = SignalDirection.SHORT
        else:
            direction = SignalDirection.NEUTRAL
        
        conflict_detected, conflicts = self.detect_group_conflicts(signals)
        
        logger.info(
            f"Consensus calculated: {direction.value} "
            f"(strength={weighted_strength:.2f}, conflicts={conflict_detected})"
        )
        
        return {
            'direction': direction.value,
            'strength': weighted_strength,
            'confidence': avg_confidence,
            'conflict_detected': conflict_detected,
            'active_groups': len(valid_signals),
            'conflicts': conflicts
        }
