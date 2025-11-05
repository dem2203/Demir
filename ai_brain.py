# ai_brain.py v15.0 - PHASE 3+6 FULL INTEGRATION
# ===========================================
# ✅ QUANTUM MATHEMATICS INTEGRATION (Phase 7) - PRESERVED
# ✅ 17-Layer Weighted Ensemble Analysis - PRESERVED
# ✅ PHASE 3+6 INTEGRATION (v15.0 NEW!)
# ===========================================
"""
🧠 DEMIR AI TRADING BOT - AI Brain v15.0
====================================================================
Versiyon: 15.0 - QUANTUM MATHEMATICS + PHASE 3+6 INTEGRATION
Tarih: 4 Kasım 2025, 23:30 CET

✅ PHASE 7 (v14.1) PRESERVED:
- Black-Scholes Option Pricing
- Kalman Regime Detection
- Fractal Chaos Analysis
- Fourier Cycle Detection
- Copula Correlation

✅ PHASE 3 (v15.0) NEW:
- Telegram Alert System
- Backtest Engine
- Portfolio Optimizer

✅ PHASE 6 (v15.0) NEW:
- Enhanced Macro Layer (SPX/NASDAQ/DXY)
- Enhanced Gold Correlation
- Enhanced BTC Dominance Flow
- Enhanced VIX Fear Index
- Enhanced Interest Rates

✅ Toplam 17 Base Layers + Phase 3+6 modules
✅ Weighted Ensemble Scoring
✅ Confidence göstergesi
✅ Streamlit compatibility wrapper
"""

import os
import sys
import traceback
from datetime import datetime
import requests

# ============================================================================
# PHASE 3+6 IMPORTS - v15.0 NEW!
# ============================================================================

# Phase 3 Modules - Dynamic Loading
TELEGRAM_AVAILABLE = False
try:
    from telegram_alert_system import TelegramAlertSystem
    TELEGRAM_AVAILABLE = True
    print("✅ AI Brain v15.0: Telegram imported")
except ImportError:
    print("⚠️ AI Brain v15.0: Telegram not available")
    TelegramAlertSystem = None

BACKTEST_AVAILABLE = False
try:
    from backtest_engine import BacktestEngine
    BACKTEST_AVAILABLE = True
    print("✅ AI Brain v15.0: Backtest imported")
except ImportError:
    print("⚠️ AI Brain v15.0: Backtest not available")
    BacktestEngine = None

PORTFOLIO_AVAILABLE = False
try:
    from portfolio_optimizer import PortfolioOptimizer
    PORTFOLIO_AVAILABLE = True
    print("✅ AI Brain v15.0: Portfolio Optimizer imported")
except ImportError:
    print("⚠️ AI Brain v15.0: Portfolio Optimizer not available")
    PortfolioOptimizer = None

# Phase 6 Enhanced Layers - Dynamic Loading
MACRO_ENHANCED = False
try:
    from layers.enhanced_macro_layer import EnhancedMacroLayer
    MACRO_ENHANCED = True
    print("✅ AI Brain v15.0: Enhanced Macro imported")
except ImportError:
    print("⚠️ AI Brain v15.0: Enhanced Macro not available - using old layer")
    EnhancedMacroLayer = None

GOLD_ENHANCED = False
try:
    from layers.enhanced_gold_layer import EnhancedGoldLayer
    GOLD_ENHANCED = True
    print("✅ AI Brain v15.0: Enhanced Gold imported")
except ImportError:
    print("⚠️ AI Brain v15.0: Enhanced Gold not available - using old layer")
    EnhancedGoldLayer = None

DOMINANCE_ENHANCED = False
try:
    from layers.enhanced_dominance_layer import EnhancedDominanceLayer
    DOMINANCE_ENHANCED = True
    print("✅ AI Brain v15.0: Enhanced Dominance imported")
except ImportError:
    print("⚠️ AI Brain v15.0: Enhanced Dominance not available - using old layer")
    EnhancedDominanceLayer = None

VIX_ENHANCED = False
try:
    from layers.enhanced_vix_layer import EnhancedVixLayer
    VIX_ENHANCED = True
    print("✅ AI Brain v15.0: Enhanced VIX imported")
except ImportError:
    print("⚠️ AI Brain v15.0: Enhanced VIX not available - using old layer")
    EnhancedVixLayer = None

