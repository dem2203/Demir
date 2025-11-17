"""
Position Manager - Pozisyon Yönetimi ve Risk Kontrolü
DEMIR AI v6.0 - Phase 4 Production Grade

Açık pozisyonlar, SL/TP, lot boyutlama, hedging
Real-time position tracking ve P&L monitoring
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np

logger = logging.getLogger(__name__)


class PositionStatus(Enum):
    """Pozisyon durumu"""
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_CLOSED = "partially_closed"
    CLOSED = "closed"
    CANCELED = "canceled"
    ERROR = "error"


class OrderType(Enum):
    """Order türü"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


@dataclass
class Order:
    """Order (İşlem Emri)"""
    order_id: str
    order_type: OrderType
    symbol: str
    side: str  # "buy", "sell"
    quantity: float
    price: float
    timestamp: float
    
    status: str = "pending"  # pending, filled, partially_filled, canceled
    filled_quantity: float = 0.0
    filled_price: float = 0.0
    commission: float = 0.0
    
    stop_price: Optional[float] = None  # SL/TP için
    
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Dict'e dönüştür"""
        return asdict(self)


@dataclass
class Position:
    """Pozisyon"""
    position_id: str
    symbol: str
    side: str  # "long", "short"
    
    entry_price: float
    current_price: float
    quantity: float
    
    entry_time: float
    
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    unrealized_pnl: float = 0.0
    unrealized_pnl_percent: float = 0.0
    
    status: PositionStatus = PositionStatus.OPEN
    
    orders: List[Order] = field(default_factory=list)
    commission: float = 0.0
    
    metadata: Dict = field(default_factory=dict)
    
    def update_price(self, new_price: float):
        """Fiyat güncelle ve P&L hesapla"""
        self.current_price = new_price
        
        if self.side == "long":
            self.unrealized_pnl = (new_price - self.entry_price) * self.quantity
        else:  # short
            self.unrealized_pnl = (self.entry_price - new_price) * self.quantity
        
        self.unrealized_pnl -= self.commission
        self.unrealized_pnl_percent = (self.unrealized_pnl / (self.entry_price * self.quantity)) * 100
    
    def to_dict(self) -> Dict:
        """Dict'e dönüştür"""
        return {
            "position_id": self.position_id,
            "symbol": self.symbol,
            "side": self.side,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "quantity": self.quantity,
            "entry_time": self.entry_time,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "unrealized_pnl": self.unrealized_pnl,
            "unrealized_pnl_percent": self.unrealized_pnl_percent,
            "status": self.status.value,
            "commission": self.commission,
            "metadata": self.metadata
        }


class RiskCalculator:
    """Risk Hesaplayıcı"""
    
    def __init__(self, max_position_size: float = 0.05):  # Max 5% per position
        """
        Args:
            max_position_size: Maksimum pozisyon boyutu (% olarak)
        """
        self.max_position_size = max_position_size
        self.max_account_risk = 0.02  # Max 2% account risk per trade
    
    def calculate_lot_size(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss: float,
        risk_percent: float = 1.0
    ) -> float:
        """
        Lot boyutu hesapla (Kelly Criterion bazlı)
        
        Args:
            account_balance: Hesap bakiyesi
            entry_price: Giriş fiyatı
            stop_loss: Stop loss fiyatı
            risk_percent: Riske atmaya razı olduğu % (account'un)
        
        Returns:
            Lot boyutu
        """
        
        try:
            risk_amount = account_balance * (risk_percent / 100)
            price_risk = abs(entry_price - stop_loss)
            
            if price_risk <= 0:
                return 0
            
            lot_size = risk_amount / price_risk
            
            # Position size limit
            max_size = account_balance * self.max_position_size / entry_price
            lot_size = min(lot_size, max_size)
            
            return lot_size
        
        except Exception as e:
            logger.error(f"Error calculating lot size: {e}")
            return 0
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        atr: float,
        side: str = "long"
    ) -> float:
        """
        Stop loss hesapla (ATR bazlı)
        
        Args:
            entry_price: Giriş fiyatı
            atr: Average True Range
            side: "long" veya "short"
        
        Returns:
            Stop loss fiyatı
        """
        
        if side == "long":
            return entry_price - (atr * 1.5)
        else:  # short
            return entry_price + (atr * 1.5)
    
    def calculate_take_profit(
        self,
        entry_price: float,
        stop_loss: float,
        risk_reward_ratio: float = 2.0,
        side: str = "long"
    ) -> float:
        """
        Take profit hesapla (Risk-Reward bazlı)
        
        Args:
            entry_price: Giriş fiyatı
            stop_loss: Stop loss fiyatı
            risk_reward_ratio: Risk-Reward oranı
            side: "long" veya "short"
        
        Returns:
            Take profit fiyatı
        """
        
        risk = abs(entry_price - stop_loss)
        reward = risk * risk_reward_ratio
        
        if side == "long":
            return entry_price + reward
        else:  # short
            return entry_price - reward


