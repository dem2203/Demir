"""
🔱 DEMIR AI TRADING BOT - AI Brain v6.0 ULTIMATE MERGE
======================================================
Date: 2 Kasım 2025, 00:57 CET
Version: 6.0 - 14-LAYER ULTIMATE SYSTEM

EVOLUTION:
----------
v4: Phase 3A + 3B (11 layers)
v5: Phase 6 MACRO (12 layers - added macro_correlation_layer)
v6: ULTIMATE MERGE (14 layers - added gold, dominance, cross-asset)

ALL 14 LAYERS:
--------------
1. Historical Volatility
2. GARCH Volatility
3. Fibonacci Retracement
4. Markov Regime
5. Volume Profile
6. VWAP Deviation
7. Pivot Points
8. Volatility Squeeze
9-11. Macro Correlation (SPX, NASDAQ, DXY, Gold, Silver, BTC.D, USDT.D, VIX, US10Y, OIL, EURUSD)
12. Gold Correlation (XAU, XAG, Gold/BTC ratio) ⭐ NEW
13. BTC Dominance Flow (BTC.D, USDT.D, Altseason detector) ⭐ NEW
14. Cross-Asset Correlation (BTC/ETH/LTC/BNB rotation) ⭐ NEW

COMPATIBILITY:
--------------
✅ Works with existing streamlit_app.py (NO changes needed!)
✅ Returns same structure ('decision', 'layer_scores', etc.)
✅ Backwards compatible with v4 and v5

NO LAYERS REMOVED - ADDITIVE ONLY!
"""

from datetime import datetime

# ============================================================================
# IMPORTS - PHASE 1-5 (PRESERVED)
# ============================================================================

# Phase 1-2: Core Technical Layers
from historical_volatility_layer import calculate_historical_volatility
from garch_volatility_layer import calculate_garch_volatility
from fibonacci_layer import calculate_fibonacci_levels
from markov_regime_layer import calculate_markov_regime

# Phase 3A: Advanced Technical Layers
from volume_profile_layer import calculate_volume_profile
from vwap_layer import calculate_vwap_deviation
from pivot_points_layer import calculate_pivot_points
from volatility_squeeze_layer import calculate_volatility_squeeze

# Phase 6 (v5): Macro Correlation Layer
try:
    from macro_correlation_layer import calculate_macro_correlation
    MACRO_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: macro_correlation_layer not found (v5 feature)")
    MACRO_AVAILABLE = False

# ============================================================================
# PHASE 6 NEW IMPORTS (v6.0) ⭐ NEW
# ============================================================================

# Phase 6.2: Gold & Precious Metals Correlation
try:
    from gold_correlation_layer import calculate_gold_correlation
    GOLD_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: gold_correlation_layer not found (Phase 6.2)")
    GOLD_AVAILABLE = False

# Phase 6.3: BTC Dominance & Money Flow
try:
    from dominance_flow_layer import calculate_dominance_flow
    DOMINANCE_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: dominance_flow_layer not found (Phase 6.3)")
    DOMINANCE_AVAILABLE = False

# Phase 6.4: Cross-Asset Correlation
try:
    from cross_asset_layer import calculate_cross_asset
    CROSS_ASSET_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: cross_asset_layer not found (Phase 6.4)")
    CROSS_ASSET_AVAILABLE = False

# ============================================================================
# LAYER WEIGHTS (Total = 100%)
# ============================================================================
LAYER_WEIGHTS = {
    # Core Technical (Layers 1-8) - 56%
    'historical_volatility': 0.07,   # 7%
    'garch_volatility': 0.07,        # 7%
    'fibonacci': 0.07,               # 7%
    'markov_regime': 0.07,           # 7%
    'volume_profile': 0.07,          # 7%
    'vwap': 0.07,                    # 7%
    'pivot_points': 0.07,            # 7%
    'volatility_squeeze': 0.07,      # 7%
    
    # Macro Analysis (Layers 9-11) - 22%
    'macro_correlation': 0.22,       # 22% (11 factors combined)
    
    # Phase 6 New Layers (12-14) - 22% ⭐ NEW
    'gold_correlation': 0.08,        # 8%
    'dominance_flow': 0.07,          # 7%
    'cross_asset': 0.07              # 7%
}

