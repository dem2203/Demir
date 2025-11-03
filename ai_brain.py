# ai_brain.py v13.0 - MULTI-TIMEFRAME INTEGRATION

"""
🧠 DEMIR AI TRADING BOT - AI Brain v13.0
================================================================
Versiyon: 13.0 - MULTI-TIMEFRAME INTEGRATION
Tarih: 3 Kasım 2025, 23:11 CET

✅ YENİ v13.0:
--------------
✅ Multi-Timeframe Analyzer entegrasyonu (12. layer!)
✅ 5 farklı timeframe konsensüsü (5min, 15min, 1h, 4h, 1d)
✅ Weighted scoring güncellendi
✅ 12 layer toplam

AĞIRLIKLAR:
-----------
1. strategy: 18% (teknik analiz)
2. multi_timeframe: 8% (YENİ!)
3. macro: 7%
4. gold: 5%
5. dominance: 6%
6. cross_asset: 9%
7. vix: 5%
8. rates: 5%
9. trad_markets: 7%
10. news: 9%
11. monte_carlo: 11%
12. kelly: 10%

TOPLAM: 100%
"""

import os
import sys
import traceback
from datetime import datetime
import requests

# ============================================================================
# LAYER AĞIRLIKLARI (WEIGHTED ENSEMBLE) - UPDATED v13.0!
# ============================================================================
LAYER_WEIGHTS = {
    'strategy': 18,           # Teknik analiz - azaltıldı (20→18)
    'multi_timeframe': 8,     # YENİ! - Multi-timeframe konsensüsü
    'macro': 7,               # 8→7
    'gold': 5,
    'dominance': 6,           # 7→6
    'cross_asset': 9,         # 10→9
    'vix': 5,                 # 6→5
    'rates': 5,               # 6→5
    'trad_markets': 7,        # 8→7
    'news': 9,                # 10→9
    'monte_carlo': 11,        # 10→11
    'kelly': 10
}

TOTAL_WEIGHT = sum(LAYER_WEIGHTS.values())  # Should be 100

# ============================================================================
# LAYER IMPORTS - UPDATED v13.0!
# ============================================================================
try:
    from strategy_layer import StrategyEngine
    print("✅ AI Brain v13.0: strategy_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v13.0: strategy_layer hatası: {e}")
    StrategyEngine = None

# YENİ v13.0: Multi-Timeframe Analyzer
try:
    from multi_timeframe_analyzer import MultiTimeframeAnalyzer
    print("✅ AI Brain v13.0: multi_timeframe_analyzer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v13.0: multi_timeframe_analyzer hatası: {e}")
    MultiTimeframeAnalyzer = None

try:
    from monte_carlo_layer import run_monte_carlo_simulation
    print("✅ AI Brain v13.0: monte_carlo_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v13.0: monte_carlo_layer hatası: {e}")
    run_monte_carlo_simulation = None

try:
    from kelly_enhanced_layer import calculate_dynamic_kelly
    print("✅ AI Brain v13.0: kelly_enhanced_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v13.0: kelly_enhanced_layer hatası: {e}")
    calculate_dynamic_kelly = None

try:
    from macro_correlation_layer import get_macro_signal
    print("✅ AI Brain v13.0: macro_correlation_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v13.0: macro_correlation_layer hatası: {e}")
    get_macro_signal = None

try:
    from gold_correlation_layer import calculate_gold_correlation
    print("✅ AI Brain v13.0: gold_correlation_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v13.0: gold_correlation_layer hatası: {e}")
    calculate_gold_correlation = None

try:
    from dominance_flow_layer import calculate_dominance_flow
    print("✅ AI Brain v13.0: dominance_flow_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v13.0: dominance_flow_layer hatası: {e}")
    calculate_dominance_flow = None

try:
    from cross_asset_layer import get_cross_asset_signal
    print("✅ AI Brain v13.0: cross_asset_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v13.0: cross_asset_layer hatası: {e}")
    get_cross_asset_signal = None

try:
    from vix_layer import get_vix_signal
    print("✅ AI Brain v13.0: vix_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v13.0: vix_layer hatası: {e}")
    get_vix_signal = None

