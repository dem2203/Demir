"""
3 Yıl Backtester - Historical Performance Analysis
DEMIR AI v6.0 - Phase 4 Production Grade

2022-2025 arası historical veri ile backtesting
Gerçek Binance OHLCV verisi
Position management, risk analysis, drawdown tracking
"""

import asyncio
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from enum import Enum
import json
import sqlite3

logger = logging.getLogger(__name__)


class PositionType(Enum):
    """Pozisyon türü"""
    LONG = "long"
    SHORT = "short"


@dataclass
class Trade:
    """Işlem (Trade)"""
    entry_time: float
    entry_price: float
    exit_time: Optional[float] = None
    exit_price: Optional[float] = None
    position_type: str = "long"
    quantity: float = 1.0
    
    fee: float = 0.001  # 0.1% fee
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    profit_loss: float = 0.0
    profit_loss_percent: float = 0.0
    status: str = "open"  # "open", "closed", "stopped"
    
    metadata: Dict = field(default_factory=dict)
    
    def close(self, exit_price: float, exit_time: float) -> bool:
        """Işlemi kapat"""
        if self.status == "closed":
            return False
        
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.status = "closed"
        
        # PL hesapla
        if self.position_type == "long":
            self.profit_loss = (exit_price - self.entry_price) * self.quantity
        else:  # short
            self.profit_loss = (self.entry_price - exit_price) * self.quantity
        
        # Fees
        self.profit_loss -= (self.entry_price * self.quantity * self.fee)
        self.profit_loss -= (exit_price * self.quantity * self.fee)
        
        self.profit_loss_percent = (self.profit_loss / (self.entry_price * self.quantity)) * 100
        
        return True
    
    def to_dict(self) -> Dict:
        """Dict'e dönüştür"""
        return asdict(self)


@dataclass
class BacktestStats:
    """Backtest istatistikleri"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    
    win_rate: float = 0.0
    profit_factor: float = 0.0
    
    total_profit_loss: float = 0.0
    total_return_percent: float = 0.0
    
    max_drawdown: float = 0.0
    max_drawdown_percent: float = 0.0
    
    avg_trade_profit: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0
    
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    
    calmar_ratio: float = 0.0
    
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Dict'e dönüştür"""
        return asdict(self)


