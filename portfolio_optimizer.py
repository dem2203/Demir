# ============================================================================
# DEMIR AI TRADING BOT - Portfolio Optimizer
# ============================================================================
# Phase 3.3: Advanced Position Sizing & Risk Management
# Date: 4 Kasım 2025, 22:40 CET
# Version: 1.0 - PRODUCTION READY
#
# ✅ FEATURES:
# - Kelly Criterion position sizing
# - Risk/Reward optimization
# - Correlation-based allocation
# - Multi-coin portfolio balancing
# - Dynamic risk adjustment
# - Maximum drawdown protection
# ============================================================================

import numpy as np
from typing import Dict, List, Optional

class PortfolioOptimizer:
    """
    Advanced portfolio optimization with Kelly Criterion
    """

    def __init__(self, total_capital: float = 10000, max_risk_per_trade: float = 0.02):
        """
        Initialize portfolio optimizer

        Args:
            total_capital: Total available capital
            max_risk_per_trade: Maximum risk per trade (0.02 = 2%)
        """
        self.total_capital = total_capital
        self.max_risk_per_trade = max_risk_per_trade

        print(f"✅ Portfolio Optimizer initialized")
        print(f"   Total Capital: ${total_capital:,.2f}")
        print(f"   Max Risk/Trade: {max_risk_per_trade:.1%}")

    def calculate_kelly_criterion(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """
        Calculate Kelly Criterion for optimal position sizing

        Formula: K = (W * R - L) / R
        where:
          K = Kelly percentage
          W = Win rate (probability of win)
          R = Win/Loss ratio (avg_win / avg_loss)
          L = Loss rate (1 - W)

        Args:
            win_rate: Historical win rate (0-1)
            avg_win: Average win amount
            avg_loss: Average loss amount

        Returns:
            Kelly percentage (0-1)
        """
        if avg_loss == 0 or win_rate == 0:
            return 0

        win_loss_ratio = avg_win / avg_loss
        loss_rate = 1 - win_rate

        kelly = (win_rate * win_loss_ratio - loss_rate) / win_loss_ratio

        # Kelly can be negative (don't trade) or > 1 (leverage)
        # We cap it at 0.25 (25%) for safety (Half Kelly)
        kelly_capped = max(0, min(kelly, 0.25))

        print(f"📊 Kelly Criterion:")
        print(f"   Raw Kelly: {kelly:.2%}")
        print(f"   Capped Kelly: {kelly_capped:.2%}")
        print(f"   (Win Rate: {win_rate:.1%}, W/L Ratio: {win_loss_ratio:.2f})")

        return kelly_capped

    def calculate_position_size(self, signal_confidence: float, kelly_fraction: float, 
                               entry_price: float, stop_loss: float) -> Dict:
        """
        Calculate optimal position size

        Args:
            signal_confidence: AI confidence (0-1)
            kelly_fraction: Kelly criterion result (0-1)
            entry_price: Entry price
            stop_loss: Stop loss price

        Returns:
            Dict with position size, risk, and allocation
        """
        # Risk per trade (in dollars)
        risk_amount = self.total_capital * min(self.max_risk_per_trade, kelly_fraction)

        # Adjust by confidence
        risk_adjusted = risk_amount * signal_confidence

        # Calculate position size based on distance to stop loss
        price_risk = abs(entry_price - stop_loss) / entry_price
        position_value = risk_adjusted / price_risk if price_risk > 0 else 0

        # Number of units to buy
        units = position_value / entry_price if entry_price > 0 else 0

        # Allocation percentage
        allocation = position_value / self.total_capital

        return {
            'position_value': position_value,
            'units': units,
            'risk_amount': risk_adjusted,
            'allocation': allocation,
            'kelly_fraction': kelly_fraction,
            'confidence_adjusted': signal_confidence
        }

    def optimize_multi_coin_portfolio(self, signals: List[Dict]) -> List[Dict]:
        """
        Optimize allocation across multiple coins

        Args:
            signals: List of signals with {symbol, score, confidence}

        Returns:
            List of optimized allocations
        """
        if not signals:
            return []

        print(f"
{'='*80}")
        print(f"🎯 PORTFOLIO OPTIMIZATION: {len(signals)} signals")
        print(f"{'='*80}
")

        # Calculate total confidence-weighted score
        total_score = sum(s['score'] * s['confidence'] for s in signals)

        if total_score == 0:
            return []

        # Allocate capital proportionally to confidence-weighted scores
        allocations = []
        remaining_capital = self.total_capital

        for signal in signals:
            # Skip neutral signals
            if signal['signal'] == 'NEUTRAL':
                continue

            # Weighted allocation
            weight = (signal['score'] * signal['confidence']) / total_score
            allocated_capital = self.total_capital * weight

            # Cap individual allocation at 30%
            allocated_capital = min(allocated_capital, self.total_capital * 0.3)

            # Calculate position
            entry = signal.get('entry', signal.get('price', 0))
            sl = signal.get('sl', entry * 0.985)  # Default 1.5% SL

            if entry > 0:
                position = self.calculate_position_size(
                    signal_confidence=signal['confidence'],
                    kelly_fraction=weight,
                    entry_price=entry,
                    stop_loss=sl
                )

                allocations.append({
                    'symbol': signal['symbol'],
                    'signal': signal['signal'],
                    'score': signal['score'],
                    'confidence': signal['confidence'],
                    'allocated_capital': allocated_capital,
                    'position': position,
                    'weight': weight
                })

                remaining_capital -= allocated_capital

        # Print summary
        print("📊 ALLOCATION SUMMARY:")
        for alloc in allocations:
            print(f"   {alloc['symbol']:10} | "
                  f"Signal: {alloc['signal']:7} | "
                  f"Allocation: ${alloc['allocated_capital']:>8,.0f} ({alloc['weight']:>5.1%}) | "
                  f"Conf: {alloc['confidence']:>4.1%}")

        print(f"
💰 Remaining Capital: ${remaining_capital:,.2f}")
        print(f"{'='*80}
")

        return allocations

    def calculate_portfolio_risk(self, allocations: List[Dict], 
                                correlation_matrix: Optional[np.ndarray] = None) -> Dict:
        """
        Calculate portfolio-level risk metrics

        Args:
            allocations: List of position allocations
            correlation_matrix: Correlation between assets (optional)

        Returns:
            Dict with portfolio risk metrics
        """
        if not allocations:
            return {'portfolio_risk': 0, 'diversification_ratio': 0}

        # Individual position risks
        position_risks = [a['position']['risk_amount'] for a in allocations]
        total_risk = sum(position_risks)

        # If correlation matrix provided, calculate diversified risk
        if correlation_matrix is not None and len(correlation_matrix) == len(allocations):
            # Simplified portfolio risk calculation
            weights = np.array([a['weight'] for a in allocations])
            variance = weights @ correlation_matrix @ weights
            diversified_risk = np.sqrt(variance) * self.total_capital
            diversification_ratio = diversified_risk / total_risk if total_risk > 0 else 0
        else:
            # Assume average correlation of 0.7 (typical for crypto)
            avg_correlation = 0.7
            n = len(allocations)
            diversification_ratio = 1 / np.sqrt(1 + (n - 1) * avg_correlation)
            diversified_risk = total_risk * diversification_ratio

        return {
            'total_undiversified_risk': total_risk,
            'diversified_risk': diversified_risk,
            'diversification_ratio': diversification_ratio,
            'risk_as_percent_capital': diversified_risk / self.total_capital
        }

    def adjust_for_drawdown(self, current_drawdown: float) -> float:
        """
        Adjust position sizes based on current drawdown

        Args:
            current_drawdown: Current drawdown (0-1)

        Returns:
            Risk adjustment multiplier (0-1)
        """
        # Reduce risk as drawdown increases
        # No reduction until 5% DD, then linear reduction to 50% at 20% DD
        if current_drawdown < 0.05:
            return 1.0
        elif current_drawdown < 0.20:
            return 1.0 - (current_drawdown - 0.05) * (0.5 / 0.15)
        else:
            return 0.5  # Cap at 50% reduction

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_optimizer(total_capital: float = 10000, max_risk: float = 0.02) -> PortfolioOptimizer:
    """
    Create portfolio optimizer instance

    Args:
        total_capital: Total capital
        max_risk: Max risk per trade (0.02 = 2%)

    Returns:
        PortfolioOptimizer instance
    """
    return PortfolioOptimizer(total_capital, max_risk)

def optimize_positions(signals: List[Dict], capital: float = 10000) -> List[Dict]:
    """
    Quick optimization of multiple positions

    Args:
        signals: List of AI signals
        capital: Available capital

    Returns:
        List of optimized allocations
    """
    optimizer = PortfolioOptimizer(total_capital=capital)
    return optimizer.optimize_multi_coin_portfolio(signals)

# ============================================================================
# TESTING
# ============================================================================
if __name__ == "__main__":
    print("="*80)
    print("🎯 PORTFOLIO OPTIMIZER TEST")
    print("="*80)

    # Test Kelly Criterion
    optimizer = PortfolioOptimizer(total_capital=10000, max_risk_per_trade=0.02)
    kelly = optimizer.calculate_kelly_criterion(
        win_rate=0.60,
        avg_win=400,
        avg_loss=200
    )
    print(f"✅ Kelly Result: {kelly:.2%}
")

    # Test multi-coin optimization
    test_signals = [
        {'symbol': 'BTCUSDT', 'signal': 'LONG', 'score': 75, 'confidence': 0.8, 'entry': 35000, 'sl': 34500},
        {'symbol': 'ETHUSDT', 'signal': 'LONG', 'score': 68, 'confidence': 0.7, 'entry': 1800, 'sl': 1770},
        {'symbol': 'LTCUSDT', 'signal': 'SHORT', 'score': 45, 'confidence': 0.6, 'entry': 65, 'sl': 66}
    ]

    allocations = optimizer.optimize_multi_coin_portfolio(test_signals)
    print(f"✅ Optimization complete! {len(allocations)} positions allocated")

    # Calculate portfolio risk
    risk = optimizer.calculate_portfolio_risk(allocations)
    print(f"
📊 Portfolio Risk:")
    print(f"   Diversified Risk: ${risk['diversified_risk']:,.2f}")
    print(f"   Risk % of Capital: {risk['risk_as_percent_capital']:.2%}")
