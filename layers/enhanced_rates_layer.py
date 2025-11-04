# Enhanced Interest Rates Layer - Phase 6.5
import requests
from typing import Dict, Optional

class EnhancedRatesLayer:
    def __init__(self):
        print("✅ Enhanced Rates Layer initialized")

    def get_10y_treasury_yield(self) -> Optional[float]:
        """Get 10-Year US Treasury Yield"""
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ETNX"
            response = requests.get(url, params={'interval': '1d', 'range': '5d'}, timeout=10)
            data = response.json()
            closes = [c for c in data['chart']['result'][0]['indicators']['quote'][0]['close'] if c]
            return closes[-1] if closes else None
        except:
            return None

    def calculate_rates_score(self, symbol: str = 'BTCUSDT') -> Dict:
        yield_10y = self.get_10y_treasury_yield()
        if not yield_10y:
            return {'score': 50, 'signal': 'NEUTRAL', 'confidence': 0}

        # Lower rates = bullish for crypto (capital flows to risk assets)
        # Higher rates = bearish for crypto
        if yield_10y < 4.0:
            score = 60
        elif yield_10y > 5.0:
            score = 40
        else:
            score = 50

        return {
            'score': score,
            'signal': 'LONG' if score > 55 else 'SHORT' if score < 45 else 'NEUTRAL',
            'yield_10y': yield_10y,
            'confidence': 0.6
        }

def get_rates_signal(symbol: str = 'BTCUSDT') -> Dict:
    layer = EnhancedRatesLayer()
    return layer.calculate_rates_score(symbol)

if __name__ == "__main__":
    result = get_rates_signal()
    print(f"Rates Signal: {result['signal']} (10Y: {result.get('yield_10y', 0):.2f}%)")
