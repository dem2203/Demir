"""
DEMIR AI BOT - Emergency Stop Loss
Market crash protection, cascading failures prevention
Auto stop-loss triggers for extreme conditions
"""

import logging
from typing import Tuple, List
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class EmergencyStopLoss:
    """Emergency stop-loss triggers for extreme conditions."""

    def __init__(self):
        """Initialize emergency stop-loss."""
        self.triggered = False
        self.trigger_time = None

    def check_flash_crash(
        self,
        price: float,
        sma_50: float,
        threshold_percent: float = 10.0
    ) -> Tuple[bool, str]:
        """Detect flash crash (price down >10% from SMA50)."""
        if sma_50 == 0:
            return False, "SMA50 not available"

        deviation_percent = abs((price - sma_50) / sma_50) * 100

        if deviation_percent > threshold_percent and price < sma_50:
            msg = f"FLASH CRASH DETECTED: {deviation_percent:.1f}% below SMA50"
            logger.critical(msg)
            return True, msg

        return False, ""

    def check_circuit_breaker_hit(
        self,
        price_change_percent: float,
        threshold: float = 7.0
    ) -> Tuple[bool, str]:
        """Check if price moved beyond circuit breaker threshold."""
        if abs(price_change_percent) > threshold:
            msg = f"CIRCUIT BREAKER: {price_change_percent:.1f}% move"
            logger.critical(msg)
            return True, msg

        return False, ""

    def check_volatility_spike(
        self,
        current_atr: float,
        avg_atr: float,
        spike_threshold: float = 3.0
    ) -> Tuple[bool, str]:
        """Detect extreme volatility spike."""
        if avg_atr == 0:
            return False, ""

        atr_ratio = current_atr / avg_atr

        if atr_ratio > spike_threshold:
            msg = f"VOLATILITY SPIKE: ATR ratio {atr_ratio:.2f}x above average"
            logger.critical(msg)
            return True, msg

        return False, ""

    def check_liquidation_cascade(
        self,
        liquidations_usd: float,
        threshold: float = 10_000_000
    ) -> Tuple[bool, str]:
        """Detect liquidation cascade."""
        if liquidations_usd > threshold:
            msg = f"LIQUIDATION CASCADE: ${liquidations_usd/1_000_000:.1f}M in liquidations"
            logger.critical(msg)
            return True, msg

        return False, ""

    def check_exchange_down(
        self,
        api_uptime_percent: float,
        threshold: float = 90.0
    ) -> Tuple[bool, str]:
        """Check if exchange is having issues."""
        if api_uptime_percent < threshold:
            msg = f"EXCHANGE ISSUE: Uptime only {api_uptime_percent:.1f}%"
            logger.warning(msg)
            return True, msg

        return False, ""

    def run_all_checks(
        self,
        market_data: dict
    ) -> Tuple[bool, List[str]]:
        """Run all emergency checks."""
        emergencies = []

        # Flash crash check
        triggered, msg = self.check_flash_crash(
            price=market_data.get('price', 0),
            sma_50=market_data.get('sma_50', 0)
        )
        if triggered:
            emergencies.append(msg)

        # Circuit breaker check
        triggered, msg = self.check_circuit_breaker_hit(
            price_change_percent=market_data.get('price_change_24h', 0)
        )
        if triggered:
            emergencies.append(msg)

        # Volatility spike check
        triggered, msg = self.check_volatility_spike(
            current_atr=market_data.get('atr_current', 0),
            avg_atr=market_data.get('atr_avg', 1)
        )
        if triggered:
            emergencies.append(msg)

        # Liquidation cascade check
        triggered, msg = self.check_liquidation_cascade(
            liquidations_usd=market_data.get('liquidations_usd', 0)
        )
        if triggered:
            emergencies.append(msg)

        if emergencies:
            self.triggered = True
            self.trigger_time = datetime.now()
            logger.critical(f"EMERGENCY STOP-LOSS TRIGGERED: {len(emergencies)} conditions")

        return len(emergencies) > 0, emergencies

    def should_close_all_positions(self) -> bool:
        """Determine if all positions should be closed."""
        return self.triggered

    def reset(self):
        """Reset emergency trigger."""
        self.triggered = False
        self.trigger_time = None
        logger.info("Emergency stop-loss reset")
