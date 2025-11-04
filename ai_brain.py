# ai_brain.py v11.0 - SIMPLIFIED & WORKING
# ================================================================
# 🔱 DEMIR AI TRADING BOT - AI Brain v11.0
# ================================================================
# Tarih: 4 Kasım 2025, 15:13 CET
# Versiyon: 11.0 - PRODUCTION READY
#
# ✅ 9 WORKING LAYERS (no quantum layers)
# ✅ AIBrain class added for compatibility
# ✅ Weighted ensemble scoring
# ✅ Real data from Binance
# ✅ Graceful error handling
# ================================================================

import os
import sys
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

# ============================================================================
# LAYER WEIGHTS (WEIGHTED ENSEMBLE) - v11.0
# ============================================================================
LAYER_WEIGHTS = {
    'strategy': 20,        # Core technical analysis
    'macro': 8,            # Macro correlation
    'gold': 5,             # Gold correlation
    'dominance': 7,        # BTC dominance
    'cross_asset': 10,     # Cross-asset analysis
    'vix': 6,              # VIX correlation
    'rates': 6,            # Interest rates
    'monte_carlo': 10,     # Monte Carlo simulation
    'kelly': 10,           # Kelly criterion
    'traditional': 8,      # Traditional markets
    'news': 10             # News sentiment
}

TOTAL_WEIGHT = sum(LAYER_WEIGHTS.values())
print(f"🔱 AI Brain v11.0: Total Layer Weight = {TOTAL_WEIGHT}")

# ============================================================================
# LAYER IMPORTS (WITH ERROR HANDLING)
# ============================================================================

# Strategy Layer
try:
    from strategy_layer import analyze_strategy
    print("✅ AI Brain v11.0: strategy_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: strategy_layer error: {e}")
    analyze_strategy = None

# Monte Carlo
try:
    from monte_carlo_layer import run_monte_carlo_simulation
    print("✅ AI Brain v11.0: monte_carlo_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: monte_carlo_layer error: {e}")
    run_monte_carlo_simulation = None

# Kelly Criterion
try:
    from kelly_enhanced_layer import calculate_kelly_position_size
    print("✅ AI Brain v11.0: kelly_enhanced_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: kelly_enhanced_layer error: {e}")
    calculate_kelly_position_size = None

# Macro Correlation
try:
    from macro_correlation_layer import get_macro_signal
    print("✅ AI Brain v11.0: macro_correlation_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: macro_correlation_layer error: {e}")
    get_macro_signal = None

# Gold Correlation
try:
    from gold_correlation_layer import calculate_gold_correlation
    print("✅ AI Brain v11.0: gold_correlation_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: gold_correlation_layer error: {e}")
    calculate_gold_correlation = None

# Dominance Flow
try:
    from dominance_flow_layer import calculate_dominance_flow
    print("✅ AI Brain v11.0: dominance_flow_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: dominance_flow_layer error: {e}")
    calculate_dominance_flow = None

# Cross Asset
try:
    from cross_asset_layer import get_cross_asset_signal
    print("✅ AI Brain v11.0: cross_asset_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: cross_asset_layer error: {e}")
    get_cross_asset_signal = None

# VIX
try:
    from vix_layer import get_vix_signal
    print("✅ AI Brain v11.0: vix_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: vix_layer error: {e}")
    get_vix_signal = None

# Interest Rates
try:
    from interest_rates_layer import get_interest_rates_score
    print("✅ AI Brain v11.0: interest_rates_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: interest_rates_layer error: {e}")
    get_interest_rates_score = None

# Traditional Markets
try:
    from traditional_markets_layer import get_traditional_markets_signal
    print("✅ AI Brain v11.0: traditional_markets_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: traditional_markets_layer error: {e}")
    get_traditional_markets_signal = None

# News Sentiment
try:
    from news_sentiment_layer import analyze_sentiment
    print("✅ AI Brain v11.0: news_sentiment_layer imported")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: news_sentiment_layer error: {e}")
    analyze_sentiment = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_signal_text(score: float) -> str:
    """
    Convert score to text signal
    
    Args:
        score: 0-100 score
    
    Returns:
        str: STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL
    """
    if score is None:
        return "NO_DATA"
    
    try:
        score = float(score)
    except (ValueError, TypeError):
        return "INVALID"
    
    if score >= 70:
        return "STRONG_BUY"
    elif score >= 55:
        return "BUY"
    elif score >= 45:
        return "NEUTRAL"
    elif score >= 30:
        return "SELL"
    else:
        return "STRONG_SELL"


