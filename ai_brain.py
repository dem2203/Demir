# ai_brain.py v16.2 - PHASE 3+6+8 + SOURCE TRACKING
# ===========================================
# ✅ QUANTUM MATHEMATICS INTEGRATION (Phase 7) - PRESERVED
# ✅ PHASE 3+6 INTEGRATION - PRESERVED + BUGFIXED
# ✅ PHASE 8 QUANTUM AI (NEW)
# ✅ SOURCE TRACKING - Her layer'ın veri kaynağı gösterilir
# ===========================================
"""
DEMIR AI TRADING BOT - AI Brain v16.2
====================================================================
Versiyon: 16.2 - PHASE 3+6+8 + SOURCE TRACKING
Tarih: 7 Kasim 2025, 12:25 CET

YENILIK:
- ✅ Her layer'ın data source'u trackleniyor (REAL / FALLBACK / ERROR)
- ✅ Console output'da kaynak gösterilir
- ✅ JSON response'ta 'source' field ekli
"""

import os
import sys
import traceback
from datetime import datetime
import requests

# ============================================================================
# DATA SOURCE CONSTANTS
# ============================================================================

SOURCE_TYPES = {
    'REAL': '✅ Real Data',
    'FALLBACK': '⚠️ Fallback (Default)',
    'ERROR': '❌ Error (NULL)'
}

# ============================================================================
# PHASE 3+6 IMPORTS - v16.2 WITH SOURCE TRACKING
# ============================================================================

TELEGRAM_AVAILABLE = False
try:
    from telegram_alert_system import TelegramAlertSystem
    TELEGRAM_AVAILABLE = True
    print("AI Brain v16.2: Telegram imported")
except ImportError:
    print("AI Brain v16.2: Telegram not available")
    TelegramAlertSystem = None

BACKTEST_AVAILABLE = False
try:
    from backtest_engine import BacktestEngine
    BACKTEST_AVAILABLE = True
    print("AI Brain v16.2: Backtest imported")
except ImportError:
    print("AI Brain v16.2: Backtest not available")
    BacktestEngine = None

PORTFOLIO_AVAILABLE = False
try:
    from portfolio_optimizer import PortfolioOptimizer
    PORTFOLIO_AVAILABLE = True
    print("AI Brain v16.2: Portfolio Optimizer imported")
except ImportError:
    print("AI Brain v16.2: Portfolio Optimizer not available")
    PortfolioOptimizer = None

# Phase 6 Enhanced Layers
MACRO_ENHANCED = False
try:
    from layers.enhanced_macro_layer import EnhancedMacroLayer
    MACRO_ENHANCED = True
    print("AI Brain v16.2: Enhanced Macro imported")
except ImportError:
    print("AI Brain v16.2: Enhanced Macro not available")
    EnhancedMacroLayer = None

GOLD_ENHANCED = False
try:
    from layers.enhanced_gold_layer import EnhancedGoldLayer
    GOLD_ENHANCED = True
    print("AI Brain v16.2: Enhanced Gold imported")
except ImportError:
    print("AI Brain v16.2: Enhanced Gold not available")
    EnhancedGoldLayer = None

DOMINANCE_ENHANCED = False
try:
    from layers.enhanced_dominance_layer import EnhancedDominanceLayer
    DOMINANCE_ENHANCED = True
    print("AI Brain v16.2: Enhanced Dominance imported")
except ImportError:
    print("AI Brain v16.2: Enhanced Dominance not available")
    EnhancedDominanceLayer = None

VIX_ENHANCED = False
try:
    from layers.enhanced_vix_layer import EnhancedVixLayer
    VIX_ENHANCED = True
    print("AI Brain v16.2: Enhanced VIX imported")
except ImportError:
    print("AI Brain v16.2: Enhanced VIX not available")
    EnhancedVixLayer = None

RATES_ENHANCED = False
try:
    from layers.enhanced_rates_layer import EnhancedRatesLayer, get_interest_rates_signal
    RATES_ENHANCED = True
    print("AI Brain v16.2: Enhanced Rates imported (with bugfixes v2.5)")
