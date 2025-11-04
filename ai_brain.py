# ai_brain.py v14.0 - QUANTUM MATHEMATICS INTEGRATION
"""
🧠 DEMIR AI TRADING BOT - AI Brain v14.0
================================================================
Versiyon: 14.0 - QUANTUM MATHEMATICS PHASE 7
Tarih: 4 Kasım 2025, 09:25 CET

✅ PHASE 7 ENTEGRE EDİLDİ!
✅ 5 Quantum Layer eklendi:
   - Black-Scholes Option Pricing
   - Kalman Regime Detection
   - Fractal Chaos Analysis
   - Fourier Cycle Detection
   - Copula Correlation

✅ Toplam 17 Layer aktif
✅ Weighted Ensemble Scoring
✅ Confidence göstergesi
"""

import os
import sys
import traceback
from datetime import datetime
import requests

# ============================================================================
# LAYER AĞIRLIKLARI (WEIGHTED ENSEMBLE) - v14.0 UPDATED
# ============================================================================

LAYER_WEIGHTS = {
    # Phase 1-6 Layers (70 puan)
    'strategy': 15,          # Reduced from 20
    'news': 8,               # Reduced from 10
    'macro': 6,              # Reduced from 8
    'gold': 4,               # Reduced from 5
    'dominance': 5,          # Reduced from 7
    'cross_asset': 8,        # Reduced from 10
    'vix': 5,                # Reduced from 6
    'rates': 5,              # Reduced from 6
    'trad_markets': 6,       # Reduced from 8
    'monte_carlo': 8,        # Reduced from 10
    'kelly': 8,              # Reduced from 10

    # Phase 7 Quantum Layers (30 puan) - NEW!
    'black_scholes': 8,      # Option pricing + Greeks
    'kalman': 7,             # Regime detection
    'fractal': 6,            # Hurst + chaos
    'fourier': 5,            # Cycle analysis
    'copula': 4              # Tail dependencies
}

TOTAL_WEIGHT = sum(LAYER_WEIGHTS.values())

print(f"🔱 AI Brain v14.0: Total Layer Weight = {TOTAL_WEIGHT}")

# ============================================================================
# PHASE 1-6 LAYER IMPORTS
# ============================================================================

try:
    from strategy_layer import StrategyEngine
    print("✅ AI Brain v14.0: strategy_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v14.0: strategy_layer hatası: {e}")
    StrategyEngine = None

try:
    from monte_carlo_layer import run_monte_carlo_simulation
    print("✅ AI Brain v14.0: monte_carlo_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v14.0: monte_carlo_layer hatası: {e}")
    run_monte_carlo_simulation = None

try:
    from kelly_enhanced_layer import calculate_dynamic_kelly
    print("✅ AI Brain v14.0: kelly_enhanced_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v14.0: kelly_enhanced_layer hatası: {e}")
    calculate_dynamic_kelly = None

try:
    from macro_correlation_layer import MacroCorrelationLayer
    print("✅ AI Brain v14.0: macro_correlation_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v14.0: macro_correlation_layer hatası: {e}")
    MacroCorrelationLayer = None

try:
    from gold_correlation_layer import calculate_gold_correlation
    print("✅ AI Brain v14.0: gold_correlation_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v14.0: gold_correlation_layer hatası: {e}")
    calculate_gold_correlation = None

try:
    from dominance_flow_layer import calculate_dominance_flow
    print("✅ AI Brain v14.0: dominance_flow_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v14.0: dominance_flow_layer hatası: {e}")
    calculate_dominance_flow = None

try:
    from cross_asset_layer import get_multi_coin_data
    print("✅ AI Brain v14.0: cross_asset_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v14.0: cross_asset_layer hatası: {e}")
    get_multi_coin_data = None

try:
    from vix_layer import get_vix_signal
    print("✅ AI Brain v14.0: vix_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v14.0: vix_layer hatası: {e}")
    get_vix_signal = None

try:
    from interest_rates_layer import get_rates_signal
    print("✅ AI Brain v14.0: interest_rates_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v14.0: interest_rates_layer hatası: {e}")
    get_rates_signal = None

try:
    from traditional_markets_layer import get_traditional_markets_signal
    print("✅ AI Brain v14.0: traditional_markets_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v14.0: traditional_markets_layer hatası: {e}")
    get_traditional_markets_signal = None

try:
    from news_sentiment_layer import get_news_sentiment
    print("✅ AI Brain v14.0: news_sentiment_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v14.0: news_sentiment_layer hatası: {e}")
    get_news_sentiment = None

# ============================================================================
# PHASE 7 QUANTUM LAYER IMPORTS - NEW!
# ============================================================================

try:
    from quantum_black_scholes_layer import get_quantum_black_scholes_signal
    print("✅ AI Brain v14.0: 🔮 quantum_black_scholes_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v14.0: quantum_black_scholes_layer hatası: {e}")
    get_quantum_black_scholes_signal = None

