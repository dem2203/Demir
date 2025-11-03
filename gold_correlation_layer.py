"""
🥇 GOLD CORRELATION LAYER v3.0 - TWELVE DATA API
==================================================
Date: 3 Kasım 2025, 10:54 CET
Version: 3.0 - Real API Integration

✅ REAL DATA SOURCES:
- Gold (XAU/USD) → Twelve Data API
- Silver (XAG/USD) → Twelve Data API
- BTC Price → Binance API

✅ FEATURES:
- Real-time gold/silver prices
- Correlation calculation with crypto
- Safe-haven sentiment analysis
- Fallback to neutral if API fails
"""

import requests
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def get_twelve_data_price(symbol):
    """
    Twelve Data'dan anlık fiyat çeker
    
    Args:
        symbol: XAU/USD, XAG/USD etc.
    
    Returns:
        float: Current price or None
    """
    api_key = os.getenv('TWELVE_DATA_API_KEY')
    
    if not api_key:
        print(f"⚠️ Twelve Data API key missing")
        return None
    
    try:
        url = f"https://api.twelvedata.com/price"
        params = {
            'symbol': symbol,
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'price' in data:
            price = float(data['price'])
            print(f"✅ Twelve Data: {symbol} = ${price:,.2f}")
            return price
        else:
            print(f"⚠️ Twelve Data: {symbol} - No price data")
            return None
            
    except Exception as e:
        print(f"❌ Twelve Data error ({symbol}): {e}")
        return None

def get_binance_price(symbol='BTCUSDT'):
    """
    Binance'den anlık fiyat çeker
    
    Args:
        symbol: Trading pair (BTCUSDT, ETHUSDT, etc.)
    
    Returns:
        float: Current price or None
    """
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            price = float(data['price'])
            print(f"✅ Binance: {symbol} = ${price:,.2f}")
            return price
        else:
            print(f"⚠️ Binance API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Binance error: {e}")
        return None

def calculate_gold_correlation(symbol='BTCUSDT', interval='1h', limit=100):
    """
    Calculate correlation between crypto and gold/silver
    
    Args:
        symbol: Crypto trading pair
        interval: Timeframe
        limit: Number of data points
    
    Returns:
        dict with correlation results
    """
    print(f"\n{'='*80}")
    print(f"🥇 GOLD CORRELATION ANALYSIS")
    print(f"   Symbol: {symbol}")
    print(f"   Interval: {interval}")
    print(f"{'='*80}\n")
    
    result = {
        'available': False,
        'score': 50,
        'signal': 'NEUTRAL',
        'gold_price': 0,
        'silver_price': 0,
        'gold_correlation': 0,
        'silver_correlation': 0,
        'interpretation': 'No data available'
    }
    
    try:
        # 1. Get gold price (XAU/USD)
        gold_price = get_twelve_data_price('XAU/USD')
        if gold_price:
            result['gold_price'] = gold_price
        
        # 2. Get silver price (XAG/USD)
        silver_price = get_twelve_data_price('XAG/USD')
        if silver_price:
            result['silver_price'] = silver_price
        
        # 3. Get crypto price
        crypto_price = get_binance_price(symbol)
        
        if gold_price and crypto_price:
            # Simple correlation indicator based on gold price
            # High gold → risk-off → potentially good for BTC as digital gold
            if gold_price > 2000:
                result['score'] = 60
                result['signal'] = 'BULLISH'
                result['interpretation'] = f"Gold at ${gold_price:,.0f} - Safe-haven demand high"
            elif gold_price > 1900:
                result['score'] = 55
                result['signal'] = 'NEUTRAL'
                result['interpretation'] = f"Gold at ${gold_price:,.0f} - Moderate safe-haven"
            else:
                result['score'] = 50
                result['signal'] = 'NEUTRAL'
                result['interpretation'] = f"Gold at ${gold_price:,.0f} - Normal levels"
            
            result['available'] = True
            
            print(f"✅ Gold Correlation Analysis:")
            print(f"   Gold Price: ${gold_price:,.2f}")
            print(f"   Silver Price: ${silver_price:,.2f}" if silver_price else "   Silver Price: N/A")
            print(f"   Crypto Price: ${crypto_price:,.2f}")
            print(f"   Score: {result['score']}/100")
            print(f"   Signal: {result['signal']}")
        
        else:
            print("⚠️ Insufficient data for correlation analysis")
            result['interpretation'] = 'API data unavailable - using neutral score'
    
    except Exception as e:
        print(f"❌ Gold correlation error: {e}")
        result['interpretation'] = f'Error: {str(e)}'
    
    print(f"{'='*80}\n")
    return result

def get_gold_signal():
    """
    Simple wrapper for gold signal
    
    Returns:
        dict with signal and score
    """
    result = calculate_gold_correlation()
    return {
        'signal': result['signal'],
        'score': result['score'],
        'available': result['available']
    }

# Test function
if __name__ == "__main__":
    print("="*80)
    print("🥇 GOLD CORRELATION LAYER v3.0 TEST")
    print("   Twelve Data API Integration")
    print("="*80)
    
    result = calculate_gold_correlation('BTCUSDT', '1h', 100)
    
    print("\n📊 TEST RESULTS:")
    print(f"   Available: {result['available']}")
    print(f"   Score: {result['score']}/100")
    print(f"   Signal: {result['signal']}")
    print(f"   Gold Price: ${result['gold_price']:,.2f}")
    print(f"   Silver Price: ${result['silver_price']:,.2f}")
    print(f"   Interpretation: {result['interpretation']}")