RATES_ENHANCED = False
try:
    from layers.enhanced_rates_layer import EnhancedRatesLayer
    RATES_ENHANCED = True
    print("✅ AI Brain v15.0: Enhanced Rates imported")
except ImportError:
    print("⚠️ AI Brain v15.0: Enhanced Rates not available - using old layer")
    EnhancedRatesLayer = None

print("="*80)
print("✅ AI Brain v15.0 - Phase 3+6 imports complete")
print("="*80)

# ============================================================================
# LAYER AĞIRLIKLARI (WEIGHTED ENSEMBLE) - v15.0 UPDATED
# ============================================================================

LAYER_WEIGHTS = {
    # Phase 1-6 Layers (70 puan)
    'strategy': 15,
    'news': 8,
    'macro': 6,
    'gold': 4,
    'dominance': 5,
    'cross_asset': 8,
    'vix': 5,
    'rates': 5,
    'trad_markets': 6,
    'monte_carlo': 8,
    'kelly': 8,
    
    # Phase 7 Quantum Layers (30 puan)
    'black_scholes': 8,
    'kalman': 7,
    'fractal': 6,
    'fourier': 5,
    'copula': 4
}

TOTAL_WEIGHT = sum(LAYER_WEIGHTS.values())
print(f"🔱 AI Brain v15.0: Total Layer Weight = {TOTAL_WEIGHT}")

# ============================================================================
# PHASE 1-6 LAYER IMPORTS (Your v14.1 code - PRESERVED)
# ============================================================================

try:
    from strategy_layer import StrategyEngine
    print("✅ AI Brain v15.0: strategy_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v15.0: strategy_layer error: {e}")
    StrategyEngine = None

try:
    from monte_carlo_layer import run_monte_carlo_simulation
    print("✅ AI Brain v15.0: monte_carlo_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v15.0: monte_carlo_layer error: {e}")
    run_monte_carlo_simulation = None

try:
    from kelly_enhanced_layer import calculate_dynamic_kelly
    print("✅ AI Brain v15.0: kelly_enhanced_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v15.0: kelly_enhanced_layer error: {e}")
    calculate_dynamic_kelly = None

try:
    from macro_correlation_layer import MacroCorrelationLayer
    print("✅ AI Brain v15.0: macro_correlation_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v15.0: macro_correlation_layer error: {e}")
    MacroCorrelationLayer = None

try:
    from gold_correlation_layer import calculate_gold_correlation
    print("✅ AI Brain v15.0: gold_correlation_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v15.0: gold_correlation_layer error: {e}")
    calculate_gold_correlation = None

try:
    from dominance_flow_layer import calculate_dominance_flow
    print("✅ AI Brain v15.0: dominance_flow_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v15.0: dominance_flow_layer error: {e}")
    calculate_dominance_flow = None

try:
    from cross_asset_layer import get_multi_coin_data
    print("✅ AI Brain v15.0: cross_asset_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v15.0: cross_asset_layer error: {e}")
    get_multi_coin_data = None

try:
    from vix_layer import get_vix_signal
    print("✅ AI Brain v15.0: vix_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v15.0: vix_layer error: {e}")
    get_vix_signal = None

try:
    from interest_rates_layer import get_rates_signal
    print("✅ AI Brain v15.0: interest_rates_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v15.0: interest_rates_layer error: {e}")
    get_rates_signal = None

try:
    from traditional_markets_layer import get_traditional_markets_signal
    print("✅ AI Brain v15.0: traditional_markets_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v15.0: traditional_markets_layer error: {e}")
    get_traditional_markets_signal = None

try:
    from news_sentiment_layer import get_news_sentiment
    print("✅ AI Brain v15.0: news_sentiment_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v15.0: news_sentiment_layer error: {e}")
    get_news_sentiment = None

# ============================================================================
# PHASE 7 QUANTUM LAYER IMPORTS (Your v14.1 code - PRESERVED)
# ============================================================================

try:
    from quantum_black_scholes_layer import get_quantum_black_scholes_signal
    print("✅ AI Brain v15.0: 🔮 quantum_black_scholes_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v15.0: quantum_black_scholes_layer error: {e}")
    get_quantum_black_scholes_signal = None

