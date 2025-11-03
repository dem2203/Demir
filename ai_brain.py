# ai_brain.py v13.0 - FIXED
# ============================================================================
# 🧠 DEMIR AI TRADING BOT - AI Brain v13.0 FIXED
# ============================================================================
# Date: 4 Kasım 2025, 00:45 CET
# Version: 13.0 - LAYER CALL FIXES + 12-LAYER SYSTEM
# 
# CRITICAL FIXES:
# - cross_asset: Now calls get_cross_asset_signal(symbol) correctly
# - multi_timeframe: Now calls analyze_all_timeframes(symbol) correctly
# - strategy & kelly: Better error handling
# - 12-Layer weighted ensemble system active
# ============================================================================

import os
import sys
import traceback
from datetime import datetime
import requests

# ============================================================================
# LAYER WEIGHTS (12 LAYERS)
# ============================================================================
LAYER_WEIGHTS = {
    'strategy': 18,
    'multi_timeframe': 8,
    'macro': 7,
    'gold': 5,
    'dominance': 6,
    'cross_asset': 9,
    'vix': 5,
    'rates': 5,
    'trad_markets': 7,
    'news': 9,
    'monte_carlo': 11,
    'kelly': 10
}

TOTAL_WEIGHT = sum(LAYER_WEIGHTS.values())

# ============================================================================
# LAYER IMPORTS
# ============================================================================

# Strategy Layer
try:
    from strategy_layer import StrategyEngine
    STRATEGY_AVAILABLE = True
    print("✅ strategy_layer imported")
except Exception as e:
    STRATEGY_AVAILABLE = False
    print(f"⚠️ strategy_layer import failed: {e}")

# Multi-Timeframe Layer - FIXED IMPORT
try:
    from multi_timeframe_analyzer import MultiTimeframeAnalyzer
    MULTI_TF_AVAILABLE = True
    print("✅ multi_timeframe_analyzer imported")
except Exception as e:
    MULTI_TF_AVAILABLE = False
    print(f"⚠️ multi_timeframe_analyzer import failed: {e}")

# Monte Carlo Layer
try:
    from monte_carlo_layer import run_monte_carlo_simulation
    MONTE_CARLO_AVAILABLE = True
    print("✅ monte_carlo_layer imported")
except Exception as e:
    MONTE_CARLO_AVAILABLE = False
    print(f"⚠️ monte_carlo_layer import failed: {e}")

# Kelly Layer
try:
    from kelly_enhanced_layer import calculate_dynamic_kelly
    KELLY_AVAILABLE = True
    print("✅ kelly_enhanced_layer imported")
except Exception as e:
    KELLY_AVAILABLE = False
    print(f"⚠️ kelly_enhanced_layer import failed: {e}")

# Macro Layer
try:
    from macro_correlation_layer import MacroCorrelationLayer
    MACRO_AVAILABLE = True
    print("✅ macro_correlation_layer imported")
except Exception as e:
    MACRO_AVAILABLE = False
    print(f"⚠️ macro_correlation_layer import failed: {e}")

# Gold Layer
try:
    from gold_correlation_layer import calculate_gold_correlation
    GOLD_AVAILABLE = True
    print("✅ gold_correlation_layer imported")
except Exception as e:
    GOLD_AVAILABLE = False
    print(f"⚠️ gold_correlation_layer import failed: {e}")

# Dominance Layer
try:
    from dominance_flow_layer import calculate_dominance_flow
    DOMINANCE_AVAILABLE = True
    print("✅ dominance_flow_layer imported")
except Exception as e:
    DOMINANCE_AVAILABLE = False
    print(f"⚠️ dominance_flow_layer import failed: {e}")

# Cross-Asset Layer - FIXED IMPORT
try:
    from cross_asset_layer import get_cross_asset_signal
    CROSS_ASSET_AVAILABLE = True
    print("✅ cross_asset_layer imported (get_cross_asset_signal)")
except Exception as e:
    CROSS_ASSET_AVAILABLE = False
    print(f"⚠️ cross_asset_layer import failed: {e}")

# VIX Layer
try:
    from vix_layer import get_vix_signal
    VIX_AVAILABLE = True
    print("✅ vix_layer imported")
except Exception as e:
    VIX_AVAILABLE = False
    print(f"⚠️ vix_layer import failed: {e}")

# Interest Rates Layer
try:
    from interest_rates_layer import get_interest_signal
    RATES_AVAILABLE = True
    print("✅ interest_rates_layer imported")
except Exception as e:
    RATES_AVAILABLE = False
    print(f"⚠️ interest_rates_layer import failed: {e}")

# Traditional Markets Layer
try:
    from traditional_markets_layer import TraditionalMarketsLayer
    TRAD_MARKETS_AVAILABLE = True
    print("✅ traditional_markets_layer imported")
