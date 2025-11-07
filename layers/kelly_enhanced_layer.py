# kelly_enhanced_layer.py - WITH SOURCE TRACKING (UPDATED)
# 7 Kasım 2025 - v2.3 - Source field eklendi

import requests
import pandas as pd
from typing import Dict, Tuple, Optional, Any
import time

def calculate_atr(df: pd.DataFrame, period: int = 14) -> Optional[float]:
    """Calculate Average True Range"""
    try:
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(period).mean()
        return atr.iloc[-1] if not atr.empty else None
    except Exception as e:
        print(f"ATR Calculation Error: {e}")
        return None

def calculate_adx(df: pd.DataFrame, period: int = 14) -> Optional[float]:
    """Calculate Average Directional Index"""
    try:
        plus_dm = df['high'].diff()
        minus_dm = -df['low'].diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr1 = df['high'] - df['low']
        tr2 = abs(df['high'] - df['close'].shift())
        tr3 = abs(df['low'] - df['close'].shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr_val = tr.rolling(period).mean()
        di_plus = 100 * (plus_dm.rolling(period).mean() / atr_val)
        di_minus = 100 * (minus_dm.rolling(period).mean() / atr_val)
        
        di_diff = abs(di_plus - di_minus)
        adx = di_diff.rolling(period).mean()
        
        return adx.iloc[-1] if not adx.empty else None
    except Exception as e:
        print(f"ADX Calculation Error: {e}")
        return None

def calculate_dynamic_kelly(symbol: str = 'BTCUSDT') -> Dict[str, Any]:
    """
    Calculate Kelly Criterion-based position sizing
    Enhanced with volatility analysis and market regime detection
    UPDATED: Added 'source': 'REAL' field
    """
    
    try:
        print(f"📊 Calculating Kelly-Enhanced Position Sizing for {symbol}...")
        
        # Fetch price data from Binance
        try:
            url = f'https://api.binance.com/api/v3/klines'
            params = {
                'symbol': symbol,
                'interval': '1h',
                'limit': 100
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Error fetching data: {e}")
            return {
                'available': False,
                'score': 50,
                'reason': 'Failed to fetch price data',
                'source': 'ERROR'
            }
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'volume', 
                                        'close_time', 'quote_asset_volume', 'trades',
                                        'taker_buy_base', 'taker_buy_quote', 'ignore'])
        df['close'] = pd.to_numeric(df['close'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        
        # ==========================================
        # 1. VOLATILITY ANALYSIS (ATR)
        # ==========================================
        current_price = df['close'].iloc[-1]
        atr = calculate_atr(df, period=14)
        
        if atr is None:
            return {
                'available': False,
                'score': 50,
                'reason': 'ATR calculation failed',
                'source': 'ERROR'
            }
        
        atr_percent = (atr / current_price) * 100
        
        # ==========================================
        # 2. MARKET REGIME DETECTION (ADX)
        # ==========================================
        adx = calculate_adx(df, period=14)
        
        if adx is not None and adx >= 25:
            market_regime = 'TRENDING'
        elif adx is not None and adx < 20:
            market_regime = 'RANGING'
        else:
            market_regime = 'NEUTRAL'
        
        # ==========================================
        # 3. KELLY SCORE CALCULATION
        # ==========================================
        
        if atr_percent < 0.5:
            volatility_level = 'VERY_LOW'
            vol_score = 90
        elif atr_percent < 1.0:
            volatility_level = 'LOW'
            vol_score = 75
        elif atr_percent < 2.0:
            volatility_level = 'MODERATE'
            vol_score = 60
        elif atr_percent < 3.0:
            volatility_level = 'HIGH'
            vol_score = 40
        else:
            volatility_level = 'VERY_HIGH'
            vol_score = 20
        
        # Regime adjustment
        if market_regime == 'TRENDING':
            regime_multiplier = 1.1
        elif market_regime == 'RANGING':
            regime_multiplier = 0.85
        else:
            regime_multiplier = 1.0
        
        kelly_score = vol_score * regime_multiplier
        kelly_score = min(100, max(0, kelly_score))
        
        # Position sizing recommendation
        if kelly_score >= 80:
            position_size = 'LARGE'
        elif kelly_score >= 60:
            position_size = 'MEDIUM'
        elif kelly_score >= 40:
            position_size = 'SMALL'
        else:
            position_size = 'MINIMAL'
        
        result = {
            'available': True,
            'score': kelly_score,
            'signal': 'KELLY_OPTIMIZED',
            'volatility': volatility_level,
            'atr_percent': round(atr_percent, 3),
            'adx': round(adx, 2) if adx else None,
            'market_regime': market_regime,
            'position_size': position_size,
            'source': 'REAL'  # ← ADDED: Source tracking
        }
        
        print(f"✅ Kelly Analysis Complete!")
        print(f"   Volatility: {volatility_level} (ATR: {atr_percent:.3f}%)")
        print(f"   Market Regime: {market_regime} (ADX: {adx:.2f if adx else 'N/A'})")
        print(f"   Kelly Score: {kelly_score:.2f}/100")
        print(f"   Position Size: {position_size}")
        
        return result
        
    except Exception as e:
        print(f"Kelly Calculation Error: {str(e)}")
        return {
            'available': False,
            'score': 50,
            'reason': str(e),
            'source': 'ERROR'
        }

if __name__ == "__main__":
    print("="*80)
    print("🎯 KELLY ENHANCED LAYER v2.3 TEST")
    print("="*80)
    result = calculate_dynamic_kelly('BTCUSDT')
    print(f"\n📊 Result: {result}")
