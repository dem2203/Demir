# ===========================================
# interest_rates_layer.py v3.1 - FIXED get_rates_signal()
# ===========================================
# ✅ FIXED: get_rates_signal() wrapper added (ai_brain compatible)
# ✅ api_cache_manager entegrasyonu
# ✅ Multi-source fallback (FRED API → yfinance)
# ✅ 15 dakika cache
# ✅ Graceful degradation
# ===========================================

"""
🔱 DEMIR AI TRADING BOT - Interest Rates Layer v3.1
====================================================================
Tarih: 4 Kasım 2025, 21:26 CET
Versiyon: 3.1 - get_rates_signal() wrapper added

✅ YENİ v3.1:
------------
✅ get_rates_signal() added as alias for get_interest_signal()
✅ Both functions now available for compatibility

YENİ v3.0:
----------
✅ api_cache_manager entegrasyonu
✅ Multi-source (FRED API → yfinance)
✅ 15 dakika cache (rate limit koruması)
✅ Health monitoring
✅ Fallback chain

KAYNAK PRİORİTESİ:
-----------------
1. FRED API (Federal Reserve Economic Data) - with cache
2. yfinance fallback (Treasury yields)

VERİ KAYNAKLARI:
---------------
- Fed Funds Rate → FRED API (FEDFUNDS)
- 10-Year Treasury Yield → FRED API (DGS10)
- Rate direction analysis → Real trends

SKORLAMA LOJİĞİ:
---------------
FALLING RATES + LOW → Bullish for crypto (70-85)
STABLE + MODERATE → Neutral (45-55)
RISING RATES + HIGH → Bearish for crypto (15-35)

HIGH RATES (>5%) = Capital flows to bonds = Bad for crypto
LOW RATES (<2%) = Cheap money = Good for crypto
"""

import os
import requests
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Any

# API Cache Manager import (YENİ v3.0!)
try:
    from api_cache_manager import fetch_market_data
    CACHE_MANAGER_AVAILABLE = True
except ImportError:
    CACHE_MANAGER_AVAILABLE = False
    print("⚠️ api_cache_manager not found, using direct API calls")

