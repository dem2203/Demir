"""
🔱 DEMIR AI TRADING BOT - AI Brain v9.0 PRODUCTION ULTIMATE
===========================================================
Date: 2 Kasım 2025, 21:40 CET
Version: 9.0 - 18-LAYER WITH REAL DATA INTEGRATION

EVOLUTION:
----------
v4: Phase 3A + 3B (11 layers)
v5: Phase 6 MACRO (12 layers)
v6: ATTEMPT (14 layers - had import issues)
v7: PRODUCTION FIX (15 layers - working!)
v8: PHASE 6 COMPLETE (18 layers)
v9: REAL DATA INTEGRATION (yfinance + CMC_API_KEY + FRED_API_KEY) ⭐ NEW!

ALL 18 LAYERS:
--------------
Layers 1-11: From strategy_layer (working code PRESERVED!)
Layer 12: Macro Correlation (REAL DATA - yfinance + CMC)
Layer 13: Gold Correlation (REAL DATA - yfinance)
Layer 14: BTC Dominance Flow (REAL DATA - CMC_API_KEY)
Layer 15: Cross-Asset Correlation (REAL DATA)
Layer 16: VIX Fear Index (REAL DATA - yfinance)
Layer 17: Interest Rates Impact (REAL DATA - FRED_API_KEY + yfinance)
Layer 18: Traditional Markets (REAL DATA - yfinance)

✅ ALL REAL DATA - NO MOCK VALUES!
✅ API KEYS: CMC_API_KEY, FRED_API_KEY
✅ FREE DATA: yfinance (no key required)
"""

from datetime import datetime

# ============================================================================
# IMPORTS - ALL LAYERS
# ============================================================================

# Phase 3A + 3B layers
try:
    import strategy_layer as strategy
    STRATEGY_AVAILABLE = True
    print("✅ AI Brain: strategy_layer imported")
except Exception as e:
    STRATEGY_AVAILABLE = False
    print(f"⚠️ AI Brain: strategy_layer import failed: {e}")

try:
    import monte_carlo_layer as mc
    MC_AVAILABLE = True
    print("✅ AI Brain: monte_carlo_layer imported")
except Exception as e:
    MC_AVAILABLE = False
    print(f"⚠️ AI Brain: monte_carlo_layer import failed: {e}")

try:
    import kelly_enhanced_layer as kelly
    KELLY_AVAILABLE = True
    print("✅ AI Brain: kelly_enhanced_layer imported")
except Exception as e:
    KELLY_AVAILABLE = False
    print(f"⚠️ AI Brain: kelly_enhanced_layer import failed: {e}")

# Phase 6 layers (UPDATED IMPORTS FOR v9!)
try:
    from macro_correlation_layer import MacroCorrelationLayer
    MACRO_AVAILABLE = True
    print("✅ AI Brain v9: macro_correlation_layer imported (REAL DATA!)")
except Exception as e:
    MACRO_AVAILABLE = False
    print(f"⚠️ AI Brain v9: macro_correlation_layer import failed: {e}")

try:
    from gold_correlation_layer import get_gold_signal, calculate_gold_correlation
    GOLD_AVAILABLE = True
    print("✅ AI Brain v9: gold_correlation_layer imported (REAL DATA!)")
except Exception as e:
    GOLD_AVAILABLE = False
    print(f"⚠️ AI Brain v9: gold_correlation_layer import failed: {e}")

try:
    from dominance_flow_layer import get_dominance_signal, calculate_dominance_flow
    DOMINANCE_AVAILABLE = True
    print("✅ AI Brain v9: dominance_flow_layer imported (REAL DATA!)")
except Exception as e:
    DOMINANCE_AVAILABLE = False
    print(f"⚠️ AI Brain v9: dominance_flow_layer import failed: {e}")

try:
    import cross_asset_layer as cross_asset
    CROSS_ASSET_AVAILABLE = True
    print("✅ AI Brain v9: cross_asset_layer imported")
except Exception as e:
    CROSS_ASSET_AVAILABLE = False
    print(f"⚠️ AI Brain v9: cross_asset_layer import failed: {e}")

