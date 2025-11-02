"""
🔱 VIX FEAR INDEX LAYER - REAL DATA
===================================
Date: 2 Kasım 2025, 21:45 CET
Version: 2.0 - yfinance Integration

✅ REAL DATA SOURCE:
- VIX Index (^VIX) → yfinance (FREE!)
- Historical VIX data → 30 days
- Fear/Greed calculation → Real levels

✅ NO API KEY REQUIRED - 100% FREE!
"""

import requests
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def get_vix_data():
    """
    Fetch VIX data from Yahoo Finance using yfinance
    Returns:
        dict: VIX current level, change, and trend
    """
    try:
        print(f"\n📊 Fetching VIX Fear Index (REAL DATA)...")
        
        # ==========================================
        # FETCH VIX FROM YFINANCE
        # ==========================================
        vix_ticker = yf.Ticker("^VIX")
        
        # Get last 30 days of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        vix_hist = vix_ticker.history(start=start_date, end=end_date)
        
        if len(vix_hist) == 0:
            print("⚠️ VIX data unavailable from yfinance")
            return None
        
        # Current VIX level
        vix_current = vix_hist['Close'].iloc[-1]
        
        # Calculate changes
        vix_yesterday = vix_hist['Close'].iloc[-2] if len(vix_hist) > 1 else vix_current
        vix_7d_ago = vix_hist['Close'].iloc[-7] if len(vix_hist) > 7 else vix_current
        vix_30d_ago = vix_hist['Close'].iloc[0]
        
        vix_change_1d = vix_current - vix_yesterday
        vix_change_7d = ((vix_current / vix_7d_ago) - 1) * 100
        vix_change_30d = ((vix_current / vix_30d_ago) - 1) * 100
        
        # Calculate trend (simple moving average)
        vix_sma_7 = vix_hist['Close'].iloc[-7:].mean() if len(vix_hist) >= 7 else vix_current
        
        # Determine trend
        if vix_current > vix_sma_7 * 1.05:
            trend = "RISING"
        elif vix_current < vix_sma_7 * 0.95:
            trend = "FALLING"
        else:
            trend = "STABLE"
        
        print(f"✅ VIX Data Retrieved!")
        print(f"   Current VIX: {vix_current:.2f}")
        print(f"   1D Change: {vix_change_1d:+.2f}")
        print(f"   7D Change: {vix_change_7d:+.2f}%")
        print(f"   Trend: {trend}")
        
        return {
            'vix_current': vix_current,
            'vix_change_1d': vix_change_1d,
            'vix_change_7d': vix_change_7d,
            'vix_change_30d': vix_change_30d,
            'vix_sma_7': vix_sma_7,
            'trend': trend,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"⚠️ VIX fetch error: {e}")
        return None