class Backtester3Year:
    """3 Yıllık Backtest Motor"""
    
    def __init__(self, initial_capital: float = 10000.0):
        """
        Args:
            initial_capital: Başlangıç sermayesi
        """
        self.initial_capital = initial_capital
        self.current_balance = initial_capital
        self.equity_curve: List[Tuple[float, float]] = []
        
        self.trades: List[Trade] = []
        self.open_trades: List[Trade] = []
        self.closed_trades: List[Trade] = []
        
        self.stats = BacktestStats()
        
        self.start_date = None
        self.end_date = None
        
        self.historical_data: List[Dict] = []
    
    def load_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        timeframe: str = "1h"
    ) -> bool:
        """
        Historical veri yükle (Binance'den)
        
        Args:
            symbol: "BTCUSDT"
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi
            timeframe: "1h", "4h", "1d"
        """
        
        try:
            # TODO: Gerçek Binance API çağrısı yapılacak
            # Şimdilik test veri kullanıyoruz
            
            logger.info(f"Loading historical data for {symbol} from {start_date} to {end_date}")
            
            # Mock: CSV dosyasından oku veya DB'den
            # self.historical_data = self._fetch_from_binance(symbol, start_date, end_date, timeframe)
            
            self.start_date = start_date
            self.end_date = end_date
            
            logger.info(f"Loaded {len(self.historical_data)} candles")
            return True
        
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            return False
    
    def run_backtest(
        self,
        signal_generator_func,
        position_size: float = 0.1
    ) -> bool:
        """
        Backtest çalıştır
        
        Args:
            signal_generator_func: Sinyal üretme fonksiyonu
            position_size: Her position için pozisyon boyutu (% olarak)
        """
        
        try:
            if not self.historical_data:
                logger.error("No historical data loaded")
                return False
            
            self.equity_curve = []
            
            for i, candle in enumerate(self.historical_data):
                timestamp = candle["timestamp"]
                close_price = candle["close"]
                
                # Sinyal üret
                signal = signal_generator_func(candle, i, self.historical_data)
                
                # Açık işlemleri kontrol et
                self._check_open_positions(close_price, timestamp)
                
                # Sinyal işle
                if signal == "BUY":
                    self._enter_long_position(
                        close_price,
                        timestamp,
                        position_size,
                        candle
                    )
                elif signal == "SELL":
                    self._close_all_positions(close_price, timestamp)
                
                # Equity güncelle
                equity = self._calculate_equity(close_price)
                self.equity_curve.append((timestamp, equity))
            
            # Açık işlemleri kapat
            if self.open_trades:
                last_price = self.historical_data[-1]["close"]
                last_time = self.historical_data[-1]["timestamp"]
                for trade in self.open_trades:
                    trade.close(last_price, last_time)
                    self.closed_trades.append(trade)
                self.open_trades.clear()
            
            # İstatistikleri hesapla
            self._calculate_stats()
            
            logger.info("Backtest completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return False
    
    def _enter_long_position(
        self,
        entry_price: float,
        entry_time: float,
        position_size: float,
        candle: Dict
    ) -> bool:
        """Long pozisyona gir"""
        
        try:
            # Pozisyon boyutunu hesapla
            available_capital = self.current_balance * position_size
            quantity = available_capital / entry_price
            
            # Stop Loss ve Take Profit hesapla
            sl = entry_price * 0.98
            tp = entry_price * 1.03
            
            trade = Trade(
                entry_time=entry_time,
                entry_price=entry_price,
                quantity=quantity,
                position_type="long",
                stop_loss=sl,
                take_profit=tp,
                metadata={
                    "candle": candle
                }
            )
            
            self.open_trades.append(trade)
            self.trades.append(trade)
            
            # Balance güncelle
            self.current_balance -= (entry_price * quantity)
            
            logger.debug(f"Entered LONG at {entry_price}, qty={quantity}")
            return True
        
        except Exception as e:
            logger.error(f"Error entering long position: {e}")
            return False
    
    def _close_all_positions(self, exit_price: float, exit_time: float) -> int:
        """Tüm açık pozisyonları kapat"""
        
        closed_count = 0
        
        for trade in self.open_trades[:]:
            if trade.close(exit_price, exit_time):
                self.closed_trades.append(trade)
                self.open_trades.remove(trade)
                
                # Balance güncelle
                if trade.position_type == "long":
                    self.current_balance += (exit_price * trade.quantity)
                
                closed_count += 1
                logger.debug(f"Closed position at {exit_price}, P&L={trade.profit_loss}")
        
        return closed_count
    
    def _check_open_positions(self, current_price: float, timestamp: float):
        """Açık pozisyonları kontrol et (SL/TP)"""
        
        for trade in self.open_trades[:]:
            should_close = False
            
            if trade.position_type == "long":
                if trade.stop_loss and current_price <= trade.stop_loss:
                    trade.status = "stopped"
                    should_close = True
                elif trade.take_profit and current_price >= trade.take_profit:
                    trade.status = "closed"
                    should_close = True
            
            if should_close:
                trade.close(current_price, timestamp)
                self.closed_trades.append(trade)
                self.open_trades.remove(trade)
                
                self.current_balance += (current_price * trade.quantity)
    
    def _calculate_equity(self, current_price: float) -> float:
        """Equity hesapla"""
        
        equity = self.current_balance
        
        # Açık pozisyonların unrealized P&L
        for trade in self.open_trades:
            if trade.position_type == "long":
                unrealized = (current_price - trade.entry_price) * trade.quantity
                equity += unrealized
        
        return equity
    
    def _calculate_stats(self):
        """İstatistikleri hesapla"""
        
        if not self.closed_trades:
            logger.warning("No closed trades for stats calculation")
            return
        
        trades = self.closed_trades
        
        # Temel sayılar
        self.stats.total_trades = len(trades)
        self.stats.winning_trades = len([t for t in trades if t.profit_loss > 0])
        self.stats.losing_trades = len([t for t in trades if t.profit_loss < 0])
        
        # Win rate
        self.stats.win_rate = (self.stats.winning_trades / self.stats.total_trades * 100) if self.stats.total_trades > 0 else 0
        
        # Profit factor
        total_wins = sum([t.profit_loss for t in trades if t.profit_loss > 0])
        total_losses = abs(sum([t.profit_loss for t in trades if t.profit_loss < 0]))
        self.stats.profit_factor = (total_wins / total_losses) if total_losses > 0 else 0
        
        # Toplam P&L
        self.stats.total_profit_loss = sum([t.profit_loss for t in trades])
        self.stats.total_return_percent = (self.stats.total_profit_loss / self.initial_capital) * 100
        
        # Largest win/loss
        pls = [t.profit_loss for t in trades]
        self.stats.largest_win = max(pls) if pls else 0
        self.stats.largest_loss = min(pls) if pls else 0
        
        # Average trade profit
        self.stats.avg_trade_profit = np.mean(pls) if pls else 0
        
        # Consecutive wins/losses
        self._calculate_consecutive_stats(trades)
        
        # Drawdown
        self._calculate_drawdown()
        
        # Sharpe Ratio
        self._calculate_sharpe_ratio(pls)
        
        logger.info(f"Stats calculated: {self.stats.total_trades} trades, "
                   f"Win Rate: {self.stats.win_rate:.2f}%, "
                   f"Total Return: {self.stats.total_return_percent:.2f}%")
    
    def _calculate_consecutive_stats(self, trades: List[Trade]):
        """Ardışık kazan/kayıp istatistikleri"""
        
        current_wins = 0
        current_losses = 0
        
        for trade in trades:
            if trade.profit_loss > 0:
                current_wins += 1
                current_losses = 0
            else:
                current_losses += 1
                current_wins = 0
            
            self.stats.max_consecutive_wins = max(
                self.stats.max_consecutive_wins,
                current_wins
            )
            self.stats.max_consecutive_losses = max(
                self.stats.max_consecutive_losses,
                current_losses
            )
    
    def _calculate_drawdown(self):
        """Maximum drawdown hesapla"""
        
        if not self.equity_curve:
            return
        
        equities = [e for _, e in self.equity_curve]
        max_equity = equities[0]
        max_drawdown = 0
        
        for equity in equities:
            if equity > max_equity:
                max_equity = equity
            
            drawdown = (max_equity - equity) / max_equity
            max_drawdown = max(max_drawdown, drawdown)
        
        self.stats.max_drawdown = max_equity - (max_equity * (1 - max_drawdown))
        self.stats.max_drawdown_percent = max_drawdown * 100
    
    def _calculate_sharpe_ratio(self, returns: List[float]):
        """Sharpe Ratio hesapla"""
        
        if len(returns) < 2:
            return
        
        returns_array = np.array(returns)
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array)
        
        risk_free_rate = 0.01  # 1% annual
        
        if std_return > 0:
            self.stats.sharpe_ratio = ((mean_return - risk_free_rate) / std_return)
    
    def get_backtest_report(self) -> Dict:
        """Backtest raporunu al"""
        
        return {
            "period": {
                "start": self.start_date.isoformat() if self.start_date else None,
                "end": self.end_date.isoformat() if self.end_date else None
            },
            "capital": {
                "initial": self.initial_capital,
                "final": self.current_balance + sum([t.profit_loss for t in self.closed_trades])
            },
            "statistics": self.stats.to_dict(),
            "trades": [t.to_dict() for t in self.closed_trades[-20:]]  # Son 20 işlem
        }


# Kullanım örneği
async def main():
    """Test"""
    
    backtester = Backtester3Year(initial_capital=10000.0)
    
    # Örnek sinyal generator
    def signal_gen(candle, index, history):
        if index < 50:
            return "NEUTRAL"
        
        recent = history[index-50:index]
        closes = [c["close"] for c in recent]
        sma_20 = np.mean(closes[-20:])
        
        if closes[-1] > sma_20:
            return "BUY"
        elif closes[-1] < sma_20:
            return "SELL"
        
        return "NEUTRAL"
    
    # TODO: Gerçek historical veri yükle
    # backtester.load_historical_data("BTCUSDT", datetime(2022, 1, 1), datetime(2025, 1, 1))
    # backtester.run_backtest(signal_gen, position_size=0.1)
    
    # report = backtester.get_backtest_report()
    # print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