# ============================================================================
# MAIN DECISION ENGINE
# ============================================================================
def get_ai_decision(symbol='BTCUSDT', interval='1h', limit=500):
    """
    ULTIMATE 14-LAYER AI DECISION ENGINE
    
    Returns:
        dict: Complete analysis with decision, scores, and layer details
    """
    
    print(f"\n🧠 AI BRAIN v6.0 - 14-LAYER ULTIMATE ANALYSIS")
    print(f"Symbol: {symbol} | Interval: {interval}")
    print("=" * 70)
    
    layer_scores = {}
    layer_details = {}
    total_weight = 0
    weighted_sum = 0
    layers_active = 0
    
    # ========================================================================
    # LAYER 1: HISTORICAL VOLATILITY
    # ========================================================================
    try:
        print("📊 Layer 1: Historical Volatility...", end=" ")
        hv_result = calculate_historical_volatility(symbol, interval, limit)
        if hv_result and hv_result.get('available'):
            score = hv_result.get('score', 50)
            layer_scores['historical_volatility'] = score
            layer_details['historical_volatility'] = hv_result
            weighted_sum += score * LAYER_WEIGHTS['historical_volatility']
            total_weight += LAYER_WEIGHTS['historical_volatility']
            layers_active += 1
            print(f"✅ {score:.1f}")
        else:
            print("⚠️ Unavailable")
    except Exception as e:
        print(f"❌ Error: {str(e)[:40]}")
    
    # ========================================================================
    # LAYER 2: GARCH VOLATILITY
    # ========================================================================
    try:
        print("📈 Layer 2: GARCH Volatility...", end=" ")
        garch_result = calculate_garch_volatility(symbol, interval, limit)
        if garch_result and garch_result.get('available'):
            score = garch_result.get('score', 50)
            layer_scores['garch_volatility'] = score
            layer_details['garch_volatility'] = garch_result
            weighted_sum += score * LAYER_WEIGHTS['garch_volatility']
            total_weight += LAYER_WEIGHTS['garch_volatility']
            layers_active += 1
            print(f"✅ {score:.1f}")
        else:
            print("⚠️ Unavailable")
    except Exception as e:
        print(f"❌ Error: {str(e)[:40]}")
    
    # ========================================================================
    # LAYER 3: FIBONACCI
    # ========================================================================
    try:
        print("🔢 Layer 3: Fibonacci Levels...", end=" ")
        fib_result = calculate_fibonacci_levels(symbol, interval, limit)
        if fib_result and fib_result.get('available'):
            score = fib_result.get('score', 50)
            layer_scores['fibonacci'] = score
            layer_details['fibonacci'] = fib_result
            weighted_sum += score * LAYER_WEIGHTS['fibonacci']
            total_weight += LAYER_WEIGHTS['fibonacci']
            layers_active += 1
            print(f"✅ {score:.1f}")
        else:
            print("⚠️ Unavailable")
    except Exception as e:
        print(f"❌ Error: {str(e)[:40]}")
    
    # ========================================================================
    # LAYER 4: MARKOV REGIME
    # ========================================================================
    try:
        print("🎲 Layer 4: Markov Regime...", end=" ")
        markov_result = calculate_markov_regime(symbol, interval, limit)
        if markov_result and markov_result.get('available'):
            score = markov_result.get('score', 50)
            layer_scores['markov_regime'] = score
            layer_details['markov_regime'] = markov_result
            weighted_sum += score * LAYER_WEIGHTS['markov_regime']
            total_weight += LAYER_WEIGHTS['markov_regime']
            layers_active += 1
            print(f"✅ {score:.1f}")
        else:
            print("⚠️ Unavailable")
    except Exception as e:
        print(f"❌ Error: {str(e)[:40]}")
    
    # ========================================================================
    # LAYER 5: VOLUME PROFILE
    # ========================================================================
    try:
        print("📊 Layer 5: Volume Profile...", end=" ")
        vol_result = calculate_volume_profile(symbol, interval, limit)
        if vol_result and vol_result.get('available'):
            score = vol_result.get('score', 50)
            layer_scores['volume_profile'] = score
            layer_details['volume_profile'] = vol_result
            weighted_sum += score * LAYER_WEIGHTS['volume_profile']
            total_weight += LAYER_WEIGHTS['volume_profile']
            layers_active += 1
            print(f"✅ {score:.1f}")
        else:
            print("⚠️ Unavailable")
    except Exception as e:
        print(f"❌ Error: {str(e)[:40]}")
    
    # ========================================================================
    # LAYER 6: VWAP
    # ========================================================================
    try:
        print("📈 Layer 6: VWAP Deviation...", end=" ")
        vwap_result = calculate_vwap_deviation(symbol, interval, limit)
        if vwap_result and vwap_result.get('available'):
            score = vwap_result.get('score', 50)
            layer_scores['vwap'] = score
            layer_details['vwap'] = vwap_result
            weighted_sum += score * LAYER_WEIGHTS['vwap']
            total_weight += LAYER_WEIGHTS['vwap']
            layers_active += 1
            print(f"✅ {score:.1f}")
        else:
            print("⚠️ Unavailable")
    except Exception as e:
        print(f"❌ Error: {str(e)[:40]}")
    
    # ========================================================================
    # LAYER 7: PIVOT POINTS
    # ========================================================================
    try:
        print("🎯 Layer 7: Pivot Points...", end=" ")
        pivot_result = calculate_pivot_points(symbol, interval, limit)
        if pivot_result and pivot_result.get('available'):
            score = pivot_result.get('score', 50)
            layer_scores['pivot_points'] = score
            layer_details['pivot_points'] = pivot_result
            weighted_sum += score * LAYER_WEIGHTS['pivot_points']
            total_weight += LAYER_WEIGHTS['pivot_points']
            layers_active += 1
            print(f"✅ {score:.1f}")
        else:
            print("⚠️ Unavailable")
    except Exception as e:
        print(f"❌ Error: {str(e)[:40]}")
    
    # ========================================================================
    # LAYER 8: VOLATILITY SQUEEZE
    # ========================================================================
    try:
        print("💥 Layer 8: Volatility Squeeze...", end=" ")
        squeeze_result = calculate_volatility_squeeze(symbol, interval, limit)
        if squeeze_result and squeeze_result.get('available'):
            score = squeeze_result.get('score', 50)
            layer_scores['volatility_squeeze'] = score
            layer_details['volatility_squeeze'] = squeeze_result
            weighted_sum += score * LAYER_WEIGHTS['volatility_squeeze']
            total_weight += LAYER_WEIGHTS['volatility_squeeze']
            layers_active += 1
            print(f"✅ {score:.1f}")
        else:
            print("⚠️ Unavailable")
    except Exception as e:
        print(f"❌ Error: {str(e)[:40]}")
    
    # ========================================================================
    # LAYERS 9-11: MACRO CORRELATION (v5 - PRESERVED)
    # ========================================================================
    if MACRO_AVAILABLE:
        try:
            print("🌍 Layers 9-11: Macro Correlation (SPX/NASDAQ/DXY/Gold/VIX...)...", end=" ")
            macro_result = calculate_macro_correlation()
            if macro_result and macro_result.get('available'):
                score = macro_result.get('score', 50)
                layer_scores['macro_correlation'] = score
                layer_details['macro_correlation'] = macro_result
                weighted_sum += score * LAYER_WEIGHTS['macro_correlation']
                total_weight += LAYER_WEIGHTS['macro_correlation']
                layers_active += 1
                print(f"✅ {score:.1f}")
            else:
                print("⚠️ Unavailable")
        except Exception as e:
            print(f"❌ Error: {str(e)[:40]}")
    else:
        print("🌍 Layers 9-11: Macro Correlation... ⏭️ Skipped (not installed)")
    
    # ========================================================================
    # LAYER 12: GOLD CORRELATION ⭐ NEW (Phase 6.2)
    # ========================================================================
    if GOLD_AVAILABLE:
        try:
            print("🥇 Layer 12: Gold Correlation (XAU/XAG)...", end=" ")
            gold_result = calculate_gold_correlation(symbol, interval, limit)
            if gold_result and gold_result.get('available'):
                score = gold_result.get('score', 50)
                layer_scores['gold_correlation'] = score
                layer_details['gold_correlation'] = gold_result
                weighted_sum += score * LAYER_WEIGHTS['gold_correlation']
                total_weight += LAYER_WEIGHTS['gold_correlation']
                layers_active += 1
                print(f"✅ {score:.1f}")
            else:
                print("⚠️ Unavailable")
        except Exception as e:
            print(f"❌ Error: {str(e)[:40]}")
    else:
        print("🥇 Layer 12: Gold Correlation... ⏭️ Skipped (not installed)")
    
    # ========================================================================
    # LAYER 13: BTC DOMINANCE FLOW ⭐ NEW (Phase 6.3)
    # ========================================================================
    if DOMINANCE_AVAILABLE:
        try:
            print("📊 Layer 13: BTC Dominance Flow (Altseason detector)...", end=" ")
            dom_result = calculate_dominance_flow()
            if dom_result and dom_result.get('available'):
                score = dom_result.get('score', 50)
                layer_scores['dominance_flow'] = score
                layer_details['dominance_flow'] = dom_result
                weighted_sum += score * LAYER_WEIGHTS['dominance_flow']
                total_weight += LAYER_WEIGHTS['dominance_flow']
                layers_active += 1
                print(f"✅ {score:.1f}")
            else:
                print("⚠️ Unavailable")
        except Exception as e:
            print(f"❌ Error: {str(e)[:40]}")
    else:
        print("📊 Layer 13: BTC Dominance Flow... ⏭️ Skipped (not installed)")
    
    # ========================================================================
    # LAYER 14: CROSS-ASSET CORRELATION ⭐ NEW (Phase 6.4)
    # ========================================================================
    if CROSS_ASSET_AVAILABLE:
        try:
            print("🔗 Layer 14: Cross-Asset Correlation (BTC/ETH/LTC/BNB)...", end=" ")
            cross_result = calculate_cross_asset(interval, limit)
            if cross_result and cross_result.get('available'):
                score = cross_result.get('score', 50)
                layer_scores['cross_asset'] = score
                layer_details['cross_asset'] = cross_result
                weighted_sum += score * LAYER_WEIGHTS['cross_asset']
                total_weight += LAYER_WEIGHTS['cross_asset']
                layers_active += 1
                print(f"✅ {score:.1f}")
            else:
                print("⚠️ Unavailable")
        except Exception as e:
            print(f"❌ Error: {str(e)[:40]}")
    else:
        print("🔗 Layer 14: Cross-Asset Correlation... ⏭️ Skipped (not installed)")
    
    # ========================================================================
    # CALCULATE FINAL SCORE
    # ========================================================================
    if total_weight > 0:
        final_score = round(weighted_sum / total_weight, 2)
    else:
        final_score = 50.0
    
    # Determine decision
    if final_score >= 65:
        decision = "BUY"
        confidence = "HIGH" if final_score >= 75 else "MODERATE"
    elif final_score >= 55:
        decision = "HOLD/BUY"
        confidence = "MODERATE"
    elif final_score >= 45:
        decision = "HOLD"
        confidence = "LOW"
    elif final_score >= 35:
        decision = "HOLD/SELL"
        confidence = "MODERATE"
    else:
        decision = "SELL"
        confidence = "HIGH" if final_score <= 25 else "MODERATE"
    
    # ========================================================================
    # PRINT SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print(f"🎯 FINAL SCORE: {final_score}/100")
    print(f"📊 Active Layers: {layers_active}/14")
    print(f"💡 DECISION: {decision} (Confidence: {confidence})")
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Layer breakdown
    print("\n📊 LAYER BREAKDOWN:")
    for layer_name, score in sorted(layer_scores.items(), key=lambda x: x[1], reverse=True):
        weight_pct = LAYER_WEIGHTS.get(layer_name, 0) * 100
        print(f"  • {layer_name}: {score:.1f} (weight: {weight_pct:.0f}%)")
    
    print("=" * 70)
    
    # Return result
    return {
        'decision': decision,
        'confidence': confidence,
        'final_score': final_score,
        'layer_scores': layer_scores,
        'layer_details': layer_details,
        'layers_active': layers_active,
        'total_layers': 14,
        'timestamp': datetime.now().isoformat(),
        'symbol': symbol,
        'interval': interval,
        'version': 'v6.0-14layer'
    }