def calculate_vix_score(vix_data):
    """
    Calculate VIX-based score for crypto risk appetite
    
    VIX LEVELS INTERPRETATION:
    ---------------------------
    < 12: EXTREME COMPLACENCY → Very bullish for crypto (80-90)
    12-15: LOW FEAR → Bullish for crypto (65-80)
    15-20: NORMAL → Neutral (45-65)
    20-25: ELEVATED FEAR → Caution (35-45)
    25-30: HIGH FEAR → Bearish (25-35)
    > 30: EXTREME FEAR/PANIC → Very bearish (10-25)
    
    Returns:
        dict: Score (0-100), signal, interpretation
    """
    if vix_data is None:
        return {
            'available': False,
            'score': 50,
            'signal': 'NEUTRAL',
            'reason': 'VIX data unavailable'
        }
    
    try:
        vix_current = vix_data['vix_current']
        vix_change_7d = vix_data['vix_change_7d']
        trend = vix_data['trend']
        
        # ==========================================
        # BASE SCORE FROM ABSOLUTE VIX LEVEL
        # ==========================================
        
        if vix_current < 12:
            # Extreme complacency
            base_score = 85
            fear_level = "EXTREME_COMPLACENCY"
            interpretation = "Market extremely complacent - Very bullish for crypto"
        elif vix_current < 15:
            # Low fear
            base_score = 72
            fear_level = "LOW_FEAR"
            interpretation = "Low fear environment - Bullish for risk assets"
        elif vix_current < 20:
            # Normal levels
            base_score = 55
            fear_level = "NORMAL"
            interpretation = "Normal market conditions - Neutral sentiment"
        elif vix_current < 25:
            # Elevated fear
            base_score = 40
            fear_level = "ELEVATED_FEAR"
            interpretation = "Elevated fear - Caution recommended"
        elif vix_current < 30:
            # High fear
            base_score = 30
            fear_level = "HIGH_FEAR"
            interpretation = "High fear in markets - Bearish for crypto"
        else:
            # Extreme fear/panic
            base_score = 20
            fear_level = "EXTREME_FEAR"
            interpretation = "Market panic mode - Very bearish for crypto"
        
        # ==========================================
        # ADJUST FOR TREND
        # ==========================================
        
        # Rising VIX = increasing fear = bad for crypto
        # Falling VIX = decreasing fear = good for crypto
        
        if trend == "RISING":
            trend_adjustment = -5
        elif trend == "FALLING":
            trend_adjustment = +5
        else:
            trend_adjustment = 0
        
        # Additional adjustment for sharp moves
        if abs(vix_change_7d) > 20:
            # Sharp move in past week
            if vix_change_7d > 0:
                # Sharp increase in fear
                trend_adjustment -= 10
            else:
                # Sharp decrease in fear
                trend_adjustment += 10
        
        # ==========================================
        # FINAL SCORE
        # ==========================================
        
        final_score = base_score + trend_adjustment
        final_score = max(0, min(100, final_score))
        
        # Determine signal
        if final_score >= 70:
            signal = "VERY_BULLISH"
        elif final_score >= 55:
            signal = "BULLISH"
        elif final_score >= 45:
            signal = "NEUTRAL"
        elif final_score >= 30:
            signal = "BEARISH"
        else:
            signal = "VERY_BEARISH"
        
        print(f"✅ VIX Score Calculated!")
        print(f"   Fear Level: {fear_level}")
        print(f"   Score: {final_score:.2f}/100")
        print(f"   Signal: {signal}")
        
        return {
            'available': True,
            'score': round(final_score, 2),
            'vix_current': round(vix_current, 2),
            'vix_change_1d': round(vix_data['vix_change_1d'], 2),
            'vix_change_7d': round(vix_change_7d, 2),
            'vix_change_30d': round(vix_data['vix_change_30d'], 2),
            'fear_level': fear_level,
            'trend': trend,
            'signal': signal,
            'interpretation': interpretation,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"⚠️ VIX score calculation error: {e}")
        return {
            'available': False,
            'score': 50,
            'signal': 'NEUTRAL',
            'reason': str(e)
        }


def get_vix_signal():
    """
    Main function: Get VIX signal (used by ai_brain.py)
    
    Returns:
        dict: {'available': bool, 'score': float, 'signal': str}
    """
    vix_data = get_vix_data()
    result = calculate_vix_score(vix_data)
    
    return {
        'available': result['available'],
        'score': result.get('score', 50),
        'signal': result.get('signal', 'NEUTRAL')
    }


def analyze_vix():
    """
    Complete VIX analysis with detailed output
    """
    print("🔱 VIX FEAR INDEX ANALYSIS - REAL DATA")
    print("=" * 70)
    
    vix_data = get_vix_data()
    
    if vix_data is None:
        print("❌ Unable to fetch VIX data")
        return None
    
    result = calculate_vix_score(vix_data)
    
    print("\n" + "=" * 70)
    print("📊 VIX ANALYSIS COMPLETE:")
    print(f"   VIX Level: {result.get('vix_current', 'N/A')}")
    print(f"   Fear Level: {result.get('fear_level', 'N/A')}")
    print(f"   Trend: {result.get('trend', 'N/A')}")
    print(f"   Score: {result.get('score', 'N/A')}/100")
    print(f"   Signal: {result.get('signal', 'N/A')}")
    print(f"   Interpretation: {result.get('interpretation', 'N/A')}")
    print("=" * 70)
    
    return result


# ============================================================================
# STANDALONE TESTING
# ============================================================================

if __name__ == "__main__":
    result = analyze_vix()
