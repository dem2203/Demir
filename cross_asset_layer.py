"""
🔱 CROSS-ASSET CORRELATION LAYER ENHANCED - Phase 6.4
======================================================
Date: 2 Kasım 2025
Version: 2.0 - ENHANCED & MERGED

WHAT IT DOES:
-------------
- Analyzes BTC/ETH/LTC/BNB momentum & correlation
- Detects crypto rotation patterns (money flow between assets)
- Identifies leader/laggard coins
- Provides actionable rotation signals
- Calculates pairwise correlations
- Recent performance tracking

ROTATION LOGIC:
---------------
- BTC leading (strong BTC, weak alts) → Focus on BTC
- ALT season (weak BTC, strong alts) → Focus on alts
- Correlated move (all strong/weak together) → Follow trend
- Divergence → Rotation opportunity

SCORING:
--------
- Strong rotation into target coin → 70-80 (Very Bullish)
- Moderate positive correlation → 55-65 (Bullish)
- Neutral/mixed signals → 45-55 (Neutral)
- Rotation out of target coin → 35-45 (Bearish)
- Strong rotation away → 20-30 (Very Bearish)
"""

import requests
import numpy as np
from datetime import datetime
from binance.client import Client
import os

def get_multi_coin_data(symbols=['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'BNBUSDT'], interval='1h', limit=168):
    """
    Fetch price data for multiple coins using Binance API
    
    Args:
        symbols (list): List of trading pairs
        interval (str): Timeframe (1h, 4h, 1d)
        limit (int): Number of candles (default 168 = 1 week on 1h)
    
    Returns:
        dict: Price data and returns for each symbol
    """
    try:
        # Try to initialize Binance client
        api_key = os.getenv('BINANCE_API_KEY', '')
        api_secret = os.getenv('BINANCE_SECRET_KEY', '')
        
        if api_key and api_secret:
            client = Client(api_key, api_secret)
        else:
            client = None  # Will use public API
        
        data = {}
        returns_data = {}
        
        for symbol in symbols:
            try:
                # Method 1: Using python-binance if available
                if client:
                    klines = client.get_klines(
                        symbol=symbol,
                        interval=interval,
                        limit=limit
                    )
                else:
                    # Method 2: Public API fallback
                    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code != 200:
                        continue
                    
                    klines = response.json()
                
                if not klines or not isinstance(klines, list):
                    continue
                
                # Extract close prices
                closes = np.array([float(candle[4]) for candle in klines])
                
                # Calculate returns (percentage change)
                returns = []
                for i in range(1, len(closes)):
                    ret = ((closes[i] - closes[i-1]) / closes[i-1]) * 100
                    returns.append(ret)
                
                # Calculate metrics
                current_price = closes[-1]
                price_7d_ago = closes[0] if len(closes) > 0 else current_price
                change_7d = ((current_price - price_7d_ago) / price_7d_ago) * 100
                
                # 24h change
                hours_24 = min(24, len(closes) - 1)
                price_24h_ago = closes[-hours_24] if len(closes) >= hours_24 else closes[0]
                change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
                
                # Momentum (last 7 periods avg return)
                recent_returns = returns[-7:] if len(returns) >= 7 else returns
                momentum = np.mean(recent_returns) if recent_returns else 0
                
                # Volatility (std of returns)
                volatility = np.std(returns) if len(returns) > 1 else 0
                
                # Recent performance (last 10 periods cumulative)
                recent_perf = np.sum(returns[-10:]) if len(returns) >= 10 else np.sum(returns)
                
                data[symbol] = {
                    'current_price': current_price,
                    'change_24h': change_24h,
                    'change_7d': change_7d,
                    'momentum': momentum,
                    'volatility': volatility,
                    'recent_performance': recent_perf,
                    'returns': returns
                }
                
                returns_data[symbol] = returns
                
            except Exception as e:
                print(f"⚠️ Error fetching {symbol}: {e}")
                continue
        
        return {'success': True, 'data': data, 'returns': returns_data}
        
    except Exception as e:
        print(f"❌ Multi-coin data error: {e}")
        return {'success': False}

def calculate_correlations(returns_data):
    """
    Calculate pairwise correlations between coins
    
    Args:
        returns_data (dict): Returns for each symbol
    
    Returns:
        dict: Correlation matrix with short names
    """
    correlations = {}
    asset_names = list(returns_data.keys())
    
    for i in range(len(asset_names)):
        for j in range(i+1, len(asset_names)):
            asset1 = asset_names[i]
            asset2 = asset_names[j]
            
            returns1 = returns_data[asset1]
            returns2 = returns_data[asset2]
            
            # Ensure same length
            min_len = min(len(returns1), len(returns2))
            returns1_aligned = returns1[:min_len]
            returns2_aligned = returns2[:min_len]
            
            if len(returns1_aligned) > 1:
                corr = np.corrcoef(returns1_aligned, returns2_aligned)[0, 1]
                
                # Use short names (BTC/ETH instead of BTCUSDT/ETHUSDT)
                short1 = asset1.replace('USDT', '').replace('BUSD', '')[:3]
                short2 = asset2.replace('USDT', '').replace('BUSD', '')[:3]
                
                correlations[f"{short1}/{short2}"] = round(corr, 3)
    
    return correlations

def detect_rotation(target_symbol, data, returns_data):
    """
    Detect if money is rotating into or out of target coin
    
    Args:
        target_symbol (str): The coin to analyze (e.g., 'BTCUSDT')
        data (dict): Multi-coin metrics
        returns_data (dict): Returns data
    
    Returns:
        dict: Rotation analysis
    """
    
    if target_symbol not in data:
        return {'available': False}
    
    target = data[target_symbol]
    others = {k: v for k, v in data.items() if k != target_symbol}
    
    # Compare target momentum vs others
    target_mom = target['momentum']
    other_moms = [v['momentum'] for v in others.values()]
    avg_other_mom = np.mean(other_moms) if other_moms else 0
    
    # Relative strength
    relative_strength = target_mom - avg_other_mom
    
    # Determine rotation signal
    if relative_strength > 0.5:
        rotation_signal = "ROTATING IN"
        rotation_strength = "STRONG"
    elif relative_strength > 0.2:
        rotation_signal = "ROTATING IN"
        rotation_strength = "MODERATE"
    elif relative_strength > -0.2:
        rotation_signal = "NEUTRAL"
        rotation_strength = "WEAK"
    elif relative_strength > -0.5:
        rotation_signal = "ROTATING OUT"
        rotation_strength = "MODERATE"
    else:
        rotation_signal = "ROTATING OUT"
        rotation_strength = "STRONG"
    
    # Leader/Laggard detection
    sorted_by_mom = sorted(data.items(), key=lambda x: x[1]['momentum'], reverse=True)
    target_rank = [i for i, (sym, _) in enumerate(sorted_by_mom) if sym == target_symbol][0] + 1
    
    if target_rank == 1:
        position = "LEADER"
    elif target_rank == len(data):
        position = "LAGGARD"
    else:
        position = "MIDDLE"
    
    return {
        'available': True,
        'rotation_signal': rotation_signal,
        'rotation_strength': rotation_strength,
        'relative_strength': round(relative_strength, 3),
        'target_momentum': round(target_mom, 3),
        'avg_other_momentum': round(avg_other_mom, 3),
        'position': position,
        'rank': target_rank,
        'total_coins': len(data)
    }

def calculate_cross_asset_score(rotation_data, correlations, data, target_symbol):
    """
    Calculate trading score based on cross-asset analysis
    
    Combines:
    - Rotation signals
    - Correlation strength
    - Recent performance
    - Leader/laggard position
    
    Args:
        rotation_data (dict): Rotation analysis
        correlations (dict): Correlation matrix
        data (dict): Coin metrics
        target_symbol (str): Target coin
    
    Returns:
        tuple: (score, sentiment, reason)
    """
    
    # Calculate average correlation
    avg_correlation = np.mean(list(correlations.values())) if correlations else 0.5
    
    # Get target performance
    target_perf = data[target_symbol]['recent_performance']
    
    # Base score from rotation signal
    rotation_signal = rotation_data['rotation_signal']
    strength = rotation_data['rotation_strength']
    
    if rotation_signal == "ROTATING IN":
        if strength == "STRONG":
            base_score = 75
        else:
            base_score = 65
    elif rotation_signal == "NEUTRAL":
        base_score = 50
    else:  # ROTATING OUT
        if strength == "STRONG":
            base_score = 25
        else:
            base_score = 35
    
    # Adjust for correlation and performance
    if avg_correlation > 0.7:
        # High correlation - coordinated move
        if target_perf > 0:
            corr_adjustment = +5
            sentiment = "BULLISH"
            reason = f"Strong correlation ({avg_correlation:.2f}) - coordinated rally"
        else:
            corr_adjustment = -5
            sentiment = "BEARISH"
            reason = f"Strong correlation ({avg_correlation:.2f}) - coordinated selloff"
    elif avg_correlation > 0.4:
        # Moderate correlation
        corr_adjustment = 0
        sentiment = "NEUTRAL"
        reason = f"Moderate correlation ({avg_correlation:.2f})"
    else:
        # Low correlation - rotation active
        corr_adjustment = 0
        sentiment = "ROTATION"
        reason = f"Low correlation ({avg_correlation:.2f}) - rotation active"
    
    # Adjust for position (leader/laggard)
    position = rotation_data['position']
    if position == "LEADER":
        position_adjustment = +5
    elif position == "LAGGARD":
        position_adjustment = -5
    else:
        position_adjustment = 0
    
    # Final score
    final_score = np.clip(base_score + corr_adjustment + position_adjustment, 0, 100)
    
    return round(final_score, 1), sentiment, reason

def calculate_cross_asset(target_symbol='BTCUSDT', interval='1h', limit=168):
    """
    Main function: Calculate Cross-Asset Correlation Layer
    
    Args:
        target_symbol (str): Coin to analyze
        interval (str): Timeframe (1h, 4h, 1d)
        limit (int): Number of candles
    
    Returns:
        dict: Complete cross-asset analysis
    """
    
    # Define coin basket
    symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'BNBUSDT']
    
    # Ensure target is in basket
    if target_symbol not in symbols:
        symbols.append(target_symbol)
    
    # cross_asset_layer.py - RETURN FORMAT FIX (Satır 450 civarı)
# Sadece bu fonksiyonun return kısmını düzeltiyoruz!

def get_multi_coin_data(symbols, interval='1h', limit=100):
    """
    ✅ DÜZELTME: Return formatı standardize edildi
    
    Birden fazla coin için fiyat verisi çeker (Binance API)
    """
    try:
        result_data = {}
        
        for symbol in symbols:
            url = f"https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                klines = response.json()
                bars = []
                
                for kline in klines:
                    bars.append({
                        'timestamp': int(kline[0]),
                        'open': float(kline[1]),
                        'high': float(kline[2]),
                        'low': float(kline[3]),
                        'close': float(kline[4]),
                        'volume': float(kline[5])
                    })
                
                result_data[symbol] = bars
        
        # ✅ DÜZELTME: Standardize return format
        return {
            'success': True,
            'data': result_data,
            'symbols': list(result_data.keys()),
            'count': len(result_data)
        }
    
    except Exception as e:
        print(f"⚠️ get_multi_coin_data hatası: {e}")
        return {
            'success': False,
            'data': {},
            'symbols': [],
            'count': 0,
            'error': str(e)
        }
    
    data = result['data']
    returns_data = result['returns']
    
    # Calculate correlations
    correlations = calculate_correlations(returns_data)
    
    # Calculate average correlation
    avg_correlation = np.mean(list(correlations.values())) if correlations else 0.5
    
    # Detect rotation
    rotation = detect_rotation(target_symbol, data, returns_data)
    
    if not rotation['available']:
        return {
            'available': False,
            'score': 50,
            'reason': 'Target coin data unavailable',
            'sentiment': 'NEUTRAL'
        }
    
    # Calculate score with enhanced logic
    score, sentiment, reason = calculate_cross_asset_score(
        rotation, correlations, data, target_symbol
    )
    
    # Identify leader and laggard for full market view
    sorted_by_perf = sorted(
        [(sym, d['recent_performance']) for sym, d in data.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    leader_full = sorted_by_perf[0][0]
    leader = leader_full.replace('USDT', '').replace('BUSD', '')[:3]
    leader_perf = sorted_by_perf[0][1]
    
    laggard_full = sorted_by_perf[-1][0]
    laggard = laggard_full.replace('USDT', '').replace('BUSD', '')[:3]
    laggard_perf = sorted_by_perf[-1][1]
    
    # Compile performance dict with short names
    performance = {
        sym.replace('USDT', '').replace('BUSD', '')[:3]: round(data[sym]['recent_performance'], 2)
        for sym in symbols if sym in data
    }
    
    # Compile full result
    result_dict = {
        'available': True,
        'score': score,
        'signal': 'LONG' if score >= 55 else 'SHORT' if score <= 45 else 'NEUTRAL',
        'sentiment': sentiment,
        'reason': reason,
        'interpretation': f"{rotation['rotation_signal']} ({rotation['rotation_strength']}) - {reason}",
        
        # Rotation details
        'rotation_signal': rotation['rotation_signal'],
        'rotation_strength': rotation['rotation_strength'],
        'relative_strength': rotation['relative_strength'],
        'position': rotation['position'],
        'rank': rotation['rank'],
        'total_coins': rotation['total_coins'],
        
        # Correlation details
        'avg_correlation': round(avg_correlation, 3),
        'correlations': correlations,
        
        # Leader/Laggard
        'leader': leader,
        'leader_performance': round(leader_perf, 2),
        'laggard': laggard,
        'laggard_performance': round(laggard_perf, 2),
        
        # Performance summary
        'performance': performance,
        
        # Coin-specific details
        'coin_performance': {
            sym.replace('USDT', '').replace('BUSD', '')[:3]: {
                'change_24h': data[sym]['change_24h'],
                'change_7d': data[sym]['change_7d'],
                'momentum': data[sym]['momentum']
            }
            for sym in symbols if sym in data
        },
        
        'timestamp': datetime.now().isoformat()
    }
    
    return result_dict

# ============================================================================
# TEST EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("🔱 CROSS-ASSET CORRELATION LAYER ENHANCED - TEST")
    print("=" * 60)
    
    result = calculate_cross_asset('BTCUSDT', '1h', 168)
    
    if result['available']:
        print(f"\n✅ Cross-Asset Layer Active")
        print(f"📊 Score: {result['score']}/100")
        print(f"🎯 Signal: {result['signal']}")
        print(f"🎭 Sentiment: {result['sentiment']}")
        print(f"💡 Interpretation: {result['interpretation']}")
        
        print(f"\n🔄 Rotation Analysis:")
        print(f"  Signal: {result['rotation_signal']} ({result['rotation_strength']})")
        print(f"  Relative Strength: {result['relative_strength']}")
        print(f"  Position: {result['position']} (Rank {result['rank']}/{result['total_coins']})")
        
        print(f"\n📈 Coin Performance (Recent):")
        for coin, perf in result['performance'].items():
            print(f"  {coin}: {perf:+.2f}%")
        
        print(f"\n🔗 Correlations:")
        print(f"  Average: {result['avg_correlation']:.3f}")
        for pair, corr in result['correlations'].items():
            print(f"  {pair}: {corr:.3f}")
        
        print(f"\n🏆 Market Leaders:")
        print(f"  Leader: {result['leader']} ({result['leader_performance']:+.2f}%)")
        print(f"  Laggard: {result['laggard']} ({result['laggard_performance']:+.2f}%)")
    else:
        print(f"\n❌ Cross-Asset Layer Unavailable")
        print(f"Reason: {result['reason']}")
    
    print("\n" + "=" * 60)
