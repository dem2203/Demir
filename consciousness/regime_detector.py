"""
🧠 DEMIR AI - PHASE 10: CONSCIOUSNESS ENGINE - Regime Detector
=========================================================================
Kalman Filter + HMM for market regime detection (TREND/RANGE/VOLATILE)
Date: 8 November 2025
Version: 1.0 - Production Ready
=========================================================================
"""

import logging
from typing import Dict, Tuple, List, Optional
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime

try:
    from hmmlearn import hmm
except ImportError:
    hmm = None

logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class KalmanState:
    """State of Kalman filter"""
    position: float  # Estimated value
    velocity: float  # Estimated rate of change
    uncertainty: float  # Estimation uncertainty
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RegimeState:
    """Current market regime state"""
    regime: str  # TREND, RANGE, VOLATILE
    confidence: float  # 0-1
    duration_bars: int  # How many bars in this regime
    volatility_level: str  # LOW, MEDIUM, HIGH
    trend_direction: str  # UP, DOWN, NEUTRAL
    timestamp: datetime = field(default_factory=datetime.now)

# ============================================================================
# KALMAN FILTER
# ============================================================================

class KalmanFilter:
    """
    1D Kalman Filter for price smoothing
    Estimates true price trajectory
    """

    def __init__(self, process_variance: float = 0.01, measurement_variance: float = 4.0):
        """
        Initialize Kalman filter
        process_variance: How much we expect price to change
        measurement_variance: Measurement noise
        """
        self.logger = logging.getLogger(__name__)

        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.state_estimate = 0.0
        self.estimate_error = 1.0

        self.logger.info("✅ KalmanFilter initialized")

    def update(self, measurement: float) -> float:
        """Update filter with new measurement (price)"""

        # Prediction step
        prediction = self.state_estimate
        prediction_error = self.estimate_error + self.process_variance

        # Update step
        kalman_gain = prediction_error / (prediction_error + self.measurement_variance)

        self.state_estimate = prediction + kalman_gain * (measurement - prediction)
        self.estimate_error = (1 - kalman_gain) * prediction_error

        return self.state_estimate

    def get_velocity(self, measurements: List[float], window: int = 5) -> float:
        """Estimate velocity (rate of change)"""
        if len(measurements) < 2:
            return 0.0

        # Use last 'window' measurements to estimate velocity
        recent = measurements[-window:]
        velocity = (recent[-1] - recent[0]) / max(len(recent) - 1, 1)
        return velocity

# ============================================================================
# HIDDEN MARKOV MODEL - REGIME DETECTION
# ============================================================================

class HMMRegimeDetector:
    """
    Hidden Markov Model for regime detection
    States: TREND (strong direction), RANGE (consolidation), VOLATILE (unstable)
    """

    def __init__(self, n_states: int = 3):
        """Initialize HMM regime detector"""
        self.logger = logging.getLogger(__name__)
        self.n_states = n_states
        self.state_names = ['TREND', 'RANGE', 'VOLATILE']

        # HMM model (will be trained on historical data)
        self.model = None
        if hmm:
            self.model = hmm.GaussianHMM(n_components=n_states, covariance_type="diag")
            self.logger.info("✅ HMMRegimeDetector initialized with hmmlearn")
        else:
            self.logger.warning("⚠️ hmmlearn not available, using fallback detector")

        self.regime_history = []
        self.smoothed_prices = []

    def detect_regime(self, prices: np.ndarray, volumes: np.ndarray) -> Tuple[str, float]:
        """
        Detect current market regime
        Returns (regime_name, confidence)
        """
        if len(prices) < 10:
            return 'RANGE', 0.5

        if self.model and hmm:
            return self._hmm_detect(prices, volumes)
        else:
            return self._fallback_detect(prices, volumes)

    def _hmm_detect(self, prices: np.ndarray, volumes: np.ndarray) -> Tuple[str, float]:
        """HMM-based regime detection"""

        # Calculate features
        returns = np.diff(np.log(prices))
        volatility = np.std(returns[-20:]) if len(returns) >= 20 else np.std(returns)

        # Features for HMM: [return, volatility, volume]
        X = np.column_stack([
            returns[-20:],  # Last 20 returns
            np.full(20, volatility),  # Volatility
            volumes[-20:] / np.mean(volumes[-20:])  # Normalized volume
        ])

        try:
            # Predict regime for latest observation
            latest = np.array([[returns[-1], volatility, volumes[-1] / np.mean(volumes)]])
            regime_idx = self.model.predict(latest)[0]
            confidence = np.max(self.model.predict_proba(latest))

            regime_name = self.state_names[regime_idx]
            return regime_name, float(confidence)

        except Exception as e:
            self.logger.warning(f"HMM detection failed: {e}")
            return self._fallback_detect(prices, volumes)

    def _fallback_detect(self, prices: np.ndarray, volumes: np.ndarray) -> Tuple[str, float]:
        """Fallback regime detection using heuristics"""

        # Calculate metrics
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns[-20:]) if len(returns) >= 20 else np.std(returns)

        # Trend detection (ATR-like)
        high_low = np.max(prices[-20:]) - np.min(prices[-20:])
        atr = high_low / np.mean(prices[-20:])

        # Momentum
        momentum = np.sum(returns[-10:]) if len(returns) >= 10 else 0

        # Regime classification
        if volatility > 0.05:  # High volatility
            regime = 'VOLATILE'
            confidence = min(1.0, volatility / 0.1)
        elif abs(momentum) > 0.02:  # Strong momentum
            regime = 'TREND'
            confidence = min(1.0, abs(momentum) / 0.05)
        else:  # Low volatility & momentum
            regime = 'RANGE'
            confidence = min(1.0, (0.05 - volatility) / 0.05)

        return regime, max(0.3, min(1.0, confidence))

