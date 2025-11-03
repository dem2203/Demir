# ===========================================
# kelly_enhanced_layer.py v2.0 - SIMPLIFIED POSITION SIZING
# ===========================================
# ✅ Simplified Kelly Criterion (no trade history needed)
# ✅ Based on market conditions + volatility
# ✅ Conservative risk management
# ===========================================

"""
🔱 DEMIR AI TRADING BOT - Kelly Enhanced Layer v2.0
====================================================================
Tarih: 3 Kasım 2025, 22:28 CET
Versiyon: 2.0 - SIMPLIFIED KELLY WITHOUT TRADE HISTORY

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
- Win Rate = 55% (crypto trend following baseline)
- Avg Win/Loss Ratio = 1.5:1 (standard risk-reward)
- Adjusted by: Volatility, Trend Strength, Market Regime

POSITION SIZING:
----------------
Low volatility + Strong trend → 70-85 (larger position)
High volatility + Weak trend → 20-35 (smaller position)
Medium conditions → 45-55 (neutral position)

SCORING LOGIC:
--------------
Score represents recommended position size as % of ideal Kelly
100 = Full Kelly (1.0x)
75 = 3/4 Kelly (0.75x)
50 = Half Kelly (0.5x)
25 = Quarter Kelly (0.25x)
"""

import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any

# ============================================================================
# BINANCE API FUNCTIONS
# ============================================================================

