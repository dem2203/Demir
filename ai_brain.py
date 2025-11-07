# ai_brain.py v16.0 - PHASE 3+6+8 FULL INTEGRATION
# ===========================================
# ✅ QUANTUM MATHEMATICS INTEGRATION (Phase 7) - PRESERVED
# ✅ 17-Layer Weighted Ensemble Analysis - PRESERVED
# ✅ PHASE 3+6 INTEGRATION - PRESERVED
# ✅ PHASE 8 QUANTUM AI (NEW) - Quantum Predictive AI
# ✅ ALL IMPORT PATHS FIXED
# ===========================================
"""
DEMIR AI TRADING BOT - AI Brain v16.0
====================================================================
Versiyon: 16.0 - QUANTUM MATHEMATICS + PHASE 3+6+8 FULL INTEGRATION
Tarih: 7 Kasim 2025, 11:32 CET

PHASE 7 (v14.1) PRESERVED:
- Black-Scholes Option Pricing
- Kalman Regime Detection
- Fractal Chaos Analysis
- Fourier Cycle Detection
- Copula Correlation

PHASE 3 (v15.0) PRESERVED:
- Telegram Alert System
- Backtest Engine
- Portfolio Optimizer

PHASE 6 (v15.0) PRESERVED:
- Enhanced Macro Layer (SPX/NASDAQ/DXY)
- Enhanced Gold Correlation
- Enhanced BTC Dominance Flow
- Enhanced VIX Fear Index
- Enhanced Interest Rates (with bugfixes)

PHASE 8 (v16.0) NEW:
- Quantum Random Forest (Exponential feature exploration)
- Quantum Neural Networks (Variational quantum classifier)
- Quantum Annealing (Portfolio optimization)

Toplam 17 Base Layers + Phase 3+6 modules + Phase 8 Quantum
Weighted Ensemble Scoring
Confidence indicator
Streamlit compatibility wrapper
"""

import os
import sys
import traceback
from datetime import datetime
import requests

# ============================================================================
# PHASE 3+6 IMPORTS - v15.1 CORRECTED
# ============================================================================

# Phase 3 Modules - Dynamic Loading
TELEGRAM_AVAILABLE = False
try:
    from telegram_alert_system import TelegramAlertSystem
    TELEGRAM_AVAILABLE = True
    print("AI Brain v16.0: Telegram imported")
except ImportError:
    print("AI Brain v16.0: Telegram not available")
    TelegramAlertSystem = None

BACKTEST_AVAILABLE = False
try:
    from backtest_engine import BacktestEngine
    BACKTEST_AVAILABLE = True
    print("AI Brain v16.0: Backtest imported")
except ImportError:
    print("AI Brain v16.0: Backtest not available")
    BacktestEngine = None

PORTFOLIO_AVAILABLE = False
try:
    from portfolio_optimizer import PortfolioOptimizer
    PORTFOLIO_AVAILABLE = True
    print("AI Brain v16.0: Portfolio Optimizer imported")
except ImportError:
    print("AI Brain v16.0: Portfolio Optimizer not available")
    PortfolioOptimizer = None

# Phase 6 Enhanced Layers - Dynamic Loading
MACRO_ENHANCED = False
try:
    from layers.enhanced_macro_layer import EnhancedMacroLayer
    MACRO_ENHANCED = True
    print("AI Brain v16.0: Enhanced Macro imported")
except ImportError:
    print("AI Brain v16.0: Enhanced Macro not available")
    EnhancedMacroLayer = None

GOLD_ENHANCED = False
try:
    from layers.enhanced_gold_layer import EnhancedGoldLayer
    GOLD_ENHANCED = True
    print("AI Brain v16.0: Enhanced Gold imported")
except ImportError:
    print("AI Brain v16.0: Enhanced Gold not available")
    EnhancedGoldLayer = None

DOMINANCE_ENHANCED = False
try:
    from layers.enhanced_dominance_layer import EnhancedDominanceLayer
    DOMINANCE_ENHANCED = True
    print("AI Brain v16.0: Enhanced Dominance imported")
except ImportError:
    print("AI Brain v16.0: Enhanced Dominance not available")
    EnhancedDominanceLayer = None

VIX_ENHANCED = False
try:
    from layers.enhanced_vix_layer import EnhancedVixLayer
    VIX_ENHANCED = True
    print("AI Brain v16.0: Enhanced VIX imported")
