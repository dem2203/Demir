"""
💰 DEMIR AI - STRICT RISK MANAGEMENT MODULE
============================================================================
CRITICAL: Enforces stop-loss and prevents catastrophic losses
Date: 8 November 2025
Version: 1.0 - Position Sizing & Risk Controls

🔒 PURPOSE: Ensure position size never exceeds risk tolerance
============================================================================
"""

import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import math

logger = logging.getLogger(__name__)

# ============================================================================
# POSITION SIZING CALCULATOR
# ============================================================================

@dataclass
class PositionSize:
    """Calculated position size"""
    quantity: float
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_amount: float  # Dollar amount at risk
    reward_amount: float  # Dollar amount to gain
    risk_reward_ratio: float  # e.g., 1:3
    max_loss_percent: float  # % of account at risk
    account_required: float  # Margin required
    is_valid: bool
    message: str
    timestamp: datetime = field(default_factory=datetime.now)

# ============================================================================
# RISK MANAGER
# ============================================================================

class StrictRiskManager:
    """
    Implements STRICT position sizing rules.
    Prevents catastrophic losses through proper risk management.
    """

    def __init__(self, 
                 max_risk_per_trade: float = 0.02,  # 2% max per trade
                 max_account_risk: float = 0.05,  # 5% max total risk
                 min_rr_ratio: float = 1.5,  # Minimum 1:1.5 risk:reward
                 max_leverage: float = 5.0):
        
        self.logger = logging.getLogger(__name__)
        self.max_risk_per_trade = max_risk_per_trade  # 2% per trade
        self.max_account_risk = max_account_risk  # 5% total
        self.min_rr_ratio = min_rr_ratio  # 1:1.5 minimum
        self.max_leverage = max_leverage
        
        self.trade_history: Dict[str, PositionSize] = {}
        
        self.logger.info(f"""
        ✅ StrictRiskManager initialized:
           Max risk/trade: {self.max_risk_per_trade*100:.1f}%
           Max total risk: {self.max_account_risk*100:.1f}%
           Min R:R ratio: 1:{self.min_rr_ratio:.1f}
           Max leverage: {self.max_leverage:.1f}x
        """)

    def calculate_position_size(self,
                               symbol: str,
                               direction: str,  # LONG/SHORT
                               entry_price: float,
                               stop_loss: float,
                               take_profit: float,
                               account_balance: float,
                               current_open_risk: float = 0.0,
                               leverage: float = 1.0) -> PositionSize:
        """
        Calculate position size based on STRICT risk management rules.
        
        Rules:
        1. Never risk more than 2% per trade
        2. Never have more than 5% total risk
        3. Minimum 1:1.5 risk:reward ratio
        4. Stop-loss MUST be enforced
        """
        
        self.logger.info(f"📊 Calculating position size: {symbol} {direction}")
        
        # ====================================================================
        # 1. VALIDATE INPUT PARAMETERS
        # ====================================================================
        
        if entry_price <= 0:
            return PositionSize(
                quantity=0, entry_price=entry_price, stop_loss=stop_loss,
                take_profit=take_profit, risk_amount=0, reward_amount=0,
                risk_reward_ratio=0, max_loss_percent=0, account_required=0,
                is_valid=False, message="❌ Invalid entry price"
            )
        
        if account_balance < 100:
            return PositionSize(
                quantity=0, entry_price=entry_price, stop_loss=stop_loss,
                take_profit=take_profit, risk_amount=0, reward_amount=0,
                risk_reward_ratio=0, max_loss_percent=0, account_required=0,
                is_valid=False, message="❌ Account balance too low ($100 minimum)"
            )
        
        # ====================================================================
        # 2. CHECK STOP-LOSS IS PROPERLY PLACED
        # ====================================================================
        
        if direction == 'LONG':
            if stop_loss >= entry_price:
                return PositionSize(
                    quantity=0, entry_price=entry_price, stop_loss=stop_loss,
                    take_profit=take_profit, risk_amount=0, reward_amount=0,
                    risk_reward_ratio=0, max_loss_percent=0, account_required=0,
                    is_valid=False, 
                    message="❌ LONG: Stop-loss must be BELOW entry price"
                )
            if take_profit <= entry_price:
                return PositionSize(
                    quantity=0, entry_price=entry_price, stop_loss=stop_loss,
                    take_profit=take_profit, risk_amount=0, reward_amount=0,
                    risk_reward_ratio=0, max_loss_percent=0, account_required=0,
                    is_valid=False,
                    message="❌ LONG: Take-profit must be ABOVE entry price"
                )
        
        else:  # SHORT
            if stop_loss <= entry_price:
                return PositionSize(
                    quantity=0, entry_price=entry_price, stop_loss=stop_loss,
                    take_profit=take_profit, risk_amount=0, reward_amount=0,
                    risk_reward_ratio=0, max_loss_percent=0, account_required=0,
                    is_valid=False,
                    message="❌ SHORT: Stop-loss must be ABOVE entry price"
                )
            if take_profit >= entry_price:
                return PositionSize(
                    quantity=0, entry_price=entry_price, stop_loss=stop_loss,
                    take_profit=take_profit, risk_amount=0, reward_amount=0,
                    risk_reward_ratio=0, max_loss_percent=0, account_required=0,
                    is_valid=False,
                    message="❌ SHORT: Take-profit must be BELOW entry price"
                )
        
        # ====================================================================
        # 3. CALCULATE RISK/REWARD
        # ====================================================================
        
        # Risk = distance from entry to SL (per unit)
        if direction == 'LONG':
            risk_per_unit = entry_price - stop_loss
            reward_per_unit = take_profit - entry_price
        else:
            risk_per_unit = stop_loss - entry_price
            reward_per_unit = entry_price - take_profit
        
        # Risk:Reward ratio
        rr_ratio = reward_per_unit / max(risk_per_unit, 0.0001)
        
        # ====================================================================
        # 4. CHECK MINIMUM RISK:REWARD RATIO
        # ====================================================================
        
        if rr_ratio < self.min_rr_ratio:
            return PositionSize(
                quantity=0, entry_price=entry_price, stop_loss=stop_loss,
                take_profit=take_profit, risk_amount=0, reward_amount=0,
                risk_reward_ratio=rr_ratio, max_loss_percent=0, account_required=0,
                is_valid=False,
                message=f"❌ R:R ratio ({rr_ratio:.2f}) below minimum (1:{self.min_rr_ratio:.1f})"
            )
        
        # ====================================================================
        # 5. CALCULATE QUANTITY BASED ON RISK
        # ====================================================================
        
        # Maximum risk per trade = 2% of account
        max_risk_amount = account_balance * self.max_risk_per_trade
        
        # Total risk must not exceed 5%
        max_total_risk = account_balance * self.max_account_risk
        available_risk = max_total_risk - current_open_risk
        
        if available_risk <= 0:
            return PositionSize(
                quantity=0, entry_price=entry_price, stop_loss=stop_loss,
                take_profit=take_profit, risk_amount=0, reward_amount=0,
                risk_reward_ratio=rr_ratio, max_loss_percent=0, account_required=0,
                is_valid=False,
                message=f"❌ Total account risk limit (5%) exceeded. Current: {current_open_risk/account_balance*100:.1f}%"
            )
        
        # Actual risk we can take (minimum of trade risk and remaining risk)
        actual_risk_amount = min(max_risk_amount, available_risk)
        
        # Position quantity = risk amount / risk per unit
        quantity = actual_risk_amount / max(risk_per_unit, 0.0001)
        
        # Apply leverage constraint
        margin_required = (quantity * entry_price) / leverage
        if margin_required > account_balance * 0.9:  # Leave 10% buffer
            quantity = (account_balance * 0.9 * leverage) / entry_price
        
        # ====================================================================
        # 6. RECALCULATE ACTUAL RISK/REWARD
        # ====================================================================
        
        actual_risk = quantity * risk_per_unit
        actual_reward = quantity * reward_per_unit
        max_loss_pct = (actual_risk / account_balance) * 100
        
        # ====================================================================
        # 7. VALIDATE FINAL POSITION
        # ====================================================================
        
        warnings = []
        
        if quantity < 0.001:
            warnings.append("⚠️ Position too small")
            is_valid = False
        else:
            is_valid = True
        
        if max_loss_pct > self.max_risk_per_trade * 100:
            warnings.append(f"⚠️ Risk {max_loss_pct:.1f}% exceeds max {self.max_risk_per_trade*100:.1f}%")
            is_valid = False
        
        if actual_risk + current_open_risk > account_balance * self.max_account_risk:
            warnings.append(f"⚠️ Total risk exceeds {self.max_account_risk*100:.1f}% limit")
            is_valid = False
        
        message = "✅ VALID - Position approved for execution" if is_valid else f"❌ {warnings[0]}"
        
        position = PositionSize(
            quantity=quantity,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_amount=actual_risk,
            reward_amount=actual_reward,
            risk_reward_ratio=rr_ratio,
            max_loss_percent=max_loss_pct,
            account_required=margin_required,
            is_valid=is_valid,
            message=message
        )
        
        self.trade_history[symbol] = position
        
        self.logger.info(f"""
        📊 POSITION SIZING RESULT:
           Quantity: {quantity:.8f}
           Entry: ${entry_price:.2f}
           SL: ${stop_loss:.2f}
           TP: ${take_profit:.2f}
           Risk: ${actual_risk:.2f} ({max_loss_pct:.2f}%)
           Reward: ${actual_reward:.2f}
           R:R: 1:{rr_ratio:.2f}
           Margin: ${margin_required:.2f}
           Valid: {is_valid}
        """)
        
        return position

    def enforce_stop_loss(self, 
                         symbol: str,
                         current_price: float,
                         position: PositionSize,
                         direction: str) -> Tuple[bool, str]:
        """
        ENFORCE stop-loss immediately if triggered.
        
        Returns:
        - should_close: True if stop-loss hit, close position
        - message: Explanation
        """
        
        if direction == 'LONG':
            if current_price <= position.stop_loss:
                return True, f"🛑 STOP-LOSS HIT: {symbol} @ ${current_price:.2f} <= SL ${position.stop_loss:.2f}"
        
        else:  # SHORT
            if current_price >= position.stop_loss:
                return True, f"🛑 STOP-LOSS HIT: {symbol} @ ${current_price:.2f} >= SL ${position.stop_loss:.2f}"
        
        return False, "✅ Stop-loss not hit"

    def get_account_risk_summary(self, 
                                open_positions: Dict[str, Tuple[float, float]],
                                account_balance: float) -> Dict:
        """
        Get summary of current account risk exposure.
        
        open_positions: {symbol: (risk_amount, position_direction)}
        """
        
        total_risk = sum(risk for risk, _ in open_positions.values())
        total_risk_pct = (total_risk / account_balance * 100) if account_balance > 0 else 0
        
        max_allowed = account_balance * self.max_account_risk
        risk_buffer = max_allowed - total_risk
        
        warning = ""
        if total_risk_pct > 80:
            warning = "🔴 HIGH RISK: 80%+ of risk limit used"
        elif total_risk_pct > 60:
            warning = "🟡 MEDIUM RISK: 60%+ of risk limit used"
        else:
            warning = "🟢 LOW RISK: Under 60% of risk limit"
        
        return {
            'total_risk_usd': total_risk,
            'total_risk_pct': total_risk_pct,
            'max_allowed_risk': max_allowed,
            'risk_buffer': risk_buffer,
            'open_positions': len(open_positions),
            'warning': warning
        }

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'StrictRiskManager',
    'PositionSize'
]
