"""
=============================================================================
DEMIR AI v25.0 - TRADE ENTRY & TP/SL CALCULATOR
=============================================================================
Purpose: Trade entry seviyeleri, TP1/TP2/TP3 ve SL otomatik hesaplama
Location: /utils/ klasörü
Integrations: streamlit_app.py, trade_history_db.py, telegram_alert_system.py
=============================================================================
"""

import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Trade signal types"""
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"


@dataclass
class TradePlan:
    """Tam trade planı - Entry, TP, SL detayları"""
    symbol: str
    signal_type: SignalType
    entry_price: float
    entry_qty: float  # Position size
    
    tp1_price: float
    tp1_qty: float  # % of position to exit at TP1
    
    tp2_price: float
    tp2_qty: float
    
    tp3_price: float
    tp3_qty: float
    
    sl_price: float
    
    timestamp: str = None
    signal_confidence: float = 0.0  # 0-100
    risk_reward_ratio: float = 0.0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        
        # Calculate R:R ratio
        if self.signal_type == SignalType.LONG:
            risk = self.entry_price - self.sl_price
            reward = self.tp3_price - self.entry_price
        else:  # SHORT
            risk = self.sl_price - self.entry_price
            reward = self.entry_price - self.tp3_price
        
        if risk > 0:
            self.risk_reward_ratio = round(reward / risk, 2)


class TradeEntryCalculator:
    """
    Trade Entry & TP/SL Calculation Engine
    
    Features:
    - Dinamik TP1/TP2/TP3 seviyeleri hesaplama
    - SL otomatik hesaplama (ATR, % bazlı)
    - Multiple TP stratejileri
    - Risk/Reward ratio hesaplama
    """
    
    def __init__(self):
        self.trades_history: Dict[str, TradePlan] = {}
    
    # ========================================================================
    # TP/SL CALCULATION METHODS
    # ========================================================================
    
    def calculate_tp_levels_percentage(
        self,
        entry_price: float,
        tp_percentage: List[float] = None,
        sl_percentage: float = 2.0,
        signal_type: SignalType = SignalType.LONG
    ) -> Tuple[List[float], float]:
        """
        TP seviyeleri % bazlı hesapla
        
        Args:
            entry_price: Giriş fiyatı
            tp_percentage: TP yüzdeleri (örn: [3, 7, 15])
            sl_percentage: SL yüzdesi
            signal_type: LONG/SHORT
        
        Returns:
            (tp_levels, sl_level)
        """
        if tp_percentage is None:
            tp_percentage = [3.0, 7.0, 15.0]
        
        tp_levels = []
        
        if signal_type == SignalType.LONG:
            for tp_pct in tp_percentage:
                tp_price = entry_price * (1 + tp_pct / 100)
                tp_levels.append(round(tp_price, 2))
            
            sl_price = entry_price * (1 - sl_percentage / 100)
        
        else:  # SHORT
            for tp_pct in tp_percentage:
                tp_price = entry_price * (1 - tp_pct / 100)
                tp_levels.append(round(tp_price, 2))
            
            sl_price = entry_price * (1 + sl_percentage / 100)
        
        return tp_levels, round(sl_price, 2)
    
    def calculate_tp_levels_atr(
        self,
        entry_price: float,
        atr_value: float,
        atr_multipliers: List[float] = None,
        signal_type: SignalType = SignalType.LONG
    ) -> Tuple[List[float], float]:
        """
        TP seviyeleri ATR (Average True Range) bazlı hesapla
        
        Args:
            entry_price: Giriş fiyatı
            atr_value: ATR değeri
            atr_multipliers: ATR çarpanları (örn: [1, 2, 3])
            signal_type: LONG/SHORT
        
        Returns:
            (tp_levels, sl_level)
        """
        if atr_multipliers is None:
            atr_multipliers = [1.0, 2.0, 3.0]
        
        tp_levels = []
        
        if signal_type == SignalType.LONG:
            for multiplier in atr_multipliers:
                tp_price = entry_price + (atr_value * multiplier)
                tp_levels.append(round(tp_price, 2))
            
            sl_price = entry_price - (atr_value * 1.5)
        
        else:  # SHORT
            for multiplier in atr_multipliers:
                tp_price = entry_price - (atr_value * multiplier)
                tp_levels.append(round(tp_price, 2))
            
            sl_price = entry_price + (atr_value * 1.5)
        
        return tp_levels, round(sl_price, 2)
    
    def calculate_tp_levels_fib(
        self,
        entry_price: float,
        recent_high: float,
        recent_low: float,
        signal_type: SignalType = SignalType.LONG
    ) -> Tuple[List[float], float]:
        """
        TP seviyeleri Fibonacci Retracement bazlı hesapla
        
        Args:
            entry_price: Giriş fiyatı
            recent_high: Son yüksek
            recent_low: Son düşük
            signal_type: LONG/SHORT
        
        Returns:
            (tp_levels, sl_level)
        """
        # Fibonacci ratios
        fib_levels = [0.382, 0.618, 0.786]
        
        tp_levels = []
        
        if signal_type == SignalType.LONG:
            range_val = recent_high - recent_low
            for ratio in fib_levels:
                tp_price = entry_price + (range_val * ratio)
                tp_levels.append(round(tp_price, 2))
            
            sl_price = recent_low * 0.99  # Slightly below recent low
        
        else:  # SHORT
            range_val = recent_high - recent_low
            for ratio in fib_levels:
                tp_price = entry_price - (range_val * ratio)
                tp_levels.append(round(tp_price, 2))
            
            sl_price = recent_high * 1.01  # Slightly above recent high
        
        return tp_levels, round(sl_price, 2)
    
    # ========================================================================
    # TRADE PLAN CREATION
    # ========================================================================
    
    def create_trade_plan(
        self,
        symbol: str,
        entry_price: float,
        entry_qty: float,
        tp_levels: List[float],
        sl_price: float,
        signal_type: SignalType,
        signal_confidence: float = 80.0,
        tp_quantities: List[float] = None
    ) -> TradePlan:
        """
        Trade planı oluştur
        
        Args:
            symbol: Trading pair (örn: BTCUSDT)
            entry_price: Giriş fiyatı
            entry_qty: Pozisyon miktarı
            tp_levels: [TP1, TP2, TP3]
            sl_price: Stop-loss fiyatı
            signal_type: LONG/SHORT
            signal_confidence: Sinyal güven (0-100)
            tp_quantities: Her TP'de çıkacak miktar (%)
        
        Returns:
            TradePlan object
        """
        if tp_quantities is None:
            tp_quantities = [0.5, 0.3, 0.2]  # 50% TP1, 30% TP2, 20% TP3
        
        # Normalize quantities
        total = sum(tp_quantities)
        tp_quantities = [q / total * 100 for q in tp_quantities]
        
        trade_plan = TradePlan(
            symbol=symbol,
            signal_type=signal_type,
            entry_price=entry_price,
            entry_qty=entry_qty,
            tp1_price=tp_levels[0] if len(tp_levels) > 0 else entry_price * 1.05,
            tp1_qty=entry_qty * (tp_quantities[0] / 100),
            tp2_price=tp_levels[1] if len(tp_levels) > 1 else entry_price * 1.10,
            tp2_qty=entry_qty * (tp_quantities[1] / 100),
            tp3_price=tp_levels[2] if len(tp_levels) > 2 else entry_price * 1.20,
            tp3_qty=entry_qty * (tp_quantities[2] / 100),
            sl_price=sl_price,
            signal_confidence=signal_confidence
        )
        
        # Store trade plan
        trade_id = f"{symbol}_{datetime.now().timestamp()}"
        self.trades_history[trade_id] = trade_plan
        
        logger.info(f"✅ Trade plan created: {trade_id}")
        logger.info(f"   Entry: {entry_price} | TP1: {trade_plan.tp1_price} | SL: {sl_price}")
        logger.info(f"   R:R Ratio: {trade_plan.risk_reward_ratio}")
        
        return trade_plan
    
    # ========================================================================
    # TRADE MONITORING
    # ========================================================================
    
    def check_tp_hits(
        self,
        symbol: str,
        current_price: float,
        signal_type: SignalType
    ) -> Tuple[List[str], str]:
        """
        TP seviyelerine temas kontrol
        
        Returns:
            (hit_tps, status_message)
        """
        hit_tps = []
        
        for trade_id, trade_plan in self.trades_history.items():
            if trade_plan.symbol != symbol:
                continue
            
            if signal_type == SignalType.LONG:
                if trade_plan.tp1_price <= current_price < trade_plan.tp2_price:
                    hit_tps.append(f"TP1: {trade_plan.tp1_price}")
                elif trade_plan.tp2_price <= current_price < trade_plan.tp3_price:
                    hit_tps.append(f"TP2: {trade_plan.tp2_price}")
                elif current_price >= trade_plan.tp3_price:
                    hit_tps.append(f"TP3: {trade_plan.tp3_price}")
            
            else:  # SHORT
                if trade_plan.tp1_price >= current_price > trade_plan.tp2_price:
                    hit_tps.append(f"TP1: {trade_plan.tp1_price}")
                elif trade_plan.tp2_price >= current_price > trade_plan.tp3_price:
                    hit_tps.append(f"TP2: {trade_plan.tp2_price}")
                elif current_price <= trade_plan.tp3_price:
                    hit_tps.append(f"TP3: {trade_plan.tp3_price}")
        
        message = " | ".join(hit_tps) if hit_tps else "No TP hit"
        return hit_tps, message
    
    def check_sl_hit(
        self,
        symbol: str,
        current_price: float,
        signal_type: SignalType
    ) -> Tuple[bool, str]:
        """SL seviyesine temas kontrol"""
        for trade_id, trade_plan in self.trades_history.items():
            if trade_plan.symbol != symbol:
                continue
            
            if signal_type == SignalType.LONG:
                if current_price <= trade_plan.sl_price:
                    return True, f"🔴 SL HIT: {trade_plan.sl_price}"
            else:  # SHORT
                if current_price >= trade_plan.sl_price:
                    return True, f"🔴 SL HIT: {trade_plan.sl_price}"
        
        return False, "SL Safe"
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def get_trade_plan_summary(self, trade_id: str) -> Optional[Dict]:
        """Trade plan özeti al"""
        if trade_id not in self.trades_history:
            return None
        
        trade_plan = self.trades_history[trade_id]
        return {
            "Symbol": trade_plan.symbol,
            "Signal": trade_plan.signal_type.value,
            "Entry": trade_plan.entry_price,
            "TP1": trade_plan.tp1_price,
            "TP2": trade_plan.tp2_price,
            "TP3": trade_plan.tp3_price,
            "SL": trade_plan.sl_price,
            "Risk:Reward": trade_plan.risk_reward_ratio,
            "Confidence": f"{trade_plan.signal_confidence}%",
            "Timestamp": trade_plan.timestamp[:19],
        }


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    calc = TradeEntryCalculator()
    
    # Test 1: Percentage-based TP calculation
    tp_levels, sl = calc.calculate_tp_levels_percentage(
        entry_price=50000,
        tp_percentage=[3, 7, 15],
        sl_percentage=2.5,
        signal_type=SignalType.LONG
    )
    print(f"\n📊 Percentage-based TP:")
    print(f"   TP1: {tp_levels[0]}, TP2: {tp_levels[1]}, TP3: {tp_levels[2]}, SL: {sl}")
    
    # Test 2: Create trade plan
    trade_plan = calc.create_trade_plan(
        symbol="BTCUSDT",
        entry_price=50000,
        entry_qty=1.0,
        tp_levels=tp_levels,
        sl_price=sl,
        signal_type=SignalType.LONG,
        signal_confidence=85.0
    )
    
    print(f"\n✅ Trade Plan Created:")
    print(f"   Risk:Reward = {trade_plan.risk_reward_ratio}")
