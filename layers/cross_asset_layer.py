# cross_asset_layer.py v2.1 - FIXED
# ============================================================================
# 🔱 CROSS-ASSET CORRELATION LAYER - Phase 6.4 FIXED
# ============================================================================
# Date: 4 Kasım 2025, 00:42 CET
# Version: 2.1 - FUNCTION SIGNATURE FIXED
#
# CRITICAL FIX:
# - Added get_cross_asset_signal(symbol) function for ai_brain compatibility
# - Original get_multi_coin_data preserved
# ============================================================================

import requests
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import time

# Import cache manager
try:
    from api_cache_manager import CacheManager
    CACHE_AVAILABLE = True
except:
    CACHE_AVAILABLE = False
    print("⚠️ Cross-Asset: cache_manager not available")

# ============================================================================
# BINANCE DATA FETCHER
# ============================================================================

def fetch_binance_klines(symbol: str, interval: str = '1h', limit: int = 100) -> List[float]:
    """
    Fetch OHLCV data from Binance
    Returns: List of close prices
    """
    try:
        url = f"https://api.binance.com/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract close prices (index 4)
        closes = [float(candle[4]) for candle in data]
        return closes
        
    except Exception as e:
        print(f"❌ Binance fetch error for {symbol}: {e}")
        return []

# ============================================================================
# CORRELATION CALCULATOR
# ============================================================================

def calculate_correlation(prices1: List[float], prices2: List[float]) -> float:
    """
    Calculate Pearson correlation coefficient between two price series
    Returns: -1 to 1 correlation
    """
    try:
        if len(prices1) < 2 or len(prices2) < 2:
            return 0.0
        
        # Ensure same length
        min_len = min(len(prices1), len(prices2))
        prices1 = prices1[-min_len:]
        prices2 = prices2[-min_len:]
        
        # Calculate correlation
        correlation = np.corrcoef(prices1, prices2)[0, 1]
        return float(correlation)
        
    except Exception as e:
        print(f"⚠️ Correlation calc error: {e}")
        return 0.0

# ============================================================================
# PERFORMANCE CALCULATOR
# ============================================================================

def calculate_performance(prices: List[float], periods: int = 24) -> float:
    """
    Calculate % performance over last N periods
    """
    try:
        if len(prices) < periods:
            periods = len(prices)
        
        if periods < 2:
            return 0.0
        
        start_price = prices[-periods]
        end_price = prices[-1]
        
        perf = ((end_price - start_price) / start_price) * 100
        return float(perf)
        
    except Exception as e:
        print(f"⚠️ Performance calc error: {e}")
        return 0.0

# ============================================================================
# MAIN FUNCTION - ORIGINAL
# ============================================================================

