# Enhanced BTC Dominance Layer - Phase 6.3
import requests
from typing import Dict, Optional

class EnhancedDominanceLayer:
    def __init__(self):
        print("✅ Enhanced Dominance Layer initialized")

    def get_btc_dominance(self) -> Optional[float]:
        """Get BTC dominance percentage"""
        try:
            url = "https://api.coingecko.com/api/v3/global"
            response = requests.get(url, timeout=10)
            data = response.json()
            return data['data']['market_cap_percentage'].get('btc')
        except:
            return None

    def calculate_dominance_score(self, symbol: str = 'BTCUSDT') -> Dict:
        dominance = self.get_btc_dominance()
        if not dominance:
            return {'score': 50, 'signal': 'NEUTRAL', 'confidence': 0}

        # BTC dominance rising = BTC bullish, alts bearish
        # BTC dominance falling = alts bullish
        if 'BTC' in symbol:
            score = 60 if dominance > 50 else 40
        else:
            score = 40 if dominance > 50 else 60

        return {
            'score': score,
            'signal': 'LONG' if score > 55 else 'SHORT' if score < 45 else 'NEUTRAL',
            'dominance': dominance,
            'confidence': 0.7
        }

def get_dominance_signal(symbol: str = 'BTCUSDT') -> Dict:
    layer = EnhancedDominanceLayer()
    return layer.calculate_dominance_score(symbol)

if __name__ == "__main__":
    result = get_dominance_signal()
    print(f"Dominance Signal: {result['signal']} (Dom: {result.get('dominance', 0):.1f}%)")
