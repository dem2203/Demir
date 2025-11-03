# ===========================================
# cross_asset_layer.py v2.0 - BINANCE 3-COIN CORRELATION
# ===========================================
# ✅ Binance API for BTC/ETH/LTC real price data
# ✅ Correlation matrix calculation
# ✅ Altcoin rotation detection
# ✅ Relative strength analysis
# ===========================================

"""
🔱 DEMIR AI TRADING BOT - Cross Asset Layer v2.0
====================================================================
Tarih: 3 Kasım 2025, 22:22 CET
Versiyon: 2.0 - REAL BINANCE DATA + MULTI-COIN CORRELATION

YENİ v2.0:
----------
✅ Binance API for 3 coins (BTC, ETH, LTC)
✅ Correlation matrix (Pearson)
✅ Relative strength (current coin vs others)
✅ Altcoin rotation signal
✅ Performance ranking
✅ Volume-weighted scoring

3 COINS TRACKED:
----------------
- BTCUSDT (Bitcoin) - Market leader
- ETHUSDT (Ethereum) - Major altcoin
- LTCUSDT (Litecoin) - Mid-cap altcoin

CORRELATION LOGIC:
------------------
High correlation (>0.7) → Market moving together → BTC dominance
Low correlation (<0.3) → Altcoin rotation → ETH/LTC opportunity
Negative correlation → Counter-trend plays

SCORING SYSTEM:
---------------
Target coin outperforming others → 70-85 (bullish)
Target coin underperforming → 15-30 (bearish)
Equal performance → 45-55 (neutral)
"""

import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List

# ============================================================================
# BINANCE API FUNCTIONS
# ============================================================================

def get_binance_klines(symbol: str, interval: str = '1h', limit: int = 100) -> pd.DataFrame:
    """
    Fetch OHLCV data from Binance API
    
    Args:
        symbol: Trading pair (BTCUSDT, ETHUSDT, LTCUSDT)
        interval: Timeframe (1h, 4h, 1d)
        limit: Number of candles
    
    Returns:
        DataFrame with OHLCV data
    """
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Parse response
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # Convert to proper types
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        df = df.set_index('timestamp')
        
        print(f"✅ Binance: {symbol} - {len(df)} candles loaded")
        return df
        
    except Exception as e:
        print(f"❌ Binance error ({symbol}): {e}")
        return None


def fetch_multiple_coins(symbols: List[str], interval: str = '1h', limit: int = 100) -> Dict[str, pd.DataFrame]:
    """
    Fetch data for multiple coins
    
    Returns:
        dict: {symbol: DataFrame}
    """
    results = {}
    
    for symbol in symbols:
        df = get_binance_klines(symbol, interval, limit)
        if df is not None:
            results[symbol] = df
    
    return results


# ============================================================================
# CORRELATION CALCULATIONS
# ============================================================================

