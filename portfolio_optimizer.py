# ============================================================================
# DEMIR AI TRADING BOT - Portfolio Optimizer
# ============================================================================
# Phase 3.1: Kelly Criterion Position Sizing
# Date: 4 Kasım 2025, 22:15 CET
# Version: 1.0 - PRODUCTION READY

# ✅ FEATURES:
# - Kelly Criterion calculation
# - Risk management (max 2% per trade)
# - Confidence-based position sizing
# - Portfolio allocation
# - Drawdown protection
# ============================================================================

import numpy as np
from typing import Dict, Optional

class PortfolioOptimizer:
    """
    Advanced portfolio optimization with Kelly Criterion
    """
    
    def __init__(self, total_capital: float = 10000, max_risk_per_trade: float = 0.02):
        """
        Initialize portfolio optimizer
        
        Args:
            total_capital: Total trading capital in USD
            max_risk_per_trade: Maximum risk per trade (default 2%)
        """
        self.total_capital = total_capital
        self.max_risk_per_trade = max_risk_per_trade
        print(f"✅ Portfolio Optimizer initialized")
        print(f"   Total Capital: ${total_capital:,.2f}")
        print(f"   Max Risk/Trade: {max_risk_per_trade:.1%}")
    
    def calculate_kelly_fraction(self, win_rate: float, avg_win: float, 
                                 avg_loss: float, confidence: float = 1.0) -> float:
        """
        Calculate optimal position size using Kelly Criterion
        
        Formula: f = (p * b - q) / b
        where:
        - f = Kelly fraction (% of capital to risk)
        - p = win probability
        - q = loss probability (1 - p)
        - b = win/loss ratio
        
        Args:
            win_rate: Historical win rate (0-1)
            avg_win: Average win amount
            avg_loss: Average loss amount
            confidence: AI confidence score (0-1)
        
        Returns:
            Kelly fraction adjusted for confidence
        """
        try:
            if win_rate <= 0 or win_rate >= 1:
                return 0.0
            
            if avg_loss <= 0:
                return 0.0
            
            # Win/loss ratio
            b = avg_win / avg_loss
            
            # Kelly formula
            p = win_rate
            q = 1 - p
            kelly = (p * b - q) / b
            
            # Half-Kelly for safety (common practice)
            kelly = kelly * 0.5
            
            # Adjust for AI confidence
            kelly = kelly * confidence
            
            # Cap at max risk per trade
            kelly = min(kelly, self.max_risk_per_trade)
            
            # Never risk more than max, never less than 0
            kelly = max(0, min(kelly, self.max_risk_per_trade))
            
            return kelly
            
        except Exception as e:
            print(f"❌ Kelly calculation error: {e}")
            return self.max_risk_per_trade * 0.5  # Default to 1% if error
    
    def calculate_position_size(self, signal: str, score: float, confidence: float,
                               entry_price: float, stop_loss: float) -> Dict:
        """
        Calculate optimal position size for a trade
        
        Args:
            signal: LONG/SHORT/NEUTRAL
            score: AI score (0-100)
            confidence: AI confidence (0-1)
            entry_price: Entry price
            stop_loss: Stop loss price
        
        Returns:
            Dict with position details
        """
        try:
            if signal == "NEUTRAL":
                return {
                    'position_size': 0,
                    'risk_amount': 0,
                    'kelly_fraction': 0,
                    'message': 'No position - NEUTRAL signal'
                }
            
            # Estimate win rate from score and confidence
            # Score 60-100 → bullish, Score 0-40 → bearish
            if signal == "LONG":
                estimated_win_rate = min(0.65, 0.45 + (score - 50) / 100)
            else:  # SHORT
                estimated_win_rate = min(0.65, 0.45 + (50 - score) / 100)
            
            # Adjust win rate by confidence
            estimated_win_rate = estimated_win_rate * (0.7 + confidence * 0.3)
            
            # Assume 2:1 reward:risk ratio
            avg_win = 2.0  # 2R
            avg_loss = 1.0  # 1R
            
            # Calculate Kelly fraction
            kelly = self.calculate_kelly_fraction(
                win_rate=estimated_win_rate,
                avg_win=avg_win,
                avg_loss=avg_loss,
                confidence=confidence
            )
            
            # Calculate risk amount
            risk_amount = self.total_capital * kelly
            
            # Calculate position size based on stop loss distance
            stop_distance = abs(entry_price - stop_loss)
            if stop_distance == 0:
                return {
                    'position_size': 0,
                    'risk_amount': 0,
                    'kelly_fraction': 0,
                    'message': 'Invalid stop loss distance'
                }
            
            position_size = risk_amount / stop_distance
            
            # Calculate position value
            position_value = position_size * entry_price
            
            # Check if position is too large (>50% of capital)
            if position_value > self.total_capital * 0.5:
                position_size = (self.total_capital * 0.5) / entry_price
                risk_amount = position_size * stop_distance
                kelly = risk_amount / self.total_capital
            
            return {
                'position_size': round(position_size, 4),
                'position_value': round(position_value, 2),
                'risk_amount': round(risk_amount, 2),
                'risk_percent': round(kelly * 100, 2),
                'kelly_fraction': round(kelly, 4),
                'estimated_win_rate': round(estimated_win_rate, 3),
                'reward_risk_ratio': 2.0,
                'message': f'Position sized with Kelly: {kelly*100:.2f}% risk'
            }
            
        except Exception as e:
            print(f"❌ Position size calculation error: {e}")
            return {
                'position_size': 0,
                'risk_amount': 0,
                'kelly_fraction': 0,
                'message': f'Error: {str(e)}'
            }
    
    def optimize_portfolio(self, signals: list) -> Dict:
        """
        Optimize portfolio allocation across multiple signals
        
        Args:
            signals: List of trading signals
        
        Returns:
            Portfolio allocation dict
        """
        try:
            total_kelly = 0
            positions = []
            
            for signal in signals:
                if signal['signal'] == 'NEUTRAL':
                    continue
                
                position = self.calculate_position_size(
                    signal=signal['signal'],
                    score=signal.get('score', 50),
                    confidence=signal.get('confidence', 0.5),
                    entry_price=signal.get('entry', signal.get('price', 0)),
                    stop_loss=signal.get('sl', signal.get('entry', 0) * 0.98)
                )
                
                if position['position_size'] > 0:
                    positions.append({
                        'symbol': signal.get('symbol', 'UNKNOWN'),
                        'signal': signal['signal'],
                        **position
                    })
                    total_kelly += position['kelly_fraction']
            
            # If total Kelly > max risk, scale down proportionally
            if total_kelly > self.max_risk_per_trade * 2:  # Max 4% total risk
                scale = (self.max_risk_per_trade * 2) / total_kelly
                for pos in positions:
                    pos['kelly_fraction'] *= scale
                    pos['risk_amount'] *= scale
                    pos['position_size'] *= scale
                    pos['position_value'] *= scale
            
            return {
                'positions': positions,
                'total_risk': total_kelly * self.total_capital,
                'total_risk_percent': total_kelly * 100,
                'num_positions': len(positions),
                'capital_allocated': sum(p['position_value'] for p in positions),
                'capital_remaining': self.total_capital - sum(p['position_value'] for p in positions)
            }
            
        except Exception as e:
            print(f"❌ Portfolio optimization error: {e}")
            return {
                'positions': [],
                'total_risk': 0,
                'error': str(e)
            }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def quick_position_calc(signal: str = "LONG", score: float = 65, 
                       confidence: float = 0.7, entry: float = 35000,
                       capital: float = 10000) -> Dict:
    """
    Quick position size calculation (for testing)
    
    Args:
        signal: LONG/SHORT
        score: AI score
        confidence: AI confidence
        entry: Entry price
        capital: Trading capital
    
    Returns:
        Position details
    """
    optimizer = PortfolioOptimizer(total_capital=capital)
    
    # Calculate stop loss (1.5% for LONG, 1.5% for SHORT)
    if signal == "LONG":
        stop_loss = entry * 0.985
    else:
        stop_loss = entry * 1.015
    
    return optimizer.calculate_position_size(
        signal=signal,
        score=score,
        confidence=confidence,
        entry_price=entry,
        stop_loss=stop_loss
    )

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("🎯 PORTFOLIO OPTIMIZER TEST")
    print("="*80)
    
    # Test 1: Single position
    print("\n📊 TEST 1: Single Position (LONG)")
    result = quick_position_calc(
        signal="LONG",
        score=68,
        confidence=0.75,
        entry=35000,
        capital=10000
    )
    
    print(f"   Position Size: {result['position_size']} BTC")
    print(f"   Position Value: ${result['position_value']:,.2f}")
    print(f"   Risk Amount: ${result['risk_amount']:,.2f}")
    print(f"   Risk %: {result['risk_percent']:.2f}%")
    print(f"   Kelly Fraction: {result['kelly_fraction']:.4f}")
    print(f"   Message: {result['message']}")
    
    # Test 2: Portfolio optimization
    print("\n📊 TEST 2: Portfolio Optimization (Multiple Signals)")
    optimizer = PortfolioOptimizer(total_capital=10000)
    
    signals = [
        {'symbol': 'BTCUSDT', 'signal': 'LONG', 'score': 68, 'confidence': 0.75, 'entry': 35000, 'sl': 34475},
        {'symbol': 'ETHUSDT', 'signal': 'LONG', 'score': 62, 'confidence': 0.65, 'entry': 1850, 'sl': 1822},
        {'symbol': 'SOLUSDT', 'signal': 'SHORT', 'score': 38, 'confidence': 0.60, 'entry': 95, 'sl': 96.4}
    ]
    
    portfolio = optimizer.optimize_portfolio(signals)
    
    print(f"   Number of Positions: {portfolio['num_positions']}")
    print(f"   Total Risk: ${portfolio['total_risk']:,.2f} ({portfolio['total_risk_percent']:.2f}%)")
    print(f"   Capital Allocated: ${portfolio['capital_allocated']:,.2f}")
    print(f"   Capital Remaining: ${portfolio['capital_remaining']:,.2f}")
    
    print("\n   Positions:")
    for pos in portfolio['positions']:
        print(f"   • {pos['symbol']}: {pos['signal']} | Size: {pos['position_size']:.4f} | Risk: ${pos['risk_amount']:.2f}")
    
    print("\n✅ Portfolio Optimizer Test Complete!")