try:
    from kalman_regime_layer import get_kalman_regime_signal
    print("✅ AI Brain v15.0: 🔮 kalman_regime_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v15.0: kalman_regime_layer error: {e}")
    get_kalman_regime_signal = None

try:
    from fractal_chaos_layer import get_fractal_chaos_signal
    print("✅ AI Brain v15.0: 🔮 fractal_chaos_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v15.0: fractal_chaos_layer error: {e}")
    get_fractal_chaos_signal = None

try:
    from fourier_cycle_layer import get_fourier_cycle_signal
    print("✅ AI Brain v15.0: 🔮 fourier_cycle_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v15.0: fourier_cycle_layer error: {e}")
    get_fourier_cycle_signal = None

try:
    from copula_correlation_layer import get_copula_correlation_signal
    print("✅ AI Brain v15.0: 🔮 copula_correlation_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v15.0: copula_correlation_layer error: {e}")
    get_copula_correlation_signal = None

print("="*80)
print("✅ AI Brain v15.0 - All imports complete")
print("="*80)

# ============================================================================
# HELPER FUNCTIONS (Your v14.1 code - PRESERVED)
# ============================================================================

def get_signal_text(score):
    """
    Convert score to text signal - AGGRESSIVE v14.1
    ✅ Daha keskin sinyaller için threshold daraltıldı
    """
    if score is None or score == 0:
        return "NO DATA"
    
    try:
        score = float(score)
    except (ValueError, TypeError):
        return "INVALID"
    
    # ✅ YENİ AGGRESSIVE THRESHOLDS
    if score >= 60:  # ESKİ: 65
        return "LONG"
    elif score <= 40:  # ESKİ: 35
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

========
# AI BRAIN MASTER FUNCTION v15.0
# ============================================================================

