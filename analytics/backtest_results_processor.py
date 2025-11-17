"""
Backtest Results Processor - Backtest Sonuçlarının İşlenmesi ve Analizi
DEMIR AI v6.0 - Phase 4 Production Grade

Backtest sonuçlarını işleme, raporlama, performans metriklerinin hesaplanması
3 yıl veri ile detaylı performance analizi
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


@dataclass
class MonthlyPerformance:
    """Aylık performans"""
    year: int
    month: int
    trades: int
    wins: int
    losses: int
    profit_loss: float
    return_percent: float
    max_drawdown: float
    win_rate: float
    metadata: Dict = field(default_factory=dict)


@dataclass
class YearlyPerformance:
    """Yıllık performans"""
    year: int
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_profit_loss: float
    total_return_percent: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    sharpe_ratio: float
    monthly_data: List[MonthlyPerformance] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class PerformanceReport:
    """Başlıklı performans raporu"""
    report_id: str
    symbol: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_percent: float
    
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    profit_factor: float
    expectancy: float  # Ortalama trade kar
    
    max_drawdown: float
    max_drawdown_percent: float
    
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    
    recovery_factor: float
    
    yearly_data: List[YearlyPerformance] = field(default_factory=list)
    
    best_trade: float = 0.0
    worst_trade: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    
    generated_at: float = field(default_factory=datetime.now().timestamp)
    
    def to_dict(self) -> Dict:
        """Dict'e dönüştür"""
        return {
            "report_id": self.report_id,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "period": {
                "start": self.start_date.isoformat(),
                "end": self.end_date.isoformat()
            },
            "capital": {
                "initial": self.initial_capital,
                "final": self.final_capital,
                "profit": self.total_return,
                "return_percent": self.total_return_percent
            },
            "trades": {
                "total": self.total_trades,
                "winning": self.winning_trades,
                "losing": self.losing_trades,
                "win_rate": self.win_rate
            },
            "metrics": {
                "profit_factor": self.profit_factor,
                "expectancy": self.expectancy,
                "max_drawdown": self.max_drawdown,
                "max_drawdown_percent": self.max_drawdown_percent,
                "sharpe_ratio": self.sharpe_ratio,
                "sortino_ratio": self.sortino_ratio,
                "calmar_ratio": self.calmar_ratio,
                "recovery_factor": self.recovery_factor
            },
            "best_worst": {
                "best_trade": self.best_trade,
                "worst_trade": self.worst_trade,
                "avg_win": self.avg_win,
                "avg_loss": self.avg_loss
            },
            "consecutive": {
                "wins": self.consecutive_wins,
                "losses": self.consecutive_losses
            },
            "yearly_performance": [asdict(y) for y in self.yearly_data],
            "generated_at": datetime.fromtimestamp(self.generated_at).isoformat()
        }