try:
    from interest_rates_layer import get_interest_signal
    print("✅ AI Brain v13.0: interest_rates_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v13.0: interest_rates_layer hatası: {e}")
    get_interest_signal = None

try:
    from traditional_markets_layer import TraditionalMarketsLayer
    print("✅ AI Brain v13.0: traditional_markets_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v13.0: traditional_markets_layer hatası: {e}")
    TraditionalMarketsLayer = None

try:
    from news_sentiment_layer import get_news_signal
    print("✅ AI Brain v13.0: news_sentiment_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v13.0: news_sentiment_layer hatası: {e}")
    get_news_signal = None

# ============================================================================
# WEIGHTED ENSEMBLE SCORING FUNCTION
# ============================================================================
def calculate_ai_confidence_score(layer_results):
    """Weighted Ensemble Scoring System"""
    successful_layers = []
    successful_weights = []
    layer_breakdown = {}
    
    print("\n" + "="*80)
    print("🎯 WEIGHTED ENSEMBLE SCORING v13.0 (12 LAYERS)")
    print("="*80)
    
    for layer_name, result in layer_results.items():
        weight = LAYER_WEIGHTS.get(layer_name, 0)
        is_available = result.get('available', False)
        is_success = result.get('success', False)
        
        if is_available or is_success:
            score = result.get('score', 50)
            weighted_score = score * weight / 100  # Normalize to percentage
            successful_layers.append(weighted_score)
            successful_weights.append(weight)
            
            layer_breakdown[layer_name] = {
                'score': score,
                'weight': weight,
                'weighted_score': weighted_score,
                'status': 'ACTIVE'
            }
            
            print(f"   ✅ {layer_name:15s}: Score={score:5.1f} | Weight={weight:3d}% | Weighted={weighted_score:6.1f}")
        else:
            layer_breakdown[layer_name] = {
                'score': 0,
                'weight': weight,
                'weighted_score': 0,
                'status': 'INACTIVE'
            }
            
            print(f"   ❌ {layer_name:15s}: INACTIVE (veri yok)")
    
    print("="*80)
    
    if not successful_layers:
        print("\n⚠️ HİÇBİR LAYER AKTİF DEĞİL - NEUTRAL DÖNÜYORUZ")
        return {
            'score': 50.0,
            'signal': 'WAIT',
            'confidence': 0.0,
            'successful_layers': 0,
            'total_layers': len(LAYER_WEIGHTS),
            'coverage': f"0/{len(LAYER_WEIGHTS)}",
            'layer_breakdown': layer_breakdown,
            'reason': 'No data available from any layer'
        }
    
    # Weighted score calculation
    total_successful_weight = sum(successful_weights)
    weighted_score = (sum(successful_layers) / total_successful_weight) * 100
    confidence = (len(successful_layers) / len(LAYER_WEIGHTS)) * 100
    
    # Signal determination
    if weighted_score >= 70:
        signal = 'STRONG_BUY'
    elif weighted_score >= 55:
        signal = 'BUY'
    elif weighted_score >= 45:
        signal = 'NEUTRAL'
    elif weighted_score >= 30:
        signal = 'SELL'
    else:
        signal = 'STRONG_SELL'
    
    print(f"\n📊 WEIGHTED ENSEMBLE SONUÇLARI:")
    print(f"   Toplam Ağırlıklı Skor: {weighted_score:.2f}/100")
    print(f"   Signal: {signal}")
    print(f"   Confidence: {confidence:.1f}% ({len(successful_layers)}/{len(LAYER_WEIGHTS)} layer)")
    print(f"   Coverage: {len(successful_layers)}/{len(LAYER_WEIGHTS)}")
    print("="*80 + "\n")
    
    return {
        'score': round(weighted_score, 2),
        'signal': signal,
        'confidence': round(confidence, 2),
        'successful_layers': len(successful_layers),
        'total_layers': len(LAYER_WEIGHTS),
        'coverage': f"{len(successful_layers)}/{len(LAYER_WEIGHTS)}",
        'layer_breakdown': layer_breakdown
    }

