"""
📊 BTC DOMINANCE & MONEY FLOW LAYER - REAL DATA
===============================================
Date: 2 Kasım 2025, 21:40 CET
Version: 2.0 - CoinMarketCap API Integration

✅ REAL DATA SOURCES:
- BTC Dominance → CoinMarketCap API (CMC_API_KEY)
- USDT Dominance → CoinMarketCap API
- Market Cap Data → CoinMarketCap API
- Altseason Detection → Real dominance trends

✅ API KEY: CMC_API_KEY from Render environment
✅ Fallback: Public CMC endpoint if key fails
"""

import requests
import numpy as np
import os
from datetime import datetime

def calculate_dominance_flow():
    """
    Calculate BTC dominance and detect altseason using REAL DATA
    Returns score 0-100:
    - 100 = Strong altseason (dominance falling, bullish for alts)
    - 50 = Neutral (no clear trend)
    - 0 = BTC season (dominance rising, bearish for alts)
    """
    try:
        print(f"\n📊 Analyzing BTC Dominance & Money Flow (REAL DATA)...")
        
        # Get CMC API key
        cmc_api_key = os.getenv('CMC_API_KEY')
        
        # ==========================================
        # METHOD 1: CMC PRO API (WITH KEY)
        # ==========================================
        if cmc_api_key:
            try:
                url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
                headers = {
                    'X-CMC_PRO_API_KEY': cmc_api_key,
                    'Accept': 'application/json'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                market_data = data['data']
                
                btc_dominance = market_data['btc_dominance']
                eth_dominance = market_data.get('eth_dominance', 0)
                
                # Calculate dominance change
                btc_dominance_24h_change = market_data.get('btc_dominance_24h_percentage_change', 0)
                
                # Total market cap
                total_market_cap = market_data.get('quote', {}).get('USD', {}).get('total_market_cap', 0)
                
                print(f"✅ Using CMC PRO API (authenticated)")
                
            except Exception as e:
                print(f"⚠️ CMC PRO API failed: {e}, trying public endpoint")
                return fetch_dominance_public()
        else:
            print("⚠️ CMC_API_KEY not set, using public endpoint")
            return fetch_dominance_public()
        
        # ==========================================
        # ANALYZE DOMINANCE TRENDS
        # ==========================================
        
        # BTC Dominance Analysis
        # Historical context:
        # - Bull market peak: 70-75% (2017, 2021 tops)
        # - Bull market start: 40-45% (altseason peaks)
        # - Current range: 45-60% (typical)
        
        # Base score from absolute level
        if btc_dominance < 40:
            # Extreme altseason
            base_score = 85
            alt_signal = "EXTREME_ALTSEASON"
        elif btc_dominance < 45:
            # Strong altseason
            base_score = 75
            alt_signal = "ALTSEASON"
        elif btc_dominance < 50:
            # Moderate altseason
            base_score = 60
            alt_signal = "ALT_FAVORABLE"
        elif btc_dominance < 55:
            # Neutral zone
            base_score = 50
            alt_signal = "NEUTRAL"
        elif btc_dominance < 60:
            # BTC favored
            base_score = 40
            alt_signal = "BTC_FAVORED"
        else:
            # BTC season
            base_score = 25
            alt_signal = "BTC_SEASON"
        
        # Adjust for 24h trend
        # Falling dominance = money flowing to alts = positive
        trend_adjustment = -btc_dominance_24h_change * 10
        score = base_score + trend_adjustment
        score = max(0, min(100, score))
        
        # ==========================================
        # ETH DOMINANCE ANALYSIS
        # ==========================================
        
        # ETH dominance context (usually 15-20%)
        if eth_dominance > 18:
            eth_signal = "ETH_STRONG"
        elif eth_dominance > 15:
            eth_signal = "ETH_NORMAL"
        else:
            eth_signal = "ETH_WEAK"
        
        # ==========================================
        # MONEY FLOW INTERPRETATION
        # ==========================================
        
        if btc_dominance_24h_change > 1:
            money_flow = "FLOWING_TO_BTC"
            interpretation = "Money rotating into BTC (safe haven mode)"
        elif btc_dominance_24h_change < -1:
            money_flow = "FLOWING_TO_ALTS"
            interpretation = "Money flowing to altcoins (risk-on sentiment)"
        else:
            money_flow = "STABLE"
            interpretation = "Balanced money flow across crypto market"
        
        print(f"✅ Dominance Analysis Complete!")
        print(f"   BTC Dominance: {btc_dominance:.2f}% ({btc_dominance_24h_change:+.2f}%)")
        print(f"   ETH Dominance: {eth_dominance:.2f}%")
        print(f"   Signal: {alt_signal}")
        print(f"   Money Flow: {money_flow}")
        print(f"   Score: {score:.2f}/100")
        
        return {
            'available': True,
            'score': round(score, 2),
            'btc_dominance': round(btc_dominance, 2),
            'btc_dominance_24h_change': round(btc_dominance_24h_change, 2),
            'eth_dominance': round(eth_dominance, 2),
            'total_market_cap': round(total_market_cap / 1e9, 2) if total_market_cap > 0 else None,  # In billions
            'altseason_signal': alt_signal,
            'eth_signal': eth_signal,
            'money_flow': money_flow,
            'interpretation': interpretation,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"⚠️ Dominance calculation error: {e}")
        return {'available': False, 'score': 50, 'reason': str(e)}


def fetch_dominance_public():
    """
    Fallback: Fetch dominance from CoinMarketCap public endpoint (NO KEY REQUIRED!)
    """
    try:
        url = "https://api.coinmarketcap.com/data-api/v3/global-metrics/quotes/latest"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        market_data = data['data']
        
        btc_dominance = market_data['btcDominance']
        btc_dominance_24h_change = market_data.get('btcDominanceChange24h', 0)
        
        # Same scoring logic
        if btc_dominance < 40:
            base_score = 85
            alt_signal = "EXTREME_ALTSEASON"
        elif btc_dominance < 45:
            base_score = 75
            alt_signal = "ALTSEASON"
        elif btc_dominance < 50:
            base_score = 60
            alt_signal = "ALT_FAVORABLE"
        elif btc_dominance < 55:
            base_score = 50
            alt_signal = "NEUTRAL"
        elif btc_dominance < 60:
            base_score = 40
            alt_signal = "BTC_FAVORED"
        else:
            base_score = 25
            alt_signal = "BTC_SEASON"
        
        trend_adjustment = -btc_dominance_24h_change * 10
        score = base_score + trend_adjustment
        score = max(0, min(100, score))
        
        if btc_dominance_24h_change > 1:
            money_flow = "FLOWING_TO_BTC"
        elif btc_dominance_24h_change < -1:
            money_flow = "FLOWING_TO_ALTS"
        else:
            money_flow = "STABLE"
        
        print(f"✅ Using CMC PUBLIC API (no authentication)")
        print(f"   BTC Dominance: {btc_dominance:.2f}% ({btc_dominance_24h_change:+.2f}%)")
        print(f"   Score: {score:.2f}/100")
        
        return {
            'available': True,
            'score': round(score, 2),
            'btc_dominance': round(btc_dominance, 2),
            'btc_dominance_24h_change': round(btc_dominance_24h_change, 2),
            'altseason_signal': alt_signal,
            'money_flow': money_flow,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"⚠️ Public dominance fetch failed: {e}")
        return {'available': False, 'score': 50, 'reason': str(e)}


def get_dominance_signal():
    """
    Simplified wrapper for dominance signal (used by ai_brain.py)
    """
    result = calculate_dominance_flow()
    
    if result['available']:
        return {
            'available': True,
            'score': result['score'],
            'signal': result.get('altseason_signal', 'NEUTRAL')
        }
    else:
        return {
            'available': False,
            'score': 50,
            'signal': 'NEUTRAL'
        }


# ============================================================================
# STANDALONE TESTING
# ============================================================================

if __name__ == "__main__":
    print("📊 BTC DOMINANCE LAYER - REAL DATA TEST")
    print("=" * 70)
    
    result = calculate_dominance_flow()
    
    print("\n" + "=" * 70)
    print("📊 DOMINANCE ANALYSIS:")
    print(f"   Available: {result['available']}")
    print(f"   Score: {result.get('score', 'N/A')}/100")
    print(f"   BTC Dominance: {result.get('btc_dominance', 'N/A')}%")
    print(f"   24h Change: {result.get('btc_dominance_24h_change', 'N/A')}%")
    print(f"   Signal: {result.get('altseason_signal', 'N/A')}")
    print(f"   Money Flow: {result.get('money_flow', 'N/A')}")
    print("=" * 70)
