"""
ORDER BOOK ANALYSIS
Buyer/Seller imbalance tespiti
"""

class OrderBookAnalyzer:
    
    @staticmethod
    def analyze_imbalance(bid_volume: float, ask_volume: float) -> Dict:
        """
        Bid/Ask imbalance analiz et
        
        bid_volume > ask_volume = Buyer demand (LONG)
        ask_volume > bid_volume = Seller pressure (SHORT)
        """
        
        total_volume = bid_volume + ask_volume
        
        if total_volume == 0:
            return {'imbalance': 0, 'signal': 'NEUTRAL'}
        
        imbalance = (bid_volume - ask_volume) / total_volume
        
        if imbalance > 0.3:
            signal = 'STRONG_BUY'
        elif imbalance > 0.1:
            signal = 'BUY'
        elif imbalance < -0.3:
            signal = 'STRONG_SELL'
        elif imbalance < -0.1:
            signal = 'SELL'
        else:
            signal = 'NEUTRAL'
        
        return {
            'imbalance': imbalance,
            'signal': signal,
            'bid_volume': bid_volume,
            'ask_volume': ask_volume
        }