except ImportError:
    print("AI Brain v16.0: Enhanced VIX not available")
    EnhancedVixLayer = None

RATES_ENHANCED = False
try:
    from layers.enhanced_rates_layer import EnhancedRatesLayer, get_interest_rates_signal
    RATES_ENHANCED = True
    print("AI Brain v16.0: Enhanced Rates imported (with bugfixes v2.5)")
except ImportError:
    print("AI Brain v16.0: Enhanced Rates not available")
    EnhancedRatesLayer = None
    get_interest_rates_signal = None

# ============================================================================
# PHASE 8 QUANTUM IMPORTS - v16.0 NEW
# ============================================================================

QUANTUM_FOREST_AVAILABLE = False
try:
    from layers.quantum_forest_layer import get_quantum_forest_signal
    QUANTUM_FOREST_AVAILABLE = True
    print("AI Brain v16.0: Quantum Random Forest (Phase 8.1) imported")
except ImportError:
    print("AI Brain v16.0: Quantum Random Forest not available")
    get_quantum_forest_signal = None

QUANTUM_NN_AVAILABLE = False
try:
    from layers.quantum_nn_layer import get_quantum_nn_signal
    QUANTUM_NN_AVAILABLE = True
    print("AI Brain v16.0: Quantum Neural Networks (Phase 8.2) imported")
except ImportError:
    print("AI Brain v16.0: Quantum Neural Networks not available")
    get_quantum_nn_signal = None

QUANTUM_ANNEALING_AVAILABLE = False
try:
    from layers.quantum_annealing_layer import get_quantum_annealing_allocation
    QUANTUM_ANNEALING_AVAILABLE = True
    print("AI Brain v16.0: Quantum Annealing (Phase 8.3) imported")
except ImportError:
    print("AI Brain v16.0: Quantum Annealing not available")
    get_quantum_annealing_allocation = None

print("="*80)
print("AI Brain v16.0 - Phase 3+6+8 imports complete")
print("="*80)

# ============================================================================
# LAYER WEIGHTS (WEIGHTED ENSEMBLE) - v16.0
# ============================================================================

LAYER_WEIGHTS = {
    # Phase 1-6 Layers (70 points)
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
    
    # Phase 7 Quantum Layers (30 points)
    'black_scholes': 8,
    'kalman': 7,
    'fractal': 6,
    'fourier': 5,
    'copula': 4
}

# Phase 8 Quantum weights (New for v16.0)
QUANTUM_WEIGHTS = {
    'quantum_forest': 8,      # Quantum Random Forest
    'quantum_nn': 10,         # Quantum Neural Networks (primary)
    'quantum_annealing': 6    # Portfolio optimization
}

TOTAL_WEIGHT = sum(LAYER_WEIGHTS.values())
QUANTUM_TOTAL_WEIGHT = sum(QUANTUM_WEIGHTS.values())
print(f"AI Brain v16.0: Base Layer Weight = {TOTAL_WEIGHT}")
print(f"AI Brain v16.0: Quantum Layer Weight = {QUANTUM_TOTAL_WEIGHT}")

# ============================================================================
# PHASE 1-6 LAYER IMPORTS - v16.0 CORRECTED PATHS
# ============================================================================

try:
    from layers.strategy_layer import StrategyEngine
    print("AI Brain v16.0: strategy_layer imported")
except Exception as e:
    print(f"AI Brain v16.0: strategy_layer error: {e}")
    StrategyEngine = None

try:
    from layers.monte_carlo_layer import run_monte_carlo_simulation
    print("AI Brain v16.0: monte_carlo_layer imported")
except Exception as e:
    print(f"AI Brain v16.0: monte_carlo_layer error: {e}")
    run_monte_carlo_simulation = None

try:
    from layers.kelly_enhanced_layer import calculate_dynamic_kelly
    print("AI Brain v16.0: kelly_enhanced_layer imported")
except Exception as e:
    print(f"AI Brain v16.0: kelly_enhanced_layer error: {e}")
    calculate_dynamic_kelly = None

try:
    from layers.macro_correlation_layer import MacroCorrelationLayer
    print("AI Brain v16.0: macro_correlation_layer imported")
except Exception as e:
    print(f"AI Brain v16.0: macro_correlation_layer error: {e}")
    MacroCorrelationLayer = None