# ============================================================================
# GET_REALTIME_PRICE
# ============================================================================
def get_realtime_price(symbol="BTCUSDT"):
    """Binance'den gerçek zamanlı fiyat çeker"""
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
# ANA KARAR FONKSİYONU - UPDATED v13.0!
# ============================================================================
def make_trading_decision(symbol="BTCUSDT", timeframe="1h", portfolio_value=10000, **kwargs):
    """Ana AI karar motoru - v13.0 Multi-Timeframe ile"""
    
    print("\n" + "="*80)
    print(f"🧠 AI BRAIN v13.0: make_trading_decision (MULTI-TIMEFRAME!)")
    print(f"   Symbol: {symbol}")
    print(f"   Timeframe: {timeframe}")
    print(f"   Portfolio: ${portfolio_value:,.2f}")
    if kwargs:
        print(f"   Ekstra parametreler: {list(kwargs.keys())}")
    print("="*80)
    
    current_price = get_realtime_price(symbol)
    layer_results = {}
    
    # LAYER 1: STRATEGY (Technical Analysis)
    try:
        if StrategyEngine:
            print("\n🔍 strategy.get_strategy_signal çağrılıyor (v2.0)...\n")
            from strategy_layer import get_strategy_signal
            strategy_result = get_strategy_signal(symbol, timeframe)
            strategy_score = strategy_result.get('score', 50)
            
            layer_results['strategy'] = {
                'available': True,
                'score': strategy_score,
                'success': True
            }
            
            print(f"✅ Strategy (v2.0): {strategy_score:.2f}/100\n")
        else:
            layer_results['strategy'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Strategy layer hatası: {e}")
        layer_results['strategy'] = {'available': False, 'score': 0, 'success': False}
    
    # LAYER 2: MULTI-TIMEFRAME (YENİ v13.0!)
    try:
        if MultiTimeframeAnalyzer:
            print("\n📊 multi_timeframe.analyze_all_timeframes çağrılıyor...\n")
            mtf_analyzer = MultiTimeframeAnalyzer()
            mtf_result = mtf_analyzer.analyze_all_timeframes(symbol)
            mtf_score = mtf_result.get('consensus_score', 50)
            mtf_signal = mtf_result.get('consensus_signal', 'NEUTRAL')
            
            layer_results['multi_timeframe'] = {
                'available': True,
                'score': mtf_score,
                'signal': mtf_signal,
                'success': True
            }
            
            print(f"✅ Multi-Timeframe: {mtf_score:.2f}/100 - {mtf_signal}\n")
        else:
            layer_results['multi_timeframe'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Multi-Timeframe layer hatası: {e}")
        layer_results['multi_timeframe'] = {'available': False, 'score': 0, 'success': False}
    
    # LAYER 3: MACRO CORRELATION
    try:
        if get_macro_signal:
            print("\n🌍 macro.get_macro_signal çağrılıyor (v4.0)...\n")
            macro_result = get_macro_signal(symbol)
            macro_score = macro_result.get('score', 50)
            macro_signal = macro_result.get('signal', 'NEUTRAL')
            
            layer_results['macro'] = {
                'available': macro_result.get('available', False),
                'score': macro_score,
                'signal': macro_signal,
                'success': True
            }
            
            print(f"✅ Macro (v4.0): {macro_score:.2f}/100\n")
        else:
            layer_results['macro'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Macro layer hatası: {e}")
        layer_results['macro'] = {'available': False, 'score': 0, 'success': False}
    
    # LAYER 4: GOLD CORRELATION
    try:
        if calculate_gold_correlation:
            print("\n🥇 calculate_gold_correlation çağrılıyor...\n")
            gold_result = calculate_gold_correlation(symbol, timeframe)
            gold_score = gold_result.get('score', 50)
            
            layer_results['gold'] = {
                'available': True,
                'score': gold_score,
                'success': True
            }
            
            print(f"✅ Gold: {gold_score:.2f}/100\n")
        else:
            layer_results['gold'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Gold layer hatası: {e}")
        layer_results['gold'] = {'available': False, 'score': 0, 'success': False}
    
    # LAYER 5: DOMINANCE FLOW
    try:
        if calculate_dominance_flow:
            print("\n📊 calculate_dominance_flow çağrılıyor...\n")
            dom_result = calculate_dominance_flow()
            dom_score = dom_result.get('score', 50)
            
            layer_results['dominance'] = {
                'available': True,
                'score': dom_score,
                'success': True
            }
            
            print(f"✅ Dominance: {dom_score:.2f}/100\n")
        else:
            layer_results['dominance'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Dominance layer hatası: {e}")
        layer_results['dominance'] = {'available': False, 'score': 0, 'success': False}
    
    # LAYER 6: CROSS-ASSET
    try:
        if get_cross_asset_signal:
            print("\n💎 cross_asset.get_cross_asset_signal çağrılıyor (v2.0)...\n")
            cross_result = get_cross_asset_signal(symbol, timeframe)
            cross_score = cross_result.get('score', 50)
            
            layer_results['cross_asset'] = {
                'available': True,
                'score': cross_score,
                'success': True
            }
            
            print(f"✅ Cross-Asset (v2.0): {cross_score:.2f}/100\n")
        else:
            layer_results['cross_asset'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Cross-Asset layer hatası: {e}")
        layer_results['cross_asset'] = {'available': False, 'score': 0, 'success': False}
    
    # LAYER 7: VIX
    try:
        if get_vix_signal:
            print("\n⚡ get_vix_signal çağrılıyor (v4.0)...\n")
            vix_result = get_vix_signal()
            vix_score = vix_result.get('score', 50)
            
            layer_results['vix'] = {
                'available': vix_result.get('available', False),
                'score': vix_score,
                'success': True
            }
            
            print(f"✅ VIX (v4.0): {vix_score:.2f}/100\n")
        else:
            layer_results['vix'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ VIX layer hatası: {e}")
        layer_results['vix'] = {'available': False, 'score': 0, 'success': False}
    
    # LAYER 8: INTEREST RATES
    try:
        if get_interest_signal:
            print("\n💰 get_interest_signal çağrılıyor (v3.0)...\n")
            rates_result = get_interest_signal()
            rates_score = rates_result.get('score', 50)
            
            layer_results['rates'] = {
                'available': True,
                'score': rates_score,
                'success': True
            }
            
            print(f"✅ Interest Rates (v3.0): {rates_score:.2f}/100\n")
        else:
            layer_results['rates'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Interest Rates layer hatası: {e}")
        layer_results['rates'] = {'available': False, 'score': 0, 'success': False}
    
    # LAYER 9: TRADITIONAL MARKETS
    try:
        if TraditionalMarketsLayer:
            print("\n📈 TraditionalMarketsLayer.analyze_all_markets çağrılıyor...\n")
            trad_layer = TraditionalMarketsLayer()
            trad_result = trad_layer.analyze_all_markets(symbol)
            trad_score = trad_result.get('score', 50)
            
            layer_results['trad_markets'] = {
                'available': True,
                'score': trad_score,
                'success': True
            }
            
            print(f"✅ Traditional Markets: {trad_score:.2f}/100\n")
        else:
            layer_results['trad_markets'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Traditional Markets layer hatası: {e}")
        layer_results['trad_markets'] = {'available': False, 'score': 0, 'success': False}
    
    # LAYER 10: NEWS SENTIMENT
    try:
        if get_news_signal:
            print("\n📰 news.get_news_signal çağrılıyor (v2.0)...\n")
            news_result = get_news_signal(symbol)
            news_score = news_result.get('score', 50)
            
            layer_results['news'] = {
                'available': True,
                'score': news_score,
                'success': True
            }
            
            print(f"✅ News (v2.0): {news_score:.2f}/100\n")
        else:
            layer_results['news'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ News Sentiment layer hatası: {e}")
        layer_results['news'] = {'available': False, 'score': 0, 'success': False}
    
    # LAYER 11: MONTE CARLO
    try:
        if run_monte_carlo_simulation:
            print("\n🎲 monte_carlo.run_monte_carlo_simulation çağrılıyor...\n")
            mc_result = run_monte_carlo_simulation(symbol, timeframe)
            mc_return = mc_result.get('expected_return', 0)
            mc_score = 50 + (mc_return * 50)  # Convert return to 0-100 score
            mc_score = max(0, min(100, mc_score))
            
            layer_results['monte_carlo'] = {
                'available': True,
                'score': mc_score,
                'expected_return': mc_return,
                'success': True
            }
            
            print(f"✅ Monte Carlo: Return={mc_return:.2f}% → Score={mc_score:.2f}/100\n")
        else:
            layer_results['monte_carlo'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Monte Carlo layer hatası: {e}")
        layer_results['monte_carlo'] = {'available': False, 'score': 0, 'success': False}
    
    # LAYER 12: KELLY CRITERION
    try:
        if calculate_dynamic_kelly:
            print("\n🎯 kelly.calculate_dynamic_kelly çağrılıyor (v2.0)...\n")
            kelly_result = calculate_dynamic_kelly(symbol, timeframe, portfolio_value)
            kelly_fraction = kelly_result.get('kelly_fraction', 0)
            kelly_score = (kelly_fraction / 0.5) * 100  # 0.5 = max reasonable Kelly
            kelly_score = max(0, min(100, kelly_score))
            
            layer_results['kelly'] = {
                'available': True,
                'score': kelly_score,
                'kelly_fraction': kelly_fraction,
                'success': True
            }
            
            print(f"✅ Kelly (v2.0): Fraction={kelly_fraction:.3f} → Score={kelly_score:.2f}/100\n")
        else:
            layer_results['kelly'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Kelly Criterion layer hatası: {e}")
        layer_results['kelly'] = {'available': False, 'score': 0, 'success': False}
    
    # WEIGHTED ENSEMBLE SCORING
    ensemble_result = calculate_ai_confidence_score(layer_results)
    
    # FINAL DECISION
    final_decision = {
        'symbol': symbol,
        'timeframe': timeframe,
        'timestamp': datetime.now().isoformat(),
        'current_price': current_price,
        'ai_confidence_score': ensemble_result['score'],
        'signal': ensemble_result['signal'],
        'confidence': ensemble_result['confidence'],
        'coverage': ensemble_result['coverage'],
        'successful_layers': ensemble_result['successful_layers'],
        'total_layers': ensemble_result['total_layers'],
        'layer_breakdown': ensemble_result['layer_breakdown'],
        'layer_results': layer_results,
        'version': 'v13.0 - Multi-Timeframe Integration'
    }
    
    print("\n" + "="*80)
    print("🎯 FINAL DECISION")
    print("="*80)
    print(f"   AI Confidence Score: {final_decision['ai_confidence_score']:.2f}/100")
    print(f"   Signal: {final_decision['signal']}")
    print(f"   Confidence: {final_decision['confidence']:.1f}%")
    print(f"   Coverage: {final_decision['coverage']}")
    if current_price:
        print(f"   Current Price: ${current_price:,.2f}")
    print("="*80 + "\n")
    
    return final_decision

# ============================================================================
# TEST
# ============================================================================
if __name__ == "__main__":
    print("="*80)
    print("🧠 AI BRAIN v13.0 - MULTI-TIMEFRAME TEST!")
    print("="*80)
    print()
    
    decision = make_trading_decision(
        symbol="BTCUSDT",
        timeframe="1h",
        portfolio_value=10000
    )
    
    print("\n" + "="*80)
    print("📊 TRADING DECISION:")
    print(f"   Symbol: {decision['symbol']}")
    print(f"   AI Score: {decision['ai_confidence_score']}/100")
    print(f"   Signal: {decision['signal']}")
    print(f"   Confidence: {decision['confidence']}%")
    print(f"   Coverage: {decision['coverage']}")
    if decision.get('current_price'):
        print(f"   Price: ${decision['current_price']:,.2f}")
    print("="*80)
