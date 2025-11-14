#!/usr/bin/env python3
"""
🔱 DEMIR AI - Signal Engine v2.0
Advanced Trading Signal Generator with Entry/TP/SL

FEATURES:
✅ Long/Short/Neutral signals (colored)
✅ Entry price calculation
✅ Take Profit (TP1, TP2, TP3) levels
✅ Stop Loss (SL) with ATR-based sizing
✅ Risk/Reward ratio analysis
✅ Confidence scoring (0-100%)
✅ Technical explanation for each signal
"""

import os
import logging
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# SIGNAL CONSTANTS
# ============================================================================

class SignalType:
    """Signal types with colors"""
    LONG = {"name": "LONG", "color": "#00ff00", "emoji": "🟢", "value": 1}
    SHORT = {"name": "SHORT", "color": "#ff0000", "emoji": "🔴", "value": -1}
    NEUTRAL = {"name": "NEUTRAL", "color": "#ffaa00", "emoji": "🟡", "value": 0}

# ============================================================================
# SIGNAL CALCULATOR
# ============================================================================

class SignalCalculator:
    """Calculate trading signals with entry/TP/SL levels"""
    
    def __init__(self):
        logger.info("🔄 Signal Calculator initialized")
    
    def calculate_signal(self, symbol: str, price_data: Dict) -> Dict:
        """
        Calculate comprehensive signal
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            price_data: {current_price, rsi, macd, bb_upper, bb_lower, atr, vol}
        
        Returns:
            {signal_type, entry, tp1, tp2, tp3, sl, risk_reward, confidence, analysis}
        """
        
        try:
            current_price = float(price_data.get('current_price', 0))
            rsi = float(price_data.get('rsi', 50))
            macd = float(price_data.get('macd', 0))
            atr = float(price_data.get('atr', 0))
            bb_upper = float(price_data.get('bb_upper', current_price * 1.02))
            bb_lower = float(price_data.get('bb_lower', current_price * 0.98))
            
            logger.info(f"📊 Calculating signal for {symbol} @ ${current_price}")
            
            # ================================================================
            # SIGNAL GENERATION LOGIC
            # ================================================================
            
            # RSI-based signal
            if rsi < 30:
                rsi_signal = 1  # LONG (oversold)
                rsi_strength = (30 - rsi) / 30  # 0-1
                rsi_analysis = "Oversold condition - Strong buy pressure"
            elif rsi > 70:
                rsi_signal = -1  # SHORT (overbought)
                rsi_strength = (rsi - 70) / 30  # 0-1
                rsi_analysis = "Overbought condition - Strong sell pressure"
            else:
                rsi_signal = 0
                rsi_strength = 0
                rsi_analysis = "Neutral zone - No clear direction"
            
            # MACD-based signal
            if macd > 0:
                macd_signal = 1  # LONG
                macd_strength = min(abs(macd) / 0.5, 1)
                macd_analysis = "Bullish crossover - Momentum to the upside"
            elif macd < 0:
                macd_signal = -1  # SHORT
                macd_strength = min(abs(macd) / 0.5, 1)
                macd_analysis = "Bearish crossover - Momentum to the downside"
            else:
                macd_signal = 0
                macd_strength = 0
                macd_analysis = "No momentum detected"
            
            # Bollinger Bands breakout
            price_range = bb_upper - bb_lower
            if price_range > 0:
                position_in_bb = (current_price - bb_lower) / price_range
                
                if position_in_bb > 0.8:
                    bb_signal = 1  # Near upper band = bullish
                    bb_analysis = "Price near upper Bollinger Band - Bullish breakout"
                elif position_in_bb < 0.2:
                    bb_signal = -1  # Near lower band = bearish
                    bb_analysis = "Price near lower Bollinger Band - Bearish breakdown"
                else:
                    bb_signal = 0
                    bb_analysis = "Price in middle band - No clear breakout"
            else:
                bb_signal = 0
                bb_analysis = "Bands too narrow"
            
            # ================================================================
            # COMBINE SIGNALS (Weighted voting)
            # ================================================================
            
            final_score = (rsi_signal * 0.4 + 
                          macd_signal * 0.4 + 
                          bb_signal * 0.2)
            
            confidence = abs(final_score)
            
            if final_score > 0.3:
                signal_type = SignalType.LONG
            elif final_score < -0.3:
                signal_type = SignalType.SHORT
            else:
                signal_type = SignalType.NEUTRAL
            
            logger.info(f"✅ Signal: {signal_type['name']} (confidence: {confidence:.1%})")
            
            # ================================================================
            # CALCULATE ENTRY, TP, SL
            # ================================================================
            
            entry_price = current_price
            
            if signal_type['value'] == 1:  # LONG
                # ATR-based stop loss
                sl_distance = atr * 2.0  # 2x ATR below entry
                sl = entry_price - sl_distance
                
                # Profit targets (1:3 risk-reward)
                profit_distance = sl_distance * 3
                tp1 = entry_price + (profit_distance * 0.5)
                tp2 = entry_price + (profit_distance * 1.0)
                tp3 = entry_price + (profit_distance * 1.5)
                
                risk_reward = profit_distance / sl_distance if sl_distance > 0 else 0
                
                analysis_text = f"""
🟢 LONG SIGNAL (Buy)
━━━━━━━━━━━━━━━━━━━━━━
📊 Technical Analysis:
  • {rsi_analysis}
  • {macd_analysis}
  • {bb_analysis}

💰 Position Details:
  • Entry: ${entry_price:.2f}
  • SL (Stop Loss): ${sl:.2f}
  • Distance to SL: ${abs(entry_price - sl):.2f}
  
🎯 Profit Targets:
  • TP1 (50% profit): ${tp1:.2f} (+{((tp1/entry_price - 1)*100):.2f}%)
  • TP2 (Full profit): ${tp2:.2f} (+{((tp2/entry_price - 1)*100):.2f}%)
  • TP3 (Max profit): ${tp3:.2f} (+{((tp3/entry_price - 1)*100):.2f}%)

⚡ Risk/Reward: 1:{risk_reward:.2f}
📈 Confidence: {confidence*100:.1f}%
"""
            
            elif signal_type['value'] == -1:  # SHORT
                # ATR-based stop loss
                sl_distance = atr * 2.0  # 2x ATR above entry
                sl = entry_price + sl_distance
                
                # Profit targets
                profit_distance = sl_distance * 3
                tp1 = entry_price - (profit_distance * 0.5)
                tp2 = entry_price - (profit_distance * 1.0)
                tp3 = entry_price - (profit_distance * 1.5)
                
                risk_reward = profit_distance / sl_distance if sl_distance > 0 else 0
                
                analysis_text = f"""
🔴 SHORT SIGNAL (Sell)
━━━━━━━━━━━━━━━━━━━━━━
📊 Technical Analysis:
  • {rsi_analysis}
  • {macd_analysis}
  • {bb_analysis}

💰 Position Details:
  • Entry: ${entry_price:.2f}
  • SL (Stop Loss): ${sl:.2f}
  • Distance to SL: ${abs(sl - entry_price):.2f}
  
🎯 Profit Targets:
  • TP1 (50% profit): ${tp1:.2f} ({((tp1/entry_price - 1)*100):.2f}%)
  • TP2 (Full profit): ${tp2:.2f} ({((tp2/entry_price - 1)*100):.2f}%)
  • TP3 (Max profit): ${tp3:.2f} ({((tp3/entry_price - 1)*100):.2f}%)

⚡ Risk/Reward: 1:{risk_reward:.2f}
📈 Confidence: {confidence*100:.1f}%
"""
            
            else:  # NEUTRAL
                sl = entry_price * 0.97
                tp1 = tp2 = tp3 = entry_price * 1.03
                risk_reward = 0
                
                analysis_text = f"""
🟡 NEUTRAL SIGNAL (Hold/Wait)
━━━━━━━━━━━━━━━━━━━━━━
📊 Technical Analysis:
  • {rsi_analysis}
  • {macd_analysis}
  • {bb_analysis}

💰 Position Details:
  • Current Price: ${entry_price:.2f}
  • No clear direction detected
  • Waiting for breakout signal

⚠️ Recommendation: WAIT for better setup
📈 Confidence: {confidence*100:.1f}%
"""
            
            return {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'signal_type': signal_type['name'],
                'signal_color': signal_type['color'],
                'signal_emoji': signal_type['emoji'],
                'confidence': float(confidence),
                'entry_price': float(entry_price),
                'sl': float(sl),
                'tp1': float(tp1),
                'tp2': float(tp2),
                'tp3': float(tp3),
                'risk_reward': float(risk_reward),
                'analysis': analysis_text,
                'crypto_impact': self._analyze_crypto_impact(symbol, signal_type['name']),
                'status': 'success'
            }
        
        except Exception as e:
            logger.error(f"❌ Signal calculation error: {e}")
            return {'error': str(e), 'status': 'error'}
    
    def _analyze_crypto_impact(self, symbol: str, signal: str) -> str:
        """Analyze how this signal impacts crypto market"""
        
        if 'BTC' in symbol:
            if signal == 'LONG':
                return "Bitcoin LONG → Market optimism → Alts likely to follow"
            else:
                return "Bitcoin SHORT → Risk-off sentiment → Alts will bleed"
        
        elif 'ETH' in symbol:
            if signal == 'LONG':
                return "Ethereum LONG → DeFi bullish → L2s and alts pump"
            else:
                return "Ethereum SHORT → Smart contract risk → Ecosystem weakness"
        
        else:
            if signal == 'LONG':
                return "Altcoin LONG → Niche bullish → Watch for altseason"
            else:
                return "Altcoin SHORT → Sector weakness → Consolidation phase"

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    logger.info("=" * 80)
    logger.info("🔱 DEMIR AI - Signal Engine v2.0")
    logger.info("=" * 80)
    
    calculator = SignalCalculator()
    
    # Test signal
    test_data = {
        'current_price': 43250.50,
        'rsi': 28.5,
        'macd': 0.35,
        'atr': 450.00,
        'bb_upper': 43800.00,
        'bb_lower': 42700.00,
        'vol': 1500000
    }
    
    signal = calculator.calculate_signal('BTCUSDT', test_data)
    print(signal.get('analysis', 'No analysis'))
    logger.info("✅ Signal generated successfully")

if __name__ == "__main__":
    main()