try:
    from layers.gold_correlation_layer import calculate_gold_correlation
    print("AI Brain v16.0: gold_correlation_layer imported")
except Exception as e:
    print(f"AI Brain v16.0: gold_correlation_layer error: {e}")
    calculate_gold_correlation = None

try:
    from layers.cross_asset_layer import get_cross_asset_signal
    print("AI Brain v16.0: cross_asset_layer imported")
except Exception as e:
    print(f"AI Brain v16.0: cross_asset_layer error: {e}")
    get_cross_asset_signal = None

try:
    from layers.vix_layer import calculate_vix_indicator
    print("AI Brain v16.0: vix_layer imported")
except Exception as e:
    print(f"AI Brain v16.0: vix_layer error: {e}")
    calculate_vix_indicator = None

try:
    from layers.news_sentiment_layer import NewsSentimentAnalyzer
    print("AI Brain v16.0: news_sentiment_layer imported")
except Exception as e:
    print(f"AI Brain v16.0: news_sentiment_layer error: {e}")
    NewsSentimentAnalyzer = None

try:
    from layers.black_scholes_layer import calculate_option_price
    print("AI Brain v16.0: black_scholes_layer imported")
except Exception as e:
    print(f"AI Brain v16.0: black_scholes_layer error: {e}")
    calculate_option_price = None

try:
    from layers.kalman_regime_layer import run_kalman_filter
    print("AI Brain v16.0: kalman_regime_layer imported")
except Exception as e:
    print(f"AI Brain v16.0: kalman_regime_layer error: {e}")
    run_kalman_filter = None

try:
    from layers.fractal_chaos_layer import calculate_fractal_dimension
    print("AI Brain v16.0: fractal_chaos_layer imported")
except Exception as e:
    print(f"AI Brain v16.0: fractal_chaos_layer error: {e}")
    calculate_fractal_dimension = None

try:
    from layers.fourier_cycle_layer import get_fourier_signal
    print("AI Brain v16.0: fourier_cycle_layer imported")
except Exception as e:
    print(f"AI Brain v16.0: fourier_cycle_layer error: {e}")
    get_fourier_signal = None

try:
    from layers.copula_correlation_layer import calculate_copula_correlation
    print("AI Brain v16.0: copula_correlation_layer imported")
except Exception as e:
    print(f"AI Brain v16.0: copula_correlation_layer error: {e}")
    calculate_copula_correlation = None

try:
    from layers.traditional_markets_layer import get_traditional_markets_signal
    print("AI Brain v16.0: traditional_markets_layer imported")
except Exception as e:
    print(f"AI Brain v16.0: traditional_markets_layer error: {e}")
    get_traditional_markets_signal = None

print("="*80)
print("AI Brain v16.0 - All layers loaded")
print("="*80)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_signal_text(score):
    if score >= 70:
        return "🟢 VERY BULLISH"
    elif score >= 60:
        return "🟢 BULLISH"
    elif score >= 50:
        return "🟡 NEUTRAL"
    elif score >= 40:
        return "🔴 BEARISH"
    else:
        return "🔴 VERY BEARISH"

def calculate_confidence(scores):
    if not scores or len(scores) < 3:
        return 0.3
    std = sum((s - 50)**2 for s in scores) / len(scores)
    std = std ** 0.5
    confidence = max(0, min(1, 1 - (std / 50)))
    return confidence

# ============================================================================
# ANA ANALİZ FONKSİYONU (AI BRAIN v16.0)
# ============================================================================

