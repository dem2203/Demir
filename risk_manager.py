#!/usr/bin/env python3

"""
🔱 DEMIR AI - Risk Manager v1.0 (PRODUCTION)
Dynamic Position Sizing + Drawdown Protection

FEATURES:
✅ Position sizing based on equity
✅ Volatility adjustment
✅ Drawdown protection (daily/weekly)
✅ Win rate feedback
✅ Emergency stop logic
"""

import os
import logging
import json
from datetime import datetime, timedelta
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# RISK MANAGER
# ============================================================================

class RiskManager:
    """Manage trading risk and position sizing"""
    
    def __init__(self, initial_capital: float = 10000):
        """
        Initialize Risk Manager
        
        Args:
            initial_capital: Starting capital in USD
        """
        self.initial_capital = initial_capital
        self.current_balance = initial_capital
        self.daily_pnl = 0
        self.weekly_pnl = 0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.max_drawdown = 0
        self.peak_balance = initial_capital
        
        # Risk parameters
        self.risk_per_trade = 0.02  # 2% per trade
        self.max_daily_loss = 0.05  # 5% daily max
        self.max_weekly_loss = 0.10  # 10% weekly max
        self.max_position_size = 0.25  # 25% of capital max
        
        logger.info(f"🛡️ Risk Manager initialized (capital: ${initial_capital})")
    
    def calculate_position_size(self, current_price: float, sl_price: float, volatility: float = 1.0) -> float:
        """
        Calculate position size based on:
        - Account equity
        - Stop loss distance
        - Volatility
        
        Args:
            current_price: Entry price
            sl_price: Stop loss price
            volatility: Volatility multiplier (0.5 = low vol, 1.5 = high vol)
        
        Returns:
            Position size in USD
        """
        try:
            # Risk amount (2% of current balance)
            risk_amount = self.current_balance * self.risk_per_trade
            
            # Stop loss distance
            stop_distance = abs(current_price - sl_price) / current_price
            
            # Position size = risk_amount / stop_distance
            position_size = risk_amount / stop_distance if stop_distance > 0 else 0
            
            # Volatility adjustment (high vol = smaller position)
            position_size = position_size / volatility
            
            # Max position size limit (25% of capital)
            max_pos = self.current_balance * self.max_position_size
            position_size = min(position_size, max_pos)
            
            logger.info(f"📊 Position size: ${position_size:.2f} (Vol adj: {volatility}x)")
            
            return float(position_size)
        
        except Exception as e:
            logger.error(f"❌ Position sizing error: {e}")
            return 0
    
    def check_trade_allowed(self) -> Dict:
        """Check if trading should be allowed"""
        try:
            # Daily loss check
            if self.daily_pnl < -self.current_balance * self.max_daily_loss:
                return {
                    'allowed': False,
                    'reason': f'Daily loss limit hit: ${self.daily_pnl:.2f}',
                    'status': 'PAUSE_DAILY'
                }
            
            # Weekly loss check
            if self.weekly_pnl < -self.current_balance * self.max_weekly_loss:
                return {
                    'allowed': False,
                    'reason': f'Weekly loss limit hit: ${self.weekly_pnl:.2f}',
                    'status': 'PAUSE_WEEKLY'
                }
            
            # Win rate check (if below 45%, reduce risk)
            if self.total_trades >= 50:
                win_rate = self.winning_trades / self.total_trades
                if win_rate < 0.45:
                    self.risk_per_trade = 0.01  # Reduce to 1%
                    logger.warning(f"⚠️ Low win rate ({win_rate:.1%}) - reduced risk to 1%")
                    return {
                        'allowed': True,
                        'reason': f'Low win rate ({win_rate:.1%}) - reduced risk',
                        'status': 'CAUTION'
                    }
            
            return {'allowed': True, 'reason': 'Trading allowed', 'status': 'OK'}
        
        except Exception as e:
            logger.error(f"❌ Trade check error: {e}")
            return {'allowed': False, 'reason': str(e)}
    
    def update_trade_result(self, pnl: float, is_win: bool):
        """Update stats after trade"""
        try:
            self.current_balance += pnl
            self.daily_pnl += pnl
            self.weekly_pnl += pnl
            self.total_trades += 1
            
            if is_win:
                self.winning_trades += 1
                logger.info(f"✅ Win! P&L: +${pnl:.2f}")
            else:
                self.losing_trades += 1
                logger.info(f"❌ Loss! P&L: -${abs(pnl):.2f}")
            
            # Track peak and drawdown
            if self.current_balance > self.peak_balance:
                self.peak_balance = self.current_balance
            
            drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
            if drawdown > self.max_drawdown:
                self.max_drawdown = drawdown
            
            # Calculate win rate
            win_rate = self.winning_trades / self.total_trades if self.total_trades > 0 else 0
            
            logger.info(f"📊 Account: ${self.current_balance:.2f} | Win rate: {win_rate:.1%} | DD: {drawdown:.1%}")
        
        except Exception as e:
            logger.error(f"❌ Trade update error: {e}")
    
    def reset_daily_stats(self):
        """Reset daily P&L (call at 00:00)"""
        self.daily_pnl = 0
        logger.info("📅 Daily stats reset")
    
    def reset_weekly_stats(self):
        """Reset weekly P&L (call every Monday)"""
        self.weekly_pnl = 0
        logger.info("📅 Weekly stats reset")
    
    def get_status(self) -> Dict:
        """Get current status"""
        win_rate = self.winning_trades / self.total_trades if self.total_trades > 0 else 0
        
        return {
            'balance': float(self.current_balance),
            'total_pnl': float(self.current_balance - self.initial_capital),
            'total_pnl_percent': float((self.current_balance / self.initial_capital - 1) * 100),
            'daily_pnl': float(self.daily_pnl),
            'weekly_pnl': float(self.weekly_pnl),
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': float(win_rate),
            'max_drawdown': float(self.max_drawdown),
            'status': 'HEALTHY' if win_rate > 0.55 else 'CAUTION' if win_rate > 0.45 else 'ALERT'
        }