except ImportError:
    try:
        from layers.enhanced_rates_layer import EnhancedRatesLayer
        RATES_ENHANCED = True
        def get_interest_rates_signal(symbol='BTCUSDT'):
            layer = EnhancedRatesLayer()
            return layer.calculate_rates_score(symbol)
        print("AI Brain v16.2: Enhanced Rates imported (wrapper created)")
    except ImportError:
        print("AI Brain v16.2: Enhanced Rates not available")
        EnhancedRatesLayer = None
        def get_interest_rates_signal(symbol='BTCUSDT'):
            return {'score': 50, 'signal': 'NEUTRAL', 'confidence': 0.5, 'source': 'FALLBACK'}

# Phase 8 Quantum
QUANTUM_FOREST_AVAILABLE = False
try:
    from layers.quantum_forest_layer import get_quantum_forest_signal
    QUANTUM_FOREST_AVAILABLE = True
    print("AI Brain v16.2: Quantum Random Forest (Phase 8.1) imported")
except ImportError:
    print("AI Brain v16.2: Quantum Random Forest not available")
    def get_quantum_forest_signal(data_features):
        return {'prediction': 0.5, 'confidence': 0.0, 'signal': 'NEUTRAL', 'source': 'FALLBACK'}

QUANTUM_NN_AVAILABLE = False
try:
    from layers.quantum_nn_layer import get_quantum_nn_signal
    QUANTUM_NN_AVAILABLE = True
    print("AI Brain v16.2: Quantum Neural Networks (Phase 8.2) imported")
except ImportError:
    print("AI Brain v16.2: Quantum Neural Networks not available")
    def get_quantum_nn_signal(data_features):
        return {'prediction': 0.5, 'confidence': 0.0, 'signal': 'NEUTRAL', 'source': 'FALLBACK'}

QUANTUM_ANNEALING_AVAILABLE = False
try:
    from layers.quantum_annealing_layer import get_quantum_annealing_allocation
    QUANTUM_ANNEALING_AVAILABLE = True
    print("AI Brain v16.2: Quantum Annealing (Phase 8.3) imported")
except ImportError:
    print("AI Brain v16.2: Quantum Annealing not available")
    def get_quantum_annealing_allocation(assets_data):
        return {'expected_return': 0.05, 'allocation': {}, 'source': 'FALLBACK'}

print("="*80)
print("AI Brain v16.2 - Phase 3+6+8 imports complete + SOURCE TRACKING")
print("="*80)

# ============================================================================
# LAYER WEIGHTS
# ============================================================================

LAYER_WEIGHTS = {
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
    
    'black_scholes': 8,
    'kalman': 7,
    'fractal': 6,
    'fourier': 5,
    'copula': 4
}

QUANTUM_WEIGHTS = {
    'quantum_forest': 8,
    'quantum_nn': 10,
    'quantum_annealing': 6
}

TOTAL_WEIGHT = sum(LAYER_WEIGHTS.values())
QUANTUM_TOTAL_WEIGHT = sum(QUANTUM_WEIGHTS.values())
print(f"AI Brain v16.2: Base Layer Weight = {TOTAL_WEIGHT}")
print(f"AI Brain v16.2: Quantum Layer Weight = {QUANTUM_TOTAL_WEIGHT}")

# ============================================================================
# PHASE 1-6 LAYER IMPORTS - v16.2
# ============================================================================

try:
    from layers.strategy_layer import StrategyEngine
    print("AI Brain v16.2: strategy_layer imported")
except Exception as e:
    print(f"AI Brain v16.2: strategy_layer error: {e}")
    StrategyEngine = None

try:
    from layers.monte_carlo_layer import run_monte_carlo_simulation
    print("AI Brain v16.2: monte_carlo_layer imported")
except Exception as e:
    print(f"AI Brain v16.2: monte_carlo_layer error: {e}")
    run_monte_carlo_simulation = None

try:
    from layers.kelly_enhanced_layer import calculate_dynamic_kelly
    print("AI Brain v16.2: kelly_enhanced_layer imported")
except Exception as e:
    print(f"AI Brain v16.2: kelly_enhanced_layer error: {e}")
    calculate_dynamic_kelly = None

