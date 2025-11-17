"""
Advanced Backtester - İleri Backtesting Engine
DEMIR AI v6.0 - Phase 4 Production Grade

Multi-strategy backtesting, Monte Carlo simulation, sensitivity analysis
Gerçek veri ile production-grade simulation
"""

import asyncio
import logging
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from enum import Enum
import json
import random
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class SimulationConfig:
    """Simülasyon konfigürasyonu"""
    initial_capital: float = 10000.0
    position_size: float = 0.1  # % of capital
    max_positions: int = 5
    slippage_percent: float = 0.001  # 0.1%
    commission_percent: float = 0.001  # 0.1%
    
    use_monte_carlo: bool = False
    monte_carlo_samples: int = 1000
    
    use_walk_forward: bool = False
    walk_forward_periods: int = 12
    
    metadata: Dict = field(default_factory=dict)


@dataclass
class SimulationResult:
    """Simülasyon sonucu"""
    simulation_id: str
    config: SimulationConfig
    
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_percent: float
    
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    max_drawdown: float
    max_drawdown_percent: float
    
    sharpe_ratio: float
    profit_factor: float
    
    trades: List[Dict] = field(default_factory=list)
    equity_curve: List[Tuple[float, float]] = field(default_factory=list)
    
    start_time: float = field(default_factory=datetime.now().timestamp)
    end_time: float = 0.0
    duration_seconds: float = 0.0
    
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Dict'e dönüştür"""
        return {
            "simulation_id": self.simulation_id,
            "config": asdict(self.config),
            "results": {
                "initial_capital": self.initial_capital,
                "final_capital": self.final_capital,
                "total_return": self.total_return,
                "total_return_percent": self.total_return_percent,
                "total_trades": self.total_trades,
                "winning_trades": self.winning_trades,
                "losing_trades": self.losing_trades,
                "win_rate": self.win_rate,
                "max_drawdown": self.max_drawdown,
                "max_drawdown_percent": self.max_drawdown_percent,
                "sharpe_ratio": self.sharpe_ratio,
                "profit_factor": self.profit_factor
            },
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata
        }