class PositionManager:
    """Pozisyon Yöneticisi"""
    
    def __init__(self, account_balance: float = 10000.0):
        """
        Args:
            account_balance: Hesap bakiyesi
        """
        self.account_balance = account_balance
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        
        self.position_id_counter = 0
        self.order_id_counter = 0
        
        self.risk_calculator = RiskCalculator()
        
        self.total_realized_pnl = 0.0
        self.total_commission = 0.0
        
        self.price_cache: Dict[str, float] = {}
        
        logger.info(f"PositionManager initialized with balance: ${account_balance}")
    
    def open_position(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        quantity: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Pozisyon aç
        
        Args:
            symbol: "BTCUSDT"
            side: "long" veya "short"
            entry_price: Giriş fiyatı
            quantity: Miktar
            stop_loss: Stop loss fiyatı
            take_profit: Take profit fiyatı
            metadata: Ek bilgiler
        
        Returns:
            Position ID veya None
        """
        
        try:
            self.position_id_counter += 1
            position_id = f"POS_{self.position_id_counter}"
            
            position = Position(
                position_id=position_id,
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                current_price=entry_price,
                quantity=quantity,
                entry_time=datetime.now().timestamp(),
                stop_loss=stop_loss,
                take_profit=take_profit,
                status=PositionStatus.OPEN,
                metadata=metadata or {}
            )
            
            # Commission hesapla
            position.commission = entry_price * quantity * 0.001  # 0.1% commission
            
            self.positions[position_id] = position
            
            # Order oluştur
            order = Order(
                order_id=f"ORD_{self.order_id_counter}",
                order_type=OrderType.MARKET,
                symbol=symbol,
                side="buy" if side == "long" else "sell",
                quantity=quantity,
                price=entry_price,
                timestamp=datetime.now().timestamp(),
                filled_quantity=quantity,
                filled_price=entry_price,
                commission=position.commission,
                status="filled"
            )
            
            self.order_id_counter += 1
            self.orders[order.order_id] = order
            position.orders.append(order)
            
            # Balance güncelle
            self.account_balance -= (entry_price * quantity + position.commission)
            
            logger.info(f"Opened position {position_id}: {side} {quantity} {symbol} @ {entry_price}")
            return position_id
        
        except Exception as e:
            logger.error(f"Error opening position: {e}")
            return None
    
    def close_position(
        self,
        position_id: str,
        exit_price: float,
        partial: bool = False,
        partial_quantity: Optional[float] = None
    ) -> bool:
        """
        Pozisyon kapat
        
        Args:
            position_id: Position ID
            exit_price: Çıkış fiyatı
            partial: Kısmi kapatma mı?
            partial_quantity: Kısmi miktar
        
        Returns:
            Başarılı mı?
        """
        
        if position_id not in self.positions:
            logger.error(f"Position not found: {position_id}")
            return False
        
        try:
            position = self.positions[position_id]
            
            if partial and partial_quantity:
                quantity_to_close = min(partial_quantity, position.quantity)
                remaining_quantity = position.quantity - quantity_to_close
            else:
                quantity_to_close = position.quantity
                remaining_quantity = 0
            
            # P&L hesapla
            if position.side == "long":
                pnl = (exit_price - position.entry_price) * quantity_to_close
            else:  # short
                pnl = (position.entry_price - exit_price) * quantity_to_close
            
            # Commission
            exit_commission = exit_price * quantity_to_close * 0.001
            pnl -= exit_commission
            
            # Balance güncelle
            exit_amount = exit_price * quantity_to_close
            self.account_balance += exit_amount - exit_commission
            
            # Position güncelle
            if partial:
                position.quantity = remaining_quantity
                position.status = PositionStatus.PARTIALLY_CLOSED
                
                logger.info(f"Partially closed {position_id}: {quantity_to_close} @ {exit_price}, P&L: ${pnl:.2f}")
            else:
                position.status = PositionStatus.CLOSED
                self.total_realized_pnl += pnl
                self.total_commission += (position.commission + exit_commission)
                
                logger.info(f"Closed position {position_id}: P&L: ${pnl:.2f}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return False
    
    def update_position_price(self, symbol: str, new_price: float):
        """Pozisyon fiyatını güncelle"""
        
        for position in self.positions.values():
            if position.symbol == symbol:
                position.update_price(new_price)
                
                # SL/TP kontrol et
                self._check_stop_loss_take_profit(position.position_id, new_price)
        
        self.price_cache[symbol] = new_price
    
    def _check_stop_loss_take_profit(self, position_id: str, current_price: float) -> bool:
        """SL/TP kontrol et ve otomatik kapatma yap"""
        
        if position_id not in self.positions:
            return False
        
        position = self.positions[position_id]
        
        should_close = False
        reason = ""
        
        if position.stop_loss and current_price <= position.stop_loss:
            should_close = True
            reason = "Stop Loss hit"
        
        if position.take_profit and current_price >= position.take_profit:
            should_close = True
            reason = "Take Profit hit"
        
        if should_close:
            logger.info(f"Triggering {reason} for {position_id}")
            return self.close_position(position_id, current_price)
        
        return False
    
    def get_open_positions(self, symbol: Optional[str] = None) -> List[Position]:
        """Açık pozisyonları al"""
        
        positions = [
            p for p in self.positions.values()
            if p.status in [PositionStatus.OPEN, PositionStatus.PARTIALLY_CLOSED]
        ]
        
        if symbol:
            positions = [p for p in positions if p.symbol == symbol]
        
        return positions
    
    def get_position_by_id(self, position_id: str) -> Optional[Position]:
        """ID ile pozisyon al"""
        
        return self.positions.get(position_id)
    
    def get_portfolio_summary(self) -> Dict:
        """Portfolio özetini al"""
        
        open_positions = self.get_open_positions()
        
        total_unrealized_pnl = sum([p.unrealized_pnl for p in open_positions])
        total_quantity = sum([p.quantity for p in open_positions])
        
        return {
            "account_balance": self.account_balance,
            "total_realized_pnl": self.total_realized_pnl,
            "total_unrealized_pnl": total_unrealized_pnl,
            "total_pnl": self.total_realized_pnl + total_unrealized_pnl,
            "total_commission": self.total_commission,
            "open_positions": len(open_positions),
            "total_quantity": total_quantity,
            "positions": [p.to_dict() for p in open_positions]
        }
    
    def calculate_account_equity(self) -> float:
        """Hesap equity'sini hesapla"""
        
        open_positions = self.get_open_positions()
        unrealized_pnl = sum([p.unrealized_pnl for p in open_positions])
        
        return self.account_balance + unrealized_pnl
    
    def calculate_risk_metrics(self) -> Dict:
        """Risk metriklerini hesapla"""
        
        open_positions = self.get_open_positions()
        
        if not open_positions:
            return {
                "total_risk": 0,
                "max_loss": 0,
                "account_risk_percent": 0,
                "positions_at_risk": 0
            }
        
        total_risk = 0
        positions_at_risk = 0
        
        for position in open_positions:
            if position.stop_loss:
                if position.side == "long":
                    risk = (position.entry_price - position.stop_loss) * position.quantity
                else:  # short
                    risk = (position.stop_loss - position.entry_price) * position.quantity
                
                total_risk += risk
                positions_at_risk += 1
        
        account_risk_percent = (total_risk / self.account_balance) * 100 if self.account_balance > 0 else 0
        
        return {
            "total_risk": total_risk,
            "account_risk_percent": account_risk_percent,
            "positions_at_risk": positions_at_risk,
            "open_positions": len(open_positions)
        }


# Kullanım örneği
async def main():
    """Test"""
    
    manager = PositionManager(account_balance=10000)
    
    # Pozisyon aç
    pos_id = manager.open_position(
        symbol="BTCUSDT",
        side="long",
        entry_price=50000,
        quantity=0.1,
        stop_loss=49000,
        take_profit=51000
    )
    
    if pos_id:
        # Fiyat güncelle
        manager.update_position_price("BTCUSDT", 50500)
        
        # Özet
        summary = manager.get_portfolio_summary()
        print(json.dumps(summary, indent=2, default=str))
        
        # Pozisyon kapat
        manager.close_position(pos_id, 50800)
        
        # Final summary
        print("\n=== FINAL ===")
        print(json.dumps(manager.get_portfolio_summary(), indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