try:
    from layers.macro_correlation_layer import MacroCorrelationLayer
    print("AI Brain v16.2: macro_correlation_layer imported")
except Exception as e:
    print(f"AI Brain v16.2: macro_correlation_layer error: {e}")
    MacroCorrelationLayer = None

try:
    from layers.gold_correlation_layer import calculate_gold_correlation
    print("AI Brain v16.2: gold_correlation_layer imported")
except Exception as e:
    print(f"AI Brain v16.2: gold_correlation_layer error: {e}")
    calculate_gold_correlation = None

try:
    from layers.cross_asset_layer import get_cross_asset_signal
    print("AI Brain v16.2: cross_asset_layer imported")
except Exception as e:
    print(f"AI Brain v16.2: cross_asset_layer error: {e}")
    get_cross_asset_signal = None

# VIX Layer
try:
    from layers.vix_layer import get_vix_signal
    print("AI Brain v16.2: vix_layer imported (get_vix_signal)")
except Exception as e:
    try:
        from layers.vix_layer import calculate_vix_score
        get_vix_signal = calculate_vix_score
        print("AI Brain v16.2: vix_layer imported (calculate_vix_score)")
    except Exception as e2:
        print(f"AI Brain v16.2: vix_layer error: {e}")
        def get_vix_signal(symbol='BTCUSDT'):
            return {'score': 50, 'signal': 'NEUTRAL', 'source': 'FALLBACK'}

# News Sentiment
try:
    from layers.news_sentiment_layer import get_sentiment_score
    print("AI Brain v16.2: news_sentiment_layer imported (get_sentiment_score)")
except Exception as e:
    try:
        from layers.news_sentiment_layer import analyze_sentiment
        get_sentiment_score = analyze_sentiment
        print("AI Brain v16.2: news_sentiment_layer imported (analyze_sentiment)")
    except Exception as e2:
        print(f"AI Brain v16.2: news_sentiment_layer error: {e}")
        def get_sentiment_score(symbol='BTCUSDT'):
            return {'score': 50, 'signal': 'NEUTRAL', 'source': 'FALLBACK'}

# Black-Scholes
try:
    from layers.quantum_black_scholes_layer import calculate_option_price
    print("AI Brain v16.2: quantum_black_scholes_layer imported")
except Exception as e:
    print(f"AI Brain v16.2: black_scholes error: {e}")
    def calculate_option_price(symbol='BTCUSDT'):
        return {'score': 50, 'signal': 'NEUTRAL', 'source': 'FALLBACK'}

# Kalman
try:
    from layers.kalman_regime_layer import kalman_filter_analysis
    print("AI Brain v16.2: kalman_regime_layer imported (kalman_filter_analysis)")
except Exception as e:
    try:
        from layers.kalman_regime_layer import get_kalman_signal
        kalman_filter_analysis = get_kalman_signal
        print("AI Brain v16.2: kalman_regime_layer imported (get_kalman_signal)")
    except Exception as e2:
        print(f"AI Brain v16.2: kalman_regime error: {e}")
        def kalman_filter_analysis(symbol='BTCUSDT'):
            return {'score': 50, 'signal': 'NEUTRAL', 'source': 'FALLBACK'}

try:
    from layers.fractal_chaos_layer import analyze_fractal_dimension
    print("AI Brain v16.2: fractal_chaos_layer imported")
except Exception as e:
    print(f"AI Brain v16.2: fractal_chaos_layer error: {e}")
    def analyze_fractal_dimension(symbol='BTCUSDT'):
        return {'score': 50, 'signal': 'NEUTRAL', 'source': 'FALLBACK'}

# Fourier
try:
    from layers.fourier_cycle_layer import analyze_fourier_cycles
    print("AI Brain v16.2: fourier_cycle_layer imported (analyze_fourier_cycles)")
except Exception as e:
    try:
        from layers.fourier_cycle_layer import get_cycle_signal
        analyze_fourier_cycles = get_cycle_signal
        print("AI Brain v16.2: fourier_cycle_layer imported (get_cycle_signal)")
    except Exception as e2:
        print(f"AI Brain v16.2: fourier_cycle error: {e}")
        def analyze_fourier_cycles(symbol='BTCUSDT'):
            return {'score': 50, 'signal': 'NEUTRAL', 'source': 'FALLBACK'}

