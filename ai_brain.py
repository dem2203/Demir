"""
🧠 AI BRAIN - ENHANCED 11-LAYER ANALYSIS ENGINE
================================================
Date: 2 Kasım 2025, 00:29 CET
Version: 2.0 - Phase 6 Complete

PHASE 6 NEW ADDITIONS:
• Layer 9: Gold Correlation (Safe-haven flow analysis)
• Layer 10: BTC Dominance & Money Flow (Altseason detector)  
• Layer 11: Cross-Asset Correlation (Asset rotation signals)

ALL 11 LAYERS:
1. Historical Volatility
2. GARCH Volatility Forecast
3. Fibonacci Retracement
4. Markov Regime Detection
5. Volume Profile
6. VWAP Deviation
7. Pivot Points
8. Volatility Squeeze
9. Gold Correlation ⭐ NEW
10. BTC Dominance Flow ⭐ NEW
11. Cross-Asset Correlation ⭐ NEW

FINAL SCORE: Weighted average (0-100)
RECOMMENDATION: BUY / HOLD / SELL based on score + layers
"""

# ============================================================================
# IMPORTS
# ============================================================================
import sys
import traceback
from datetime import datetime

# Existing layers (Phase 1-5)
from historical_volatility_layer import calculate_historical_volatility
from garch_volatility_layer import calculate_garch_volatility
from fibonacci_layer import calculate_fibonacci_levels
from markov_regime_layer import calculate_markov_regime
from volume_profile_layer import calculate_volume_profile
from vwap_layer import calculate_vwap_deviation
from pivot_points_layer import calculate_pivot_points
from volatility_squeeze_layer import calculate_volatility_squeeze

# PHASE 6: NEW LAYERS - Macro & Cross-Asset Analysis
try:
    from gold_correlation_layer import calculate_gold_correlation
    GOLD_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: gold_correlation_layer not found (Phase 6.2)")
    GOLD_AVAILABLE = False

try:
    from dominance_flow_layer import calculate_dominance_flow
    DOMINANCE_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: dominance_flow_layer not found (Phase 6.3)")
    DOMINANCE_AVAILABLE = False

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
    'historical_volatility': 0.10,   # 10%
    'garch_volatility': 0.10,        # 10%
    'fibonacci': 0.10,               # 10%
    'markov_regime': 0.10,           # 10%
    'volume_profile': 0.08,          # 8%
    'vwap': 0.08,                    # 8%
    'pivot_points': 0.08,            # 8%
    'volatility_squeeze': 0.08,      # 8%
    'gold_correlation': 0.09,        # 9% ⭐ NEW (Phase 6.2)
    'dominance_flow': 0.10,          # 10% ⭐ NEW (Phase 6.3)
    'cross_asset': 0.09              # 9% ⭐ NEW (Phase 6.4)
}

# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================
def calculate_all_layers(symbol='BTCUSDT', interval='1h', limit=500):
    """
    Calculate all 11 layers and return comprehensive analysis
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        interval: Timeframe ('1m', '5m', '15m', '1h', '4h', '1d')
        limit: Number of candles to analyze
    
    Returns:
        dict: Complete 11-layer analysis with final score & recommendation
    """
    
    print(f"\n🧠 AI BRAIN ANALYSIS - {symbol} ({interval})")
    print("=" * 70)
    
    results = {
        'symbol': symbol,
        'interval': interval,
        'timestamp': datetime.now().isoformat(),
        'layers': {},
        'final_score': 0,
        'weighted_score': 0,
        'interpretation': '',
        'recommendation': '',
        'confidence': 0,
        'available_layers': 0,
        'total_layers': 11,
        'phase_6_enabled': GOLD_AVAILABLE and DOMINANCE_AVAILABLE and CROSS_ASSET_AVAILABLE
    }
    
    weighted_sum = 0
    total_weight = 0
    
    # ========================================================================
    # LAYER 1: HISTORICAL VOLATILITY
    # ========================================================================
    try:
        print("📊 Layer 1: Historical Volatility...", end=" ")
        hv_result = calculate_historical_volatility(symbol, interval, limit)
        if hv_result and hv_result.get('available'):
            results['layers']['historical_volatility'] = hv_result
            score = hv_result.get('score', 50)
            weighted_sum += score * LAYER_WEIGHTS['historical_volatility']
            total_weight += LAYER_WEIGHTS['historical_volatility']
            results['available_layers'] += 1
            print(f"✅ Score: {score:.1f}")
        else:
            print("⚠️ Unavailable")
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
        traceback.print_exc()
    
    # ========================================================================
    # LAYER 2: GARCH VOLATILITY
    # ========================================================================
    try:
        print("📈 Layer 2: GARCH Volatility...", end=" ")
        garch_result = calculate_garch_volatility(symbol, interval, limit)
        if garch_result and garch_result.get('available'):
            results['layers']['garch_volatility'] = garch_result
            score = garch_result.get('score', 50)
            weighted_sum += score * LAYER_WEIGHTS['garch_volatility']
            total_weight += LAYER_WEIGHTS['garch_volatility']
            results['available_layers'] += 1
            print(f"✅ Score: {score:.1f}")
        else:
            print("⚠️ Unavailable")
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
    
    # ========================================================================
    # LAYER 3: FIBONACCI
    # ========================================================================
    try:
        print("🔢 Layer 3: Fibonacci Levels...", end=" ")
        fib_result = calculate_fibonacci_levels(symbol, interval, limit)
        if fib_result and fib_result.get('available'):
            results['layers']['fibonacci'] = fib_result
            score = fib_result.get('score', 50)
            weighted_sum += score * LAYER_WEIGHTS['fibonacci']
            total_weight += LAYER_WEIGHTS['fibonacci']
            results['available_layers'] += 1
            print(f"✅ Score: {score:.1f}")
        else:
            print("⚠️ Unavailable")
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
    
    # ========================================================================
    # LAYER 4: MARKOV REGIME
    # ========================================================================
    try:
        print("🎲 Layer 4: Markov Regime...", end=" ")
        markov_result = calculate_markov_regime(symbol, interval, limit)
        if markov_result and markov_result.get('available'):
            results['layers']['markov_regime'] = markov_result
            score = markov_result.get('score', 50)
            weighted_sum += score * LAYER_WEIGHTS['markov_regime']
            total_weight += LAYER_WEIGHTS['markov_regime']
            results['available_layers'] += 1
            print(f"✅ Score: {score:.1f}")
        else:
            print("⚠️ Unavailable")
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
    
    # ========================================================================
    # LAYER 5: VOLUME PROFILE
    # ========================================================================
    try:
        print("📊 Layer 5: Volume Profile...", end=" ")
        vol_result = calculate_volume_profile(symbol, interval, limit)
        if vol_result and vol_result.get('available'):
            results['layers']['volume_profile'] = vol_result
            score = vol_result.get('score', 50)
            weighted_sum += score * LAYER_WEIGHTS['volume_profile']
            total_weight += LAYER_WEIGHTS['volume_profile']
            results['available_layers'] += 1
            print(f"✅ Score: {score:.1f}")
        else:
            print("⚠️ Unavailable")
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
    
    # ========================================================================
    # LAYER 6: VWAP DEVIATION
    # ========================================================================
    try:
        print("📈 Layer 6: VWAP Deviation...", end=" ")
        vwap_result = calculate_vwap_deviation(symbol, interval, limit)
        if vwap_result and vwap_result.get('available'):
            results['layers']['vwap'] = vwap_result
            score = vwap_result.get('score', 50)
            weighted_sum += score * LAYER_WEIGHTS['vwap']
            total_weight += LAYER_WEIGHTS['vwap']
            results['available_layers'] += 1
            print(f"✅ Score: {score:.1f}")
        else:
            print("⚠️ Unavailable")
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
    
    # ========================================================================
    # LAYER 7: PIVOT POINTS
    # ========================================================================
    try:
        print("🎯 Layer 7: Pivot Points...", end=" ")
        pivot_result = calculate_pivot_points(symbol, interval, limit)
        if pivot_result and pivot_result.get('available'):
            results['layers']['pivot_points'] = pivot_result
            score = pivot_result.get('score', 50)
            weighted_sum += score * LAYER_WEIGHTS['pivot_points']
            total_weight += LAYER_WEIGHTS['pivot_points']
            results['available_layers'] += 1
            print(f"✅ Score: {score:.1f}")
        else:
            print("⚠️ Unavailable")
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
    
    # ========================================================================
    # LAYER 8: VOLATILITY SQUEEZE
    # ========================================================================
    try:
        print("💥 Layer 8: Volatility Squeeze...", end=" ")
        squeeze_result = calculate_volatility_squeeze(symbol, interval, limit)
        if squeeze_result and squeeze_result.get('available'):
            results['layers']['volatility_squeeze'] = squeeze_result
            score = squeeze_result.get('score', 50)
            weighted_sum += score * LAYER_WEIGHTS['volatility_squeeze']
            total_weight += LAYER_WEIGHTS['volatility_squeeze']
            results['available_layers'] += 1
            print(f"✅ Score: {score:.1f}")
        else:
            print("⚠️ Unavailable")
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
    
    # ========================================================================
    # LAYER 9: GOLD CORRELATION ⭐ NEW (Phase 6.2)
    # ========================================================================
    if GOLD_AVAILABLE:
        try:
            print("🥇 Layer 9: Gold Correlation...", end=" ")
            gold_result = calculate_gold_correlation(symbol, interval, limit)
            if gold_result and gold_result.get('available'):
                results['layers']['gold_correlation'] = gold_result
                score = gold_result.get('score', 50)
                weighted_sum += score * LAYER_WEIGHTS['gold_correlation']
                total_weight += LAYER_WEIGHTS['gold_correlation']
                results['available_layers'] += 1
                print(f"✅ Score: {score:.1f}")
            else:
                print("⚠️ Unavailable")
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}")
    else:
        print("🥇 Layer 9: Gold Correlation... ⏭️ Skipped (not installed)")
    
    # ========================================================================
    # LAYER 10: BTC DOMINANCE & FLOW ⭐ NEW (Phase 6.3)
    # ========================================================================
    if DOMINANCE_AVAILABLE:
        try:
            print("📊 Layer 10: BTC Dominance Flow...", end=" ")
            dom_result = calculate_dominance_flow()
            if dom_result and dom_result.get('available'):
                results['layers']['dominance_flow'] = dom_result
                score = dom_result.get('score', 50)
                weighted_sum += score * LAYER_WEIGHTS['dominance_flow']
                total_weight += LAYER_WEIGHTS['dominance_flow']
                results['available_layers'] += 1
                print(f"✅ Score: {score:.1f}")
            else:
                print("⚠️ Unavailable")
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}")
    else:
        print("📊 Layer 10: BTC Dominance Flow... ⏭️ Skipped (not installed)")
    
    # ========================================================================
    # LAYER 11: CROSS-ASSET CORRELATION ⭐ NEW (Phase 6.4)
    # ========================================================================
    if CROSS_ASSET_AVAILABLE:
        try:
            print("🔗 Layer 11: Cross-Asset Correlation...", end=" ")
            cross_result = calculate_cross_asset(interval, limit)
            if cross_result and cross_result.get('available'):
                results['layers']['cross_asset'] = cross_result
                score = cross_result.get('score', 50)
                weighted_sum += score * LAYER_WEIGHTS['cross_asset']
                total_weight += LAYER_WEIGHTS['cross_asset']
                results['available_layers'] += 1
                print(f"✅ Score: {score:.1f}")
            else:
                print("⚠️ Unavailable")
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}")
    else:
        print("🔗 Layer 11: Cross-Asset Correlation... ⏭️ Skipped (not installed)")
    
    # ========================================================================
    # CALCULATE FINAL SCORE
    # ========================================================================
    if total_weight > 0:
        results['weighted_score'] = round(weighted_sum / total_weight, 2)
        results['final_score'] = results['weighted_score']
    else:
        results['final_score'] = 50.0
        results['weighted_score'] = 50.0
    
    # Calculate confidence based on available layers
    results['confidence'] = round((results['available_layers'] / results['total_layers']) * 100, 1)
    
    # ========================================================================
    # GENERATE INTERPRETATION & RECOMMENDATION
    # ========================================================================
    score = results['final_score']
    
    if score >= 75:
        results['interpretation'] = "🟢 STRONG BULLISH - Multiple layers confirm upside momentum"
        results['recommendation'] = "BUY"
    elif score >= 65:
        results['interpretation'] = "🟢 BULLISH - Favorable conditions for long positions"
        results['recommendation'] = "BUY"
    elif score >= 55:
        results['interpretation'] = "🟢 MODERATELY BULLISH - Slight bullish bias"
        results['recommendation'] = "BUY / HOLD"
    elif score >= 45:
        results['interpretation'] = "🟡 NEUTRAL - Mixed signals, no clear direction"
        results['recommendation'] = "HOLD"
    elif score >= 35:
        results['interpretation'] = "🔴 MODERATELY BEARISH - Caution advised"
        results['recommendation'] = "HOLD / SELL"
    elif score >= 25:
        results['interpretation'] = "🔴 BEARISH - Unfavorable conditions"
        results['recommendation'] = "SELL"
    else:
        results['interpretation'] = "🔴 STRONG BEARISH - Multiple layers show downside risk"
        results['recommendation'] = "SELL"
    
    # ========================================================================
    # PRINT SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print(f"🎯 FINAL SCORE: {results['final_score']:.2f}/100")
    print(f"📊 Confidence: {results['confidence']:.1f}% ({results['available_layers']}/{results['total_layers']} layers)")
    print(f"📖 {results['interpretation']}")
    print(f"💡 RECOMMENDATION: {results['recommendation']}")
    if results['phase_6_enabled']:
        print("✅ Phase 6 Macro Analysis: ACTIVE")
    else:
        print("⚠️ Phase 6 Macro Analysis: PARTIAL (install missing layers)")
    print("=" * 70)
    
    return results

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_layer_summary(results):
    """Get a quick summary of all layer scores"""
    summary = []
    for layer_name, layer_data in results['layers'].items():
        score = layer_data.get('score', 50)
        summary.append({
            'layer': layer_name,
            'score': score,
            'weight': LAYER_WEIGHTS.get(layer_name, 0) * 100
        })
    return sorted(summary, key=lambda x: x['score'], reverse=True)

