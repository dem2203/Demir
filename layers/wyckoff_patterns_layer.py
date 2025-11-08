"""
🔱 PHASE 19C: WYCKOFF PATTERNS LAYER
Accumulation/Distribution analysis + Volume-Price patterns
"""
import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class WyckoffPhase:
    phase_name: str
    start_idx: int
    end_idx: int
    volume_avg: float
    price_range: float

class WyckoffPatternsLayer:
    """
    Wyckoff Method: Accumulation/Distribution phases
    Phase A: Stopping of previous down-move
    Phase B: Building up of cause for the next move
    Phase C: Final test / weakness
    Phase D: Buy pressure emerges
    Phase E: Assault on previous resistance
    """
    
    def analyze_wyckoff(self, prices: list, volumes: list) -> Dict:
        """Detect Wyckoff accumulation/distribution patterns"""
        try:
            if len(prices) < 20:
                return {}
            
            # Find support/resistance
            support = min(prices[-20:])
            resistance = max(prices[-20:])
            price_range = resistance - support
            
            # Analyze volume profile
            avg_volume = sum(volumes[-20:]) / len(volumes[-20:])
            recent_volume = sum(volumes[-5:]) / 5
            
            # Detect phase
            current_price = prices[-1]
            volume_climax = recent_volume > avg_volume * 1.5
            price_near_support = current_price < support + (price_range * 0.3)
            
            if volume_climax and price_near_support:
                phase = "accumulation"
                strength = 0.8
            elif current_price > resistance - (price_range * 0.2):
                phase = "distribution"
                strength = 0.6
            else:
                phase = "sideways"
                strength = 0.4
            
            return {
                "wyckoff_phase": phase,
                "strength": strength,
                "support": support,
                "resistance": resistance,
                "volume_climax": volume_climax,
            }
        except Exception as e:
            logger.error(f"Wyckoff analysis error: {e}")
            return {}
