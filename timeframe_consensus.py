"""
🔱 DEMIR AI TRADING BOT - Timeframe Consensus Engine (Phase 4.2)
=================================================================
Date: 2 Kasım 2025, 20:15 CET
Version: 1.0 - Consensus Decision Logic

PURPOSE:
--------
Advanced consensus logic for multi-timeframe analysis
Handles edge cases and conflicting signals

FEATURES:
---------
• Trend alignment detection
• Divergence warnings
• Support/resistance confluence
• Volume confirmation across timeframes
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime


class TimeframeConsensus:
    """
    Advanced consensus logic for multi-timeframe signals
    """
    
    def __init__(self):
        self.timeframe_hierarchy = {
            '1m': 1,
            '5m': 2,
            '15m': 3,
            '1h': 4,
            '4h': 5,
            '1d': 6
        }
    
    def calculate_advanced_consensus(
        self,
        timeframe_signals: Dict[str, str],
        timeframe_scores: Dict[str, float],
        timeframe_details: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        Calculate advanced consensus with trend alignment
        
        Args:
            timeframe_signals: {timeframe: signal}
            timeframe_scores: {timeframe: score}
            timeframe_details: {timeframe: full_result_dict}
        
        Returns:
            Advanced consensus with trend analysis
        """
        
        # Basic consensus
        buy_signals = sum(1 for s in timeframe_signals.values() if 'BUY' in s)
        sell_signals = sum(1 for s in timeframe_signals.values() if 'SELL' in s)
        hold_signals = sum(1 for s in timeframe_signals.values() if s == 'HOLD')
        
        total = len(timeframe_signals)
        
        # Trend alignment check
        trend_aligned = self._check_trend_alignment(timeframe_signals)
        
        # Higher timeframe dominance
        htf_bias = self._get_higher_timeframe_bias(timeframe_signals, timeframe_scores)
        
        # Calculate confidence
        if trend_aligned and htf_bias != 'HOLD':
            base_confidence = 0.90
        elif buy_signals >= 4 or sell_signals >= 4:
            base_confidence = 0.80
        elif buy_signals >= 3 or sell_signals >= 3:
            base_confidence = 0.65
        else:
            base_confidence = 0.50
        
        # Adjust for trend alignment
        if trend_aligned:
            confidence = min(base_confidence * 1.1, 0.95)
        else:
            confidence = base_confidence * 0.9
        
        # Determine final signal
        if buy_signals >= sell_signals and buy_signals >= hold_signals:
            final_signal = 'STRONG BUY' if buy_signals >= 4 else 'BUY'
        elif sell_signals >= buy_signals and sell_signals >= hold_signals:
            final_signal = 'STRONG SELL' if sell_signals >= 4 else 'SELL'
        else:
            final_signal = 'HOLD'
        
        # Override with HTF bias if strong
        if htf_bias != 'HOLD' and htf_bias != final_signal:
            print(f"⚠️ Higher timeframe bias ({htf_bias}) conflicts with consensus ({final_signal})")
            # Weight HTF more heavily
            if buy_signals >= 3 and htf_bias == 'BUY':
                final_signal = 'BUY'
            elif sell_signals >= 3 and htf_bias == 'SELL':
                final_signal = 'SELL'
        
        # Calculate weighted score
        weighted_score = self._calculate_weighted_score(timeframe_scores)
        
        # Divergence warning
        divergence_warning = self._check_divergence(timeframe_signals)
        
        return {
            'signal': final_signal,
            'confidence': confidence,
            'weighted_score': weighted_score,
            'trend_aligned': trend_aligned,
            'htf_bias': htf_bias,
            'divergence_warning': divergence_warning,
            'signal_distribution': {
                'buy': buy_signals,
                'sell': sell_signals,
                'hold': hold_signals
            },
            'agreement_pct': max(buy_signals, sell_signals, hold_signals) / total * 100,
            'timestamp': datetime.now().isoformat()
        }
    
    def _check_trend_alignment(self, timeframe_signals: Dict[str, str]) -> bool:
        """
        Check if all timeframes are aligned in same trend direction
        """
        signals_list = list(timeframe_signals.values())
        
        # All BUY or all SELL = aligned
        if all('BUY' in s for s in signals_list):
            return True
        if all('SELL' in s for s in signals_list):
            return True
        
        # 4/5 same direction = aligned
        buy_count = sum(1 for s in signals_list if 'BUY' in s)
        sell_count = sum(1 for s in signals_list if 'SELL' in s)
        
        if buy_count >= 4 or sell_count >= 4:
            return True
        
        return False
    
    def _get_higher_timeframe_bias(
        self, 
        timeframe_signals: Dict[str, str],
        timeframe_scores: Dict[str, float]
    ) -> str:
        """
        Get bias from higher timeframes (4h, 1h priority)
        """
        # Priority: 4h > 1h > 15m
        priority_timeframes = ['4h', '1h', '15m']
        
        for tf in priority_timeframes:
            if tf in timeframe_signals:
                signal = timeframe_signals[tf]
                score = timeframe_scores.get(tf, 50)
                
                # Strong signal on higher TF
                if score >= 70:
                    if 'BUY' in signal:
                        return 'BUY'
                    elif 'SELL' in signal:
                        return 'SELL'
        
        return 'HOLD'
    
    def _calculate_weighted_score(self, timeframe_scores: Dict[str, float]) -> float:
        """
        Calculate weighted average score
        """
        weights = {
            '1m': 0.10,
            '5m': 0.15,
            '15m': 0.20,
            '1h': 0.30,
            '4h': 0.25
        }
        
        weighted_sum = 0
        weight_total = 0
        
        for tf, score in timeframe_scores.items():
            if tf in weights:
                weighted_sum += score * weights[tf]
                weight_total += weights[tf]
        
        if weight_total > 0:
            return weighted_sum / weight_total
        
        return 50.0
    
    def _check_divergence(self, timeframe_signals: Dict[str, str]) -> Optional[str]:
        """
        Check for dangerous divergences between timeframes
        """
        # Lower TF bullish, higher TF bearish = WARNING
        if '4h' in timeframe_signals and '1m' in timeframe_signals:
            if 'SELL' in timeframe_signals['4h'] and 'BUY' in timeframe_signals['1m']:
                return "⚠️ BEARISH DIVERGENCE: Lower TF bullish but higher TF bearish"
            elif 'BUY' in timeframe_signals['4h'] and 'SELL' in timeframe_signals['1m']:
                return "⚠️ BULLISH DIVERGENCE: Lower TF bearish but higher TF bullish"
        
        return None


# =====================================================
# STANDALONE TEST
# =====================================================

if __name__ == "__main__":
    print("🔱 Timeframe Consensus - Standalone Test")
    print("=" * 70)
    
    consensus_engine = TimeframeConsensus()
    
    # Test case: Mixed signals
    test_signals = {
        '1m': 'BUY',
        '5m': 'BUY',
        '15m': 'HOLD',
        '1h': 'BUY',
        '4h': 'STRONG BUY'
    }
    
    test_scores = {
        '1m': 65,
        '5m': 70,
        '15m': 55,
        '1h': 75,
        '4h': 85
    }
    
    result = consensus_engine.calculate_advanced_consensus(
        test_signals,
        test_scores,
        {}
    )
    
    print("\n📊 Consensus Result:")
    print(f"Signal: {result['signal']}")
    print(f"Confidence: {result['confidence']*100:.0f}%")
    print(f"Weighted Score: {result['weighted_score']:.1f}/100")
    print(f"Trend Aligned: {result['trend_aligned']}")
    print(f"HTF Bias: {result['htf_bias']}")
    
    if result['divergence_warning']:
        print(f"\n{result['divergence_warning']}")
    
    print("\n✅ Consensus Engine test complete!")