def get_strongest_signals(results, top_n=3):
    """Get the strongest bullish/bearish signals"""
    layer_scores = []
    for layer_name, layer_data in results['layers'].items():
        score = layer_data.get('score', 50)
        layer_scores.append((layer_name, score))
    
    sorted_scores = sorted(layer_scores, key=lambda x: x[1], reverse=True)
    
    return {
        'most_bullish': sorted_scores[:top_n],
        'most_bearish': sorted_scores[-top_n:][::-1]
    }

# ============================================================================
# TEST EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("🚀 AI BRAIN - 11-LAYER ANALYSIS ENGINE")
    print("Phase 6 Complete: Macro & Cross-Asset Analysis")
    print()
    
    # Run analysis
    result = calculate_all_layers('BTCUSDT', '1h', 500)
    
    # Print layer summary
    print("\n📊 LAYER BREAKDOWN:")
    summary = get_layer_summary(result)
    for item in summary:
        print(f"  • {item['layer']}: {item['score']:.1f} (weight: {item['weight']:.0f}%)")
    
    # Print strongest signals
    print("\n🎯 STRONGEST SIGNALS:")
    signals = get_strongest_signals(result)
    print("  BULLISH:")
    for layer, score in signals['most_bullish']:
        print(f"    • {layer}: {score:.1f}")
    print("  BEARISH:")
    for layer, score in signals['most_bearish']:
        print(f"    • {layer}: {score:.1f}")
