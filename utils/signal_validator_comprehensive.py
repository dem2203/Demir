"""
DEMIR AI BOT - Signal Validator Comprehensive
Complete signal validation and integrity checking
Business logic and data quality verification
"""

import logging
from typing import Dict, Any, Tuple, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SignalStrength(Enum):
    """Signal strength levels."""
    STRONG_BUY = 5
    BUY = 4
    NEUTRAL = 3
    SELL = 2
    STRONG_SELL = 1


@dataclass
class Signal:
    """Signal data structure."""
    symbol: str
    direction: str  # LONG, SHORT, NEUTRAL
    entry_price: float
    tp1: float
    tp2: float
    sl: float
    confidence: float
    timestamp: float
    strength: float
    layer_scores: Dict[str, float]
    metadata: Dict[str, Any]


class SignalValidator:
    """Comprehensive signal validation engine."""

    REQUIRED_SIGNAL_FIELDS = [
        'symbol', 'direction', 'entry_price',
        'tp1', 'tp2', 'sl', 'confidence',
        'timestamp', 'strength', 'layer_scores'
    ]

    VALID_DIRECTIONS = ['LONG', 'SHORT', 'NEUTRAL']

    def __init__(self):
        """Initialize signal validator."""
        self.validation_errors: List[str] = []

    def validate_structure(self, signal_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate signal has required fields."""
        errors = []

        for field in self.REQUIRED_SIGNAL_FIELDS:
            if field not in signal_data:
                errors.append(f"Missing required field: {field}")
            elif signal_data[field] is None:
                errors.append(f"Field is None: {field}")

        return len(errors) == 0, errors

    def validate_price_logic(self, signal_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate price logic (TP > Entry > SL for LONG, opposite for SHORT)."""
        errors = []

        try:
            entry = signal_data['entry_price']
            tp1 = signal_data['tp1']
            tp2 = signal_data['tp2']
            sl = signal_data['sl']
            direction = signal_data['direction']

            if direction == 'LONG':
                # For LONG: TP > Entry > SL
                if tp1 <= entry:
                    errors.append(f"TP1 ({tp1}) must be > Entry ({entry})")
                if tp2 <= tp1:
                    errors.append(f"TP2 ({tp2}) must be > TP1 ({tp1})")
                if sl >= entry:
                    errors.append(f"SL ({sl}) must be < Entry ({entry})")

            elif direction == 'SHORT':
                # For SHORT: Entry > TP > SL
                if tp1 >= entry:
                    errors.append(f"TP1 ({tp1}) must be < Entry ({entry})")
                if tp2 >= tp1:
                    errors.append(f"TP2 ({tp2}) must be < TP1 ({tp1})")
                if sl <= entry:
                    errors.append(f"SL ({sl}) must be > Entry ({entry})")

        except KeyError as e:
            errors.append(f"Missing price field: {e}")

        return len(errors) == 0, errors

    def validate_confidence_range(self, confidence: float) -> Tuple[bool, str]:
        """Validate confidence is between 0 and 1."""
        if not (0 <= confidence <= 1):
            return False, f"Confidence must be 0-1, got {confidence}"
        return True, "OK"

    def validate_layer_scores(self, layer_scores: Dict[str, float]) -> Tuple[bool, List[str]]:
        """Validate layer scores are properly formatted."""
        errors = []

        if not isinstance(layer_scores, dict):
            errors.append("Layer scores must be dictionary")
            return False, errors

        if len(layer_scores) == 0:
            errors.append("At least one layer score required")

        for layer_name, score in layer_scores.items():
            if not (0 <= score <= 1):
                errors.append(f"Layer {layer_name} score {score} outside 0-1 range")

        return len(errors) == 0, errors

    def validate_direction(self, direction: str) -> Tuple[bool, str]:
        """Validate signal direction."""
        if direction not in self.VALID_DIRECTIONS:
            return False, f"Invalid direction: {direction}"
        return True, "OK"

    def validate_symbol_format(self, symbol: str) -> Tuple[bool, str]:
        """Validate trading pair symbol format."""
        if not isinstance(symbol, str):
            return False, "Symbol must be string"

        if not symbol.endswith('USDT'):
            return False, "Symbol must end with USDT (e.g., BTCUSDT)"

        if len(symbol) < 7:  # Min AAUSDT
            return False, "Symbol too short"

        return True, "OK"

    def validate_all(self, signal_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Run all validation checks."""
        all_errors = []

        # Structure validation
        valid, errors = self.validate_structure(signal_data)
        all_errors.extend(errors)
        if not valid:
            return False, all_errors

        # Direction validation
        valid, msg = self.validate_direction(signal_data.get('direction', ''))
        if not valid:
            all_errors.append(msg)

        # Symbol validation
        valid, msg = self.validate_symbol_format(signal_data.get('symbol', ''))
        if not valid:
            all_errors.append(msg)

        # Price logic validation
        valid, errors = self.validate_price_logic(signal_data)
        all_errors.extend(errors)

        # Confidence validation
        valid, msg = self.validate_confidence_range(signal_data.get('confidence', 0))
        if not valid:
            all_errors.append(msg)

        # Layer scores validation
        valid, errors = self.validate_layer_scores(signal_data.get('layer_scores', {}))
        all_errors.extend(errors)

        return len(all_errors) == 0, all_errors

    def get_signal_strength_category(self, strength_score: float) -> SignalStrength:
        """Categorize signal strength."""
        if strength_score >= 0.8:
            return SignalStrength.STRONG_BUY
        elif strength_score >= 0.65:
            return SignalStrength.BUY
        elif strength_score >= 0.35:
            return SignalStrength.NEUTRAL
        elif strength_score >= 0.2:
            return SignalStrength.SELL
        else:
            return SignalStrength.STRONG_SELL
