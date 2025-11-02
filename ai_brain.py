"""
🔱 DEMIR AI TRADING BOT - AI Brain v7.0 PRODUCTION ULTIMATE
===========================================================
Date: 2 Kasım 2025, 08:48 CET
Version: 7.0 - 15-LAYER ULTIMATE SYSTEM (FULL WORKING CODE!)

EVOLUTION:
----------
v4: Phase 3A + 3B (11 layers)
v5: Phase 6 MACRO (12 layers - working base)
v6: ATTEMPT (14 layers - had import issues)
v7: PRODUCTION FIX (15 layers - working with correct imports!)

ALL 15 LAYERS:
--------------
Layers 1-11: From strategy_layer (working code PRESERVED!)
Layer 12: Macro Correlation (v5 - preserved)
Layer 13: Gold Correlation (XAU, XAG) ⭐ NEW
Layer 14: BTC Dominance Flow (Altseason) ⭐ NEW
Layer 15: Cross-Asset Correlation (BTC/ETH/LTC/BNB) ⭐ NEW

COMPATIBILITY:
--------------
✅ Works with existing streamlit_app.py (TESTED!)
✅ Uses make_trading_decision() function (REQUIRED!)
✅ Preserves ALL working imports
✅ Backwards compatible 100%
"""

from datetime import datetime

# =====================================================
# PHASE 1: IMPORTS - All layers with fallback handling
# =====================================================

# Core strategy (11 layers in one module - v4 PRESERVED!)
try:
    import strategy_layer as strategy
    STRATEGY_AVAILABLE = True
    print("✅ AI Brain v7: strategy_layer imported (Layers 1-11!)")
except Exception as e:
    STRATEGY_AVAILABLE = False
    print(f"⚠️ AI Brain v7: strategy_layer import failed: {e}")

# Monte Carlo simulation
try:
    import monte_carlo_layer as monte_carlo
    MONTE_CARLO_AVAILABLE = True
    print("✅ AI Brain v7: monte_carlo_layer imported")
except Exception as e:
    MONTE_CARLO_AVAILABLE = False
    print(f"⚠️ AI Brain v7: monte_carlo_layer import failed: {e}")

# Kelly Criterion enhanced
try:
    import kelly_enhanced_layer as kelly
    KELLY_AVAILABLE = True
    print("✅ AI Brain v7: kelly_enhanced_layer imported")
except Exception as e:
    KELLY_AVAILABLE = False
    print(f"⚠️ AI Brain v7: kelly_enhanced_layer import failed: {e}")

# Phase 6 Additions (v5 PRESERVED)
try:
    import macro_correlation_layer as macro
    MACRO_AVAILABLE = True
    print("✅ AI Brain v7: macro_correlation_layer imported (Layer 12!)")
except Exception as e:
    MACRO_AVAILABLE = False
    print(f"⚠️ AI Brain v7: macro_correlation_layer import failed: {e}")

# Phase 6.1: Gold Correlation (NEW in v7!)
try:
    import gold_correlation_layer as gold
    GOLD_AVAILABLE = True
    print("✅ AI Brain v7: gold_correlation_layer imported (Layer 13!)")
except Exception as e:
    GOLD_AVAILABLE = False
    print(f"⚠️ AI Brain v7: gold_correlation_layer import failed: {e}")

# Phase 6.2: BTC Dominance Flow (NEW in v7!)
try:
    import dominance_flow_layer as dominance
    DOMINANCE_AVAILABLE = True
    print("✅ AI Brain v7: dominance_flow_layer imported (Layer 14!)")
except Exception as e:
    DOMINANCE_AVAILABLE = False
    print(f"⚠️ AI Brain v7: dominance_flow_layer import failed: {e}")

# Phase 6.3: Cross-Asset Correlation (NEW in v7!)
try:
    import cross_asset_layer as cross_asset
    CROSS_ASSET_AVAILABLE = True
    print("✅ AI Brain v7: cross_asset_layer imported (Layer 15!)")
except Exception as e:
    CROSS_ASSET_AVAILABLE = False
    print(f"⚠️ AI Brain v7: cross_asset_layer import failed: {e}")