try:
    from kalman_regime_layer import get_kalman_regime_signal
    print("✅ AI Brain v14.0: 🔮 kalman_regime_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v14.0: kalman_regime_layer hatası: {e}")
    get_kalman_regime_signal = None

try:
    from fractal_chaos_layer import get_fractal_chaos_signal
    print("✅ AI Brain v14.0: 🔮 fractal_chaos_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v14.0: fractal_chaos_layer hatası: {e}")
    get_fractal_chaos_signal = None

try:
    from fourier_cycle_layer import get_fourier_cycle_signal
    print("✅ AI Brain v14.0: 🔮 fourier_cycle_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v14.0: fourier_cycle_layer hatası: {e}")
    get_fourier_cycle_signal = None

try:
    from copula_correlation_layer import get_copula_correlation_signal
    print("✅ AI Brain v14.0: 🔮 copula_correlation_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v14.0: copula_correlation_layer hatası: {e}")
    get_copula_correlation_signal = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_signal_text(score):
    """
    Convert score to text signal
    ✅ FIX v15.0: Handle None values to prevent TypeError
    """
    # ✅ Check for None or invalid values FIRST
    if score is None or score == 0:
        return "NO DATA"

    try:
        score = float(score)
    except (ValueError, TypeError):
        return "INVALID"

    # Now safe to compare
    if score >= 65:
        return "LONG"
    elif score <= 35:
        return "SHORT"
    else:
        return "NEUTRAL"


def calculate_confidence(scores_dict):
    """
    Confidence hesapla (layer agreement)

    Yüksek confidence = Layer'lar aynı yönde
    Düşük confidence = Layer'lar karışık
    """
    scores = [s for s in scores_dict.values() if s is not None]

    if len(scores) < 3:
        return 0.3  # Düşük confidence

    # Standard deviation (düşük = yüksek agreement)
    std = sum((s - 50)**2 for s in scores) / len(scores)
    std = std ** 0.5

    # Confidence: 0-1 (düşük std = yüksek confidence)
    confidence = max(0, min(1, 1 - (std / 50)))

    return confidence


# ============================================================================
# AI BRAIN MASTER FUNCTION v14.0
# ============================================================================