except Exception as e:
    TRAD_MARKETS_AVAILABLE = False
    print(f"⚠️ traditional_markets_layer import failed: {e}")

# News Sentiment Layer
try:
    from news_sentiment_layer import get_news_signal
    NEWS_AVAILABLE = True
    print("✅ news_sentiment_layer imported")
except Exception as e:
    NEWS_AVAILABLE = False
    print(f"⚠️ news_sentiment_layer import failed: {e}")

# ============================================================================
# REALTIME PRICE FETCHER
# ============================================================================

def get_realtime_price(symbol="BTCUSDT"):
    """Fetch real-time price from Binance"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=10)
        data = response.json()
        price = float(data['price'])
        print(f"✅ Gerçek fiyat çekildi: {symbol} = ${price:,.2f}\n")
        return price
    except Exception as e:
        print(f"⚠️ Fiyat çekme hatası: {e}")
        return None

# ============================================================================
# WEIGHTED ENSEMBLE SCORING
# ============================================================================

def calculate_weighted_ensemble_score(layer_scores):
    """
    Calculate weighted ensemble score from 12 layers
    
    Args:
        layer_scores: Dict of {layer_name: score}
    
    Returns:
        Dict with final score, signal, confidence
    """
    print("\n" + "="*80)
    print("🎯 WEIGHTED ENSEMBLE SCORING v13.0 (12 LAYERS)")
    print("="*80)
    
    weighted_sum = 0
    total_weight_used = 0
    active_layers = 0
    
    for layer_name, weight in LAYER_WEIGHTS.items():
        score = layer_scores.get(layer_name, None)
        
        if score is not None and score >= 0:
            weighted_contribution = score * weight / 100
            weighted_sum += weighted_contribution
            total_weight_used += weight
            active_layers += 1
            
            print(f"   ✅ {layer_name:15s}: Score={score:5.1f} | Weight={weight:3d}% | Weighted={weighted_contribution:6.2f}")
        else:
            print(f"   ❌ {layer_name:15s}: INACTIVE (veri yok)")
    
    print("="*80)
    
    if total_weight_used == 0:
        print("\n⚠️ HİÇBİR LAYER AKTİF DEĞİL - NEUTRAL")
        return {
            'score': 50.0,
            'signal': 'NEUTRAL',
            'confidence': 0.0,
            'active_layers': 0,
            'total_layers': len(LAYER_WEIGHTS)
        }
    
    # Calculate final weighted score
    final_score = (weighted_sum / total_weight_used) * 100
    
    # Determine signal
    if final_score >= 70:
        signal = "STRONG_LONG"
    elif final_score >= 55:
        signal = "LONG"
    elif final_score >= 45:
        signal = "NEUTRAL"
    elif final_score >= 30:
        signal = "SHORT"
    else:
        signal = "STRONG_SHORT"
    
    # Calculate confidence
    confidence = (active_layers / len(LAYER_WEIGHTS)) * 100
    
    print(f"\n📊 WEIGHTED ENSEMBLE SONUÇLARI:")
    print(f"   Toplam Ağırlıklı Skor: {final_score:.2f}/100")
    print(f"   Signal: {signal}")
    print(f"   Confidence: {confidence:.1f}% ({active_layers}/{len(LAYER_WEIGHTS)} layer)")
    print(f"   Coverage: {active_layers}/{len(LAYER_WEIGHTS)}")
    print("="*80 + "\n")
    
    return {
        'score': round(final_score, 2),
        'signal': signal,
        'confidence': round(confidence, 1),
        'active_layers': active_layers,
        'total_layers': len(LAYER_WEIGHTS),
        'coverage': f"{active_layers}/{len(LAYER_WEIGHTS)}"
    }

# ============================================================================
# MAIN TRADING DECISION FUNCTION
# ============================================================================

def make_trading_decision(symbol="BTCUSDT", interval="1h", capital=10000, risk_per_trade=200, **kwargs):
    """
    Main AI decision engine with 12-layer weighted ensemble
    
    Args:
        symbol: Trading pair (e.g., BTCUSDT, ETHUSDT)
        interval: Timeframe (5m, 15m, 1h, 4h, 1d)
        capital: Portfolio value
        risk_per_trade: Risk amount per trade
        **kwargs: Additional parameters
    
    Returns:
        Dict with trading decision and layer breakdown
    """
    
    print("\n" + "="*80)
    print(f"🧠 AI BRAIN v13.0: make_trading_decision (MULTI-TIMEFRAME!)")
    print(f"   Symbol: {symbol}")
    print(f"   Timeframe: {interval}")
    print(f"   Portfolio: ${capital:,.2f}")
    if kwargs:
        print(f"   Ekstra parametreler: {list(kwargs.keys())}")
    print("="*80)
    
    # Get current price
    current_price = get_realtime_price(symbol)
    
    # Layer scores dictionary
    layer_scores = {}
    
    # LAYER 1: STRATEGY
    try:
        if STRATEGY_AVAILABLE:
            print("\n🔍 strategy.calculate_comprehensive_score çağrılıyor...\n")
            engine = StrategyEngine()
            strategy_result = engine.calculate_comprehensive_score(symbol, interval)
            layer_scores['strategy'] = strategy_result.get('total_score', 50)
            print(f"✅ Strategy: {layer_scores['strategy']:.2f}/100\n")
    except Exception as e:
        print(f"⚠️ Strategy layer hatası: {e}")
        layer_scores['strategy'] = None
    
    # LAYER 2: MULTI-TIMEFRAME - FIXED CALL
    try:
        if MULTI_TF_AVAILABLE:
            print(f"\n📊 multi_timeframe.analyze_all_timeframes çağrılıyor...\n")
            analyzer = MultiTimeframeAnalyzer()
            mtf_result = analyzer.analyze_all_timeframes(symbol)  # FIXED: correct method name
            layer_scores['multi_timeframe'] = mtf_result.get('score', 50)
            print(f"✅ Multi-Timeframe: {layer_scores['multi_timeframe']:.2f}/100\n")
    except Exception as e:
        print(f"⚠️ Multi-Timeframe layer hatası: {e}")
        layer_scores['multi_timeframe'] = None
    
    # LAYER 3: MACRO CORRELATION
    try:
        if MACRO_AVAILABLE:
            print(f"\n🌍 macro.get_macro_signal çağrılıyor (v4.0)...\n")
            macro_layer = MacroCorrelationLayer()
            macro_result = macro_layer.get_macro_signal(symbol)
            layer_scores['macro'] = macro_result.get('score', 50)
            print(f"✅ Macro (v4.0): {layer_scores['macro']:.2f}/100\n")
    except Exception as e:
        print(f"⚠️ Macro layer hatası: {e}")
        layer_scores['macro'] = None
    
    # LAYER 4: GOLD CORRELATION
    try:
        if GOLD_AVAILABLE:
            print(f"\n🥇 calculate_gold_correlation çağrılıyor...\n")
            gold_result = calculate_gold_correlation(symbol, interval)
            layer_scores['gold'] = gold_result.get('score', 50)
            print(f"✅ Gold: {layer_scores['gold']:.2f}/100\n")
    except Exception as e:
        print(f"⚠️ Gold layer hatası: {e}")
        layer_scores['gold'] = None
    
    # LAYER 5: DOMINANCE FLOW
    try:
        if DOMINANCE_AVAILABLE:
            print(f"\n📊 calculate_dominance_flow çağrılıyor...\n")
            dom_result = calculate_dominance_flow()
            layer_scores['dominance'] = dom_result.get('score', 50)
            print(f"✅ Dominance: {layer_scores['dominance']:.2f}/100\n")
    except Exception as e:
        print(f"⚠️ Dominance layer hatası: {e}")
        layer_scores['dominance'] = None
    
    # LAYER 6: CROSS-ASSET - FIXED CALL
    try:
        if CROSS_ASSET_AVAILABLE:
            print(f"\n💎 cross_asset.get_cross_asset_signal çağrılıyor (v2.0)...\n")
            cross_score = get_cross_asset_signal(symbol)  # FIXED: correct function signature
            layer_scores['cross_asset'] = cross_score
            print(f"✅ Cross-Asset: {layer_scores['cross_asset']:.2f}/100\n")
    except Exception as e:
        print(f"⚠️ Cross-Asset layer hatası: {e}")
        layer_scores['cross_asset'] = None
    
    # LAYER 7: VIX FEAR INDEX
    try:
        if VIX_AVAILABLE:
            print(f"\n⚡ get_vix_signal çağrılıyor (v4.0)...\n")
            vix_result = get_vix_signal()
            layer_scores['vix'] = vix_result.get('score', 50)
            print(f"✅ VIX (v4.0): {layer_scores['vix']:.2f}/100\n")
    except Exception as e:
        print(f"⚠️ VIX layer hatası: {e}")
        layer_scores['vix'] = None
    
    # LAYER 8: INTEREST RATES
    try:
        if RATES_AVAILABLE:
            print(f"\n💰 get_interest_signal çağrılıyor (v3.0)...\n")
            rates_result = get_interest_signal()
            layer_scores['rates'] = rates_result.get('score', 50)
            print(f"✅ Interest Rates (v3.0): {layer_scores['rates']:.2f}/100\n")
    except Exception as e:
        print(f"⚠️ Interest rates layer hatası: {e}")
        layer_scores['rates'] = None
    
    # LAYER 9: TRADITIONAL MARKETS
    try:
        if TRAD_MARKETS_AVAILABLE:
            print(f"\n📈 TraditionalMarketsLayer.analyze_all_markets çağrılıyor...\n")
            trad_layer = TraditionalMarketsLayer()
            trad_result = trad_layer.analyze_all_markets(symbol)
            layer_scores['trad_markets'] = trad_result.get('score', 50)
            print(f"✅ Traditional Markets: {layer_scores['trad_markets']:.2f}/100\n")
    except Exception as e:
        print(f"⚠️ Traditional markets layer hatası: {e}")
        layer_scores['trad_markets'] = None
    
    # LAYER 10: NEWS SENTIMENT
    try:
        if NEWS_AVAILABLE:
            print(f"\n📰 news.get_news_signal çağrılıyor (v2.0)...\n")
            news_result = get_news_signal(symbol)
            layer_scores['news'] = news_result.get('score', 50)
            print(f"✅ News (v2.0): {layer_scores['news']:.2f}/100\n")
    except Exception as e:
        print(f"⚠️ News sentiment layer hatası: {e}")
        layer_scores['news'] = None
    
    # LAYER 11: MONTE CARLO
    try:
        if MONTE_CARLO_AVAILABLE:
            print(f"\n🎲 monte_carlo.run_monte_carlo_simulation çağrılıyor...\n")
            mc_result = run_monte_carlo_simulation(symbol, interval)
            mc_return = mc_result.get('expected_return', 0)
            # Convert return % to score (0% = 50, +10% = 100, -10% = 0)
            mc_score = 50 + (mc_return * 5)
            mc_score = max(0, min(100, mc_score))
            layer_scores['monte_carlo'] = mc_score
            print(f"✅ Monte Carlo: Return={mc_return:.2f}% → Score={mc_score:.2f}/100\n")
    except Exception as e:
        print(f"⚠️ Monte Carlo layer hatası: {e}")
        layer_scores['monte_carlo'] = None
    
    # LAYER 12: KELLY CRITERION
    try:
        if KELLY_AVAILABLE:
            print(f"\n🎯 kelly.calculate_dynamic_kelly çağrılıyor...\n")
            kelly_result = calculate_dynamic_kelly(symbol, interval, capital)
            kelly_fraction = kelly_result.get('kelly_fraction', 0)
            # Convert Kelly fraction to score (0 = 50, 0.5 = 100, -0.5 = 0)
            kelly_score = 50 + (kelly_fraction * 100)
            kelly_score = max(0, min(100, kelly_score))
            layer_scores['kelly'] = kelly_score
            print(f"✅ Kelly: Fraction={kelly_fraction:.3f} → Score={kelly_score:.2f}/100\n")
    except Exception as e:
        print(f"⚠️ Kelly layer hatası: {e}")
        layer_scores['kelly'] = None
    
    # Calculate weighted ensemble score
    ensemble = calculate_weighted_ensemble_score(layer_scores)
    
    # Final decision
    final_decision = {
        'symbol': symbol,
        'interval': interval,
        'timestamp': datetime.now().isoformat(),
        'current_price': current_price,
        'confidence_score': ensemble['score'],
        'decision': ensemble['signal'],
        'confidence': ensemble['confidence'],
        'coverage': ensemble['coverage'],
        'active_layers': ensemble['active_layers'],
        'total_layers': ensemble['total_layers'],
        'layer_scores': layer_scores,
        'version': 'v13.0 - 12-Layer Fixed'
    }
    
    print("\n" + "="*80)
    print("🎯 FINAL DECISION")
    print("="*80)
    print(f"   AI Confidence Score: {final_decision['confidence_score']:.2f}/100")
    print(f"   Signal: {final_decision['decision']}")
    print(f"   Confidence: {final_decision['confidence']:.1f}%")
    print(f"   Coverage: {final_decision['coverage']}")
    if current_price:
        print(f"   Current Price: ${current_price:,.2f}")
    print("="*80 + "\n")
    
    return final_decision

# ============================================================================
# TEST SECTION
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("🧠 AI BRAIN v13.0 - 12-LAYER SYSTEM TEST (FIXED)")
    print("="*80)
    print()
    
    decision = make_trading_decision(
        symbol="BTCUSDT",
        interval="1h",
        capital=10000,
        risk_per_trade=200
    )
    
    print("\n" + "="*80)
    print("📊 TRADING DECISION SUMMARY:")
    print(f"   Symbol: {decision['symbol']}")
    print(f"   AI Score: {decision['confidence_score']:.2f}/100")
    print(f"   Signal: {decision['decision']}")
    print(f"   Confidence: {decision['confidence']:.1f}%")
    print(f"   Coverage: {decision['coverage']}")
    if decision.get('current_price'):
        print(f"   Price: ${decision['current_price']:,.2f}")
    print("="*80)
