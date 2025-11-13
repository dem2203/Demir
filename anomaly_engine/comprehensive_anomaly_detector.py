"""
ANOMALY DETECTION
Flash crash, liquidation cascade, etc.
"""

class AnomalyDetector:
    
    @staticmethod
    def detect_price_spike(current_price: float, historical_prices: list, threshold: float = 0.10) -> Dict:
        """
        Fiyat spike tespiti
        >10% değişim = anomaly
        """
        
        if len(historical_prices) < 2:
            return {'anomaly': False}
        
        prev_price = historical_prices[-1]
        change = abs(current_price - prev_price) / prev_price
        
        if change > threshold:
            return {
                'anomaly': True,
                'type': 'PRICE_SPIKE',
                'change_percent': change * 100,
                'action': 'HOLD'
            }
        
        return {'anomaly': False}
    
    @staticmethod
    def detect_volume_anomaly(current_volume: float, avg_volume: float, threshold: float = 3.0) -> Dict:
        """Volume spike tespiti"""
        
        ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        if ratio > threshold:
            return {
                'anomaly': True,
                'type': 'VOLUME_SPIKE',
                'volume_ratio': ratio,
                'action': 'CHECK_NEWS'
            }
        
        return {'anomaly': False}