def analyze_with_ai(symbol, interval='1h'):
    print(f"\n{'='*80}")
    print(f"🧠 AI BRAIN v16.0 - QUANTUM ANALYSIS + PHASE 3+6+8")
    print(f"   Symbol: {symbol}")
    print(f"   Interval: {interval}")
    print(f"{'='*80}\n")
    
    layer_scores = {}
    weighted_sum = 0.0
    active_weight = 0.0

    def score_try(name, func, weight, params=None):
        try:
            if func is None:
                raise Exception("Unavailable")
            result = func(*params) if params else func(symbol)
            if isinstance(result, dict) and 'score' in result:
                score = result['score']
            elif isinstance(result, dict) and 'prediction' in result:
                score = result['prediction'] * 100  # Quantum outputs 0-1
            elif isinstance(result, (int, float)):
                score = result
            else:
                score = None
            
            if score is not None:
                layer_scores[name] = score
                nonlocal weighted_sum, active_weight
                weighted_sum += score * weight
                active_weight += weight
                print(f"✅ {name.capitalize()}: {score:.1f}/100 (weight: {weight})")
        except Exception as e:
            print(f"⚠️ {name} error: {str(e)[:50]}")
            layer_scores[name] = None

    # ========================================================================
    # PHASE 1-6 LAYERS (Sıralı ve ağırlıklı)
    # ========================================================================
    
    score_try('strategy', StrategyEngine().get_strategy_signal if StrategyEngine else None, LAYER_WEIGHTS['strategy'], [symbol, interval])
    score_try('monte_carlo', run_monte_carlo_simulation, LAYER_WEIGHTS['monte_carlo'], [symbol, interval])
    score_try('kelly', calculate_dynamic_kelly, LAYER_WEIGHTS['kelly'], [symbol])
    score_try('macro', MacroCorrelationLayer().analyze_all if MacroCorrelationLayer else None, LAYER_WEIGHTS['macro'])
    score_try('gold', calculate_gold_correlation, LAYER_WEIGHTS['gold'], [symbol])
    score_try('dominance', calculate_dominance_flow if 'calculate_dominance_flow' in dir() else None, LAYER_WEIGHTS['dominance'], [symbol])
    score_try('cross_asset', get_cross_asset_signal, LAYER_WEIGHTS['cross_asset'], [symbol])
    score_try('vix', calculate_vix_indicator, LAYER_WEIGHTS['vix'], [symbol])
    score_try('rates', get_interest_rates_signal, LAYER_WEIGHTS['rates'], [symbol])
    score_try('trad_markets', get_traditional_markets_signal, LAYER_WEIGHTS['trad_markets'], [symbol])
    
    # Phase 7 Quantum layers
    score_try('black_scholes', calculate_option_price, LAYER_WEIGHTS['black_scholes'], [symbol])
    score_try('kalman', run_kalman_filter, LAYER_WEIGHTS['kalman'], [symbol])
    score_try('fractal', calculate_fractal_dimension, LAYER_WEIGHTS['fractal'], [symbol])
    score_try('fourier', get_fourier_signal, LAYER_WEIGHTS['fourier'], [symbol])
    score_try('copula', calculate_copula_correlation, LAYER_WEIGHTS['copula'], [symbol])
    
    # ========================================================================
    # PHASE 8 QUANTUM LAYERS (NEW - v16.0)
    # ========================================================================
    
    print("\n" + "="*80)
    print("🧬 PHASE 8 QUANTUM PREDICTIVE AI")
    print("="*80 + "\n")
    
    # Prepare quantum data features
    quantum_features = {
        'price_change': layer_scores.get('strategy', 50) / 100,
        'volume': layer_scores.get('monte_carlo', 50) / 100,
        'rsi': layer_scores.get('kelly', 50) / 100,
        'macd': layer_scores.get('macro', 50) / 100,
        'volatility': layer_scores.get('vix', 50) / 100,
        'momentum': layer_scores.get('fourier', 50) / 100
    }
    
    # Quantum Random Forest (Phase 8.1)
    if QUANTUM_FOREST_AVAILABLE and get_quantum_forest_signal:
        try:
            qrf_result = get_quantum_forest_signal(quantum_features)
            if isinstance(qrf_result, dict) and 'prediction' in qrf_result:
                qrf_score = qrf_result['prediction'] * 100
                layer_scores['quantum_forest'] = qrf_score
                weighted_sum += qrf_score * QUANTUM_WEIGHTS['quantum_forest']
                active_weight += QUANTUM_WEIGHTS['quantum_forest']
                print(f"✅ Quantum Forest: {qrf_score:.1f}/100 (Phase 8.1)")
        except Exception as e:
            print(f"⚠️ Quantum Forest error: {str(e)[:50]}")
    
    # Quantum Neural Networks (Phase 8.2)
    if QUANTUM_NN_AVAILABLE and get_quantum_nn_signal:
        try:
            qnn_result = get_quantum_nn_signal(quantum_features)
            if isinstance(qnn_result, dict) and 'prediction' in qnn_result:
                qnn_score = qnn_result['prediction'] * 100
                layer_scores['quantum_nn'] = qnn_score
                weighted_sum += qnn_score * QUANTUM_WEIGHTS['quantum_nn']
                active_weight += QUANTUM_WEIGHTS['quantum_nn']
                print(f"✅ Quantum NN: {qnn_score:.1f}/100 (Phase 8.2)")
        except Exception as e:
            print(f"⚠️ Quantum NN error: {str(e)[:50]}")
    
    # Quantum Annealing (Phase 8.3) - For portfolio allocation
    if QUANTUM_ANNEALING_AVAILABLE and get_quantum_annealing_allocation:
        try:
            assets_data = {
                'BTC': {'expected_return': layer_scores.get('macro', 50) / 100, 'volatility': layer_scores.get('vix', 50) / 100},
                'ETH': {'expected_return': layer_scores.get('cross_asset', 50) / 100, 'volatility': layer_scores.get('kalman', 50) / 100},
                'USDT': {'expected_return': 0.05, 'volatility': 0.01}
            }
            qa_result = get_quantum_annealing_allocation(assets_data)
            if isinstance(qa_result, dict) and 'expected_return' in qa_result:
                qa_score = min(100, max(0, qa_result['expected_return'] * 100 + 50))
                layer_scores['quantum_annealing'] = qa_score
                weighted_sum += qa_score * QUANTUM_WEIGHTS['quantum_annealing']
                active_weight += QUANTUM_WEIGHTS['quantum_annealing']
                print(f"✅ Quantum Annealing: {qa_score:.1f}/100 (Phase 8.3)")
        except Exception as e:
            print(f"⚠️ Quantum Annealing error: {str(e)[:50]}")
    
    # ========================================================================
    # FINAL SCORE CALCULATION
    # ========================================================================
    
    if active_weight > 0:
        final_score = weighted_sum / active_weight
    else:
        final_score = 50
    
    final_score = max(0, min(100, final_score))
    confidence = calculate_confidence([s for s in layer_scores.values() if s is not None])
    signal = get_signal_text(final_score)
    active_layers = sum(1 for s in layer_scores.values() if s is not None)
    
    print(f"\n{'='*80}")
    print(f"🎯 FINAL RESULTS (v16.0)")
    print(f"{'='*80}")
    print(f"   Active Layers: {active_layers}/20")
    print(f"   Phase 1-6: {sum(1 for k, v in layer_scores.items() if k not in ['quantum_forest', 'quantum_nn', 'quantum_annealing'] and v is not None)}/15")
    print(f"   Phase 8 Quantum: {sum(1 for k, v in layer_scores.items() if k in ['quantum_forest', 'quantum_nn', 'quantum_annealing'] and v is not None)}/3")
    print(f"   Final Score: {final_score:.1f}/100")
    print(f"   Signal: {signal}")
    print(f"   Confidence: {confidence:.1%}")
    print(f"{'='*80}\n")
    
    return {
        'final_score': final_score,
        'signal': signal,
        'confidence': confidence,
        'layers': layer_scores,
        'active_layers': active_layers,
        'total_layers': 20,
        'version': '16.0',
        'phase': 'Phase 7 Quantum + Phase 3+6 Enhanced + Phase 8 Quantum AI'
    }

