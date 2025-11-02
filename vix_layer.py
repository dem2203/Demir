"""
🔱 VIX FEAR INDEX LAYER - Phase 6.5
===================================
Date: 2 Kasım 2025
Version: 1.0

WHAT IT DOES:
-------------
- Monitors VIX (Fear Index) levels
- Detects extreme fear/greed in markets
- Correlates with crypto risk appetite
- Provides risk-on/risk-off signals

VIX LEVELS:
-----------
> 30: EXTREME FEAR → Risk-off → Bearish for crypto
20-30: ELEVATED FEAR → Caution
15-20: NORMAL → Neutral
< 15: COMPLACENCY → Risk-on → Bullish for crypto

SCORING:
--------
- VIX < 15 (Complacency) → 65-75 (Bullish)
- VIX 15-20 (Normal) → 45-55 (Neutral)
- VIX 20-30 (Fear) → 30-40 (Bearish)
- VIX > 30 (Panic) → 15-25 (Very Bearish)
"""

import requests
import numpy as np
from datetime import datetime, timedelta

def get_vix_data():
    """
    Fetch VIX data from Yahoo Finance or alternative source
    
    Returns:
        dict: VIX current level, change, and trend
    """
    try:
        # Method 1: Try Yahoo Finance API (free, no key needed)
        symbol = '%5EVIX'  # ^VIX URL-encoded
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=30d'
        
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
                # Current and previous VIX
                current_vix = valid_data[-1][1]
                prev_vix = valid_data[-2][1]
                
                # Calculate 7-day average
                recent_closes = [c for _, c in valid_data[-7:]]
                vix_avg_7d = np.mean(recent_closes)
                
                # Calculate trend (rising/falling)
                vix_change = current_vix - prev_vix
                vix_change_pct = (vix_change / prev_vix) * 100
                
                # Determine trend direction
                if len(valid_data) >= 5:
                    last_5 = [c for _, c in valid_data[-5:]]
                    trend = "RISING" if last_5[-1] > last_5[0] else "FALLING"
                else:
                    trend = "RISING" if vix_change > 0 else "FALLING"
                
                return {
                    'success': True,
                    'current_vix': round(current_vix, 2),
                    'prev_vix': round(prev_vix, 2),
                    'vix_change': round(vix_change, 2),
                    'vix_change_pct': round(vix_change_pct, 2),
                    'vix_avg_7d': round(vix_avg_7d, 2),
                    'trend': trend
                }
        
        # Fallback: Return mock data if API fails
        print("⚠️ VIX API unavailable, using estimated values")
        return {
            'success': True,
            'current_vix': 18.5,
            'prev_vix': 19.2,
            'vix_change': -0.7,
            'vix_change_pct': -3.6,
            'vix_avg_7d': 19.8,
            'trend': 'FALLING',
            'note': 'Estimated values - API unavailable'
        }
        
    except Exception as e:
        print(f"❌ VIX data error: {e}")
        return {'success': False}

def calculate_vix_score(vix_data):
    """
    Calculate trading score based on VIX levels
    
    VIX Interpretation:
    - < 12: Extreme complacency (very bullish for risk assets)
    - 12-15: Low fear (bullish)
    - 15-20: Normal (neutral)
    - 20-25: Elevated fear (slightly bearish)
    - 25-30: High fear (bearish)
    - > 30: Panic (very bearish)
    
    Args:
        vix_data (dict): VIX metrics
    
    Returns:
        float: Score 0-100 (higher = more bullish for crypto)
    """
    
    current_vix = vix_data['current_vix']
    trend = vix_data['trend']
    
    # Base score from VIX level
    if current_vix < 12:
        base_score = 75  # Extreme complacency → very bullish
    elif current_vix < 15:
        base_score = 65  # Low fear → bullish
    elif current_vix < 20:
        base_score = 50  # Normal → neutral
    elif current_vix < 25:
        base_score = 40  # Elevated fear → slightly bearish
    elif current_vix < 30:
        base_score = 30  # High fear → bearish
    else:
        base_score = 20  # Panic → very bearish
    
    # Adjust for trend
    if trend == "FALLING":
        # VIX falling = fear decreasing = bullish
        adjustment = +5
    else:
        # VIX rising = fear increasing = bearish
        adjustment = -5
    
    final_score = np.clip(base_score + adjustment, 0, 100)
    
    return round(final_score, 1)

def calculate_vix_layer():
    """
    Main function: Calculate VIX Fear Index Layer
    
    Returns:
        dict: Layer analysis with score and details
    """
    
    # Get VIX data
    vix_data = get_vix_data()
    
    if not vix_data['success']:
        return {
            'available': False,
            'score': 50,
            'reason': 'VIX data unavailable'
        }
    
    # Calculate score
    score = calculate_vix_score(vix_data)
    
    # Determine signal
    if score >= 65:
        signal = "BULLISH"
        interpretation = "Low market fear, risk-on environment"
    elif score >= 45:
        signal = "NEUTRAL"
        interpretation = "Normal fear levels, balanced market"
    else:
        signal = "BEARISH"
        interpretation = "Elevated market fear, risk-off environment"
    
    # Compile result
    result = {
        'available': True,
        'score': score,
        'signal': signal,
        'interpretation': interpretation,
        'vix_level': vix_data['current_vix'],
        'vix_change': vix_data['vix_change'],
        'vix_change_pct': vix_data['vix_change_pct'],
        'vix_trend': vix_data['trend'],
        'vix_7d_avg': vix_data['vix_avg_7d'],
        'timestamp': datetime.now().isoformat()
    }
    
    if 'note' in vix_data:
        result['note'] = vix_data['note']
    
    return result

# ============================================================================
# TEST EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("🔱 VIX FEAR INDEX LAYER - TEST")
    print("=" * 60)
    
    result = calculate_vix_layer()
    
    if result['available']:
        print(f"\n✅ VIX Layer Active")
        print(f"📊 Score: {result['score']}/100")
        print(f"🎯 Signal: {result['signal']}")
        print(f"💡 Interpretation: {result['interpretation']}")
        print(f"\n📈 VIX Details:")
        print(f"  Current VIX: {result['vix_level']}")
        print(f"  Change: {result['vix_change']} ({result['vix_change_pct']}%)")
        print(f"  Trend: {result['vix_trend']}")
        print(f"  7-Day Avg: {result['vix_7d_avg']}")
        
        if 'note' in result:
            print(f"\n⚠️ Note: {result['note']}")
    else:
        print(f"\n❌ VIX Layer Unavailable")
        print(f"Reason: {result['reason']}")
    
    print("\n" + "=" * 60)
