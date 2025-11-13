"""
TRAILING TP/SL MANAGER
Dinamik take-profit ve stop-loss
Kâr koruma stratejisi

⚠️ REAL DATA: Gerçek price updates
"""

from typing import Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TrailingTPSLManager:
    """
    Trailing TP/SL yönetimi
    Kâr kilitleme ve risk yönetimi
    """
    
    def __init__(self, initial_tp: float, initial_sl: float, trailing_percent: float = 0.5):
        """
        Initialize
        
        Args:
            initial_tp: Initial take-profit level
            initial_sl: Initial stop-loss level
            trailing_percent: Trailing percentage (%)
        """
        
        self.initial_tp = initial_tp
        self.current_tp = initial_tp
        self.current_sl = initial_sl
        self.max_price = initial_tp  # Starting from entry
        self.trailing_percent = trailing_percent
        self.break_even_triggered = False
        self.history = []
    
    def update(self, current_price: float) -> Dict:
        """
        Price güncellemesinde TP/SL'yi ayarla
        
        Stratejisi:
        1. Fiyat yukarı giderse, TP'yi takip et (kâr kilitle)
        2. %1 kâr olursa, SL'yi entry'ye taşı (break-even)
        3. Fiyat düşerse, SL profit'i koru
        
        Args:
            current_price: Mevcut fiyat (REAL)
        
        Returns:
            Dict: Updated levels ve actions
        """
        
        updates = {}
        
        # TP'yi yukarı taşı (trailing stop)
        if current_price > self.max_price:
            self.max_price = current_price
            
            # Yeni TP = max_price - trailing distance
            new_tp = current_price * (1 - self.trailing_percent / 100)
            
            # TP sadece yukarı gitmeli (aşağı asla)
            if new_tp > self.current_tp:
                self.current_tp = new_tp
                updates['tp_updated'] = True
                updates['new_tp'] = new_tp
                logger.debug(f"📈 TP updated: {self.current_tp:.2f}")
        
        # SL'yi yukarı taşı (break-even ve profit protection)
        profit_amount = current_price - self.max_price
        profit_percent = (profit_amount / self.max_price * 100) if self.max_price > 0 else 0
        
        if profit_percent > 1.0 and not self.break_even_triggered:
            # Break-even'e taşı
            self.current_sl = self.max_price * 0.99
            self.break_even_triggered = True
            updates['sl_updated'] = True
            updates['break_even_triggered'] = True
            updates['new_sl'] = self.current_sl
            logger.info(f"🎯 Break-even triggered: SL moved to {self.current_sl:.2f}")
        
        elif profit_percent > 2.0 and self.break_even_triggered:
            # Further profit protection
            new_sl = current_price * (1 - self.trailing_percent / 100 * 1.5)
            
            if new_sl > self.current_sl:
                self.current_sl = new_sl
                updates['sl_updated'] = True
                updates['new_sl'] = new_sl
                logger.debug(f"📉 SL adjusted: {self.current_sl:.2f}")
        
        # Record history
        self.history.append({
            'timestamp': datetime.now(),
            'price': current_price,
            'tp': self.current_tp,
            'sl': self.current_sl,
            'updates': updates
        })
        
        return {
            'current_price': current_price,
            'current_tp': self.current_tp,
            'current_sl': self.current_sl,
            'max_price': self.max_price,
            'break_even': self.break_even_triggered,
            'updates': updates,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_current_levels(self) -> Dict:
        """Mevcut TP/SL seviyelerini al"""
        
        return {
            'tp': self.current_tp,
            'sl': self.current_sl,
            'max_price_seen': self.max_price,
            'break_even_active': self.break_even_triggered
        }