# ============================================================================
# HELPER FUNCTIONS (PRESERVED FROM v5)
# ============================================================================
def get_strongest_signals(result, top_n=3):
    """Get strongest bullish/bearish signals"""
    layer_scores = result.get('layer_scores', {})
    sorted_scores = sorted(layer_scores.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'most_bullish': sorted_scores[:top_n],
        'most_bearish': sorted_scores[-top_n:][::-1]
    }

def get_layer_summary(result):
    """Get quick summary of all layers"""
    summary = []
    for layer_name, score in result.get('layer_scores', {}).items():
        summary.append({
            'layer': layer_name,
            'score': score,
            'weight': LAYER_WEIGHTS.get(layer_name, 0) * 100
        })
    return sorted(summary, key=lambda x: x['score'], reverse=True)

# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("🚀 AI BRAIN v6.0 - ULTIMATE 14-LAYER SYSTEM")
    print("=" * 70)
    print("ALL LAYERS ACTIVE (NO REMOVALS):")
    print("  Layers 1-8: Core Technical")
    print("  Layers 9-11: Macro Correlation (v5)")
    print("  Layer 12: Gold Correlation (Phase 6.2) ⭐ NEW")
    print("  Layer 13: BTC Dominance Flow (Phase 6.3) ⭐ NEW")
    print("  Layer 14: Cross-Asset Correlation (Phase 6.4) ⭐ NEW")
    print("=" * 70)
    
    # Run analysis
    result = get_ai_decision('BTCUSDT', '1h', 500)
    
    # Print strongest signals
    print("\n🎯 STRONGEST SIGNALS:")
    signals = get_strongest_signals(result)
    print("  BULLISH:")
    for layer, score in signals['most_bullish']:
        print(f"    • {layer}: {score:.1f}")
    print("  BEARISH:")
    for layer, score in signals['most_bearish']:
        print(f"    • {layer}: {score:.1f}")