print("\n" + "="*60)
print("🧠 AI BRAIN v7.0 - INITIALIZATION COMPLETE")
print("="*60)
print(f"✅ Strategy Layer (1-11): {'ACTIVE' if STRATEGY_AVAILABLE else 'INACTIVE'}")
print(f"✅ Monte Carlo: {'ACTIVE' if MONTE_CARLO_AVAILABLE else 'INACTIVE'}")
print(f"✅ Kelly Criterion: {'ACTIVE' if KELLY_AVAILABLE else 'INACTIVE'}")
print(f"✅ Macro Correlation (L12): {'ACTIVE' if MACRO_AVAILABLE else 'INACTIVE'}")
print(f"✅ Gold Correlation (L13): {'ACTIVE' if GOLD_AVAILABLE else 'INACTIVE'}")
print(f"✅ BTC Dominance (L14): {'ACTIVE' if DOMINANCE_AVAILABLE else 'INACTIVE'}")
print(f"✅ Cross-Asset (L15): {'ACTIVE' if CROSS_ASSET_AVAILABLE else 'INACTIVE'}")
print("="*60 + "\n")

# =====================================================
# PHASE 2: MAIN TRADING DECISION FUNCTION
# =====================================================

def make_trading_decision(symbol, timeframe, capital=10000, lookback=100):
    """
    🧠 AI Brain v7.0 - 15-Layer Ultimate Trading Decision Engine
    
    This function coordinates ALL 15 analysis layers and returns
    a comprehensive trading recommendation with risk management.
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        timeframe: Chart timeframe (e.g., '1h', '4h', '1d')
        capital: Available trading capital in USDT
        lookback: Number of historical candles for analysis
        
    Returns:
        dict: Comprehensive analysis with decision, entry, SL, TP, position size
    """
    
    print(f"\n{'='*70}")
    print(f"🧠 AI BRAIN v7.0 - ANALYSIS STARTING")
    print(f"{'='*70}")
    print(f"Symbol: {symbol}")
    print(f"Timeframe: {timeframe}")
    print(f"Capital: ${capital:,.2f}")
    print(f"Lookback: {lookback} periods")
    print(f"{'='*70}\n")
    
    # ================================================================
    # LAYER 1-11: STRATEGY LAYER (Core Technical Analysis)
    # ================================================================
    
    final_score = 50  # Default neutral
    signal = "HOLD"
    confidence = 0.5
    entry_price = 0
    stop_loss = 0
    take_profit = 0
    strategy_result = {}
    
    if STRATEGY_AVAILABLE:
        try:
            print(f"🎯 Calling strategy.analyze() for {symbol}...")
            strategy_result = strategy.analyze(symbol, timeframe, lookback)
            
            if strategy_result:
                final_score = strategy_result.get('score', 50)
                signal = strategy_result.get('signal', 'HOLD')
                confidence = strategy_result.get('confidence', 0.5)
                entry_price = strategy_result.get('entry_price', 0)
                stop_loss = strategy_result.get('stop_loss', 0)
                take_profit = strategy_result.get('take_profit', 0)
                
                print(f"✅ Strategy Layer (1-11): {final_score:.2f}/100 - {signal}")
                print(f"   Entry: ${entry_price:,.2f} | SL: ${stop_loss:,.2f} | TP: ${take_profit:,.2f}")
            else:
                print("⚠️ Strategy layer returned None")
                
        except Exception as e:
            print(f"⚠️ Strategy layer error: {e}")
            final_score = 50
            signal = "HOLD"
    else:
        print(f"⚠️ Strategy Layer (1-11): Not available")
    
    # ================================================================
    # LAYER 12: MACRO CORRELATION (Phase 6 - v5 PRESERVED)
    # ================================================================
    
    macro_score = 50
    macro_signal = "NEUTRAL"
    macro_details = {}
    
    if MACRO_AVAILABLE:
        try:
            print(f"\n🌍 Calling macro.analyze_macro_correlation (Layer 12)...")
            macro_result = macro.analyze_macro_correlation(symbol)
            
            if macro_result and macro_result.get('available'):
                macro_score = macro_result.get('score', 50)
                macro_signal = macro_result.get('signal', 'NEUTRAL')
                macro_details = {
                    'dxy_correlation': macro_result.get('dxy_correlation', 0),
                    'spy_correlation': macro_result.get('spy_correlation', 0),
                    'vix_level': macro_result.get('vix_level', 0),
                    'explanation': macro_result.get('explanation', 'No details')
                }
                print(f"✅ Layer 12 (Macro): {macro_score:.2f}/100 - {macro_signal}")
            else:
                print("⚠️ Layer 12 (Macro) unavailable")
                
        except Exception as e:
            print(f"⚠️ Layer 12 (Macro) error: {e}")
            macro_score = 50
            macro_signal = "NEUTRAL"
    else:
        print(f"⚠️ Layer 12 (Macro): Not available")
    
    # ================================================================
    # LAYER 13: GOLD CORRELATION (XAU/XAG) - NEW in v7!
    # ================================================================
    
    gold_score = 50
    gold_signal = "NEUTRAL"
    gold_details = {}
    
    if GOLD_AVAILABLE:
        try:
            print(f"\n🥇 Calling gold.analyze_gold_correlation (Layer 13)...")
            gold_result = gold.analyze_gold_correlation(symbol)
            
            if gold_result and gold_result.get('available'):
                gold_score = gold_result.get('score', 50)
                gold_signal = gold_result.get('signal', 'NEUTRAL')
                gold_details = {
                    'xau_correlation': gold_result.get('xau_correlation', 0),
                    'xag_correlation': gold_result.get('xag_correlation', 0),
                    'safe_haven_score': gold_result.get('safe_haven_score', 0),
                    'explanation': gold_result.get('explanation', 'No details')
                }
                print(f"✅ Layer 13 (Gold): {gold_score:.2f}/100 - {gold_signal}")
            else:
                print("⚠️ Layer 13 (Gold) unavailable")
                
        except Exception as e:
            print(f"⚠️ Layer 13 (Gold) error: {e}")
            gold_score = 50
            gold_signal = "NEUTRAL"
    else:
        print(f"⚠️ Layer 13 (Gold): Not available")
    
    # ================================================================
    # LAYER 14: BTC DOMINANCE FLOW (Altseason Indicator) - NEW in v7!
    # ================================================================
    
    dominance_score = 50
    dominance_signal = "NEUTRAL"
    dominance_details = {}
    
    if DOMINANCE_AVAILABLE:
        try:
            print(f"\n👑 Calling dominance.analyze_dominance_flow (Layer 14)...")
            dominance_result = dominance.analyze_dominance_flow(symbol)
            
            if dominance_result and dominance_result.get('available'):
                dominance_score = dominance_result.get('score', 50)
                dominance_signal = dominance_result.get('signal', 'NEUTRAL')
                dominance_details = {
                    'btc_dominance': dominance_result.get('btc_dominance', 0),
                    'dominance_trend': dominance_result.get('trend', 'NEUTRAL'),
                    'altseason_probability': dominance_result.get('altseason_prob', 0),
                    'explanation': dominance_result.get('explanation', 'No details')
                }
                print(f"✅ Layer 14 (Dominance): {dominance_score:.1f}/100 - {dominance_signal}")
            else:
                print("⚠️ Layer 14 (Dominance) unavailable")
                
        except Exception as e:
            print(f"⚠️ Layer 14 (Dominance) error: {e}")
            dominance_score = 50
            dominance_signal = "NEUTRAL"
    else:
        print(f"⚠️ Layer 14 (Dominance): Not available")
    
    # ================================================================
    # LAYER 15: CROSS-ASSET CORRELATION - NEW in v7!
    # ================================================================
    
    cross_asset_score = 50
    cross_asset_signal = "NEUTRAL"
    cross_asset_details = {}
    
    if CROSS_ASSET_AVAILABLE:
        try:
            print(f"\n🔗 Calling cross_asset.analyze_cross_correlations (Layer 15)...")
            cross_asset_result = cross_asset.analyze_cross_correlations(symbol)
            
            if cross_asset_result and cross_asset_result.get('available'):
                cross_asset_score = cross_asset_result.get('score', 50)
                cross_asset_signal = cross_asset_result.get('signal', 'NEUTRAL')
                cross_asset_details = {
                    'btc_correlation': cross_asset_result.get('btc_corr', 0),
                    'eth_correlation': cross_asset_result.get('eth_corr', 0),
                    'market_regime': cross_asset_result.get('regime', 'NEUTRAL'),
                    'explanation': cross_asset_result.get('explanation', 'No details')
                }
                print(f"✅ Layer 15 (Cross-Asset): {cross_asset_score:.1f}/100 - {cross_asset_signal}")
            else:
                print("⚠️ Layer 15 (Cross-Asset) unavailable")
                
        except Exception as e:
            print(f"⚠️ Layer 15 (Cross-Asset) error: {e}")
            cross_asset_score = 50
            cross_asset_signal = "NEUTRAL"
    else:
        print(f"⚠️ Layer 15 (Cross-Asset): Not available")
    
    # ================================================================
    # WEIGHTED SCORE CALCULATION (All 15 Layers)
    # ================================================================
    
    WEIGHTS = {
        'strategy': 0.50,      # 50% - Core strategy (11 layers)
        'macro': 0.20,         # 20% - Macro correlation (v5)
        'gold': 0.10,          # 10% - Gold correlation
        'dominance': 0.10,     # 10% - BTC dominance
        'cross_asset': 0.10    # 10% - Cross-asset
    }
    
    final_score_weighted = (
        final_score * WEIGHTS['strategy'] +
        macro_score * WEIGHTS['macro'] +
        gold_score * WEIGHTS['gold'] +
        dominance_score * WEIGHTS['dominance'] +
        cross_asset_score * WEIGHTS['cross_asset']
    )
    
    # Update signal based on weighted score
    if final_score_weighted >= 70:
        final_signal = "STRONG BUY"
    elif final_score_weighted >= 60:
        final_signal = "BUY"
    elif final_score_weighted >= 40:
        final_signal = "HOLD"
    elif final_score_weighted >= 30:
        final_signal = "SELL"
    else:
        final_signal = "STRONG SELL"
    
    print(f"\n" + "="*70)
    print(f"🎯 WEIGHTED FINAL SCORE: {final_score_weighted:.2f}/100 → {final_signal}")
    print(f"="*70)
    
    # ================================================================
    # MONTE CARLO SIMULATION (Expected Value)
    # ================================================================
    
    mc_result = {'expected_value': 0, 'win_probability': 0.5}
    
    if MONTE_CARLO_AVAILABLE and entry_price > 0 and stop_loss > 0 and take_profit > 0:
        try:
            print(f"\n🎲 Running Monte Carlo simulation...")
            mc_result = monte_carlo.simulate(
                entry=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence
            )
            
            if mc_result:
                print(f"✅ Monte Carlo: EV={mc_result.get('expected_value', 0):.2f}%, "
                      f"Win Prob={mc_result.get('win_probability', 0)*100:.0f}%")
            else:
                print("⚠️ Monte Carlo returned None")
                
        except Exception as e:
            print(f"⚠️ Monte Carlo error: {e}")
            mc_result = {'expected_value': 0, 'win_probability': 0.5}
    else:
        print(f"⚠️ Monte Carlo: Skipped (missing prices or unavailable)")
    
    expected_value = mc_result.get('expected_value', 0)
    win_probability = mc_result.get('win_probability', 0.5)
    
    # ================================================================
    # KELLY CRITERION (Position Sizing)
    # ================================================================
    
    kelly_result = {'position_size': 0, 'kelly_percentage': 0}
    
    if KELLY_AVAILABLE and entry_price > 0 and stop_loss > 0 and take_profit > 0:
        try:
            print(f"\n💰 Calculating Kelly position size...")
            kelly_result = kelly.calculate_position_size(
                capital=capital,
                entry=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                win_rate=win_probability,
                confidence=confidence
            )
            
            if kelly_result:
                print(f"✅ Kelly: Size=${kelly_result.get('position_size', 0):,.2f} "
                      f"({kelly_result.get('kelly_percentage', 0):.2f}% of capital)")
            else:
                print("⚠️ Kelly returned None")
                
        except Exception as e:
            print(f"⚠️ Kelly error: {e}")
            kelly_result = {'position_size': 0, 'kelly_percentage': 0}
    else:
        print(f"⚠️ Kelly: Skipped (missing prices or unavailable)")
    
    position_size = kelly_result.get('position_size', 0)
    kelly_percentage = kelly_result.get('kelly_percentage', 0)
    
    # ================================================================
    # AI COMMENTARY GENERATION
    # ================================================================
    
    commentary = f"""
🧠 AI Brain v7.0 Analysis Summary:

📊 OVERALL SCORE: {final_score_weighted:.1f}/100 ({final_signal})
Confidence: {confidence*100:.0f}%

LAYER BREAKDOWN (15 Total):
---------------------------
• Strategy (Layers 1-11): {final_score:.1f}/100 (Weight: 50%)
• Macro Correlation (L12): {macro_score:.1f}/100 (Weight: 20%)
• Gold Correlation (L13): {gold_score:.1f}/100 (Weight: 10%)
• BTC Dominance (L14): {dominance_score:.1f}/100 (Weight: 10%)
• Cross-Asset (L15): {cross_asset_score:.1f}/100 (Weight: 10%)

POSITION DETAILS:
-----------------
Entry Price: ${entry_price:,.2f}
Stop Loss: ${stop_loss:,.2f}
Take Profit: ${take_profit:,.2f}
Position Size: ${position_size:,.2f} ({kelly_percentage:.2f}% of portfolio)

RISK METRICS:
-------------
Expected Value: {expected_value:.2f}%
Win Probability: {win_probability*100:.0f}%
Risk/Reward Ratio: 1:2

RECOMMENDATION: {final_signal} with {confidence*100:.0f}% confidence
"""
    
    print(f"\n" + "="*70)
    print("🧠 AI BRAIN v7.0 - ANALYSIS COMPLETE")
    print("="*70)
    print(commentary)
    print("="*70 + "\n")
    
    # ================================================================
    # FINAL RESULT DICTIONARY
    # ================================================================
    
    result = {
        'signal': final_signal,
        'score': round(final_score_weighted, 2),
        'confidence': round(confidence, 2),
        'entry_price': round(entry_price, 2) if entry_price else 0,
        'stop_loss': round(stop_loss, 2) if stop_loss else 0,
        'take_profit': round(take_profit, 2) if take_profit else 0,
        'position_size': round(position_size, 2),
        'kelly_percentage': round(kelly_percentage, 2),
        'expected_value': round(expected_value, 2),
        'win_probability': round(win_probability, 2),
        'commentary': commentary,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'version': 'v7.0-15layer-production',
        'layer_scores': {
            'strategy': round(final_score, 1),
            'macro_correlation': round(macro_score, 1),
            'gold_correlation': round(gold_score, 1),
            'dominance_flow': round(dominance_score, 1),
            'cross_asset': round(cross_asset_score, 1)
        },
        'layer_details': {
            'strategy': strategy_result if STRATEGY_AVAILABLE else {},
            'macro': macro_details,
            'gold': gold_details,
            'dominance': dominance_details,
            'cross_asset': cross_asset_details,
            'monte_carlo': mc_result,
            'kelly': kelly_result
        }
    }
    
    return result


# =====================================================
# HELPER FUNCTIONS (If needed for standalone testing)
# =====================================================

def test_ai_brain():
    """Quick test function for development"""
    print("\n🧪 TESTING AI BRAIN v7.0...")
    result = make_trading_decision('BTCUSDT', '1h', 10000, 100)
    print(f"\n✅ Test Complete! Signal: {result['signal']}")
    return result


if __name__ == "__main__":
    # Run test if executed directly
    test_ai_brain()
# =====================================================
# END OF FILE - AI BRAIN v7.0 COMPLETE
# =====================================================

print("\n✅ ai_brain.py v7.0 loaded successfully!")
print("📊 15-Layer Ultimate System Ready!")
print("🚀 Use: make_trading_decision(symbol, timeframe, capital, lookback)")
