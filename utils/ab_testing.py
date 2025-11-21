#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════════════════
ABTesting ENTERPRISE - DEMIR AI v8.0
════════════════════════════════════════════════════════════════════════════════
Production A/B testing framework for model and strategy evaluation
- Statistical significance testing (Chi-square, T-test)
- Multi-armed bandit algorithms (Epsilon-greedy, UCB, Thompson Sampling)
- Experiment tracking and result persistence
- Real-time performance monitoring
- Automatic winner selection based on statistical tests
"""

import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from scipy import stats
import json

logger = logging.getLogger(__name__)


@dataclass
class Variant:
    """
    A/B test variant (model version, strategy, etc.).
    
    Attributes:
        name: Variant identifier
        traffic_allocation: Percentage of traffic (0-1)
        conversions: Number of successful outcomes
        trials: Total number of trials
        metadata: Additional variant information
    """
    name: str
    traffic_allocation: float = 0.5
    conversions: int = 0
    trials: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def conversion_rate(self) -> float:
        """Calculate conversion rate."""
        return self.conversions / self.trials if self.trials > 0 else 0.0
    
    @property
    def confidence_interval(self, confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate Wilson score confidence interval."""
        if self.trials == 0:
            return (0.0, 0.0)
        
        p = self.conversion_rate
        n = self.trials
        z = stats.norm.ppf((1 + confidence) / 2)
        
        denominator = 1 + z**2 / n
        center = (p + z**2 / (2 * n)) / denominator
        margin = z * np.sqrt((p * (1 - p) / n + z**2 / (4 * n**2))) / denominator
        
        return (max(0, center - margin), min(1, center + margin))


