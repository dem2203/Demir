"""
🔱 DEMIR AI TRADING BOT - BACKTEST ENGINE v1.0
PHASE 3.2: Historical Data Testing & Performance Analysis
Date: 1 Kasım 2025

ÖZELLİKLER:
✅ Historical data loading (Binance API)
✅ AI decision simulation
✅ Performance metrics (Win Rate, Sharpe, Drawdown, PF)
✅ Equity curve generation
✅ Trade-by-trade analysis
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

class BacktestEngine:
    def __init__(self, symbol, initial_capital=10000, risk_per_trade=200):
        """
        Backtest Engine - AI stratejisini geçmiş verilerle test eder
        
        Args:
            symbol: Trading pair (örn: BTCUSDT)
            initial_capital: Başlangıç sermayesi ($)
            risk_per_trade: Trade başına risk ($)
        """
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.current_capital = initial_capital
        self.trades = []
        self.equity_curve = []
        
    def fetch_historical_data(self, interval='1h', lookback_days=30):
        """
        Binance'den historical OHLCV data çek
        
        Args:
            interval: Candle interval (1m, 5m, 15m, 1h, 4h, 1d)
            lookback_days: Kaç gün geriye git
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Binance API endpoint
            url = "https://fapi.binance.com/fapi/v1/klines"
            
            # Tarih hesapla
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = int((datetime.now() - timedelta(days=lookback_days)).timestamp() * 1000)
            
            # Request parameters
            params = {
                'symbol': self.symbol,
                'interval': interval,
                'startTime': start_time,
                'endTime': end_time,
                'limit': 1500  # Max 1500 candles per request
            }
            
            print(f"📊 Fetching {lookback_days} days of {interval} data for {self.symbol}...")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # DataFrame oluştur
                df = pd.DataFrame(data, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                    'taker_buy_quote', 'ignore'
                ])
                
                # Data types düzelt
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df['open'] = df['open'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['close'] = df['close'].astype(float)
                df['volume'] = df['volume'].astype(float)
                
                # Sadece gerekli kolonlar
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                
                print(f"✅ {len(df)} candles loaded successfully!")
                return df
            else:
                print(f"❌ API Error: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Error fetching data: {str(e)}")
            return pd.DataFrame()
    
    def simulate_trade(self, ai_decision, entry_price, current_price, timestamp):
        """
        Tek bir trade'i simüle et
        
        Args:
            ai_decision: AI'dan gelen decision dict
            entry_price: Giriş fiyatı
            current_price: Mevcut fiyat (çıkış simülasyonu için)
            timestamp: Trade zamanı
            
        Returns:
            Trade sonucu dict
        """
        signal = ai_decision.get('decision', 'NEUTRAL')
        
        if signal not in ['LONG', 'SHORT']:
            return None
        
        # Entry ve SL
        stop_loss = ai_decision.get('stop_loss', 0)
        if not stop_loss or stop_loss == 0:
            return None
        
        # Position size
        position_size = ai_decision.get('position_size_usd', self.risk_per_trade * 5)
        
        # Risk amount
        risk_amount = abs(entry_price - stop_loss) / entry_price * position_size
        
        # TP levels (1:1, 1:1.62, 1:2.62 R/R)
        risk_distance = abs(entry_price - stop_loss)
        if signal == 'LONG':
            tp1 = entry_price + (risk_distance * 1.0)
            tp2 = entry_price + (risk_distance * 1.618)
            tp3 = entry_price + (risk_distance * 2.618)
        else:  # SHORT
            tp1 = entry_price - (risk_distance * 1.0)
            tp2 = entry_price - (risk_distance * 1.618)
            tp3 = entry_price - (risk_distance * 2.618)
        
        # Simüle et: Current price ile SL/TP check
        trade_result = {
            'timestamp': timestamp,
            'symbol': self.symbol,
            'signal': signal,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'tp1': tp1,
            'tp2': tp2,
            'tp3': tp3,
            'position_size': position_size,
            'risk_amount': risk_amount,
            'exit_price': 0,
            'pnl': 0,
            'pnl_pct': 0,
            'result': 'PENDING'
        }
        
        # LONG trade check
        if signal == 'LONG':
            if current_price <= stop_loss:
                # SL hit
                trade_result['exit_price'] = stop_loss
                trade_result['pnl'] = -risk_amount
                trade_result['pnl_pct'] = ((stop_loss - entry_price) / entry_price) * 100
                trade_result['result'] = 'LOSS'
            elif current_price >= tp3:
                # TP3 hit (full win)
                pnl = risk_distance * 2.618 / entry_price * position_size
                trade_result['exit_price'] = tp3
                trade_result['pnl'] = pnl
                trade_result['pnl_pct'] = ((tp3 - entry_price) / entry_price) * 100
                trade_result['result'] = 'WIN'
            elif current_price >= tp2:
                # TP2 hit (80% win)
                pnl = risk_distance * 1.618 / entry_price * position_size * 0.8
                trade_result['exit_price'] = tp2
                trade_result['pnl'] = pnl
                trade_result['pnl_pct'] = ((tp2 - entry_price) / entry_price) * 100
                trade_result['result'] = 'WIN'
            elif current_price >= tp1:
                # TP1 hit (50% win)
                pnl = risk_distance * 1.0 / entry_price * position_size * 0.5
                trade_result['exit_price'] = tp1
                trade_result['pnl'] = pnl
                trade_result['pnl_pct'] = ((tp1 - entry_price) / entry_price) * 100
                trade_result['result'] = 'WIN'
            else:
                # Henüz çıkış yok
                return None
        
        # SHORT trade check
        elif signal == 'SHORT':
            if current_price >= stop_loss:
                # SL hit
                trade_result['exit_price'] = stop_loss
                trade_result['pnl'] = -risk_amount
                trade_result['pnl_pct'] = ((entry_price - stop_loss) / entry_price) * 100
                trade_result['result'] = 'LOSS'
            elif current_price <= tp3:
                # TP3 hit (full win)
                pnl = risk_distance * 2.618 / entry_price * position_size
                trade_result['exit_price'] = tp3
                trade_result['pnl'] = pnl
                trade_result['pnl_pct'] = ((entry_price - tp3) / entry_price) * 100
                trade_result['result'] = 'WIN'
            elif current_price <= tp2:
                # TP2 hit (80% win)
                pnl = risk_distance * 1.618 / entry_price * position_size * 0.8
                trade_result['exit_price'] = tp2
                trade_result['pnl'] = pnl
                trade_result['pnl_pct'] = ((entry_price - tp2) / entry_price) * 100
                trade_result['result'] = 'WIN'
            elif current_price <= tp1:
                # TP1 hit (50% win)
                pnl = risk_distance * 1.0 / entry_price * position_size * 0.5
                trade_result['exit_price'] = tp1
                trade_result['pnl'] = pnl
                trade_result['pnl_pct'] = ((entry_price - tp1) / entry_price) * 100
                trade_result['result'] = 'WIN'
            else:
                # Henüz çıkış yok
                return None
        
        return trade_result
    
    def run_backtest(self, ai_brain, interval='1h', lookback_days=30, max_trades=100):
        """
        Backtest'i çalıştır
        
        Args:
            ai_brain: AI Brain modülü
            interval: Timeframe
            lookback_days: Test süresi (gün)
            max_trades: Maksimum trade sayısı
            
        Returns:
            Backtest results dict
        """
        print(f"\n{'='*60}")
        print(f"🔱 DEMIR AI BACKTEST ENGINE")
        print(f"{'='*60}\n")
        print(f"Symbol: {self.symbol}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Risk/Trade: ${self.risk_per_trade:,.2f}")
        print(f"Lookback: {lookback_days} days")
        print(f"Interval: {interval}\n")
        
        # Historical data çek
        df = self.fetch_historical_data(interval, lookback_days)
        
        if df.empty:
            return {'error': 'No data loaded'}
        
        # Reset
        self.trades = []
        self.equity_curve = [self.initial_capital]
        self.current_capital = self.initial_capital
        
        print(f"\n🧠 Running AI analysis on {len(df)} candles...\n")
        
        trade_count = 0
        for idx in range(50, len(df) - 10):  # 50 candle warm-up, 10 candle lookahead
            if trade_count >= max_trades:
                break
            
            # AI decision
            try:
                current_price = df.iloc[idx]['close']
                decision = ai_brain.make_trading_decision(
                    self.symbol, 
                    interval, 
                    self.current_capital, 
                    self.risk_per_trade
                )
                
                # Trade simüle et
                if decision.get('decision') in ['LONG', 'SHORT']:
                    # Lookahead: sonraki 10 candle'da çıkış var mı?
                    future_candles = df.iloc[idx+1:idx+11]
                    max_price = future_candles['high'].max()
                    min_price = future_candles['low'].min()
                    
                    # LONG için max, SHORT için min kullan
                    exit_price = max_price if decision['decision'] == 'LONG' else min_price
                    
                    trade_result = self.simulate_trade(
                        decision,
                        current_price,
                        exit_price,
                        df.iloc[idx]['timestamp']
                    )
                    
                    if trade_result and trade_result['result'] != 'PENDING':
                        self.trades.append(trade_result)
                        self.current_capital += trade_result['pnl']
                        self.equity_curve.append(self.current_capital)
                        trade_count += 1
                        
                        result_emoji = '✅' if trade_result['result'] == 'WIN' else '❌'
                        print(f"{result_emoji} Trade #{trade_count}: {trade_result['signal']} @ ${trade_result['entry_price']:.2f} → ${trade_result['exit_price']:.2f} | PNL: ${trade_result['pnl']:+.2f}")
                
                # Rate limit
                time.sleep(0.1)
                
            except Exception as e:
                print(f"⚠️ Error at candle {idx}: {str(e)}")
                continue
        
        # Performance metrics hesapla
        return self.calculate_metrics()
    
    def calculate_metrics(self):
        """
        Backtest performance metrics hesapla
        
        Returns:
            Metrics dict
        """
        if not self.trades:
            return {'error': 'No trades executed'}
        
        df_trades = pd.DataFrame(self.trades)
        
        # Basic metrics
        total_trades = len(df_trades)
        winning_trades = len(df_trades[df_trades['result'] == 'WIN'])
        losing_trades = len(df_trades[df_trades['result'] == 'LOSS'])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # PNL
        total_pnl = df_trades['pnl'].sum()
        total_pnl_pct = ((self.current_capital - self.initial_capital) / self.initial_capital) * 100
        
        # Win/Loss stats
        avg_win = df_trades[df_trades['result'] == 'WIN']['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = abs(df_trades[df_trades['result'] == 'LOSS']['pnl'].mean()) if losing_trades > 0 else 0
        
        # Profit Factor
        gross_profit = df_trades[df_trades['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(df_trades[df_trades['pnl'] < 0]['pnl'].sum())
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0
        
        # Sharpe Ratio (simplified)
        returns = df_trades['pnl_pct'].values
        sharpe_ratio = (returns.mean() / returns.std()) if returns.std() > 0 else 0
        
        # Max Drawdown
        equity_array = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max * 100
        max_drawdown = drawdown.min()
        
        metrics = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'initial_capital': self.initial_capital,
            'final_capital': self.current_capital,
            'equity_curve': self.equity_curve,
            'trades_df': df_trades
        }
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"📊 BACKTEST RESULTS")
        print(f"{'='*60}\n")
        print(f"Total Trades: {total_trades}")
        print(f"Win Rate: {win_rate:.1f}% ({winning_trades}W / {losing_trades}L)")
        print(f"Total PNL: ${total_pnl:+,.2f} ({total_pnl_pct:+.2f}%)")
        print(f"Avg Win: ${avg_win:.2f} | Avg Loss: ${avg_loss:.2f}")
        print(f"Profit Factor: {profit_factor:.2f}")
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"Max Drawdown: {max_drawdown:.2f}%")
        print(f"Final Capital: ${self.current_capital:,.2f}")
        print(f"\n{'='*60}\n")
        
        return metrics


# TEST EXAMPLE
if __name__ == "__main__":
    print("🔱 DEMIR AI BACKTEST ENGINE - Test Mode")
    print("Bu modül streamlit_app.py tarafından kullanılacak")
    print("Standalone test için ai_brain.py import edin\n")
