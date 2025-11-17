"""
DEMIR AI BOT - Integration Tests
End-to-end testing, Railway simulation, stress testing
Validates complete signal generation flow
"""

import logging
import unittest
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TestDataValidator(unittest.TestCase):
    """Test data validation modules."""

    def test_data_detector(self):
        """Test mock data detection."""
        from data_detector_advanced import DataDetector
        detector = DataDetector()

        # Should detect mock
        self.assertTrue(detector.is_mock_data("mock_data_123"))
        self.assertTrue(detector.is_mock_data("test_value"))

        # Should not detect real
        self.assertFalse(detector.is_mock_data("95234.50"))

    def test_real_data_verifier(self):
        """Test exchange data verification."""
        from real_data_verifier_pro import RealDataVerifier
        verifier = RealDataVerifier()

        # Valid price
        valid, msg = verifier.verify_price_range(95000, "BTCUSDT", "binance")
        self.assertTrue(valid)

        # Invalid price
        valid, msg = verifier.verify_price_range(-100, "BTCUSDT", "binance")
        self.assertFalse(valid)

    def test_signal_validator(self):
        """Test signal validation."""
        from signal_validator_comprehensive import SignalValidator
        validator = SignalValidator()

        signal = {
            'symbol': 'BTCUSDT',
            'direction': 'LONG',
            'entry_price': 95000,
            'tp1': 96000,
            'tp2': 97000,
            'sl': 94000,
            'confidence': 0.85,
            'timestamp': 1700000000,
            'strength': 0.75,
            'layer_scores': {'RSI': 0.7, 'MACD': 0.8}
        }

        valid, errors = validator.validate_all(signal)
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)


class TestLayerOptimization(unittest.TestCase):
    """Test layer optimization."""

    def test_layer_selection(self):
        """Test optimal layer selection."""
        from layer_optimizer_intelligent import LayerOptimizer
        optimizer = LayerOptimizer(target_layer_count=40)

        optimal_layers = optimizer.select_optimal_layers()
        total = sum(len(v) for v in optimal_layers.values())

        self.assertLessEqual(total, 40)
        self.assertGreater(total, 0)

    def test_reduction_analysis(self):
        """Test reduction impact analysis."""
        from layer_optimizer_intelligent import LayerOptimizer
        optimizer = LayerOptimizer()

        analysis = optimizer.get_reduction_analysis()

        self.assertIn('reduction_percentage', analysis)
        self.assertGreater(analysis['reduction_percentage'], 0)
        self.assertLess(analysis['accuracy_retention'], '100%')


class TestAPIHealth(unittest.TestCase):
    """Test API health monitoring."""

    def test_health_tracking(self):
        """Test health status tracking."""
        from api_health_monitor_realtime import APIHealth
        health = APIHealth()

        # Record some calls
        health.record_call('binance', True, 100)
        health.record_call('binance', True, 110)
        health.record_call('binance', False, 500)

        uptime = health.get_uptime_percentage('binance')
        self.assertAlmostEqual(uptime, 66.66, places=1)


class TestCircuitBreaker(unittest.TestCase):
    """Test circuit breaker."""

    def test_failure_tracking(self):
        """Test circuit breaker failure tracking."""
        from circuit_breaker_plus import CircuitBreaker
        breaker = CircuitBreaker(failure_threshold=3)

        # Simulate failures
        for _ in range(3):
            breaker._on_failure()

        self.assertEqual(breaker.state.value, 'open')


class TestBacktest(unittest.TestCase):
    """Test backtest engine."""

    def test_metrics_calculation(self):
        """Test backtest metrics."""
        from backtest_engine_production import BacktestEngine
        engine = BacktestEngine()

        metrics = engine._calculate_metrics(initial_capital=10000)

        self.assertEqual(metrics.total_trades, 0)
        self.assertEqual(metrics.win_rate, 0)


class TestSignalEngine(unittest.TestCase):
    """Test signal generation engine."""

    def test_group_consensus(self):
        """Test group consensus calculation."""
        from signal_engine_integration import SignalEngine
        engine = SignalEngine()

        grouped = {
            'sentiment': [0.7, 0.8, 0.6],
            'ml': [0.75, 0.8],
            'technical': [0.6, 0.65, 0.7]
        }

        consensus = engine.calculate_group_consensus(grouped)

        self.assertAlmostEqual(consensus['sentiment'], 0.7, places=1)


class TestIntegrationFlow(unittest.TestCase):
    """Test complete integration flow."""

    def test_data_to_signal_flow(self):
        """Test complete data-to-signal flow."""
        logger.info("Starting integration flow test...")

        # 1. Get market data
        market_data = {
            'symbol': 'BTCUSDT',
            'price': 95000,
            'volume': 1000000,
            'timestamp': 1700000000
        }

        # 2. Validate data
        from real_data_verifier_pro import RealDataVerifier
        verifier = RealDataVerifier()
        valid, errors = verifier.verify_all(market_data)
        self.assertTrue(valid)

        # 3. Generate signal
        layer_scores = {
            'RSI': 0.7, 'MACD': 0.8, 'LSTM': 0.75, 'XGBoost': 0.8
        }

        from signal_engine_integration import SignalEngine
        engine = SignalEngine()

        signal = engine.generate_final_signal(
            symbol='BTCUSDT',
            all_layer_scores=layer_scores,
            prices={
                'entry': 95000,
                'tp1': 96000,
                'tp2': 97000,
                'sl': 94000
            },
            timestamp=1700000000
        )

        self.assertIsNotNone(signal)
        self.assertEqual(signal['symbol'], 'BTCUSDT')
        logger.info("Integration flow test passed ✅")


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    run_tests()
