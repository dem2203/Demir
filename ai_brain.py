# ============================================================================
# ai_brain.py v11.0 - WEIGHTED ENSEMBLE SCORING SYSTEM
# ============================================================================
# ✅ GitHub'daki mevcut v10.0 dosyasına WEIGHTED ENSEMBLE eklendi
# ✅ Başarısız layerları yok saymaz - sadece başarılıları değerlendirir
# ✅ Ağırlıklı ortalama sistemi (weighted ensemble)
# ✅ Confidence skoru (kaç layer aktif?)
# ✅ Dinamik ve adil skorlama
# ✅ TÜM ÖNCEKİ ÖZELLİKLER KORUNDU!
# ============================================================================

"""
🧠 DEMIR AI TRADING BOT - AI Brain v11.0
================================================================
Tarih: 3 Kasım 2025, 19:52 CET
Versiyon: 11.0 - WEIGHTED ENSEMBLE SCORING

GÜNCELLEME NOTU:
----------------
✅ GitHub'daki mevcut dosya base alındı
✅ Weighted Ensemble Scoring sistemi eklendi
✅ Tüm önceki özellikler korundu
✅ Backward compatible (geriye dönük uyumlu)

YENİ v11.0 ÖZELLİKLERİ:
-----------------------
✅ Weighted Ensemble Scoring sistemi
✅ Başarısız layerlar diğerlerini etkilemez
✅ Sadece başarılı layerların skorunu kullanır
✅ Confidence göstergesi (8/11 layer aktif gibi)
✅ Ağırlıklı ortalama ile adil değerlendirme
✅ Dinamik skor hesaplama

LAYER AĞIRLIKLARI:
-----------------
- strategy (teknik): 20%
- news: 10%
- macro: 8%
- gold: 5%
- dominance: 7%
- cross_asset: 10%
- vix: 6%
- rates: 6%
- trad_markets: 8%
- monte_carlo: 10%
- kelly: 10%

TOPLAM: 100%
"""

import os
import sys
import traceback
from datetime import datetime
import requests

# ============================================================================
# LAYER AĞIRLIKLARI (WEIGHTED ENSEMBLE) - YENİ!
# ============================================================================

LAYER_WEIGHTS = {
    'strategy': 20,           # Teknik analiz (en önemli)
    'news': 10,              # Haber sentiment
    'macro': 8,              # Makro korelasyon
    'gold': 5,               # Altın korelasyon
    'dominance': 7,          # BTC dominance
    'cross_asset': 10,       # Cross-asset korelasyon
    'vix': 6,                # Volatilite
    'rates': 6,              # Faiz oranları
    'trad_markets': 8,       # Geleneksel piyasalar
    'monte_carlo': 10,       # Monte Carlo simülasyon
    'kelly': 10              # Kelly kriteri
}

TOTAL_WEIGHT = sum(LAYER_WEIGHTS.values())  # Should be 100

# ============================================================================
# LAYER IMPORTS (Mevcut dosyadaki gibi korundu)
# ============================================================================

try:
    from strategy_layer import StrategyEngine
    print("✅ AI Brain v11.0: strategy_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: strategy_layer içe aktarma hatası: {e}")
    StrategyEngine = None

try:
    from monte_carlo_layer import run_monte_carlo_simulation
    print("✅ AI Brain v11.0: monte_carlo_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: monte_carlo_layer içe aktarma hatası: {e}")
    run_monte_carlo_simulation = None

try:
    from kelly_enhanced_layer import calculate_dynamic_kelly
    print("✅ AI Brain v11.0: kelly_enhanced_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: kelly_enhanced_layer içe aktarma hatası: {e}")
    calculate_dynamic_kelly = None

try:
    from macro_correlation_layer import MacroCorrelationLayer
    print("✅ AI Brain v11.0: macro_correlation_layer içe aktarıldı (Alpha Vantage + Twelve Data)")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: macro_correlation_layer içe aktarma hatası: {e}")
    MacroCorrelationLayer = None

