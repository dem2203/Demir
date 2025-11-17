"""
DEMIR AI BOT - Signal Engine Integration
Orchestrate all 71 layers, generate final signals
Multi-timeframe consensus, strength calculation
"""

import logging
from typing import Dict, List, Any
import numpy as np

logger = logging.getLogger(__name__)


class SignalEngine:
    """Integrate all 71 layers into final trading signal."""

    LAYER_WEIGHTS = {
        'sentiment': 0.20,
        'ml': 0.25,
        'technical': 0.25,
        'onchain': 0.10,
        'risk': 0.15,
        'execution': 0.05
    }

    def __init__(self):
        """Initialize signal engine."""
        self.all_layer_scores = {}
        self.group_consensus = {}

    def aggregate_layer_scores(
        self,
        layer_scores: Dict[str, float]
    ) -> Dict[str, List[float]]:
        """Group layer scores by category."""
        grouped = {
            'sentiment': [],
            'ml': [],
            'technical': [],
            'onchain': [],
            'risk': []
        }

        for layer, score in layer_scores.items():
            for category in grouped.keys():
                if category in layer.lower():
                    grouped[category].append(score)
                    break

        return grouped

    def calculate_group_consensus(
        self,
        grouped_scores: Dict[str, List[float]]
    ) -> Dict[str, float]:
        """Calculate consensus for each group."""
        consensus = {}

        for category, scores in grouped_scores.items():
            if scores:
                # Weighted average (higher variance means less consensus)
                consensus[category] = np.mean(scores)
            else:
                consensus[category] = 0.5  # Neutral if no scores

        return consensus

    def generate_final_signal(
        self,
        symbol: str,
        all_layer_scores: Dict[str, float],
        prices: Dict[str, float],
        timestamp: float
    ) -> Dict[str, Any]:
        """
        Generate final trading signal from all layers.

        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            all_layer_scores: Scores from all 71 layers
            prices: Current prices (entry, tp1, tp2, sl)
            timestamp: Signal timestamp

        Returns:
            Final signal dict
        """

        # Group scores
        grouped = self.aggregate_layer_scores(all_layer_scores)
        self.group_consensus = self.calculate_group_consensus(grouped)

        # Calculate final strength
        final_strength = 0
        for category, weight in self.LAYER_WEIGHTS.items():
            consensus = self.group_consensus.get(category, 0.5)
            final_strength += consensus * weight

        # Determine direction
        if final_strength >= 0.65:
            direction = 'LONG'
        elif final_strength <= 0.35:
            direction = 'SHORT'
        else:
            direction = 'NEUTRAL'

        # Calculate confidence
        bullish_count = sum(1 for s in all_layer_scores.values() if s > 0.6)
        bearish_count = sum(1 for s in all_layer_scores.values() if s < 0.4)
        total_layers = len(all_layer_scores)

        confidence = max(bullish_count, bearish_count) / total_layers

        signal = {
            'symbol': symbol,
            'direction': direction,
            'entry_price': prices.get('entry', 0),
            'tp1': prices.get('tp1', 0),
            'tp2': prices.get('tp2', 0),
            'sl': prices.get('sl', 0),
            'strength': final_strength,
            'confidence': confidence,
            'timestamp': timestamp,
            'layer_scores': all_layer_scores,
            'group_consensus': self.group_consensus,
            'bullish_layers': bullish_count,
            'bearish_layers': bearish_count,
            'neutral_layers': total_layers - bullish_count - bearish_count
        }

        logger.info(
            f"Signal generated: {symbol} {direction} "
            f"(strength: {final_strength:.2%}, confidence: {confidence:.2%})"
        )

        return signal

    def batch_generate_signals(
        self,
        signals_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate multiple signals at once."""
        results = []

        for data in signals_data:
            signal = self.generate_final_signal(
                symbol=data['symbol'],
                all_layer_scores=data['layer_scores'],
                prices=data['prices'],
                timestamp=data['timestamp']
            )
            results.append(signal)

        logger.info(f"Batch signal generation complete: {len(results)} signals")
        return results

    def filter_low_confidence_signals(
        self,
        signals: List[Dict],
        min_confidence: float = 0.70
    ) -> List[Dict]:
        """Filter out low-confidence signals."""
        filtered = [s for s in signals if s['confidence'] >= min_confidence]

        logger.info(
            f"Filtered: {len(signals)} → {len(filtered)} signals "
            f"(min confidence: {min_confidence:.0%})"
        )

        return filtered
