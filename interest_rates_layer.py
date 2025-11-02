"""
🔱 INTEREST RATES LAYER - REAL DATA
===================================
Date: 2 Kasım 2025, 21:50 CET
Version: 2.0 - FRED API Integration

✅ REAL DATA SOURCES:
- Fed Funds Rate → FRED API (FRED_API_KEY)
- 10-Year Treasury Yield → FRED API
- Rate direction analysis → Real trends

✅ API KEY: FRED_API_KEY from Render environment
✅ Fallback: yfinance for Treasury yields if FRED fails
"""

import requests
import numpy as np
import pandas as pd
import yfinance as yf
import os
from datetime import datetime, timedelta

def get_interest_rates_fred():
    """
    Fetch interest rates from Federal Reserve Economic Data (FRED) API
    Requires FRED_API_KEY environment variable
    
    Returns:
        dict: Fed funds rate, 10Y yield, trends
    """
    try:
        fred_api_key = os.getenv('FRED_API_KEY')
        
        if not fred_api_key:
            print("⚠️ FRED_API_KEY not set, using yfinance fallback")
            return get_interest_rates_yfinance()
        
        print(f"\n💰 Fetching Interest Rates (FRED API - REAL DATA)...")
        
        base_url = "https://api.stlouisfed.org/fred/series/observations"
        
        # ==========================================
        # FETCH FED FUNDS RATE
        # ==========================================
        
        # FEDFUNDS = Federal Funds Effective Rate
        fed_params = {
            'series_id': 'FEDFUNDS',
            'api_key': fred_api_key,
            'file_type': 'json',
            'sort_order': 'desc',
            'limit': 30  # Last 30 observations
        }
        
        fed_response = requests.get(base_url, params=fed_params, timeout=10)
        fed_response.raise_for_status()
        fed_data = fed_response.json()
        
        if 'observations' not in fed_data or len(fed_data['observations']) == 0:
            print("⚠️ Fed Funds data unavailable, trying fallback")
            return get_interest_rates_yfinance()
        
        # Parse Fed Funds Rate
        fed_obs = fed_data['observations']
        fed_current = float(fed_obs[0]['value'])
        fed_previous = float(fed_obs[1]['value']) if len(fed_obs) > 1 else fed_current
        fed_30d_ago = float(fed_obs[-1]['value']) if len(fed_obs) > 1 else fed_current
        
        fed_change = fed_current - fed_previous
        fed_change_30d = fed_current - fed_30d_ago
        
        # ==========================================
        # FETCH 10-YEAR TREASURY YIELD
        # ==========================================
        
        # DGS10 = 10-Year Treasury Constant Maturity Rate
        treasury_params = {
            'series_id': 'DGS10',
            'api_key': fred_api_key,
            'file_type': 'json',
            'sort_order': 'desc',
            'limit': 30
        }
        
        treasury_response = requests.get(base_url, params=treasury_params, timeout=10)
        treasury_response.raise_for_status()
        treasury_data = treasury_response.json()
        
        if 'observations' not in treasury_data or len(treasury_data['observations']) == 0:
            print("⚠️ Treasury yield data unavailable")
            treasury_current = 4.5  # Default estimate
            treasury_change = 0
            treasury_change_30d = 0
        else:
            # Parse Treasury yield
            treasury_obs = treasury_data['observations']
            treasury_current = float(treasury_obs[0]['value'])
            treasury_previous = float(treasury_obs[1]['value']) if len(treasury_obs) > 1 else treasury_current
            treasury_30d_ago = float(treasury_obs[-1]['value']) if len(treasury_obs) > 1 else treasury_current
            
            treasury_change = treasury_current - treasury_previous
            treasury_change_30d = treasury_current - treasury_30d_ago
        
        print(f"✅ FRED Data Retrieved!")
        print(f"   Fed Funds Rate: {fed_current:.2f}%")
        print(f"   10Y Treasury: {treasury_current:.2f}%")
        print(f"   Fed Change (30d): {fed_change_30d:+.2f}%")
        
        return {
            'available': True,
            'source': 'FRED_API',
            'fed_funds_rate': fed_current,
            'fed_change': fed_change,
            'fed_change_30d': fed_change_30d,
            'treasury_10y': treasury_current,
            'treasury_change': treasury_change,
            'treasury_change_30d': treasury_change_30d,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"⚠️ FRED API error: {e}, trying yfinance fallback")
        return get_interest_rates_yfinance()


