"""
DEMIR AI v6.0 - PHASE 4 [57/NEW]
Multi-Timeframe Confluence Analyzer
Divergence Detection, Alignment Scoring, Real-Time Processing
Production-Grade Multi-Timeframe Analysis Engine
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class MultiTimeframeConfluenceAnalyzer:
    """Analyze confluence and divergence across timeframes"""
    
    def __init__(self):
        """Initialize confluence analyzer"""
        self.timeframe_hierarchy = ['15m', '1h', '4h', '1d']
        self.convergence_threshold = 0.7
        self.divergence_threshold = 0.3
        logger.info("📊 MultiTimeframe Confluence Analyzer initialized")
    
    def analyze_confluence(self, timeframes_data: Dict[str, List[Dict]], symbol: str) -> Dict[str, any]:
        """Comprehensive confluence analysis across all timeframes"""
        
        try:
            if not timeframes_data or len(timeframes_data) < 2:
                return {'error': 'Insufficient timeframe data', 'confluence': 0.5}
            
            # Calculate direction score for each timeframe
            directions = {}
            scores = {}
            
            for tf in self.timeframe_hierarchy:
                if tf not in timeframes_data or len(timeframes_data[tf]) < 1:
                    continue
                
                latest = timeframes_data[tf][-1]
                
                # Determine direction
                direction = 'LONG' if latest['close'] > latest['open'] else 'SHORT'
                directions[tf] = direction
                
                # Calculate confidence score (0-1)
                body = abs(latest['close'] - latest['open'])
                wick = latest['high'] - latest['low']
                
                if wick > 0:
                    candle_strength = body / wick
                else:
                    candle_strength = 0.5
                
                scores[tf] = candle_strength
                
                logger.debug(f"{symbol} {tf}: {direction} (strength: {candle_strength:.2f})")
            
            if not directions:
                return {'error': 'No valid timeframe data', 'confluence': 0.5}
            
            # Calculate alignment score
            alignment_score = self._calculate_alignment(directions, scores)
            
            # Detect divergences
            divergences = self._detect_divergences(directions)
            
            # Calculate confluence score (0-100%)
            confluence_pct = alignment_score
            
            # Determine alignment type
            alignment_type = self._classify_alignment(confluence_pct, len(divergences))
            
            # Calculate multi-timeframe strength
            tf_strength = self._calculate_timeframe_strength(scores)
            
            result = {
                'symbol': symbol,
                'confluence': float(alignment_score),
                'confluence_pct': float(confluence_pct * 100),
                'alignment': alignment_type,
                'directions': directions,
                'scores': scores,
                'timeframe_strength': tf_strength,
                'has_divergence': len(divergences) > 0,
                'divergences': divergences,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Confluence analysis: {symbol} | Score: {confluence_pct:.1%} | Alignment: {alignment_type}")
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Confluence analysis error: {e}")
            return {'error': str(e), 'confluence': 0.5}
    
    def _calculate_alignment(self, directions: Dict[str, str], scores: Dict[str, float]) -> float:
        """Calculate alignment score based on direction agreement"""
        if not directions:
            return 0.5
        
        # Count votes
        long_votes = sum(1 for d in directions.values() if d == 'LONG')
        short_votes = sum(1 for d in directions.values() if d == 'SHORT')
        total_votes = long_votes + short_votes
        
        if total_votes == 0:
            return 0.5
        
        # Agreement ratio
        max_votes = max(long_votes, short_votes)
        agreement_ratio = max_votes / total_votes
        
        # Weight by timeframe importance (1d > 4h > 1h > 15m)
        weighted_score = 0
        weight_total = 0
        
        weights = {'1d': 4, '4h': 3, '1h': 2, '15m': 1}
        
        for tf, direction in directions.items():
            weight = weights.get(tf, 1)
            score = scores.get(tf, 0.5)
            
            # LONG = 1, SHORT = 0
            direction_value = 1 if direction == 'LONG' else 0
            
            weighted_score += (direction_value * score * weight)
            weight_total += (score * weight)
        
        if weight_total > 0:
            final_score = weighted_score / weight_total
        else:
            final_score = 0.5
        
        return float(final_score)
    
    def _detect_divergences(self, directions: Dict[str, str]) -> List[str]:
        """Detect divergences between adjacent timeframes"""
        divergences = []
        tf_list = self.timeframe_hierarchy
        
        for i in range(len(tf_list) - 1):
            tf1 = tf_list[i]
            tf2 = tf_list[i + 1]
            
            if tf1 not in directions or tf2 not in directions:
                continue
            
            if directions[tf1] != directions[tf2]:
                divergence = f"DIVERGENCE: {tf1} {directions[tf1]} vs {tf2} {directions[tf2]}"
                divergences.append(divergence)
                logger.warning(divergence)
        
        return divergences
    
    def _classify_alignment(self, confluence_pct: float, divergence_count: int) -> str:
        """Classify alignment type"""
        if divergence_count >= 2:
            return 'STRONG_DIVERGENCE'
        elif divergence_count == 1:
            return 'MINOR_DIVERGENCE'
        elif confluence_pct >= 0.85:
            return 'VERY_STRONG'
        elif confluence_pct >= 0.7:
            return 'STRONG'
        elif confluence_pct >= 0.5:
            return 'MODERATE'
        elif confluence_pct >= 0.3:
            return 'WEAK'
        else:
            return 'VERY_WEAK'
    
    def _calculate_timeframe_strength(self, scores: Dict[str, float]) -> Dict[str, str]:
        """Calculate strength for each timeframe"""
        strength_map = {}
        
        for tf, score in scores.items():
            if score >= 0.75:
                strength = 'VERY_STRONG'
            elif score >= 0.6:
                strength = 'STRONG'
            elif score >= 0.45:
                strength = 'MODERATE'
            elif score >= 0.3:
                strength = 'WEAK'
            else:
                strength = 'VERY_WEAK'
            
            strength_map[tf] = strength
        
        return strength_map


class DivergenceDetector:
    """Specialized divergence detection between price and indicators"""
    
    def __init__(self):
        """Initialize divergence detector"""
        self.min_divergence_length = 2  # Minimum bars for divergence
        logger.info("🔍 Divergence Detector initialized")
    
    def detect_price_divergence(self, prices: List[float], rsi: List[float]) -> Dict[str, any]:
        """Detect divergence between price and RSI"""
        
        if len(prices) < 5 or len(rsi) < 5:
            return {'has_divergence': False, 'type': 'INSUFFICIENT_DATA'}
        
        try:
            # Find recent high and low
            recent_prices = prices[-10:]
            recent_rsi = rsi[-10:]
            
            price_high_idx = recent_prices.index(max(recent_prices))
            price_low_idx = recent_prices.index(min(recent_prices))
            
            rsi_high_idx = recent_rsi.index(max(recent_rsi))
            rsi_low_idx = recent_rsi.index(min(recent_rsi))
            
            # Bullish divergence: price makes lower low, RSI makes higher low
            bullish = (price_low_idx > rsi_low_idx and 
                      recent_prices[-1] < recent_prices[price_low_idx] and
                      recent_rsi[-1] > recent_rsi[rsi_low_idx])
            
            # Bearish divergence: price makes higher high, RSI makes lower high
            bearish = (price_high_idx > rsi_high_idx and
                      recent_prices[-1] > recent_prices[price_high_idx] and
                      recent_rsi[-1] < recent_rsi[rsi_high_idx])
            
            if bullish:
                return {'has_divergence': True, 'type': 'BULLISH', 'strength': 0.7}
            elif bearish:
                return {'has_divergence': True, 'type': 'BEARISH', 'strength': 0.7}
            else:
                return {'has_divergence': False, 'type': 'NONE'}
        
        except Exception as e:
            logger.error(f"Divergence detection error: {e}")
            return {'has_divergence': False, 'type': 'ERROR', 'error': str(e)}
    
    def detect_macd_divergence(self, prices: List[float], macd: List[float]) -> Dict[str, any]:
        """Detect divergence between price and MACD"""
        
        if len(prices) < 5 or len(macd) < 5:
            return {'has_divergence': False}
        
        try:
            recent_prices = prices[-10:]
            recent_macd = macd[-10:]
            
            # Trend analysis
            price_trend = 'UP' if recent_prices[-1] > recent_prices[0] else 'DOWN'
            macd_trend = 'UP' if recent_macd[-1] > recent_macd[0] else 'DOWN'
            
            if price_trend != macd_trend:
                return {
                    'has_divergence': True,
                    'type': f"{price_trend}_Price_vs_{macd_trend}_MACD",
                    'strength': 0.6
                }
            else:
                return {'has_divergence': False}
        
        except Exception as e:
            logger.error(f"MACD divergence error: {e}")
            return {'has_divergence': False}


class ConvergenceScorer:
    """Score convergence quality across timeframes"""
    
    @staticmethod
    def calculate_quality_score(confluence_data: Dict) -> float:
        """Calculate overall convergence quality (0-1)"""
        
        try:
            confidence = confluence_data.get('confluence', 0.5)
            has_divergence = confluence_data.get('has_divergence', False)
            divergences = confluence_data.get('divergences', [])
            
            # Base score from confluence
            score = confidence
            
            # Penalty for divergences
            divergence_penalty = len(divergences) * 0.1
            score -= divergence_penalty
            
            # Bonus for strong alignment
            alignment = confluence_data.get('alignment', 'MODERATE')
            alignment_bonus = {
                'VERY_STRONG': 0.1,
                'STRONG': 0.05,
                'MODERATE': 0,
                'WEAK': -0.05,
                'VERY_WEAK': -0.1,
                'MINOR_DIVERGENCE': -0.05,
                'STRONG_DIVERGENCE': -0.15
            }.get(alignment, 0)
            
            score += alignment_bonus
            
            # Clamp to 0-1
            return float(np.clip(score, 0, 1))
        
        except Exception as e:
            logger.error(f"Score calculation error: {e}")
            return 0.5


class ConfluenceAlertSystem:
    """Generate alerts based on confluence analysis"""
    
    def __init__(self, alert_threshold: float = 0.7):
        """Initialize alert system"""
        self.alert_threshold = alert_threshold
        self.previous_states = {}
        logger.info("🚨 Confluence Alert System initialized")
    
    def check_alerts(self, symbol: str, confluence_data: Dict) -> List[Dict]:
        """Check for confluence-based trading alerts"""
        
        alerts = []
        confluence = confluence_data.get('confluence', 0.5)
        alignment = confluence_data.get('alignment', 'MODERATE')
        
        # Alert: Strong convergence detected
        if confluence >= self.alert_threshold and alignment == 'STRONG':
            direction = 'LONG' if confluence > 0.5 else 'SHORT'
            alerts.append({
                'type': 'STRONG_CONVERGENCE',
                'symbol': symbol,
                'direction': direction,
                'confidence': confluence,
                'message': f"🎯 STRONG {direction} SIGNAL - All timeframes aligned!"
            })
        
        # Alert: Divergence detected
        if confluence_data.get('has_divergence'):
            alerts.append({
                'type': 'DIVERGENCE_WARNING',
                'symbol': symbol,
                'divergences': confluence_data.get('divergences', []),
                'message': f"⚠️ DIVERGENCE - Multiple timeframes disagreeing"
            })
        
        # Alert: Alignment changed
        previous_state = self.previous_states.get(symbol, {})
        if previous_state.get('alignment') != alignment:
            alerts.append({
                'type': 'ALIGNMENT_CHANGE',
                'symbol': symbol,
                'from': previous_state.get('alignment'),
                'to': alignment,
                'message': f"🔄 Alignment changed: {previous_state.get('alignment')} → {alignment}"
            })
        
        # Update state
        self.previous_states[symbol] = confluence_data
        
        return alerts