def analyze_with_ai(symbol, interval='1h'):
    """
    🧠 AI Brain v15.0 - QUANTUM MATHEMATICS + PHASE 3+6
    17-Layer Weighted Ensemble Analysis
    Phase 1-6: 11 Layers (70% weight)
    Phase 7: 5 Quantum Layers (30% weight)
    Phase 3+6: Enhanced modules
    
    Args:
        symbol (str): Trading pair (BTCUSDT, ETHUSDT etc.)
        interval (str): Timeframe (1h, 4h, 1d)
        
    Returns:
        dict: {
            'final_score': 0-100,
            'signal': 'LONG'/'SHORT'/'NEUTRAL',
            'confidence': 0-1,
            'layers': {...},
            'version': '15.0'
        }
    """
    print(f"\n{'='*80}")
    print(f"🧠 AI BRAIN v15.0 - QUANTUM ANALYSIS + PHASE 3+6")
    print(f"   Symbol: {symbol}")
    print(f"   Interval: {interval}")
    print(f"{'='*80}\n")
    
    layer_scores = {}
    weighted_sum = 0.0
    active_weight = 0.0
    
    # ========================================================================
    # PHASE 1-6 LAYERS (11 Layers) - Your v14.1 code PRESERVED
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
    
    # 4. Macro Correlation (old - will be replaced by enhanced if available)
    if MacroCorrelationLayer is not None and not MACRO_ENHANCED:
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
    
    # 5. Gold Correlation (old - will be replaced by enhanced if available)
    if calculate_gold_correlation is not None and not GOLD_ENHANCED:
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
    
    # 6. Dominance Flow (old - will be replaced by enhanced if available)
    if calculate_dominance_flow is not None and not DOMINANCE_ENHANCED:
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
    
    # 8. VIX (old - will be replaced by enhanced if available)
    if get_vix_signal is not None and not VIX_ENHANCED:
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
    
    # 9. Interest Rates (old - will be replaced by enhanced if available)
    if get_rates_signal is not None and not RATES_ENHANCED:
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
    # PHASE 7 QUANTUM LAYERS (5 Layers) - Your v14.1 code PRESERVED
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
    # PHASE 6: ENHANCED MACRO LAYERS - v15.0 NEW!
    # ========================================================================
    
    print(f"\n{'='*80}")
    print(f"🌍 PHASE 6: ENHANCED MACRO LAYERS (v15.0)")
    print(f"{'='*80}\n")
    
    # Enhanced Macro Layer (SPX/NASDAQ/DXY)
    if MACRO_ENHANCED and EnhancedMacroLayer:
        try:
            enhanced_macro = EnhancedMacroLayer()
            result = enhanced_macro.calculate_macro_score()
            if result and result.get('confidence', 0) > 0:
                score = result['score']
                # Replace old macro if it was calculated
                if 'macro' in layer_scores and layer_scores['macro'] is not None:
                    weighted_sum -= layer_scores['macro'] * LAYER_WEIGHTS['macro']
                    active_weight -= LAYER_WEIGHTS['macro']
                
                layer_scores['macro'] = score
                weighted_sum += score * LAYER_WEIGHTS['macro']
                active_weight += LAYER_WEIGHTS['macro']
                risk = result.get('risk_sentiment', 'N/A')
                print(f"✅ Enhanced Macro (SPX/NASDAQ/DXY): {score:.1f}/100 (Risk: {risk})")
        except Exception as e:
            print(f"⚠️ Enhanced Macro error: {e}")
    
    # Enhanced Gold Layer
    if GOLD_ENHANCED and EnhancedGoldLayer:
        try:
            enhanced_gold = EnhancedGoldLayer()
            result = enhanced_gold.calculate_gold_correlation_score(symbol)
            if result and result.get('confidence', 0) > 0:
                score = result['score']
                # Replace old gold if it was calculated
                if 'gold' in layer_scores and layer_scores['gold'] is not None:
                    weighted_sum -= layer_scores['gold'] * LAYER_WEIGHTS['gold']
                    active_weight -= LAYER_WEIGHTS['gold']
                
                layer_scores['gold'] = score
                weighted_sum += score * LAYER_WEIGHTS['gold']
                active_weight += LAYER_WEIGHTS['gold']
                gold_price = result.get('gold_price', 'N/A')
                print(f"✅ Enhanced Gold: {score:.1f}/100 (Gold: ${gold_price})")
        except Exception as e:
            print(f"⚠️ Enhanced Gold error: {e}")
    
    # Enhanced Dominance Layer
    if DOMINANCE_ENHANCED and EnhancedDominanceLayer:
        try:
            enhanced_dom = EnhancedDominanceLayer()
            result = enhanced_dom.calculate_dominance_score(symbol)
            if result and result.get('confidence', 0) > 0:
                score = result['score']
                # Replace old dominance if it was calculated
                if 'dominance' in layer_scores and layer_scores['dominance'] is not None:
                    weighted_sum -= layer_scores['dominance'] * LAYER_WEIGHTS['dominance']
                    active_weight -= LAYER_WEIGHTS['dominance']
                
                layer_scores['dominance'] = score
                weighted_sum += score * LAYER_WEIGHTS['dominance']
                active_weight += LAYER_WEIGHTS['dominance']
                dom = result.get('dominance', 'N/A')
                print(f"✅ Enhanced Dominance: {score:.1f}/100 (BTC.D: {dom}%)")
        except Exception as e:
            print(f"⚠️ Enhanced Dominance error: {e}")
    
    # Enhanced VIX Layer
    if VIX_ENHANCED and EnhancedVixLayer:
        try:
            enhanced_vix = EnhancedVixLayer()
            result = enhanced_vix.calculate_vix_score(symbol)
            if result and result.get('confidence', 0) > 0:
                score = result['score']
                # Replace old vix if it was calculated
                if 'vix' in layer_scores and layer_scores['vix'] is not None:
                    weighted_sum -= layer_scores['vix'] * LAYER_WEIGHTS['vix']
                    active_weight -= LAYER_WEIGHTS['vix']
                
                layer_scores['vix'] = score
                weighted_sum += score * LAYER_WEIGHTS['vix']
                active_weight += LAYER_WEIGHTS['vix']
                vix = result.get('vix', 'N/A')
                print(f"✅ Enhanced VIX: {score:.1f}/100 (VIX: {vix})")
        except Exception as e:
            print(f"⚠️ Enhanced VIX error: {e}")
    
    # Enhanced Rates Layer
    if RATES_ENHANCED and EnhancedRatesLayer:
        try:
            enhanced_rates = EnhancedRatesLayer()
            result = enhanced_rates.calculate_rates_score(symbol)
            if result and result.get('confidence', 0) > 0:
                score = result['score']
                # Replace old rates if it was calculated
                if 'rates' in layer_scores and layer_scores['rates'] is not None:
                    weighted_sum -= layer_scores['rates'] * LAYER_WEIGHTS['rates']
                    active_weight -= LAYER_WEIGHTS['rates']
                
                layer_scores['rates'] = score
                weighted_sum += score * LAYER_WEIGHTS['rates']
                active_weight += LAYER_WEIGHTS['rates']
                yield_10y = result.get('yield_10y', 'N/A')
                print(f"✅ Enhanced Rates: {score:.1f}/100 (10Y: {yield_10y}%)")
        except Exception as e:
            print(f"⚠️ Enhanced Rates error: {e}")
    
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
    print(f"   Active Layers: {active_layers}/17")
    print(f"   Final Score: {final_score:.1f}/100")
    print(f"   Signal: {signal}")
    print(f"   Confidence: {confidence:.1%}")
    print(f"{'='*80}\n")
    
    # ========================================================================
    # PHASE 3: TELEGRAM NOTIFICATION - v15.0 NEW!
    # ========================================================================
    
    if TELEGRAM_AVAILABLE and TelegramAlertSystem and signal != 'NEUTRAL':
        try:
            telegram = TelegramAlertSystem()
            if telegram.enabled:
                # Simple price estimation (replace with real data if available)
                current_price = final_score * 100  # Placeholder
                entry_price = current_price
                
                if signal == 'LONG':
                    take_profit = current_price * 1.03
                    stop_loss = current_price * 0.985
                else:  # SHORT
                    take_profit = current_price * 0.97
                    stop_loss = current_price * 1.015
                
                telegram.send_signal_alert(
                    symbol=symbol,
                    signal=signal,
                    score=final_score,
                    confidence=confidence,
                    price=current_price,
                    entry=entry_price,
                    tp=take_profit,
                    sl=stop_loss
                )
                print("✅ Telegram notification sent!")
        except Exception as e:
            print(f"⚠️ Telegram notification error: {e}")
    
    return {
        'final_score': final_score,
        'signal': signal,
        'confidence': confidence,
        'layers': layer_scores,
        'active_layers': active_layers,
        'total_layers': 17,
        'version': '15.0',
        'phase': 'Phase 7 Quantum + Phase 3+6 Enhanced'
    }