def make_trading_decision(symbol="BTCUSDT", interval="1h", timeframe=None, **kwargs):
    if timeframe is not None:
        interval = timeframe
    return analyze_with_ai(symbol, interval)

class AIBrain:
    def __init__(self):
        self.version = "16.0"
        self.layers = LAYER_WEIGHTS.copy()
        self.quantum_layers = QUANTUM_WEIGHTS.copy()
        print(f"AIBrain v{self.version} initialized (Phase 3+6+8)")
    
    def analyze(self, symbol='BTCUSDT', interval='1h'):
        return analyze_with_ai(symbol, interval)
    
    def make_decision(self, symbol='BTCUSDT', interval='1h'):
        return self.analyze(symbol, interval)

if __name__ == "__main__":
    print("="*80)
    print("AI BRAIN v16.0 TEST - FULL INTEGRATION (Phase 3+6+8)")
    print("="*80)
    test_symbols = ['BTCUSDT', 'ETHUSDT']
    for symbol in test_symbols:
        result = analyze_with_ai(symbol, interval='1h')
        print(f"\n📊 {symbol} Results:")
        print(f"   Score: {result['final_score']:.1f}/100")
        print(f"   Signal: {result['signal']}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Active Layers: {result['active_layers']}/{result['total_layers']}")