# Copula
try:
    from layers.copula_correlation_layer import analyze_copula_correlation
    print("AI Brain v16.2: copula_correlation_layer imported (analyze_copula_correlation)")
except Exception as e:
    try:
        from layers.copula_correlation_layer import get_copula_score
        analyze_copula_correlation = get_copula_score
        print("AI Brain v16.2: copula_correlation_layer imported (get_copula_score)")
    except Exception as e2:
        print(f"AI Brain v16.2: copula_correlation error: {e}")
        def analyze_copula_correlation(symbol='BTCUSDT'):
            return {'score': 50, 'signal': 'NEUTRAL', 'source': 'FALLBACK'}

try:
    from layers.traditional_markets_layer import get_traditional_markets_signal
    print("AI Brain v16.2: traditional_markets_layer imported")
except Exception as e:
    print(f"AI Brain v16.2: traditional_markets_layer error: {e}")
    def get_traditional_markets_signal(symbol='BTCUSDT'):
        return {'score': 50, 'signal': 'NEUTRAL', 'source': 'FALLBACK'}

print("="*80)
print("AI Brain v16.2 - All layers loaded (with SOURCE TRACKING)")
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

def extract_score(result):
    """Extract score from various result formats"""
    if result is None:
        return None, 'ERROR'
    if isinstance(result, dict):
        source = result.get('source', 'UNKNOWN')
        if 'score' in result:
            return result['score'], source
        elif 'prediction' in result:
            return result['prediction'] * 100, source
        elif 'final_score' in result:
            return result['final_score'], source
    elif isinstance(result, (int, float)):
        return result, 'UNKNOWN'
    return None, 'ERROR'

# ============================================================================
# ANA ANALİZ FONKSİYONU (AI BRAIN v16.2 + SOURCE TRACKING)
# ============================================================================

