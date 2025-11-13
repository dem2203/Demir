"""
TRAILING TP/SL - Dinamik kâr kilitleme
"""

class TrailingTPSLManager:
    
    def __init__(self, initial_tp: float, initial_sl: float, trailing_percent: float = 0.5):
        self.current_tp = initial_tp
        self.current_sl = initial_sl
        self.max_price = initial_tp
        self.trailing_percent = trailing_percent
    
    def update(self, current_price: float) -> Dict:
        """
        Fiyat güncellemesinde TP'yi yukarı çek
        (Kâr koruma stratejisi)
        """
        
        updates = {}
        
        # TP'yi yukarı taşı (hiçbir zaman aşağı gitme)
        if current_price > self.max_price:
            self.max_price = current_price
            new_tp = current_price * (1 - self.trailing_percent / 100)
            
            if new_tp > self.current_tp:
                self.current_tp = new_tp
                updates['tp_updated'] = True
        
        # SL'yi yukarı taşı (break-even'e geç)
        if current_price > self.max_price * 1.01:  # >%1 kâr
            new_sl = self.max_price * 0.99
            if new_sl > self.current_sl:
                self.current_sl = new_sl
                updates['sl_updated'] = True
        
        return {
            'current_tp': self.current_tp,
            'current_sl': self.current_sl,
            'updates': updates
        }
