"""
=============================================================================
DEMIR AI - SEMI-AUTONOMOUS TRADE EXECUTOR
=============================================================================
Purpose: Manual confirmation + otomatik trade açma/kapama
Location: /execution/ klasörü
=============================================================================
"""

import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """İşlem modu"""
    MANUAL = "MANUAL"              # Sadece AI önerisi, siz onaylarsınız
    SEMI_AUTONOMOUS = "SEMI"       # AI'nin TP/SL önerileri, siz entry açıyorsunuz
    AUTONOMOUS = "AUTONOMOUS"      # Tam otomatik (riskli!)


@dataclass
class ExecutionSignal:
    """İşlem sinyali"""
    symbol: str
    signal_type: str  # LONG/SHORT
    entry_price: float
    tp1: float
    tp2: float
    tp3: float
    sl: float
    confidence: float
    mode: ExecutionMode
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class SemiAutonomousExecutor:
    """
    Yarı-Otonom İşlem Yöneticisi
    
    Features:
    - Manual approval + auto execution
    - TP/SL trailing
    - Partial exit on TP1/2
    - Risk management
    """
    
    def __init__(self, mode: ExecutionMode = ExecutionMode.SEMI_AUTONOMOUS):
        self.mode = mode
        self.active_orders = {}
        self.execution_history = []
    
    def generate_execution_signal(self, symbol: str, signal_type: str,
                                 entry_price: float, tp1: float, tp2: float,
                                 tp3: float, sl: float, confidence: float) -> ExecutionSignal:
        """İşlem sinyali oluştur"""
        signal = ExecutionSignal(
            symbol=symbol,
            signal_type=signal_type,
            entry_price=entry_price,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl=sl,
            confidence=confidence,
            mode=self.mode
        )
        
        logger.info(f"📤 Execution Signal Generated: {symbol} {signal_type}")
        return signal
    
    def request_manual_approval(self, signal: ExecutionSignal) -> Dict:
        """Manuel onay isteği"""
        approval_request = {
            "id": f"{signal.symbol}_{signal.timestamp}",
            "symbol": signal.symbol,
            "type": signal.signal_type,
            "entry": signal.entry_price,
            "tp_levels": [signal.tp1, signal.tp2, signal.tp3],
            "sl": signal.sl,
            "confidence": signal.confidence,
            "status": "PENDING_APPROVAL"
        }
        
        logger.warning(f"⏳ Awaiting manual approval for {signal.symbol}")
        return approval_request
    
    def execute_trade_approved(self, signal: ExecutionSignal, approved: bool) -> Tuple[bool, str]:
        """Onaylı trade'i çalıştır"""
        if not approved:
            logger.info(f"❌ Trade rejected by user: {signal.symbol}")
            return False, "Trade rejected"
        
        try:
            order_id = f"{signal.symbol}_{datetime.now().timestamp()}"
            
            self.active_orders[order_id] = {
                "symbol": signal.symbol,
                "type": signal.signal_type,
                "entry": signal.entry_price,
                "tp1": signal.tp1,
                "tp2": signal.tp2,
                "tp3": signal.tp3,
                "sl": signal.sl,
                "status": "OPENED",
                "opened_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Trade executed: {order_id}")
            return True, f"Trade opened: {order_id}"
        
        except Exception as e:
            logger.error(f"❌ Execution error: {e}")
            return False, str(e)
    
    def auto_close_on_tp(self, order_id: str, tp_level: int, current_price: float) -> bool:
        """TP'ye otomatik olarak kapat"""
        if order_id not in self.active_orders:
            return False
        
        order = self.active_orders[order_id]
        
        if tp_level == 1 and current_price >= order['tp1']:
            exit_percent = 50
        elif tp_level == 2 and current_price >= order['tp2']:
            exit_percent = 30
        elif tp_level == 3 and current_price >= order['tp3']:
            exit_percent = 20
        else:
            return False
        
        logger.info(f"✅ TP{tp_level} hit - Closing {exit_percent}% position")
        return True
    
    def auto_close_on_sl(self, order_id: str, current_price: float) -> bool:
        """SL'ye otomatik olarak kapat"""
        if order_id not in self.active_orders:
            return False
        
        order = self.active_orders[order_id]
        
        if current_price <= order['sl']:
            logger.error(f"🔴 SL HIT - Closing full position")
            del self.active_orders[order_id]
            return True
        
        return False
    
    def get_execution_stats(self) -> Dict:
        """İşlem istatistikleri"""
        return {
            "mode": self.mode.value,
            "active_orders": len(self.active_orders),
            "total_executed": len(self.execution_history),
            "active_orders_list": self.active_orders
        }


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    executor = SemiAutonomousExecutor(ExecutionMode.SEMI_AUTONOMOUS)
    
    # Generate signal
    signal = executor.generate_execution_signal(
        "BTCUSDT", "LONG", 50000, 51500, 53000, 55000, 48500, 85.0
    )
    
    # Request approval
    approval = executor.request_manual_approval(signal)
    print(f"Approval Request: {approval}")
    
    # Execute approved
    success, msg = executor.execute_trade_approved(signal, approved=True)
    print(f"Execution: {msg}")
    
    # Check stats
    stats = executor.get_execution_stats()
    print(f"Stats: {stats}")
