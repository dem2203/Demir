# ===========================================
# kelly_enhanced_layer.py v2.1 - FIXED calculate_dynamic_kelly
# ===========================================
# ✅ FIXED: calculate_dynamic_kelly function added
# ✅ Simplified Kelly Criterion (no trade history needed)
# ✅ Based on market conditions + volatility
# ✅ Conservative risk management
# ===========================================

"""
🔱 DEMIR AI TRADING BOT - Kelly Enhanced Layer v2.1
====================================================================
Tarih: 4 Kasım 2025, 21:26 CET
Versiyon: 2.1 - calculate_dynamic_kelly FIXED

YENİ v2.1:
----------
✅ calculate_dynamic_kelly() function added
✅ Returns float score directly (0-100)
✅ Compatible with ai_brain v12.0

YENİ v2.0:
----------
✅ Simplified Kelly formula (no historical win rate needed)
✅ Market regime detection (trending/ranging)
✅ Volatility-based sizing (ATR-based)
✅ Conservative multiplier (0.25x Kelly = safer)
✅ Binance real-time data

KELLY FORMULA (SIMPLIFIED):
---------------------------
Kelly% = (Win Rate × Avg Win - Avg Loss) / Avg Win

WITHOUT TRADE HISTORY:
---------------------
We use market-based estimates:
- Win Rate = 55% (conservative estimate for trend-following)
- Avg Win/Loss Ratio = 1.5:1 (typical for good risk/reward)

KELLY SCORE INTERPRETATION:
---------------------------
- 80-100: High confidence (strong trend + low volatility)
- 60-80: Moderate confidence (normal conditions)
- 40-60: Low confidence (choppy/uncertain)
- 0-40: Very low confidence (high risk)
"""

import requests
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

