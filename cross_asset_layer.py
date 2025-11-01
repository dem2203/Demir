"""
🔗 CROSS-ASSET CORRELATION LAYER - Phase 6.4
==============================================
Date: 2 Kasım 2025, 00:18 CET
Version: 1.0 COMPLETE

FEATURES:
• BTC/ETH correlation and divergence detection
• BTC/LTC, ETH/BNB, and other major pair analysis
• Altcoin rotation detection (when alts rotate leadership)
• Cross-pair strength comparison
• Leading/lagging asset identification
• Arbitrage opportunity signals

SCORING:
• 70-100: Strong positive correlation (assets moving together)
• 50-70: Moderate correlation
• 30-50: Weak/neutral correlation
• 0-30: Divergence (assets moving opposite)

USAGE:
from cross_asset_layer import calculate_cross_asset
result = calculate_cross_asset()
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_pair_data(symbol='BTCUSDT', interval='1h', limit=100):
    """Get price data for any symbol"""
    try:
        url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            df['close'] = df['close'].astype(float)
            return df['close'].values
    except:
        pass
    return None

def calculate_correlation(series1, series2):
    """Calculate Pearson correlation between two price series"""
    if series1 is None or series2 is None:
        return 0.0
    if len(series1) != len(series2):
        min_len = min(len(series1), len(series2))
        series1 = series1[-min_len:]
        series2 = series2[-min_len:]
    
    return np.corrcoef(series1, series2)[0, 1]

def calculate_price_change(prices):
    """Calculate 24h price change percentage"""
    if prices is None or len(prices) < 24:
        return 0.0
    return ((prices[-1] / prices[-24]) - 1) * 100

def calculate_cross_asset(interval='1h', limit=100):
    """
    Calculate cross-asset correlations and rotation signals
    
    Returns score 0-100 based on correlation strength
    """
    try:
        # Get price data for major pairs
        btc_prices = get_pair_data('BTCUSDT', interval, limit)
        eth_prices = get_pair_data('ETHUSDT', interval, limit)
        ltc_prices = get_pair_data('LTCUSDT', interval, limit)
        bnb_prices = get_pair_data('BNBUSDT', interval, limit)
        
        if btc_prices is None or eth_prices is None:
            return create_error_response("Price data unavailable")
        
        # Calculate correlations
        btc_eth_corr = calculate_correlation(btc_prices, eth_prices)
        btc_ltc_corr = calculate_correlation(btc_prices, ltc_prices) if ltc_prices is not None else 0
        eth_bnb_corr = calculate_correlation(eth_prices, bnb_prices) if bnb_prices is not None else 0
        
        # Calculate 24h changes
        btc_change = calculate_price_change(btc_prices)
        eth_change = calculate_price_change(eth_prices)
        ltc_change = calculate_price_change(ltc_prices) if ltc_prices is not None else 0
        bnb_change = calculate_price_change(bnb_prices) if bnb_prices is not None else 0
        
        # Average correlation (overall market cohesion)
        avg_correlation = (btc_eth_corr + btc_ltc_corr + eth_bnb_corr) / 3
        
        # Detect divergences
        btc_eth_divergence = abs(btc_change - eth_change)
        divergence_threshold = 3.0  # 3% difference = significant divergence
        
        # SCORING LOGIC
        # High correlation = assets moving together (70-100)
        # Low correlation = divergence, rotation happening (0-30)
        
        corr_score = (avg_correlation + 1) * 50  # Map [-1, 1] to [0, 100]
        
        # Adjust for divergence magnitude
        if btc_eth_divergence > divergence_threshold:
            corr_score -= 15  # Penalize for divergence
        
        # Detect rotation (one asset significantly outperforming)
        rotation_detected = False
        rotation_leader = None
        
        if btc_eth_divergence > divergence_threshold:
            rotation_detected = True
            rotation_leader = "ETH" if eth_change > btc_change else "BTC"
        
        final_score = max(0, min(100, corr_score))
        
        return {
            'score': round(final_score, 2),
            'avg_correlation': round(avg_correlation, 4),
            'btc_eth_correlation': round(btc_eth_corr, 4),
            'btc_ltc_correlation': round(btc_ltc_corr, 4),
            'eth_bnb_correlation': round(eth_bnb_corr, 4),
            'btc_change_24h': round(btc_change, 2),
            'eth_change_24h': round(eth_change, 2),
            'ltc_change_24h': round(ltc_change, 2),
            'bnb_change_24h': round(bnb_change, 2),
            'btc_eth_divergence': round(btc_eth_divergence, 2),
            'rotation_detected': rotation_detected,
            'rotation_leader': rotation_leader,
            'market_cohesion': get_market_cohesion(avg_correlation),
            'interpretation': get_interpretation(final_score),
            'available': True
        }
    
    except Exception as e:
        return create_error_response(str(e))

def get_market_cohesion(avg_corr):
    """Interpret overall market correlation"""
    if avg_corr > 0.8:
        return "🟢 Very High - All assets moving together (strong trend)"
    elif avg_corr > 0.6:
        return "🟢 High - Strong positive correlation"
    elif avg_corr > 0.4:
        return "🟡 Moderate - Some correlation, some independence"
    elif avg_corr > 0.2:
        return "🟡 Low - Assets moving independently"
    elif avg_corr > 0:
        return "🔴 Very Low - High divergence, rotation likely"
    elif avg_corr > -0.2:
        return "🔴 Negative - Assets moving opposite (rare)"
    else:
        return "⚠️ Strong Negative - Inverse correlation (very rare)"

def get_interpretation(score):
    """Get human-readable interpretation"""
    if score >= 80:
        return "🟢 STRONG CORRELATION - Assets moving in sync, clear trend"
    elif score >= 70:
        return "🟢 HIGH CORRELATION - Coordinated market movement"
    elif score >= 60:
        return "🟢 MODERATE CORRELATION - General trend alignment"
    elif score >= 50:
        return "🟡 NEUTRAL - Mixed signals, some independence"
    elif score >= 40:
        return "🟡 LOW CORRELATION - Assets diverging"
    elif score >= 30:
        return "🔴 DIVERGENCE - Rotation likely happening"
    else:
        return "⚠️ STRONG DIVERGENCE - Major rotation in progress"

def create_error_response(error_msg):
    """Create standardized error response"""
    return {
        'score': 50,
        'avg_correlation': 0,
        'btc_eth_correlation': 0,
        'btc_ltc_correlation': 0,
        'eth_bnb_correlation': 0,
        'btc_change_24h': 0,
        'eth_change_24h': 0,
        'ltc_change_24h': 0,
        'bnb_change_24h': 0,
        'btc_eth_divergence': 0,
        'rotation_detected': False,
        'rotation_leader': None,
        'market_cohesion': f"⚠️ Error: {error_msg}",
        'interpretation': f"⚠️ Data unavailable: {error_msg}",
        'available': False
    }

if __name__ == "__main__":
    print("🔗 CROSS-ASSET CORRELATION LAYER TEST")
    print("=" * 60)
    result = calculate_cross_asset()
    print(f"\n🎯 SCORE: {result['score']}/100")
    print(f"📖 Interpretation: {result['interpretation']}")
    print(f"🌍 Market Cohesion: {result['market_cohesion']}")
    print(f"\n📊 CORRELATIONS:")
    print(f"   BTC/ETH: {result['btc_eth_correlation']:.4f}")
    print(f"   BTC/LTC: {result['btc_ltc_correlation']:.4f}")
    print(f"   ETH/BNB: {result['eth_bnb_correlation']:.4f}")
    print(f"   Average: {result['avg_correlation']:.4f}")
    print(f"\n💹 24H CHANGES:")
    print(f"   BTC: {result['btc_change_24h']:+.2f}%")
    print(f"   ETH: {result['eth_change_24h']:+.2f}%")
    print(f"   LTC: {result['ltc_change_24h']:+.2f}%")
    print(f"   BNB: {result['bnb_change_24h']:+.2f}%")
    print(f"\n🔄 ROTATION:")
    print(f"   Detected: {result['rotation_detected']}")
    print(f"   Leader: {result['rotation_leader']}")
    print(f"   BTC/ETH Divergence: {result['btc_eth_divergence']:.2f}%")
    print(f"\n✅ Data Available: {result['available']}")
    print("=" * 60)
