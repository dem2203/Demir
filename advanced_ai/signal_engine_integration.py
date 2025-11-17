"""
DEMIR AI BOT - Signal Engine Integration (UPDATED)
Group-based signal orchestration
Replace old generate_final_signal() with 5-group architecture
Production-grade implementation
"""

import logging
from typing import Dict, Any, List, Optional
import numpy as np
import time
from enum import Enum

logger = logging.getLogger(__name__)


class SignalGroupOrchestrator:
    """Orchestrate signals from all 5 groups."""
    
    def __init__(self):
        """Initialize orchestrator."""
        # Import group signal engine
        try:
            from ui.group_signal_engine import GroupSignalEngine
            self.group_engine = GroupSignalEngine()
            logger.info("GroupSignalEngine initialized successfully")
        except ImportError as e:
            logger.error(f"Failed to import GroupSignalEngine: {e}")
            raise
    
    def orchestrate_group_signals(
        self,
        symbol: str,
        all_scores: Dict[str, Dict[str, float]],
        timestamp: float = None
    ) -> Dict[str, Any]:
        """
        Generate signals from all 5 groups.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            all_scores: Dict with keys: technical, sentiment, ml, onchain, risk
                       Each containing layer scores (0-1)
            timestamp: Unix timestamp (default: current time)
        
        Returns:
            Dict with all group signals, consensus, conflicts
        """
        
        if timestamp is None:
            timestamp = time.time()
        
        logger.info(f"Orchestrating signals for {symbol}")
        
        signals = {}
        
        try:
            # Generate Technical Signal (28 layers)
            signals['technical'] = self.group_engine.generate_technical_signal(
                symbol=symbol,
                technical_scores=all_scores.get('technical', {}),
                timestamp=timestamp
            )
            logger.debug(f"Technical signal generated: {signals['technical'].direction.value}")
            
        except Exception as e:
            logger.error(f"Failed to generate technical signal: {e}")
            signals['technical'] = None
        
        try:
            # Generate Sentiment Signal (20 layers)
            signals['sentiment'] = self.group_engine.generate_sentiment_signal(
                symbol=symbol,
                sentiment_scores=all_scores.get('sentiment', {}),
                timestamp=timestamp
            )
            logger.debug(f"Sentiment signal generated: {signals['sentiment'].direction.value}")
            
        except Exception as e:
            logger.error(f"Failed to generate sentiment signal: {e}")
            signals['sentiment'] = None
        
        try:
            # Generate ML Signal (10 layers)
            signals['ml'] = self.group_engine.generate_ml_signal(
                symbol=symbol,
                ml_scores=all_scores.get('ml', {}),
                timestamp=timestamp
            )
            logger.debug(f"ML signal generated: {signals['ml'].direction.value}")
            
        except Exception as e:
            logger.error(f"Failed to generate ML signal: {e}")
            signals['ml'] = None
        
        try:
            # Generate OnChain Signal (6 layers)
            signals['onchain'] = self.group_engine.generate_onchain_signal(
                symbol=symbol,
                onchain_scores=all_scores.get('onchain', {}),
                timestamp=timestamp
            )
            logger.debug(f"OnChain signal generated: {signals['onchain'].direction.value}")
            
        except Exception as e:
            logger.error(f"Failed to generate OnChain signal: {e}")
            signals['onchain'] = None
        
        try:
            # Generate Risk Assessment (5 layers, not buy/sell signal)
            risk_assessment = self.group_engine.generate_risk_assessment(
                symbol=symbol,
                risk_scores=all_scores.get('risk', {}),
                timestamp=timestamp
            )
            logger.debug(f"Risk assessment generated")
            
        except Exception as e:
            logger.error(f"Failed to generate risk assessment: {e}")
            risk_assessment = {}
        
        # Filter valid signals
        valid_signals = {
            k: v for k, v in signals.items()
            if v is not None and hasattr(v, 'active_layers') and v.active_layers > 0
        }
        
        if not valid_signals:
            logger.warning(f"No valid signals generated for {symbol}")
            return {
                'symbol': symbol,
                'timestamp': timestamp,
                'groups': {},
                'risk': risk_assessment,
                'consensus': None,
                'conflict_detected': False,
                'conflicts': [],
                'error': 'No valid signals generated'
            }
        
        try:
            # Detect conflicts between groups
            conflict_detected, conflicts = self.group_engine.detect_group_conflicts(
                valid_signals
            )
            
            if conflict_detected:
                logger.warning(f"Conflicts detected for {symbol}: {conflicts}")
            
        except Exception as e:
            logger.error(f"Failed to detect conflicts: {e}")
            conflict_detected = False
            conflicts = []
        
        try:
            # Calculate Consensus
            consensus = self.group_engine.calculate_consensus(valid_signals)
            logger.info(f"Consensus calculated for {symbol}: {consensus['direction']}")
            
        except Exception as e:
            logger.error(f"Failed to calculate consensus: {e}")
            consensus = {}
        
        # Prepare result
        result = {
            'symbol': symbol,
            'timestamp': timestamp,
            'groups': {
                'technical': {
                    'direction': signals['technical'].direction.value if signals['technical'] else None,
                    'strength': signals['technical'].strength if signals['technical'] else None,
                    'confidence': signals['technical'].confidence if signals['technical'] else None,
                    'active_layers': signals['technical'].active_layers if signals['technical'] else 0,
                    'layer_details': signals['technical'].layer_details if signals['technical'] else {}
                } if signals['technical'] else None,
                'sentiment': {
                    'direction': signals['sentiment'].direction.value if signals['sentiment'] else None,
                    'strength': signals['sentiment'].strength if signals['sentiment'] else None,
                    'confidence': signals['sentiment'].confidence if signals['sentiment'] else None,
                    'active_layers': signals['sentiment'].active_layers if signals['sentiment'] else 0,
                } if signals['sentiment'] else None,
                'ml': {
                    'direction': signals['ml'].direction.value if signals['ml'] else None,
                    'strength': signals['ml'].strength if signals['ml'] else None,
                    'confidence': signals['ml'].confidence if signals['ml'] else None,
                    'active_layers': signals['ml'].active_layers if signals['ml'] else 0,
                } if signals['ml'] else None,
                'onchain': {
                    'direction': signals['onchain'].direction.value if signals['onchain'] else None,
                    'strength': signals['onchain'].strength if signals['onchain'] else None,
                    'confidence': signals['onchain'].confidence if signals['onchain'] else None,
                    'active_layers': signals['onchain'].active_layers if signals['onchain'] else 0,
                } if signals['onchain'] else None,
            },
            'risk': risk_assessment,
            'consensus': consensus,
            'conflict_detected': conflict_detected,
            'conflicts': conflicts
        }
        
        logger.info(f"Signal orchestration completed for {symbol}")
        
        return result
    
    def get_group_signals_summary(self, orchestrated_result: Dict[str, Any]) -> str:
        """Get human-readable summary of group signals."""
        
        summary = f"\n{'='*80}\n"
        summary += f"SIGNAL ORCHESTRATION SUMMARY - {orchestrated_result['symbol']}\n"
        summary += f"{'='*80}\n\n"
        
        groups = orchestrated_result.get('groups', {})
        
        if groups.get('technical'):
            tech = groups['technical']
            summary += f"📊 TECHNICAL: {tech['direction']} ({tech['strength']:.1%} strength, {tech['confidence']:.1%} confidence)\n"
        
        if groups.get('sentiment'):
            sent = groups['sentiment']
            summary += f"💭 SENTIMENT: {sent['direction']} ({sent['strength']:.1%} strength, {sent['confidence']:.1%} confidence)\n"
        
        if groups.get('ml'):
            ml = groups['ml']
            summary += f"🤖 ML: {ml['direction']} ({ml['strength']:.1%} strength, {ml['confidence']:.1%} confidence)\n"
        
        if groups.get('onchain'):
            oc = groups['onchain']
            summary += f"⛓️ ONCHAIN: {oc['direction']} ({oc['strength']:.1%} strength, {oc['confidence']:.1%} confidence)\n"
        
        risk = orchestrated_result.get('risk', {})
        if risk:
            summary += f"\n⚠️ RISK ASSESSMENT:\n"
            summary += f"   Volatility: {risk.get('volatility_score', 0):.1%}\n"
            summary += f"   Max Loss: {risk.get('max_loss_exposure', 'N/A')}\n"
            summary += f"   Kelly Fraction: {risk.get('kelly_fraction', 0):.1%}\n"
        
        consensus = orchestrated_result.get('consensus', {})
        if consensus:
            conflict_text = "⚠️ CONFLICT DETECTED" if orchestrated_result.get('conflict_detected') else "✅ ALIGNED"
            summary += f"\n⭐ CONSENSUS:\n"
            summary += f"   Direction: {consensus.get('direction', 'N/A')}\n"
            summary += f"   Strength: {consensus.get('strength', 0):.1%}\n"
            summary += f"   Confidence: {consensus.get('confidence', 0):.1%}\n"
            summary += f"   Status: {conflict_text}\n"
        
        summary += f"\n{'='*80}\n"
        
        return summary
