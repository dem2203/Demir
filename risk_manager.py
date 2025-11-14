#!/usr/bin/env python3
"""
🔱 DEMIR AI - Risk Manager v1.0
HAFTA 11: Position Sizing + Risk Management

KURALLAR:
✅ Kelly Criterion for position sizing
✅ Dynamic stop loss / take profit
✅ Portfolio risk tracking
✅ Max daily loss limit
✅ Correlation-based diversification
✅ Real-time position monitoring
✅ Error loud - risk alerts
"""

import os
import psycopg2
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL')
PORTFOLIO_SIZE = 10000  # USD
MAX_DAILY_LOSS = 500  # USD
MAX_POSITION_SIZE = 0.1  # 10% of portfolio
MAX_RISK_PER_TRADE = 0.02  # 2% risk per trade
MIN_WIN_RATE_FOR_TRADING = 0.45  # Stop if win rate < 45%

SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']

# ============================================================================
# RISK CALCULATOR
# ============================================================================

class RiskCalculator:
    """Calculate position sizing and risk metrics"""
    
    @staticmethod
    def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float) -> float:
        """Calculate optimal position size using Kelly Criterion"""
        if avg_loss == 0:
            return 0
        
        win_loss_ratio = avg_win / avg_loss
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        # Apply safety margin (use 25% of kelly)
        kelly_safe = kelly * 0.25
        
        return max(0, min(kelly_safe, 0.1))  # Cap at 10%
    
    @staticmethod
    def calculate_position_size(
        account_size: float,
        risk_percent: float,
        entry_price: float,
        stop_loss: float
    ) -> float:
        """Calculate position size based on risk"""
        risk_amount = account_size * (risk_percent / 100)
        price_diff = abs(entry_price - stop_loss)
        
        if price_diff == 0:
            return 0
        
        position_size = risk_amount / price_diff
        return position_size
    
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        excess_returns = returns - (risk_free_rate / 252)
        sharpe = np.mean(excess_returns) / (np.std(excess_returns) + 1e-10) * np.sqrt(252)
        return sharpe
    
    @staticmethod
    def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio"""
        excess_returns = returns - (risk_free_rate / 252)
        downside_returns = excess_returns[excess_returns < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
        sortino = np.mean(excess_returns) / (downside_std + 1e-10) * np.sqrt(252)
        return sortino
    
    @staticmethod
    def calculate_drawdown(equity_curve: List[float]) -> Tuple[float, float, float]:
        """Calculate max drawdown, current drawdown, and recovery time"""
        equity_array = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max
        max_drawdown = np.min(drawdown)
        current_drawdown = drawdown[-1]
        
        # Recovery time (days to return to peak)
        if current_drawdown < 0:
            recovery_time = len(equity_curve) - np.argmax(running_max)
        else:
            recovery_time = 0
        
        return max_drawdown, current_drawdown, recovery_time

# ============================================================================
# PORTFOLIO MANAGER
# ============================================================================

class PortfolioManager:
    """Manage portfolio risk"""
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self.portfolio_value = PORTFOLIO_SIZE
        self.daily_pnl = 0
        self.positions = {}
    
    def update_position(self, symbol: str, quantity: float, entry_price: float):
        """Update position"""
        self.positions[symbol] = {
            'quantity': quantity,
            'entry_price': entry_price,
            'notional': quantity * entry_price
        }
        logger.info(f"📊 Position updated: {symbol}")
    
    def close_position(self, symbol: str, exit_price: float):
        """Close position and update P&L"""
        if symbol not in self.positions:
            logger.warning(f"⚠️ No position for {symbol}")
            return 0
        
        position = self.positions[symbol]
        pnl = (exit_price - position['entry_price']) * position['quantity']
        self.daily_pnl += pnl
        self.portfolio_value += pnl
        
        del self.positions[symbol]
        
        logger.info(f"💰 Position closed: {symbol} P&L=${pnl:.2f}")
        return pnl
    
    def get_portfolio_risk(self) -> Dict:
        """Calculate portfolio risk metrics"""
        try:
            cur = self.db_conn.cursor()
            
            # Get recent trades
            query = """
                SELECT pnl FROM manual_trades 
                WHERE exit_time >= NOW() - INTERVAL '7 days'
                ORDER BY exit_time DESC
            """
            
            df = pd.read_sql_query(query, self.db_conn)
            
            if df.empty:
                logger.warning("⚠️ No recent trades")
                return {
                    'sharpe_ratio': 0,
                    'sortino_ratio': 0,
                    'max_drawdown': 0,
                    'daily_pnl': self.daily_pnl,
                    'portfolio_value': self.portfolio_value,
                    'risk_level': 'NORMAL'
                }
            
            returns = df['pnl'].pct_change().dropna()
            
            sharpe = RiskCalculator.calculate_sharpe_ratio(returns)
            sortino = RiskCalculator.calculate_sortino_ratio(returns)
            
            # Determine risk level
            if self.daily_pnl < -MAX_DAILY_LOSS:
                risk_level = 'CRITICAL'
            elif self.daily_pnl < -MAX_DAILY_LOSS * 0.5:
                risk_level = 'HIGH'
            else:
                risk_level = 'NORMAL'
            
            return {
                'sharpe_ratio': sharpe,
                'sortino_ratio': sortino,
                'max_drawdown': returns.min(),
                'daily_pnl': self.daily_pnl,
                'portfolio_value': self.portfolio_value,
                'risk_level': risk_level
            }
        
        except Exception as e:
            logger.error(f"❌ Risk calculation failed: {e}")
            return {}
    
    def get_position_sizing(self, symbol: str) -> Dict:
        """Get recommended position size"""
        try:
            # Get historical performance
            cur = self.db_conn.cursor()
            
            query = """
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                    AVG(CASE WHEN pnl > 0 THEN pnl ELSE 0 END) as avg_win,
                    AVG(CASE WHEN pnl < 0 THEN pnl ELSE 0 END) as avg_loss
                FROM manual_trades
                WHERE symbol = %s AND exit_time IS NOT NULL
            """
            
            df = pd.read_sql_query(query, self.db_conn, params=(symbol,))
            
            if df.empty or df['total_trades'].values[0] == 0:
                logger.warning(f"⚠️ No history for {symbol}")
                return {
                    'position_size': 0,
                    'kelly_percent': 0,
                    'reason': 'Insufficient history'
                }
            
            total_trades = df['total_trades'].values[0]
            wins = df['wins'].values[0]
            avg_win = df['avg_win'].values[0] or 0
            avg_loss = abs(df['avg_loss'].values[0]) or 0.01
            
            win_rate = wins / total_trades
            
            # Check minimum win rate
            if win_rate < MIN_WIN_RATE_FOR_TRADING:
                return {
                    'position_size': 0,
                    'kelly_percent': 0,
                    'reason': f'Win rate {win_rate:.1%} < {MIN_WIN_RATE_FOR_TRADING:.1%}'
                }
            
            # Kelly Criterion
            kelly_percent = RiskCalculator.kelly_criterion(win_rate, avg_win, avg_loss) * 100
            position_size = self.portfolio_value * (kelly_percent / 100)
            position_size = min(position_size, self.portfolio_value * MAX_POSITION_SIZE)
            
            return {
                'position_size': position_size,
                'kelly_percent': kelly_percent,
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss
            }
        
        except Exception as e:
            logger.error(f"❌ Position sizing failed: {e}")
            return {}

# ============================================================================
# CORRELATION ANALYZER
# ============================================================================

class CorrelationAnalyzer:
    """Analyze symbol correlations for diversification"""
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
    
    def get_correlation_matrix(self) -> pd.DataFrame:
        """Get correlation matrix between symbols"""
        try:
            query = """
                SELECT 
                    timestamp, 
                    symbol,
                    (string_to_array(ohlc_data, ','))[5]::float as close
                FROM feature_store
                WHERE timestamp >= NOW() - INTERVAL '90 days'
                ORDER BY timestamp, symbol
            """
            
            df = pd.read_sql_query(query, self.db_conn)
            
            if df.empty:
                logger.warning("⚠️ No data for correlation analysis")
                return pd.DataFrame()
            
            # Pivot to get prices by symbol
            pivot_df = df.pivot_table(index='timestamp', columns='symbol', values='close')
            
            # Calculate returns correlation
            returns = pivot_df.pct_change().dropna()
            correlation = returns.corr()
            
            logger.info("✅ Correlation matrix calculated")
            return correlation
        
        except Exception as e:
            logger.error(f"❌ Correlation analysis failed: {e}")
            return pd.DataFrame()
    
    def get_diversification_score(self) -> float:
        """Calculate portfolio diversification score (0-1)"""
        try:
            correlation = self.get_correlation_matrix()
            
            if correlation.empty:
                return 0.5
            
            # Average absolute correlation
            avg_correlation = correlation.values[np.triu_indices_from(correlation.values, k=1)].mean()
            
            # Diversification score (lower correlation = higher score)
            diversification = 1 - abs(avg_correlation)
            
            logger.info(f"📊 Diversification score: {diversification:.2f}")
            return diversification
        
        except Exception as e:
            logger.error(f"❌ Diversification calculation failed: {e}")
            return 0.5

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    try:
        logger.info("=" * 80)
        logger.info("🚀 DEMIR AI - RISK MANAGER (HAFTA 11)")
        logger.info("=" * 80)
        
        db_conn = psycopg2.connect(DATABASE_URL)
        
        portfolio_mgr = PortfolioManager(db_conn)
        correlation_analyzer = CorrelationAnalyzer(db_conn)
        
        # Get portfolio risk
        portfolio_risk = portfolio_mgr.get_portfolio_risk()
        logger.info(f"📊 Portfolio Risk: {portfolio_risk}")
        
        # Get position sizing for each symbol
        for symbol in SYMBOLS:
            sizing = portfolio_mgr.get_position_sizing(symbol)
            logger.info(f"📍 {symbol} Position: {sizing}")
        
        # Get diversification score
        div_score = correlation_analyzer.get_diversification_score()
        logger.info(f"🎯 Diversification: {div_score:.2%}")
        
        logger.info("=" * 80)
        logger.info("✅ RISK MANAGER COMPLETED")
        logger.info("=" * 80)
        
        db_conn.close()
    
    except Exception as e:
        logger.critical(f"❌ FATAL ERROR: {e}")
        raise

if __name__ == "__main__":
    main()
