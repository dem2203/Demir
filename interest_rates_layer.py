"""
🔱 INTEREST RATES LAYER - Phase 6.6
====================================
Date: 2 Kasım 2025
Version: 1.0 - SYNTAX FIXED

HOTFIX 2025-11-02 16:32:
------------------------
✅ Fixed syntax error on line 222 (missing colon)
✅ All other code preserved exactly

WHAT IT DOES:
-------------
- Monitors Fed interest rates (Federal Funds Rate)
- Tracks US 10-Year Treasury Yield
- Analyzes rate direction (rising/falling)
- Correlates with crypto risk appetite

RATE LOGIC:
-----------
RISING RATES → Bearish for crypto (capital flows to bonds)
FALLING RATES → Bullish for crypto (liquidity flows to risk assets)
HIGH RATES (>5%) → Very bearish
LOW RATES (<2%) → Very bullish

SCORING:
--------
- Rates falling + low → 70-80 (Very Bullish)
- Rates falling + moderate → 55-65 (Bullish)
- Rates stable → 45-55 (Neutral)
- Rates rising + moderate → 35-45 (Bearish)
- Rates rising + high → 20-30 (Very Bearish)
"""

import requests
import numpy as np
from datetime import datetime, timedelta

def get_interest_rate_data():
    """
    Fetch US interest rate data
    Data sources:
    - Fed Funds Rate (Federal Reserve target rate)
    - US 10Y Treasury Yield
    
    Returns:
        dict: Interest rate metrics
    """
    try:
        # Method 1: Try FRED API (Federal Reserve Economic Data)
        # This is a fallback - requires API key in production
        # For now, we'll use Yahoo Finance for US10Y
        
        # Get US 10-Year Treasury Yield from Yahoo Finance
        symbol = '%5ETNX'  # ^TNX (10-year treasury) URL-encoded
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=60d'
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
                # Current and previous yields
                current_yield = valid_data[-1][1]
                prev_yield = valid_data[-2][1]
                
                # Calculate 30-day average
                recent_closes = [c for _, c in valid_data[-30:] if c is not None]
                yield_avg_30d = np.mean(recent_closes) if recent_closes else current_yield
                
                # Calculate trend (rising/falling)
                yield_change = current_yield - prev_yield
                yield_change_pct = (yield_change / prev_yield) * 100 if prev_yield != 0 else 0
                
                # Determine trend direction (last 10 days)
                if len(valid_data) >= 10:
                    last_10 = [c for _, c in valid_data[-10:]]
                    trend = "RISING" if last_10[-1] > last_10[0] else "FALLING"
                else:
                    trend = "RISING" if yield_change > 0 else "FALLING"
                
                # Estimate Fed Funds Rate (usually 0.5-1% below 10Y yield)
                # This is an approximation - in production use actual Fed data
                fed_rate_est = max(0, current_yield - 1.0)
                
                return {
                    'success': True,
                    'us10y_yield': round(current_yield, 2),
                    'us10y_prev': round(prev_yield, 2),
                    'us10y_change': round(yield_change, 2),
                    'us10y_change_pct': round(yield_change_pct, 2),
                    'us10y_avg_30d': round(yield_avg_30d, 2),
                    'fed_rate_est': round(fed_rate_est, 2),
                    'trend': trend
                }
        
        # Fallback: Return estimated values if API fails
        print("⚠️ Interest Rate API unavailable, using estimated values")
        return {
            'success': True,
            'us10y_yield': 4.25,
            'us10y_prev': 4.35,
            'us10y_change': -0.10,
            'us10y_change_pct': -2.3,
            'us10y_avg_30d': 4.40,
            'fed_rate_est': 5.25,
            'trend': 'FALLING',
            'note': 'Estimated values - API unavailable'
        }
        
    except Exception as e:
        print(f"❌ Interest Rate data error: {e}")
        return {'success': False}

def calculate_rates_score(rate_data):
    """
    Calculate trading score based on interest rates
    Logic:
    - Low rates + falling → Very bullish for crypto
    - High rates + rising → Very bearish for crypto
    
    Args:
        rate_data (dict): Interest rate metrics
    
    Returns:
        float: Score 0-100 (higher = more bullish for crypto)
    """
    us10y = rate_data['us10y_yield']
    trend = rate_data['trend']
    
    # Base score from yield level
    if us10y < 2.0:
        # Very low rates → very bullish
        base_score = 75
    elif us10y < 3.0:
        # Low rates → bullish
        base_score = 65
    elif us10y < 4.0:
        # Moderate rates → slightly bullish
        base_score = 55
    elif us10y < 5.0:
        # Elevated rates → slightly bearish
        base_score = 40
    elif us10y < 6.0:
        # High rates → bearish
        base_score = 30
    else:
        # Very high rates → very bearish
        base_score = 20
    
    # Adjust for trend
    if trend == "FALLING":
        # Rates falling = more liquidity = bullish
        adjustment = +8
    else:
        # Rates rising = tighter conditions = bearish
        adjustment = -8
    
    final_score = np.clip(base_score + adjustment, 0, 100)
    return round(final_score, 1)

def calculate_interest_rates_layer():
    """
    Main function: Calculate Interest Rates Layer
    
    Returns:
        dict: Layer analysis with score and details
    """
    # Get interest rate data
    rate_data = get_interest_rate_data()
    
    if not rate_data['success']:
        return {
            'available': False,
            'score': 50,
            'reason': 'Interest rate data unavailable'
        }
    
    # Calculate score
    score = calculate_rates_score(rate_data)
    
    # Determine signal
    if score >= 65:
        signal = "BULLISH"
        interpretation = "Low/falling rates, favorable for risk assets"
    elif score >= 45:
        signal = "NEUTRAL"
        interpretation = "Moderate rates, balanced environment"
    else:
        signal = "BEARISH"
        interpretation = "High/rising rates, challenging for crypto"
    
    # Compile result
    result = {
        'available': True,
        'score': score,
        'signal': signal,
        'interpretation': interpretation,
        'us10y_yield': rate_data['us10y_yield'],
        'us10y_change': rate_data['us10y_change'],
        'us10y_change_pct': rate_data['us10y_change_pct'],
        'us10y_trend': rate_data['trend'],
        'us10y_avg_30d': rate_data['us10y_avg_30d'],
        'fed_rate_est': rate_data['fed_rate_est'],
        'timestamp': datetime.now().isoformat()
    }
    
    # ⭐ HOTFIX: Added missing colon here (line 222 fix)
    if 'note' in rate_data:
        result['note'] = rate_data['note']
    
    return result

# ============================================================================
# TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("🔱 INTEREST RATES LAYER - TEST")
    print("=" * 60)
    
    result = calculate_interest_rates_layer()
    
    if result['available']:
        print(f"\n✅ Interest Rates Layer Active")
        print(f"📊 Score: {result['score']}/100")
        print(f"🎯 Signal: {result['signal']}")
        print(f"💡 Interpretation: {result['interpretation']}")
        print(f"\n📈 Rate Details:")
        print(f"   US 10Y Yield: {result['us10y_yield']}%")
        print(f"   Change: {result['us10y_change']}% ({result['us10y_change_pct']}%)")
        print(f"   Trend: {result['us10y_trend']}")
        print(f"   30-Day Avg: {result['us10y_avg_30d']}%")
        print(f"   Fed Rate (est): {result['fed_rate_est']}%")
        
        if 'note' in result:
            print(f"\n⚠️ Note: {result['note']}")
    else:
        print(f"\n❌ Interest Rates Layer Unavailable")
        print(f"Reason: {result['reason']}")
    
    print("\n" + "=" * 60)
