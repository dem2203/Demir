"""
DEMIR AI Trading Bot - AI Brain v3 ENHANCED
Phase 3A: Detailed Output with All Indicators
Tarih: 31 Ekim 2025

ENHANCED OUTPUT:
- Volume Profile zone details
- Pivot Points levels
- Fibonacci levels
- VWAP deviation info
- Monte Carlo metrics
- Kelly sizing
"""

from datetime import datetime

# Import layers
try:
    import strategy_layer_v3 as strategy
    STRATEGY_AVAILABLE = True
except:
    try:
        import strategy_layer as strategy
        STRATEGY_AVAILABLE = True
    except:
        STRATEGY_AVAILABLE = False

try:
    import monte_carlo_layer as mc
    MC_AVAILABLE = True
except:
    MC_AVAILABLE = False

try:
    import kelly_enhanced_layer as kelly
    KELLY_AVAILABLE = True
except:
    KELLY_AVAILABLE = False


def make_trading_decision(
    symbol,
    interval='1h',
    portfolio_value=10000,
    risk_per_trade=200
):
    """
    AI Brain - Final trading decision with DETAILED component breakdown
    """
    
    # 1. Strategy Layer v3 - Comprehensive score
    if STRATEGY_AVAILABLE:
        try:
            strategy_result = strategy.calculate_comprehensive_score(symbol, interval)
            final_score = strategy_result['final_score']
            signal = strategy_result['signal']
            confidence = strategy_result['confidence']
            components = strategy_result['components']
        except:
            # Fallback
            final_score = 50
            signal = 'NEUTRAL'
            confidence = 0.5
            components = {}
    else:
        final_score = 50
        signal = 'NEUTRAL'
        confidence = 0.5
        components = {}
    
    # 2. Monte Carlo risk assessment
    if MC_AVAILABLE:
        try:
            win_rate = 0.55
            avg_win = 2.0
            avg_loss = 1.0
            
            mc_assessment = mc.get_monte_carlo_risk_assessment(
                win_rate=win_rate,
                avg_win=avg_win,
                avg_loss=avg_loss,
                num_trades=100
            )
            
            risk_of_ruin = mc_assessment['risk_assessment']['risk_of_ruin_pct']
            max_drawdown = mc_assessment['drawdown_assessment']['worst_case_pct']
            sharpe = mc_assessment['sharpe_assessment']['ratio']
        except:
            risk_of_ruin = 5.0
            max_drawdown = 20.0
            sharpe = 1.5
    else:
        risk_of_ruin = 5.0
        max_drawdown = 20.0
        sharpe = 1.5
    
    # 3. Kelly Criterion position sizing
    if KELLY_AVAILABLE:
        try:
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
        except:
            position_size_usd = risk_per_trade
            position_size_pct = (risk_per_trade / portfolio_value) * 100
            risk_amount = risk_per_trade
    else:
        position_size_usd = risk_per_trade
        position_size_pct = (risk_per_trade / portfolio_value) * 100
        risk_amount = risk_per_trade
    
    # 4. Build detailed description text
    description_parts = []
    
    # Volume Profile
    if components.get('volume_profile', {}).get('available'):
        vp = components['volume_profile']
        zone = vp.get('zone', 'UNKNOWN')
        desc = vp.get('description', 'N/A')
        description_parts.append(f"📊 **Volume Profile:** {zone} - {desc}")
    else:
        description_parts.append("📊 **Volume Profile:** Not available")
    
    # Pivot Points
    if components.get('pivot_points', {}).get('available'):
        pp = components['pivot_points']
        zone = pp.get('zone', 'UNKNOWN')
        desc = pp.get('description', 'N/A')
        description_parts.append(f"📍 **Pivot Points:** {zone} - {desc}")
    else:
        description_parts.append("📍 **Pivot Points:** Not available")
    
    # Fibonacci
    if components.get('fibonacci', {}).get('available'):
        fib = components['fibonacci']
        level = fib.get('level', 'UNKNOWN')
        desc = fib.get('description', 'N/A')
        description_parts.append(f"📐 **Fibonacci:** {level} - {desc}")
    else:
        description_parts.append("📐 **Fibonacci:** Not available")
    
    # VWAP
    if components.get('vwap', {}).get('available'):
        vwap = components['vwap']
        zone = vwap.get('zone', 'UNKNOWN')
        desc = vwap.get('description', 'N/A')
        description_parts.append(f"📈 **VWAP:** {zone} - {desc}")
    else:
        description_parts.append("📈 **VWAP:** Not available")
    
    # Monte Carlo
    description_parts.append(f"🎲 **Monte Carlo:** Risk of Ruin: {risk_of_ruin:.2f}% | Max DD: -{max_drawdown:.2f}%")
    
    # Kelly
    description_parts.append(f"💰 **Kelly:** Optimal: ${position_size_usd:,.2f} ({position_size_pct:.2f}%)")
    
    # Combine all descriptions
    detailed_description = "\n\n".join(description_parts)
    
    # 5. Risk adjustments
    if components.get('volume_profile', {}).get('available'):
        vp_zone = components['volume_profile'].get('zone', 'UNKNOWN')
        
        if vp_zone == 'POC':
            position_size_usd *= 0.8
            risk_amount *= 0.8
        elif vp_zone == 'LVN':
            position_size_usd *= 1.2
            risk_amount *= 1.2
    
    if components.get('vwap', {}).get('available'):
        vwap_zone = components['vwap'].get('zone', 'UNKNOWN')
        
        if vwap_zone in ['+3STD', '-3STD']:
            position_size_usd *= 0.7
            risk_amount *= 0.7
    
    if risk_of_ruin > 10:
        position_size_usd *= 0.5
        risk_amount *= 0.5
    
    max_position = portfolio_value * 0.10
    if position_size_usd > max_position:
        position_size_usd = max_position
    
    # 6. Entry/Stop/Target calculation
    try:
        import requests
        url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            current_price = float(response.json()['price'])
        else:
            current_price = None
    except:
        current_price = None
    
    if current_price:
        atr_multiplier_stop = 2.0
        atr_multiplier_target = 3.0
        atr = current_price * 0.015
        
        if signal == 'LONG':
            entry_price = current_price
            stop_loss = entry_price - (atr * atr_multiplier_stop)
            take_profit = entry_price + (atr * atr_multiplier_target)
        elif signal == 'SHORT':
            entry_price = current_price
            stop_loss = entry_price + (atr * atr_multiplier_stop)
            take_profit = entry_price - (atr * atr_multiplier_target)
        else:
            entry_price = current_price
            stop_loss = None
            take_profit = None
        
        if stop_loss and take_profit:
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            risk_reward = reward / risk if risk > 0 else 0
        else:
            risk_reward = 0
    else:
        entry_price = None
        stop_loss = None
        take_profit = None
        risk_reward = 0
    
    # 7. Final decision
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
        'detailed_description': detailed_description,  # YENİ: Detaylı açıklama
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# Test fonksiyonu
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 DEMIR AI - AI Brain v3 Enhanced Test")
    print("=" * 80)
    
    symbol = 'BTCUSDT'
    interval = '1h'
    portfolio = 10000
    risk_per_trade = 200
    
    print(f"\n🧠 Making Trading Decision for {symbol}...")
    
    decision = make_trading_decision(
        symbol=symbol,
        interval=interval,
        portfolio_value=portfolio,
        risk_per_trade=risk_per_trade
    )
    
    print(f"\n✅ FINAL DECISION:")
    print(f"   Decision: {decision['decision']} {decision['signal']}")
    print(f"   Confidence: {decision['confidence']*100:.0f}%")
    print(f"   Score: {decision['final_score']}/100")
    
    print(f"\n📋 DETAILED DESCRIPTION:")
    print(decision['detailed_description'])
    
    print("\n" + "=" * 80)
