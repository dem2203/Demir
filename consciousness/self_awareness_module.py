"""
🧠 DEMIR AI - PHASE 10: CONSCIOUSNESS ENGINE - Self-Awareness Module
======================================================================
Tracks confidence, learning progress, and mistake patterns
Date: 8 November 2025
Version: 1.0 - Production Ready
======================================================================
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class MistakeRecord:
    """Record of a trading mistake"""
    timestamp: datetime
    scenario: str  # Brief description
    expected_outcome: str
    actual_outcome: str
    consequence: float  # Loss in %
    root_cause: str  # Why it happened
    confidence_was: float  # What confidence was when decision made

@dataclass
class LearningMetric:
    """Learning progress metric"""
    metric_name: str
    current_value: float
    historical_values: List[float] = field(default_factory=list)
    improvement_rate: float = 0.0  # % improvement per time period
    timestamp: datetime = field(default_factory=datetime.now)

# ============================================================================
# SELF-AWARENESS ENGINE
# ============================================================================

class SelfAwarenessModule:
    """
    Tracks own performance, mistakes, confidence calibration
    Represents the AI's introspective capabilities
    """

    def __init__(self):
        """Initialize self-awareness"""
        self.logger = logging.getLogger(__name__)

        # Confidence tracking
        self.confidence_levels = []  # Historical confidence predictions
        self.outcomes_correct = []  # Whether actual outcome matched confidence

        # Mistake tracking
        self.mistakes: List[MistakeRecord] = []
        self.mistake_patterns: Dict[str, int] = {}  # Pattern -> count

        # Performance metrics
        self.learning_metrics: Dict[str, LearningMetric] = {}
        self.accuracy_by_regime: Dict[str, float] = {}
        self.accuracy_by_timeframe: Dict[str, float] = {}

        # Awareness state
        self.self_confidence = 0.5  # Meta-confidence (how sure about our own judgments)
        self.knowledge_gaps: List[str] = []
        self.strengths: List[str] = []
        self.weaknesses: List[str] = []

        # Learning progress
        self.learning_stage = 'EARLY'  # EARLY, DEVELOPING, MATURE, EXPERT
        self.trade_count = 0

        self.logger.info("✅ SelfAwarenessModule initialized")

    def record_prediction(self, prediction: Tuple[str, float], actual: str, 
                         regime: str = 'UNKNOWN', timeframe: str = '1h'):
        """
        Record a prediction and actual outcome for calibration
        """
        predicted_signal, confidence = prediction
        correct = predicted_signal == actual

        # Track confidence calibration
        self.confidence_levels.append(confidence)
        self.outcomes_correct.append(correct)

        # Update accuracy by regime/timeframe
        if regime not in self.accuracy_by_regime:
            self.accuracy_by_regime[regime] = []
        self.accuracy_by_regime[regime].append(float(correct))

        if timeframe not in self.accuracy_by_timeframe:
            self.accuracy_by_timeframe[timeframe] = []
        self.accuracy_by_timeframe[timeframe].append(float(correct))

        # Keep rolling window
        if len(self.confidence_levels) > 1000:
            self.confidence_levels.pop(0)
            self.outcomes_correct.pop(0)

        self.trade_count += 1

        self.logger.debug(
            f"Prediction recorded: {predicted_signal} "
            f"(conf: {confidence:.2f}), actual: {actual}, correct: {correct}"
        )

    def record_mistake(self, scenario: str, expected: str, actual: str, 
                      loss_percent: float, root_cause: str, confidence_was: float):
        """Record a trading mistake for learning"""

        mistake = MistakeRecord(
            timestamp=datetime.now(),
            scenario=scenario,
            expected_outcome=expected,
            actual_outcome=actual,
            consequence=loss_percent,
            root_cause=root_cause,
            confidence_was=confidence_was
        )

        self.mistakes.append(mistake)

        # Track mistake patterns
        pattern_key = f"{scenario}:{root_cause}"
        self.mistake_patterns[pattern_key] = self.mistake_patterns.get(pattern_key, 0) + 1

        self.logger.warning(
            f"Mistake recorded: {scenario} caused {loss_percent:.1f}% loss. "
            f"Root: {root_cause}"
        )

    def calculate_confidence_calibration(self) -> Dict[str, float]:
        """
        Check if confidence predictions match actual outcomes
        Good calibration = high confidence when right, low when wrong
        """
        if not self.confidence_levels:
            return {}

        # Group by confidence level
        calibration_bins = {}

        for confidence, correct in zip(self.confidence_levels, self.outcomes_correct):
            bin_key = f"{int(confidence * 10)}-{int(confidence * 10) + 1}/10"

            if bin_key not in calibration_bins:
                calibration_bins[bin_key] = {'correct': 0, 'total': 0}

            calibration_bins[bin_key]['total'] += 1
            if correct:
                calibration_bins[bin_key]['correct'] += 1

        # Calculate actual accuracy in each bin
        calibration = {
            bin_key: stats['correct'] / max(stats['total'], 1)
            for bin_key, stats in calibration_bins.items()
        }

        return calibration

    def get_accuracy_metrics(self) -> Dict[str, float]:
        """Get accuracy metrics by different dimensions"""

        metrics = {}

        # Overall accuracy
        if self.outcomes_correct:
            metrics['overall_accuracy'] = sum(self.outcomes_correct) / len(self.outcomes_correct)

        # By regime
        for regime, accuracies in self.accuracy_by_regime.items():
            if accuracies:
                metrics[f'accuracy_regime_{regime}'] = sum(accuracies) / len(accuracies)

        # By timeframe
        for tf, accuracies in self.accuracy_by_timeframe.items():
            if accuracies:
                metrics[f'accuracy_tf_{tf}'] = sum(accuracies) / len(accuracies)

        return metrics

    def identify_strengths_weaknesses(self):
        """
        Analyze performance to identify strengths and weaknesses
        """
        accuracy = self.get_accuracy_metrics()

        self.strengths = []
        self.weaknesses = []

        # Find where we're good (>60% accuracy)
        for key, value in accuracy.items():
            if value > 0.60:
                self.strengths.append(f"{key}: {value*100:.0f}% accuracy")
            elif value < 0.45:
                self.weaknesses.append(f"{key}: {value*100:.0f}% accuracy")

        # Identify most common mistake patterns
        if self.mistake_patterns:
            sorted_patterns = sorted(
                self.mistake_patterns.items(),
                key=lambda x: x[1],
                reverse=True
            )

            for pattern, count in sorted_patterns[:3]:
                if count >= 2:
                    self.weaknesses.insert(
                        0,
                        f"Recurring mistake: {pattern} ({count} times)"
                    )

    def identify_knowledge_gaps(self):
        """
        Identify where the AI lacks knowledge/confidence
        """
        self.knowledge_gaps = []

        # Low accuracy on specific regimes/timeframes
        accuracy = self.get_accuracy_metrics()

        for key, value in accuracy.items():
            if 'regime' in key or 'tf' in key:
                if value < 0.50:
                    self.knowledge_gaps.append(
                        f"Low confidence area: {key} ({value*100:.0f}% accurate)"
                    )

        # Scenarios with high mistake rate
        for mistake in self.mistakes[-10:]:
            if mistake.confidence_was > 0.7:  # Was confident but wrong
                self.knowledge_gaps.append(
                    f"Overconfident mistake: {mistake.scenario}"
                )

    def update_learning_stage(self):
        """Update learning stage based on progress"""

        if self.trade_count < 50:
            self.learning_stage = 'EARLY'
            self.self_confidence = 0.3
        elif self.trade_count < 200:
            self.learning_stage = 'DEVELOPING'
            self.self_confidence = 0.5
        elif self.trade_count < 1000:
            self.learning_stage = 'MATURE'
            self.self_confidence = 0.7
        else:
            self.learning_stage = 'EXPERT'
            self.self_confidence = 0.85

        # Adjust based on accuracy
        accuracy = self.get_accuracy_metrics().get('overall_accuracy', 0.5)
        self.self_confidence *= accuracy  # Dampen by actual accuracy

    def get_awareness_report(self) -> Dict[str, Any]:
        """Generate complete self-awareness report"""

        # Update analysis
        self.identify_strengths_weaknesses()
        self.identify_knowledge_gaps()
        self.update_learning_stage()

        # Get calibration
        calibration = self.calculate_confidence_calibration()

        return {
            'trade_count': self.trade_count,
            'learning_stage': self.learning_stage,
            'self_confidence': self.self_confidence,
            'accuracy_metrics': self.get_accuracy_metrics(),
            'confidence_calibration': calibration,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'knowledge_gaps': self.knowledge_gaps,
            'recent_mistakes': len(self.mistakes),
            'total_mistake_patterns': len(self.mistake_patterns),
            'timestamp': datetime.now().isoformat()
        }

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'SelfAwarenessModule',
    'MistakeRecord',
    'LearningMetric'
]
