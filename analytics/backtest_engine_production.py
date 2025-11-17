"""
DEMIR AI v6.0 - PHASE 4 [58/NEW]
Backtester 3-Year Historical
Montecarlo Simulation, Performance Metrics, Real Data Analysis
Production-Grade Historical Backtesting Engine
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class Backtester3Year:
    """Professional 3-year historical backtester"""
    
    def __init__(self, initial_capital: float = 10000):
        """Initialize backtester"""
        self.initial_capital = initial_capital
        self.annual_rf_rate = 0.02  # 2% risk-free rate
        self.trading_days_per_year = 252
        logger.info(f"📈 3-Year Backtester initialized (Capital: ${initial_capital})")
    
    def backtest(self, symbol: str, signals: List[Dict], ohlcv: List[Dict]) -> Dict[str, any]:
        """Run comprehensive backtest on 3+ years of data"""
        
        try:
            logger.info(f"🔄 Starting backtest for {symbol}...")
            
            if len(ohlcv) < 252:  # Need at least 1 year
                logger.warning("⚠️ Insufficient data for backtest")
                return {'error': 'Need at least 1 year of data'}
            
            # Sort signals by entry time
            sorted_signals = sorted(signals, key=lambda x: x.get('timestamp', 0))
            
            # Initialize tracking
            trades = []
            equity_curve = [self.initial_capital]
            portfolio_value = self.initial_capital
            win_count = 0
            loss_count = 0
            total_pnl = 0
            max_portfolio = self.initial_capital
            min_portfolio = self.initial_capital
            peak_portfolio = self.initial_capital
            
            # Process each signal
            for i, signal in enumerate(sorted_signals):
                if i + 1 >= len(ohlcv):
                    break
                
                try:
                    entry_price = signal.get('entry_price', ohlcv[i]['close'])
                    entry_index = i + 1
                    exit_price = ohlcv[entry_index]['close']
                    exit_time = ohlcv[entry_index]['timestamp']
                    
                    # Calculate PnL
                    if signal.get('direction') == 'LONG':
                        pnl = (exit_price - entry_price) / entry_price
                    else:  # SHORT
                        pnl = (entry_price - exit_price) / entry_price
                    
                    # Position size (Kelly-based)
                    kelly = signal.get('kelly', 0.1)
                    position_size = portfolio_value * kelly
                    trade_pnl = position_size * pnl
                    
                    # Update portfolio
                    portfolio_value += trade_pnl
                    total_pnl += trade_pnl
                    
                    # Track trade
                    if pnl > 0:
                        win_count += 1
                    else:
                        loss_count += 1
                    
                    trades.append({
                        'symbol': symbol,
                        'direction': signal.get('direction'),
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'pnl': float(pnl),
                        'pnl_amount': float(trade_pnl),
                        'portfolio_value': float(portfolio_value)
                    })
                    
                    # Update equity curve
                    equity_curve.append(portfolio_value)
                    
                    # Update peak/drawdown tracking
                    if portfolio_value > peak_portfolio:
                        peak_portfolio = portfolio_value
                    
                    max_portfolio = max(max_portfolio, portfolio_value)
                    min_portfolio = min(min_portfolio, portfolio_value)
                
                except Exception as e:
                    logger.debug(f"Trade processing error: {e}")
                    continue
            
            total_trades = win_count + loss_count
            if total_trades == 0:
                return {'error': 'No trades executed'}
            
            # Calculate metrics
            win_rate = win_count / total_trades
            avg_win = np.mean([t['pnl'] for t in trades if t['pnl'] > 0]) if win_count > 0 else 0
            avg_loss = abs(np.mean([t['pnl'] for t in trades if t['pnl'] < 0])) if loss_count > 0 else 0
            
            # Profit factor
            gross_profit = sum([t['pnl_amount'] for t in trades if t['pnl_amount'] > 0])
            gross_loss = abs(sum([t['pnl_amount'] for t in trades if t['pnl_amount'] < 0]))
            profit_factor = gross_profit / (gross_loss + 1e-10)
            
            # Return metrics
            total_return = (portfolio_value - self.initial_capital) / self.initial_capital
            
            # Sharpe ratio
            returns = np.diff(equity_curve) / equity_curve[:-1]
            sharpe = self._calculate_sharpe(returns)
            
            # Max drawdown
            max_drawdown = self._calculate_max_drawdown(equity_curve)
            
            # Sortino ratio
            sortino = self._calculate_sortino(returns)
            
            # Recovery factor
            recovery_factor = total_return / max(abs(max_drawdown), 1e-10)
            
            # CAGR (Compound Annual Growth Rate)
            years = len(ohlcv) / self.trading_days_per_year
            cagr = (portfolio_value / self.initial_capital) ** (1 / years) - 1 if years > 0 else 0
            
            result = {
                'symbol': symbol,
                'total_trades': total_trades,
                'wins': win_count,
                'losses': loss_count,
                'win_rate': float(win_rate),
                'profit_factor': float(profit_factor),
                'avg_win': float(avg_win),
                'avg_loss': float(avg_loss),
                'total_pnl': float(total_pnl),
                'total_return_pct': float(total_return * 100),
                'portfolio_value': float(portfolio_value),
                'initial_capital': float(self.initial_capital),
                'gross_profit': float(gross_profit),
                'gross_loss': float(gross_loss),
                'max_drawdown_pct': float(max_drawdown * 100),
                'sharpe_ratio': float(sharpe),
                'sortino_ratio': float(sortino),
                'recovery_factor': float(recovery_factor),
                'cagr_pct': float(cagr * 100),
                'trades': trades,
                'backtest_start': datetime.fromtimestamp(ohlcv[0]['timestamp'] / 1000).isoformat(),
                'backtest_end': datetime.fromtimestamp(ohlcv[-1]['timestamp'] / 1000).isoformat()
            }
            
            logger.info(f"✅ Backtest complete: WinRate={win_rate:.1%}, Sharpe={sharpe:.2f}, MaxDD={max_drawdown*100:.1f}%")
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Backtest error: {e}")
            return {'error': str(e)}
    
    def _calculate_sharpe(self, returns: np.ndarray) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) < 2:
            return 0.0
        
        excess_return = np.mean(returns) - (self.annual_rf_rate / self.trading_days_per_year)
        volatility = np.std(returns)
        
        if volatility == 0:
            return 0.0
        
        sharpe = excess_return / volatility * np.sqrt(self.trading_days_per_year)
        return float(sharpe)
    
    def _calculate_sortino(self, returns: np.ndarray) -> float:
        """Calculate Sortino ratio (only downside volatility)"""
        if len(returns) < 2:
            return 0.0
        
        excess_return = np.mean(returns) - (self.annual_rf_rate / self.trading_days_per_year)
        
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0:
            downside_volatility = 0.0
        else:
            downside_volatility = np.std(downside_returns)
        
        if downside_volatility == 0:
            return float(excess_return * np.sqrt(self.trading_days_per_year))
        
        sortino = excess_return / downside_volatility * np.sqrt(self.trading_days_per_year)
        return float(sortino)
    
    def _calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """Calculate maximum drawdown"""
        if len(equity_curve) < 2:
            return 0.0
        
        peak = equity_curve[0]
        max_dd = 0.0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            
            drawdown = (peak - value) / peak
            if drawdown > max_dd:
                max_dd = drawdown
        
        return float(-max_dd)
    
    def monte_carlo_simulation(self, backtest_result: Dict, simulations: int = 1000) -> Dict[str, any]:
        """Run Monte Carlo simulation on trades"""
        
        try:
            trades = backtest_result.get('trades', [])
            if len(trades) < 2:
                return {'error': 'Insufficient trades for simulation'}
            
            pnl_list = [t['pnl'] for t in trades]
            portfolio_value = self.initial_capital
            
            worst_case = portfolio_value
            best_case = portfolio_value
            avg_case = portfolio_value
            
            for _ in range(simulations):
                sim_portfolio = self.initial_capital
                
                for _ in range(len(trades)):
                    random_pnl = np.random.choice(pnl_list)
                    sim_portfolio *= (1 + random_pnl)
                
                worst_case = min(worst_case, sim_portfolio)
                best_case = max(best_case, sim_portfolio)
                avg_case += sim_portfolio
            
            avg_case /= simulations
            
            return {
                'simulations': simulations,
                'worst_case': float(worst_case),
                'best_case': float(best_case),
                'average_case': float(avg_case),
                'worst_case_loss_pct': float((worst_case - self.initial_capital) / self.initial_capital * 100),
                'best_case_gain_pct': float((best_case - self.initial_capital) / self.initial_capital * 100)
            }
        
        except Exception as e:
            logger.error(f"Monte Carlo error: {e}")
            return {'error': str(e)}


class BacktestReportGenerator:
    """Generate professional backtest reports"""
    
    @staticmethod
    def generate_report(backtest_result: Dict, monte_carlo_result: Dict = None) -> str:
        """Generate text report"""
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           DEMIR AI v6.0 - BACKTEST REPORT                    ║
╚══════════════════════════════════════════════════════════════╝

📊 SYMBOL: {backtest_result.get('symbol', 'N/A')}
📅 PERIOD: {backtest_result.get('backtest_start', 'N/A')} to {backtest_result.get('backtest_end', 'N/A')}

╔══ TRADE STATISTICS ═══════════════════════════════════════════╗
│ Total Trades:        {backtest_result.get('total_trades', 0):>8} trades
│ Winning Trades:      {backtest_result.get('wins', 0):>8} ({backtest_result.get('win_rate', 0)*100:>5.1f}%)
│ Losing Trades:       {backtest_result.get('losses', 0):>8}
│ Avg Win:             {backtest_result.get('avg_win', 0):>8.2%}
│ Avg Loss:            {backtest_result.get('avg_loss', 0):>8.2%}
│ Profit Factor:       {backtest_result.get('profit_factor', 0):>8.2f}

╔══ RETURNS & RISK ═════════════════════════════════════════════╗
│ Initial Capital:     ${backtest_result.get('initial_capital', 0):>12,.2f}
│ Final Portfolio:     ${backtest_result.get('portfolio_value', 0):>12,.2f}
│ Total Return:        {backtest_result.get('total_return_pct', 0):>8.1f}%
│ CAGR:                {backtest_result.get('cagr_pct', 0):>8.1f}%
│ Max Drawdown:        {backtest_result.get('max_drawdown_pct', 0):>8.1f}%

╔══ RISK-ADJUSTED RETURNS ══════════════════════════════════════╗
│ Sharpe Ratio:        {backtest_result.get('sharpe_ratio', 0):>8.2f}
│ Sortino Ratio:       {backtest_result.get('sortino_ratio', 0):>8.2f}
│ Recovery Factor:     {backtest_result.get('recovery_factor', 0):>8.2f}

"""
        
        if monte_carlo_result:
            report += f"""
╔══ MONTE CARLO SIMULATION (1000x) ═════════════════════════════╗
│ Worst Case:          ${monte_carlo_result.get('worst_case', 0):>12,.2f} ({monte_carlo_result.get('worst_case_loss_pct', 0):>6.1f}%)
│ Best Case:           ${monte_carlo_result.get('best_case', 0):>12,.2f} ({monte_carlo_result.get('best_case_gain_pct', 0):>6.1f}%)
│ Average Case:        ${monte_carlo_result.get('average_case', 0):>12,.2f}
"""
        
        report += "\n╚═════════════════════════════════════════════════════════════════╝\n"
        
        return report