def get_multi_coin_data(target_symbol: str = "BTCUSDT", interval: str = '1h') -> Dict[str, Any]:
    """
    Original function - analyzes cross-asset correlations
    
    Args:
        target_symbol: Main coin to analyze (e.g., BTCUSDT, ETHUSDT)
        interval: Timeframe (1h, 4h, 1d)
    
    Returns:
        Dict with correlation data, rotation signals, and score
    """
    print(f"\n💎 Analyzing Cross-Asset Correlations for {target_symbol}...")
    
    # Define asset pairs
    assets = {
        'BTC': 'BTCUSDT',
        'ETH': 'ETHUSDT',
        'LTC': 'LTCUSDT',
        'BNB': 'BNBUSDT'
    }
    
    # Fetch price data for all assets
    asset_data = {}
    for name, symbol in assets.items():
        prices = fetch_binance_klines(symbol, interval=interval, limit=100)
        if prices:
            perf_24h = calculate_performance(prices, periods=24)
            asset_data[name] = {
                'symbol': symbol,
                'prices': prices,
                'current_price': prices[-1] if prices else 0,
                'performance_24h': perf_24h
            }
            print(f" ✅ {name}: ${prices[-1]:.2f} ({perf_24h:+.2f}% 24h)")
        else:
            print(f" ❌ {name}: Data unavailable")
    
    # If target symbol not in default list, fetch it
    target_key = None
    for key, val in assets.items():
        if val == target_symbol:
            target_key = key
            break
    
    if not target_key and target_symbol not in [d['symbol'] for d in asset_data.values()]:
        prices = fetch_binance_klines(target_symbol, interval=interval, limit=100)
        if prices:
            target_key = 'TARGET'
            perf_24h = calculate_performance(prices, periods=24)
            asset_data[target_key] = {
                'symbol': target_symbol,
                'prices': prices,
                'current_price': prices[-1],
                'performance_24h': perf_24h
            }
    
    if not target_key or target_key not in asset_data:
        return {
            'score': 50,
            'signal': 'NEUTRAL',
            'rotation': 'MIXED',
            'correlations': {},
            'error': f'Target symbol {target_symbol} data unavailable'
        }
    
    # Calculate correlations with target
    correlations = {}
    target_prices = asset_data[target_key]['prices']
    for name, data in asset_data.items():
        if name != target_key:
            corr = calculate_correlation(target_prices, data['prices'])
            correlations[name] = corr
            print(f" 📊 Correlation {target_key}-{name}: {corr:.3f}")
    
    # Determine rotation pattern
    target_perf = asset_data[target_key]['performance_24h']
    avg_other_perf = np.mean([d['performance_24h'] for k, d in asset_data.items() if k != target_key])
    
    # Rotation logic
    if target_perf > 2 and target_perf > avg_other_perf + 1:
        rotation = "ROTATING_INTO_TARGET"
        score_base = 75
    elif target_perf < -2 and target_perf < avg_other_perf - 1:
        rotation = "ROTATING_OUT_OF_TARGET"
        score_base = 25
    elif abs(target_perf - avg_other_perf) < 1:
        rotation = "CORRELATED_MOVE"
        score_base = 60 if target_perf > 0 else 40
    else:
        rotation = "MIXED"
        score_base = 50
    
    # Adjust score based on correlations
    avg_corr = np.mean(list(correlations.values())) if correlations else 0
    score_adjustment = avg_corr * 10  # High correlation = stronger signal
    final_score = np.clip(score_base + score_adjustment, 0, 100)
    
    # Determine signal
    if final_score >= 65:
        signal = "VERY_BULLISH"
    elif final_score >= 55:
        signal = "BULLISH"
    elif final_score >= 45:
        signal = "NEUTRAL"
    elif final_score >= 35:
        signal = "BEARISH"
    else:
        signal = "VERY_BEARISH"
    
    print(f" 🎯 Rotation: {rotation}")
    print(f" 📊 Score: {final_score:.1f}/100")
    print(f" 🔔 Signal: {signal}")
    
    return {
        'score': final_score,
        'signal': signal,
        'rotation': rotation,
        'correlations': correlations,
        'target_performance': target_perf,
        'avg_other_performance': avg_other_perf,
        'asset_data': asset_data
    }

# ============================================================================
# NEW FUNCTION - AI BRAIN COMPATIBLE (FIXED)
# ============================================================================

def get_cross_asset_signal(symbol: str = "BTCUSDT") -> float:
    """
    NEW FUNCTION for ai_brain compatibility
    
    Args:
        symbol: Trading pair (e.g., BTCUSDT, ETHUSDT)
    
    Returns:
        float: Score 0-100
    """
    try:
        print(f"\n💎 cross_asset.get_cross_asset_signal çağrılıyor (v2.1)...")
        
        # Call original function
        result = get_multi_coin_data(target_symbol=symbol, interval='1h')
        
        # Return score
        score = result.get('score', 50)
        print(f"✅ Cross-Asset: {score:.2f}/100\n")
        
        return float(score)
        
    except Exception as e:
        print(f"⚠️ Cross-Asset layer hatası: {e}")
        return 50.0  # Neutral fallback

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Test original function
    result = get_multi_coin_data("BTCUSDT")
    print("\n📊 ORIGINAL FUNCTION TEST:")
    print(f"Score: {result['score']}")
    print(f"Signal: {result['signal']}")
    print(f"Rotation: {result['rotation']}")
    
    # Test new function
    print("\n" + "="*80)
    score = get_cross_asset_signal("ETHUSDT")
    print(f"\n📊 NEW FUNCTION TEST:")
    print(f"Score: {score}")
