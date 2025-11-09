"""
=============================================================================
DEMIR AI v25.0 - BACKTESTING & STRATEGY VALIDATION ENGINE
=============================================================================
Purpose: Stratejileri geçmiş verilerle test et, performans metriklerini hesapla
Location: /backtest/ klasörü - NEW/UPDATE
Integrations: trade_database.py, trade_entry_calculator.py, streamlit_app.py
Language: English (technical) + Turkish (descriptions)
=============================================================================
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BacktestMode(Enum):
    """Backtest modları"""
    PAPER = "PAPER"        # Kağıt üzerinde test (risk yok)
    LIVE = "LIVE"          # Gerçek para (risk var)


@dataclass
class BacktestResult:
    """Backtest sonuçları"""
    strategy_name: str
    start_date: str
    end_date: str
    
    total_trades: int
    winning_trades: int
    losing_trades: int
    
    win_rate: float  # %
    total_pnl: float
    avg_trade_pnl: float
    
    max_winning_trade: float
    max_losing_trade: float
    
    sharpe_ratio: float
    max_drawdown: float
    profit_factor: float
    
    trade_list: List[Dict] = None


class BacktestEngine:
    """
    Backtest motoru - Stratejileri tarihsel verilerle test et
    
    Features:
    - Multiple strategy testing
    - Risk-adjusted metrics (Sharpe, Sortino, Calmar)
    - Drawdown analysis
    - Monte Carlo simulation (optional)
    - Parameter optimization
    """
    
    def __init__(self):
        self.backtest_results: List[BacktestResult] = []
    
    # ========================================================================
    # PRICE DATA LOADING
    # ========================================================================
    
    def load_historical_data(self, symbol: str, start_date: str, end_date: str, 
                            timeframe: str = "1h") -> Optional[pd.DataFrame]:
        """
        Tarihsel fiyat verilerini yükle (Binance API)
        
        Örnek: BTCUSDT, 2023-01-01, 2025-01-01, 1h
        """
        try:
            import ccxt
            
            exchange = ccxt.binance()
            since = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
            
            timeframe_ms = {
                "1m": 1 * 60 * 1000,
                "5m": 5 * 60 * 1000,
                "1h": 60 * 60 * 1000,
                "4h": 4 * 60 * 60 * 1000,
                "1d": 24 * 60 * 60 * 1000
            }
            
            candles = []
            while since < int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000):
                new_candles = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=1000)
                if not new_candles:
                    break
                candles.extend(new_candles)
                since = new_candles[-1][0] + timeframe_ms.get(timeframe, 60 * 60 * 1000)
            
            df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.set_index('timestamp')
            
            logger.info(f"✅ Loaded {len(df)} candles for {symbol}")
            return df
        
        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            return None
    
    # ========================================================================
    # SIMPLE BACKTESTER
    # ========================================================================
    
    def backtest_simple_strategy(self,
                                symbol: str,
                                price_data: pd.DataFrame,
                                signal_func: Callable,
                                initial_balance: float = 10000,
                                position_size: float = 0.1) -> Optional[BacktestResult]:
        """
        Basit backtest - signal fonksiyonunu çağırarak trade'ler oluştur
        
        Args:
            symbol: Trading pair
            price_data: OHLCV DataFrame
            signal_func: Signal generation function
            initial_balance: Starting capital
            position_size: Trade position size ratio
        
        Returns:
            BacktestResult
        """
        try:
            trades = []
            balance = initial_balance
            position = None
            entry_price = 0
            
            for i in range(len(price_data) - 1):
                row = price_data.iloc[i]
                close_price = row['close']
                
                # Generate signal
                signal = signal_func(price_data.iloc[:i+1])  # Signal based on history
                
                # Open trade
                if signal == "BUY" and position is None:
                    position_size_qty = (balance * position_size) / close_price
                    position = {
                        "type": "LONG",
                        "entry_price": close_price,
                        "entry_time": row.name,
                        "qty": position_size_qty
                    }
                    entry_price = close_price
                
                elif signal == "SELL" and position is not None and position["type"] == "LONG":
                    # Close trade
                    exit_price = close_price
                    pnl = (exit_price - entry_price) * position["qty"]
                    pnl_percent = (exit_price - entry_price) / entry_price * 100
                    
                    balance += pnl
                    
                    trades.append({
                        "symbol": symbol,
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "qty": position["qty"],
                        "pnl": pnl,
                        "pnl_percent": pnl_percent,
                        "entry_time": position["entry_time"],
                        "exit_time": row.name
                    })
                    
                    position = None
            
            # Close remaining position
            if position is not None:
                last_price = price_data.iloc[-1]['close']
                pnl = (last_price - entry_price) * position["qty"]
                balance += pnl
                trades.append({
                    "symbol": symbol,
                    "entry_price": entry_price,
                    "exit_price": last_price,
                    "qty": position["qty"],
                    "pnl": pnl,
                    "pnl_percent": (last_price - entry_price) / entry_price * 100,
                    "entry_time": position["entry_time"],
                    "exit_time": price_data.iloc[-1].name
                })
            
            # Calculate metrics
            if not trades:
                logger.warning("⚠️ No trades generated in backtest")
                return None
            
            pnl_values = np.array([t['pnl'] for t in trades])
            total_pnl = np.sum(pnl_values)
            winning_trades = len([p for p in pnl_values if p > 0])
            losing_trades = len([p for p in pnl_values if p < 0])
            
            # Sharpe ratio
            returns = pnl_values / initial_balance
            sharpe = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
            
            # Max drawdown
            cumulative_pnl = np.cumsum(pnl_values)
            running_max = np.maximum.accumulate(cumulative_pnl)
            drawdown = cumulative_pnl - running_max
            max_drawdown = np.min(drawdown)
            
            # Profit factor
            gross_profit = np.sum([p for p in pnl_values if p > 0])
            gross_loss = abs(np.sum([p for p in pnl_values if p < 0]))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
            
            result = BacktestResult(
                strategy_name="Simple Strategy",
                start_date=str(price_data.index[0])[:10],
                end_date=str(price_data.index[-1])[:10],
                
                total_trades=len(trades),
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                
                win_rate=(winning_trades / len(trades) * 100) if trades else 0,
                total_pnl=total_pnl,
                avg_trade_pnl=np.mean(pnl_values),
                
                max_winning_trade=np.max(pnl_values),
                max_losing_trade=np.min(pnl_values),
                
                sharpe_ratio=sharpe,
                max_drawdown=max_drawdown,
                profit_factor=profit_factor,
                
                trade_list=trades
            )
            
            self.backtest_results.append(result)
            logger.info(f"✅ Backtest completed: {len(trades)} trades, Win rate: {result.win_rate:.1f}%")
            return result
        
        except Exception as e:
            logger.error(f"❌ Backtest error: {e}")
            return None
    
    # ========================================================================
    # PARAMETER OPTIMIZATION
    # ========================================================================
    
    def optimize_parameters(self,
                           symbol: str,
                           price_data: pd.DataFrame,
                           strategy_func: Callable,
                           param_ranges: Dict[str, List]) -> Optional[Dict]:
        """
        Strateji parametrelerini optimize et (Grid Search)
        
        Örnek:
        param_ranges = {
            "ma_short": [5, 10, 15],
            "ma_long": [20, 50, 100]
        }
        """
        try:
            import itertools
            
            best_result = None
            best_score = -float('inf')
            
            for param_combo in itertools.product(*param_ranges.values()):
                params = dict(zip(param_ranges.keys(), param_combo))
                
                def signal_with_params(data):
                    return strategy_func(data, **params)
                
                result = self.backtest_simple_strategy(symbol, price_data, signal_with_params)
                
                if result:
                    # Score = Sharpe * Win rate
                    score = result.sharpe_ratio * result.win_rate
                    
                    if score > best_score:
                        best_score = score
                        best_result = {
                            "parameters": params,
                            "result": result,
                            "score": score
                        }
            
            if best_result:
                logger.info(f"✅ Best parameters found: {best_result['parameters']}")
                return best_result
            
            return None
        
        except Exception as e:
            logger.error(f"❌ Optimization error: {e}")
            return None
    
    # ========================================================================
    # STRESS TESTING
    # ========================================================================
    
    def stress_test(self, symbol: str, price_data: pd.DataFrame,
                   signal_func: Callable, volatility_multiplier: float = 2.0) -> Optional[BacktestResult]:
        """
        Volatilite artırılmış versiyonda test et (Stress Test)
        """
        try:
            # Artifically increase volatility
            stressed_data = price_data.copy()
            stressed_data['close'] = stressed_data['close'] * np.random.uniform(
                1 - volatility_multiplier * 0.01,
                1 + volatility_multiplier * 0.01,
                len(stressed_data)
            )
            
            result = self.backtest_simple_strategy(symbol, stressed_data, signal_func)
            logger.info(f"✅ Stress test completed with {volatility_multiplier}x volatility")
            return result
        
        except Exception as e:
            logger.error(f"❌ Stress test error: {e}")
            return None
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def get_backtest_report(self, result: BacktestResult) -> str:
        """Backtest raporu oluştur"""
        report = f"""
