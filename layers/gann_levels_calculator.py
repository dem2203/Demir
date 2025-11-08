"""
🔱 DEMIR AI - PHASE 19A: GANN LEVELS & SQUARING CALCULATOR
============================================================================
Gann Square of 9 + Gann Angles + Price Projections

Date: 8 November 2025
Version: 1.0 - Full Gann Theory Implementation

PURPOSE: Calculate Gann levels for BTC/ETH/LTC - major support/resistance

KEY CONCEPTS:
- Gann Square of 9 (numerological angles)
- Gann Angles (45°, 90°, 120°, 135°, etc)
- Price squares (major pivot points)
- Time squares (time-price confluence)
- Gann fan projections

USAGE:
Identify key highs/lows, calculate Gann levels, use as confluence zones
============================================================================
"""

import logging
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

# ============================================================================
# GANN SQUARE OF 9 CALCULATOR
# ============================================================================

class GannSquareOf9:
    """
    Gann Square of 9 - numerological grid
    
    The square spirals from center (1) outward in a square pattern:
    17 16 15 14 13
    18  5  4  3 12
    19  6  1  2 11
    20  7  8  9 10
    21 22 23 24 25
    
    Key levels: corners of squares (1, 4, 9, 16, 25, 36, 49, 64, 81, 100...)
    """
    
    @staticmethod
    def get_square_roots(price: float) -> Tuple[float, float]:
        """Get square root and next integer square root"""
        sqrt = math.sqrt(price)
        lower = math.floor(sqrt)
        upper = lower + 1
        return sqrt, lower, upper
    
    @staticmethod
    def calculate_gann_levels(price: float) -> Dict[str, float]:
        """
        Calculate all key Gann levels for a given price
        
        Returns: Dictionary of support/resistance levels
        """
        sqrt, lower, upper = GannSquareOf9.get_square_roots(price)
        
        # Middle of the square (45° angle)
        mid_level = (lower ** 2 + upper ** 2) / 2
        
        # Gann levels at different angles
        levels = {
            "current": price,
            "lower_square": lower ** 2,
            "upper_square": upper ** 2,
            "45_degree": mid_level,
            
            # 1/8 divisions (octiles)
            "1_8_low": lower ** 2 + ((upper ** 2 - lower ** 2) * 0.125),
            "2_8": lower ** 2 + ((upper ** 2 - lower ** 2) * 0.25),
            "3_8": lower ** 2 + ((upper ** 2 - lower ** 2) * 0.375),
            "4_8": lower ** 2 + ((upper ** 2 - lower ** 2) * 0.5),
            "5_8": lower ** 2 + ((upper ** 2 - lower ** 2) * 0.625),
            "6_8": lower ** 2 + ((upper ** 2 - lower ** 2) * 0.75),
            "7_8": lower ** 2 + ((upper ** 2 - lower ** 2) * 0.875),
            
            # 90° angle (square of price)
            "top_of_square": upper ** 2,
            
            # Angles out of the square (projections)
            "prev_square": max(1, (lower - 1) ** 2),
            "next_square": (upper + 1) ** 2,
        }
        
        return {k: round(v, 2) for k, v in levels.items()}
    
    @staticmethod
    def calculate_gann_fan_levels(low: float, high: float) -> Dict[str, float]:
        """
        Calculate Gann fan from a significant low
        
        Gann believed prices move at 45° angles
        """
        price_range = high - low
        levels = {
            "base": low,
            "45_deg": low + price_range,        # 1x1 (45°)
            "52_5_deg": low + price_range * 1.33,  # 2x1
            "63_deg": low + price_range * 2,        # 3x1
            "82_5_deg": low + price_range * 3,      # 4x1
            "prev_45": max(1, low - price_range),   # 1x1 below
        }
        return levels

# ============================================================================
# GANN ANGLES & PRICE PROJECTIONS
# ============================================================================

class GannAngles:
    """Calculate price projections using Gann angles"""
    
    # Gann's key angles
    ANGLES = {
        "1x8": 82.5,   # Steepest uptrend
        "1x4": 75.0,   # Very strong uptrend
        "1x3": 71.25,  # Strong uptrend
        "1x2": 63.75,  # Moderate uptrend
        "1x1": 45.0,   # Perfect angle (45°)
        "2x1": 26.25,  # Weak uptrend
        "3x1": 18.75,  # Very weak uptrend
        "4x1": 14.06,  # Extremely weak uptrend
        "8x1": 7.13,   # Almost flat
    }
    
    @staticmethod
    def get_price_projection(start_price: float, start_time: int, 
                            end_time: int, angle_name: str) -> float:
        """
        Project price using Gann angle
        
        Args:
            start_price: Starting price level
            start_time: Starting time (candle index)
            end_time: Target time
            angle_name: Angle name (e.g., "1x1", "1x2")
        
        Returns:
            Projected price at end_time
        """
        if angle_name not in GannAngles.ANGLES:
            return start_price
        
        angle_deg = GannAngles.ANGLES[angle_name]
        angle_rad = math.radians(angle_deg)
        
        time_diff = end_time - start_time
        price_change = time_diff * math.tan(angle_rad)
        
        return start_price + price_change
    
    @staticmethod
    def get_all_projections(start_price: float, start_time: int, 
                           target_time: int) -> Dict[str, float]:
        """Get price projections for all key angles"""
        projections = {}
        for angle_name in GannAngles.ANGLES.keys():
            price = GannAngles.get_price_projection(
                start_price, start_time, target_time, angle_name
            )
            projections[angle_name] = round(price, 2)
        return projections

# ============================================================================
# GANN LEVELS LAYER - FULL INTEGRATION
# ============================================================================

