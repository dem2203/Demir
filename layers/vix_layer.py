# ===========================================
# vix_layer.py v4.2 - SYMBOL PARAMETER ADDED
# ===========================================
# ✅ FIXED: symbol parameter added to all functions
# ✅ api_cache_manager entegrasyonu
# ✅ Multi-source fallback (Twelve Data → yfinance)
# ✅ 15 dakika cache
# ✅ Graceful degradation
# ===========================================

"""
🔱 DEMIR AI TRADING BOT - VIX Layer v4.2 (SYMBOL PARAMETER FIXED!)
====================================================================
Tarih: 4 Kasım 2025, 21:26 CET
Versiyon: 4.2 - Symbol parameter added

✅ YENİ v4.2:
------------
✅ symbol parameter added to calculate_vix_fear() and get_vix_signal()
✅ Default value: symbol="BTC" for backward compatibility

YENİ v4.0:
----------
✅ api_cache_manager entegrasyonu
✅ Multi-source (Twelve Data → yfinance)
✅ 15 dakika cache (rate limit koruması)
✅ Health monitoring
✅ Fallback chain
"""

import os
import requests
from datetime import datetime
from typing import Dict, Any

# API Cache Manager import (YENİ!)
try:
    from api_cache_manager import APICache
    cache = APICache()
    CACHE_AVAILABLE = True
    print("✅ api_cache_manager loaded successfully")
except ImportError:
    CACHE_AVAILABLE = False
    print("⚠️ api_cache_manager not available, caching disabled")