def get_binance_klines(symbol: str = 'BTCUSDT', interval: str = '1h', limit: int = 100) -> pd.DataFrame:
    """
    Fetch OHLCV data from Binance API
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
        
        print(f"✅ Binance: {symbol} - {len(df)} candles loaded")
        return df
        
    except Exception as e:
        print(f"❌ Binance error ({symbol}): {e}")
        return None


# ============================================================================
# MARKET ANALYSIS FUNCTIONS
# ============================================================================

def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
    """Calculate Average True Range (volatility measure)"""
    try:
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr.iloc[-1]
    except:
        return 0.0


def detect_trend_strength(prices: pd.Series, period: int = 20) -> Dict[str, Any]:
    """
    Detect trend strength using ADX-like logic
    
    Returns:
        dict: trend_strength (0-100), trend_direction
    """
    try:
        # Simple trend detection: EMA slope
        ema = prices.ewm(span=period, adjust=False).mean()
        
        # Calculate slope
        slope = (ema.iloc[-1] - ema.iloc[-period]) / ema.iloc[-period] * 100
        
        # Trend strength (0-100)
        trend_strength = min(abs(slope) * 10, 100)
        
        # Direction
        if slope > 1:
            trend_direction = 'uptrend'
        elif slope < -1:
            trend_direction = 'downtrend'
        else:
            trend_direction = 'ranging'
        
        return {
            'strength': trend_strength,
            'direction': trend_direction,
            'slope': slope
        }
        
    except Exception as e:
        print(f"❌ Trend detection error: {e}")
        return {'strength': 50, 'direction': 'ranging', 'slope': 0}


def calculate_volatility_regime(atr: float, current_price: float) -> str:
    """
    Classify volatility regime
    
    Returns:
        'low', 'medium', or 'high'
    """
    try:
        atr_percent = (atr / current_price) * 100
        
        if atr_percent < 1.5:
            return 'low'
        elif atr_percent < 3.0:
            return 'medium'
        else:
            return 'high'
        
    except:
        return 'medium'


# ============================================================================
# KELLY CALCULATION
# ============================================================================

def calculate_simplified_kelly(
    trend_strength: float,
    volatility_regime: str,
    trend_direction: str
) -> Dict[str, Any]:
    """
    Calculate simplified Kelly position sizing
    
    Args:
        trend_strength: 0-100 (trend conviction)
        volatility_regime: 'low', 'medium', 'high'
        trend_direction: 'uptrend', 'downtrend', 'ranging'
    
    Returns:
        dict: Kelly score, recommended position size
    """
    # Base Kelly estimates (without trade history)
    base_win_rate = 0.55  # 55% baseline for crypto trend following
    base_risk_reward = 1.5  # 1.5:1 reward-to-risk ratio
    
    # Adjust win rate based on trend strength
    if trend_strength > 70:
        adjusted_win_rate = 0.60  # Strong trend = higher edge
    elif trend_strength > 40:
        adjusted_win_rate = 0.55  # Medium trend
    else:
        adjusted_win_rate = 0.50  # Weak trend = lower edge
    
    # Adjust for trend direction
    if trend_direction == 'ranging':
        adjusted_win_rate -= 0.05  # Harder in ranging markets
    
    # Kelly formula: (Win_Rate × Reward - Loss_Probability) / Reward
    loss_probability = 1 - adjusted_win_rate
    kelly_percent = (adjusted_win_rate * base_risk_reward - loss_probability) / base_risk_reward
    
    # Fractional Kelly (25% of full Kelly = safer)
    fractional_kelly = kelly_percent * 0.25
    
    # Adjust for volatility
    if volatility_regime == 'high':
        volatility_multiplier = 0.6
    elif volatility_regime == 'medium':
        volatility_multiplier = 0.8
    else:
        volatility_multiplier = 1.0
    
    final_kelly = fractional_kelly * volatility_multiplier
    
    # Convert to score (0-100)
    # 1.0 = 100 (full fractional Kelly)
    # 0.5 = 50 (half)
    # 0.0 = 0 (no position)
    kelly_score = final_kelly * 100
    kelly_score = max(15, min(85, kelly_score))  # Clamp to 15-85
    
    return {
        'kelly_percent': round(final_kelly, 4),
        'kelly_score': round(kelly_score, 2),
        'win_rate': round(adjusted_win_rate, 3),
        'risk_reward': base_risk_reward,
        'volatility_adjustment': volatility_multiplier
    }


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def analyze_kelly_position(symbol: str = 'BTCUSDT', interval: str = '1h') -> Dict[str, Any]:
    """
    Complete Kelly position sizing analysis
    
    Args:
        symbol: Trading pair (BTCUSDT, ETHUSDT, LTCUSDT)
        interval: Timeframe (1h, 4h, 1d)
    
    Returns:
        dict with score, signal, and Kelly details
    """
    print(f"\n{'='*80}")
    print(f"💰 KELLY ENHANCED LAYER v2.0 - POSITION SIZING")
    print(f"   Symbol: {symbol}")
    print(f"   Interval: {interval}")
    print(f"{'='*80}\n")
    
    # Fetch data from Binance
    df = get_binance_klines(symbol, interval, limit=100)
    
    if df is None or len(df) < 30:
        print("❌ Kelly: Insufficient data")
        return {
            'available': False,
            'score': 50,
            'signal': 'NEUTRAL',
            'reason': 'Insufficient data from Binance'
        }
    
    try:
        prices = df['close']
        high = df['high']
        low = df['low']
        current_price = prices.iloc[-1]
        
        # Calculate volatility
        atr = calculate_atr(high, low, prices)
        volatility_regime = calculate_volatility_regime(atr, current_price)
        
        # Detect trend
        trend_data = detect_trend_strength(prices)
        
        # Calculate Kelly
        kelly_result = calculate_simplified_kelly(
            trend_data['strength'],
            volatility_regime,
            trend_data['direction']
        )
        
        score = kelly_result['kelly_score']
        
        # Determine signal
        if score >= 65:
            signal = 'BULLISH'  # Larger position recommended
        elif score <= 35:
            signal = 'BEARISH'  # Smaller position recommended
        else:
            signal = 'NEUTRAL'  # Medium position
        
        # Print results
        print(f"📊 MARKET CONDITIONS:")
        print(f"   Trend Strength: {trend_data['strength']:.1f}/100")
        print(f"   Trend Direction: {trend_data['direction'].upper()}")
        print(f"   Volatility: {volatility_regime.upper()}")
        print(f"   ATR: ${atr:.2f}")
        
        print(f"\n📊 KELLY CALCULATION:")
        print(f"   Estimated Win Rate: {kelly_result['win_rate']:.1%}")
        print(f"   Risk/Reward Ratio: 1:{kelly_result['risk_reward']}")
        print(f"   Volatility Adjustment: {kelly_result['volatility_adjustment']:.2f}x")
        print(f"   Kelly Percent: {kelly_result['kelly_percent']:.2%}")
        
        print(f"\n{'='*80}")
        print(f"✅ KELLY ANALYSIS COMPLETE!")
        print(f"   Score: {score:.1f}/100")
        print(f"   Signal: {signal}")
        print(f"{'='*80}\n")
        
        return {
            'available': True,
            'score': score,
            'signal': signal,
            'kelly_percent': kelly_result['kelly_percent'],
            'win_rate': kelly_result['win_rate'],
            'risk_reward': kelly_result['risk_reward'],
            'trend_strength': round(trend_data['strength'], 2),
            'trend_direction': trend_data['direction'],
            'volatility': volatility_regime,
            'atr': round(atr, 2),
            'current_price': round(current_price, 2),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Kelly analysis error: {e}")
        return {
            'available': False,
            'score': 50,
            'signal': 'NEUTRAL',
            'reason': str(e)
        }


def get_kelly_signal(symbol: str = 'BTCUSDT') -> Dict[str, Any]:
    """
    Main function called by ai_brain.py
    
    Returns:
        dict: {'available': bool, 'score': float, 'signal': str}
    """
    result = analyze_kelly_position(symbol, interval='1h')
    
    return {
        'available': result['available'],
        'score': result.get('score', 50),
        'signal': result.get('signal', 'NEUTRAL'),
        'kelly_percent': result.get('kelly_percent', 0),
        'trend_strength': result.get('trend_strength', 0),
        'volatility': result.get('volatility', 'medium')
    }


# ============================================================================
# STANDALONE TESTING
# ============================================================================
if __name__ == "__main__":
    print("="*80)
    print("🔱 KELLY ENHANCED LAYER v2.0 TEST")
    print("   SIMPLIFIED POSITION SIZING")
    print("="*80)
    
    # Test with BTCUSDT
    result = get_kelly_signal('BTCUSDT')
    
    print("\n" + "="*80)
    print("📊 KELLY TEST RESULTS:")
    print(f"   Available: {result['available']}")
    print(f"   Score: {result.get('score', 'N/A')}/100")
    print(f"   Signal: {result.get('signal', 'N/A')}")
    print(f"   Kelly%: {result.get('kelly_percent', 'N/A'):.2%}")
    print(f"   Trend Strength: {result.get('trend_strength', 'N/A')}")
    print(f"   Volatility: {result.get('volatility', 'N/A')}")
    print("="*80)