def analyze_with_ai(symbol, interval='1h'):
    print(f"\n{'='*80}")
    print(f"🧠 AI BRAIN v16.2 - QUANTUM ANALYSIS + SOURCE TRACKING")
    print(f"   Symbol: {symbol}")
    print(f"   Interval: {interval}")
    print(f"{'='*80}\n")
    
    layer_scores = {}
    layer_sources = {}
    weighted_sum = 0.0
    active_weight = 0.0

    def score_try(name, func, weight, params=None):
        try:
            if func is None:
                raise Exception("Function unavailable")
            
            result = func(*params) if params else func(symbol)
            score, source = extract_score(result)
            
            if score is not None:
                score = max(0, min(100, score))
                layer_scores[name] = score
                layer_sources[name] = source
                nonlocal weighted_sum, active_weight
                weighted_sum += score * weight
                active_weight += weight
                
                source_icon = '✅' if source == 'REAL' else '⚠️' if source == 'FALLBACK' else '❌'
                print(f"{source_icon} {name.capitalize()}: {score:.1f}/100 (weight: {weight}) [{source}]")
            else:
                layer_scores[name] = None
                layer_sources[name] = 'ERROR'
                print(f"❌ {name}: No score returned [ERROR]")
        except Exception as e:
            print(f"❌ {name} error: {str(e)[:50]} [ERROR]")
            layer_scores[name] = None
            layer_sources[name] = 'ERROR'

    # ========================================================================
    # PHASE 1-6 LAYERS
    # ========================================================================
    
    score_try('strategy', StrategyEngine().get_strategy_signal if StrategyEngine else None, LAYER_WEIGHTS['strategy'], [symbol, interval])
    score_try('monte_carlo', run_monte_carlo_simulation, LAYER_WEIGHTS['monte_carlo'], [symbol, interval])
    score_try('kelly', calculate_dynamic_kelly, LAYER_WEIGHTS['kelly'], [symbol])
    score_try('macro', MacroCorrelationLayer().analyze_all if MacroCorrelationLayer else None, LAYER_WEIGHTS['macro'])
    score_try('gold', calculate_gold_correlation, LAYER_WEIGHTS['gold'], [symbol])
    score_try('cross_asset', get_cross_asset_signal, LAYER_WEIGHTS['cross_asset'], [symbol])
    score_try('vix', get_vix_signal, LAYER_WEIGHTS['vix'], [symbol])
    score_try('rates', get_interest_rates_signal, LAYER_WEIGHTS['rates'], [symbol])
    score_try('news', get_sentiment_score, LAYER_WEIGHTS['news'], [symbol])
    score_try('trad_markets', get_traditional_markets_signal, LAYER_WEIGHTS['trad_markets'], [symbol])
    
    # Phase 7 Quantum layers
    score_try('black_scholes', calculate_option_price, LAYER_WEIGHTS['black_scholes'], [symbol])
    score_try('kalman', kalman_filter_analysis, LAYER_WEIGHTS['kalman'], [symbol])
    score_try('fractal', analyze_fractal_dimension, LAYER_WEIGHTS['fractal'], [symbol])
    score_try('fourier', analyze_fourier_cycles, LAYER_WEIGHTS['fourier'], [symbol])
    score_try('copula', analyze_copula_correlation, LAYER_WEIGHTS['copula'], [symbol])
    
    # ========================================================================
    # PHASE 8 QUANTUM LAYERS
    # ========================================================================
    
    print("\n" + "="*80)
    print("🧬 PHASE 8 QUANTUM PREDICTIVE AI")
    print("="*80 + "\n")
    
    quantum_features = {
        'price_change': (layer_scores.get('strategy', 50) or 50) / 100,
        'volume': (layer_scores.get('monte_carlo', 50) or 50) / 100,
        'rsi': (layer_scores.get('kelly', 50) or 50) / 100,
        'macd': (layer_scores.get('macro', 50) or 50) / 100,
        'volatility': (layer_scores.get('vix', 50) or 50) / 100,
        'momentum': (layer_scores.get('fourier', 50) or 50) / 100
    }
    
    # Quantum Random Forest
    try:
        qrf_result = get_quantum_forest_signal(quantum_features)
        qrf_score, qrf_source = extract_score(qrf_result)
        if qrf_score:
            layer_scores['quantum_forest'] = qrf_score
            layer_sources['quantum_forest'] = qrf_source
            weighted_sum += qrf_score * QUANTUM_WEIGHTS['quantum_forest']
            active_weight += QUANTUM_WEIGHTS['quantum_forest']
            qrf_icon = '✅' if qrf_source == 'REAL' else '⚠️'
            print(f"{qrf_icon} Quantum Forest: {qrf_score:.1f}/100 [{qrf_source}] (Phase 8.1)")
    except Exception as e:
        print(f"❌ Quantum Forest error: {str(e)[:50]} [ERROR]")
    
    # Quantum Neural Networks
    try:
        qnn_result = get_quantum_nn_signal(quantum_features)
        qnn_score, qnn_source = extract_score(qnn_result)
        if qnn_score:
            layer_scores['quantum_nn'] = qnn_score
            layer_sources['quantum_nn'] = qnn_source
            weighted_sum += qnn_score * QUANTUM_WEIGHTS['quantum_nn']
            active_weight += QUANTUM_WEIGHTS['quantum_nn']
            qnn_icon = '✅' if qnn_source == 'REAL' else '⚠️'
            print(f"{qnn_icon} Quantum NN: {qnn_score:.1f}/100 [{qnn_source}] (Phase 8.2)")
    except Exception as e:
        print(f"❌ Quantum NN error: {str(e)[:50]} [ERROR]")
    
    # Quantum Annealing
    try:
        assets_data = {
            'BTC': {'expected_return': (layer_scores.get('macro', 50) or 50) / 100, 'volatility': (layer_scores.get('vix', 50) or 50) / 100},
            'ETH': {'expected_return': (layer_scores.get('cross_asset', 50) or 50) / 100, 'volatility': (layer_scores.get('kalman', 50) or 50) / 100},
        }
        qa_result = get_quantum_annealing_allocation(assets_data)
        qa_source = qa_result.get('source', 'FALLBACK') if isinstance(qa_result, dict) else 'UNKNOWN'
        if isinstance(qa_result, dict) and 'expected_return' in qa_result:
            qa_score = min(100, max(0, (qa_result['expected_return'] * 100) + 50))
            layer_scores['quantum_annealing'] = qa_score
            layer_sources['quantum_annealing'] = qa_source
            weighted_sum += qa_score * QUANTUM_WEIGHTS['quantum_annealing']
            active_weight += QUANTUM_WEIGHTS['quantum_annealing']
            qa_icon = '✅' if qa_source == 'REAL' else '⚠️'
            print(f"{qa_icon} Quantum Annealing: {qa_score:.1f}/100 [{qa_source}] (Phase 8.3)")
    except Exception as e:
        print(f"❌ Quantum Annealing error: {str(e)[:50]} [ERROR]")
    
    # ========================================================================
    # FINAL SCORE
    # ========================================================================
    
    if active_weight > 0:
        final_score = weighted_sum / active_weight
    else:
        final_score = 50
    
    final_score = max(0, min(100, final_score))
    active_layers = sum(1 for s in layer_scores.values() if s is not None)
    confidence = calculate_confidence([s for s in layer_scores.values() if s is not None])
    signal = get_signal_text(final_score)
    
    # Source statistics
    real_count = sum(1 for s in layer_sources.values() if s == 'REAL')
    fallback_count = sum(1 for s in layer_sources.values() if s == 'FALLBACK')
    error_count = sum(1 for s in layer_sources.values() if s == 'ERROR')
    
    print(f"\n{'='*80}")
    print(f"🎯 FINAL RESULTS (v16.2 + SOURCE TRACKING)")
    print(f"{'='*80}")
    print(f"   Active Layers: {active_layers}/20")
    print(f"   Data Quality: {real_count} REAL | {fallback_count} FALLBACK | {error_count} ERROR")
    print(f"   Real Data %: {(real_count/20*100):.0f}%")
    print(f"   Final Score: {final_score:.1f}/100")
    print(f"   Signal: {signal}")
    print(f"   Confidence: {confidence:.1%}")
    print(f"{'='*80}\n")
    
    return {
        'final_score': final_score,
        'signal': signal,
        'confidence': confidence,
        'layers': layer_scores,
        'sources': layer_sources,
        'active_layers': active_layers,
        'total_layers': 20,
        'data_quality': {
            'real': real_count,
            'fallback': fallback_count,
            'error': error_count
        },
        'version': '16.2',
        'phase': 'Phase 7 Quantum + Phase 3+6 Enhanced + Phase 8 Quantum AI'
    }