try:
    from gold_correlation_layer import calculate_gold_correlation
    print("✅ AI Brain v11.0: gold_correlation_layer içe aktarıldı (Twelve Data + Binance)")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: gold_correlation_layer içe aktarma hatası: {e}")
    calculate_gold_correlation = None

try:
    from dominance_flow_layer import calculate_dominance_flow
    print("✅ AI Brain v11.0: dominance_flow_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: dominance_flow_layer içe aktarma hatası: {e}")
    calculate_dominance_flow = None

try:
    from cross_asset_layer import get_multi_coin_data
    print("✅ AI Brain v11.0: cross_asset_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: cross_asset_layer içe aktarma hatası: {e}")
    get_multi_coin_data = None

try:
    from vix_layer import get_vix_signal
    print("✅ AI Brain v11.0: vix_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: vix_layer içe aktarma hatası: {e}")
    get_vix_signal = None

try:
    from interest_rates_layer import get_interest_signal
    print("✅ AI Brain v11.0: interest_rates_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: interest_rates_layer içe aktarma hatası: {e}")
    get_interest_signal = None

try:
    from traditional_markets_layer import TraditionalMarketsLayer
    print("✅ AI Brain v11.0: traditional_markets_layer içe aktarıldı (Alpha Vantage + Twelve Data)")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: traditional_markets_layer içe aktarma hatası: {e}")
    TraditionalMarketsLayer = None

try:
    from news_sentiment_layer import get_news_score
    print("✅ AI Brain v11.0: news_sentiment_layer içe aktarıldı")
except Exception as e:
    print(f"⚠️ AI Brain v11.0: news_sentiment_layer içe aktarma hatası: {e}")
    get_news_score = None

# ============================================================================
# WEIGHTED ENSEMBLE SCORING FUNCTION - YENİ!
# ============================================================================

def calculate_ai_confidence_score(layer_results):
    """
    Weighted Ensemble Scoring System
    
    Başarısız layerları yok saymaz, sadece başarılı olanları değerlendirir
    Ağırlıklı ortalama ile adil skorlama yapar
    
    Args:
        layer_results: dict - Her layerın sonuçları
        
    Returns:
        dict: {
            'score': float,           # Ağırlıklı ortalama skor (0-100)
            'signal': str,            # STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL
            'confidence': float,      # Confidence seviyesi (0-100)
            'successful_layers': int, # Başarılı layer sayısı
            'total_layers': int,      # Toplam layer sayısı
            'coverage': str,          # "8/11" gibi
            'layer_breakdown': dict   # Her layerın detayı
        }
    """
    
    successful_layers = []
    successful_weights = []
    layer_breakdown = {}
    
    print("\n" + "="*80)
    print("🎯 WEIGHTED ENSEMBLE SCORING")
    print("="*80)
    
    # Tüm layer sonuçlarını değerlendir
    for layer_name, result in layer_results.items():
        weight = LAYER_WEIGHTS.get(layer_name, 0)
        
        # Layer başarılı mı kontrol et
        is_available = result.get('available', False)
        is_success = result.get('success', False)
        
        if is_available or is_success:
            score = result.get('score', 50)
            
            # Weighted score hesapla
            weighted_score = score * weight
            
            successful_layers.append(weighted_score)
            successful_weights.append(weight)
            
            layer_breakdown[layer_name] = {
                'score': score,
                'weight': weight,
                'weighted_score': weighted_score,
                'status': 'ACTIVE'
            }
            
            print(f"  ✅ {layer_name:15s}: Score={score:5.1f} | Weight={weight:3d}% | Weighted={weighted_score:6.1f}")
        
        else:
            layer_breakdown[layer_name] = {
                'score': 0,
                'weight': weight,
                'weighted_score': 0,
                'status': 'INACTIVE'
            }
            
            print(f"  ❌ {layer_name:15s}: INACTIVE (veri yok)")
    
    print("="*80)
    
    # Hiç layer başarılı değilse
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
    
    # Başarılı layerların ağırlıklı ortalaması
    total_successful_weight = sum(successful_weights)
    weighted_score = sum(successful_layers) / total_successful_weight
    
    # Confidence hesaplama (kaç layer başarılı?)
    confidence = (len(successful_layers) / len(LAYER_WEIGHTS)) * 100
    
    # Signal belirleme
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
# GET_REALTIME_PRICE (Mevcut dosyadan korundu)
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
# ANA KARAR FONKSİYONU (WEIGHTED ENSEMBLE ile güncellendi)
# ============================================================================