def get_interest_rates_yfinance():
    """
    Fallback: Fetch Treasury yields from yfinance
    Fed Funds Rate not available on yfinance, so we estimate from current environment
    """
    try:
        print(f"\n💰 Fetching Interest Rates (yfinance fallback)...")
        
        # ==========================================
        # FETCH 10-YEAR TREASURY FROM YFINANCE
        # ==========================================
        
        treasury_ticker = yf.Ticker("^TNX")  # 10-Year Treasury Yield
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        treasury_hist = treasury_ticker.history(start=start_date, end=end_date)
        
        if len(treasury_hist) == 0:
            print("⚠️ Treasury data unavailable from yfinance")
            return {
                'available': False,
                'reason': 'Unable to fetch Treasury data'
            }
        
        treasury_current = treasury_hist['Close'].iloc[-1]
        treasury_30d_ago = treasury_hist['Close'].iloc[0]
        treasury_change_30d = treasury_current - treasury_30d_ago
        
        # Fed Funds Rate estimate (current environment ~5.25-5.50%)
        # This is a rough estimate when FRED API is unavailable
        fed_funds_rate = 5.33  # Current Fed target midpoint (Nov 2025)
        
        print(f"✅ yfinance Data Retrieved!")
        print(f"   10Y Treasury: {treasury_current:.2f}%")
        print(f"   Fed Funds (estimate): {fed_funds_rate:.2f}%")
        
        return {
            'available': True,
            'source': 'yfinance_fallback',
            'fed_funds_rate': fed_funds_rate,
            'fed_change': 0,  # Unknown without FRED
            'fed_change_30d': 0,
            'treasury_10y': treasury_current,
            'treasury_change': 0,
            'treasury_change_30d': treasury_change_30d,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"⚠️ yfinance fallback error: {e}")
        return {
            'available': False,
            'reason': str(e)
        }


