# gold_correlation_layer.py - WITH SOURCE TRACKING (UPDATED)
# 7 Kasım 2025 - v3.1 - Source field eklendi

import requests
import pandas as pd
from typing import Dict, Optional, Any

def get_gold_price() -> Optional[float]:
    """Fetch current gold price from Twelve Data API"""
    try:
        api_key = "YOUR_TWELVE_DATA_API_KEY"  # Set from config
        url = "https://api.twelvedata.com/price"
        params = {
            'symbol': 'XAU/USD',
            'apikey': api_key
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'price' in data:
            return float(data['price'])
        return None
    except Exception as e:
        print(f"Gold Price Error: {e}")
        return None

def get_silver_price() -> Optional[float]:
    """Fetch current silver price from Twelve Data API"""
    try:
        api_key = "YOUR_TWELVE_DATA_API_KEY"
        url = "https://api.twelvedata.com/price"
        params = {
            'symbol': 'XAG/USD',
            'apikey': api_key
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'price' in data:
            return float(data['price'])
        return None
    except Exception as e:
        print(f"Silver Price Error: {e}")
        return None

def get_crypto_price(symbol: str = 'BTCUSDT') -> Optional[float]:
    """Fetch current crypto price from Binance"""
    try:
        url = f'https://api.binance.com/api/v3/ticker/price'
        params = {'symbol': symbol}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'price' in data:
            return float(data['price'])
        return None
    except Exception as e:
        print(f"Crypto Price Error: {e}")
        return None

def calculate_gold_correlation(symbol: str = 'BTCUSDT', interval: str = '1h', limit: int = 100) -> Dict[str, Any]:
    """
    Calculate correlation between gold and crypto
    UPDATED: Added 'source': 'REAL' field
    """
    
    print(f"\n{'='*80}")
    print(f"🥇 GOLD CORRELATION ANALYSIS")
    print(f"   Symbol: {symbol}")
    print(f"   Interval: {interval}")
    print(f"{'='*80}\n")
    
    try:
        # Fetch prices
        gold_price = get_gold_price()
        silver_price = get_silver_price()
        crypto_price = get_crypto_price(symbol)
        
        if not gold_price or not crypto_price:
            print("❌ Failed to fetch price data")
            return {
                'available': False,
                'score': 50,
                'signal': 'NEUTRAL',
                'source': 'ERROR'
            }
        
        print(f"✅ Twelve Data: XAU/USD = ${gold_price:.2f}")
        if silver_price:
            print(f"✅ Twelve Data: XAG/USD = ${silver_price:.2f}")
        else:
            print(f"⚠️ Twelve Data: XAG/USD - No price data")
        
        print(f"✅ Binance: {symbol} = ${crypto_price:.2f}")
        
        # Calculate correlation logic
        # Higher gold prices typically inverse to crypto (safe haven)
        # If gold up 5%+ = crypto risk aversion = score down
        # If gold down = risk appetite = score up
        
        if gold_price > 3950:  # Above recent average
            correlation_signal = 'RISK_OFF'
            score_adjustment = -10  # Less bullish
            signal = 'BEARISH'
        elif gold_price < 3900:
            correlation_signal = 'RISK_ON'
            score_adjustment = +10  # More bullish
            signal = 'BULLISH'
        else:
            correlation_signal = 'NEUTRAL'
            score_adjustment = 0
            signal = 'NEUTRAL'
        
        score = 50 + score_adjustment
        score = max(0, min(100, score))
        
        result = {
            'available': True,
            'score': score,
            'signal': signal,
            'gold_price': round(gold_price, 2),
            'crypto_price': round(crypto_price, 2),
            'correlation': correlation_signal,
            'source': 'REAL'  # ← ADDED: Source tracking
        }
        
        print(f"\n✅ Gold Correlation Analysis:")
        print(f"   Gold Price: ${gold_price:.2f}")
        print(f"   Crypto Price: ${crypto_price:.2f}")
        print(f"   Score: {score}/100")
        print(f"   Signal: {signal}")
        print(f"{'='*80}\n")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            'available': False,
            'score': 50,
            'signal': 'NEUTRAL',
            'error': str(e),
            'source': 'ERROR'
        }

if __name__ == "__main__":
    print("="*80)
    print("🥇 GOLD CORRELATION LAYER v3.1 TEST")
    print("   Twelve Data API Integration")
    print("="*80)
    
    result = calculate_gold_correlation('BTCUSDT', '1h', 100)
    
    print(f"\n📊 Final Result:")
    print(f"   Score: {result['score']}/100")
    print(f"   Signal: {result['signal']}")
    print(f"   Source: {result.get('source', 'UNKNOWN')}")
