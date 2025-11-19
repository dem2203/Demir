# analytics/advisor_opportunity_service.py
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 DEMIR AI v7.0 - ADVISOR OPPORTUNITY SERVICE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADVISORY MODE - INTELLIGENT OPPORTUNITY DETECTION

Features:
    ✅ High-confidence opportunity detection
    ✅ Risk/Reward optimization
    ✅ Real-time market scanning
    ✅ Multi-criteria filtering
    ✅ Probability scoring
    ✅ Trade plan generation

Advisory Mode:
    - NO automatic trading
    - Human review required
    - Educational insights
    - Risk warnings included

Filtering Criteria:
    - Minimum confidence: 75%
    - Minimum R:R ratio: 2:1
    - Maximum risk: 3% per trade
    - Real exchange data only
    - Fresh signals only (<5 minutes)

DEPLOYMENT: Railway Production
AUTHOR: DEMIR AI Research Team
DATE: 2025-11-19
VERSION: 7.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import deque
from dataclasses import dataclass, asdict
import numpy as np

logger = logging.getLogger(__name__)

# ============================================================================
# OPPORTUNITY THRESHOLDS
# ============================================================================

# Confidence thresholds
MIN_CONFIDENCE = 0.75           # 75% minimum
HIGH_CONFIDENCE = 0.85          # 85% for premium opportunities

# Risk/Reward thresholds
MIN_RR_RATIO = 2.0              # 1:2 minimum
EXCELLENT_RR_RATIO = 3.0        # 1:3 for excellent opportunities

# Risk management
MAX_RISK_PERCENT = 3.0          # 3% max risk per trade
MAX_DRAWDOWN_PERCENT = 15.0     # 15% max portfolio drawdown

# Volume requirements
MIN_VOLUME_24H = 10_000_000     # $10M minimum 24h volume

# Signal freshness
MAX_SIGNAL_AGE = 300            # 5 minutes max age

# ============================================================================
# OPPORTUNITY DATA CLASS
# ============================================================================

@dataclass
class TradingOpportunity:
    """Trading opportunity data structure"""
    
    # Identification
    opportunity_id: str
    symbol: str
    direction: str              # 'LONG' or 'SHORT'
    
    # Pricing
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: Optional[float] = None
    take_profit_3: Optional[float] = None
    
    # Analysis
    confidence: float
    ensemble_score: float
    tech_score: float
    sentiment_score: float
    ml_score: float
    onchain_score: float
    macro_risk_score: float
    
    # Risk metrics
    risk_amount: float
    potential_profit: float
    risk_reward_ratio: float
    risk_percent: float
    
    # Market context
    market_regime: str
    volatility: str
    volume_24h: float
    
    # Reasoning
    reasoning: str
    key_factors: List[str]
    warnings: List[str]
    
    # Metadata
    created_at: datetime
    expires_at: datetime
    status: str                 # 'active', 'expired', 'executed'
    data_source: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat()
        return data

# ============================================================================
# ADVISOR OPPORTUNITY SERVICE
# ============================================================================