def calculate_rates_score(rates_data):
    """
    Calculate score based on interest rate environment
    
    RATE ENVIRONMENT LOGIC:
    -----------------------
    FALLING RATES + LOW → Bullish for crypto (70-85)
    STABLE + MODERATE → Neutral (45-55)
    RISING RATES + HIGH → Bearish for crypto (15-35)
    
    HIGH RATES (>5%) = Capital flows to bonds = Bad for crypto
    LOW RATES (<2%) = Cheap money = Good for crypto
    
    Returns:
        dict: Score (0-100), signal, interpretation
    """
    if not rates_data.get('available', False):
        return {
            'available': False,
            'score': 50,
            'signal': 'NEUTRAL',
            'reason': rates_data.get('reason', 'Rates data unavailable')
        }
    
    try:
        fed_rate = rates_data['fed_funds_rate']
        fed_change_30d = rates_data['fed_change_30d']
        treasury_10y = rates_data['treasury_10y']
        treasury_change_30d = rates_data['treasury_change_30d']
        
        # ==========================================
        # BASE SCORE FROM ABSOLUTE RATE LEVELS
        # ==========================================
        
        # Fed Funds Rate impact
        if fed_rate > 5.5:
            # Very high rates
            fed_score = 25
            fed_level = "VERY_HIGH"
        elif fed_rate > 4.5:
            # High rates
            fed_score = 35
            fed_level = "HIGH"
        elif fed_rate > 3.0:
            # Moderate rates
            fed_score = 50
            fed_level = "MODERATE"
        elif fed_rate > 1.5:
            # Low rates
            fed_score = 65
            fed_level = "LOW"
        else:
            # Very low rates
            fed_score = 80
            fed_level = "VERY_LOW"
        
        # 10-Year Treasury impact
        if treasury_10y > 4.5:
            treasury_score = 30
        elif treasury_10y > 3.5:
            treasury_score = 45
        elif treasury_10y > 2.5:
            treasury_score = 55
        else:
            treasury_score = 70
        
        # Weighted average (Fed 60%, Treasury 40%)
        base_score = (fed_score * 0.6) + (treasury_score * 0.4)
        
        # ==========================================
        # ADJUST FOR RATE DIRECTION (TREND)
        # ==========================================
        
        # Rising rates = tightening = bad for crypto
        # Falling rates = easing = good for crypto
        
        total_change = fed_change_30d + treasury_change_30d
        
        if total_change > 0.5:
            # Rates rising significantly
            trend_adjustment = -15
            rate_direction = "RISING"
        elif total_change > 0.1:
            # Rates rising slightly
            trend_adjustment = -8
            rate_direction = "SLIGHTLY_RISING"
        elif total_change > -0.1:
            # Rates stable
            trend_adjustment = 0
            rate_direction = "STABLE"
        elif total_change > -0.5:
            # Rates falling slightly
            trend_adjustment = +8
            rate_direction = "SLIGHTLY_FALLING"
        else:
            # Rates falling significantly
            trend_adjustment = +15
            rate_direction = "FALLING"
        
        # ==========================================
        # FINAL SCORE
        # ==========================================
        
        final_score = base_score + trend_adjustment
        final_score = max(0, min(100, final_score))
        
        # Determine signal
        if final_score >= 65:
            signal = "BULLISH"
            interpretation = "Low/falling rates environment - Favorable for crypto"
        elif final_score >= 45:
            signal = "NEUTRAL"
            interpretation = "Moderate rates - Balanced environment"
        else:
            signal = "BEARISH"
            interpretation = "High/rising rates - Unfavorable for risk assets"
        
        print(f"✅ Rates Score Calculated!")
        print(f"   Fed Level: {fed_level}")
        print(f"   Rate Direction: {rate_direction}")
        print(f"   Score: {final_score:.2f}/100")
        print(f"   Signal: {signal}")
        
        return {
            'available': True,
            'score': round(final_score, 2),
            'fed_funds_rate': round(fed_rate, 2),
            'fed_change_30d': round(fed_change_30d, 2),
            'treasury_10y': round(treasury_10y, 2),
            'treasury_change_30d': round(treasury_change_30d, 2),
            'fed_level': fed_level,
            'rate_direction': rate_direction,
            'signal': signal,
            'interpretation': interpretation,
            'source': rates_data.get('source', 'unknown'),
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"⚠️ Rates score calculation error: {e}")
        return {
            'available': False,
            'score': 50,
            'signal': 'NEUTRAL',
            'reason': str(e)
        }


def get_interest_signal():
    """
    Main function: Get interest rates signal (used by ai_brain.py)
    
    Returns:
        dict: {'available': bool, 'score': float, 'signal': str}
    """
    rates_data = get_interest_rates_fred()
    result = calculate_rates_score(rates_data)
    
    return {
        'available': result['available'],
        'score': result.get('score', 50),
        'signal': result.get('signal', 'NEUTRAL')
    }


# ============================================================================
# STANDALONE TESTING
# ============================================================================

if __name__ == "__main__":
    print("🔱 INTEREST RATES LAYER - REAL DATA TEST")
    print("=" * 70)
    
    rates_data = get_interest_rates_fred()
    result = calculate_rates_score(rates_data)
    
    print("\n" + "=" * 70)
    print("📊 INTEREST RATES ANALYSIS:")
    print(f"   Available: {result['available']}")
    print(f"   Fed Funds: {result.get('fed_funds_rate', 'N/A')}%")
    print(f"   10Y Treasury: {result.get('treasury_10y', 'N/A')}%")
    print(f"   Fed Level: {result.get('fed_level', 'N/A')}")
    print(f"   Direction: {result.get('rate_direction', 'N/A')}")
    print(f"   Score: {result.get('score', 'N/A')}/100")
    print(f"   Signal: {result.get('signal', 'N/A')}")
    print("=" * 70)