def analyze_with_ai(symbol, interval='1h'):
    """
    🧠 AI Brain v14.0 - QUANTUM MATHEMATICS

    17-Layer Weighted Ensemble Analysis

    Phase 1-6: 11 Layers (70% weight)
    Phase 7: 5 Quantum Layers (30% weight)

    Args:
        symbol (str): Trading pair (BTCUSDT, ETHUSDT etc.)
        interval (str): Timeframe (1h, 4h, 1d)

    Returns:
        dict: {
            'final_score': 0-100,
            'signal': 'LONG'/'SHORT'/'NEUTRAL',
            'confidence': 0-1,
            'layers': {...},
            'version': '14.0'
        }
    """
    print(f"\n{'='*80}")
    print(f"🧠 AI BRAIN v14.0 - QUANTUM ANALYSIS")
    print(f"Symbol: {symbol} | Interval: {interval}")
    print(f"{'='*80}\n")

    layer_scores = {}
    weighted_sum = 0.0
    active_weight = 0.0

    # ========================================================================
    # PHASE 1-6 LAYERS (11 Layers)
    # ========================================================================

    # 1. Strategy Layer
    if StrategyEngine is not None:
        try:
            engine = StrategyEngine()
            score = engine.get_strategy_signal(symbol, interval)
            layer_scores['strategy'] = score
            weighted_sum += score * LAYER_WEIGHTS['strategy']
            active_weight += LAYER_WEIGHTS['strategy']
            print(f"✅ Strategy: {score:.1f}/100 (weight: {LAYER_WEIGHTS['strategy']})")
        except Exception as e:
            print(f"⚠️ Strategy error: {e}")
            layer_scores['strategy'] = None

    # 2. Monte Carlo
    if run_monte_carlo_simulation is not None:
        try:
            result = run_monte_carlo_simulation(symbol, interval)
            if result and 'score' in result:
                score = result['score']
                layer_scores['monte_carlo'] = score
                weighted_sum += score * LAYER_WEIGHTS['monte_carlo']
                active_weight += LAYER_WEIGHTS['monte_carlo']
                print(f"✅ Monte Carlo: {score:.1f}/100 (weight: {LAYER_WEIGHTS['monte_carlo']})")
        except Exception as e:
            print(f"⚠️ Monte Carlo error: {e}")
            layer_scores['monte_carlo'] = None

    # 3. Kelly Criterion
    if calculate_dynamic_kelly is not None:
        try:
            kelly_result = calculate_dynamic_kelly(symbol)
            if kelly_result and 'score' in kelly_result:
                score = kelly_result['score']
                layer_scores['kelly'] = score
                weighted_sum += score * LAYER_WEIGHTS['kelly']
                active_weight += LAYER_WEIGHTS['kelly']
                print(f"✅ Kelly: {score:.1f}/100 (weight: {LAYER_WEIGHTS['kelly']})")
        except Exception as e:
            print(f"⚠️ Kelly error: {e}")
            layer_scores['kelly'] = None

    # 4. Macro Correlation
    if MacroCorrelationLayer is not None:
        try:
            macro_layer = MacroCorrelationLayer()
            result = macro_layer.analyze_all()
            if result and 'signal' in result:
                score = result['signal']
                layer_scores['macro'] = score
                weighted_sum += score * LAYER_WEIGHTS['macro']
                active_weight += LAYER_WEIGHTS['macro']
                print(f"✅ Macro: {score:.1f}/100 (weight: {LAYER_WEIGHTS['macro']})")
        except Exception as e:
            print(f"⚠️ Macro error: {e}")
            layer_scores['macro'] = None

    # 5. Gold Correlation
    if calculate_gold_correlation is not None:
        try:
            score = calculate_gold_correlation(symbol)
            if score is not None:
                layer_scores['gold'] = score
                weighted_sum += score * LAYER_WEIGHTS['gold']
                active_weight += LAYER_WEIGHTS['gold']
                print(f"✅ Gold: {score:.1f}/100 (weight: {LAYER_WEIGHTS['gold']})")
        except Exception as e:
            print(f"⚠️ Gold error: {e}")
            layer_scores['gold'] = None

    # 6. Dominance Flow
    if calculate_dominance_flow is not None:
        try:
            score = calculate_dominance_flow(symbol)
            if score is not None:
                layer_scores['dominance'] = score
                weighted_sum += score * LAYER_WEIGHTS['dominance']
                active_weight += LAYER_WEIGHTS['dominance']
                print(f"✅ Dominance: {score:.1f}/100 (weight: {LAYER_WEIGHTS['dominance']})")
        except Exception as e:
            print(f"⚠️ Dominance error: {e}")
            layer_scores['dominance'] = None

    # 7. Cross Asset
    if get_multi_coin_data is not None:
        try:
            result = get_multi_coin_data(symbol)
            if result and 'score' in result:
                score = result['score']
                layer_scores['cross_asset'] = score
                weighted_sum += score * LAYER_WEIGHTS['cross_asset']
                active_weight += LAYER_WEIGHTS['cross_asset']
                print(f"✅ Cross Asset: {score:.1f}/100 (weight: {LAYER_WEIGHTS['cross_asset']})")
        except Exception as e:
            print(f"⚠️ Cross Asset error: {e}")
            layer_scores['cross_asset'] = None

    # 8. VIX
    if get_vix_signal is not None:
        try:
            score = get_vix_signal(symbol)
            if score is not None:
                layer_scores['vix'] = score
                weighted_sum += score * LAYER_WEIGHTS['vix']
                active_weight += LAYER_WEIGHTS['vix']
                print(f"✅ VIX: {score:.1f}/100 (weight: {LAYER_WEIGHTS['vix']})")
        except Exception as e:
            print(f"⚠️ VIX error: {e}")
            layer_scores['vix'] = None

    # 9. Interest Rates
    if get_rates_signal is not None:
        try:
            score = get_rates_signal()
            if score is not None:
                layer_scores['rates'] = score
                weighted_sum += score * LAYER_WEIGHTS['rates']
                active_weight += LAYER_WEIGHTS['rates']
                print(f"✅ Rates: {score:.1f}/100 (weight: {LAYER_WEIGHTS['rates']})")
        except Exception as e:
            print(f"⚠️ Rates error: {e}")
            layer_scores['rates'] = None

    # 10. Traditional Markets
    if get_traditional_markets_signal is not None:
        try:
            score = get_traditional_markets_signal()
            if score is not None:
                layer_scores['trad_markets'] = score
                weighted_sum += score * LAYER_WEIGHTS['trad_markets']
                active_weight += LAYER_WEIGHTS['trad_markets']
                print(f"✅ Traditional Markets: {score:.1f}/100 (weight: {LAYER_WEIGHTS['trad_markets']})")
        except Exception as e:
            print(f"⚠️ Traditional Markets error: {e}")
            layer_scores['trad_markets'] = None

    # 11. News Sentiment
    if get_news_sentiment is not None:
        try:
            score = get_news_sentiment(symbol)
            if score is not None:
                layer_scores['news'] = score
                weighted_sum += score * LAYER_WEIGHTS['news']
                active_weight += LAYER_WEIGHTS['news']
                print(f"✅ News: {score:.1f}/100 (weight: {LAYER_WEIGHTS['news']})")
        except Exception as e:
            print(f"⚠️ News error: {e}")
            layer_scores['news'] = None

    # ========================================================================
    # PHASE 7 QUANTUM LAYERS (5 Layers) - NEW!
    # ========================================================================

    print(f"\n{'='*80}")
    print(f"🔮 QUANTUM MATHEMATICS LAYERS")
    print(f"{'='*80}\n")

    # 12. Black-Scholes
    if get_quantum_black_scholes_signal is not None:
        try:
            score = get_quantum_black_scholes_signal(symbol, interval)
            if score is not None:
                layer_scores['black_scholes'] = score
                weighted_sum += score * LAYER_WEIGHTS['black_scholes']
                active_weight += LAYER_WEIGHTS['black_scholes']
                print(f"✅ Black-Scholes: {score:.1f}/100 (weight: {LAYER_WEIGHTS['black_scholes']})")
        except Exception as e:
            print(f"⚠️ Black-Scholes error: {e}")
            layer_scores['black_scholes'] = None

    # 13. Kalman Regime
    if get_kalman_regime_signal is not None:
        try:
            score = get_kalman_regime_signal(symbol, interval)
            if score is not None:
                layer_scores['kalman'] = score
                weighted_sum += score * LAYER_WEIGHTS['kalman']
                active_weight += LAYER_WEIGHTS['kalman']
                print(f"✅ Kalman: {score:.1f}/100 (weight: {LAYER_WEIGHTS['kalman']})")
        except Exception as e:
            print(f"⚠️ Kalman error: {e}")
            layer_scores['kalman'] = None

    # 14. Fractal Chaos
    if get_fractal_chaos_signal is not None:
        try:
            score = get_fractal_chaos_signal(symbol, interval)
            if score is not None:
                layer_scores['fractal'] = score
                weighted_sum += score * LAYER_WEIGHTS['fractal']
                active_weight += LAYER_WEIGHTS['fractal']
                print(f"✅ Fractal: {score:.1f}/100 (weight: {LAYER_WEIGHTS['fractal']})")
        except Exception as e:
            print(f"⚠️ Fractal error: {e}")
            layer_scores['fractal'] = None

    # 15. Fourier Cycle
    if get_fourier_cycle_signal is not None:
        try:
            score = get_fourier_cycle_signal(symbol, interval)
            if score is not None:
                layer_scores['fourier'] = score
                weighted_sum += score * LAYER_WEIGHTS['fourier']
                active_weight += LAYER_WEIGHTS['fourier']
                print(f"✅ Fourier: {score:.1f}/100 (weight: {LAYER_WEIGHTS['fourier']})")
        except Exception as e:
            print(f"⚠️ Fourier error: {e}")
            layer_scores['fourier'] = None

    # 16. Copula Correlation
    if get_copula_correlation_signal is not None:
        try:
            score = get_copula_correlation_signal(symbol, interval)
            if score is not None:
                layer_scores['copula'] = score
                weighted_sum += score * LAYER_WEIGHTS['copula']
                active_weight += LAYER_WEIGHTS['copula']
                print(f"✅ Copula: {score:.1f}/100 (weight: {LAYER_WEIGHTS['copula']})")
        except Exception as e:
            print(f"⚠️ Copula error: {e}")
            layer_scores['copula'] = None

    # ========================================================================
    # FINAL SCORE CALCULATION
    # ========================================================================

    if active_weight == 0:
        final_score = 50.0  # Neutral if no layers active
        confidence = 0.0
    else:
        final_score = weighted_sum / active_weight
        confidence = calculate_confidence(layer_scores)

    signal = get_signal_text(final_score)

    active_layers = sum(1 for s in layer_scores.values() if s is not None)

    print(f"\n{'='*80}")
    print(f"🎯 FINAL RESULTS")
    print(f"{'='*80}")
    print(f"Active Layers: {active_layers}/17")
    print(f"Final Score: {final_score:.1f}/100")
    print(f"Signal: {signal}")
    print(f"Confidence: {confidence:.1%}")
    print(f"{'='*80}\n")

    return {
        'final_score': final_score,
        'signal': signal,
        'confidence': confidence,
        'layers': layer_scores,
        'active_layers': active_layers,
        'total_layers': 17,
        'version': '14.0',
        'phase': 'Phase 7 - Quantum Mathematics'
    }


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("🧠 AI BRAIN v14.0 TEST - QUANTUM MATHEMATICS")
    print("="*80)

    test_symbols = ['BTCUSDT', 'ETHUSDT']

    for symbol in test_symbols:
        result = analyze_with_ai(symbol, interval='1h')

        print(f"\n📊 {symbol} Results:")
        print(f"   Score: {result['final_score']:.1f}/100")
        print(f"   Signal: {result['signal']}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Active Layers: {result['active_layers']}/{result['total_layers']}")
        print("-"*80)
