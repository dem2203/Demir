# multi_timeframe_analyzer.py v1.1 - FIXED
# ============================================================================
# 🔱 MULTI-TIMEFRAME ANALYZER - Phase 4.2 FIXED
# ============================================================================
# Date: 4 Kasım 2025, 00:43 CET
# Version: 1.1 - METHOD NAME FIXED
# 
# CRITICAL FIX:
# - Method name changed from analyze_multi_timeframe to analyze_all_timeframes
# - Now compatible with ai_brain.py calls
# ============================================================================

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
import requests

# ============================================================================
# BINANCE DATA FETCHER
# ============================================================================

def fetch_ohlcv(symbol: str, interval: str = '1h', limit: int = 100) -> pd.DataFrame:
    """
    Fetch OHLCV data from Binance
    
    Args:
        symbol: Trading pair (e.g., BTCUSDT)
        interval: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
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
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # Convert to numeric
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        
    except Exception as e:
        print(f"❌ OHLCV fetch error: {e}")
        return pd.DataFrame()

# ============================================================================
# TECHNICAL INDICATORS (SIMPLE)
# ============================================================================

def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    """Calculate RSI"""
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi.iloc[-1])
    except:
        return 50.0

def calculate_macd(prices: pd.Series) -> Dict[str, float]:
    """Calculate MACD"""
    try:
        ema12 = prices.ewm(span=12, adjust=False).mean()
        ema26 = prices.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': float(macd_line.iloc[-1]),
            'signal': float(signal_line.iloc[-1]),
            'histogram': float(histogram.iloc[-1])
        }
    except:
        return {'macd': 0, 'signal': 0, 'histogram': 0}

def calculate_ma_cross(prices: pd.Series) -> str:
    """Calculate MA crossover signal"""
    try:
        ma20 = prices.rolling(window=20).mean()
        ma50 = prices.rolling(window=50).mean()
        
        current_diff = ma20.iloc[-1] - ma50.iloc[-1]
        prev_diff = ma20.iloc[-2] - ma50.iloc[-2]
        
        if ma20.iloc[-1] > ma50.iloc[-1]:
            if prev_diff < 0:
                return "GOLDEN_CROSS"
            return "BULLISH"
        else:
            if prev_diff > 0:
                return "DEATH_CROSS"
            return "BEARISH"
    except:
        return "NEUTRAL"

# ============================================================================
# TIMEFRAME ANALYSIS
# ============================================================================

def analyze_single_timeframe(symbol: str, interval: str) -> Dict[str, Any]:
    """
    Analyze single timeframe
    
    Returns:
        Dict with score, signal, and indicators
    """
    try:
        df = fetch_ohlcv(symbol, interval=interval, limit=100)
        
        if df.empty:
            return {
                'timeframe': interval,
                'score': 50,
                'signal': 'NEUTRAL',
                'error': 'No data'
            }
        
        close_prices = df['close']
        
        # Calculate indicators
        rsi = calculate_rsi(close_prices)
        macd_data = calculate_macd(close_prices)
        ma_signal = calculate_ma_cross(close_prices)
        
        # Score calculation
        score = 50  # Base neutral
        
        # RSI contribution (30% weight)
        if rsi > 70:
            score -= 10  # Overbought
        elif rsi > 55:
            score += 5
        elif rsi < 30:
            score += 10  # Oversold
        elif rsi < 45:
            score -= 5
        
        # MACD contribution (30% weight)
        if macd_data['histogram'] > 0:
            score += 10
        else:
            score -= 10
        
        # MA crossover contribution (40% weight)
        if ma_signal == "GOLDEN_CROSS":
            score += 15
        elif ma_signal == "BULLISH":
            score += 10
        elif ma_signal == "DEATH_CROSS":
            score -= 15
        elif ma_signal == "BEARISH":
            score -= 10
        
        # Clip score
        score = np.clip(score, 0, 100)
        
        # Determine signal
        if score >= 65:
            signal = "LONG"
        elif score <= 35:
            signal = "SHORT"
        else:
            signal = "NEUTRAL"
        
        return {
            'timeframe': interval,
            'score': float(score),
            'signal': signal,
            'rsi': rsi,
            'macd': macd_data,
            'ma_signal': ma_signal,
            'current_price': float(close_prices.iloc[-1])
        }
        
    except Exception as e:
        print(f"⚠️ TF analysis error ({interval}): {e}")
        return {
            'timeframe': interval,
            'score': 50,
            'signal': 'NEUTRAL',
            'error': str(e)
        }

# ============================================================================
# MULTI-TIMEFRAME CONSENSUS
# ============================================================================

class MultiTimeframeAnalyzer:
    """
    Analyze multiple timeframes and generate consensus signal
    """
    
    def __init__(self):
        self.timeframes = ['5m', '15m', '1h', '4h', '1d']
    
    def analyze_all_timeframes(self, symbol: str) -> Dict[str, Any]:
        """
        FIXED METHOD NAME - was analyze_multi_timeframe
        
        Analyze symbol across all timeframes
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
        
        Returns:
            Dict with consensus score and individual TF results
        """
        try:
            print(f"\n📊 multi_timeframe.analyze_all_timeframes çağrılıyor...")
            print(f"   Symbol: {symbol}")
            print(f"   Timeframes: {', '.join(self.timeframes)}")
            
            results = []
            
            # Analyze each timeframe
            for tf in self.timeframes:
                result = analyze_single_timeframe(symbol, tf)
                results.append(result)
                print(f"   ✅ {tf}: Score={result['score']:.1f} ({result['signal']})")
            
            # Calculate consensus
            scores = [r['score'] for r in results if 'score' in r]
            signals = [r['signal'] for r in results if 'signal' in r]
            
            if not scores:
                return {
                    'score': 50,
                    'signal': 'NEUTRAL',
                    'confidence': 0,
                    'timeframe_results': results,
                    'error': 'No valid timeframe data'
                }
            
            # Weighted average (longer TF = more weight)
            weights = [1, 2, 3, 4, 5]  # 1d has highest weight
            weighted_score = np.average(scores, weights=weights[:len(scores)])
            
            # Count signal agreement
            long_count = signals.count('LONG')
            short_count = signals.count('SHORT')
            neutral_count = signals.count('NEUTRAL')
            
            total_signals = len(signals)
            
            # Determine consensus signal
            if long_count >= total_signals * 0.6:
                consensus_signal = "LONG"
                confidence = (long_count / total_signals) * 100
            elif short_count >= total_signals * 0.6:
                consensus_signal = "SHORT"
                confidence = (short_count / total_signals) * 100
            else:
                consensus_signal = "NEUTRAL"
                confidence = (neutral_count / total_signals) * 100
            
            print(f"\n   🎯 Consensus: {consensus_signal}")
            print(f"   📊 Weighted Score: {weighted_score:.1f}/100")
            print(f"   💪 Confidence: {confidence:.1f}%")
            print(f"   📈 Signals: {long_count}L / {neutral_count}N / {short_count}S")
            
            return {
                'score': float(weighted_score),
                'signal': consensus_signal,
                'confidence': float(confidence),
                'long_count': long_count,
                'short_count': short_count,
                'neutral_count': neutral_count,
                'timeframe_results': results
            }
            
        except Exception as e:
            print(f"⚠️ Multi-Timeframe layer hatası: {e}")
            return {
                'score': 50,
                'signal': 'NEUTRAL',
                'confidence': 0,
                'error': str(e)
            }

# ============================================================================
# STANDALONE FUNCTION (AI BRAIN COMPATIBLE)
# ============================================================================

def get_multi_timeframe_signal(symbol: str) -> float:
    """
    Standalone function for ai_brain compatibility
    
    Args:
        symbol: Trading pair
    
    Returns:
        float: Consensus score 0-100
    """
    analyzer = MultiTimeframeAnalyzer()
    result = analyzer.analyze_all_timeframes(symbol)
    
    score = result.get('score', 50)
    print(f"✅ Multi-Timeframe: {score:.2f}/100\n")
    
    return float(score)

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Test analyzer
    analyzer = MultiTimeframeAnalyzer()
    result = analyzer.analyze_all_timeframes("BTCUSDT")
    
    print("\n" + "="*80)
    print("📊 MULTI-TIMEFRAME ANALYSIS RESULT:")
    print(f"Score: {result['score']:.1f}/100")
    print(f"Signal: {result['signal']}")
    print(f"Confidence: {result['confidence']:.1f}%")
    
    # Test standalone function
    print("\n" + "="*80)
    score = get_multi_timeframe_signal("ETHUSDT")
    print(f"\n📊 STANDALONE FUNCTION TEST:")
    print(f"Score: {score:.1f}")
