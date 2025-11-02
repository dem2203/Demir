"""
🔱 DEMIR AI TRADING BOT - Multi-Timeframe Analyzer (Phase 4.2)
===============================================================
Date: 2 Kasım 2025, 20:10 CET
Version: 1.0 - Multi-Timeframe Consensus System

PURPOSE:
--------
Analyze same coin across multiple timeframes simultaneously
Generate consensus signal with higher accuracy

TIMEFRAMES:
-----------
• 1m - Ultra-short (scalping)
• 5m - Short-term (day trading)
• 15m - Intraday
• 1h - Medium-term (swing)
• 4h - Position trading

CONSENSUS LOGIC:
----------------
All timeframes must agree (or majority 4/5) for strong signal
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any

# Import AI Brain for single-timeframe analysis
try:
    from ai_brain import make_trading_decision
    AI_BRAIN_AVAILABLE = True
except:
    AI_BRAIN_AVAILABLE = False
    print("⚠️ Multi-TF: ai_brain not available")


class MultiTimeframeAnalyzer:
    """
    Analyze same symbol across multiple timeframes
    Generate consensus trading signal
    """
    
    def __init__(self):
        self.timeframes = ['1m', '5m', '15m', '1h', '4h']
        self.weights = {
            '1m': 0.10,  # 10% - Noise filter
            '5m': 0.15,  # 15% - Short-term
            '15m': 0.20,  # 20% - Intraday
            '1h': 0.30,  # 30% - Primary
            '4h': 0.25   # 25% - Trend confirmation
        }
    
    def analyze_multi_timeframe(
        self, 
        symbol: str = 'BTCUSDT',
        capital: float = 10000.0,
        lookback: int = 100
    ) -> Dict[str, Any]:
        """
        Analyze symbol across all timeframes
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            capital: Portfolio value in USDT
            lookback: Number of candles to analyze
        
        Returns:
            dict: Consensus analysis with all timeframe results
        """
        
        if not AI_BRAIN_AVAILABLE:
            return self._generate_fallback_result(symbol)
        
        print(f"\n{'='*70}")
        print(f"🕐 MULTI-TIMEFRAME ANALYSIS - {symbol}")
        print(f"{'='*70}")
        
        timeframe_results = {}
        signals = []
        scores = []
        
        # Analyze each timeframe
        for tf in self.timeframes:
            try:
                print(f"\n📊 Analyzing {tf} timeframe...")
                
                result = make_trading_decision(
                    symbol=symbol,
                    timeframe=tf,
                    capital=capital,
                    lookback=lookback
                )
                
                if result:
                    timeframe_results[tf] = result
                    signals.append(result.get('signal', 'HOLD'))
                    scores.append(result.get('score', 50))
                    
                    print(f"✅ {tf}: {result.get('signal')} - {result.get('score'):.1f}/100")
                else:
                    print(f"⚠️ {tf}: No result")
                    timeframe_results[tf] = None
                    signals.append('HOLD')
                    scores.append(50)
                    
            except Exception as e:
                print(f"❌ {tf} analysis error: {e}")
                timeframe_results[tf] = None
                signals.append('HOLD')
                scores.append(50)
        
        # Generate consensus
        consensus = self._calculate_consensus(
            timeframe_results, 
            signals, 
            scores
        )
        
        return consensus
    
    def _calculate_consensus(
        self, 
        timeframe_results: Dict,
        signals: List[str],
        scores: List[float]
    ) -> Dict[str, Any]:
        """
        Calculate consensus signal from all timeframes
        
        Logic:
        - If all timeframes agree → STRONG signal
        - If 4/5 agree → MODERATE signal
        - If 3/5 agree → WEAK signal
        - Otherwise → HOLD
        """
        
        # Count signal types
        buy_count = signals.count('BUY') + signals.count('STRONG BUY')
        sell_count = signals.count('SELL') + signals.count('STRONG SELL')
        hold_count = signals.count('HOLD')
        
        total = len(signals)
        
        # Calculate weighted average score
        weighted_score = 0
        for i, tf in enumerate(self.timeframes):
            weighted_score += scores[i] * self.weights[tf]
        
        # Determine consensus signal
        if buy_count >= 5:  # All agree BUY
            consensus_signal = 'STRONG BUY'
            confidence = 0.95
        elif buy_count >= 4:  # 4/5 agree BUY
            consensus_signal = 'BUY'
            confidence = 0.80
        elif buy_count >= 3:  # 3/5 agree BUY
            consensus_signal = 'BUY'
            confidence = 0.65
        elif sell_count >= 5:  # All agree SELL
            consensus_signal = 'STRONG SELL'
            confidence = 0.95
        elif sell_count >= 4:  # 4/5 agree SELL
            consensus_signal = 'SELL'
            confidence = 0.80
        elif sell_count >= 3:  # 3/5 agree SELL
            consensus_signal = 'SELL'
            confidence = 0.65
        else:
            consensus_signal = 'HOLD'
            confidence = 0.50
        
        # Agreement percentage
        agreement = max(buy_count, sell_count, hold_count) / total * 100
        
        # Generate summary
        print(f"\n{'='*70}")
        print(f"🎯 CONSENSUS RESULT")
        print(f"{'='*70}")
        print(f"Signal: {consensus_signal}")
        print(f"Confidence: {confidence*100:.0f}%")
        print(f"Weighted Score: {weighted_score:.1f}/100")
        print(f"Agreement: {agreement:.0f}% ({max(buy_count, sell_count, hold_count)}/{total} timeframes)")
        print(f"BUY: {buy_count} | SELL: {sell_count} | HOLD: {hold_count}")
        print(f"{'='*70}\n")
        
        return {
            'signal': consensus_signal,
            'confidence': confidence,
            'score': weighted_score,
            'agreement': agreement,
            'timeframe_breakdown': {
                'buy_count': buy_count,
                'sell_count': sell_count,
                'hold_count': hold_count
            },
            'timeframe_results': timeframe_results,
            'individual_signals': dict(zip(self.timeframes, signals)),
            'individual_scores': dict(zip(self.timeframes, scores)),
            'timestamp': datetime.now().isoformat(),
            'version': 'v1.0-phase4.2'
        }
    
    def _generate_fallback_result(self, symbol: str) -> Dict[str, Any]:
        """Generate fallback result when AI Brain unavailable"""
        return {
            'signal': 'HOLD',
            'confidence': 0.50,
            'score': 50.0,
            'agreement': 0,
            'timeframe_breakdown': {
                'buy_count': 0,
                'sell_count': 0,
                'hold_count': 5
            },
            'timeframe_results': {},
            'individual_signals': {tf: 'HOLD' for tf in self.timeframes},
            'individual_scores': {tf: 50.0 for tf in self.timeframes},
            'timestamp': datetime.now().isoformat(),
            'version': 'v1.0-phase4.2-fallback',
            'error': 'AI Brain not available'
        }


# =====================================================
# STANDALONE TEST
# =====================================================

if __name__ == "__main__":
    print("🔱 Multi-Timeframe Analyzer - Standalone Test")
    print("=" * 70)
    
    analyzer = MultiTimeframeAnalyzer()
    
    result = analyzer.analyze_multi_timeframe(
        symbol='BTCUSDT',
        capital=10000.0,
        lookback=100
    )
    
    print("\n📊 Final Result:")
    print(f"Signal: {result['signal']}")
    print(f"Confidence: {result['confidence']*100:.0f}%")
    print(f"Score: {result['score']:.1f}/100")
    print(f"Agreement: {result['agreement']:.0f}%")
    
    print("\n✅ Multi-Timeframe Analyzer test complete!")