def get_binance_klines(symbol='BTCUSDT', interval='1h', limit=100):
    """Fetch real-time price data from Binance"""
    try:
        url = 'https://api.binance.com/api/v3/klines'
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        klines = response.json()
        
        # Convert to DataFrame
        df = pd.DataFrame(klines, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # Convert to float
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        return df
        
    except Exception as e:
        print(f"⚠️ Binance API error: {e}")
        return None

def calculate_atr(df, period=14):
    """Calculate Average True Range (volatility measure)"""
    try:
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr.iloc[-1]
        
    except Exception as e:
        print(f"⚠️ ATR calculation error: {e}")
        return None

def detect_market_regime(df):
    """Detect if market is trending or ranging"""
    try:
        # Calculate ADX (trend strength indicator)
        high = df['high']
        low = df['low']
        close = df['close']
        
        # True Range
        tr = pd.concat([
            high - low,
            abs(high - close.shift()),
            abs(low - close.shift())
        ], axis=1).max(axis=1)
        
        # Directional Movement
        up_move = high - high.shift()
        down_move = low.shift() - low
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        # Smooth
        atr = tr.rolling(14).mean()
        plus_di = 100 * pd.Series(plus_dm).rolling(14).mean() / atr
        minus_di = 100 * pd.Series(minus_dm).rolling(14).mean() / atr
        
        # ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(14).mean().iloc[-1]
        
        # Interpretation
        if adx > 25:
            return "TRENDING", adx
        elif adx > 20:
            return "WEAK_TREND", adx
        else:
            return "RANGING", adx
            
    except Exception as e:
        print(f"⚠️ Market regime detection error: {e}")
        return "UNKNOWN", 0

def calculate_kelly_enhanced(symbol='BTCUSDT'):
    """
    Calculate Kelly Criterion-based position sizing score
    
    Returns:
        dict: Kelly analysis with score 0-100
    """
    try:
        print(f"\n📊 Calculating Kelly-Enhanced Position Sizing for {symbol}...")
        
        # Get price data
        df = get_binance_klines(symbol, interval='1h', limit=100)
        if df is None or df.empty:
            return {
                'available': False,
                'score': 50,
                'reason': 'Failed to fetch price data'
            }
        
        # ==========================================
        # 1. VOLATILITY ANALYSIS (ATR)
        # ==========================================
        current_price = df['close'].iloc[-1]
        atr = calculate_atr(df, period=14)
        
        if atr is None:
            return {'available': False, 'score': 50, 'reason': 'ATR calculation failed'}
        
        # ATR as percentage of price
        atr_pct = (atr / current_price) * 100
        
        # Volatility scoring (inverse - lower volatility = higher score)
        if atr_pct < 1:
            volatility_score = 90
            volatility_level = "VERY_LOW"
        elif atr_pct < 2:
            volatility_score = 75
            volatility_level = "LOW"
        elif atr_pct < 3:
            volatility_score = 60
            volatility_level = "MODERATE"
        elif atr_pct < 5:
            volatility_score = 40
            volatility_level = "HIGH"
        else:
            volatility_score = 20
            volatility_level = "VERY_HIGH"
        
        # ==========================================
        # 2. MARKET REGIME DETECTION
        # ==========================================
        regime, adx_value = detect_market_regime(df)
        
        if regime == "TRENDING":
            regime_score = 85
            regime_multiplier = 1.2
        elif regime == "WEAK_TREND":
            regime_score = 60
            regime_multiplier = 1.0
        else:  # RANGING or UNKNOWN
            regime_score = 40
            regime_multiplier = 0.8
        
        # ==========================================
        # 3. SIMPLIFIED KELLY CALCULATION
        # ==========================================
        # Conservative estimates (no trade history)
        win_rate = 0.55  # 55% win rate (conservative for trend-following)
        avg_win_loss_ratio = 1.5  # 1.5:1 reward/risk
        
        # Kelly formula: (Win Rate × RR - Loss Rate) / RR
        loss_rate = 1 - win_rate
        kelly_pct = (win_rate * avg_win_loss_ratio - loss_rate) / avg_win_loss_ratio
        
        # Apply fractional Kelly (0.25x for safety)
        fractional_kelly = kelly_pct * 0.25
        
        # Convert to score (0-100)
        kelly_base_score = fractional_kelly * 100 * 4  # Scale up
        
        # ==========================================
        # 4. COMBINE SCORES
        # ==========================================
        # Weighted average
        final_score = (
            volatility_score * 0.4 +   # 40% weight on volatility
            regime_score * 0.35 +       # 35% weight on trend strength
            kelly_base_score * 0.25     # 25% weight on Kelly base
        )
        
        # Apply regime multiplier
        final_score = final_score * regime_multiplier
        
        # Cap at 0-100
        final_score = max(0, min(100, final_score))
        
        # ==========================================
        # 5. POSITION SIZE RECOMMENDATION
        # ==========================================
        if final_score >= 80:
            position_size = "LARGE"
            recommendation = "High confidence - consider larger position"
        elif final_score >= 60:
            position_size = "MODERATE"
            recommendation = "Moderate confidence - standard position"
        elif final_score >= 40:
            position_size = "SMALL"
            recommendation = "Low confidence - reduce position size"
        else:
            position_size = "MINIMAL"
            recommendation = "Very low confidence - minimal/no position"
        
        print(f"✅ Kelly Analysis Complete!")
        print(f"   Volatility: {volatility_level} (ATR: {atr_pct:.2f}%)")
        print(f"   Market Regime: {regime} (ADX: {adx_value:.1f})")
        print(f"   Kelly Score: {final_score:.2f}/100")
        print(f"   Position Size: {position_size}")
        
        return {
            'available': True,
            'score': round(final_score, 2),
            'volatility_level': volatility_level,
            'atr_percent': round(atr_pct, 2),
            'market_regime': regime,
            'adx': round(adx_value, 1),
            'position_size': position_size,
            'recommendation': recommendation,
            'kelly_percentage': round(fractional_kelly * 100, 2),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"⚠️ Kelly calculation error: {e}")
        return {'available': False, 'score': 50, 'reason': str(e)}

def calculate_dynamic_kelly(symbol='BTCUSDT'):
    """
    Simplified wrapper for Kelly signal (used by ai_brain.py)
    
    Args:
        symbol: Trading pair symbol (e.g., "BTCUSDT")
    
    Returns:
        float: Kelly score (0-100)
    """
    result = calculate_kelly_enhanced(symbol)
    
    if result['available']:
        return result['score']
    else:
        return 50.0  # Neutral score if unavailable

# ============================================================================
# STANDALONE TESTING
# ============================================================================
if __name__ == "__main__":
    print("📊 KELLY ENHANCED LAYER - REAL DATA TEST")
    print("=" * 70)
    
    result = calculate_kelly_enhanced("BTCUSDT")
    
    print("\n" + "=" * 70)
    print("📊 KELLY ANALYSIS:")
    print(f"   Available: {result['available']}")
    print(f"   Score: {result.get('score', 'N/A')}/100")
    print(f"   Volatility: {result.get('volatility_level', 'N/A')} ({result.get('atr_percent', 'N/A')}%)")
    print(f"   Market Regime: {result.get('market_regime', 'N/A')} (ADX: {result.get('adx', 'N/A')})")
    print(f"   Position Size: {result.get('position_size', 'N/A')}")
    print(f"   Kelly%: {result.get('kelly_percentage', 'N/A')}%")
    print("=" * 70)