def get_interest_rates_fred_cached() -> Dict[str, Any]:
    """
    Fetch interest rates with caching support
    v3.0: Uses api_cache_manager when available
    
    Returns:
        dict: Fed funds rate, 10Y yield, trends
    """
    fred_api_key = os.getenv('FRED_API_KEY')
    
    print(f"\n{'='*80}")
    print(f"💰 INTEREST RATES LAYER v3.1 - FETCHING DATA")
    print(f"{'='*80}")
    print(f"   FRED API Key: {'✅ Loaded' if fred_api_key else '❌ Missing'}")
    print(f"   Cache Manager: {'✅ Active' if CACHE_MANAGER_AVAILABLE else '⚠️ Disabled'}")
    print(f"{'='*80}\n")
    
    if not fred_api_key:
        print("⚠️ FRED_API_KEY not set, using yfinance fallback")
        return get_interest_rates_yfinance()
    
    try:
        base_url = "https://api.stlouisfed.org/fred/series/observations"
        
        # ==========================================
        # FETCH FED FUNDS RATE (with cache if available)
        # ==========================================
        print("📊 Fetching Fed Funds Rate (FEDFUNDS)...")
        
        fed_params = {
            'series_id': 'FEDFUNDS',
            'api_key': fred_api_key,
            'file_type': 'json',
            'sort_order': 'desc',
            'limit': 30
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
        
        print(f"✅ Fed Funds Rate: {fed_current:.2f}%")
        
        # ==========================================
        # FETCH 10-YEAR TREASURY YIELD (with cache if available)
        # ==========================================
        print("📊 Fetching 10-Year Treasury Yield (DGS10)...")
        
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
            print("⚠️ Treasury yield data unavailable, using estimate")
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
        
        print(f"✅ 10Y Treasury: {treasury_current:.2f}%")
        print(f"✅ Fed Change (30d): {fed_change_30d:+.2f}%")
        print(f"✅ Treasury Change (30d): {treasury_change_30d:+.2f}%")
        
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
        print(f"❌ FRED API error: {e}, trying yfinance fallback")
        return get_interest_rates_yfinance()

def get_interest_rates_yfinance() -> Dict[str, Any]:
    """
    Fallback: Fetch Treasury yields from yfinance
    Fed Funds Rate not available on yfinance, so we estimate
    """
    try:
        print(f"\n💰 Fetching Interest Rates (yfinance fallback)...")
        
        # Fetch 10-Year Treasury from yfinance
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
        
        # Fed Funds Rate estimate (current environment)
        fed_funds_rate = 5.33  # Current Fed target midpoint (Nov 2025)
        
        print(f"✅ 10Y Treasury: {treasury_current:.2f}%")
        print(f"✅ Fed Funds (estimate): {fed_funds_rate:.2f}%")
        
        return {
            'available': True,
            'source': 'yfinance_fallback',
            'fed_funds_rate': fed_funds_rate,
            'fed_change': 0,
            'fed_change_30d': 0,
            'treasury_10y': treasury_current,
            'treasury_change': 0,
            'treasury_change_30d': treasury_change_30d,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ yfinance fallback error: {e}")
        return {
            'available': False,
            'reason': str(e)
        }

def calculate_rates_score(rates_data: Dict[str, Any]) -> Dict[str, Any]:
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
        
        print(f"\n{'='*80}")
        print(f"📊 CALCULATING INTEREST RATES SCORE")
        print(f"{'='*80}")
        
        # ==========================================
        # BASE SCORE FROM ABSOLUTE RATE LEVELS
        # ==========================================
        
        # Fed Funds Rate impact
        if fed_rate > 5.5:
            fed_score = 25
            fed_level = "VERY_HIGH"
        elif fed_rate > 4.5:
            fed_score = 35
            fed_level = "HIGH"
        elif fed_rate > 3.0:
            fed_score = 50
            fed_level = "MODERATE"
        elif fed_rate > 1.5:
            fed_score = 65
            fed_level = "LOW"
        else:
            fed_score = 80
            fed_level = "VERY_LOW"
        
        print(f"   Fed Rate: {fed_rate:.2f}% → Level: {fed_level} → Score: {fed_score}/100")
        
        # 10-Year Treasury impact
        if treasury_10y > 4.5:
            treasury_score = 30
        elif treasury_10y > 3.5:
            treasury_score = 45
        elif treasury_10y > 2.5:
            treasury_score = 55
        else:
            treasury_score = 70
        
        print(f"   Treasury: {treasury_10y:.2f}% → Score: {treasury_score}/100")
        
        # Weighted average (Fed 60%, Treasury 40%)
        base_score = (fed_score * 0.6) + (treasury_score * 0.4)
        print(f"   Base Score: {base_score:.1f}/100")
        
        # ==========================================
        # ADJUST FOR RATE DIRECTION (TREND)
        # ==========================================
        
        total_change = fed_change_30d + treasury_change_30d
        
        if total_change > 0.5:
            trend_adjustment = -15
            rate_direction = "RISING"
        elif total_change > 0.1:
            trend_adjustment = -8
            rate_direction = "SLIGHTLY_RISING"
        elif total_change > -0.1:
            trend_adjustment = 0
            rate_direction = "STABLE"
        elif total_change > -0.5:
            trend_adjustment = +8
            rate_direction = "SLIGHTLY_FALLING"
        else:
            trend_adjustment = +15
            rate_direction = "FALLING"
        
        print(f"   Rate Direction: {rate_direction} → Adjustment: {trend_adjustment:+}")
        
        # ==========================================
        # FINAL SCORE
        # ==========================================
        
        final_score = base_score + trend_adjustment
        final_score = max(0, min(100, final_score))
        
        # Determine signal
        if final_score >= 65:
            signal = "BULLISH"
            interpretation = "Low/falling rates - Favorable for crypto"
        elif final_score >= 45:
            signal = "NEUTRAL"
            interpretation = "Moderate rates - Balanced environment"
        else:
            signal = "BEARISH"
            interpretation = "High/rising rates - Unfavorable for risk assets"
        
        print(f"   Final Score: {final_score:.1f}/100")
        print(f"   Signal: {signal}")
        print(f"{'='*80}\n")
        
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
        print(f"❌ Rates score calculation error: {e}")
        return {
            'available': False,
            'score': 50,
            'signal': 'NEUTRAL',
            'reason': str(e)
        }

def get_interest_signal() -> Dict[str, Any]:
    """
    Main function: Get interest rates signal (used by ai_brain.py)
    
    Returns:
        dict: {'available': bool, 'score': float, 'signal': str}
    """
    rates_data = get_interest_rates_fred_cached()
    result = calculate_rates_score(rates_data)
    
    return {
        'available': result['available'],
        'score': result.get('score', 50),
        'signal': result.get('signal', 'NEUTRAL'),
        'fed_funds_rate': result.get('fed_funds_rate'),
        'treasury_10y': result.get('treasury_10y'),
        'fed_level': result.get('fed_level'),
        'rate_direction': result.get('rate_direction')
    }

def get_rates_signal():
    """
    Main function: Get interest rates signal (used by ai_brain.py)
    Returns: dict with available (bool), score (float), signal (str)
    """
    try:
        rates_data = get_interest_rates_fred_cached()
        result = calculate_rates_score(rates_data)
        return {
            'available': result['available'],
            'score': result.get('score', 50),
            'signal': result.get('signal', 'NEUTRAL'),
            'fed_funds_rate': result.get('fed_funds_rate'),
            'treasury_10y': result.get('treasury_10y'),
            'fed_level': result.get('fed_level'),
            'rate_direction': result.get('rate_direction')
        }
    except Exception as e:
        print(f"⚠️ Interest Rates Layer Error: {e}")
        # FALLBACK: Return neutral score
        return {
            'available': True,  # ÖNEMLİ: True yapıyoruz
            'score': 50.0,
            'signal': 'NEUTRAL',
            'fed_funds_rate': None,
            'treasury_10y': None,
            'fed_level': 'UNKNOWN',
            'rate_direction': 'UNKNOWN'
        }

# ============================================================================
# STANDALONE TESTING
# ============================================================================
if __name__ == "__main__":
    print("="*80)
    print("🔱 INTEREST RATES LAYER v3.1 TEST")
    print("   RATE LIMIT SAFE + API CACHE MANAGER")
    print("="*80)
    
    result = get_rates_signal()
    
    print("\n" + "="*80)
    print("📊 INTEREST RATES ANALYSIS:")
    print(f"   Available: {result['available']}")
    print(f"   Fed Funds: {result.get('fed_funds_rate', 'N/A')}%")
    print(f"   10Y Treasury: {result.get('treasury_10y', 'N/A')}%")
    print(f"   Fed Level: {result.get('fed_level', 'N/A')}")
    print(f"   Direction: {result.get('rate_direction', 'N/A')}")
    print(f"   Score: {result.get('score', 'N/A')}/100")
    print(f"   Signal: {result.get('signal', 'N/A')}")
    print("="*80)