class AdvisorOpportunityService:
    """
    Intelligent opportunity detection and advisory service
    
    Responsibilities:
        1. Scan signals for high-quality opportunities
        2. Apply multi-criteria filtering
        3. Calculate risk metrics
        4. Generate trade plans
        5. Provide educational insights
        6. Track opportunity lifecycle
    """
    
    def __init__(self, db_manager):
        """
        Initialize service
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        
        # Active opportunities cache
        self.active_opportunities: Dict[str, TradingOpportunity] = {}
        
        # Opportunity history
        self.opportunity_history = deque(maxlen=1000)
        
        # Statistics
        self.stats = {
            'total_scanned': 0,
            'opportunities_found': 0,
            'high_confidence_count': 0,
            'excellent_rr_count': 0,
            'expired_count': 0
        }
        
        logger.info("✅ AdvisorOpportunityService initialized")
    
    # ========================================================================
    # OPPORTUNITY DETECTION
    # ========================================================================
    
    def scan_for_opportunities(
        self,
        signals: List[Dict[str, Any]],
        portfolio_value: float = 10000.0
    ) -> List[TradingOpportunity]:
        """
        Scan signals and identify high-quality trading opportunities
        
        Args:
            signals: List of validated signals
            portfolio_value: Current portfolio value (for risk calculation)
        
        Returns:
            List of TradingOpportunity objects
        """
        opportunities = []
        
        for signal in signals:
            self.stats['total_scanned'] += 1
            
            # 1. Pre-filter: Basic requirements
            if not self._meets_basic_requirements(signal):
                continue
            
            # 2. Calculate opportunity metrics
            opportunity = self._create_opportunity(signal, portfolio_value)
            
            if opportunity is None:
                continue
            
            # 3. Quality filter
            if not self._meets_quality_criteria(opportunity):
                continue
            
            # 4. Add to opportunities
            opportunities.append(opportunity)
            self.stats['opportunities_found'] += 1
            
            # Track high-confidence
            if opportunity.confidence >= HIGH_CONFIDENCE:
                self.stats['high_confidence_count'] += 1
            
            # Track excellent R:R
            if opportunity.risk_reward_ratio >= EXCELLENT_RR_RATIO:
                self.stats['excellent_rr_count'] += 1
        
        # Sort by quality score
        opportunities.sort(key=lambda x: self._calculate_quality_score(x), reverse=True)
        
        # Update active opportunities
        for opp in opportunities:
            self.active_opportunities[opp.opportunity_id] = opp
        
        logger.info(
            f"✅ Scan complete: {len(opportunities)} opportunities "
            f"from {len(signals)} signals"
        )
        
        return opportunities
    
    def _meets_basic_requirements(self, signal: Dict[str, Any]) -> bool:
        """Check if signal meets basic requirements"""
        
        # Required fields
        required = ['symbol', 'direction', 'entry_price', 'sl', 'tp1', 'confidence']
        if not all(field in signal for field in required):
            return False
        
        # Confidence threshold
        if signal['confidence'] < MIN_CONFIDENCE:
            return False
        
        # Valid direction
        if signal['direction'] not in ['LONG', 'SHORT']:
            return False
        
        # Positive prices
        if signal['entry_price'] <= 0 or signal['sl'] <= 0 or signal['tp1'] <= 0:
            return False
        
        # Signal freshness
        if 'timestamp' in signal:
            age = time.time() - signal['timestamp']
            if age > MAX_SIGNAL_AGE:
                logger.debug(f"Signal too old: {age:.0f}s")
                return False
        
        # Data source validation
        data_source = signal.get('data_source', '').upper()
        real_sources = ['BINANCE', 'BYBIT', 'COINBASE']
        if not any(source in data_source for source in real_sources):
            logger.warning(f"Invalid data source: {data_source}")
            return False
        
        return True
    
    def _create_opportunity(
        self,
        signal: Dict[str, Any],
        portfolio_value: float
    ) -> Optional[TradingOpportunity]:
        """
        Create opportunity object from signal
        
        Args:
            signal: Validated signal
            portfolio_value: Portfolio value
        
        Returns:
            TradingOpportunity or None
        """
        try:
            # Extract data
            symbol = signal['symbol']
            direction = signal['direction']
            entry_price = signal['entry_price']
            sl = signal['sl']
            tp1 = signal['tp1']
            
            # Calculate risk metrics
            risk = abs(entry_price - sl)
            reward = abs(tp1 - entry_price)
            rr_ratio = reward / risk if risk > 0 else 0
            
            # Risk amount (percentage of portfolio)
            risk_amount = portfolio_value * (MAX_RISK_PERCENT / 100)
            potential_profit = risk_amount * rr_ratio
            risk_percent = (risk / entry_price) * 100
            
            # Generate reasoning
            reasoning = self._generate_reasoning(signal)
            key_factors = self._extract_key_factors(signal)
            warnings = self._generate_warnings(signal, risk_percent)
            
            # Create opportunity
            opportunity = TradingOpportunity(
                opportunity_id=f"{symbol}_{direction}_{int(time.time())}",
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                stop_loss=sl,
                take_profit_1=tp1,
                take_profit_2=signal.get('tp2'),
                take_profit_3=signal.get('tp3'),
                confidence=signal['confidence'],
                ensemble_score=signal.get('ensemble_score', signal['confidence']),
                tech_score=signal.get('tech_group_score', 0.5),
                sentiment_score=signal.get('sentiment_group_score', 0.5),
                ml_score=signal.get('ml_group_score', 0.5),
                onchain_score=signal.get('onchain_group_score', 0.5),
                macro_risk_score=signal.get('macro_risk_group_score', 0.5),
                risk_amount=risk_amount,
                potential_profit=potential_profit,
                risk_reward_ratio=rr_ratio,
                risk_percent=risk_percent,
                market_regime=signal.get('market_regime', 'UNKNOWN'),
                volatility=self._assess_volatility(signal),
                volume_24h=signal.get('volume_24h', 0),
                reasoning=reasoning,
                key_factors=key_factors,
                warnings=warnings,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=4),
                status='active',
                data_source=signal.get('data_source', 'UNKNOWN')
            )
            
            return opportunity
        
        except Exception as e:
            logger.error(f"Failed to create opportunity: {e}")
            return None
    
    def _meets_quality_criteria(self, opportunity: TradingOpportunity) -> bool:
        """Check if opportunity meets quality criteria"""
        
        # Minimum R:R ratio
        if opportunity.risk_reward_ratio < MIN_RR_RATIO:
            return False
        
        # Maximum risk percent
        if opportunity.risk_percent > MAX_RISK_PERCENT:
            return False
        
        # Minimum confidence
        if opportunity.confidence < MIN_CONFIDENCE:
            return False
        
        return True
    
    def _calculate_quality_score(self, opportunity: TradingOpportunity) -> float:
        """
        Calculate overall quality score for opportunity ranking
        
        Returns:
            Quality score (0.0 to 100.0)
        """
        # Weighted factors
        confidence_score = opportunity.confidence * 40  # 40 points
        rr_score = min(opportunity.risk_reward_ratio / 5.0, 1.0) * 30  # 30 points
        ensemble_score = opportunity.ensemble_score * 20  # 20 points
        
        # Bonus for high agreement across groups
        group_scores = [
            opportunity.tech_score,
            opportunity.sentiment_score,
            opportunity.ml_score,
            opportunity.onchain_score,
            opportunity.macro_risk_score
        ]
        agreement = 1.0 - np.std(group_scores)  # High agreement = low std
        agreement_score = agreement * 10  # 10 points
        
        total_score = confidence_score + rr_score + ensemble_score + agreement_score
        
        return total_score
    
    # ========================================================================
    # REASONING & INSIGHTS
    # ========================================================================
    
    def _generate_reasoning(self, signal: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for opportunity"""
        
        direction = signal['direction']
        symbol = signal['symbol']
        confidence = signal['confidence'] * 100
        
        # Get strongest group
        group_scores = {
            'Technical Analysis': signal.get('tech_group_score', 0.5),
            'Sentiment Analysis': signal.get('sentiment_group_score', 0.5),
            'ML Models': signal.get('ml_group_score', 0.5),
            'On-Chain Data': signal.get('onchain_group_score', 0.5),
            'Macro/Risk': signal.get('macro_risk_group_score', 0.5)
        }
        
        strongest_group = max(group_scores.items(), key=lambda x: x[1])
        
        reasoning = (
            f"High-probability {direction} opportunity detected for {symbol} "
            f"with {confidence:.0f}% confidence. "
            f"Primary signal strength from {strongest_group[0]} "
            f"({strongest_group[1]*100:.0f}% score). "
        )
        
        # Add market context
        if 'market_regime' in signal:
            regime = signal['market_regime']
            reasoning += f"Market regime: {regime}. "
        
        return reasoning
    
    def _extract_key_factors(self, signal: Dict[str, Any]) -> List[str]:
        """Extract key factors contributing to opportunity"""
        
        factors = []
        
        # High confidence
        if signal['confidence'] >= HIGH_CONFIDENCE:
            factors.append(f"Very high confidence ({signal['confidence']*100:.0f}%)")
        
        # Strong technical
        if signal.get('tech_group_score', 0) > 0.65:
            factors.append("Strong technical indicators alignment")
        
        # Strong ML
        if signal.get('ml_group_score', 0) > 0.65:
            factors.append("AI models show high probability")
        
        # Multi-timeframe agreement
        tf_directions = [
            signal.get('tf_15m_direction'),
            signal.get('tf_1h_direction'),
            signal.get('tf_4h_direction'),
            signal.get('tf_1d_direction')
        ]
        tf_directions = [d for d in tf_directions if d]
        
        if len(tf_directions) >= 3:
            direction = signal['direction']
            agreement = sum(1 for d in tf_directions if d == direction)
            if agreement >= 3:
                factors.append(f"Multi-timeframe agreement ({agreement}/{len(tf_directions)})")
        
        # Excellent R:R
        entry = signal['entry_price']
        sl = signal['sl']
        tp1 = signal['tp1']
        rr = abs(tp1 - entry) / abs(entry - sl)
        if rr >= EXCELLENT_RR_RATIO:
            factors.append(f"Excellent risk/reward ratio (1:{rr:.1f})")
        
        return factors if factors else ["Multiple indicators alignment"]
    
    def _generate_warnings(
        self,
        signal: Dict[str, Any],
        risk_percent: float
    ) -> List[str]:
        """Generate risk warnings"""
        
        warnings = []
        
        # High risk
        if risk_percent > 2.5:
            warnings.append(f"⚠️ High risk per trade: {risk_percent:.1f}%")
        
        # Low volume
        volume = signal.get('volume_24h', 0)
        if volume < MIN_VOLUME_24H:
            warnings.append("⚠️ Low trading volume - liquidity risk")
        
        # Weak group scores
        weak_groups = []
        if signal.get('tech_group_score', 0.5) < 0.4:
            weak_groups.append("Technical")
        if signal.get('sentiment_group_score', 0.5) < 0.4:
            weak_groups.append("Sentiment")
        
        if weak_groups:
            warnings.append(f"⚠️ Weak {', '.join(weak_groups)} indicators")
        
        # Advisory disclaimer
        warnings.append("📚 Advisory only - conduct own analysis before trading")
        
        return warnings
    
    def _assess_volatility(self, signal: Dict[str, Any]) -> str:
        """Assess market volatility level"""
        
        # Would use ATR or other volatility metrics
        # For now, return based on risk percent
        risk = abs(signal['entry_price'] - signal['sl']) / signal['entry_price'] * 100
        
        if risk > 3.0:
            return "HIGH"
        elif risk > 1.5:
            return "MODERATE"
        else:
            return "LOW"
    
    # ========================================================================
    # OPPORTUNITY MANAGEMENT
    # ========================================================================
    
    def get_top_opportunities(
        self,
        limit: int = 10,
        min_confidence: float = MIN_CONFIDENCE,
        min_rr_ratio: float = MIN_RR_RATIO
    ) -> List[TradingOpportunity]:
        """
        Get top opportunities sorted by quality
        
        Args:
            limit: Maximum opportunities to return
            min_confidence: Minimum confidence filter
            min_rr_ratio: Minimum R:R ratio filter
        
        Returns:
            List of top opportunities
        """
        # Filter active opportunities
        filtered = [
            opp for opp in self.active_opportunities.values()
            if opp.status == 'active'
            and opp.confidence >= min_confidence
            and opp.risk_reward_ratio >= min_rr_ratio
            and opp.expires_at > datetime.now()
        ]
        
        # Sort by quality score
        filtered.sort(key=lambda x: self._calculate_quality_score(x), reverse=True)
        
        # Clean up expired
        self._cleanup_expired_opportunities()
        
        return filtered[:limit]
    
    def get_opportunity_by_id(self, opportunity_id: str) -> Optional[TradingOpportunity]:
        """Get specific opportunity by ID"""
        return self.active_opportunities.get(opportunity_id)
    
    def mark_opportunity_executed(self, opportunity_id: str):
        """Mark opportunity as executed"""
        if opportunity_id in self.active_opportunities:
            opp = self.active_opportunities[opportunity_id]
            opp.status = 'executed'
            
            # Move to history
            self.opportunity_history.append(opp)
            
            logger.info(f"Opportunity {opportunity_id} marked as executed")
    
    def _cleanup_expired_opportunities(self):
        """Remove expired opportunities"""
        now = datetime.now()
        expired = []
        
        for opp_id, opp in self.active_opportunities.items():
            if opp.expires_at < now:
                expired.append(opp_id)
                opp.status = 'expired'
                self.opportunity_history.append(opp)
                self.stats['expired_count'] += 1
        
        for opp_id in expired:
            del self.active_opportunities[opp_id]
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired opportunities")
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            'total_scanned': self.stats['total_scanned'],
            'opportunities_found': self.stats['opportunities_found'],
            'high_confidence_count': self.stats['high_confidence_count'],
            'excellent_rr_count': self.stats['excellent_rr_count'],
            'active_opportunities': len([
                o for o in self.active_opportunities.values()
                if o.status == 'active'
            ]),
            'expired_count': self.stats['expired_count'],
            'opportunity_rate': (
                self.stats['opportunities_found'] / 
                max(self.stats['total_scanned'], 1) * 100
            )
        }
    
    def reset_statistics(self):
        """Reset statistics"""
        self.stats = {
            'total_scanned': 0,
            'opportunities_found': 0,
            'high_confidence_count': 0,
            'excellent_rr_count': 0,
            'expired_count': 0
        }
        logger.info("Statistics reset")

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_trade_plan(opportunity: TradingOpportunity) -> Dict[str, Any]:
    """Create detailed trade plan from opportunity"""
    
    plan = {
        'opportunity_id': opportunity.opportunity_id,
        'symbol': opportunity.symbol,
        'direction': opportunity.direction,
        
        'entry': {
            'price': opportunity.entry_price,
            'order_type': 'LIMIT',
            'notes': 'Wait for confirmation at entry level'
        },
        
        'stop_loss': {
            'price': opportunity.stop_loss,
            'type': 'STOP_MARKET',
            'risk_amount': opportunity.risk_amount,
            'risk_percent': opportunity.risk_percent
        },
        
        'take_profit': {
            'tp1': {
                'price': opportunity.take_profit_1,
                'size': '50%',
                'profit': opportunity.potential_profit * 0.5
            }
        },
        
        'analysis': {
            'confidence': f"{opportunity.confidence*100:.0f}%",
            'risk_reward_ratio': f"1:{opportunity.risk_reward_ratio:.2f}",
            'reasoning': opportunity.reasoning,
            'key_factors': opportunity.key_factors
        },
        
        'warnings': opportunity.warnings,
        
        'expiry': opportunity.expires_at.isoformat(),
        'created': opportunity.created_at.isoformat()
    }
    
    # Add TP2, TP3 if present
    if opportunity.take_profit_2:
        plan['take_profit']['tp2'] = {
            'price': opportunity.take_profit_2,
            'size': '30%',
            'profit': opportunity.potential_profit * 0.3
        }
    
    if opportunity.take_profit_3:
        plan['take_profit']['tp3'] = {
            'price': opportunity.take_profit_3,
            'size': '20%',
            'profit': opportunity.potential_profit * 0.2
        }
    
    return plan
