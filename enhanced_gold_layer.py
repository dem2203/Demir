# Enhanced Gold Correlation Layer - Phase 6.2
import requests
from typing import Dict, Optional

class EnhancedGoldLayer:
    def __init__(self):
        print("✅ Enhanced Gold Layer initialized")

    def get_gold_price(self) -> Optional[float]:
        """Get current gold price (XAU/USD)"""
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F"
            response = requests.get(url, params={'interval': '1d', 'range': '5d'}, timeout=10)
            data = response.json()
            closes = [c for c in data['chart']['result'][0]['indicators']['quote'][0]['close'] if c]
            return closes[-1] if closes else None
        except:
            return None

    def calculate_gold_correlation_score(self, symbol: str = 'BTCUSDT') -> Dict:
        gold_price = self.get_gold_price()
        if not gold_price:
            return {'score': 50, 'signal': 'NEUTRAL', 'confidence': 0}

        # Gold up = crypto up (safe haven correlation)
        # Simplified: Gold > $2000 = bullish for crypto
        score = 60 if gold_price > 2000 else 40

        return {
            'score': score,
            'signal': 'LONG' if score > 55 else 'SHORT' if score < 45 else 'NEUTRAL',
            'gold_price': gold_price,
            'confidence': 0.6
        }

def get_gold_signal(symbol: str = 'BTCUSDT') -> Dict:
    layer = EnhancedGoldLayer()
    return layer.calculate_gold_correlation_score(symbol)

if __name__ == "__main__":
    result = get_gold_signal()
    print(f"Gold Signal: {result['signal']} (Score: {result['score']:.1f})")