def fetch_vix_twelvedata(symbol="BTC"):
    """
    Twelve Data'dan VIX çeker (Primary source)
    Args:
        symbol: Trading pair symbol (for context)
    Returns:
        dict: VIX data or None
    """
    api_key = os.getenv('TWELVE_DATA_API_KEY')
    if not api_key:
        print(f"⚠️ TWELVE_DATA_API_KEY not set for {symbol}")
        return None

    # Cache kontrolü
    if CACHE_AVAILABLE:
        cached = cache.get('vix', 'twelvedata')
        if cached:
            print(f"✅ VIX (Twelve Data) - using cache for {symbol}")
            return cached

    try:
        url = "https://api.twelvedata.com/price"
        params = {
            'symbol': 'VIX',
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'price' in data:
            vix_value = float(data['price'])
            result = {
                'value': vix_value,
                'source': 'twelvedata',
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache'e kaydet
            if CACHE_AVAILABLE:
                cache.set('vix', 'twelvedata', result)
                print(f"✅ VIX cached (Twelve Data) for {symbol}")
            
            return result
        else:
            print(f"⚠️ Twelve Data VIX: No price data for {symbol}")
            return None
            
    except Exception as e:
        print(f"⚠️ Twelve Data VIX error for {symbol}: {e}")
        return None

def fetch_vix_yfinance(symbol="BTC"):
    """
    yfinance'den VIX çeker (Fallback source)
    Args:
        symbol: Trading pair symbol (for context)
    Returns:
        dict: VIX data or None
    """
    try:
        import yfinance as yf
        
        # Cache kontrolü
        if CACHE_AVAILABLE:
            cached = cache.get('vix', 'yfinance')
            if cached:
                print(f"✅ VIX (yfinance) - using cache for {symbol}")
                return cached
        
        ticker = yf.Ticker("^VIX")
        data = ticker.history(period="1d")
        
        if not data.empty:
            vix_value = float(data['Close'].iloc[-1])
            result = {
                'value': vix_value,
                'source': 'yfinance',
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache'e kaydet
            if CACHE_AVAILABLE:
                cache.set('vix', 'yfinance', result)
                print(f"✅ VIX cached (yfinance) for {symbol}")
            
            return result
        else:
            print(f"⚠️ yfinance VIX: No data available for {symbol}")
            return None
            
    except ImportError:
        print(f"⚠️ yfinance not installed for {symbol}")
        return None
    except Exception as e:
        print(f"⚠️ yfinance VIX error for {symbol}: {e}")
        return None

def calculate_vix_fear(symbol="BTC"):
    """
    VIX Fear Index hesapla ve crypto correlation analiz et
    Args:
        symbol: Trading pair symbol (e.g., "BTCUSDT")
    Returns score 0-100:
        - 100 = Extreme fear (VIX very high, risk-off)
        - 50 = Normal market (VIX moderate)
        - 0 = Complacency (VIX very low, risk-on)
    """
    try:
        print(f"\n📊 Analyzing VIX Fear Index for {symbol} (REAL DATA)...")
        
        # Try primary source: Twelve Data
        vix_data = fetch_vix_twelvedata(symbol)
        
        # Fallback: yfinance
        if not vix_data:
            print(f"⚠️ Twelve Data failed for {symbol}, trying yfinance...")
            vix_data = fetch_vix_yfinance(symbol)
        
        # Both failed
        if not vix_data:
            print(f"❌ All VIX sources failed for {symbol}")
            return {'available': False, 'score': 50, 'reason': 'All sources failed'}
        
        vix_value = vix_data['value']
        source = vix_data['source']
        
        print(f"✅ Using VIX from {source} for {symbol}: {vix_value:.2f}")
        
        # ==========================================
        # VIX INTERPRETATION
        # ==========================================
        # Historical VIX levels:
        # - <12: Extreme complacency (2017, 2019 lows)
        # - 12-20: Normal/low volatility
        # - 20-30: Elevated fear
        # - 30-40: High fear (2020 COVID start)
        # - >40: Extreme fear/panic (2008, 2020 peak ~80)
        
        if vix_value > 40:
            fear_level = "EXTREME_PANIC"
            base_score = 95
            interpretation = "Extreme market panic - flight to safety"
        elif vix_value > 30:
            fear_level = "HIGH_FEAR"
            base_score = 80
            interpretation = "High fear - significant risk aversion"
        elif vix_value > 20:
            fear_level = "ELEVATED_FEAR"
            base_score = 65
            interpretation = "Elevated fear - cautious sentiment"
        elif vix_value > 15:
            fear_level = "MODERATE"
            base_score = 50
            interpretation = "Moderate volatility - normal conditions"
        elif vix_value > 12:
            fear_level = "LOW_FEAR"
            base_score = 35
            interpretation = "Low fear - risk-on sentiment"
        else:
            fear_level = "COMPLACENCY"
            base_score = 20
            interpretation = "Extreme complacency - potential reversal risk"
        
        # ==========================================
        # CRYPTO CORRELATION
        # ==========================================
        # VIX and crypto typically INVERSELY correlated:
        # - High VIX → Risk-off → Crypto down
        # - Low VIX → Risk-on → Crypto up
        
        if vix_value > 30:
            crypto_impact = "BEARISH"
            impact_desc = "High VIX typically bearish for crypto (risk-off)"
        elif vix_value > 20:
            crypto_impact = "SLIGHTLY_BEARISH"
            impact_desc = "Elevated VIX slightly bearish for crypto"
        elif vix_value > 12:
            crypto_impact = "NEUTRAL"
            impact_desc = "Moderate VIX - neutral for crypto"
        else:
            crypto_impact = "BULLISH"
            impact_desc = "Low VIX typically bullish for crypto (risk-on)"
        
        score = base_score
        
        print(f"✅ VIX Analysis Complete for {symbol}!")
        print(f"   VIX Value: {vix_value:.2f}")
        print(f"   Fear Level: {fear_level}")
        print(f"   Crypto Impact: {crypto_impact}")
        print(f"   Score: {score:.2f}/100")
        
        return {
            'available': True,
            'score': round(score, 2),
            'vix_value': round(vix_value, 2),
            'fear_level': fear_level,
            'crypto_impact': crypto_impact,
            'interpretation': interpretation,
            'impact_description': impact_desc,
            'source': source,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"⚠️ VIX calculation error for {symbol}: {e}")
        return {'available': False, 'score': 50, 'reason': str(e)}

def get_vix_signal(symbol="BTC"):
    """
    Simplified wrapper for VIX signal (used by ai_brain.py)
    Args:
        symbol: Trading pair symbol (e.g., "BTCUSDT")
    Returns:
        dict: Signal with score and availability
    """
    result = calculate_vix_fear(symbol)
    
    if result['available']:
        return {
            'available': True,
            'score': result['score'],
            'signal': result.get('fear_level', 'MODERATE')
        }
    else:
        return {
            'available': False,
            'score': 50,
            'signal': 'MODERATE'
        }

# ============================================================================
# STANDALONE TESTING
# ============================================================================

if __name__ == "__main__":
    print("📊 VIX FEAR LAYER - REAL DATA TEST")
    print("=" * 70)
    
    result = calculate_vix_fear("BTCUSDT")
    
    print("\n" + "=" * 70)
    print("📊 VIX ANALYSIS:")
    print(f"   Available: {result['available']}")
    print(f"   Score: {result.get('score', 'N/A')}/100")
    print(f"   VIX Value: {result.get('vix_value', 'N/A')}")
    print(f"   Fear Level: {result.get('fear_level', 'N/A')}")
    print(f"   Crypto Impact: {result.get('crypto_impact', 'N/A')}")
    print(f"   Source: {result.get('source', 'N/A')}")
    print("=" * 70)