class ABTest:
    """
    Enterprise A/B testing system for model and strategy evaluation.
    
    Features:
    - Statistical significance testing
    - Multi-armed bandit algorithms
    - Experiment tracking
    - Real-time monitoring
    - Automatic winner selection
    
    Attributes:
        experiment_name: Unique experiment identifier
        variants: Dictionary of test variants
        algorithm: Traffic allocation algorithm
        min_samples: Minimum samples for statistical tests
    """
    
    def __init__(
        self,
        experiment_name: str,
        algorithm: str = "epsilon_greedy",
        epsilon: float = 0.1,
        min_samples_per_variant: int = 100
    ):
        """
        Initialize A/B test.
        
        Args:
            experiment_name: Unique experiment identifier
            algorithm: Traffic allocation algorithm
            epsilon: Exploration rate for epsilon-greedy
            min_samples_per_variant: Minimum samples for significance test
        """
        self.experiment_name = experiment_name
        self.algorithm = algorithm
        self.epsilon = epsilon
        self.min_samples = min_samples_per_variant
        
        self.variants: Dict[str, Variant] = {}
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        
        logger.info(
            f"🧪 A/B Test '{experiment_name}' initialized - "
            f"algorithm={algorithm}, epsilon={epsilon}"
        )
    
    def add_variant(
        self,
        name: str,
        traffic_allocation: float = None,
        metadata: Optional[Dict] = None
    ):
        """
        Add a variant to the experiment.
        
        Args:
            name: Variant identifier
            traffic_allocation: Initial traffic allocation (auto if None)
            metadata: Additional variant information
        """
        if traffic_allocation is None:
            # Equal allocation by default
            n_variants = len(self.variants) + 1
            traffic_allocation = 1.0 / n_variants
            
            # Rebalance existing variants
            for v in self.variants.values():
                v.traffic_allocation = 1.0 / n_variants
        
        self.variants[name] = Variant(
            name=name,
            traffic_allocation=traffic_allocation,
            metadata=metadata or {}
        )
        
        logger.info(f"✅ Added variant '{name}' with {traffic_allocation*100:.1f}% traffic")
    
    def select_variant(self) -> str:
        """
        Select variant based on allocation algorithm.
        
        Returns:
            Selected variant name
        """
        if not self.variants:
            raise ValueError("No variants available")
        
        if self.algorithm == "epsilon_greedy":
            return self._epsilon_greedy()
        elif self.algorithm == "ucb":
            return self._ucb()
        elif self.algorithm == "thompson_sampling":
            return self._thompson_sampling()
        else:
            # Random allocation
            return np.random.choice(list(self.variants.keys()))
    
    def _epsilon_greedy(self) -> str:
        """Epsilon-greedy variant selection."""
        if np.random.random() < self.epsilon:
            # Explore: random selection
            return np.random.choice(list(self.variants.keys()))
        else:
            # Exploit: best performing variant
            best_variant = max(
                self.variants.values(),
                key=lambda v: v.conversion_rate
            )
            return best_variant.name
    
    def _ucb(self) -> str:
        """Upper Confidence Bound variant selection."""
        total_trials = sum(v.trials for v in self.variants.values())
        
        if total_trials == 0:
            return np.random.choice(list(self.variants.keys()))
        
        ucb_scores = {}
        for name, variant in self.variants.items():
            if variant.trials == 0:
                ucb_scores[name] = float('inf')
            else:
                exploration_term = np.sqrt(2 * np.log(total_trials) / variant.trials)
                ucb_scores[name] = variant.conversion_rate + exploration_term
        
        return max(ucb_scores, key=ucb_scores.get)
    
    def _thompson_sampling(self) -> str:
        """Thompson Sampling variant selection."""
        samples = {}
        for name, variant in self.variants.items():
            # Beta distribution with prior Beta(1, 1)
            alpha = variant.conversions + 1
            beta = variant.trials - variant.conversions + 1
            samples[name] = np.random.beta(alpha, beta)
        
        return max(samples, key=samples.get)
    
    def record_result(self, variant_name: str, success: bool):
        """
        Record experiment result for a variant.
        
        Args:
            variant_name: Variant that was tested
            success: Whether outcome was successful
        """
        if variant_name not in self.variants:
            logger.error(f"❌ Unknown variant: {variant_name}")
            return
        
        variant = self.variants[variant_name]
        variant.trials += 1
        if success:
            variant.conversions += 1
        
        logger.debug(
            f"📊 {variant_name}: {variant.conversions}/{variant.trials} "
            f"({variant.conversion_rate*100:.1f}%)"
        )
    
    def calculate_significance(
        self,
        variant_a: str,
        variant_b: str,
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        """
        Calculate statistical significance between two variants.
        
        Args:
            variant_a: First variant name
            variant_b: Second variant name
            alpha: Significance level (default 0.05)
            
        Returns:
            Dictionary with test results
        """
        if variant_a not in self.variants or variant_b not in self.variants:
            return {'error': 'Variant not found'}
        
        va = self.variants[variant_a]
        vb = self.variants[variant_b]
        
        # Check minimum sample size
        if va.trials < self.min_samples or vb.trials < self.min_samples:
            return {
                'significant': False,
                'reason': f'Insufficient samples (min: {self.min_samples})',
                'samples_a': va.trials,
                'samples_b': vb.trials
            }
        
        # Chi-square test for proportions
        contingency_table = [
            [va.conversions, va.trials - va.conversions],
            [vb.conversions, vb.trials - vb.conversions]
        ]
        
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        significant = p_value < alpha
        
        result = {
            'variant_a': variant_a,
            'variant_b': variant_b,
            'conversion_rate_a': va.conversion_rate,
            'conversion_rate_b': vb.conversion_rate,
            'improvement': ((vb.conversion_rate - va.conversion_rate) / va.conversion_rate * 100) if va.conversion_rate > 0 else 0,
            'chi_square': chi2,
            'p_value': p_value,
            'significant': significant,
            'confidence': 1 - alpha,
            'samples_a': va.trials,
            'samples_b': vb.trials
        }
        
        logger.info(
            f"📊 Significance test: {variant_a} vs {variant_b} - "
            f"p={p_value:.4f}, significant={significant}"
        )
        
        return result
    
    def get_winner(self, alpha: float = 0.05) -> Optional[str]:
        """
        Determine winning variant based on statistical tests.
        
        Args:
            alpha: Significance level
            
        Returns:
            Name of winning variant or None if inconclusive
        """
        if len(self.variants) < 2:
            return list(self.variants.keys())[0] if self.variants else None
        
        # Compare all variants against control (first variant)
        control_name = list(self.variants.keys())[0]
        
        for variant_name in list(self.variants.keys())[1:]:
            result = self.calculate_significance(control_name, variant_name, alpha)
            
            if result.get('significant'):
                if result['conversion_rate_b'] > result['conversion_rate_a']:
                    logger.info(f"🏆 Winner: {variant_name} (significant improvement)")
                    return variant_name
        
        # No significant difference found
        logger.info("⚖️ No clear winner - results inconclusive")
        return None
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get experiment summary with all variant statistics.
        
        Returns:
            Dictionary with experiment summary
        """
        summary = {
            'experiment_name': self.experiment_name,
            'algorithm': self.algorithm,
            'start_time': self.start_time.isoformat(),
            'duration_hours': (datetime.now() - self.start_time).total_seconds() / 3600,
            'variants': {}
        }
        
        for name, variant in self.variants.items():
            ci = variant.confidence_interval
            summary['variants'][name] = {
                'trials': variant.trials,
                'conversions': variant.conversions,
                'conversion_rate': variant.conversion_rate,
                'confidence_interval_95': ci,
                'traffic_allocation': variant.traffic_allocation,
                'metadata': variant.metadata
            }
        
        return summary
    
    def end_experiment(self):
        """Mark experiment as ended."""
        self.end_time = datetime.now()
        logger.info(f"🏁 Experiment '{self.experiment_name}' ended")


if __name__ == "__main__":
    # Test instantiation
    test = ABTest("model_comparison", algorithm="thompson_sampling")
    test.add_variant("model_v1")
    test.add_variant("model_v2")
    print(f"✅ ABTest initialized: {test.experiment_name}")