@dataclass
class GannLevelAnalysis:
    """Gann level analysis result"""
    current_price: float
    square_of_9_levels: Dict[str, float]
    gann_fan_levels: Dict[str, float]
    angle_projections: Dict[str, float]
    nearest_support: float
    nearest_resistance: float
    confluence_zones: List[Tuple[float, str]]  # (price, description)
    signal_strength: float  # 0-100

class GannLevelsLayer:
    """
    Real-time Gann levels calculation layer
    
    Maintains key highs/lows and calculates Gann levels
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.key_levels = {}  # Symbol -> {high, low, timestamp}
        self.gann_history = {}  # Symbol -> list of historical analyses
    
    def update_key_level(self, symbol: str, price: float, 
                        is_high: bool = False, is_low: bool = False):
        """Update key high/low for a symbol"""
        if symbol not in self.key_levels:
            self.key_levels[symbol] = {"high": price, "low": price}
        
        if is_high and price > self.key_levels[symbol]["high"]:
            self.key_levels[symbol]["high"] = price
            logger.info(f"New high for {symbol}: {price}")
        
        if is_low and price < self.key_levels[symbol]["low"]:
            self.key_levels[symbol]["low"] = price
            logger.info(f"New low for {symbol}: {price}")
    
    def analyze_gann_levels(self, symbol: str, current_price: float, 
                           time_index: int = None) -> Optional[GannLevelAnalysis]:
        """
        Full Gann level analysis
        """
        try:
            if symbol not in self.key_levels:
                self.update_key_level(symbol, current_price)
            
            levels = self.key_levels[symbol]
            
            # Calculate Gann Square of 9 from current price
            square_of_9 = GannSquareOf9.calculate_gann_levels(current_price)
            
            # Calculate Gann fan from recent low
            gann_fan = GannSquareOf9.calculate_gann_fan_levels(
                levels["low"], current_price
            )
            
            # Calculate angle projections
            time_idx = time_index or 0
            projections = GannAngles.get_all_projections(
                levels["low"], time_idx, time_idx + 24  # 24 candles ahead
            )
            
            # Find confluence zones (prices that align across methods)
            confluence = self._find_confluence_zones(
                square_of_9, gann_fan, projections, current_price
            )
            
            # Find nearest support and resistance
            all_levels = list(square_of_9.values()) + list(gann_fan.values())
            support = max([l for l in all_levels if l < current_price], default=levels["low"])
            resistance = min([l for l in all_levels if l > current_price], default=levels["high"])
            
            # Calculate signal strength (confluence count)
            signal_strength = len(confluence) * 10
            signal_strength = min(100, signal_strength)
            
            analysis = GannLevelAnalysis(
                current_price=current_price,
                square_of_9_levels=square_of_9,
                gann_fan_levels=gann_fan,
                angle_projections=projections,
                nearest_support=round(support, 2),
                nearest_resistance=round(resistance, 2),
                confluence_zones=confluence,
                signal_strength=signal_strength,
            )
            
            # Store in history
            if symbol not in self.gann_history:
                self.gann_history[symbol] = []
            self.gann_history[symbol].append(analysis)
            if len(self.gann_history[symbol]) > 100:
                self.gann_history[symbol] = self.gann_history[symbol][-100:]
            
            logger.info(f"Gann analysis for {symbol}: S={round(support,2)} R={round(resistance,2)}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing Gann levels for {symbol}: {e}", exc_info=True)
            return None
    
    def _find_confluence_zones(self, square_of_9: Dict, gann_fan: Dict, 
                              projections: Dict, current_price: float,
                              tolerance: float = 2.0) -> List[Tuple[float, str]]:
        """Find prices that appear in multiple calculation methods"""
        confluence = {}
        
        # Extract all values
        all_values = {}
        for level, price in square_of_9.items():
            all_values[price] = f"SQ9:{level}"
        for level, price in gann_fan.items():
            if price not in all_values:
                all_values[price] = f"FAN:{level}"
            else:
                all_values[price] += f", FAN:{level}"
        for level, price in projections.items():
            if price not in all_values:
                all_values[price] = f"PROJ:{level}"
            else:
                all_values[price] += f", PROJ:{level}"
        
        # Find confluences (within tolerance)
        confluences = []
        for price, desc in all_values.items():
            if price > current_price * 0.95 and price < current_price * 1.05:
                confluences.append((price, desc))
        
        return sorted(confluences)
    
    def get_gann_signals(self, symbol: str, analysis: GannLevelAnalysis) -> Dict:
        """
        Generate trading signals from Gann analysis
        """
        if not analysis:
            return {}
        
        signals = {
            "gann_support": analysis.nearest_support,
            "gann_resistance": analysis.nearest_resistance,
            "confluence_count": len(analysis.confluence_zones),
            "signal_strength": analysis.signal_strength / 100.0,  # 0-1
            "timestamp": datetime.now().isoformat(),
        }
        
        # Determine signal direction based on confluence
        if analysis.signal_strength > 60:  # Strong confluence
            if analysis.nearest_resistance - analysis.current_price < analysis.current_price - analysis.nearest_support:
                signals["direction"] = "bearish"  # Closer to resistance
            else:
                signals["direction"] = "bullish"  # Closer to support
        else:
            signals["direction"] = "neutral"
        
        return signals

# ============================================================================
# INTEGRATION
# ============================================================================

async def integrate_gann_levels(config: Dict, symbol: str, 
                               current_price: float) -> Dict:
    """Integration point for consciousness engine"""
    layer = GannLevelsLayer(config)
    analysis = layer.analyze_gann_levels(symbol, current_price)
    
    if not analysis:
        return {}
    
    return layer.get_gann_signals(symbol, analysis)

if __name__ == "__main__":
    print("✅ Phase 19A: Gann Levels Layer ready")