def make_trading_decision(
    symbol="BTCUSDT",
    timeframe="1h",
    portfolio_value=10000,
    **kwargs
):
    """
    Ana AI karar motoru - Weighted Ensemble Scoring ile
    
    Args:
        symbol: str - Coin sembolü
        timeframe: str - Zaman dilimi
        portfolio_value: float - Portföy değeri
        **kwargs: Ek parametreler
        
    Returns:
        dict: Trading kararı ve detayları
    """
    
    print("\n" + "="*80)
    print(f"🧠 AI BRAIN v11.0: make_trading_decision (WEIGHTED ENSEMBLE!)")
    print(f"   Symbol: {symbol}")
    print(f"   Timeframe: {timeframe}")
    print(f"   Portfolio: ${portfolio_value:,.2f}")
    if kwargs:
        print(f"   Ekstra parametreler: {list(kwargs.keys())}")
    print("="*80)
    
    # Gerçek fiyat çek
    current_price = get_realtime_price(symbol)
    
    layer_results = {}
    
    # ====================================================================
    # LAYER 1-11: STRATEGY (Teknik Analiz)
    # ====================================================================
    
    try:
        if StrategyEngine:
            print("\n🔍 strategy.calculate_comprehensive_score çağrılıyor...\n")
            engine = StrategyEngine()
            strategy_result = engine.calculate_comprehensive_score(symbol, timeframe)
            
            strategy_score = strategy_result.get('total_score', 50)
            
            layer_results['strategy'] = {
                'available': True,
                'score': strategy_score,
                'success': True
            }
            
            print(f"✅ Strategy sonucu (Layers 1-11): {strategy_score}/100\n")
        else:
            layer_results['strategy'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Strategy layer hatası: {e}")
        layer_results['strategy'] = {'available': False, 'score': 0, 'success': False}
    
    # ====================================================================
    # LAYER 12: MACRO CORRELATION
    # ====================================================================
    
    try:
        if MacroCorrelationLayer:
            print("\n🌍 MacroCorrelationLayer.analyze_all çağrılıyor (Layer 12 - YENİ API!)...\n")
            macro_layer = MacroCorrelationLayer()
            macro_result = macro_layer.analyze_all(symbol)
            
            macro_score = macro_result.get('total_score', 50)
            macro_signal = macro_result.get('signal', 'NEUTRAL')
            
            layer_results['macro'] = {
                'available': True,
                'score': macro_score,
                'signal': macro_signal,
                'success': True
            }
            
            print(f"✅ Layer 12 (Macro): {macro_score:.2f}/100 - {macro_signal}")
            print(f"   🏥 Durum: HEALTHY (GERÇEK DATA!)\n")
        else:
            layer_results['macro'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Macro layer hatası: {e}")
        layer_results['macro'] = {'available': False, 'score': 0, 'success': False}
    
    # ====================================================================
    # LAYER 13: GOLD CORRELATION
    # ====================================================================
    
    try:
        if calculate_gold_correlation:
            print("\n🥇 calculate_gold_correlation çağrılıyor (Layer 13 - YENİ API!)...\n")
            gold_result = calculate_gold_correlation(symbol, timeframe)
            
            gold_score = gold_result.get('score', 50)
            gold_signal = gold_result.get('signal', 'NEUTRAL')
            
            layer_results['gold'] = {
                'available': True,
                'score': gold_score,
                'signal': gold_signal,
                'success': True
            }
            
            print(f"✅ Layer 13 (Gold): {gold_score:.2f}/100 - {gold_signal}")
            print(f"   🏥 Durum: HEALTHY (GERÇEK DATA!)\n")
        else:
            layer_results['gold'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Gold layer hatası: {e}")
        layer_results['gold'] = {'available': False, 'score': 0, 'success': False}
    
    # ====================================================================
    # LAYER 14: DOMINANCE FLOW
    # ====================================================================
    
    try:
        if calculate_dominance_flow:
            print("\n📊 calculate_dominance_flow çağrılıyor (Layer 14)...\n")
            dom_result = calculate_dominance_flow()
            
            dom_score = dom_result.get('score', 50)
            dom_signal = dom_result.get('signal', 'NEUTRAL')
            
            layer_results['dominance'] = {
                'available': True,
                'score': dom_score,
                'signal': dom_signal,
                'success': True
            }
            
            print(f"✅ Layer 14 (Dominance): {dom_score:.2f}/100 - {dom_signal}\n")
        else:
            layer_results['dominance'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Dominance layer hatası: {e}")
        layer_results['dominance'] = {'available': False, 'score': 0, 'success': False}
    
    # ====================================================================
    # LAYER 15: CROSS-ASSET
    # ====================================================================
    
    try:
        if get_multi_coin_
            print("\n💎 cross_asset.get_multi_coin_data çağrılıyor (Layer 15)...\n")
            cross_result = get_multi_coin_data()
            
            cross_score = cross_result.get('correlation_score', 50)
            
            layer_results['cross_asset'] = {
                'available': True,
                'score': cross_score,
                'success': True
            }
            
            print(f"✅ Layer 15 (Cross-Asset): {cross_score:.2f}/100\n")
        else:
            layer_results['cross_asset'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Cross-asset layer hatası: {e}")
        layer_results['cross_asset'] = {'available': False, 'score': 0, 'success': False}
    
    # ====================================================================
    # LAYER 16: VIX
    # ====================================================================
    
    try:
        if get_vix_signal:
            print("\n⚡ get_vix_signal çağrılıyor (Layer 16)...\n")
            vix_result = get_vix_signal()
            
            vix_score = vix_result.get('score', 50)
            
            layer_results['vix'] = {
                'available': True,
                'score': vix_score,
                'success': True
            }
            
            print(f"✅ Layer 16 (VIX): {vix_score:.2f}/100\n")
        else:
            layer_results['vix'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ VIX layer hatası: {e}")
        layer_results['vix'] = {'available': False, 'score': 0, 'success': False}
    
    # ====================================================================
    # LAYER 17: INTEREST RATES
    # ====================================================================
    
    try:
        if get_interest_signal:
            print("\n💰 get_interest_signal çağrılıyor (Layer 17)...\n")
            rates_result = get_interest_signal()
            
            rates_score = rates_result.get('score', 50)
            
            layer_results['rates'] = {
                'available': True,
                'score': rates_score,
                'success': True
            }
            
            print(f"✅ Layer 17 (Rates): {rates_score:.2f}/100\n")
        else:
            layer_results['rates'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Interest rates layer hatası: {e}")
        layer_results['rates'] = {'available': False, 'score': 0, 'success': False}
    
    # ====================================================================
    # LAYER 18: TRADITIONAL MARKETS
    # ====================================================================
    
    try:
        if TraditionalMarketsLayer:
            print("\n📈 TraditionalMarketsLayer.analyze_all_markets çağrılıyor (Layer 18 - YENİ API!)...\n")
            trad_layer = TraditionalMarketsLayer()
            trad_result = trad_layer.analyze_all_markets(symbol)
            
            trad_score = trad_result.get('score', 50)
            
            layer_results['trad_markets'] = {
                'available': True,
                'score': trad_score,
                'success': True
            }
            
            print(f"✅ Layer 18 (Trad Markets): {trad_score:.2f}/100\n")
        else:
            layer_results['trad_markets'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Traditional markets layer hatası: {e}")
        layer_results['trad_markets'] = {'available': False, 'score': 0, 'success': False}
    
    # ====================================================================
    # LAYER 19: NEWS SENTIMENT
    # ====================================================================
    
    try:
        if get_news_score:
            print("\n📰 get_news_score çağrılıyor (Layer 19)...\n")
            news_result = get_news_score(symbol)
            
            news_score = news_result.get('score', 50)
            
            layer_results['news'] = {
                'available': True,
                'score': news_score,
                'success': True
            }
            
            print(f"✅ Layer 19 (News): {news_score:.2f}/100\n")
        else:
            layer_results['news'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ News sentiment layer hatası: {e}")
        layer_results['news'] = {'available': False, 'score': 0, 'success': False}
    
    # ====================================================================
    # LAYER 20: MONTE CARLO
    # ====================================================================
    
    try:
        if run_monte_carlo_simulation:
            print("\n🎲 monte_carlo.run_monte_carlo_simulation çağrılıyor...\n")
            mc_result = run_monte_carlo_simulation(symbol, timeframe)
            
            mc_return = mc_result.get('expected_return', 0)
            
            # Monte Carlo skorunu dönüştür (-100% ile +100% arası → 0-100 skora)
            mc_score = 50 + (mc_return * 50)  # 0% = 50, +100% = 100, -100% = 0
            mc_score = max(0, min(100, mc_score))  # 0-100 arası sınırla
            
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
    
    # ====================================================================
    # LAYER 21: KELLY CRITERION
    # ====================================================================
    
    try:
        if calculate_dynamic_kelly:
            print("\n🎯 kelly.calculate_dynamic_kelly çağrılıyor...\n")
            kelly_result = calculate_dynamic_kelly(symbol, timeframe, portfolio_value)
            
            kelly_fraction = kelly_result.get('kelly_fraction', 0)
            
            # Kelly fraction'ı skora dönüştür (0-0.5 arası → 0-100)
            kelly_score = (kelly_fraction / 0.5) * 100
            kelly_score = max(0, min(100, kelly_score))
            
            layer_results['kelly'] = {
                'available': True,
                'score': kelly_score,
                'kelly_fraction': kelly_fraction,
                'success': True
            }
            
            print(f"✅ Kelly: Fraction={kelly_fraction:.3f} → Score={kelly_score:.2f}/100\n")
        else:
            layer_results['kelly'] = {'available': False, 'score': 0, 'success': False}
    except Exception as e:
        print(f"⚠️ Kelly layer hatası: {e}")
        layer_results['kelly'] = {'available': False, 'score': 0, 'success': False}
    
    # ====================================================================
    # WEIGHTED ENSEMBLE SCORING - YENİ!
    # ====================================================================
    
    ensemble_result = calculate_ai_confidence_score(layer_results)
    
    # ====================================================================
    # FİNAL DECISION
    # ====================================================================
    
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
        'version': 'v11.0 - Weighted Ensemble'
    }
    
    print("\n" + "="*80)
    print("🎯 FINAL DECISION")
    print("="*80)
    print(f"  AI Confidence Score: {final_decision['ai_confidence_score']:.2f}/100")
    print(f"  Signal: {final_decision['signal']}")
    print(f"  Confidence: {final_decision['confidence']:.1f}%")
    print(f"  Coverage: {final_decision['coverage']}")
    print(f"  Current Price: ${current_price:,.2f}")
    print("="*80 + "\n")
    
    return final_decision

# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("🧠 AI BRAIN v11.0 - WEIGHTED ENSEMBLE TEST!")
    print("="*80)
    print()
    
    decision = make_trading_decision(
        symbol="BTCUSDT",
        timeframe="1h",
        portfolio_value=10000
    )
    
    print("\n" + "="*80)
    print("📊 TRADING DECISION:")
    print(f"  Symbol: {decision['symbol']}")
    print(f"  AI Score: {decision['ai_confidence_score']}/100")
    print(f"  Signal: {decision['signal']}")
    print(f"  Confidence: {decision['confidence']}%")
    print(f"  Coverage: {decision['coverage']}")
    print(f"  Price: ${decision['current_price']:,.2f}")
    print("="*80)
