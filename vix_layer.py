"""
😱 VIX FEAR INDEX LAYER v3.0 - TWELVE DATA API
================================================
Date: 3 Kasım 2025, 10:55 CET
Version: 3.0 - Real API Integration

✅ REAL DATA SOURCES:
- VIX Index → Twelve Data API
- CBOE Volatility Index (^VIX)

✅ FEATURES:
- Real-time VIX levels
- Fear/Greed sentiment analysis
- Crypto correlation scoring
- Fallback to neutral if API fails
"""

import requests
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def get_vix_from_twelve_data():
    """
    Twelve Data'dan VIX indexini çeker
    
    Returns:
        float: Current VIX level or None
    """
    api_key = os.getenv('TWELVE_DATA_API_KEY')
    
    if not api_key:
        print(f"⚠️ Twelve Data API key missing")
        return None
    
    try:
        url = f"https://api.twelvedata.com/price"
        params = {
            'symbol': 'VIX',
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'price' in data:
            vix = float(data['price'])
            print(f"✅ Twelve Data: VIX = {vix:.2f}")
            return vix
        else:
            print(f"⚠️ Twelve Data: VIX - No price data")
            return None
            
    except Exception as e:
        print(f"❌ Twelve Data VIX error: {e}")
        return None

def analyze_vix():
    """
    Analyze VIX and return crypto market implications
    
    Returns:
        dict with VIX analysis results
    """
    print(f"\n{'='*80}")
    print(f"😱 VIX FEAR INDEX ANALYSIS")
    print(f"{'='*80}\n")
    
    result = {
        'available': False,
        'score': 50,
        'signal': 'NEUTRAL',
        'vix_current': 0,
        'fear_level': 'UNKNOWN',
        'crypto_implication': 'No data',
        'interpretation': 'VIX data unavailable'
    }
    
    try:
        # Get VIX from Twelve Data
        vix = get_vix_from_twelve_data()
        
        if vix is None:
            print("⚠️ VIX data unavailable - using neutral score")
            return result
        
        result['vix_current'] = vix
        result['available'] = True
        
        # Scoring logic based on VIX levels
        # Lower VIX = less fear = better for risk assets like crypto
        if vix < 12:
            result['score'] = 75
            result['signal'] = 'BULLISH'
            result['fear_level'] = 'EXTREME_GREED'
            result['crypto_implication'] = 'Very bullish for crypto - low market fear'
        elif vix < 15:
            result['score'] = 70
            result['signal'] = 'BULLISH'
            result['fear_level'] = 'GREED'
            result['crypto_implication'] = 'Bullish for crypto - calm markets'
        elif vix < 20:
            result['score'] = 60
            result['signal'] = 'BULLISH'
            result['fear_level'] = 'LOW_FEAR'
            result['crypto_implication'] = 'Slightly bullish - normal volatility'
        elif vix < 25:
            result['score'] = 50
            result['signal'] = 'NEUTRAL'
            result['fear_level'] = 'NEUTRAL'
            result['crypto_implication'] = 'Neutral - moderate volatility'
        elif vix < 30:
            result['score'] = 40
            result['signal'] = 'BEARISH'
            result['fear_level'] = 'FEAR'
            result['crypto_implication'] = 'Bearish - elevated fear'
        elif vix < 40:
            result['score'] = 30
            result['signal'] = 'BEARISH'
            result['fear_level'] = 'HIGH_FEAR'
            result['crypto_implication'] = 'Very bearish - high market fear'
        else:
            result['score'] = 20
            result['signal'] = 'BEARISH'
            result['fear_level'] = 'EXTREME_FEAR'
            result['crypto_implication'] = 'Extremely bearish - panic levels'
        
        result['interpretation'] = f"VIX at {vix:.2f} indicates {result['fear_level']} - {result['crypto_implication']}"
        
        print(f"✅ VIX Analysis:")
        print(f"   Current VIX: {vix:.2f}")
        print(f"   Fear Level: {result['fear_level']}")
        print(f"   Score: {result['score']}/100")
        print(f"   Signal: {result['signal']}")
        print(f"   Crypto Impact: {result['crypto_implication']}")
    
    except Exception as e:
        print(f"❌ VIX analysis error: {e}")
        result['interpretation'] = f"Error: {str(e)}"
    
    print(f"{'='*80}\n")
    return result

def get_vix_signal():
    """
    Simple wrapper for VIX signal
    
    Returns:
        dict with signal and score
    """
    result = analyze_vix()
    return {
        'signal': result['signal'],
        'score': result['score'],
        'available': result['available'],
        'vix_current': result['vix_current']
    }

# Test function
if __name__ == "__main__":
    print("="*80)
    print("😱 VIX FEAR INDEX LAYER v3.0 TEST")
    print("   Twelve Data API Integration")
    print("="*80)
    
    result = analyze_vix()
    
    print("\n📊 TEST RESULTS:")
    print(f"   Available: {result['available']}")
    print(f"   Score: {result['score']}/100")
    print(f"   Signal: {result['signal']}")
    print(f"   VIX Level: {result['vix_current']:.2f}")
    print(f"   Fear Level: {result['fear_level']}")
    print(f"   Crypto Impact: {result['crypto_implication']}")
    print(f"   Interpretation: {result['interpretation']}")
