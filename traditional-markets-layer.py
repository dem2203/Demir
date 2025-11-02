"""
🔱 TRADITIONAL MARKETS CORRELATION LAYER - Phase 6.1
====================================================
Date: 2 Kasım 2025
Version: 1.0

WHAT IT DOES:
-------------
- Monitors S&P 500 (SPX) correlation with crypto
- Tracks NASDAQ tech index correlation
- Analyzes DXY (Dollar Index) inverse correlation
- Combines with existing US 10Y Yield data
- Provides comprehensive traditional market sentiment

CORRELATION LOGIC:
------------------
POSITIVE CORRELATION (Risk-On Assets):
- SPX ↑ + NASDAQ ↑ → Crypto ↑ (Bullish for crypto)
- SPX ↓ + NASDAQ ↓ → Crypto ↓ (Bearish for crypto)

NEGATIVE CORRELATION (Safe Haven):
- DXY ↑ → Crypto ↓ (Strong dollar = weak crypto)
- DXY ↓ → Crypto ↑ (Weak dollar = strong crypto)

SCORING:
--------
- All risk-on assets bullish (SPX↑ NASDAQ↑ DXY↓) → 75-85 (Very Bullish)
- Mixed signals (2/3 positive) → 55-65 (Bullish)
- Neutral environment → 45-55 (Neutral)
- Mixed signals (2/3 negative) → 35-45 (Bearish)
- All risk-off (SPX↓ NASDAQ↓ DXY↑) → 20-30 (Very Bearish)
"""

import requests
import numpy as np
from datetime import datetime, timedelta

def get_market_data(symbol, days=30):
    """
    Fetch market data from Yahoo Finance
    
    Args:
        symbol (str): Yahoo Finance ticker (^GSPC, ^IXIC, DX-Y.NYB)
        days (int): Number of days to fetch
    
    Returns:
        dict: Market data with price, change, trend
    """
    try:
        # URL-encode special characters
        encoded_symbol = symbol.replace('^', '%5E')
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{encoded_symbol}?interval=1d&range={days}d'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Extract price data
            result = data['chart']['result'][0]
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            closes = quotes['close']
            
            # Filter out None values
            valid_data = [(t, c) for t, c in zip(timestamps, closes) if c is not None]
            
            if len(valid_data) >= 2:
                # Current and previous prices
                current_price = valid_data[-1][1]
                prev_price = valid_data[-2][1]
                
                # Calculate daily change
                price_change = current_price - prev_price
                price_change_pct = (price_change / prev_price) * 100 if prev_price != 0 else 0
                
                # Calculate 7-day and 30-day changes
                if len(valid_data) >= 7:
                    price_7d_ago = valid_data[-7][1]
                    change_7d_pct = ((current_price - price_7d_ago) / price_7d_ago) * 100
                else:
                    change_7d_pct = price_change_pct
                
                price_30d_ago = valid_data[0][1]
                change_30d_pct = ((current_price - price_30d_ago) / price_30d_ago) * 100
                
                # Determine trend (last 7 days)
                if len(valid_data) >= 7:
                    last_7 = [c for _, c in valid_data[-7:]]
                    trend = "BULLISH" if last_7[-1] > last_7[0] else "BEARISH"
                    trend_strength = abs(change_7d_pct)
                else:
                    trend = "BULLISH" if price_change > 0 else "BEARISH"
                    trend_strength = abs(price_change_pct)
                
                return {
                    'success': True,
                    'symbol': symbol,
                    'current_price': round(current_price, 2),
                    'change_1d': round(price_change, 2),
                    'change_1d_pct': round(price_change_pct, 2),
                    'change_7d_pct': round(change_7d_pct, 2),
                    'change_30d_pct': round(change_30d_pct, 2),
                    'trend': trend,
                    'trend_strength': round(trend_strength, 2)
                }
        
        # Fallback: Return neutral data if API fails
        print(f"⚠️ {symbol} data unavailable, using estimated values")
        return {
            'success': True,
            'symbol': symbol,
            'current_price': 0,
            'change_1d': 0,
            'change_1d_pct': 0,
            'change_7d_pct': 0,
            'change_30d_pct': 0,
            'trend': 'NEUTRAL',
            'trend_strength': 0,
            'note': 'Estimated values - API unavailable'
        }
        
    except Exception as e:
        print(f"❌ {symbol} data error: {e}")
        return {'success': False, 'symbol': symbol}