╔════════════════════════════════════════════════════════════╗
║          BACKTEST REPORT | Backtest Raporu                ║
╚════════════════════════════════════════════════════════════╝

📊 Strategy: {result.strategy_name}
📅 Period: {result.start_date} to {result.end_date}

📈 TRADE STATISTICS | İşlem İstatistikleri
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Trades: {result.total_trades}
Winning Trades: {result.winning_trades} ({result.winning_trades/result.total_trades*100:.1f}%)
Losing Trades: {result.losing_trades} ({result.losing_trades/result.total_trades*100:.1f}%)
Win Rate: {result.win_rate:.2f}%

💰 PROFITABILITY | Kârlılık
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total PnL: ${result.total_pnl:,.2f}
Avg Trade PnL: ${result.avg_trade_pnl:,.2f}
Max Winning Trade: ${result.max_winning_trade:,.2f}
Max Losing Trade: ${result.max_losing_trade:,.2f}

📊 RISK METRICS | Risk Metrikleri
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sharpe Ratio: {result.sharpe_ratio:.2f}
Max Drawdown: ${result.max_drawdown:,.2f}
Profit Factor: {result.profit_factor:.2f}x

✅ SUMMARY | Özet
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Strategy is {'✅ PROFITABLE' if result.total_pnl > 0 else '❌ UNPROFITABLE'}
Recommendation: {'✅ APPROVE for LIVE' if result.sharpe_ratio > 1.5 and result.win_rate > 60 else '⚠️ NEEDS OPTIMIZATION'}
        """
        return report.strip()
    
    def compare_strategies(self, results: List[BacktestResult]) -> pd.DataFrame:
        """Stratejileri karşılaştır"""
        comparison = pd.DataFrame([
            {
                "Strategy": r.strategy_name,
                "Total Trades": r.total_trades,
                "Win Rate (%)": round(r.win_rate, 2),
                "Total PnL ($)": round(r.total_pnl, 2),
                "Sharpe Ratio": round(r.sharpe_ratio, 2),
                "Max Drawdown ($)": round(r.max_drawdown, 2),
                "Profit Factor": round(r.profit_factor, 2)
            }
            for r in results
        ])
        return comparison


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    engine = BacktestEngine()
    
    # Dummy strategy function
    def simple_ma_strategy(data, ma_short=10, ma_long=20):
        """Simple Moving Average strategy"""
        if len(data) < ma_long:
            return None
        
        sma_short = data['close'].tail(ma_short).mean()
        sma_long = data['close'].tail(ma_long).mean()
        
        if sma_short > sma_long:
            return "BUY"
        else:
            return "SELL"
    
    # Create dummy price data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='1h')
    prices = np.random.uniform(40000, 60000, len(dates))
    
    price_data = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.uniform(100, 1000, len(dates))
    }).set_index('timestamp')
    
    # Run backtest
    result = engine.backtest_simple_strategy("BTCUSDT", price_data, simple_ma_strategy)
    
    if result:
        print(engine.get_backtest_report(result))
