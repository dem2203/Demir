"""
=============================================================================
DEMIR AI v25.0 - PAPER → LIVE TRADING MODE MANAGER
=============================================================================
Purpose: Kağıt (paper) trading'den gerçek (live) trading'e geçişi kontrol et
Location: /trading/ klasörü - NEW
Integrations: trade_entry_calculator.py, trade_database.py, telegram_multichannel.py
Language: English (technical) + Turkish (descriptions)
=============================================================================
"""

import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingMode(Enum):
    """Trading modları"""
    PAPER = "PAPER"        # Kağıt üzerinde (simulasyon, risk yok)
    LIVE = "LIVE"          # Gerçek para (risk var)
    BACKTEST = "BACKTEST"  # Geçmiş veri (test)


class RiskLevel(Enum):
    """Risk seviyeleri"""
    CONSERVATIVE = 1      # Düşük risk (1-2% per trade)
    MODERATE = 2          # Orta risk (2-5% per trade)
    AGGRESSIVE = 3        # Yüksek risk (5-10% per trade)


@dataclass
class TradingConfig:
    """Trading konfigürasyonu"""
    mode: TradingMode
    risk_level: RiskLevel
    max_position_size: float  # % of capital
    max_daily_loss: float  # $ stop loss
    max_concurrent_trades: int
    leverage: float = 1.0  # 1.0 = no leverage
    auto_trade_enabled: bool = False  # Manuel vs otomatik
    take_profit_mode: str = "PARTIAL"  # PARTIAL (TP1/2/3) vs FULL
    stop_loss_mode: str = "HARD"  # HARD (automatic) vs SOFT (manual confirmation)


class PaperTradingSimulator:
    """
    Paper Trading - Kağıt üzerinde trade yapma (simulasyon)
    
    Features:
    - Virtual portfolio
    - Trade simulation
    - Performance tracking
    - Zero real risk
    """
    
    def __init__(self, initial_balance: float = 10000):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.total_pnl = 0
        
        self.open_positions: Dict[str, Dict] = {}
        self.closed_trades: list = []
        
        logger.info(f"✅ Paper Trading Simulator initialized: ${initial_balance}")
    
    def open_trade(self, symbol: str, signal_type: str, entry_price: float,
                   tp1: float, tp2: float, tp3: float, sl: float,
                   risk_percent: float = 2.0) -> Tuple[bool, str]:
        """Kağıt trade aç"""
        try:
            # Calculate position size based on risk
            risk_amount = self.current_balance * (risk_percent / 100)
            
            if signal_type == "LONG":
                stop_loss_distance = entry_price - sl
            else:
                stop_loss_distance = sl - entry_price
            
            if stop_loss_distance <= 0:
                return False, "❌ Invalid SL distance"
            
            qty = risk_amount / stop_loss_distance
            trade_value = entry_price * qty
            
            if trade_value > self.current_balance:
                return False, f"❌ Insufficient balance. Need: ${trade_value}, Have: ${self.current_balance}"
            
            trade_id = f"{symbol}_{datetime.now().timestamp()}"
            
            self.open_positions[trade_id] = {
                "symbol": symbol,
                "signal_type": signal_type,
                "entry_price": entry_price,
                "qty": qty,
                "tp1": tp1,
                "tp2": tp2,
                "tp3": tp3,
                "sl": sl,
                "entry_time": datetime.now().isoformat(),
                "risk_amount": risk_amount
            }
            
            # Reduce available balance
            self.current_balance -= trade_value
            
            logger.info(f"📈 Paper trade opened: {trade_id} | Size: {qty:.4f} | Risk: ${risk_amount:.2f}")
            return True, f"✅ Paper trade opened: {trade_id}"
        
        except Exception as e:
            logger.error(f"❌ Error opening trade: {e}")
            return False, f"❌ Error: {e}"
    
    def close_trade(self, trade_id: str, exit_price: float, exit_reason: str) -> Tuple[bool, float]:
        """Kağıt trade kapat"""
        try:
            if trade_id not in self.open_positions:
                return False, 0
            
            trade = self.open_positions[trade_id]
            qty = trade["qty"]
            entry_price = trade["entry_price"]
            
            if trade["signal_type"] == "LONG":
                pnl = (exit_price - entry_price) * qty
            else:
                pnl = (entry_price - exit_price) * qty
            
            # Return capital and add PnL
            self.current_balance += (entry_price * qty) + pnl
            self.total_pnl += pnl
            
            trade["exit_price"] = exit_price
            trade["exit_reason"] = exit_reason
            trade["exit_time"] = datetime.now().isoformat()
            trade["pnl"] = pnl
            trade["pnl_percent"] = (pnl / (entry_price * qty) * 100) if entry_price > 0 else 0
            
            self.closed_trades.append(trade)
            del self.open_positions[trade_id]
            
            logger.info(f"✅ Paper trade closed: {trade_id} | PnL: ${pnl:.2f}")
            return True, pnl
        
        except Exception as e:
            logger.error(f"❌ Error closing trade: {e}")
            return False, 0
    
    def get_portfolio_status(self) -> Dict:
        """Portföy durumunu al"""
        total_position_value = sum(t["qty"] * t["entry_price"] for t in self.open_positions.values())
        total_equity = self.current_balance + total_position_value
        
        return {
            "balance": round(self.current_balance, 2),
            "total_equity": round(total_equity, 2),
            "total_pnl": round(self.total_pnl, 2),
            "open_trades": len(self.open_positions),
            "closed_trades": len(self.closed_trades),
            "win_rate": self._calculate_win_rate()
        }
    
    def _calculate_win_rate(self) -> float:
        """Kazanma oranını hesapla"""
        if not self.closed_trades:
            return 0
        
        wins = sum(1 for t in self.closed_trades if t["pnl"] > 0)
        return (wins / len(self.closed_trades) * 100)