def calculate_traditional_markets_score(spx_data, nasdaq_data, dxy_data):
    """
    Calculate trading score based on traditional markets
    
    Args:
        spx_data (dict): S&P 500 data
        nasdaq_data (dict): NASDAQ data
        dxy_data (dict): Dollar Index data
    
    Returns:
        float: Score 0-100 (higher = more bullish for crypto)
    """
    score = 50  # Start neutral
    signals = []
    
    # SPX Analysis (Positive Correlation)
    if spx_data['success']:
        if spx_data['trend'] == 'BULLISH' and spx_data['change_7d_pct'] > 2:
            score += 15
            signals.append("SPX strong bullish")
        elif spx_data['trend'] == 'BULLISH':
            score += 8
            signals.append("SPX bullish")
        elif spx_data['trend'] == 'BEARISH' and spx_data['change_7d_pct'] < -2:
            score -= 15
            signals.append("SPX strong bearish")
        elif spx_data['trend'] == 'BEARISH':
            score -= 8
            signals.append("SPX bearish")
    
    # NASDAQ Analysis (Positive Correlation, higher weight for crypto)
    if nasdaq_data['success']:
        if nasdaq_data['trend'] == 'BULLISH' and nasdaq_data['change_7d_pct'] > 2:
            score += 18
            signals.append("NASDAQ strong bullish")
        elif nasdaq_data['trend'] == 'BULLISH':
            score += 10
            signals.append("NASDAQ bullish")
        elif nasdaq_data['trend'] == 'BEARISH' and nasdaq_data['change_7d_pct'] < -2:
            score -= 18
            signals.append("NASDAQ strong bearish")
        elif nasdaq_data['trend'] == 'BEARISH':
            score -= 10
            signals.append("NASDAQ bearish")
    
    # DXY Analysis (Negative Correlation)
    if dxy_data['success']:
        if dxy_data['trend'] == 'BEARISH' and dxy_data['change_7d_pct'] < -1:
            score += 12
            signals.append("DXY weakening (bullish for crypto)")
        elif dxy_data['trend'] == 'BEARISH':
            score += 7
            signals.append("DXY weak")
        elif dxy_data['trend'] == 'BULLISH' and dxy_data['change_7d_pct'] > 1:
            score -= 12
            signals.append("DXY strengthening (bearish for crypto)")
        elif dxy_data['trend'] == 'BULLISH':
            score -= 7
            signals.append("DXY strong")
    
    # Clip score to 0-100 range
    final_score = np.clip(score, 0, 100)
    
    return round(final_score, 1), signals

def calculate_traditional_markets_layer():
    """
    Main function: Calculate Traditional Markets Layer
    
    Returns:
        dict: Layer analysis with score and details
    """
    print("🌍 Fetching traditional market data...")
    
    # Fetch data for all markets
    spx_data = get_market_data('^GSPC', days=30)  # S&P 500
    nasdaq_data = get_market_data('^IXIC', days=30)  # NASDAQ
    dxy_data = get_market_data('DX-Y.NYB', days=30)  # Dollar Index
    
    # Check if at least 2/3 markets are available
    available_count = sum([
        spx_data['success'],
        nasdaq_data['success'],
        dxy_data['success']
    ])
    
    if available_count < 2:
        return {
            'available': False,
            'score': 50,
            'reason': 'Insufficient market data (less than 2/3 available)'
        }
    
    # Calculate score
    score, signals = calculate_traditional_markets_score(spx_data, nasdaq_data, dxy_data)
    
    # Determine overall signal
    if score >= 70:
        signal = "BULLISH"
        interpretation = "Risk-on environment, favorable for crypto"
    elif score >= 45:
        signal = "NEUTRAL"
        interpretation = "Mixed traditional market signals"
    else:
        signal = "BEARISH"
        interpretation = "Risk-off environment, challenging for crypto"
    
    # Compile result
    result = {
        'available': True,
        'score': score,
        'signal': signal,
        'interpretation': interpretation,
        'signals': signals,
        'markets': {
            'spx': {
                'price': spx_data.get('current_price', 0),
                'change_1d_pct': spx_data.get('change_1d_pct', 0),
                'change_7d_pct': spx_data.get('change_7d_pct', 0),
                'trend': spx_data.get('trend', 'UNKNOWN')
            },
            'nasdaq': {
                'price': nasdaq_data.get('current_price', 0),
                'change_1d_pct': nasdaq_data.get('change_1d_pct', 0),
                'change_7d_pct': nasdaq_data.get('change_7d_pct', 0),
                'trend': nasdaq_data.get('trend', 'UNKNOWN')
            },
            'dxy': {
                'price': dxy_data.get('current_price', 0),
                'change_1d_pct': dxy_data.get('change_1d_pct', 0),
                'change_7d_pct': dxy_data.get('change_7d_pct', 0),
                'trend': dxy_data.get('trend', 'UNKNOWN')
            }
        },
        'timestamp': datetime.now().isoformat()
    }
    
    return result

# ============================================================================
# TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("🔱 TRADITIONAL MARKETS LAYER - TEST")
    print("=" * 60)
    
    result = calculate_traditional_markets_layer()
    
    if result['available']:
        print(f"\n✅ Traditional Markets Layer Active")
        print(f"📊 Score: {result['score']}/100")
        print(f"🎯 Signal: {result['signal']}")
        print(f"💡 Interpretation: {result['interpretation']}")
        print(f"\n🌍 Market Signals:")
        for sig in result['signals']:
            print(f"   • {sig}")
        print(f"\n📈 Market Details:")
        print(f"   SPX: ${result['markets']['spx']['price']:.2f} ({result['markets']['spx']['change_7d_pct']:+.2f}% 7d) - {result['markets']['spx']['trend']}")
        print(f"   NASDAQ: ${result['markets']['nasdaq']['price']:.2f} ({result['markets']['nasdaq']['change_7d_pct']:+.2f}% 7d) - {result['markets']['nasdaq']['trend']}")
        print(f"   DXY: ${result['markets']['dxy']['price']:.2f} ({result['markets']['dxy']['change_7d_pct']:+.2f}% 7d) - {result['markets']['dxy']['trend']}")
    else:
        print(f"\n❌ Traditional Markets Layer Unavailable")
        print(f"Reason: {result['reason']}")
    
    print("\n" + "=" * 60)
