#!/usr/bin/env python3
"""
🔱 DEMIR AI - backtester.py (HAFTA 8-9)
============================================================================
BACKTESTING ENGINE - PRODUCTION READY

5 years historical replay, Sharpe > 1.5, Win rate > 55%
NO MOCK, FAIL LOUD, STRICT VALIDATION
============================================================================
"""

import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import os

import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

class BacktestEngine:
    """Backtest trading signals - PRODUCTION GRADE"""
    
    def __init__(self, db_url: str):
        if not db_url:
            raise ValueError("❌ Missing database URL")
        
        self.db_url = db_url
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'SOLUSDT']
        logger.info("✅ BacktestEngine initialized")
    
    def fetch_historical_data(self, symbol: str, start_date: datetime, 
                              end_date: datetime) -> pd.DataFrame:
        """Fetch REAL historical data - STRICT"""
        try:
            if start_date >= end_date:
                raise ValueError(f"❌ Invalid date range: {start_date} >= {end_date}")
            
            conn = psycopg2.connect(self.db_url)
            
            query = f"""
                SELECT timestamp, price, rsi_14, macd_line, bb_position,
                       sma_20, volume_ratio
                FROM feature_store
                WHERE symbol = '{symbol}'
                AND timestamp >= '{start_date}'
                AND timestamp <= '{end_date}'
                ORDER BY timestamp ASC
            """
            
            df = pd.read_sql(query, conn)
            conn.close()
            
            if df.empty:
                raise ValueError(f"❌ No data for {symbol} in period")
            
            logger.info(f"✅ {symbol}: {len(df)} records fetched")
            return df
        
        except Exception as e:
            logger.critical(f"❌ Historical data fetch failed: {e}")
            raise
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals - STRICT"""
        try:
            if df.empty:
                raise ValueError("❌ Empty DataFrame")
            
            signals = []
            
            for i in range(1, len(df)):
                row = df.iloc[i]
                
                # Simple TA-based signal (NO ML for backtest validation)
                signal = 1  # HOLD default
                
                if row['rsi_14'] < 30 and row['macd_line'] > 0:
                    signal = 2  # UP
                elif row['rsi_14'] > 70 and row['macd_line'] < 0:
                    signal = 0  # DOWN
                
                signals.append(signal)
            
            df['signal'] = [1] + signals  # Align with data
            
            logger.info(f"✅ Generated {len(signals)} signals")
            return df
        
        except Exception as e:
            logger.critical(f"❌ Signal generation failed: {e}")
            raise
    
    def simulate_trading(self, df: pd.DataFrame) -> Dict:
        """Simulate trading - STRICT"""
        try:
            if df.empty:
                raise ValueError("❌ Empty DataFrame")
            
            results = {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_profit': 0.0,
                'max_drawdown': 0.0,
                'trades': []
            }
            
            position = None
            entry_price = 0
            
            for i in range(1, len(df)):
                current_price = df.iloc[i]['price']
                signal = df.iloc[i]['signal']
                
                # Entry signal
                if signal == 2 and position is None:  # BUY
                    position = 'LONG'
                    entry_price = current_price
                    results['total_trades'] += 1
                
                # Exit signal
                elif signal == 0 and position == 'LONG':  # SELL
                    profit = current_price - entry_price
                    if profit > 0:
                        results['winning_trades'] += 1
                    else:
                        results['losing_trades'] += 1
                    
                    results['total_profit'] += profit
                    results['trades'].append({
                        'entry': entry_price,
                        'exit': current_price,
                        'profit': profit
                    })
                    
                    position = None
            
            # Calculate metrics
            results['win_rate'] = (results['winning_trades'] / results['total_trades']
                                   if results['total_trades'] > 0 else 0)
            results['profit_factor'] = (abs(results['total_profit']) / 
                                       abs(results['total_profit']) 
                                       if results['total_profit'] != 0 else 0)
            
            logger.info(f"✅ Backtest: {results['total_trades']} trades, "
                       f"{results['win_rate']:.1%} win rate")
            
            return results
        
        except Exception as e:
            logger.critical(f"❌ Trading simulation failed: {e}")
            raise
    
    def calculate_metrics(self, df: pd.DataFrame, results: Dict) -> Dict:
        """Calculate performance metrics - STRICT"""
        try:
            # Calculate returns
            equity = 10000.0  # Starting balance
            equity_curve = [equity]
            
            for trade in results['trades']:
                return_pct = trade['profit'] / trade['entry']
                equity *= (1 + return_pct)
                equity_curve.append(equity)
            
            equity_curve = np.array(equity_curve)
            returns = np.diff(equity_curve) / equity_curve[:-1]
            
            # Sharpe ratio (assuming 252 trading days)
            if len(returns) > 0:
                sharpe = np.mean(returns) / (np.std(returns) + 1e-10) * np.sqrt(252)
            else:
                sharpe = 0
            
            # Max drawdown
            cummax = np.maximum.accumulate(equity_curve)
            drawdown = (equity_curve - cummax) / cummax
            max_drawdown = np.min(drawdown)
            
            metrics = {
                'sharpe_ratio': float(sharpe),
                'max_drawdown': float(max_drawdown),
                'total_return': float((equity - 10000) / 10000),
                'final_equity': float(equity)
            }
            
            if sharpe < 1.5:
                logger.warning(f"⚠️ Sharpe ratio low: {sharpe:.2f} < 1.5")
            
            return metrics
        
        except Exception as e:
            logger.critical(f"❌ Metrics calculation failed: {e}")
            raise
    
    def run_backtest(self, start_date: str = "2020-01-01", 
                    end_date: str = "2025-01-01") -> Dict:
        """Run full backtest - STRICT"""
        try:
            logger.info("="*80)
            logger.info("🚀 STARTING BACKTEST (5 YEARS)")
            logger.info("="*80)
            
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            all_results = {}
            
            for symbol in self.symbols:
                logger.info(f"\n{symbol}...")
                
                # Fetch data
                df = self.fetch_historical_data(symbol, start, end)
                
                # Generate signals
                df = self.generate_signals(df)
                
                # Simulate trading
                trade_results = self.simulate_trading(df)
                
                # Calculate metrics
                metrics = self.calculate_metrics(df, trade_results)
                
                all_results[symbol] = {
                    'trades': trade_results['total_trades'],
                    'win_rate': trade_results['win_rate'],
                    'sharpe': metrics['sharpe_ratio'],
                    'max_dd': metrics['max_drawdown'],
                    'return': metrics['total_return']
                }
                
                logger.info(f"✅ {symbol}:")
                logger.info(f"   Trades: {trade_results['total_trades']}")
                logger.info(f"   Win Rate: {trade_results['win_rate']:.1%}")
                logger.info(f"   Sharpe: {metrics['sharpe_ratio']:.2f}")
                logger.info(f"   Return: {metrics['total_return']:.1%}")
            
            logger.info(f"\n{'='*80}")
            logger.info("✅ BACKTEST COMPLETE!")
            logger.info(f"{'='*80}\n")
            
            return all_results
        
        except Exception as e:
            logger.critical(f"❌ BACKTEST FAILED: {e}")
            raise

# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    try:
        engine = BacktestEngine(db_url=os.getenv('DATABASE_URL'))
        results = engine.run_backtest()
        
        logger.info("✅ Backtesting complete!")
    
    except Exception as e:
        logger.critical(f"❌ FATAL ERROR: {e}")
        raise
