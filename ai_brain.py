"""
🧠 AI BRAIN v17 - PHASE 9 HYBRID + REEL VERİ
=============================================
Date: 7 Kasım 2025, 20:15 CET
Version: 17.0 - Real Data Layers + Telegram Alerts + State Management
"""

import os
import sys
import logging
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("="*80)
print("🧠 AI BRAIN v17 - PHASE 9 HYBRID + REAL DATA")
print("="*80)

# ============================================================
# IMPORT REAL DATA LAYERS
# ============================================================

try:
    from external_data_REAL import get_all_external_data
    logger.info("✅ external_data_REAL imported (REAL)")
except Exception as e:
    logger.warning(f"⚠️ external_data_REAL import failed: {e}")
    from external_data import get_all_external_data

try:
    from enhanced_rates_REAL import get_rates_signal
    logger.info("✅ enhanced_rates_REAL imported (REAL)")
except Exception as e:
    logger.warning(f"⚠️ enhanced_rates_REAL import failed: {e}")
    try:
        from layers.enhanced_rates_layer import get_rates_signal
    except:
        pass

try:
    from vix_layer_REAL import get_vix_signal
    logger.info("✅ vix_layer_REAL imported (REAL)")
except Exception as e:
    logger.warning(f"⚠️ vix_layer_REAL import failed: {e}")
    try:
        from layers.vix_layer import get_vix_signal
    except:
        pass

try:
    from alert_system_REAL import AlertSystem, send_trading_signal
    logger.info("✅ alert_system_REAL imported (REAL)")
    ALERT_SYSTEM = AlertSystem()
except Exception as e:
    logger.warning(f"⚠️ alert_system_REAL import failed: {e}")
    ALERT_SYSTEM = None

# ============================================================
# IMPORT OTHER LAYERS (FALLBACK IF NEEDED)
# ============================================================

try:
    from layers.strategy_layer import StrategyEngine
    STRATEGY_AVAILABLE = True
except:
    STRATEGY_AVAILABLE = False

try:
    from layers.macro_correlation_layer import MacroCorrelationLayer
    MACRO_AVAILABLE = True
except:
    MACRO_AVAILABLE = False

try:
    from layers.cross_asset_layer import get_cross_asset_signal
    CROSS_ASSET_AVAILABLE = True
except:
    CROSS_ASSET_AVAILABLE = False

# ============================================================
# CORE ANALYSIS ENGINE
# ============================================================

