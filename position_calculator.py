"""
FILE 16: position_calculator.py
PHASE 6.3 - POSITION CALCULATOR (Kelly Criterion)
400 lines
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

class PositionCalculator:
    """Smart Position Sizing using Kelly Criterion"""
    
    def calculate_optimal_position(
        self,
        account_balance: float,
        risk_percent: float,
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> float:
        """
        Kelly Criterion: f* = (bp - q) / b
        where:
        - b = avg_win / avg_loss
        - p = win_rate
        - q = 1 - win_rate
        
        Use 25% of Kelly for safety (conservative)
        """
        try:
            if avg_loss == 0 or win_rate == 0:
                return account_balance * 0.01  # Min 1%
            
            b = avg_win / avg_loss
            p = win_rate
            q = 1 - win_rate
            
            kelly_fraction = (b * p - q) / b
            
            # 25% Kelly (very conservative)
            position_fraction = kelly_fraction * 0.25
            
            # Calculate position size
            position_size = account_balance * position_fraction * (risk_percent / 100)
            
            # Limits: Min 1%, Max 10% of account
            position_size = max(
                min(position_size, account_balance * 0.10),
                account_balance * 0.01
            )
            
            logger.info(f"Calculated position size: {position_size:,.2f} ({position_size/account_balance*100:.2f}% of account)")
            
            return position_size
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return account_balance * 0.01

if __name__ == "__main__":
    calc = PositionCalculator()
    size = calc.calculate_optimal_position(
        account_balance=10000,
        risk_percent=2.0,
        win_rate=0.65,
        avg_win=100,
        avg_loss=50
    )
    print(f"✅ Position size: ${size:,.2f}")
