# Enhanced VIX Fear Index Layer - Phase 6.4
import requests
from typing import Dict, Optional

class EnhancedVixLayer:
    def __init__(self):
        print("✅ Enhanced VIX Layer initialized")

    def get_vix_value(self) -> Optional[float]:
        """Get current VIX (Fear Index)"""
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX"
            response = requests.get(url, params={'interval': '1d', 'range': '5d'}, timeout=10)
            data = response.json()
            closes = [c for c in data['chart']['result'][0]['indicators']['quote'][0]['close'] if c]
            return closes[-1] if closes else None
        except:
            return None

    def calculate_vix_score(self, symbol: str = 'BTCUSDT') -> Dict:
        vix = self.get_vix_value()
        if not vix:
            return {'score': 50, 'signal': 'NEUTRAL', 'confidence': 0}

        # VIX < 20 = low fear = bullish
        # VIX > 30 = high fear = bearish
        if vix < 20:
            score = 65
        elif vix > 30:
            score = 35
        else:
            score = 50

        return {
            'score': score,
            'signal': 'LONG' if score > 55 else 'SHORT' if score < 45 else 'NEUTRAL',
            'vix': vix,
            'confidence': 0.7
        }

def get_vix_signal(symbol: str = 'BTCUSDT') -> Dict:
    layer = EnhancedVixLayer()
    return layer.calculate_vix_score(symbol)

if __name__ == "__main__":
    result = get_vix_signal()
    print(f"VIX Signal: {result['signal']} (VIX: {result.get('vix', 0):.1f})")
