"""
🧠 DEMIR AI - PHASE 10: CONSCIOUSNESS ENGINE - Predictive Impact Analyzer
===========================================================================
Forecasts market movement impact across multiple timeframes
Date: 8 November 2025
Version: 1.0 - Production Ready
===========================================================================
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class PriceForecast:
    """Price movement forecast"""
    timeframe: str  # 5m, 1h, 4h, 1d
    expected_direction: str  # UP, DOWN, RANGE
    probability_up: float  # 0-1
    probability_down: float  # 0-1
    probability_range: float  # 0-1
    target_price_up: Optional[float] = None
    target_price_down: Optional[float] = None
    confidence: float = 0.5
    forecast_timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ImpactAnalysis:
    """Impact of a factor on market"""
    factor_name: str
    factor_value: float
    impact_direction: str  # BULLISH, BEARISH, NEUTRAL
    impact_strength: float  # 0-1
    affected_timeframes: List[str]
    probability_shift: float  # How much it shifts probabilities
    timestamp: datetime = field(default_factory=datetime.now)

# ============================================================================
# PREDICTIVE IMPACT ANALYZER
# ============================================================================

class PredictiveImpactAnalyzer:
    """
    Analyzes how various factors impact price movements
    Generates probabilistic forecasts across timeframes
    """

    def __init__(self):
        """Initialize analyzer"""
        self.logger = logging.getLogger(__name__)

        # Factor impact database
        self.factor_impacts: Dict[str, Dict[str, float]] = {}  # factor -> impact metrics
        self.impact_history: List[ImpactAnalysis] = []

        # Forecasts by timeframe
        self.active_forecasts: Dict[str, List[PriceForecast]] = {
            '5m': [],
            '15m': [],
            '1h': [],
            '4h': [],
            '1d': []
        }

        # Historical price data for trend analysis
        self.price_history: Dict[str, List[float]] = {
            tf: [] for tf in ['5m', '15m', '1h', '4h', '1d']
        }

        self.logger.info("✅ PredictiveImpactAnalyzer initialized")

    def analyze_factor_impact(self, factor_name: str, factor_value: float,
                             historical_impacts: Optional[List[float]] = None) -> ImpactAnalysis:
        """
        Analyze impact of a factor on price movement
        """
        # Determine impact direction and strength
        if factor_value >= 66:
            impact_direction = 'BULLISH'
            impact_strength = (factor_value - 50) / 50  # 0-1 scale
        elif factor_value <= 33:
            impact_direction = 'BEARISH'
            impact_strength = (50 - factor_value) / 50
        else:
            impact_direction = 'NEUTRAL'
            impact_strength = 0.2

        # Determine affected timeframes (stronger on longer timeframes)
        affected_timeframes = ['1d', '4h', '1h']  # Strong factors affect longer TFs first

        if impact_strength > 0.7:
            affected_timeframes.append('15m')
        if impact_strength > 0.85:
            affected_timeframes.append('5m')

        # Calculate probability shift
        probability_shift = impact_strength * (0.1 if factor_value >= 50 else -0.1)

        analysis = ImpactAnalysis(
            factor_name=factor_name,
            factor_value=factor_value,
            impact_direction=impact_direction,
            impact_strength=impact_strength,
            affected_timeframes=affected_timeframes,
            probability_shift=probability_shift
        )

        self.impact_history.append(analysis)

        self.logger.debug(
            f"Factor impact: {factor_name} = {factor_value:.1f} -> "
            f"{impact_direction} (+{probability_shift:.3f})"
        )

        return analysis

    def generate_forecast(self, timeframe: str, current_price: float,
                         base_probabilities: Dict[str, float],
                         active_impacts: List[ImpactAnalysis]) -> PriceForecast:
        """
        Generate probabilistic price forecast for a timeframe
        """

        # Start with base probabilities
        prob_up = base_probabilities.get('UP', 0.33)
        prob_down = base_probabilities.get('DOWN', 0.33)
        prob_range = base_probabilities.get('RANGE', 0.34)

        # Apply active impacts
        total_shift = 0
        for impact in active_impacts:
            if timeframe in impact.affected_timeframes:
                if impact.impact_direction == 'BULLISH':
                    prob_up += impact.probability_shift
                    prob_down -= impact.probability_shift * 0.5
                elif impact.impact_direction == 'BEARISH':
                    prob_down += impact.probability_shift
                    prob_up -= impact.probability_shift * 0.5

                total_shift += abs(impact.probability_shift)

        # Normalize to sum to 1.0
        total = prob_up + prob_down + prob_range
        if total > 0:
            prob_up /= total
            prob_down /= total
            prob_range /= total

        # Determine expected direction
        max_prob = max(prob_up, prob_down, prob_range)
        if max_prob == prob_up:
            expected_direction = 'UP'
        elif max_prob == prob_down:
            expected_direction = 'DOWN'
        else:
            expected_direction = 'RANGE'

        # Calculate target prices based on timeframe
        timeframe_moves = {
            '5m': 0.002,    # 0.2%
            '15m': 0.005,   # 0.5%
            '1h': 0.01,     # 1%
            '4h': 0.025,    # 2.5%
            '1d': 0.05      # 5%
        }

        move_percent = timeframe_moves.get(timeframe, 0.01)

        target_price_up = current_price * (1 + move_percent)
        target_price_down = current_price * (1 - move_percent)

        # Confidence from probability distribution (how concentrated)
        confidence = max(prob_up, prob_down, prob_range)

        forecast = PriceForecast(
            timeframe=timeframe,
            expected_direction=expected_direction,
            probability_up=prob_up,
            probability_down=prob_down,
            probability_range=prob_range,
            target_price_up=target_price_up,
            target_price_down=target_price_down,
            confidence=confidence
        )

        self.active_forecasts[timeframe].append(forecast)

        return forecast

    def forecast_multi_timeframe(self, current_price: float,
                                base_probabilities: Dict[str, float],
                                active_impacts: List[ImpactAnalysis]) -> Dict[str, PriceForecast]:
        """
        Generate forecasts across all timeframes
        """
        forecasts = {}

        for timeframe in ['5m', '15m', '1h', '4h', '1d']:
            forecast = self.generate_forecast(
                timeframe, current_price, base_probabilities, active_impacts
            )
            forecasts[timeframe] = forecast

        return forecasts

    def calculate_forecast_consensus(self, timeframe: str = '1h') -> Dict[str, Any]:
        """
        Calculate consensus forecast from recent forecasts
        """

        recent_forecasts = self.active_forecasts[timeframe][-10:]  # Last 10 forecasts

        if not recent_forecasts:
            return {
                'consensus_direction': 'NEUTRAL',
                'consensus_confidence': 0.5,
                'agreement_level': 0.0
            }

        # Aggregate probabilities
        avg_prob_up = np.mean([f.probability_up for f in recent_forecasts])
        avg_prob_down = np.mean([f.probability_down for f in recent_forecasts])
        avg_prob_range = np.mean([f.probability_range for f in recent_forecasts])

        # Direction agreement (how many agree with consensus)
        directions = [f.expected_direction for f in recent_forecasts]
        most_common = max(set(directions), key=directions.count)
        agreement = directions.count(most_common) / len(directions)

        consensus_direction = most_common
        consensus_confidence = max(avg_prob_up, avg_prob_down, avg_prob_range)

        return {
            'consensus_direction': consensus_direction,
            'consensus_confidence': consensus_confidence,
            'agreement_level': agreement,
            'probability_up': avg_prob_up,
            'probability_down': avg_prob_down,
            'probability_range': avg_prob_range,
            'forecast_count': len(recent_forecasts)
        }

    def get_forecast_summary(self) -> Dict[str, Any]:
        """Get complete forecast summary"""

        summary = {
            'timestamp': datetime.now().isoformat(),
            'active_impacts': len(self.impact_history[-5:]),
            'forecasts_by_timeframe': {}
        }

        for timeframe in ['5m', '15m', '1h', '4h', '1d']:
            consensus = self.calculate_forecast_consensus(timeframe)
            summary['forecasts_by_timeframe'][timeframe] = consensus

        return summary

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'PredictiveImpactAnalyzer',
    'PriceForecast',
    'ImpactAnalysis'
]