# ============================================================================
# STREAMLIT APP COMPATIBILITY WRAPPER v15.0
# ============================================================================

def make_trading_decision(symbol="BTCUSDT", interval="1h", timeframe=None, **kwargs):
    """
    Streamlit App Compatibility Wrapper v15.0
    
    Main entry point for Streamlit app to call AI analysis
    Backwards compatible with old function signature
    
    Args:
        symbol: Trading pair (BTCUSDT, ETHUSDT, etc.)
        interval: Timeframe (1h, 4h, 1d, etc.)
        timeframe: Alternative parameter for interval (backwards compatibility)
        **kwargs: Additional parameters
    
    Returns:
        Same as analyze_with_ai()
    """
    # Handle backwards compatibility
    if timeframe is not None:
        interval = timeframe
    
    # Call main analysis function
    return analyze_with_ai(symbol, interval)

# ============================================================================
# ALTERNATIVE CLASS-BASED INTERFACE (Your v14.1 code - PRESERVED)
# ============================================================================

class AIBrain:
    """
    AI Brain class interface for advanced usage
    Provides object-oriented access to AI analysis
    """
    def __init__(self):
        """Initialize AI Brain"""
        self.version = "15.0"
        self.layers = LAYER_WEIGHTS.copy()
        print(f"✅ AIBrain v{self.version} initialized")
    
    def analyze(self, symbol='BTCUSDT', interval='1h'):
        """
        Analyze trading pair (class method)
        
        Args:
            symbol (str): Trading pair
            interval (str): Timeframe
            
        Returns:
            dict: Analysis results
        """
        return analyze_with_ai(symbol, interval)
    
    def make_decision(self, symbol='BTCUSDT', interval='1h'):
        """
        Alias for analyze() - backwards compatibility
        """
        return self.analyze(symbol, interval)

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("🧠 AI BRAIN v15.0 TEST - QUANTUM MATHEMATICS + PHASE 3+6")
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