def analyze_market(symbol='BTCUSDT', current_price=45000, interval='1h'):
    """
    Main market analysis function - v17 with real data
    
    Returns: {
        'score': 0-100,
        'signal': 'LONG'/'SHORT'/'NEUTRAL',
        'confidence': 0-1,
        'layers': {...},
        'trade_levels': {...},
        'timestamp': ISO timestamp
    }
    """
    
    logger.info(f"\n{'='*80}")
    logger.info(f"🔍 ANALYZING {symbol} | Price: ${current_price:,.2f}")
    logger.info(f"{'='*80}\n")
    
    analysis = {
        'timestamp': datetime.now().isoformat(),
        'symbol': symbol,
        'price': current_price,
        'layers': {},
        'sources': {},
        'errors': []
    }
    
    # ============================================================
    # LAYER 1: EXTERNAL DATA (Fear & Greed, Funding, etc.)
    # ============================================================
    
    try:
        logger.info("📊 Layer 1: External Data...")
        ext_data = get_all_external_data(symbol)
        
        # Fear & Greed
        fg_value = ext_data.get('fear_greed', {}).get('value', 50)
        analysis['layers']['fear_greed'] = fg_value
        analysis['sources']['fear_greed'] = ext_data.get('fear_greed', {}).get('source', 'UNKNOWN')
        
        # Funding Rate (higher funding = more leveraged longs = bearish)
        funding = ext_data.get('funding_rate', {}).get('rate', 0)
        funding_score = 50 - (funding * 1000)  # Convert to score
        funding_score = max(0, min(100, funding_score))
        analysis['layers']['funding_rate'] = funding_score
        
        # Bitcoin Dominance (higher = alt weakness = bearish alts)
        btc_dom = ext_data.get('bitcoin_dominance', {}).get('dominance', 45)
        dom_score = 50 + (btc_dom - 45) * 2  # 45% → 50, 50% → 60
        analysis['layers']['btc_dominance'] = dom_score
        
        logger.info(f" ✅ Fear & Greed: {fg_value} | Funding: {funding:.4f}% | BTC Dom: {btc_dom:.1f}%")
        
    except Exception as e:
        logger.error(f" ❌ External data error: {str(e)[:60]}")
        analysis['errors'].append(f"External data: {str(e)[:50]}")
        analysis['layers']['fear_greed'] = 50
        analysis['layers']['funding_rate'] = 50
        analysis['layers']['btc_dominance'] = 50
    
    # ============================================================
    # LAYER 2: INTEREST RATES
    # ============================================================
    
    try:
        logger.info("📊 Layer 2: Interest Rates...")
        rates_result = get_rates_signal(symbol)
        rates_score = rates_result.get('score', 50)
        analysis['layers']['interest_rates'] = rates_score
        analysis['sources']['interest_rates'] = rates_result.get('source', 'UNKNOWN')
        logger.info(f" ✅ Rates Score: {rates_score}/100")
        
    except Exception as e:
        logger.error(f" ❌ Rates error: {str(e)[:60]}")
        analysis['errors'].append(f"Rates: {str(e)[:50]}")
        analysis['layers']['interest_rates'] = 50
    
    # ============================================================
    # LAYER 3: VIX FEAR INDEX
    # ============================================================
    
    try:
        logger.info("📊 Layer 3: VIX Fear Index...")
        vix_result = get_vix_signal(symbol)
        vix_score = vix_result.get('score', 50)
        analysis['layers']['vix'] = vix_score
        analysis['sources']['vix'] = vix_result.get('source', 'UNKNOWN')
        logger.info(f" ✅ VIX Score: {vix_score}/100")
        
    except Exception as e:
        logger.error(f" ❌ VIX error: {str(e)[:60]}")
        analysis['errors'].append(f"VIX: {str(e)[:50]}")
        analysis['layers']['vix'] = 50
    
    # ============================================================
    # FILL REMAINING LAYERS WITH DEFAULTS (for demo)
    # ============================================================
    
    # In production, each layer would have real implementations
    default_layers = [
        'strategy', 'kelly', 'macro', 'gold', 'cross_asset',
        'monte_carlo', 'news', 'trad_markets', 'black_scholes',
        'kalman', 'fractal', 'fourier', 'copula', 'momentum'
    ]
    
    for layer in default_layers:
        if layer not in analysis['layers']:
            # For now, use 50 as default (neutral)
            analysis['layers'][layer] = 50
    
    # ============================================================
    # CALCULATE FINAL SCORE
    # ============================================================
    
    layer_scores = [v for v in analysis['layers'].values() if v is not None]
    if layer_scores:
        final_score = sum(layer_scores) / len(layer_scores)
    else:
        final_score = 50
    
    # Determine signal
    if final_score >= 65:
        signal = 'LONG'
        emoji = '🟢'
    elif final_score <= 35:
        signal = 'SHORT'
        emoji = '🔴'
    else:
        signal = 'NEUTRAL'
        emoji = '🟡'
    
    # Calculate confidence
    real_data_count = sum(1 for s in analysis['sources'].values() if s == 'REAL_API')
    confidence = 0.5 + (real_data_count / len(analysis['sources'])) * 0.5
    
    # Calculate trade levels
    if signal == 'LONG':
        entry = current_price
        risk = current_price * 0.02
        sl = entry - risk
        tp = entry + (risk * 2.5)
    elif signal == 'SHORT':
        entry = current_price
        risk = current_price * 0.02
        sl = entry + risk
        tp = entry - (risk * 2.5)
    else:
        entry = current_price
        sl = current_price * 0.98
        tp = current_price * 1.02
    
    analysis.update({
        'final_score': round(final_score, 2),
        'signal': signal,
        'emoji': emoji,
        'confidence': round(confidence, 2),
        'trade_levels': {
            'entry': round(entry, 2),
            'tp': round(tp, 2),
            'sl': round(sl, 2),
            'risk_reward': round(abs(tp - entry) / abs(entry - sl), 2) if abs(entry - sl) > 0 else 1.0
        },
        'data_quality': {
            'real_sources': real_data_count,
            'total_sources': len(analysis['sources']),
            'errors': len(analysis['errors'])
        }
    })
    
    # ============================================================
    # SEND ALERTS (if enabled)
    # ============================================================
    
    if ALERT_SYSTEM and final_score >= 65 or final_score <= 35:
        logger.info(f"\n🔔 Sending alerts...")
        
        # Trading signal alert
        ALERT_SYSTEM.send_trading_signal({
            'symbol': symbol,
            'score': final_score,
            'action': signal,
            'confidence': confidence,
            'entry': entry,
            'tp': tp,
            'sl': sl,
            'price': current_price
        })
        
        # Layer analysis alert
        ALERT_SYSTEM.send_layer_analysis(analysis['layers'])
    
    # ============================================================
    # PRINT RESULTS
    # ============================================================
    
    logger.info(f"\n{'='*80}")
    logger.info(f"📊 ANALYSIS COMPLETE")
    logger.info(f"{'='*80}")
    logger.info(f"{emoji} SIGNAL: {signal} | Score: {final_score:.2f}/100 | Confidence: {confidence:.0%}")
    logger.info(f"\n💰 TRADE LEVELS:")
    logger.info(f"  Entry: ${entry:,.2f}")
    logger.info(f"  TP:    ${tp:,.2f}")
    logger.info(f"  SL:    ${sl:,.2f}")
    logger.info(f"  R:R:   1:{analysis['trade_levels']['risk_reward']:.2f}")
    logger.info(f"\n📈 LAYER SCORES:")
    
    for layer, score in sorted(analysis['layers'].items()):
        if score >= 65:
            emoji_layer = "🟢"
        elif score <= 35:
            emoji_layer = "🔴"
        else:
            emoji_layer = "🟡"
        logger.info(f"  {emoji_layer} {layer:20} {score:5.1f}")
    
    logger.info(f"\n📡 DATA QUALITY:")
    logger.info(f"  Real APIs: {analysis['data_quality']['real_sources']}/{analysis['data_quality']['total_sources']}")
    logger.info(f"  Errors: {analysis['data_quality']['errors']}")
    
    if analysis['errors']:
        logger.warning(f"\n⚠️ ERRORS ENCOUNTERED:")
        for error in analysis['errors']:
            logger.warning(f"  - {error}")
    
    logger.info(f"{'='*80}\n")
    
    return analysis

# ============================================================
# STREAMLIT COMPATIBILITY
# ============================================================

def make_trading_decision(symbol='BTCUSDT', interval='1h', current_price=45000):
    """Wrapper for Streamlit compatibility"""
    return analyze_market(symbol, current_price, interval)

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    try:
        result = analyze_market('BTCUSDT', 45000, '1h')
        print("\n✅ Analysis Complete")
        print(json.dumps({
            'score': result['final_score'],
            'signal': result['signal'],
            'confidence': result['confidence']
        }, indent=2))
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