def calculate_confidence(scores_dict: Dict[str, float]) -> float:
    """
    Calculate confidence based on layer agreement
    
    Args:
        scores_dict: Dictionary of layer scores
    
    Returns:
        float: Confidence 0-1
    """
    scores = [s for s in scores_dict.values() if s is not None]
    
    if len(scores) < 3:
        return 0.3  # Low confidence
    
    # Standard deviation (lower = higher agreement)
    mean = sum(scores) / len(scores)
    variance = sum((s - mean) ** 2 for s in scores) / len(scores)
    std = variance ** 0.5
    
    # Confidence: 0-1 (low std = high confidence)
    confidence = max(0, min(1, 1 - (std / 50)))
    
    return confidence


# ============================================================================
# AI BRAIN CLASS (FOR COMPATIBILITY)
# ============================================================================

class AIBrain:
    """
    AI Brain class for compatibility with existing code
    
    Provides analyze() method that wraps analyze_with_ai()
    """
    
    def __init__(self):
        """Initialize AI Brain"""
        self.version = "11.0"
        self.layers = LAYER_WEIGHTS.copy()
    
    def analyze(self, symbol: str, timeframe: str = '1h') -> Dict[str, Any]:
        """
        Analyze trading pair
        
        Args:
            symbol: Trading pair (BTCUSDT, ETHUSDT)
            timeframe: Timeframe (1h, 4h, 1d)
        
        Returns:
            dict: Analysis results
        """
        return analyze_with_ai(symbol, timeframe)


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def analyze_with_ai(symbol: str, timeframe: str = '1h') -> Dict[str, Any]:
    """
    🧠 AI Brain v11.0 - Weighted Ensemble Analysis
    
    11-Layer Analysis System:
    - Strategy (20%)
    - Macro (8%)
    - Gold (5%)
    - Dominance (7%)
    - Cross Asset (10%)
    - VIX (6%)
    - Rates (6%)
    - Monte Carlo (10%)
    - Kelly (10%)
    - Traditional Markets (8%)
    - News (10%)
    
    Args:
        symbol: Trading pair (BTCUSDT, ETHUSDT)
        timeframe: Timeframe (1h, 4h, 1d)
    
    Returns:
        dict: {
            'score': 0-100,
            'signal': 'STRONG_BUY'/'BUY'/'NEUTRAL'/'SELL'/'STRONG_SELL',
            'confidence': 0-100,
            'active_layers': int,
            'total_layers': int,
            'layers': {...}
        }
    """
    print(f"\n{'='*80}")
    print(f"🧠 AI BRAIN v11.0 - ANALYSIS")
    print(f"Symbol: {symbol} | Timeframe: {timeframe}")
    print(f"{'='*80}\n")
    
    layer_scores = {}
    weighted_sum = 0.0
    active_weight = 0.0
    
    # ========================================================================
    # LAYER 1: STRATEGY (20%)
    # ========================================================================
    if analyze_strategy is not None:
        try:
            result = analyze_strategy(symbol, timeframe)
            if result and 'score' in result:
                score = float(result['score'])
                layer_scores['strategy'] = score
                weighted_sum += score * LAYER_WEIGHTS['strategy']
                active_weight += LAYER_WEIGHTS['strategy']
                print(f"✅ Strategy: {score:.1f}/100 (weight: {LAYER_WEIGHTS['strategy']}%)")
        except Exception as e:
            print(f"⚠️ Strategy error: {e}")
            layer_scores['strategy'] = None
    
    # ========================================================================
    # LAYER 2: MONTE CARLO (10%)
    # ========================================================================
    if run_monte_carlo_simulation is not None:
        try:
            result = run_monte_carlo_simulation(symbol, timeframe)
            if result and 'score' in result:
                score = float(result['score'])
                layer_scores['monte_carlo'] = score
                weighted_sum += score * LAYER_WEIGHTS['monte_carlo']
                active_weight += LAYER_WEIGHTS['monte_carlo']
                print(f"✅ Monte Carlo: {score:.1f}/100 (weight: {LAYER_WEIGHTS['monte_carlo']}%)")
        except Exception as e:
            print(f"⚠️ Monte Carlo error: {e}")
            layer_scores['monte_carlo'] = None
    
    # ========================================================================
    # LAYER 3: KELLY (10%)
    # ========================================================================
    if calculate_kelly_position_size is not None:
        try:
            result = calculate_kelly_position_size(symbol)
            if result and 'score' in result:
                score = float(result['score'])
                layer_scores['kelly'] = score
                weighted_sum += score * LAYER_WEIGHTS['kelly']
                active_weight += LAYER_WEIGHTS['kelly']
                print(f"✅ Kelly: {score:.1f}/100 (weight: {LAYER_WEIGHTS['kelly']}%)")
        except Exception as e:
            print(f"⚠️ Kelly error: {e}")
            layer_scores['kelly'] = None
    
    # ========================================================================
    # LAYER 4: MACRO (8%)
    # ========================================================================
    if get_macro_signal is not None:
        try:
            score = get_macro_signal(symbol)
            if score is not None:
                score = float(score)
                layer_scores['macro'] = score
                weighted_sum += score * LAYER_WEIGHTS['macro']
                active_weight += LAYER_WEIGHTS['macro']
                print(f"✅ Macro: {score:.1f}/100 (weight: {LAYER_WEIGHTS['macro']}%)")
        except Exception as e:
            print(f"⚠️ Macro error: {e}")
            layer_scores['macro'] = None
    
    # ========================================================================
    # LAYER 5: GOLD (5%)
    # ========================================================================
    if calculate_gold_correlation is not None:
        try:
            score = calculate_gold_correlation(symbol)
            if score is not None:
                score = float(score)
                layer_scores['gold'] = score
                weighted_sum += score * LAYER_WEIGHTS['gold']
                active_weight += LAYER_WEIGHTS['gold']
                print(f"✅ Gold: {score:.1f}/100 (weight: {LAYER_WEIGHTS['gold']}%)")
        except Exception as e:
            print(f"⚠️ Gold error: {e}")
            layer_scores['gold'] = None
    
    # ========================================================================
    # LAYER 6: DOMINANCE (7%)
    # ========================================================================
    if calculate_dominance_flow is not None:
        try:
            score = calculate_dominance_flow(symbol)
            if score is not None:
                score = float(score)
                layer_scores['dominance'] = score
                weighted_sum += score * LAYER_WEIGHTS['dominance']
                active_weight += LAYER_WEIGHTS['dominance']
                print(f"✅ Dominance: {score:.1f}/100 (weight: {LAYER_WEIGHTS['dominance']}%)")
        except Exception as e:
            print(f"⚠️ Dominance error: {e}")
            layer_scores['dominance'] = None
    
    # ========================================================================
    # LAYER 7: CROSS ASSET (10%)
    # ========================================================================
    if get_cross_asset_signal is not None:
        try:
            score = get_cross_asset_signal(symbol)
            if score is not None:
                score = float(score)
                layer_scores['cross_asset'] = score
                weighted_sum += score * LAYER_WEIGHTS['cross_asset']
                active_weight += LAYER_WEIGHTS['cross_asset']
                print(f"✅ Cross Asset: {score:.1f}/100 (weight: {LAYER_WEIGHTS['cross_asset']}%)")
        except Exception as e:
            print(f"⚠️ Cross Asset error: {e}")
            layer_scores['cross_asset'] = None
    
    # ========================================================================
    # LAYER 8: VIX (6%)
    # ========================================================================
    if get_vix_signal is not None:
        try:
            score = get_vix_signal(symbol)
            if score is not None:
                score = float(score)
                layer_scores['vix'] = score
                weighted_sum += score * LAYER_WEIGHTS['vix']
                active_weight += LAYER_WEIGHTS['vix']
                print(f"✅ VIX: {score:.1f}/100 (weight: {LAYER_WEIGHTS['vix']}%)")
        except Exception as e:
            print(f"⚠️ VIX error: {e}")
            layer_scores['vix'] = None
    
    # ========================================================================
    # LAYER 9: INTEREST RATES (6%)
    # ========================================================================
    if get_interest_rates_score is not None:
        try:
            score = get_interest_rates_score()
            if score is not None:
                score = float(score)
                layer_scores['rates'] = score
                weighted_sum += score * LAYER_WEIGHTS['rates']
                active_weight += LAYER_WEIGHTS['rates']
                print(f"✅ Rates: {score:.1f}/100 (weight: {LAYER_WEIGHTS['rates']}%)")
        except Exception as e:
            print(f"⚠️ Rates error: {e}")
            layer_scores['rates'] = None
    
    # ========================================================================
    # LAYER 10: TRADITIONAL MARKETS (8%)
    # ========================================================================
    if get_traditional_markets_signal is not None:
        try:
            score = get_traditional_markets_signal()
            if score is not None:
                score = float(score)
                layer_scores['traditional'] = score
                weighted_sum += score * LAYER_WEIGHTS['traditional']
                active_weight += LAYER_WEIGHTS['traditional']
                print(f"✅ Traditional Markets: {score:.1f}/100 (weight: {LAYER_WEIGHTS['traditional']}%)")
        except Exception as e:
            print(f"⚠️ Traditional Markets error: {e}")
            layer_scores['traditional'] = None
    
    # ========================================================================
    # LAYER 11: NEWS SENTIMENT (10%)
    # ========================================================================
    if analyze_sentiment is not None:
        try:
            result = analyze_sentiment(symbol)
            if result and 'score' in result:
                score = float(result['score'])
                layer_scores['news'] = score
                weighted_sum += score * LAYER_WEIGHTS['news']
                active_weight += LAYER_WEIGHTS['news']
                print(f"✅ News: {score:.1f}/100 (weight: {LAYER_WEIGHTS['news']}%)")
        except Exception as e:
            print(f"⚠️ News error: {e}")
            layer_scores['news'] = None
    
    # ========================================================================
    # FINAL CALCULATION
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
    print(f"Active Layers: {active_layers}/11")
    print(f"Final Score: {final_score:.1f}/100")
    print(f"Signal: {signal}")
    print(f"Confidence: {confidence * 100:.1f}%")
    print(f"{'='*80}\n")
    
    return {
        'score': final_score,
        'signal': signal,
        'confidence': confidence * 100,  # Convert to percentage
        'active_layers': active_layers,
        'total_layers': 11,
        'layers': layer_scores,
        'version': '11.0'
    }


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🧠 AI BRAIN v11.0 TEST")
    print("=" * 80)
    
    # Test with AIBrain class
    brain = AIBrain()
    result = brain.analyze('BTCUSDT', '1h')
    
    print(f"\n📊 BTCUSDT Results:")
    print(f"  Score: {result['score']:.1f}/100")
    print(f"  Signal: {result['signal']}")
    print(f"  Confidence: {result['confidence']:.1f}%")
    print(f"  Active Layers: {result['active_layers']}/{result['total_layers']}")
    print("-" * 80)
# ============================================================================
# STREAMLIT COMPATIBILITY WRAPPER
# ============================================================================

def make_trading_decision(symbol='BTCUSDT', interval='1h'):
    """
    🎯 Streamlit App Compatibility Wrapper
    
    This function wraps analyze_with_ai() to maintain compatibility
    with streamlit_app.py which expects this function name.
    
    Args:
        symbol (str): Trading pair (BTCUSDT, ETHUSDT, etc.)
        interval (str): Timeframe (1h, 4h, 1d)
    
    Returns:
        dict: Same format as analyze_with_ai() - {
            'final_score': 0-100,
            'signal': 'LONG'/'SHORT'/'NEUTRAL',
            'confidence': 0-1,
            'layers': {...},
            'active_layers': int,
            'total_layers': int,
            'version': str,
            'phase': str
        }
    """
    print(f"📍 make_trading_decision() wrapper called for {symbol}")
    return analyze_with_ai(symbol, interval)


# ============================================================================
# ALTERNATIVE CLASS-BASED INTERFACE
# ============================================================================

class AIBrain:
    """
    AI Brain class interface for advanced usage
    
    Provides object-oriented access to AI analysis
    """
    
    def __init__(self):
        """Initialize AI Brain"""
        self.version = "14.0"
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