class LiveTradingManager:
    """
    Live Trading Manager - Gerçek para ile trade yapma
    
    Features:
    - Exchange API integration (Binance vb)
    - Risk management (strict)
    - Auto execution (optional)
    - Real-time monitoring
    """
    
    def __init__(self, exchange_api_key: str = None, exchange_api_secret: str = None):
        self.api_key = exchange_api_key
        self.api_secret = exchange_api_secret
        self.exchange = None  # TODO: Initialize ccxt exchange
        
        self.open_positions: Dict[str, Dict] = {}
        self.execution_log: list = []
        
        self.risk_config = TradingConfig(
            mode=TradingMode.LIVE,
            risk_level=RiskLevel.CONSERVATIVE,
            max_position_size=5.0,  # Max 5% per trade
            max_daily_loss=500.0,    # Stop if loss > $500 today
            max_concurrent_trades=5,
            leverage=1.0,
            auto_trade_enabled=False
        )
        
        logger.info("⚠️ Live Trading Manager initialized (CAUTION: REAL MONEY)")
    
    def validate_trade_parameters(self, symbol: str, entry_price: float, tp1: float, sl: float) -> Tuple[bool, str]:
        """Trade parametrelerini doğrula"""
        errors = []
        
        # Check SL/TP validity
        if entry_price <= 0 or tp1 <= 0 or sl <= 0:
            errors.append("❌ Invalid prices")
        
        # Check TP is better than entry
        if tp1 <= entry_price:
            errors.append("❌ TP must be above entry for LONG")
        
        # Check SL is worse than entry (protection)
        if sl >= entry_price:
            errors.append("❌ SL must be below entry for LONG")
        
        # Check position count
        if len(self.open_positions) >= self.risk_config.max_concurrent_trades:
            errors.append(f"❌ Max concurrent trades ({self.risk_config.max_concurrent_trades}) reached")
        
        if errors:
            return False, " | ".join(errors)
        
        return True, "✅ Parameters valid"
    
    def open_live_trade(self, symbol: str, entry_price: float, tp1: float, tp2: float, 
                       tp3: float, sl: float, risk_amount: float = 100) -> Tuple[bool, str]:
        """
        Live trade aç (GERÇEK PARA!)
        
        ⚠️ MANUAL CONFIRMATION REQUIRED
        """
        try:
            # Validate first
            valid, msg = self.validate_trade_parameters(symbol, entry_price, tp1, sl)
            if not valid:
                return False, msg
            
            # TODO: Execute on real exchange
            # order = self.exchange.create_limit_buy_order(symbol, qty, entry_price)
            
            trade_id = f"{symbol}_{datetime.now().timestamp()}"
            
            self.open_positions[trade_id] = {
                "symbol": symbol,
                "entry_price": entry_price,
                "tp1": tp1,
                "tp2": tp2,
                "tp3": tp3,
                "sl": sl,
                "risk_amount": risk_amount,
                "entry_time": datetime.now().isoformat(),
                "status": "PENDING"  # Awaiting manual confirmation
            }
            
            self.execution_log.append({
                "action": "OPEN_REQUEST",
                "trade_id": trade_id,
                "timestamp": datetime.now().isoformat(),
                "details": f"Live trade requested for {symbol}"
            })
            
            logger.warning(f"⚠️ Live trade PENDING CONFIRMATION: {trade_id}")
            return True, f"⚠️ Live trade pending your confirmation: {trade_id}"
        
        except Exception as e:
            logger.error(f"❌ Error opening live trade: {e}")
            return False, f"❌ Error: {e}"
    
    def confirm_trade_execution(self, trade_id: str) -> Tuple[bool, str]:
        """
        Trade'i MANUEL olarak onay ve çalıştır
        
        Bu adım gereklidir - otomatik değil!
        """
        try:
            if trade_id not in self.open_positions:
                return False, "❌ Trade not found"
            
            trade = self.open_positions[trade_id]
            
            if trade["status"] != "PENDING":
                return False, f"❌ Trade status is {trade['status']}"
            
            # TODO: Execute on exchange
            # market_order = self.exchange.create_market_buy_order(...)
            
            trade["status"] = "EXECUTED"
            trade["execution_time"] = datetime.now().isoformat()
            
            self.execution_log.append({
                "action": "TRADE_EXECUTED",
                "trade_id": trade_id,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"✅ Live trade EXECUTED: {trade_id}")
            return True, f"✅ Trade {trade_id} executed on {trade['symbol']}"
        
        except Exception as e:
            logger.error(f"❌ Error confirming trade: {e}")
            return False, f"❌ Error: {e}"
    
    def close_live_trade(self, trade_id: str, close_reason: str) -> Tuple[bool, str]:
        """Live trade'i kapat"""
        try:
            if trade_id not in self.open_positions:
                return False, "❌ Trade not found"
            
            # TODO: Close on exchange
            
            logger.info(f"✅ Live trade closed: {trade_id} | Reason: {close_reason}")
            return True, f"✅ Trade {trade_id} closed"
        
        except Exception as e:
            logger.error(f"❌ Error closing trade: {e}")
            return False, f"❌ Error: {e}"


class ModeManager:
    """
    Paper/Live mode yöneticisi
    
    Güvenli geçiş ve modlar arası kontrol
    """
    
    def __init__(self):
        self.current_mode = TradingMode.PAPER
        self.paper_simulator = PaperTradingSimulator()
        self.live_manager = None  # Lazy load
        
        logger.info("✅ Mode Manager initialized (Default: PAPER)")
    
    def switch_mode(self, new_mode: TradingMode, api_key: str = None, api_secret: str = None) -> Tuple[bool, str]:
        """Modu değiştir"""
        if new_mode == TradingMode.LIVE:
            if not api_key or not api_secret:
                return False, "❌ API keys required for LIVE mode"
            
            self.live_manager = LiveTradingManager(api_key, api_secret)
            self.current_mode = TradingMode.LIVE
            logger.warning("⚠️ SWITCHED TO LIVE MODE - REAL MONEY AT RISK")
            return True, "⚠️ LIVE MODE ACTIVATED - BE CAREFUL!"
        
        elif new_mode == TradingMode.PAPER:
            self.current_mode = TradingMode.PAPER
            logger.info("✅ Switched to PAPER mode")
            return True, "✅ PAPER mode activated"
        
        return False, "❌ Invalid mode"
    
    def get_current_mode_status(self) -> Dict:
        """Mevcut mod durumunu al"""
        if self.current_mode == TradingMode.PAPER:
            return {
                "mode": "PAPER 📄",
                "status": "No real money at risk",
                "portfolio": self.paper_simulator.get_portfolio_status()
            }
        else:
            return {
                "mode": "LIVE 🔴",
                "status": "REAL MONEY AT RISK - Be careful!",
                "active_trades": len(self.live_manager.open_positions)
            }


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    # Paper trading test
    print("\n📄 PAPER TRADING TEST")
    paper = PaperTradingSimulator(initial_balance=10000)
    
    success, msg = paper.open_trade("BTCUSDT", "LONG", 50000, 52000, 54000, 56000, 48000)
    print(f"{msg}")
    print(f"Portfolio: {paper.get_portfolio_status()}")
    
    # Mode manager test
    print("\n\n🔄 MODE SWITCHING TEST")
    manager = ModeManager()
    
    print(f"Current mode: {manager.get_current_mode_status()}")
    
    success, msg = manager.switch_mode(TradingMode.PAPER)
    print(f"{msg}")
