"""
🎯 DEMIR AI - SIGNAL QUALITY ASSURANCE MODULE
============================================================================
CRITICAL: Prevents false signals that cause money loss
Date: 8 November 2025
Version: 1.0 - Signal Validation & Confidence Calibration

🔒 PURPOSE: Convert unreliable AI signals into profitable trade decisions
============================================================================
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

# ============================================================================
# SIGNAL QUALITY CHECKS
# ============================================================================

@dataclass
class SignalValidation:
    """Signal validation result"""
    is_valid: bool
    confidence: float  # 0-100
    confidence_tier: str  # EXTREME (90+), VERY_HIGH (75-90), HIGH (60-75), MEDIUM (50-60), LOW (<50)
    risk_level: str  # SAFE, CAUTION, DANGER
    required_conditions: List[str]  # What must be true for this signal
    warning_flags: List[str]  # Issues found
    message: str
    execution_recommended: bool  # Should we actually trade this?
    position_size_factor: float  # 0.0-1.0: scale down position if <1.0
    stop_loss_tightness: float  # 1.0 = normal, 0.5 = twice as tight
    timestamp: datetime = field(default_factory=datetime.now)

# ============================================================================
# SIGNAL QUALITY VALIDATOR
# ============================================================================

class SignalQualityValidator:
    """
    Validates AI signals before execution.
    Only allows trades that meet STRICT criteria.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.signal_history: List[SignalValidation] = []
        self.accuracy_tracker = {
            'total_signals': 0,
            'executed_signals': 0,
            'profitable_signals': 0,
            'accuracy_rate': 0.0
        }

    def validate_signal(self, 
                       symbol: str,
                       direction: str,  # LONG/SHORT
                       confidence: float,  # 0-100
                       layer_scores: Dict[str, float],  # macro, derivatives, sentiment, technical
                       market_conditions: Dict,  # current market state
                       account_info: Dict) -> SignalValidation:
        """
        VALIDATE signal before execution.
        Only returns executable=True if ALL conditions met!
        """
        
        self.logger.info(f"🔍 Validating signal: {symbol} {direction} @ {confidence:.0f}%")
        
        warning_flags = []
        required_conditions = []
        position_size_factor = 1.0
        stop_loss_tightness = 1.0
        
        # ====================================================================
        # 1. CONFIDENCE CHECK - MINIMUM 75%!
        # ====================================================================
        
        if confidence < 75:
            warning_flags.append(f"❌ Confidence too low ({confidence:.0f}% < 75% minimum)")
            confidence_tier = 'LOW' if confidence < 50 else 'MEDIUM' if confidence < 60 else 'HIGH'
            self.logger.warning(f"⚠️ Signal REJECTED: Confidence {confidence:.0f}% below threshold")
            
            return SignalValidation(
                is_valid=False,
                confidence=confidence,
                confidence_tier=confidence_tier,
                risk_level='DANGER',
                required_conditions=required_conditions,
                warning_flags=warning_flags,
                message=f"Signal confidence too low ({confidence:.0f}%). Minimum: 75%",
                execution_recommended=False,
                position_size_factor=0.0,
                stop_loss_tightness=2.0  # If we did execute, ultra tight stops
            )
        
        # ====================================================================
        # 2. MULTI-LAYER CONSENSUS CHECK
        # ====================================================================
        
        # Require agreement from at least 3/4 layers
        bullish_layers = sum(1 for layer, score in layer_scores.items() if score >= 60)
        bearish_layers = sum(1 for layer, score in layer_scores.items() if score <= 40)
        
        if direction == 'LONG':
            if bullish_layers < 3:
                warning_flags.append(f"❌ Only {bullish_layers}/4 layers bullish")
                self.logger.warning(f"Signal REJECTED: Insufficient layer consensus")
                return SignalValidation(
                    is_valid=False,
                    confidence=max(0, confidence - 20),  # Reduce confidence
                    confidence_tier='MEDIUM',
                    risk_level='DANGER',
                    required_conditions=['3+ bullish layers needed'],
                    warning_flags=warning_flags,
                    message=f"Only {bullish_layers}/4 layers bullish. Need 3+ consensus.",
                    execution_recommended=False,
                    position_size_factor=0.0,
                    stop_loss_tightness=2.0
                )
            required_conditions.append(f"✅ {bullish_layers}/4 layers bullish (consensus met)")
        
        else:  # SHORT
            if bearish_layers < 3:
                warning_flags.append(f"❌ Only {bearish_layers}/4 layers bearish")
                return SignalValidation(
                    is_valid=False,
                    confidence=max(0, confidence - 20),
                    confidence_tier='MEDIUM',
                    risk_level='DANGER',
                    required_conditions=['3+ bearish layers needed'],
                    warning_flags=warning_flags,
                    message=f"Only {bearish_layers}/4 layers bearish. Need 3+ consensus.",
                    execution_recommended=False,
                    position_size_factor=0.0,
                    stop_loss_tightness=2.0
                )
            required_conditions.append(f"✅ {bearish_layers}/4 layers bearish (consensus met)")
        
        # ====================================================================
        # 3. MARKET REGIME CHECK - SIGNAL APPROPRIATE TO MARKET?
        # ====================================================================
        
        regime = market_conditions.get('regime', 'UNKNOWN')  # TREND/RANGE/VOLATILE
        vix = market_conditions.get('vix', 50)
        
        if regime == 'VOLATILE' and vix > 30:
            # High volatility: reduce position size significantly
            warning_flags.append(f"⚠️ High volatility mode (VIX={vix:.0f})")
            position_size_factor = 0.5  # 50% of normal position
            stop_loss_tightness = 1.5  # 50% wider stop loss needed
            required_conditions.append(f"⚠️ Market volatile (VIX {vix:.0f}) - reducing position to 50%")
        
        elif regime == 'RANGE':
            # Range bound: only take strong signals
            if confidence < 85:
                warning_flags.append(f"❌ Range-bound market requires 85%+ confidence (have {confidence:.0f}%)")
                return SignalValidation(
                    is_valid=False,
                    confidence=confidence,
                    confidence_tier='HIGH',
                    risk_level='CAUTION',
                    required_conditions=['85%+ confidence in range-bound market'],
                    warning_flags=warning_flags,
                    message=f"Range-bound market: need 85%+ confidence, have {confidence:.0f}%",
                    execution_recommended=False,
                    position_size_factor=0.0,
                    stop_loss_tightness=1.5
                )
            required_conditions.append(f"✅ Range-bound market with sufficient confidence ({confidence:.0f}%)")
        
        else:  # TREND
            required_conditions.append(f"✅ Trend regime detected - ideal for this signal")
        
        # ====================================================================
        # 4. MOMENTUM CHECK - Is signal direction aligned with momentum?
        # ====================================================================
        
        short_term_momentum = market_conditions.get('momentum_1h', 0)  # -100 to +100
        long_term_momentum = market_conditions.get('momentum_4h', 0)
        
        if direction == 'LONG' and short_term_momentum < -30:
            warning_flags.append(f"⚠️ Strong negative momentum ({short_term_momentum:.0f}) vs LONG signal")
            confidence = max(0, confidence - 15)  # Reduce confidence
            required_conditions.append(f"⚠️ Negative momentum detected (but confidence adjusted)")
        
        if direction == 'SHORT' and short_term_momentum > 30:
            warning_flags.append(f"⚠️ Strong positive momentum ({short_term_momentum:.0f}) vs SHORT signal")
            confidence = max(0, confidence - 15)
            required_conditions.append(f"⚠️ Positive momentum detected (but confidence adjusted)")
        
        else:
            required_conditions.append(f"✅ Momentum aligned with signal direction")
        
        # ====================================================================
        # 5. RISK/ACCOUNT CHECK
        # ============================================================ ========
        
        account_size = account_info.get('balance', 0)
        recent_loss = account_info.get('recent_loss_percent', 0)  # % of account lost recently
        
        if recent_loss > 10:
            # Recent big loss: reduce risk
            warning_flags.append(f"⚠️ Recent 10%+ loss ({recent_loss:.1f}%) - reducing position")
            position_size_factor = 0.5
            stop_loss_tightness = 1.5
            required_conditions.append(f"⚠️ Recent drawdown {recent_loss:.1f}% - reducing to {position_size_factor*100:.0f}% position")
        
        if recent_loss > 20:
            # Recent huge loss: STOP TRADING
            warning_flags.append(f"🚨 Recent 20%+ loss ({recent_loss:.1f}%) - DO NOT TRADE")
            return SignalValidation(
                is_valid=False,
                confidence=confidence,
                confidence_tier='HIGH',
                risk_level='DANGER',
                required_conditions=['Risk management override'],
                warning_flags=warning_flags,
                message=f"Recent {recent_loss:.1f}% loss exceeds risk tolerance. Trading paused.",
                execution_recommended=False,
                position_size_factor=0.0,
                stop_loss_tightness=2.0
            )
        
        if account_size < 100:
            warning_flags.append(f"❌ Account too small (${account_size:.0f})")
            return SignalValidation(
                is_valid=False,
                confidence=confidence,
                confidence_tier='HIGH',
                risk_level='DANGER',
                required_conditions=['Minimum account size $100'],
                warning_flags=warning_flags,
                message=f"Account size too low (${account_size:.0f}). Minimum: $100",
                execution_recommended=False,
                position_size_factor=0.0,
                stop_loss_tightness=2.0
            )
        
        # ====================================================================
        # 6. DETERMINE CONFIDENCE TIER
        # ====================================================================
        
        if confidence >= 90:
            confidence_tier = 'EXTREME'
            risk_level = 'SAFE'
            position_size_factor = min(1.0, position_size_factor * 1.2)  # Can increase position
        elif confidence >= 75:
            confidence_tier = 'VERY_HIGH'
            risk_level = 'SAFE'
        elif confidence >= 60:
            confidence_tier = 'HIGH'
            risk_level = 'CAUTION'
            position_size_factor *= 0.7
        else:
            confidence_tier = 'LOW'
            risk_level = 'DANGER'
            position_size_factor = 0.0
        
        # ====================================================================
        # 7. FINAL DECISION
        # ====================================================================
        
        execution_recommended = (
            confidence >= 75 and
            bullish_layers >= 3 if direction == 'LONG' else bearish_layers >= 3 and
            len(warning_flags) == 0
        )
        
        if not execution_recommended and len(warning_flags) == 0:
            # Probably just a low confidence - not critical
            message = f"Signal valid but below execution threshold. Confidence: {confidence:.0f}%"
        elif not execution_recommended:
            message = f"Signal REJECTED: {warning_flags[0]}"
        else:
            message = f"✅ SIGNAL APPROVED - Execute with {position_size_factor*100:.0f}% position size"
        
        validation = SignalValidation(
            is_valid=True,  # Data-wise valid, but not necessarily executable
            confidence=confidence,
            confidence_tier=confidence_tier,
            risk_level=risk_level,
            required_conditions=required_conditions,
            warning_flags=warning_flags,
            message=message,
            execution_recommended=execution_recommended,
            position_size_factor=position_size_factor,
            stop_loss_tightness=stop_loss_tightness
        )
        
        self.signal_history.append(validation)
        
        self.logger.info(f"""
        ✅ VALIDATION RESULT:
           Confidence: {confidence:.0f}% ({confidence_tier})
           Executable: {execution_recommended}
           Position Size: {position_size_factor*100:.0f}%
           SL Tightness: {stop_loss_tightness:.1f}x
           Risk Level: {risk_level}
        """)
        
        return validation

    def calibrate_confidence(self, raw_score: float, layer_agreement: int, 
                            momentum_alignment: bool, volatility: float) -> float:
        """
        Calibrate raw confidence score to realistic level.
        Raw score is often optimistic - this grounds it in reality.
        """
        
        # Start with raw score (typically 0-100)
        calibrated = raw_score
        
        # Layer agreement bonus/penalty
        if layer_agreement == 4:
            calibrated += 10  # All 4 layers agree
        elif layer_agreement == 3:
            calibrated += 5   # 3/4 agree (OK)
        elif layer_agreement < 3:
            calibrated -= 25  # Less than 3/4 (not good)
        
        # Momentum alignment
        if not momentum_alignment:
            calibrated -= 15  # Signal goes against momentum
        
        # Volatility penalty
        # High volatility = lower confidence
        if volatility > 30:
            calibrated *= 0.8  # 20% confidence reduction
        elif volatility > 20:
            calibrated *= 0.9  # 10% confidence reduction
        
        # Bound between 0-100
        calibrated = max(0, min(100, calibrated))
        
        return calibrated

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'SignalQualityValidator',
    'SignalValidation'
]