# ============================================================================
# TRADE EXECUTION MANAGER
# ============================================================================

class TradeExecutor:
    """Execute trades with risk management"""
    
    def __init__(self, risk_manager: RiskManager):
        self.risk_manager = risk_manager
        self.open_trades = []
        logger.info("💰 Trade Executor initialized")
    
    def place_order(self, signal: Dict) -> Dict:
        """
        Place trade order with full risk management
        
        Args:
            signal: Signal with entry, TP, SL, confidence
        
        Returns:
            Order confirmation
        """
        try:
            # Check if trading allowed
            check = self.risk_manager.check_trade_allowed()
            if not check['allowed']:
                logger.warning(f"⚠️ Trade blocked: {check['reason']}")
                return {
                    'status': 'REJECTED',
                    'reason': check['reason']
                }
            
            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(
                signal['entry_price'],
                signal['sl'],
                volatility=1.0 + (1 - signal.get('confidence', 0.5)) * 0.5
            )
            
            # Check if position size is valid
            if position_size <= 0:
                return {
                    'status': 'REJECTED',
                    'reason': 'Invalid position size'
                }
            
            # Create trade
            trade = {
                'id': len(self.open_trades) + 1,
                'symbol': signal['symbol'],
                'signal_type': signal['signal_type'],
                'entry_price': signal['entry_price'],
                'sl': signal['sl'],
                'tp1': signal['tp1'],
                'tp2': signal['tp2'],
                'tp3': signal['tp3'],
                'position_size': position_size,
                'risk_amount': position_size * (signal['entry_price'] - signal['sl']) / signal['entry_price'],
                'reward_amount': position_size * (signal['tp2'] - signal['entry_price']) / signal['entry_price'],
                'risk_reward': signal.get('risk_reward', 0),
                'confidence': signal.get('confidence', 0),
                'timestamp': datetime.now().isoformat(),
                'status': 'OPEN'
            }
            
            self.open_trades.append(trade)
            
            logger.info(f"✅ Trade #{trade['id']} opened: {signal['symbol']} {signal['signal_type']} @ ${signal['entry_price']:.2f}")
            logger.info(f"   Position: ${position_size:.2f} | Risk: ${trade['risk_amount']:.2f} | Reward: ${trade['reward_amount']:.2f}")
            
            return {
                'status': 'SUCCESS',
                'trade': trade
            }
        
        except Exception as e:
            logger.error(f"❌ Order placement error: {e}")
            return {
                'status': 'ERROR',
                'reason': str(e)
            }
    
    def close_trade(self, trade_id: int, exit_price: float):
        """Close trade and update stats"""
        try:
            trade = next((t for t in self.open_trades if t['id'] == trade_id), None)
            
            if not trade:
                logger.error(f"❌ Trade #{trade_id} not found")
                return
            
            # Calculate P&L
            if trade['signal_type'] == 'LONG':
                pnl = (exit_price - trade['entry_price']) / trade['entry_price'] * trade['position_size']
            else:  # SHORT
                pnl = (trade['entry_price'] - exit_price) / trade['entry_price'] * trade['position_size']
            
            is_win = pnl > 0
            
            # Update risk manager
            self.risk_manager.update_trade_result(pnl, is_win)
            
            # Close trade
            trade['exit_price'] = exit_price
            trade['pnl'] = pnl
            trade['status'] = 'CLOSED'
            
            logger.info(f"📊 Trade #{trade_id} closed: {'WIN' if is_win else 'LOSS'} ${pnl:.2f}")
        
        except Exception as e:
            logger.error(f"❌ Trade closure error: {e}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    logger.info("=" * 80)
    logger.info("🔱 DEMIR AI - RISK MANAGER v1.0")
    logger.info("=" * 80)
    
    # Initialize
    rm = RiskManager(initial_capital=10000)
    executor = TradeExecutor(rm)
    
    # Test signal
    test_signal = {
        'symbol': 'BTCUSDT',
        'signal_type': 'LONG',
        'entry_price': 43250,
        'sl': 42800,
        'tp1': 43750,
        'tp2': 44250,
        'tp3': 44750,
        'risk_reward': 3.0,
        'confidence': 0.85
    }
    
    # Place order
    result = executor.place_order(test_signal)
    print(json.dumps(result, indent=2))
    
    # Check status
    status = rm.get_status()
    print(json.dumps(status, indent=2))
    
    logger.info("✅ Risk management test complete")

if __name__ == "__main__":
    main()