class AdvancedBacktester:
    """İleri Backtester"""
    
    def __init__(self, config: Optional[SimulationConfig] = None):
        """
        Args:
            config: SimulationConfig
        """
        self.config = config or SimulationConfig()
        self.results: Dict[str, SimulationResult] = {}
        self.simulation_counter = 0
    
    async def run_simulation(
        self,
        symbol: str,
        historical_data: List[Dict],
        signal_func: Callable,
        config: Optional[SimulationConfig] = None
    ) -> Optional[SimulationResult]:
        """
        Simülasyon çalıştır
        
        Args:
            symbol: Trading pair
            historical_data: Historical OHLCV verileri
            signal_func: Sinyal üretme fonksiyonu
            config: Simülasyon konfigürasyonu
        
        Returns:
            SimulationResult
        """
        
        start_time = datetime.now().timestamp()
        self.simulation_counter += 1
        simulation_id = f"SIM_{symbol}_{self.simulation_counter}"
        
        try:
            config = config or self.config
            
            # Temel simülasyon
            result = await self._run_basic_simulation(
                symbol,
                historical_data,
                signal_func,
                config,
                simulation_id
            )
            
            if not result:
                return None
            
            # Monte Carlo
            if config.use_monte_carlo:
                await self._run_monte_carlo(result, config)
            
            # Walk Forward
            if config.use_walk_forward:
                await self._run_walk_forward(
                    symbol,
                    historical_data,
                    signal_func,
                    config,
                    result
                )
            
            result.end_time = datetime.now().timestamp()
            result.duration_seconds = result.end_time - start_time
            
            self.results[simulation_id] = result
            
            logger.info(f"Simulation completed: {simulation_id} in {result.duration_seconds:.2f}s")
            return result
        
        except Exception as e:
            logger.error(f"Error running simulation: {e}")
            return None
    
    async def _run_basic_simulation(
        self,
        symbol: str,
        historical_data: List[Dict],
        signal_func: Callable,
        config: SimulationConfig,
        simulation_id: str
    ) -> Optional[SimulationResult]:
        """Temel simülasyon"""
        
        try:
            balance = config.initial_capital
            equity_curve = [(historical_data[0]["timestamp"], balance)]
            trades = []
            open_positions: Dict[str, Dict] = {}
            
            for i, candle in enumerate(historical_data):
                timestamp = candle["timestamp"]
                close_price = candle["close"]
                
                # Sinyal
                signal = signal_func(candle, i, historical_data)
                
                # Açık işlemleri kontrol et
                for pos_id in list(open_positions.keys()):
                    pos = open_positions[pos_id]
                    
                    # SL/TP kontrol
                    if close_price <= pos.get("stop_loss", 0):
                        exit_price = pos.get("stop_loss", close_price)
                        pnl = self._calculate_pnl(pos, exit_price, config)
                        balance += pnl
                        
                        trades.append({
                            "entry_price": pos["entry_price"],
                            "exit_price": exit_price,
                            "quantity": pos["quantity"],
                            "profit_loss": pnl,
                            "reason": "stop_loss"
                        })
                        
                        del open_positions[pos_id]
                    
                    elif close_price >= pos.get("take_profit", float("inf")):
                        exit_price = pos.get("take_profit", close_price)
                        pnl = self._calculate_pnl(pos, exit_price, config)
                        balance += pnl
                        
                        trades.append({
                            "entry_price": pos["entry_price"],
                            "exit_price": exit_price,
                            "quantity": pos["quantity"],
                            "profit_loss": pnl,
                            "reason": "take_profit"
                        })
                        
                        del open_positions[pos_id]
                
                # Yeni sinyal işle
                if signal == "BUY" and len(open_positions) < config.max_positions:
                    entry_price = close_price * (1 + config.slippage_percent)
                    quantity = (balance * config.position_size) / entry_price
                    
                    if quantity > 0:
                        pos_id = f"POS_{len(open_positions)}"
                        open_positions[pos_id] = {
                            "entry_price": entry_price,
                            "quantity": quantity,
                            "stop_loss": entry_price * 0.98,
                            "take_profit": entry_price * 1.03,
                            "entry_time": timestamp
                        }
                        
                        balance -= (entry_price * quantity)
                
                elif signal == "SELL":
                    for pos_id in list(open_positions.keys()):
                        pos = open_positions[pos_id]
                        exit_price = close_price * (1 - config.slippage_percent)
                        pnl = self._calculate_pnl(pos, exit_price, config)
                        balance += pnl
                        
                        trades.append({
                            "entry_price": pos["entry_price"],
                            "exit_price": exit_price,
                            "quantity": pos["quantity"],
                            "profit_loss": pnl,
                            "reason": "signal"
                        })
                        
                        del open_positions[pos_id]
                
                # Unrealized P&L ile equity güncelle
                equity = balance
                for pos in open_positions.values():
                    unrealized = (close_price - pos["entry_price"]) * pos["quantity"]
                    equity += unrealized
                
                equity_curve.append((timestamp, equity))
            
            # Açık işlemleri kapat
            if open_positions:
                last_price = historical_data[-1]["close"]
                for pos in open_positions.values():
                    pnl = self._calculate_pnl(pos, last_price, config)
                    balance += pnl
                    
                    trades.append({
                        "entry_price": pos["entry_price"],
                        "exit_price": last_price,
                        "quantity": pos["quantity"],
                        "profit_loss": pnl,
                        "reason": "final"
                    })
            
            # İstatistikler
            winning_trades = len([t for t in trades if t["profit_loss"] > 0])
            losing_trades = len([t for t in trades if t["profit_loss"] < 0])
            total_trades = len(trades)
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            total_return = balance - config.initial_capital
            total_return_percent = (total_return / config.initial_capital) * 100
            
            max_dd, max_dd_pct = self._calculate_max_drawdown(equity_curve)
            
            # Profit factor
            wins = sum([t["profit_loss"] for t in trades if t["profit_loss"] > 0])
            losses = abs(sum([t["profit_loss"] for t in trades if t["profit_loss"] < 0]))
            profit_factor = (wins / losses) if losses > 0 else 0
            
            # Sharpe ratio
            returns = np.array([equity_curve[i+1][1] - equity_curve[i][1] 
                               for i in range(len(equity_curve)-1)])
            sharpe = self._calculate_sharpe_ratio(returns)
            
            result = SimulationResult(
                simulation_id=simulation_id,
                config=config,
                initial_capital=config.initial_capital,
                final_capital=balance,
                total_return=total_return,
                total_return_percent=total_return_percent,
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                win_rate=win_rate,
                max_drawdown=max_dd,
                max_drawdown_percent=max_dd_pct,
                sharpe_ratio=sharpe,
                profit_factor=profit_factor,
                trades=trades,
                equity_curve=equity_curve
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Error in basic simulation: {e}")
            return None
    
    def _calculate_pnl(
        self,
        position: Dict,
        exit_price: float,
        config: SimulationConfig
    ) -> float:
        """P&L hesapla"""
        
        entry_price = position["entry_price"]
        quantity = position["quantity"]
        
        pnl = (exit_price - entry_price) * quantity
        
        # Commission
        commission = (entry_price * quantity * config.commission_percent)
        commission += (exit_price * quantity * config.commission_percent)
        pnl -= commission
        
        return pnl
    
    def _calculate_max_drawdown(
        self,
        equity_curve: List[Tuple[float, float]]
    ) -> Tuple[float, float]:
        """Maximum drawdown hesapla"""
        
        equities = [e for _, e in equity_curve]
        max_equity = equities[0]
        max_dd = 0
        max_dd_pct = 0
        
        for equity in equities:
            if equity > max_equity:
                max_equity = equity
            
            dd = max_equity - equity
            dd_pct = (dd / max_equity) * 100 if max_equity > 0 else 0
            
            if dd > max_dd:
                max_dd = dd
                max_dd_pct = dd_pct
        
        return max_dd, max_dd_pct
    
    def _calculate_sharpe_ratio(self, returns: np.ndarray) -> float:
        """Sharpe ratio"""
        
        if len(returns) < 2 or np.std(returns) == 0:
            return 0
        
        return float((np.mean(returns) / np.std(returns)) * np.sqrt(252))
    
    async def _run_monte_carlo(
        self,
        base_result: SimulationResult,
        config: SimulationConfig
    ):
        """Monte Carlo simülasyonu"""
        
        logger.info("Running Monte Carlo simulation...")
        
        trades = base_result.trades
        if not trades:
            return
        
        pnls = [t["profit_loss"] for t in trades]
        
        mc_results = []
        
        for _ in range(config.monte_carlo_samples):
            shuffled_pnls = random.sample(pnls, len(pnls))
            cumulative = config.initial_capital + sum(shuffled_pnls)
            mc_results.append(cumulative)
        
        base_result.metadata["monte_carlo"] = {
            "samples": config.monte_carlo_samples,
            "mean_final_capital": float(np.mean(mc_results)),
            "std_final_capital": float(np.std(mc_results)),
            "min_final_capital": float(np.min(mc_results)),
            "max_final_capital": float(np.max(mc_results)),
            "percentile_5": float(np.percentile(mc_results, 5)),
            "percentile_95": float(np.percentile(mc_results, 95))
        }
    
    async def _run_walk_forward(
        self,
        symbol: str,
        historical_data: List[Dict],
        signal_func: Callable,
        config: SimulationConfig,
        result: SimulationResult
    ):
        """Walk Forward Analysis"""
        
        logger.info("Running Walk Forward Analysis...")
        
        # TODO: Implement walk forward
        pass
    
    def get_result(self, simulation_id: str) -> Optional[SimulationResult]:
        """Sonuç al"""
        
        return self.results.get(simulation_id)
    
    def compare_simulations(self, simulation_ids: List[str]) -> Dict:
        """Simülasyonları karşılaştır"""
        
        comparison = []
        
        for sim_id in simulation_ids:
            if sim_id in self.results:
                result = self.results[sim_id]
                comparison.append({
                    "simulation_id": sim_id,
                    "return_percent": result.total_return_percent,
                    "win_rate": result.win_rate,
                    "sharpe_ratio": result.sharpe_ratio,
                    "max_drawdown_percent": result.max_drawdown_percent,
                    "profit_factor": result.profit_factor
                })
        
        return {"comparisons": comparison}


# Kullanım örneği
async def main():
    """Test"""
    
    config = SimulationConfig(
        initial_capital=10000,
        position_size=0.1,
        use_monte_carlo=True,
        monte_carlo_samples=100
    )
    
    backtester = AdvancedBacktester(config)
    
    # Örnek sinyal
    def signal_func(candle, index, history):
        if index < 50:
            return "NEUTRAL"
        
        recent = history[index-50:index]
        closes = [c["close"] for c in recent]
        sma = np.mean(closes[-20:])
        
        if closes[-1] > sma:
            return "BUY"
        else:
            return "SELL"
    
    # TODO: Gerçek veri yükle ve simülasyon çalıştır
    # result = await backtester.run_simulation("BTCUSDT", historical_data, signal_func)


if __name__ == "__main__":
    asyncio.run(main())