def calculate_correlation_matrix(coin_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Calculate correlation matrix for all coins
    
    Returns:
        DataFrame: Correlation matrix
    """
    try:
        # Extract close prices
        prices = pd.DataFrame()
        for symbol, df in coin_data.items():
            prices[symbol] = df['close']
        
        # Calculate percentage changes
        returns = prices.pct_change().dropna()
        
        # Calculate correlation matrix
        corr_matrix = returns.corr()
        
        return corr_matrix
        
    except Exception as e:
        print(f"❌ Correlation calculation error: {e}")
        return None


def calculate_relative_strength(target_symbol: str, coin_data: Dict[str, pd.DataFrame], period: int = 30) -> Dict[str, float]:
    """
    Calculate relative strength of target coin vs others
    
    Args:
        target_symbol: Coin to analyze (e.g., 'ETHUSDT')
        coin_data: Price data for all coins
        period: Lookback period in candles
    
    Returns:
        dict: Relative performance metrics
    """
    try:
        # Get target coin data
        if target_symbol not in coin_data:
            return None
        
        target_df = coin_data[target_symbol]
        
        # Calculate percentage change for target
        target_change = ((target_df['close'].iloc[-1] / target_df['close'].iloc[-period]) - 1) * 100
        
        # Calculate for all coins
        changes = {}
        for symbol, df in coin_data.items():
            change = ((df['close'].iloc[-1] / df['close'].iloc[-period]) - 1) * 100
            changes[symbol] = change
        
        # Rank coins by performance
        sorted_coins = sorted(changes.items(), key=lambda x: x[1], reverse=True)
        target_rank = [i for i, (s, _) in enumerate(sorted_coins) if s == target_symbol][0] + 1
        
        # Calculate relative strength score
        avg_change = np.mean(list(changes.values()))
        relative_performance = target_change - avg_change
        
        return {
            'target_change': target_change,
            'avg_change': avg_change,
            'relative_performance': relative_performance,
            'rank': target_rank,
            'total_coins': len(changes),
            'all_changes': changes
        }
        
    except Exception as e:
        print(f"❌ Relative strength calculation error: {e}")
        return None


def calculate_volume_profile(target_symbol: str, coin_data: Dict[str, pd.DataFrame]) -> float:
    """
    Calculate relative volume for target coin
    
    Returns:
        float: Volume ratio (current vs average)
    """
    try:
        df = coin_data[target_symbol]
        
        # Current volume vs 20-period average
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].iloc[-20:].mean()
        
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        return volume_ratio
        
    except Exception as e:
        print(f"❌ Volume profile error: {e}")
        return 1.0


# ============================================================================
# SCORING FUNCTIONS
# ============================================================================

def score_correlation(target_symbol: str, corr_matrix: pd.DataFrame) -> float:
    """
    Score based on correlation with other coins
    
    High correlation = Moving with market (50)
    Low correlation = Independent movement (60-70)
    Negative correlation = Counter-trend (40-30)
    """
    try:
        # Get target coin correlations
        target_corr = corr_matrix[target_symbol]
        
        # Remove self-correlation
        other_corr = target_corr.drop(target_symbol)
        
        # Average correlation with others
        avg_corr = other_corr.mean()
        
        if avg_corr > 0.8:
            return 50  # High correlation = neutral
        elif avg_corr > 0.6:
            return 55  # Moderate correlation
        elif avg_corr > 0.3:
            return 65  # Low correlation = good for altcoins
        else:
            return 60  # Very low correlation
        
    except Exception as e:
        print(f"❌ Correlation scoring error: {e}")
        return 50


def score_relative_strength(rel_strength: Dict[str, Any]) -> float:
    """
    Score based on relative performance
    
    Outperforming others → 70-85
    Underperforming → 15-30
    Equal → 45-55
    """
    try:
        relative_perf = rel_strength['relative_performance']
        rank = rel_strength['rank']
        total = rel_strength['total_coins']
        
        # Rank-based score
        if rank == 1:
            rank_score = 80  # Best performer
        elif rank == 2:
            rank_score = 65  # Second best
        else:
            rank_score = 40  # Underperforming
        
        # Performance-based adjustment
        if relative_perf > 5:
            perf_bonus = 10
        elif relative_perf > 2:
            perf_bonus = 5
        elif relative_perf < -5:
            perf_bonus = -15
        elif relative_perf < -2:
            perf_bonus = -5
        else:
            perf_bonus = 0
        
        final_score = rank_score + perf_bonus
        final_score = max(15, min(85, final_score))  # Clamp to 15-85
        
        return final_score
        
    except Exception as e:
        print(f"❌ Relative strength scoring error: {e}")
        return 50


def score_volume(volume_ratio: float) -> float:
    """
    Score based on volume
    
    High volume = Stronger signal → +5 to +10
    Low volume = Weaker signal → -5 to 0
    """
    if volume_ratio > 2.0:
        return 10
    elif volume_ratio > 1.5:
        return 5
    elif volume_ratio < 0.5:
        return -5
    else:
        return 0


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def analyze_cross_asset(target_symbol: str = 'ETHUSDT', interval: str = '1h', lookback: int = 30) -> Dict[str, Any]:
    """
    Complete cross-asset correlation analysis
    
    Args:
        target_symbol: Coin to analyze (BTCUSDT, ETHUSDT, LTCUSDT)
        interval: Timeframe (1h, 4h, 1d)
        lookback: Lookback period for relative strength
    
    Returns:
        dict with score, signal, and correlation details
    """
    print(f"\n{'='*80}")
    print(f"🔗 CROSS ASSET LAYER v2.0 - CORRELATION ANALYSIS")
    print(f"   Target: {target_symbol}")
    print(f"   Interval: {interval}")
    print(f"{'='*80}\n")
    
    # Define coin universe
    symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
    
    # Fetch data for all coins
    coin_data = fetch_multiple_coins(symbols, interval, limit=100)
    
    if len(coin_data) < 2:
        print("❌ Cross Asset: Insufficient data")
        return {
            'available': False,
            'score': 50,
            'signal': 'NEUTRAL',
            'reason': 'Insufficient data from Binance'
        }
    
    try:
        # Calculate correlation matrix
        corr_matrix = calculate_correlation_matrix(coin_data)
        
        if corr_matrix is None:
            return {
                'available': False,
                'score': 50,
                'signal': 'NEUTRAL',
                'reason': 'Correlation calculation failed'
            }
        
        # Calculate relative strength
        rel_strength = calculate_relative_strength(target_symbol, coin_data, lookback)
        
        if rel_strength is None:
            return {
                'available': False,
                'score': 50,
                'signal': 'NEUTRAL',
                'reason': 'Relative strength calculation failed'
            }
        
        # Calculate volume profile
        volume_ratio = calculate_volume_profile(target_symbol, coin_data)
        
        # Score each component
        corr_score = score_correlation(target_symbol, corr_matrix)
        rel_strength_score = score_relative_strength(rel_strength)
        volume_adjustment = score_volume(volume_ratio)
        
        # Weighted ensemble
        weights = {
            'correlation': 0.30,
            'relative_strength': 0.70
        }
        
        base_score = (
            corr_score * weights['correlation'] +
            rel_strength_score * weights['relative_strength']
        )
        
        total_score = base_score + volume_adjustment
        total_score = max(0, min(100, total_score))  # Clamp to 0-100
        
        # Determine signal
        if total_score >= 60:
            signal = 'BULLISH'
        elif total_score <= 40:
            signal = 'BEARISH'
        else:
            signal = 'NEUTRAL'
        
        # Print results
        print(f"📊 CORRELATION MATRIX:")
        print(corr_matrix.round(3))
        
        print(f"\n📊 RELATIVE STRENGTH:")
        print(f"   {target_symbol}: {rel_strength['target_change']:+.2f}%")
        print(f"   Avg All Coins: {rel_strength['avg_change']:+.2f}%")
        print(f"   Relative Performance: {rel_strength['relative_performance']:+.2f}%")
        print(f"   Rank: #{rel_strength['rank']} of {rel_strength['total_coins']}")
        
        print(f"\n📊 SCORING:")
        print(f"   Correlation Score: {corr_score:.1f}/100")
        print(f"   Relative Strength Score: {rel_strength_score:.1f}/100")
        print(f"   Volume Adjustment: {volume_adjustment:+.1f}")
        
        print(f"\n{'='*80}")
        print(f"✅ CROSS ASSET ANALYSIS COMPLETE!")
        print(f"   Total Score: {total_score:.1f}/100")
        print(f"   Signal: {signal}")
        print(f"{'='*80}\n")
        
        return {
            'available': True,
            'score': round(total_score, 2),
            'signal': signal,
            'correlation_matrix': corr_matrix.to_dict(),
            'relative_strength': {
                'target_change': round(rel_strength['target_change'], 2),
                'avg_change': round(rel_strength['avg_change'], 2),
                'relative_performance': round(rel_strength['relative_performance'], 2),
                'rank': rel_strength['rank'],
                'total_coins': rel_strength['total_coins']
            },
            'volume_ratio': round(volume_ratio, 2),
            'components': {
                'correlation_score': round(corr_score, 2),
                'relative_strength_score': round(rel_strength_score, 2),
                'volume_adjustment': round(volume_adjustment, 2)
            },
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Cross asset analysis error: {e}")
        return {
            'available': False,
            'score': 50,
            'signal': 'NEUTRAL',
            'reason': str(e)
        }


def get_cross_asset_signal(symbol: str = 'ETHUSDT') -> Dict[str, Any]:
    """
    Main function called by ai_brain.py
    
    Returns:
        dict: {'available': bool, 'score': float, 'signal': str}
    """
    result = analyze_cross_asset(symbol, interval='1h', lookback=30)
    
    return {
        'available': result['available'],
        'score': result.get('score', 50),
        'signal': result.get('signal', 'NEUTRAL'),
        'correlation_matrix': result.get('correlation_matrix', {}),
        'relative_strength': result.get('relative_strength', {}),
        'volume_ratio': result.get('volume_ratio', 1.0)
    }


# ============================================================================
# STANDALONE TESTING
# ============================================================================
if __name__ == "__main__":
    print("="*80)
    print("🔱 CROSS ASSET LAYER v2.0 TEST")
    print("   BINANCE 3-COIN CORRELATION ANALYSIS")
    print("="*80)
    
    # Test with ETHUSDT
    result = get_cross_asset_signal('ETHUSDT')
    
    print("\n" + "="*80)
    print("📊 CROSS ASSET TEST RESULTS:")
    print(f"   Available: {result['available']}")
    print(f"   Score: {result.get('score', 'N/A')}/100")
    print(f"   Signal: {result.get('signal', 'N/A')}")
    
    if 'correlation_matrix' in result and result['correlation_matrix']:
        print(f"\n   Correlation Matrix:")
        for coin, corr in result['correlation_matrix'].items():
            print(f"   {coin}: {corr}")
    
    if 'relative_strength' in result and result['relative_strength']:
        print(f"\n   Relative Strength:")
        print(f"   {result['relative_strength']}")
    
    print("="*80)
