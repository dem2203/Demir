"""
🧠 DEMIR AI v8.0 - AI META-LAYER INTERPRETER

Enterprise-grade meta-analysis engine that orchestrates 5 independent signal groups:
- Technical Analysis Layer
- Sentiment Analysis Layer  
- Machine Learning Layer
- On-Chain Analytics Layer
- Risk Management Layer

Generates consensus signals with AI-powered natural language reasoning.
ZERO mock data, ZERO fallback, production-grade only.

Author: DEMIR AI Research Team
Version: 8.0
Date: 2025-11-21
"""

import logging
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from collections import Counter
import statistics

logger = logging.getLogger('AI_META_INTERPRETER')

class AIMetaInterpreter:
    """
    AI Meta-Layer: Ensemble intelligence coordinator
    
    Responsibilities:
    1. Collect signals from 5 independent group layers
    2. Calculate weighted consensus (majority voting + confidence weighting)
    3. Detect divergences and conflicts between groups
    4. Generate natural language AI reasoning
    5. Produce final meta-signal with actionable recommendations
    
    Signal Flow:
    Technical → 
    Sentiment →  [AI META-LAYER] → Meta Signal + AI Commentary
    ML Models →
    On-Chain  →
    Risk Mgmt →
    
    Output Format:
    {
        'meta_signal': 'LONG/SHORT/NEUTRAL',
        'consensus_strength': 0-100,
        'confidence': 0-100,
        'recommended_action': 'BUY/SELL/HOLD/WAIT',
        'entry_price': float,
        'targets': [tp1, tp2, tp3],
        'stop_loss': float,
        'risk_reward': float,
        'ai_reasoning': 'Natural language explanation...',
        'supporting_groups': ['technical', 'ml', ...],
        'opposing_groups': ['risk', ...],
        'divergences': [...],
        'group_details': {...}
    }
    """
    
    def __init__(self):
        """
        Initialize AI Meta-Interpreter with production-grade settings
        """
        self.group_weights = {
            'technical': 0.25,   # 25% - Price action and indicators
            'sentiment': 0.20,   # 20% - Market mood and news
            'ml': 0.25,          # 25% - Machine learning predictions
            'onchain': 0.15,     # 15% - Blockchain metrics
            'risk': 0.15         # 15% - Risk assessment
        }
        
        # Minimum groups required for valid meta-signal
        self.min_groups_required = 3
        
        # Consensus threshold (% of groups that must agree)
        self.consensus_threshold = 0.60  # 60%
        
        # Confidence adjustment factors
        self.confidence_boost_unanimous = 1.2  # +20% if all agree
        self.confidence_penalty_divergence = 0.8  # -20% if major divergence
        
        logger.info("✅ AI Meta-Interpreter initialized (5-group ensemble)")
    
    def interpret_group_signals(
        self,
        symbol: str,
        group_signals: Dict[str, Dict[str, Any]],
        current_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Main interpretation method: Analyze all group signals and produce meta-signal
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            group_signals: Dictionary of group signals
                {
                    'technical': {'direction': 'LONG', 'confidence': 78, 'strength': 82, ...},
                    'sentiment': {'direction': 'LONG', 'confidence': 65, 'strength': 70, ...},
                    'ml': {'direction': 'LONG', 'confidence': 72, 'strength': 68, ...},
                    'onchain': {'direction': 'NEUTRAL', 'confidence': 55, 'strength': 50, ...},
                    'risk': {'direction': 'SHORT', 'confidence': 60, 'strength': 65, ...}
                }
            current_price: Current market price (optional, for entry/TP/SL calculation)
        
        Returns:
            Meta-signal dictionary with AI reasoning
        """
        try:
            # Validate input
            if not group_signals or len(group_signals) < self.min_groups_required:
                logger.error(f"❌ Insufficient group signals: {len(group_signals)}/{self.min_groups_required} required")
                return self._error_response(
                    symbol,
                    f"Only {len(group_signals)} groups available, need {self.min_groups_required}"
                )
            
            # Extract directions and confidences
            directions = []
            confidences = []
            strengths = []
            valid_groups = []
            
            for group_name, signal in group_signals.items():
                if signal and signal.get('direction') and signal.get('confidence'):
                    directions.append(signal['direction'])
                    confidences.append(float(signal.get('confidence', 0)))
                    strengths.append(float(signal.get('strength', 0)))
                    valid_groups.append(group_name)
            
            if len(valid_groups) < self.min_groups_required:
                logger.error(f"❌ Insufficient valid signals: {len(valid_groups)}/{self.min_groups_required}")
                return self._error_response(
                    symbol,
                    f"Only {len(valid_groups)} valid signals"
                )
            
            # Calculate consensus direction (weighted majority voting)
            consensus_direction, consensus_strength = self._calculate_consensus(
                group_signals,
                valid_groups
            )
            
            # Calculate aggregate confidence
            aggregate_confidence = self._calculate_aggregate_confidence(
                confidences,
                consensus_direction,
                group_signals,
                valid_groups
            )
            
            # Identify supporting and opposing groups
            supporting_groups = [
                g for g in valid_groups
                if group_signals[g]['direction'] == consensus_direction
            ]
            opposing_groups = [
                g for g in valid_groups
                if group_signals[g]['direction'] != consensus_direction
                and group_signals[g]['direction'] != 'NEUTRAL'
            ]
            neutral_groups = [
                g for g in valid_groups
                if group_signals[g]['direction'] == 'NEUTRAL'
            ]
            
            # Detect divergences
            divergences = self._detect_divergences(
                group_signals,
                valid_groups,
                consensus_direction
            )
            
            # Determine recommended action
            recommended_action = self._determine_action(
                consensus_direction,
                consensus_strength,
                aggregate_confidence,
                len(divergences)
            )
            
            # Calculate entry, targets, stop-loss
            entry_price, targets, stop_loss, risk_reward = self._calculate_levels(
                symbol,
                consensus_direction,
                current_price,
                group_signals,
                valid_groups
            )
            
            # Generate AI natural language reasoning
            ai_reasoning = self._generate_ai_reasoning(
                symbol,
                consensus_direction,
                consensus_strength,
                aggregate_confidence,
                supporting_groups,
                opposing_groups,
                neutral_groups,
                divergences,
                group_signals,
                recommended_action
            )
            
            # Build comprehensive meta-signal response
            meta_signal = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'symbol': symbol,
                'meta_signal': consensus_direction,
                'consensus_strength': round(consensus_strength, 1),
                'confidence': round(aggregate_confidence, 1),
                'recommended_action': recommended_action,
                'entry_price': entry_price,
                'targets': targets,
                'stop_loss': stop_loss,
                'risk_reward': risk_reward,
                'ai_reasoning': ai_reasoning,
                'supporting_groups': supporting_groups,
                'opposing_groups': opposing_groups,
                'neutral_groups': neutral_groups,
                'divergences': divergences,
                'group_count': len(valid_groups),
                'group_details': {
                    g: {
                        'direction': group_signals[g]['direction'],
                        'confidence': group_signals[g]['confidence'],
                        'strength': group_signals[g]['strength']
                    }
                    for g in valid_groups
                },
                'weights_used': self.group_weights,
                'analysis_complete': True
            }
            
            logger.info(
                f"✅ Meta-signal for {symbol}: {consensus_direction} "
                f"(Strength: {consensus_strength:.1f}%, Confidence: {aggregate_confidence:.1f}%, "
                f"Support: {len(supporting_groups)}/{len(valid_groups)})"
            )
            
            return meta_signal
            
        except Exception as e:
            logger.error(f"❌ Error interpreting group signals for {symbol}: {e}")
            return self._error_response(symbol, str(e))
    
    def _calculate_consensus(
        self,
        group_signals: Dict[str, Dict],
        valid_groups: List[str]
    ) -> Tuple[str, float]:
        """
        Calculate consensus direction using weighted voting
        
        Returns:
            (consensus_direction, consensus_strength_percentage)
        """
        # Weighted vote scores
        scores = {'LONG': 0.0, 'SHORT': 0.0, 'NEUTRAL': 0.0}
        
        for group in valid_groups:
            signal = group_signals[group]
            direction = signal['direction']
            confidence = float(signal.get('confidence', 0))
            weight = self.group_weights.get(group, 0.2)  # Default 20% if not defined
            
            # Weighted vote = weight * confidence
            scores[direction] += weight * confidence
        
        # Find winning direction
        consensus_direction = max(scores, key=scores.get)
        max_score = scores[consensus_direction]
        total_possible = sum(self.group_weights[g] for g in valid_groups) * 100
        
        # Consensus strength = (winning score / total possible) * 100
        consensus_strength = (max_score / total_possible) * 100 if total_possible > 0 else 0
        
        return consensus_direction, consensus_strength
    
    def _calculate_aggregate_confidence(
        self,
        confidences: List[float],
        consensus_direction: str,
        group_signals: Dict[str, Dict],
        valid_groups: List[str]
    ) -> float:
        """
        Calculate aggregate confidence with adjustments for unanimity/divergence
        
        Returns:
            Aggregate confidence (0-100)
        """
        if not confidences:
            return 0.0
        
        # Base confidence: weighted average
        weighted_sum = 0.0
        total_weight = 0.0
        
        for group in valid_groups:
            signal = group_signals[group]
            confidence = float(signal.get('confidence', 0))
            weight = self.group_weights.get(group, 0.2)
            
            weighted_sum += confidence * weight
            total_weight += weight
        
        base_confidence = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Adjustment 1: Unanimous agreement boost
        all_agree = all(
            group_signals[g]['direction'] == consensus_direction
            for g in valid_groups
        )
        if all_agree:
            base_confidence *= self.confidence_boost_unanimous
        
        # Adjustment 2: Major divergence penalty
        opposing_count = sum(
            1 for g in valid_groups
            if group_signals[g]['direction'] != consensus_direction
            and group_signals[g]['direction'] != 'NEUTRAL'
        )
        if opposing_count >= 2:  # 2+ groups opposing
            base_confidence *= self.confidence_penalty_divergence
        
        # Clamp to 0-100
        return max(0, min(100, base_confidence))
    
    def _detect_divergences(
        self,
        group_signals: Dict[str, Dict],
        valid_groups: List[str],
        consensus_direction: str
    ) -> List[Dict[str, str]]:
        """
        Detect and document divergences between groups
        
        Returns:
            List of divergence descriptions
        """
        divergences = []
        
        for group in valid_groups:
            signal = group_signals[group]
            direction = signal['direction']
            
            # Opposite direction = major divergence
            if (consensus_direction == 'LONG' and direction == 'SHORT') or \
               (consensus_direction == 'SHORT' and direction == 'LONG'):
                divergences.append({
                    'group': group,
                    'type': 'opposite_direction',
                    'description': f"{group.upper()} signals {direction} while consensus is {consensus_direction}"
                })
            
            # Neutral when consensus is directional
            elif direction == 'NEUTRAL' and consensus_direction != 'NEUTRAL':
                divergences.append({
                    'group': group,
                    'type': 'neutral_divergence',
                    'description': f"{group.upper()} is neutral while consensus signals {consensus_direction}"
                })
        
        return divergences
    
    def _determine_action(
        self,
        direction: str,
        strength: float,
        confidence: float,
        divergence_count: int
    ) -> str:
        """
        Determine recommended action based on signal quality
        
        Returns:
            'BUY', 'SELL', 'HOLD', or 'WAIT'
        """
        # High quality signal thresholds
        min_strength = 60.0
        min_confidence = 70.0
        max_divergences = 1
        
        if direction == 'NEUTRAL':
            return 'HOLD'
        
        # Check if signal quality is sufficient
        if strength >= min_strength and confidence >= min_confidence and divergence_count <= max_divergences:
            return 'BUY' if direction == 'LONG' else 'SELL'
        else:
            return 'WAIT'  # Signal not strong enough
    
    def _calculate_levels(
        self,
        symbol: str,
        direction: str,
        current_price: Optional[float],
        group_signals: Dict[str, Dict],
        valid_groups: List[str]
    ) -> Tuple[Optional[float], List[float], Optional[float], Optional[float]]:
        """
        Calculate entry price, targets, stop-loss, and risk/reward ratio
        
        Returns:
            (entry_price, [tp1, tp2, tp3], stop_loss, risk_reward)
        """
        if not current_price or direction == 'NEUTRAL':
            return None, [], None, None
        
        # Use current price as entry
        entry = current_price
        
        # Calculate targets based on direction
        if direction == 'LONG':
            tp1 = entry * 1.02   # +2%
            tp2 = entry * 1.04   # +4%
            tp3 = entry * 1.06   # +6%
            sl = entry * 0.99    # -1%
        else:  # SHORT
            tp1 = entry * 0.98   # -2%
            tp2 = entry * 0.96   # -4%
            tp3 = entry * 0.94   # -6%
            sl = entry * 1.01    # +1%
        
        # Calculate risk/reward (using TP1)
        reward = abs(tp1 - entry)
        risk = abs(entry - sl)
        rr = reward / risk if risk > 0 else 0
        
        return entry, [tp1, tp2, tp3], sl, round(rr, 2)
    
    def _generate_ai_reasoning(
        self,
        symbol: str,
        direction: str,
        strength: float,
        confidence: float,
        supporting: List[str],
        opposing: List[str],
        neutral: List[str],
        divergences: List[Dict],
        group_signals: Dict[str, Dict],
        action: str
    ) -> str:
        """
        Generate natural language AI reasoning explaining the meta-signal
        
        Returns:
            Human-readable reasoning text
        """
        reasoning_parts = []
        
        # Opening statement
        support_count = len(supporting)
        total_groups = len(supporting) + len(opposing) + len(neutral)
        
        if support_count == total_groups:
            reasoning_parts.append(
                f"🎯 STRONG CONSENSUS: All {total_groups} analysis layers unanimously signal {direction}. "
                f"This represents exceptional market alignment."
            )
        elif support_count >= total_groups * 0.75:
            reasoning_parts.append(
                f"✅ ROBUST SIGNAL: {support_count}/{total_groups} layers support {direction}. "
                f"Strong majority agreement with high conviction."
            )
        elif support_count >= total_groups * 0.60:
            reasoning_parts.append(
                f"⚠️ MODERATE CONSENSUS: {support_count}/{total_groups} layers signal {direction}. "
                f"Majority agreement but with some dissent."
            )
        else:
            reasoning_parts.append(
                f"❌ WEAK SIGNAL: Only {support_count}/{total_groups} layers support {direction}. "
                f"Insufficient consensus for confident action."
            )
        
        # Supporting evidence
        if supporting:
            evidence = []
            for group in supporting:
                sig = group_signals[group]
                conf = sig.get('confidence', 0)
                evidence.append(f"{group.upper()} ({conf:.0f}% confidence)")
            reasoning_parts.append(
                f"\n\n📊 SUPPORTING LAYERS: {', '.join(evidence)}."
            )
        
        # Opposing/divergent groups
        if opposing or neutral:
            concerns = []
            for group in opposing:
                sig = group_signals[group]
                concerns.append(f"{group.upper()} warns {sig['direction']}")
            for group in neutral:
                concerns.append(f"{group.upper()} neutral")
            
            if concerns:
                reasoning_parts.append(
                    f"\n\n⚠️ DISSENTING VIEWS: {', '.join(concerns)}. "
                    f"Exercise caution due to conflicting signals."
                )
        
        # Strength and confidence assessment
        reasoning_parts.append(
            f"\n\n📈 SIGNAL QUALITY: Consensus strength {strength:.1f}%, "
            f"Aggregate confidence {confidence:.1f}%. "
        )
        
        if strength >= 75 and confidence >= 80:
            reasoning_parts.append("Exceptional quality signal with high reliability.")
        elif strength >= 60 and confidence >= 70:
            reasoning_parts.append("Good quality signal, suitable for action.")
        else:
            reasoning_parts.append("Signal quality below optimal threshold.")
        
        # Final recommendation
        reasoning_parts.append(
            f"\n\n💡 RECOMMENDATION: {action}. "
        )
        
        if action == 'BUY':
            reasoning_parts.append(
                f"Enter long position on {symbol}. Monitor stop-loss closely."
            )
        elif action == 'SELL':
            reasoning_parts.append(
                f"Enter short position on {symbol}. Use tight risk management."
            )
        elif action == 'WAIT':
            reasoning_parts.append(
                f"Signal insufficient for entry. Wait for clearer confirmation."
            )
        else:  # HOLD
            reasoning_parts.append(
                f"No directional edge. Remain in cash or hold existing positions."
            )
        
        return ''.join(reasoning_parts)
    
    def _error_response(
        self,
        symbol: str,
        error_message: str
    ) -> Dict[str, Any]:
        """
        Generate error response when meta-signal cannot be produced
        
        Returns:
            Error response dictionary
        """
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'symbol': symbol,
            'meta_signal': 'ERROR',
            'consensus_strength': 0,
            'confidence': 0,
            'recommended_action': 'WAIT',
            'entry_price': None,
            'targets': [],
            'stop_loss': None,
            'risk_reward': None,
            'ai_reasoning': f"❌ Unable to generate meta-signal: {error_message}",
            'supporting_groups': [],
            'opposing_groups': [],
            'neutral_groups': [],
            'divergences': [],
            'group_count': 0,
            'group_details': {},
            'weights_used': self.group_weights,
            'analysis_complete': False,
            'error': error_message
        }
