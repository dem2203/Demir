"""
📊 BTC DOMINANCE & MONEY FLOW LAYER - Phase 6.3
===============================================
Tracks Bitcoin dominance and money flow patterns
- BTC.D (Bitcoin Dominance %)
- USDT.D (Tether Dominance %)
- Altseason detector
- Money rotation analysis
"""

import requests
import numpy as np
from datetime import datetime

def calculate_dominance_flow():
    """
    Calculate BTC dominance and detect altseason
    
    Returns score 0-100:
    - 100 = Strong altseason (dominance falling, bullish for alts)
    - 50 = Neutral (no clear trend)
    - 0 = BTC season (dominance rising, bearish for alts)
    """
    
    try:
        # Fetch BTC Dominance from CoinGecko
        url = "https://api.coingecko.com/api/v3/global"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'data' not in data:
            return {'available': False, 'score': 50, 'reason': 'Dominance data unavailable'}
        
        market_data = data['data']
        btc_dominance = market_data.get('market_cap_percentage', {}).get('btc', 0)
        eth_dominance = market_data.get('market_cap_percentage', {}).get('eth', 0)
        
        if btc_dominance == 0:
            return {'available': False, 'score': 50, 'reason': 'BTC dominance unavailable'}
        
        # Calculate dominance trend
        # BTC dominance typically ranges 40-70%
        # Lower dominance = altseason
        # Higher dominance = BTC season
        
        if btc_dominance < 45:
            score = 75  # Strong altseason
            phase = "ALTSEASON"
            reason = f"BTC dominance low at {btc_dominance:.1f}% - strong altcoin momentum"
        elif btc_dominance < 50:
            score = 65  # Moderate altseason
            phase = "MILD_ALTSEASON"
            reason = f"BTC dominance {btc_dominance:.1f}% - altcoins gaining ground"
        elif btc_dominance < 55:
            score = 50  # Neutral
            phase = "NEUTRAL"
            reason = f"BTC dominance {btc_dominance:.1f}% - balanced market"
        elif btc_dominance < 60:
            score = 35  # BTC gaining
            phase = "BTC_SEASON"
            reason = f"BTC dominance {btc_dominance:.1f}% - BTC outperforming"
        else:
            score = 20  # Strong BTC season
            phase = "STRONG_BTC_SEASON"
            reason = f"BTC dominance high at {btc_dominance:.1f}% - alts underperforming"
        
        # ETH analysis
        eth_ratio = eth_dominance / btc_dominance if btc_dominance > 0 else 0
        
        if eth_ratio > 0.25:
            eth_signal = "BULLISH"
        elif eth_ratio > 0.20:
            eth_signal = "NEUTRAL"
        else:
            eth_signal = "BEARISH"
        
        return {
            'available': True,
            'score': score,
            'phase': phase,
            'reason': reason,
            'btc_dominance': round(btc_dominance, 2),
            'eth_dominance': round(eth_dominance, 2),
            'eth_btc_ratio': round(eth_ratio, 3),
            'eth_signal': eth_signal,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'available': False,
            'score': 50,
            'reason': f'Dominance flow error: {str(e)[:50]}'
        }

if __name__ == "__main__":
    result = calculate_dominance_flow()
    print(f"Dominance Flow Score: {result['score']}")
    print(f"Phase: {result.get('phase', 'N/A')}")
    print(f"BTC Dominance: {result.get('btc_dominance', 0)}%")
    print(f"Reason: {result.get('reason', 'N/A')}")
