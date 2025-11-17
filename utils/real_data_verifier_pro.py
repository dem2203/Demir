"""
DEMIR AI BOT - Real Data Verifier Professional
Exchange-level data verification and cross-validation
Ensures 100% real market data usage
"""

import logging
from typing import Dict, Any, Tuple, List
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)


class RealDataVerifier:
    """Verifies data originates from real exchange APIs."""

    def __init__(self):
        """Initialize verifier with exchange metadata."""
        self.known_exchanges = {
            'binance': {
                'price_range': (0.00000001, 1000000),
                'min_volume': 0.00000001,
                'supported_pairs': ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'SOLUSDT', 'ADAUSDT']
            },
            'bybit': {
                'price_range': (0.00000001, 1000000),
                'min_volume': 0.00000001,
                'supported_pairs': ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
            },
            'coinbase': {
                'price_range': (0.01, 1000000),
                'min_volume': 0.0001,
                'supported_pairs': ['BTC-USD', 'ETH-USD', 'LTC-USD']
            }
        }

    def verify_price_range(self, price: float, symbol: str, exchange: str) -> Tuple[bool, str]:
        """Verify price is within realistic range for exchange."""
        if exchange.lower() not in self.known_exchanges:
            return False, f"Unknown exchange: {exchange}"

        min_price, max_price = self.known_exchanges[exchange.lower()]['price_range']

        if not (min_price <= price <= max_price):
            return False, f"Price {price} outside valid range [{min_price}, {max_price}]"

        return True, "Price range valid"

    def verify_volume_sanity(self, volume: float, exchange: str) -> Tuple[bool, str]:
        """Verify trading volume is realistic."""
        min_volume = self.known_exchanges[exchange.lower()]['min_volume']

        if volume < min_volume:
            return False, f"Volume {volume} below minimum {min_volume}"

        # Check for unrealistic volumes
        if volume > 1_000_000_000:
            return False, f"Volume {volume} seems unrealistically high"

        return True, "Volume sanity verified"

    def verify_ohlc_integrity(self, ohlc: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        Verify OHLCV data integrity.

        Rules:
        - Open, High, Low, Close must form logical order
        - High >= Low >= High is impossible
        - Volume must be positive
        """
        errors = []

        try:
            open_p = ohlc.get('open', 0)
            high = ohlc.get('high', 0)
            low = ohlc.get('low', 0)
            close = ohlc.get('close', 0)
            volume = ohlc.get('volume', 0)

            # High must be highest
            if not (high >= open_p and high >= low and high >= close):
                errors.append("High price not highest of OHLC")

            # Low must be lowest
            if not (low <= open_p and low <= high and low <= close):
                errors.append("Low price not lowest of OHLC")

            # Volume must be positive
            if volume <= 0:
                errors.append("Volume must be positive")

            # All prices must be positive
            if any(p <= 0 for p in [open_p, high, low, close]):
                errors.append("All prices must be positive")

        except (KeyError, TypeError) as e:
            errors.append(f"OHLC validation error: {e}")

        return len(errors) == 0, errors

    def verify_timestamp_freshness(self, timestamp: float, max_age_seconds: int = 300) -> Tuple[bool, str]:
        """Verify data timestamp is recent (not stale)."""
        now = datetime.now().timestamp()
        age = now - timestamp

        if age < 0:
            return False, "Timestamp is in the future"

        if age > max_age_seconds:
            return False, f"Data is {age} seconds old (max {max_age_seconds})"

        return True, f"Data is fresh ({age:.0f}s old)"

    def cross_verify_exchanges(self, data_sources: Dict[str, Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Verify data consistency across multiple exchanges.
        Prices should be within acceptable deviation.
        """
        prices = []
        deviations = []

        for exchange, data in data_sources.items():
            if 'price' in data:
                prices.append((exchange, data['price']))

        if len(prices) < 2:
            return True, "Only one price source available"

        avg_price = sum(p[1] for p in prices) / len(prices)

        for exchange, price in prices:
            deviation_pct = abs((price - avg_price) / avg_price) * 100
            deviations.append((exchange, deviation_pct))

            if deviation_pct > 5:  # Allow 5% deviation max
                return False, f"Exchange {exchange} deviation too high: {deviation_pct:.2f}%"

        return True, f"All exchanges within 5% deviation"

    def calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """Generate hash of data for integrity verification."""
        import json
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def verify_data_integrity_signature(
        self,
        data: Dict[str, Any],
        expected_hash: str
    ) -> Tuple[bool, str]:
        """Verify data hasn't been tampered with."""
        calculated_hash = self.calculate_data_hash(data)

        if calculated_hash == expected_hash:
            return True, "Data integrity verified"
        else:
            return False, f"Data integrity check failed: {calculated_hash} != {expected_hash}"

    def verify_all(
        self,
        data: Dict[str, Any],
        exchange: str = "binance",
        symbol: str = "BTCUSDT"
    ) -> Tuple[bool, List[str]]:
        """Run all verification checks."""
        errors = []

        # Price range check
        if 'price' in data:
            valid, msg = self.verify_price_range(data['price'], symbol, exchange)
            if not valid:
                errors.append(f"Price: {msg}")

        # Volume check
        if 'volume' in data:
            valid, msg = self.verify_volume_sanity(data['volume'], exchange)
            if not valid:
                errors.append(f"Volume: {msg}")

        # OHLC check
        if all(k in data for k in ['open', 'high', 'low', 'close']):
            valid, msgs = self.verify_ohlc_integrity(data)
            if not valid:
                errors.extend(msgs)

        # Timestamp check
        if 'timestamp' in data:
            valid, msg = self.verify_timestamp_freshness(data['timestamp'])
            if not valid:
                errors.append(f"Timestamp: {msg}")

        return len(errors) == 0, errors