def make_trading_decision(symbol="BTCUSDT", interval="1h", timeframe=None, **kwargs):
    if timeframe is not None:
        interval = timeframe
    return analyze_with_ai(symbol, interval)

class AIBrain:
    def __init__(self):
        self.version = "16.2"
        self.layers = LAYER_WEIGHTS.copy()
        self.quantum_layers = QUANTUM_WEIGHTS.copy()
        print(f"AIBrain v{self.version} initialized (Phase 3+6+8 + SOURCE TRACKING)")
    
    def analyze(self, symbol='BTCUSDT', interval='1h'):
        return analyze_with_ai(symbol, interval)
    
    def make_decision(self, symbol='BTCUSDT', interval='1h'):
        return self.analyze(symbol, interval)

if __name__ == "__main__":
    print("="*80)
    print("AI BRAIN v16.2 TEST - FULL INTEGRATION (Phase 3+6+8 + SOURCE TRACKING)")
    print("="*80)
    test_symbols = ['BTCUSDT', 'ETHUSDT']
    for symbol in test_symbols:
        result = analyze_with_ai(symbol, interval='1h')
        print(f"\n📊 {symbol} Results:")
        print(f"   Score: {result['final_score']:.1f}/100")
        print(f"   Signal: {result['signal']}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Active Layers: {result['active_layers']}/{result['total_layers']}")
        print(f"   Data Quality: {result['data_quality']['real']} REAL, {result['data_quality']['fallback']} FALLBACK, {result['data_quality']['error']} ERROR")
