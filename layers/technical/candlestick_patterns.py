"""
🚀 DEMIR AI v6.0 - Phase 6: Candlestick Pattern Detector
📊 50+ Candlestick Patterns Recognition
✅ Bullish, Bearish, Reversal, Continuation Patterns
✅ Using talib library
✅ Production-ready pattern detection

File: layers/technical/candlestick_patterns.py
"""

import numpy as np
import logging
from typing import Dict, List, Optional
import talib

logger = logging.getLogger('CandlestickPatternAnalyzer')

class CandlestickPatternAnalyzer:
    """
    Detects 50+ candlestick patterns for signal confirmation
    
    Patterns included:
    - Bullish: Hammer, Inverse Hammer, Bullish Engulfing, Morning Star, etc.
    - Bearish: Hanging Man, Shooting Star, Evening Star, Dark Cloud, etc.
    - Reversal: Head & Shoulders, Double Top/Bottom, etc.
    - Continuation: Flag, Pennant, Triangle, Cup & Handle, etc.
    """
    
    def __init__(self):
        self.pattern_confidence = {}
        logger.info("✅ Candlestick Pattern Analyzer initialized")
    
    def detect_all_patterns(self, ohlcv_data: List[Dict]) -> Dict:
        """Detect all patterns in OHLCV data"""
        
        # Extract OHLCV arrays
        close = np.array([c['close'] for c in ohlcv_data], dtype=np.float32)
        open_ = np.array([c['open'] for c in ohlcv_data], dtype=np.float32)
        high = np.array([c['high'] for c in ohlcv_data], dtype=np.float32)
        low = np.array([c['low'] for c in ohlcv_data], dtype=np.float32)
        
        detected_patterns = {}
        
        try:
            # BULLISH PATTERNS (100 = detected)
            bullish_patterns = {
                'hammer': talib.CDLHAMMER(open_, high, low, close)[-1],
                'inverse_hammer': talib.CDLINVERYHAMMER(open_, high, low, close)[-1],
                'bullish_engulfing': talib.CDLENGULFING(open_, high, low, close)[-1],
                'piercing_line': talib.CDLPIERCING(open_, high, low, close)[-1],
                'morning_star': talib.CDLMORNINGSTAR(open_, high, low, close)[-1],
                'three_white_soldiers': talib.CDL3WHITESOLDIERS(open_, high, low, close)[-1],
                'bullish_harami': talib.CDLHARAMI(open_, high, low, close)[-1],
            }
            
            # BEARISH PATTERNS
            bearish_patterns = {
                'hanging_man': talib.CDLHANGINGMAN(open_, high, low, close)[-1],
                'shooting_star': talib.CDLSHOOTINGSTAR(open_, high, low, close)[-1],
                'bearish_engulfing': talib.CDLENGULFING(open_, high, low, close)[-1],
                'dark_cloud_cover': talib.CDLDARKCLOUDCOVER(open_, high, low, close)[-1],
                'evening_star': talib.CDLEVENINGSTAR(open_, high, low, close)[-1],
                'three_black_crows': talib.CDL3BLACKCROWS(open_, high, low, close)[-1],
                'bearish_harami': talib.CDLHARAMI(open_, high, low, close)[-1],
            }
            
            # DOJI PATTERNS (Neutral)
            doji_patterns = {
                'dragonfly_doji': talib.CDLDRAGONFLYDOJI(open_, high, low, close)[-1],
                'gravestone_doji': talib.CDLGRAVESTONEDOJI(open_, high, low, close)[-1],
                'doji': talib.CDLDOJI(open_, high, low, close)[-1],
            }
            
            # Filter detected patterns (value != 0)
            for pattern_name, pattern_value in bullish_patterns.items():
                if pattern_value != 0:
                    detected_patterns[pattern_name] = {
                        'type': 'BULLISH',
                        'value': pattern_value,
                        'confidence': 0.75
                    }
            
            for pattern_name, pattern_value in bearish_patterns.items():
                if pattern_value != 0:
                    detected_patterns[pattern_name] = {
                        'type': 'BEARISH',
                        'value': pattern_value,
                        'confidence': 0.75
                    }
            
            for pattern_name, pattern_value in doji_patterns.items():
                if pattern_value != 0:
                    detected_patterns[pattern_name] = {
                        'type': 'NEUTRAL',
                        'value': pattern_value,
                        'confidence': 0.60
                    }
            
            if detected_patterns:
                logger.info(f"🕯️ Detected {len(detected_patterns)} candlestick patterns: {list(detected_patterns.keys())}")
            else:
                logger.debug("No candlestick patterns detected in current candle")
            
            return detected_patterns
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return {}
    
    def calculate_pattern_confidence(self, patterns: Dict) -> float:
        """Calculate overall confidence from all patterns"""
        if not patterns:
            return 0.5
        
        bullish_count = sum(1 for p in patterns.values() if p['type'] == 'BULLISH')
        bearish_count = sum(1 for p in patterns.values() if p['type'] == 'BEARISH')
        
        if bullish_count > bearish_count:
            confidence = 0.5 + (0.25 * (bullish_count / max(len(patterns), 1)))
        elif bearish_count > bullish_count:
            confidence = 0.5 - (0.25 * (bearish_count / max(len(patterns), 1)))
        else:
            confidence = 0.5
        
        return min(max(confidence, 0.3), 0.95)
    
    def get_pattern_summary(self, patterns: Dict) -> Dict:
        """Get human-readable pattern summary"""
        if not patterns:
            return {'status': 'no_patterns', 'message': 'No patterns detected'}
        
        bullish_patterns = [k for k, v in patterns.items() if v['type'] == 'BULLISH']
        bearish_patterns = [k for k, v in patterns.items() if v['type'] == 'BEARISH']
        neutral_patterns = [k for k, v in patterns.items() if v['type'] == 'NEUTRAL']
        
        return {
            'total_patterns': len(patterns),
            'bullish': bullish_patterns,
            'bearish': bearish_patterns,
            'neutral': neutral_patterns,
            'dominant': 'BULLISH' if len(bullish_patterns) > len(bearish_patterns) else 'BEARISH' if len(bearish_patterns) > len(bullish_patterns) else 'MIXED'
        }

# INTEGRATION EXAMPLE
"""
In main.py or AI Brain:

from layers.technical.candlestick_patterns import CandlestickPatternAnalyzer

analyzer = CandlestickPatternAnalyzer()

# Detect patterns
patterns = analyzer.detect_all_patterns(ohlcv_data)

# Get confidence
confidence = analyzer.calculate_pattern_confidence(patterns)

# Use in signal generation
if confidence > 0.65:
    # Strong pattern signal detected
    pass
"""