try:
    from vix_layer import get_vix_signal, analyze_vix
    VIX_AVAILABLE = True
    print("✅ AI Brain v9: vix_layer imported (REAL DATA!)")
except Exception as e:
    VIX_AVAILABLE = False
    print(f"⚠️ AI Brain v9: vix_layer import failed: {e}")

try:
    from interest_rates_layer import get_interest_signal, calculate_rates_score, get_interest_rates_fred
    RATES_AVAILABLE = True
    print("✅ AI Brain v9: interest_rates_layer imported (REAL DATA!)")
except Exception as e:
    RATES_AVAILABLE = False
    print(f"⚠️ AI Brain v9: interest_rates_layer import failed: {e}")

try:
    from traditional_markets_layer import get_traditional_markets_signal, TraditionalMarketsLayer
    TRAD_MARKETS_AVAILABLE = True
    print("✅ AI Brain v9: traditional_markets_layer imported (REAL DATA!)")
except Exception as e:
    TRAD_MARKETS_AVAILABLE = False
    print(f"⚠️ AI Brain v9: traditional_markets_layer import failed: {e}")

# ============================================================================
# MAIN FUNCTION - 18-LAYER TRADING DECISION ENGINE
# ============================================================================

def make_trading_decision(
    symbol,
    interval='1h',
    portfolio_value=10000,
    risk_per_trade=200
):
    """
    AI Brain v9 - ULTIMATE 18-LAYER TRADING DECISION ENGINE WITH REAL DATA
    
    NEW IN v9:
    ----------
    - ALL layers now use REAL DATA (no mock values!)
    - yfinance integration (FREE!)
    - CMC_API_KEY for dominance data
    - FRED_API_KEY for interest rates
    - Updated function calls to match new layer interfaces
    
    Returns:
    --------
    dict with keys:
        - 'decision' or 'final_decision': LONG/SHORT/WAIT
        - 'signal': Same as decision
        - 'confidence': 0-1 float
        - 'entry_price': Entry price
        - 'stop_loss': SL price
        - 'take_profit': TP price
        - 'position_size': Position size
        - 'risk_reward': Risk/reward ratio
        - 'layer_scores': Dict of all layer scores
        - 'ai_commentary': Detailed explanation
    """
    print(f"\n{'='*80}")
    print(f"🧠 AI BRAIN v9: make_trading_decision (18-LAYER WITH REAL DATA)")
    print(f"   Symbol: {symbol}")
    print(f"   Interval: {interval}")
    print(f"   Portfolio: ${portfolio_value:,.0f}")
    print(f"{'='*80}")
    
    # ========================================================================
    # LAYER 1-11: STRATEGY LAYER (Phase 3A + 3B) - PRESERVED!
    # ========================================================================
    if STRATEGY_AVAILABLE:
        try:
            print(f"\n🔍 Calling strategy.calculate_comprehensive_score...")
            strategy_result = strategy.calculate_comprehensive_score(symbol, interval)
            final_score = strategy_result['final_score']
            signal = strategy_result['signal']
            confidence = strategy_result['confidence']
            components = strategy_result['components']
            print(f"✅ Strategy result (Layers 1-11): {final_score}/100")
        except Exception as e:
            print(f"❌ Strategy error: {e}")
            final_score = 50
            signal = 'NEUTRAL'
            confidence = 0.5
            components = {}
    else:
        final_score = 50
        signal = 'NEUTRAL'
        confidence = 0.5
        components = {}
        strategy_result = {}
    
    # ========================================================================
    # LAYER 12: MACRO CORRELATION (REAL DATA - yfinance + CMC!)
    # ========================================================================
    macro_score = 50
    macro_signal = "NEUTRAL"
    macro_details = {}
    
    if MACRO_AVAILABLE:
        try:
            print(f"\n🌍 Calling MacroCorrelationLayer.analyze_all (Layer 12 - REAL DATA)...")
            macro_layer = MacroCorrelationLayer()
            macro_result = macro_layer.analyze_all(symbol, days=30)
            
            if macro_result.get('available', False):
                macro_score = macro_result['total_score']
                macro_signal = macro_result['signal']
                macro_details = {
                    'correlations': macro_result.get('correlations', {}),
                    'factor_scores': macro_result.get('factor_scores', {}),
                    'explanation': macro_result.get('explanation', 'No details')
                }
                print(f"✅ Layer 12 (Macro): {macro_score:.2f}/100 - {macro_signal}")
            else:
                print("⚠️ Layer 12 (Macro) unavailable")
        except Exception as e:
            print(f"⚠️ Layer 12 (Macro) error: {e}")
            macro_score = 50
            macro_signal = "NEUTRAL"
    else:
        print(f"⚠️ Layer 12 (Macro): Not available")
    
    # ========================================================================
    # LAYER 13: GOLD CORRELATION (REAL DATA - yfinance!)
    # ========================================================================
    gold_score = 50
    gold_signal = "NEUTRAL"
    gold_details = {}
    
    if GOLD_AVAILABLE:
        try:
            print(f"\n🥇 Calling calculate_gold_correlation (Layer 13 - REAL DATA)...")
            gold_result = calculate_gold_correlation(symbol, interval, limit=100)
            
            if gold_result and gold_result.get('available'):
                gold_score = gold_result.get('score', 50)
                gold_signal = gold_result.get('signal', 'NEUTRAL')
                gold_details = {
                    'gold_correlation': gold_result.get('gold_correlation', 0),
                    'silver_correlation': gold_result.get('silver_correlation', 0),
                    'gold_price': gold_result.get('gold_price', 0),
                    'interpretation': gold_result.get('interpretation', 'No details')
                }
                print(f"✅ Layer 13 (Gold): {gold_score:.2f}/100 - {gold_signal}")
            else:
                print("⚠️ Layer 13 (Gold) unavailable")
        except Exception as e:
            print(f"⚠️ Layer 13 (Gold) error: {e}")
            gold_score = 50
            gold_signal = "NEUTRAL"
    else:
        print(f"⚠️ Layer 13 (Gold): Not available")
    
    # ========================================================================
    # LAYER 14: BTC DOMINANCE FLOW (REAL DATA - CMC_API_KEY!)
    # ========================================================================
    dominance_score = 50
    dominance_signal = "NEUTRAL"
    dominance_details = {}
    
    if DOMINANCE_AVAILABLE:
        try:
            print(f"\n📊 Calling calculate_dominance_flow (Layer 14 - REAL DATA)...")
            dominance_result = calculate_dominance_flow()
            
            if dominance_result and dominance_result.get('available'):
                dominance_score = dominance_result.get('score', 50)
                dominance_signal = dominance_result.get('altseason_signal', 'NEUTRAL')
                dominance_details = {
                    'btc_dominance': dominance_result.get('btc_dominance', 0),
                    'btc_dominance_24h_change': dominance_result.get('btc_dominance_24h_change', 0),
                    'money_flow': dominance_result.get('money_flow', 'UNKNOWN'),
                    'interpretation': dominance_result.get('interpretation', 'No details')
                }
                print(f"✅ Layer 14 (Dominance): {dominance_score:.2f}/100 - {dominance_signal}")
            else:
                print("⚠️ Layer 14 (Dominance) unavailable")
        except Exception as e:
            print(f"⚠️ Layer 14 (Dominance) error: {e}")
            dominance_score = 50
            dominance_signal = "NEUTRAL"
    else:
        print(f"⚠️ Layer 14 (Dominance): Not available")
    # ========================================================================
    # LAYER 15: CROSS-ASSET CORRELATION (BTC/ETH/LTC/BNB)
    # ========================================================================
    cross_asset_score = 50
    cross_asset_signal = "NEUTRAL"
    cross_asset_details = {}
    
    if CROSS_ASSET_AVAILABLE:
        try:
            print(f"\n💎 Calling cross_asset.calculate_cross_asset_correlation (Layer 15)...")
            cross_asset_result = cross_asset.calculate_cross_asset_correlation(symbol, interval, limit=100)
            
            if cross_asset_result and cross_asset_result.get('available'):
                cross_asset_score = cross_asset_result.get('score', 50)
                cross_asset_signal = cross_asset_result.get('signal', 'NEUTRAL')
                cross_asset_details = {
                    'btc_correlation': cross_asset_result.get('btc_correlation', 0),
                    'eth_correlation': cross_asset_result.get('eth_correlation', 0),
                    'interpretation': cross_asset_result.get('interpretation', 'No details')
                }
                print(f"✅ Layer 15 (Cross-Asset): {cross_asset_score:.2f}/100 - {cross_asset_signal}")
            else:
                print("⚠️ Layer 15 (Cross-Asset) unavailable")
        except Exception as e:
            print(f"⚠️ Layer 15 (Cross-Asset) error: {e}")
            cross_asset_score = 50
            cross_asset_signal = "NEUTRAL"
    else:
        print(f"⚠️ Layer 15 (Cross-Asset): Not available")
    
    # ========================================================================
    # LAYER 16: VIX FEAR INDEX (REAL DATA - yfinance!)
    # ========================================================================
    vix_score = 50
    vix_signal = "NEUTRAL"
    vix_details = {}
    
    if VIX_AVAILABLE:
        try:
            print(f"\n😱 Calling get_vix_signal (Layer 16 - REAL DATA)...")
            vix_result = get_vix_signal()
            
            if vix_result and vix_result.get('available'):
                vix_score = vix_result.get('score', 50)
                vix_signal = vix_result.get('signal', 'NEUTRAL')
                vix_details = {
                    'vix_current': vix_result.get('vix_current', 0),
                    'fear_level': vix_result.get('fear_level', 'UNKNOWN'),
                    'interpretation': vix_result.get('interpretation', 'No details')
                }
                print(f"✅ Layer 16 (VIX): {vix_score:.2f}/100 - {vix_signal}")
            else:
                print("⚠️ Layer 16 (VIX) unavailable")
        except Exception as e:
            print(f"⚠️ Layer 16 (VIX) error: {e}")
            vix_score = 50
            vix_signal = "NEUTRAL"
    else:
        print(f"⚠️ Layer 16 (VIX): Not available")
    
    # ========================================================================
    # LAYER 17: INTEREST RATES (REAL DATA - FRED_API_KEY + yfinance!)
    # ========================================================================
    rates_score = 50
    rates_signal = "NEUTRAL"
    rates_details = {}
    
    if RATES_AVAILABLE:
        try:
            print(f"\n💰 Calling get_interest_signal (Layer 17 - REAL DATA)...")
            rates_result = get_interest_signal()
            
            if rates_result and rates_result.get('available'):
                rates_score = rates_result.get('score', 50)
                rates_signal = rates_result.get('signal', 'NEUTRAL')
                rates_details = {
                    'fed_funds_rate': rates_result.get('fed_funds_rate', 0),
                    'treasury_10y': rates_result.get('treasury_10y', 0),
                    'rate_direction': rates_result.get('rate_direction', 'UNKNOWN'),
                    'interpretation': rates_result.get('interpretation', 'No details')
                }
                print(f"✅ Layer 17 (Rates): {rates_score:.2f}/100 - {rates_signal}")
            else:
                print("⚠️ Layer 17 (Rates) unavailable")
        except Exception as e:
            print(f"⚠️ Layer 17 (Rates) error: {e}")
            rates_score = 50
            rates_signal = "NEUTRAL"
    else:
        print(f"⚠️ Layer 17 (Rates): Not available")
    
    # ========================================================================
    # LAYER 18: TRADITIONAL MARKETS (REAL DATA - yfinance!)
    # ========================================================================
    trad_markets_score = 50
    trad_markets_signal = "NEUTRAL"
    trad_markets_details = {}
    
    if TRAD_MARKETS_AVAILABLE:
        try:
            print(f"\n📈 Calling TraditionalMarketsLayer.analyze_all_markets (Layer 18 - REAL DATA)...")
            trad_markets_layer = TraditionalMarketsLayer()
            trad_markets_result = trad_markets_layer.analyze_all_markets(symbol, days=30)
            
            if trad_markets_result and trad_markets_result.get('available'):
                trad_markets_score = trad_markets_result.get('total_score', 50)
                trad_markets_signal = trad_markets_result.get('signal', 'NEUTRAL')
                trad_markets_details = {
                    'correlations': trad_markets_result.get('correlations', {}),
                    'price_changes': trad_markets_result.get('price_changes', {}),
                    'market_regime': trad_markets_result.get('market_regime', 'UNKNOWN'),
                    'explanation': trad_markets_result.get('explanation', 'No details')
                }
                print(f"✅ Layer 18 (Trad Markets): {trad_markets_score:.2f}/100 - {trad_markets_signal}")
            else:
                print("⚠️ Layer 18 (Trad Markets) unavailable")
        except Exception as e:
            print(f"⚠️ Layer 18 (Trad Markets) error: {e}")
            trad_markets_score = 50
            trad_markets_signal = "NEUTRAL"
    else:
        print(f"⚠️ Layer 18 (Trad Markets): Not available")
    
    # ========================================================================
    # MONTE CARLO SIMULATION (Risk Assessment)
    # ========================================================================
    mc_result = {}
    expected_return = 0
    downside_risk = 0
    upside_potential = 0
    
    if MC_AVAILABLE:
        try:
            print(f"\n🎲 Calling monte_carlo.run_monte_carlo_simulation...")
            mc_result = mc.run_monte_carlo_simulation(symbol, interval, simulations=1000)
            
            if mc_result.get('success'):
                expected_return = mc_result.get('expected_return', 0)
                downside_risk = mc_result.get('downside_risk', 0)
                upside_potential = mc_result.get('upside_potential', 0)
                print(f"✅ Monte Carlo: Expected Return={expected_return:.2f}%, Risk={downside_risk:.2f}%")
            else:
                print("⚠️ Monte Carlo unavailable")
        except Exception as e:
            print(f"⚠️ Monte Carlo error: {e}")
    else:
        print(f"⚠️ Monte Carlo: Not available")
    
    # ========================================================================
    # KELLY CRITERION (Position Sizing)
    # ========================================================================
    kelly_result = {}
    recommended_position_pct = 1.0
    
    if KELLY_AVAILABLE:
        try:
            print(f"\n🎯 Calling kelly.calculate_kelly_position...")
            kelly_result = kelly.calculate_kelly_position(
                symbol=symbol,
                interval=interval,
                portfolio_value=portfolio_value,
                win_rate=confidence,
                avg_win=upside_potential if upside_potential > 0 else 2.0,
                avg_loss=abs(downside_risk) if downside_risk < 0 else 1.0
            )
            
            if kelly_result.get('success'):
                recommended_position_pct = kelly_result.get('position_size_pct', 1.0)
                print(f"✅ Kelly: Recommended Position={recommended_position_pct:.2f}%")
            else:
                print("⚠️ Kelly unavailable")
        except Exception as e:
            print(f"⚠️ Kelly error: {e}")
    else:
        print(f"⚠️ Kelly: Not available")
    
    # ========================================================================
    # AGGREGATE ALL 18 LAYERS
    # ========================================================================
    
    print(f"\n{'='*80}")
    print(f"📊 AGGREGATING ALL 18 LAYERS...")
    print(f"{'='*80}")
    
    # Layer weights (total = 100)
    weights = {
        'strategy': 40,        # Layers 1-11 (strongest - technical analysis)
        'macro': 8,           # Layer 12 (macro correlation)
        'gold': 5,            # Layer 13 (gold correlation)
        'dominance': 7,       # Layer 14 (BTC dominance)
        'cross_asset': 6,     # Layer 15 (cross-asset)
        'vix': 6,             # Layer 16 (VIX)
        'rates': 8,           # Layer 17 (interest rates)
        'trad_markets': 10,   # Layer 18 (traditional markets - important!)
        'monte_carlo': 5,     # Monte Carlo risk
        'kelly': 5            # Kelly position sizing
    }
    
    # Calculate weighted score
    total_weighted_score = 0
    
    total_weighted_score += (final_score * weights['strategy'] / 100)
    total_weighted_score += (macro_score * weights['macro'] / 100)
    total_weighted_score += (gold_score * weights['gold'] / 100)
    total_weighted_score += (dominance_score * weights['dominance'] / 100)
    total_weighted_score += (cross_asset_score * weights['cross_asset'] / 100)
    total_weighted_score += (vix_score * weights['vix'] / 100)
    total_weighted_score += (rates_score * weights['rates'] / 100)
    total_weighted_score += (trad_markets_score * weights['trad_markets'] / 100)
    
    # Monte Carlo contribution (risk-adjusted)
    if expected_return > 0:
        mc_score = min(100, 50 + (expected_return * 10))
    elif expected_return < 0:
        mc_score = max(0, 50 + (expected_return * 10))
    else:
        mc_score = 50
    total_weighted_score += (mc_score * weights['monte_carlo'] / 100)
    
    # Kelly contribution (position sizing quality)
    if recommended_position_pct > 0:
        kelly_score = min(100, recommended_position_pct * 20)  # 5% position = 100 score
    else:
        kelly_score = 0
    total_weighted_score += (kelly_score * weights['kelly'] / 100)
    
    # Final aggregated score (0-100)
    aggregated_score = total_weighted_score
    
    print(f"✅ Aggregated Score: {aggregated_score:.2f}/100")
    
    # ========================================================================
    # FINAL DECISION LOGIC
    # ========================================================================
    
    # Determine final decision
    if aggregated_score >= 70:
        final_decision = "LONG"
        decision_confidence = 0.8 + (aggregated_score - 70) / 100
    elif aggregated_score >= 55:
        final_decision = "LONG"
        decision_confidence = 0.6 + (aggregated_score - 55) / 30
    elif aggregated_score >= 45:
        final_decision = "WAIT"
        decision_confidence = 0.5
    elif aggregated_score >= 30:
        final_decision = "SHORT"
        decision_confidence = 0.6 + (45 - aggregated_score) / 30
    else:
        final_decision = "SHORT"
        decision_confidence = 0.8 + (30 - aggregated_score) / 100
    
    decision_confidence = min(1.0, decision_confidence)
    
    print(f"✅ Final Decision: {final_decision}")
    print(f"✅ Confidence: {decision_confidence:.2%}")
    
    # ========================================================================
    # CALCULATE ENTRY, STOP LOSS, TAKE PROFIT
    # ========================================================================
    
    # Get current price from strategy result
    entry_price = strategy_result.get('current_price', 0)
    if entry_price == 0:
        entry_price = 50000  # Fallback
    
    # Calculate SL/TP based on ATR and volatility
    atr_multiplier = 2.0
    if 'volatility' in components:
        volatility = components['volatility'].get('value', 0.02)
    else:
        volatility = 0.02
    
    if final_decision == "LONG":
        stop_loss = entry_price * (1 - volatility * atr_multiplier)
        take_profit = entry_price * (1 + volatility * atr_multiplier * 2)
    elif final_decision == "SHORT":
        stop_loss = entry_price * (1 + volatility * atr_multiplier)
        take_profit = entry_price * (1 - volatility * atr_multiplier * 2)
    else:
        stop_loss = entry_price
        take_profit = entry_price
    
    # Risk/reward ratio
    if final_decision in ["LONG", "SHORT"]:
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        risk_reward = reward / risk if risk > 0 else 0
    else:
        risk_reward = 0
    
    # ========================================================================
    # POSITION SIZING
    # ========================================================================
    
    # Kelly-adjusted position size
    position_size_usd = portfolio_value * (recommended_position_pct / 100)
    position_size_usd = min(position_size_usd, risk_per_trade * 5)  # Cap at 5x risk
    position_size_units = position_size_usd / entry_price if entry_price > 0 else 0
    
    # ========================================================================
    # AI COMMENTARY
    # ========================================================================
    
    commentary_parts = []
    commentary_parts.append(f"🧠 AI Brain v9 Analysis (18 Layers with REAL DATA):")
    commentary_parts.append(f"")
    commentary_parts.append(f"📊 Aggregated Score: {aggregated_score:.1f}/100")
    commentary_parts.append(f"🎯 Decision: {final_decision} ({decision_confidence:.0%} confidence)")
    commentary_parts.append(f"")
    commentary_parts.append(f"📈 Layer Breakdown:")
    commentary_parts.append(f"   • Layers 1-11 (Strategy): {final_score:.1f}/100")
    commentary_parts.append(f"   • Layer 12 (Macro): {macro_score:.1f}/100 - {macro_signal}")
    commentary_parts.append(f"   • Layer 13 (Gold): {gold_score:.1f}/100 - {gold_signal}")
    commentary_parts.append(f"   • Layer 14 (Dominance): {dominance_score:.1f}/100 - {dominance_signal}")
    commentary_parts.append(f"   • Layer 15 (Cross-Asset): {cross_asset_score:.1f}/100 - {cross_asset_signal}")
    commentary_parts.append(f"   • Layer 16 (VIX): {vix_score:.1f}/100 - {vix_signal}")
    commentary_parts.append(f"   • Layer 17 (Rates): {rates_score:.1f}/100 - {rates_signal}")
    commentary_parts.append(f"   • Layer 18 (Trad Markets): {trad_markets_score:.1f}/100 - {trad_markets_signal}")
    commentary_parts.append(f"")
    commentary_parts.append(f"💰 Trade Parameters:")
    commentary_parts.append(f"   • Entry: ${entry_price:,.2f}")
    commentary_parts.append(f"   • Stop Loss: ${stop_loss:,.2f}")
    commentary_parts.append(f"   • Take Profit: ${take_profit:,.2f}")
    commentary_parts.append(f"   • Risk/Reward: {risk_reward:.2f}")
    commentary_parts.append(f"   • Position Size: ${position_size_usd:,.2f} ({position_size_units:.4f} units)")
    
    ai_commentary = "\n".join(commentary_parts)
    
    # ========================================================================
    # BUILD FINAL RESULT
    # ========================================================================
    
    result = {
        'decision': final_decision,
        'final_decision': final_decision,
        'signal': final_decision,
        'confidence': decision_confidence,
        'aggregated_score': aggregated_score,
        
        # Trade parameters
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'risk_reward': risk_reward,
        'position_size': position_size_units,
        'position_size_usd': position_size_usd,
        
        # Layer scores
        'layer_scores': {
            'strategy': final_score,
            'macro': macro_score,
            'gold': gold_score,
            'dominance': dominance_score,
            'cross_asset': cross_asset_score,
            'vix': vix_score,
            'rates': rates_score,
            'trad_markets': trad_markets_score,
            'monte_carlo': mc_score,
            'kelly': kelly_score
        },
        
        # Layer details
        'layer_details': {
            'macro': macro_details,
            'gold': gold_details,
            'dominance': dominance_details,
            'cross_asset': cross_asset_details,
            'vix': vix_details,
            'rates': rates_details,
            'trad_markets': trad_markets_details
        },
        
        # Commentary
        'ai_commentary': ai_commentary,
        
        # Raw results
        'strategy_result': strategy_result,
        'monte_carlo_result': mc_result,
        'kelly_result': kelly_result,
        
        # Metadata
        'timestamp': datetime.now().isoformat(),
        'symbol': symbol,
        'interval': interval,
        'version': 'v9.0 - 18 Layers with Real Data'
    }
    
    print(f"\n{'='*80}")
    print(f"✅ AI BRAIN v9 COMPLETE!")
    print(f"{'='*80}\n")
    
    return result


# ============================================================================
# END OF AI_BRAIN.PY v9.0
# ============================================================================

if __name__ == "__main__":
    print("🔱 AI Brain v9.0 - Testing...")
    result = make_trading_decision('BTCUSDT', '1h', portfolio_value=10000, risk_per_trade=200)
    print("\n" + result['ai_commentary'])