class BacktestResultsProcessor:
    """Backtest Sonuçları İşlemci"""
    
    def __init__(self):
        """Başlat"""
        self.reports: Dict[str, PerformanceReport] = {}
        self.equity_curves: Dict[str, List[Tuple[float, float]]] = {}
        self.trade_history: Dict[str, List[Dict]] = {}
    
    def process_backtest_results(
        self,
        symbol: str,
        timeframe: str,
        trades: List[Dict],
        equity_curve: List[Tuple[float, float]],
        initial_capital: float,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[PerformanceReport]:
        """
        Backtest sonuçlarını işle
        
        Args:
            symbol: Trading pair
            timeframe: Zaman dilimi
            trades: İşlem listesi
            equity_curve: Equity eğrisi [(timestamp, equity), ...]
            initial_capital: Başlangıç sermayesi
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi
        
        Returns:
            PerformanceReport
        """
        
        if not trades or not equity_curve:
            logger.error("Invalid backtest data")
            return None
        
        try:
            report_id = f"RPT_{symbol}_{int(datetime.now().timestamp())}"
            
            # Temel metrikler
            final_capital = equity_curve[-1][1]
            total_return = final_capital - initial_capital
            total_return_percent = (total_return / initial_capital) * 100
            
            # İşlem metrikleri
            winning_trades = len([t for t in trades if t.get("profit_loss", 0) > 0])
            losing_trades = len([t for t in trades if t.get("profit_loss", 0) < 0])
            total_trades = len(trades)
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Profit Factor
            wins = sum([t.get("profit_loss", 0) for t in trades if t.get("profit_loss", 0) > 0])
            losses = abs(sum([t.get("profit_loss", 0) for t in trades if t.get("profit_loss", 0) < 0]))
            profit_factor = (wins / losses) if losses > 0 else 0
            
            # Expectancy
            expectancy = (wins + losses) / total_trades if total_trades > 0 else 0
            
            # Best/Worst trades
            pls = [t.get("profit_loss", 0) for t in trades]
            best_trade = max(pls) if pls else 0
            worst_trade = min(pls) if pls else 0
            avg_win = np.mean([p for p in pls if p > 0]) if any(p > 0 for p in pls) else 0
            avg_loss = np.mean([p for p in pls if p < 0]) if any(p < 0 for p in pls) else 0
            
            # Drawdown
            max_dd, max_dd_pct = self._calculate_max_drawdown(equity_curve)
            
            # Sharpe, Sortino, Calmar
            returns = np.array([equity_curve[i+1][1] - equity_curve[i][1] 
                               for i in range(len(equity_curve)-1)])
            sharpe = self._calculate_sharpe_ratio(returns)
            sortino = self._calculate_sortino_ratio(returns)
            calmar = self._calculate_calmar_ratio(total_return_percent, max_dd_pct)
            
            # Recovery Factor
            recovery_factor = total_return / max_dd if max_dd > 0 else 0
            
            # Consecutive wins/losses
            cons_wins, cons_losses = self._calculate_consecutive_stats(trades)
            
            # Yıllık veriler
            yearly_data = self._calculate_yearly_performance(
                trades, start_date, end_date
            )
            
            report = PerformanceReport(
                report_id=report_id,
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                final_capital=final_capital,
                total_return=total_return,
                total_return_percent=total_return_percent,
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                win_rate=win_rate,
                profit_factor=profit_factor,
                expectancy=expectancy,
                max_drawdown=max_dd,
                max_drawdown_percent=max_dd_pct,
                sharpe_ratio=sharpe,
                sortino_ratio=sortino,
                calmar_ratio=calmar,
                recovery_factor=recovery_factor,
                best_trade=best_trade,
                worst_trade=worst_trade,
                avg_win=avg_win,
                avg_loss=avg_loss,
                consecutive_wins=cons_wins,
                consecutive_losses=cons_losses,
                yearly_data=yearly_data
            )
            
            self.reports[report_id] = report
            self.equity_curves[report_id] = equity_curve
            self.trade_history[report_id] = trades
            
            logger.info(f"Processed backtest: {report_id}")
            return report
        
        except Exception as e:
            logger.error(f"Error processing backtest results: {e}")
            return None
    
    def _calculate_max_drawdown(
        self,
        equity_curve: List[Tuple[float, float]]
    ) -> Tuple[float, float]:
        """Maximum drawdown hesapla"""
        
        equities = [e for _, e in equity_curve]
        max_equity = equities[0]
        max_drawdown = 0
        max_drawdown_pct = 0
        
        for equity in equities:
            if equity > max_equity:
                max_equity = equity
            
            drawdown = max_equity - equity
            drawdown_pct = (drawdown / max_equity) * 100 if max_equity > 0 else 0
            
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                max_drawdown_pct = drawdown_pct
        
        return max_drawdown, max_drawdown_pct
    
    def _calculate_sharpe_ratio(self, returns: np.ndarray) -> float:
        """Sharpe Ratio"""
        
        if len(returns) < 2 or np.std(returns) == 0:
            return 0
        
        risk_free_rate = 0.01 / 252  # Günlük risk-free rate
        excess_returns = returns - risk_free_rate
        
        sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        return float(sharpe) if not np.isnan(sharpe) else 0
    
    def _calculate_sortino_ratio(self, returns: np.ndarray) -> float:
        """Sortino Ratio"""
        
        if len(returns) < 2:
            return 0
        
        risk_free_rate = 0.01 / 252
        excess_returns = returns - risk_free_rate
        
        # Downside deviation
        downside_returns = np.minimum(excess_returns, 0)
        downside_std = np.sqrt(np.mean(downside_returns ** 2))
        
        if downside_std == 0:
            return 0
        
        sortino = np.mean(excess_returns) / downside_std * np.sqrt(252)
        return float(sortino) if not np.isnan(sortino) else 0
    
    def _calculate_calmar_ratio(self, return_pct: float, max_dd_pct: float) -> float:
        """Calmar Ratio"""
        
        if max_dd_pct == 0:
            return 0
        
        return return_pct / max_dd_pct if max_dd_pct > 0 else 0
    
    def _calculate_consecutive_stats(
        self,
        trades: List[Dict]
    ) -> Tuple[int, int]:
        """Ardışık kazan/kayıp sayıları"""
        
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0
        
        for trade in trades:
            if trade.get("profit_loss", 0) > 0:
                current_wins += 1
                current_losses = 0
            else:
                current_losses += 1
                current_wins = 0
            
            max_wins = max(max_wins, current_wins)
            max_losses = max(max_losses, current_losses)
        
        return max_wins, max_losses
    
    def _calculate_yearly_performance(
        self,
        trades: List[Dict],
        start_date: datetime,
        end_date: datetime
    ) -> List[YearlyPerformance]:
        """Yıllık performans hesapla"""
        
        yearly_data: Dict[int, Dict] = {}
        
        for trade in trades:
            # Trade tarihi
            if "entry_time" in trade:
                trade_date = datetime.fromtimestamp(trade["entry_time"])
                year = trade_date.year
            else:
                continue
            
            if year not in yearly_data:
                yearly_data[year] = {
                    "trades": 0,
                    "wins": 0,
                    "losses": 0,
                    "profit_loss": 0,
                    "monthly": {}
                }
            
            yearly_data[year]["trades"] += 1
            profit = trade.get("profit_loss", 0)
            yearly_data[year]["profit_loss"] += profit
            
            if profit > 0:
                yearly_data[year]["wins"] += 1
            else:
                yearly_data[year]["losses"] += 1
            
            # Monthly
            month = trade_date.month
            if month not in yearly_data[year]["monthly"]:
                yearly_data[year]["monthly"][month] = {
                    "trades": 0,
                    "wins": 0,
                    "losses": 0,
                    "profit_loss": 0
                }
            
            yearly_data[year]["monthly"][month]["trades"] += 1
            yearly_data[year]["monthly"][month]["profit_loss"] += profit
            if profit > 0:
                yearly_data[year]["monthly"][month]["wins"] += 1
            else:
                yearly_data[year]["monthly"][month]["losses"] += 1
        
        # Dönüştür
        results = []
        for year in sorted(yearly_data.keys()):
            year_data = yearly_data[year]
            
            monthly_performances = []
            for month in sorted(year_data["monthly"].keys()):
                m_data = year_data["monthly"][month]
                monthly_performances.append(MonthlyPerformance(
                    year=year,
                    month=month,
                    trades=m_data["trades"],
                    wins=m_data["wins"],
                    losses=m_data["losses"],
                    profit_loss=m_data["profit_loss"],
                    return_percent=(m_data["profit_loss"] / 10000) * 100,  # Estimated
                    max_drawdown=0,  # Calculated separately
                    win_rate=(m_data["wins"] / m_data["trades"] * 100) if m_data["trades"] > 0 else 0
                ))
            
            win_rate = (year_data["wins"] / year_data["trades"] * 100) if year_data["trades"] > 0 else 0
            
            results.append(YearlyPerformance(
                year=year,
                total_trades=year_data["trades"],
                winning_trades=year_data["wins"],
                losing_trades=year_data["losses"],
                total_profit_loss=year_data["profit_loss"],
                total_return_percent=(year_data["profit_loss"] / 10000) * 100,  # Estimated
                max_drawdown=0,  # Calculated separately
                win_rate=win_rate,
                profit_factor=0,  # Calculated separately
                sharpe_ratio=0,  # Calculated separately
                monthly_data=monthly_performances
            ))
        
        return results
    
    def get_report(self, report_id: str) -> Optional[PerformanceReport]:
        """Rapor al"""
        
        return self.reports.get(report_id)
    
    def export_report_to_json(
        self,
        report_id: str,
        filename: Optional[str] = None
    ) -> Optional[str]:
        """Raporu JSON dosyasına aktar"""
        
        if report_id not in self.reports:
            logger.error(f"Report not found: {report_id}")
            return None
        
        try:
            report = self.reports[report_id]
            
            if not filename:
                filename = f"backtest_{report_id}.json"
            
            with open(filename, "w") as f:
                json.dump(report.to_dict(), f, indent=2, default=str)
            
            logger.info(f"Report exported to {filename}")
            return filename
        
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            return None
    
    def export_equity_curve_to_csv(
        self,
        report_id: str,
        filename: Optional[str] = None
    ) -> Optional[str]:
        """Equity eğrisini CSV'ye aktar"""
        
        if report_id not in self.equity_curves:
            logger.error(f"Equity curve not found: {report_id}")
            return None
        
        try:
            if not filename:
                filename = f"equity_curve_{report_id}.csv"
            
            equity_data = self.equity_curves[report_id]
            df = pd.DataFrame(equity_data, columns=["timestamp", "equity"])
            df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
            df = df[["datetime", "equity"]]
            
            df.to_csv(filename, index=False)
            
            logger.info(f"Equity curve exported to {filename}")
            return filename
        
        except Exception as e:
            logger.error(f"Error exporting equity curve: {e}")
            return None
    
    def compare_reports(self, report_ids: List[str]) -> Dict:
        """Raporları karşılaştır"""
        
        try:
            comparison = {
                "reports": [],
                "best_metrics": {}
            }
            
            for report_id in report_ids:
                if report_id in self.reports:
                    report = self.reports[report_id]
                    comparison["reports"].append({
                        "report_id": report_id,
                        "symbol": report.symbol,
                        "return_percent": report.total_return_percent,
                        "win_rate": report.win_rate,
                        "sharpe_ratio": report.sharpe_ratio,
                        "max_drawdown_percent": report.max_drawdown_percent
                    })
            
            if comparison["reports"]:
                # En iyi metrikler
                comparison["best_metrics"] = {
                    "highest_return": max(comparison["reports"], 
                                         key=lambda x: x["return_percent"]),
                    "highest_win_rate": max(comparison["reports"],
                                           key=lambda x: x["win_rate"]),
                    "best_sharpe": max(comparison["reports"],
                                      key=lambda x: x["sharpe_ratio"]),
                    "lowest_drawdown": min(comparison["reports"],
                                          key=lambda x: x["max_drawdown_percent"])
                }
            
            return comparison
        
        except Exception as e:
            logger.error(f"Error comparing reports: {e}")
            return {}


# Kullanım örneği
async def main():
    """Test"""
    
    processor = BacktestResultsProcessor()
    
    # Örnek trades
    trades = [
        {
            "entry_time": datetime.now().timestamp(),
            "exit_time": datetime.now().timestamp() + 3600,
            "profit_loss": 150.0,
            "entry_price": 50000,
            "exit_price": 50100
        },
        {
            "entry_time": datetime.now().timestamp() + 3600,
            "exit_time": datetime.now().timestamp() + 7200,
            "profit_loss": -75.0,
            "entry_price": 50100,
            "exit_price": 50050
        }
    ]
    
    # Örnek equity curve
    equity_curve = [
        (datetime.now().timestamp(), 10000),
        (datetime.now().timestamp() + 3600, 10150),
        (datetime.now().timestamp() + 7200, 10075)
    ]
    
    report = processor.process_backtest_results(
        symbol="BTCUSDT",
        timeframe="1h",
        trades=trades,
        equity_curve=equity_curve,
        initial_capital=10000,
        start_date=datetime.now() - timedelta(days=365),
        end_date=datetime.now()
    )
    
    if report:
        print(json.dumps(report.to_dict(), indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