# ============================================================================
# COMPLETE REGIME DETECTOR
# ============================================================================

class RegimeDetector:
    """
    Complete regime detection system
    Combines Kalman filter + HMM + Volatility analysis
    """

    def __init__(self):
        """Initialize regime detector"""
        self.logger = logging.getLogger(__name__)

        self.kalman = KalmanFilter()
        self.hmm_detector = HMMRegimeDetector()

        self.price_history = []
        self.volume_history = []
        self.regime_history = []

        self.current_regime = RegimeState(
            regime='RANGE',
            confidence=0.5,
            duration_bars=0,
            volatility_level='MEDIUM',
            trend_direction='NEUTRAL'
        )

        self.logger.info("✅ RegimeDetector initialized")

    def update(self, price: float, volume: float) -> RegimeState:
        """
        Update detector with new price/volume
        Returns current regime state
        """
        # Update Kalman filter
        smoothed_price = self.kalman.update(price)

        # Store history
        self.price_history.append(price)
        self.volume_history.append(volume)

        # Keep reasonable window (last 100 bars)
        if len(self.price_history) > 100:
            self.price_history.pop(0)
            self.volume_history.pop(0)

        if len(self.price_history) < 10:
            return self.current_regime

        # Detect regime
        prices_array = np.array(self.price_history)
        volumes_array = np.array(self.volume_history)

        regime_name, regime_confidence = self.hmm_detector.detect_regime(
            prices_array, volumes_array
        )

        # Calculate volatility level
        returns = np.diff(np.log(prices_array))
        volatility = np.std(returns[-20:]) if len(returns) >= 20 else np.std(returns)

        if volatility > 0.05:
            volatility_level = 'HIGH'
        elif volatility > 0.025:
            volatility_level = 'MEDIUM'
        else:
            volatility_level = 'LOW'

        # Calculate trend direction
        recent_return = (prices_array[-1] - prices_array[-10]) / prices_array[-10] if len(prices_array) >= 10 else 0

        if recent_return > 0.02:
            trend_direction = 'UP'
        elif recent_return < -0.02:
            trend_direction = 'DOWN'
        else:
            trend_direction = 'NEUTRAL'

        # Update regime state
        if regime_name == self.current_regime.regime:
            self.current_regime.duration_bars += 1
        else:
            self.current_regime.duration_bars = 1

        self.current_regime = RegimeState(
            regime=regime_name,
            confidence=regime_confidence,
            duration_bars=self.current_regime.duration_bars,
            volatility_level=volatility_level,
            trend_direction=trend_direction
        )

        self.regime_history.append(self.current_regime)

        return self.current_regime

    def get_regime_summary(self) -> Dict[str, any]:
        """Get regime summary"""
        return {
            'current_regime': self.current_regime.regime,
            'confidence': self.current_regime.confidence,
            'duration_bars': self.current_regime.duration_bars,
            'volatility_level': self.current_regime.volatility_level,
            'trend_direction': self.current_regime.trend_direction,
            'recent_regimes': [r.regime for r in self.regime_history[-10:]]
        }

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'RegimeDetector',
    'KalmanFilter',
    'HMMRegimeDetector',
    'RegimeState'
]
