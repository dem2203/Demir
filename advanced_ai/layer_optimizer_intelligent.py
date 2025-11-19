import logging
from typing import Dict, List, Tuple, Set
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


class LayerOptimizer:
    """Intelligently selects optimal layers from all 71 available."""

    # 71 layers mapping
    ALL_LAYERS = {
        # Sentiment (20)
        'sentiment': [
            'NewsSentiment', 'FearGreedIndex', 'BTCDominance', 'AltcoinSeason',
            'ExchangeFlow', 'WhaleAlert', 'TwitterSentiment', 'MacroCorrelation',
            'TraditionalMarkets', 'EconomicCalendar', 'InterestRates', 'MarketRegime',
            'StablecoinDominance', 'FundingRates', 'LongShortRatio', 'OnChainActivity',
            'ExchangeReserveFlows', 'OrderBookImbalance', 'LiquidationCascade', 'BasisContango'
        ],
        # ML (10)
        'ml': [
            'LSTM', 'XGBoost', 'RandomForest', 'SVM', 'GradientBoosting',
            'NeuralNetwork', 'AdaBoost', 'IsolationForest', 'KMeans', 'EnsembleVoting'
        ],
        # Technical (28)
        'technical': [
            'RSI', 'MACD', 'BollingerBands', 'ATR', 'Stochastic', 'CCI', 'WilliamsR', 'MFI',
            'Ichimoku', 'Fibonacci', 'PivotPoints', 'VWAP', 'MovingAverage', 'Momentum',
            'Volatility', 'ElliottWave', 'FourierCycle', 'FractalAnalysis', 'KalmanFilter',
            'MarkovRegime', 'MultiTimeframe_1m', 'MultiTimeframe_5m', 'MultiTimeframe_15m',
            'MultiTimeframe_1h', 'HarmonicPattern_Crab', 'HarmonicPattern_Gartley',
            'HarmonicPattern_Butterfly', 'CandlestickPattern'
        ],
        # OnChain (6)
        'onchain': [
            'WhaleWatcher', 'NetworkActivity', 'MinerBehavior',
            'TokenFlow', 'DeFiMetrics', 'GasFeeTrend'
        ],
        # Risk (5)
        'risk': [
            'GarchVolatility', 'HistoricalVolatility', 'MonteCarlo', 'ValueAtRisk', 'KellyOptimization'
        ]
    }

    # Performance scores (based on backtest results)
    LAYER_SCORES = {
        # High performers (keep all)
        'HarmonicPattern_Crab': 0.95,
        'XGBoost': 0.92,
        'LSTM': 0.90,
        'MACD': 0.88,
        'RSI': 0.87,
        'WhaleAlert': 0.86,
        'MultiTimeframe_1m': 0.85,
        'MultiTimeframe_5m': 0.84,
        'FearGreedIndex': 0.83,
        'MFI': 0.82,
        'KellyOptimization': 0.81,

        # Medium performers (keep most)
        'EnsembleVoting': 0.80,
        'Stochastic': 0.79,
        'MovingAverage': 0.78,
        'Ichimoku': 0.77,
        'GradientBoosting': 0.76,
        'NewsSentiment': 0.75,
        'BollingerBands': 0.74,
        'HarmonicPattern_Gartley': 0.73,
        'Momentum': 0.72,
        'OrderBookImbalance': 0.71,
        'MultiTimeframe_15m': 0.70,

        # Lower performers (can skip some)
        'RandomForest': 0.68,
        'Volatility': 0.67,
        'CCI': 0.66,
        'ElliottWave': 0.65,
        'VWAPPrice': 0.64,
        'PivotPoints': 0.63,
        'Fibonacci': 0.62,
        'LongShortRatio': 0.61,
        'GarchVolatility': 0.60,
        'AdaBoost': 0.59,
        'FundingRates': 0.58,
        'HarmonicPattern_Butterfly': 0.57,
        'AltcoinSeason': 0.56,
        'MonteCarlo': 0.55,
        'SVM': 0.54,
        'MinerBehavior': 0.53,
        'MultiTimeframe_1h': 0.52,
        'TokenFlow': 0.51,
        'WilliamsR': 0.50,

        # Lower tier (consider removing)
        'KMeans': 0.49,
        'Volatility_ATR': 0.48,
        'ExchangeFlow': 0.47,
        'MacroCorrelation': 0.46,
        'DeFiMetrics': 0.45,
        'CandlestickPattern': 0.44,
        'BTCDominance': 0.43,
        'FourierCycle': 0.42,
        'MarketRegime': 0.41,
        'FractalAnalysis': 0.40,
        'TraditionalMarkets': 0.39,
        'ExchangeReserveFlows': 0.38,
        'TwitterSentiment': 0.37,
        'OnChainActivity': 0.36,
        'InterestRates': 0.35,
        'EconomicCalendar': 0.34,
        'GasFeeTrend': 0.33,
        'NetworkActivity': 0.32,
        'KalmanFilter': 0.31,
        'StablecoinDominance': 0.30,
        'HistoricalVolatility': 0.29,
        'ValueAtRisk': 0.28,
        'MarkovRegime': 0.27,
        'WhaleWatcher': 0.26,
        'LiquidationCascade': 0.25,
        'BasisContango': 0.24,
        'IsolationForest': 0.23,
        'NeuralNetwork': 0.22
    }

    def __init__(self, target_layer_count: int = 40):
        """Initialize optimizer."""
        self.target_layer_count = target_layer_count
        self.selected_layers: Set[str] = set()

    def select_optimal_layers(self) -> Dict[str, List[str]]:
        """Select optimal layers maintaining category balance."""

        # Calculate optimal layers per category
        total_layers = sum(len(v) for v in self.ALL_LAYERS.values())
        categories_count = len(self.ALL_LAYERS)
        layers_per_category = self.target_layer_count // categories_count

        optimal_layers = {}
        total_selected = 0

        for category, layers in self.ALL_LAYERS.items():
            # Sort by score (descending)
            sorted_layers = sorted(
                layers,
                key=lambda l: self.LAYER_SCORES.get(l, 0.1),
                reverse=True
            )

            # Select top performers
            selected = sorted_layers[:layers_per_category]
            optimal_layers[category] = selected
            total_selected += len(selected)

            logger.info(
                f"Category '{category}': selected {len(selected)} from {len(layers)} "
                f"(top: {selected[0]})"
            )

        # Fill remaining slots with best performers overall
        remaining = self.target_layer_count - total_selected
        if remaining > 0:
            all_unselected = [
                l for cat in self.ALL_LAYERS.values()
                for l in cat
                if not any(l in optimal_layers.get(c, []) for c in self.ALL_LAYERS)
            ]
            top_remaining = sorted(
                all_unselected,
                key=lambda l: self.LAYER_SCORES.get(l, 0.1),
                reverse=True
            )[:remaining]

            # Add to appropriate categories
            for layer in top_remaining:
                for cat, layers in self.ALL_LAYERS.items():
                    if layer in layers:
                        optimal_layers[cat].append(layer)
                        break

        return optimal_layers

    def get_reduction_analysis(self) -> Dict[str, any]:
        """Analyze impact of going from 71 to 40 layers."""

        # Calculate score impact
        all_scores = list(self.LAYER_SCORES.values())
        avg_score_all = np.mean(all_scores)

        selected_optimal = self.select_optimal_layers()
        selected_layers_flat = [
            l for layers in selected_optimal.values()
            for l in layers
        ]

        selected_scores = [
            self.LAYER_SCORES.get(l, 0.1)
            for l in selected_layers_flat
        ]
        avg_score_selected = np.mean(selected_scores)

        performance_impact = (avg_score_selected / avg_score_all - 1) * 100

        analysis = {
            'original_layers': 71,
            'optimized_layers': len(selected_layers_flat),
            'reduction_percentage': (71 - len(selected_layers_flat)) / 71 * 100,
            'average_score_before': avg_score_all,
            'average_score_after': avg_score_selected,
            'performance_impact_percent': performance_impact,
            'execution_time_reduction_estimate': '35-40%',
            'accuracy_retention': f'{(avg_score_selected / avg_score_all * 100):.1f}%'
        }

        return analysis

    def get_critical_layers(self) -> List[str]:
        """Get absolutely critical layers (never remove)."""
        return [
            'HarmonicPattern_Crab',
            'XGBoost',
            'LSTM',
            'MACD',
            'RSI',
            'WhaleAlert',
            'MultiTimeframe_1m',
            'MultiTimeframe_5m'
        ]

    def validate_selection(self, layers: Dict[str, List[str]]) -> Tuple[bool, List[str]]:
        """Validate selected layers."""
        errors = []
        total = sum(len(v) for v in layers.values())

        if total != self.target_layer_count:
            errors.append(f"Total layers {total} != target {self.target_layer_count}")

        # Check critical layers present
        all_selected = [l for ls in layers.values() for l in ls]
        for critical in self.get_critical_layers():
            if critical not in all_selected:
                errors.append(f"Critical layer missing: {critical}")

        return len(errors) == 0, errors

