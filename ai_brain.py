"""
DEMIR AI Trading Bot - AI Brain v4 FULL
Phase 3A + Phase 3B: Complete Integration
Tarih: 31 Ekim 2025

ENTEGRASYON:
- Phase 3A: Volume Profile, Pivot, Fibonacci, VWAP, News, Monte Carlo, Kelly
- Phase 3B: GARCH, Markov Regime, HVI, Volatility Squeeze

Eternal Continuity Protocol: Tüm özellikler korundu!
"""

from datetime import datetime

# ============================================================================
# Import layers
# ============================================================================
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


def make_trading_decision(
    symbol,
    interval='1h',
    portfolio_value=10000,
    risk_per_trade=200
):
    """
    AI Brain v4 - Final trading decision
    Phase 3A + Phase 3B full integration with detailed breakdown
    """
    
    print(f"\n{'='*80}")
    print(f"🧠 AI BRAIN v4: make_trading_decision")
    print(f"   Symbol: {symbol}")
    print(f"   Interval: {interval}")
    print(f"   Portfolio: ${portfolio_value:,.0f}")
    print(f"{'='*80}")
    
    # ========================================================================
    # 1. Strategy Layer v4 (Phase 3A + 3B Comprehensive Score)
    # ========================================================================
    if STRATEGY_AVAILABLE:
        try:
            print(f"\n🔍 Calling strategy.calculate_comprehensive_score...")
            strategy_result = strategy.calculate_comprehensive_score(symbol, interval)
            
            final_score = strategy_result['final_score']
            signal = strategy_result['signal']
            confidence = strategy_result['confidence']
            components = strategy_result['components']
            
            print(f"✅ Strategy result received:")
            print(f"   Final Score: {final_score}")
            print(f"   Signal: {signal}")
            print(f"   Confidence: {confidence}")
            
        except Exception as e:
            print(f"❌ Strategy error: {e}")
            import traceback
            traceback.print_exc()
            
            final_score = 50
            signal = 'NEUTRAL'
            confidence = 0.5
            components = {}
    else:
        final_score = 50
        signal = 'NEUTRAL'
        confidence = 0.5
        components = {}
    
    # ========================================================================
    # 2. Monte Carlo Risk Assessment
    # ========================================================================
    if MC_AVAILABLE:
        try:
            print(f"\n🎲 Calling monte_carlo.get_monte_carlo_risk_assessment...")
            mc_assessment = mc.get_monte_carlo_risk_assessment(
                win_rate=0.55,
                avg_win=2.0,
                avg_loss=1.0,
                num_trades=100,
                num_simulations=1000
            )
            
            risk_of_ruin = mc_assessment['risk_assessment']['risk_of_ruin_pct']
            max_drawdown = mc_assessment['drawdown_assessment']['worst_case_pct']
            sharpe = mc_assessment['sharpe_assessment']['ratio']
            
            print(f"✅ Monte Carlo result:")
            print(f"   Risk of Ruin: {risk_of_ruin}%")
            print(f"   Max DD: {max_drawdown}%")
            print(f"   Sharpe: {sharpe}")
            
        except Exception as e:
            print(f"⚠️ Monte Carlo error: {e}")
            risk_of_ruin = 5.0
            max_drawdown = 20.0
            sharpe = 1.5
    else:
        risk_of_ruin = 5.0
        max_drawdown = 20.0
        sharpe = 1.5
    
    # ========================================================================
    # 3. Kelly Criterion Position Sizing
    # ========================================================================
    if KELLY_AVAILABLE:
        try:
            print(f"\n💰 Calling kelly.calculate_dynamic_kelly...")
            kelly_result = kelly.calculate_dynamic_kelly(
                win_rate=0.55,
                avg_win=2.0,
                avg_loss=1.0,
                confidence=confidence,
                portfolio_value=portfolio_value
            )
            
            position_size_usd = kelly_result['position_size_usd']
            position_size_pct = kelly_result['position_size_pct']
            risk_amount = kelly_result['risk_amount_usd']
            
            print(f"✅ Kelly result:")
            print(f"   Position: ${position_size_usd:,.2f} ({position_size_pct}%)")
            print(f"   Risk: ${risk_amount:,.2f}")
            
        except Exception as e:
            print(f"⚠️ Kelly error: {e}")
            position_size_usd = risk_per_trade
            position_size_pct = (risk_per_trade / portfolio_value) * 100
            risk_amount = risk_per_trade
    else:
        position_size_usd = risk_per_trade
        position_size_pct = (risk_per_trade / portfolio_value) * 100
        risk_amount = risk_per_trade
    
    # ========================================================================
    # 4. Build Detailed Description (Phase 3A + 3B)
    # ========================================================================
    print(f"\n📋 Building detailed description...")
    description_parts = []
    
    # Phase 3A Components
    if components.get('volume_profile', {}).get('available'):
        vp = components['volume_profile']
        description_parts.append(f"📊 **Volume Profile:** {vp.get('zone', 'N/A')} - {vp.get('description', 'N/A')}")
    else:
        description_parts.append("📊 **Volume Profile:** Not available")
    
    if components.get('pivot_points', {}).get('available'):
        pp = components['pivot_points']
        description_parts.append(f"📍 **Pivot Points:** {pp.get('zone', 'N/A')} - {pp.get('description', 'N/A')}")
    else:
        description_parts.append("📍 **Pivot Points:** Not available")
    
    if components.get('fibonacci', {}).get('available'):
        fib = components['fibonacci']
        description_parts.append(f"📐 **Fibonacci:** {fib.get('level', 'N/A')} - {fib.get('description', 'N/A')}")
    else:
        description_parts.append("📐 **Fibonacci:** Not available")
    
    if components.get('vwap', {}).get('available'):
        vwap = components['vwap']
        description_parts.append(f"📈 **VWAP:** {vwap.get('zone', 'N/A')} - {vwap.get('description', 'N/A')}")
    else:
        description_parts.append("📈 **VWAP:** Not available")
    
    # Phase 3B Components (NEW!)
    if components.get('garch_volatility', {}).get('available'):
        garch = components['garch_volatility']
        vol_level = garch.get('volatility_level', 'UNKNOWN')
        forecast_vol = garch.get('forecast_vol', 0)
        description_parts.append(f"🎲 **GARCH Forecast:** Expected Vol: {forecast_vol:.2f}% (Next 24h) - {vol_level} volatility")
    else:
        description_parts.append("🎲 **GARCH Forecast:** Not available")
    
    if components.get('markov_regime', {}).get('available'):
        markov = components['markov_regime']
        regime = markov.get('regime', 'UNKNOWN')
        direction = markov.get('direction', 'NEUTRAL')
        markov_conf = markov.get('confidence', 0)
        description_parts.append(f"🔄 **Market Regime:** {regime} ({direction}) - Confidence: {markov_conf*100:.0f}%")
    else:
        description_parts.append("🔄 **Market Regime:** Not available")
    
    if components.get('hvi', {}).get('available'):
        hvi = components['hvi']
        zscore = hvi.get('hvi_zscore', 0)
        vol_level = hvi.get('volatility_level', 'UNKNOWN')
        description_parts.append(f"📊 **HVI Index:** {zscore:.2f}σ ({vol_level}) - Historical volatility analysis")
    else:
        description_parts.append("📊 **HVI Index:** Not available")
    
    if components.get('volatility_squeeze', {}).get('available'):
        squeeze = components['volatility_squeeze']
        status = squeeze.get('squeeze_status', 'UNKNOWN')
        duration = squeeze.get('squeeze_duration', 0)
        breakout = squeeze.get('breakout_direction', None)
        
        if breakout:
            description_parts.append(f"🎯 **Vol Squeeze:** {status} ({duration}p) - {breakout} breakout detected")
        else:
            description_parts.append(f"🎯 **Vol Squeeze:** {status} ({duration}p)")
    else:
        description_parts.append("🎯 **Vol Squeeze:** Not available")
    
    # Monte Carlo & Kelly
    description_parts.append(f"🎲 **Monte Carlo:** Risk of Ruin: {risk_of_ruin:.2f}% | Max DD: -{max_drawdown:.2f}%")
    description_parts.append(f"💰 **Kelly:** Optimal: ${position_size_usd:,.2f} ({position_size_pct:.2f}%)")
    
    detailed_description = "\n\n".join(description_parts)
    
    print(f"✅ Detailed description built ({len(description_parts)} components)")
    
    # ========================================================================
    # 5. Risk Adjustments (Phase 3A + 3B)
    # ========================================================================
    print(f"\n⚙️ Applying risk adjustments...")
    
    # Volume Profile adjustments
    if components.get('volume_profile', {}).get('available'):
        vp_zone = components['volume_profile'].get('zone', 'UNKNOWN')
        if vp_zone == 'POC':
            position_size_usd *= 0.8
            risk_amount *= 0.8
            print(f"   📉 VP POC: Position reduced by 20%")
        elif vp_zone == 'LVN':
            position_size_usd *= 1.2
            risk_amount *= 1.2
            print(f"   📈 VP LVN: Position increased by 20%")
    
    # VWAP adjustments
    if components.get('vwap', {}).get('available'):
        vwap_zone = components['vwap'].get('zone', 'UNKNOWN')
        if vwap_zone in ['+3STD', '-3STD']:
            position_size_usd *= 0.7
            risk_amount *= 0.7
            print(f"   📉 VWAP extreme: Position reduced by 30%")
    
    # GARCH volatility adjustments (NEW!)
    if components.get('garch_volatility', {}).get('available'):
        vol_level = components['garch_volatility'].get('volatility_level', 'MODERATE')
        if vol_level == 'EXTREME':
            position_size_usd *= 0.5
            risk_amount *= 0.5
            print(f"   ⚠️ GARCH EXTREME vol: Position halved")
        elif vol_level == 'HIGH':
            position_size_usd *= 0.75
            risk_amount *= 0.75
            print(f"   ⚠️ GARCH HIGH vol: Position reduced by 25%")
    
    # Markov regime adjustments (NEW!)
    if components.get('markov_regime', {}).get('available'):
        regime = components['markov_regime'].get('regime', 'RANGE')
        if regime == 'HIGH_VOL':
            position_size_usd *= 0.6
            risk_amount *= 0.6
            print(f"   ⚠️ Markov HIGH_VOL regime: Position reduced by 40%")
    
    # Monte Carlo risk-of-ruin adjustment
    if risk_of_ruin > 10:
        position_size_usd *= 0.5
        risk_amount *= 0.5
        print(f"   ⚠️ High Risk of Ruin: Position halved")
    
    # Max position cap (10% of portfolio)
    max_position = portfolio_value * 0.10
    if position_size_usd > max_position:
        position_size_usd = max_position
        print(f"   🚫 Position capped at 10% of portfolio")
    
    # ========================================================================
    # 6. Entry/Stop/Target Calculation (ALWAYS CALCULATE!)
    # ========================================================================
    try:
        import requests
        url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            current_price = float(response.json()['price'])
            print(f"\n✅ Current price fetched: ${current_price:,.2f}")
        else:
            current_price = None
    except Exception as e:
        current_price = None
        print(f"\n❌ Price fetch error: {e}")
    
    if current_price:
        atr_multiplier_stop = 2.0
        atr_multiplier_target = 3.0
        atr = current_price * 0.015
        
        entry_price = current_price
        
        if signal == 'LONG':
            stop_loss = entry_price - (atr * atr_multiplier_stop)
            take_profit = entry_price + (atr * atr_multiplier_target)
        elif signal == 'SHORT':
            stop_loss = entry_price + (atr * atr_multiplier_stop)
            take_profit = entry_price - (atr * atr_multiplier_target)
        else:  # NEUTRAL - still calculate symmetric
            stop_loss = entry_price - (atr * atr_multiplier_stop)
            take_profit = entry_price + (atr * atr_multiplier_target)
        
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        risk_reward = reward / risk if risk > 0 else 0
        
        print(f"✅ Stop/Target calculated:")
        print(f"   Entry: ${entry_price:,.2f}")
        print(f"   Stop: ${stop_loss:,.2f}")
        print(f"   Target: ${take_profit:,.2f}")
        print(f"   R/R: 1:{risk_reward:.2f}")
    else:
        entry_price = None
        stop_loss = None
        take_profit = None
        risk_reward = 0
    
    # ========================================================================
    # 7. Final Decision
    # ========================================================================
    decision = 'WAIT'
    
    if signal == 'LONG' and confidence >= 0.6 and final_score >= 65:
        decision = 'LONG'
    elif signal == 'SHORT' and confidence >= 0.6 and final_score <= 35:
        decision = 'SHORT'
    else:
        decision = 'WAIT'
    
    if risk_of_ruin > 15:
        decision = 'WAIT'
        reason = f"Risk of Ruin too high: {risk_of_ruin}%"
    elif max_drawdown > 40:
        decision = 'WAIT'
        reason = f"Max Drawdown too high: {max_drawdown}%"
    elif confidence < 0.5:
        decision = 'WAIT'
        reason = f"Low confidence: {confidence*100:.0f}%"
    else:
        reason = f"Score: {final_score}/100, Confidence: {confidence*100:.0f}%"
    
    print(f"\n🎯 FINAL DECISION: {decision}")
    print(f"   Reason: {reason}")
    print(f"{'='*80}\n")
    
    return {
        'symbol': symbol,
        'interval': interval,
        'decision': decision,
        'signal': signal,
        'confidence': round(confidence, 2),
        'final_score': final_score,
        'entry_price': round(entry_price, 2) if entry_price else None,
        'stop_loss': round(stop_loss, 2) if stop_loss else None,
        'take_profit': round(take_profit, 2) if take_profit else None,
        'risk_reward': round(risk_reward, 2) if risk_reward else 0,
        'position_size_usd': round(position_size_usd, 2),
        'position_size_pct': round(position_size_pct, 2),
        'risk_amount_usd': round(risk_amount, 2),
        'risk_metrics': {
            'risk_of_ruin': risk_of_ruin,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe
        },
        'reason': reason,
        'detailed_description': detailed_description,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# Test
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 DEMIR AI - AI Brain v4 (Phase 3A + 3B) Test")
    print("=" * 80)
    
    symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
    
    for symbol in symbols:
        decision = make_trading_decision(
            symbol=symbol,
            interval='1h',
            portfolio_value=10000,
            risk_per_trade=200
        )
        
        print(f"\n✅ {symbol} FINAL DECISION:")
        print(f"   Decision: {decision['decision']} {decision['signal']}")
        print(f"   Confidence: {decision['confidence']*100:.0f}%")
        print(f"   Score: {decision['final_score']}/100")
        
        if decision['entry_price']:
            print(f"   Entry: ${decision['entry_price']:,.2f}")
            print(f"   Stop: ${decision['stop_loss']:,.2f}")
            print(f"   Target: ${decision['take_profit']:,.2f}")
            print(f"   R/R: 1:{decision['risk_reward']:.2f}")
    
    print("\n" + "=" * 80)
