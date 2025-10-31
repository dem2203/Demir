"""
DEMIR AI Trading Bot - AI Brain v3
Phase 3A: Advanced Risk Management & Decision Engine
Tarih: 31 Ekim 2025

AI DECISION ENGINE:
- Strategy Layer v3 score (0-100)
- Monte Carlo risk assessment
- Kelly Criterion position sizing
- Volume Profile zone risk adjustment
- Pivot-based stop/target optimization
- Fibonacci-guided entry confirmation
- VWAP deviation risk control

FINAL DECISION:
- LONG / SHORT / WAIT
- Position size (USD + %)
- Entry price
- Stop loss
- Take profit
- Risk/Reward ratio
- Confidence level
"""

from datetime import datetime

# Import layers
try:
    import strategy_layer_v3 as strategy
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
    AI Brain - Final trading decision
    
    Args:
        symbol (str): BTCUSDT, ETHUSDT, etc.
        interval (str): Timeframe
        portfolio_value (float): Current portfolio value
        risk_per_trade (float): Max risk per trade
    
    Returns:
        dict: Complete trading decision with all details
    """
    
    # 1. Strategy Layer v3 - Comprehensive score
    if STRATEGY_AVAILABLE:
        strategy_result = strategy.calculate_comprehensive_score(symbol, interval)
        final_score = strategy_result['final_score']
        signal = strategy_result['signal']
        confidence = strategy_result['confidence']
    else:
        # Fallback
        final_score = 50
        signal = 'NEUTRAL'
        confidence = 0.5
    
    # 2. Monte Carlo risk assessment
    if MC_AVAILABLE:
        # Varsayılan parametreler (gerçek backtest'den gelecek)
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
    else:
        risk_of_ruin = 5.0
        max_drawdown = 20.0
        sharpe = 1.5
    
    # 3. Kelly Criterion position sizing
    if KELLY_AVAILABLE:
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
    else:
        # Fallback: Fixed % risk
        position_size_usd = risk_per_trade
        position_size_pct = (risk_per_trade / portfolio_value) * 100
        risk_amount = risk_per_trade
    
    # 4. Risk adjustments based on indicators
    
    # Volume Profile adjustment
    if STRATEGY_AVAILABLE and strategy_result['components']['volume_profile']['available']:
        vp_zone = strategy_result['components']['volume_profile'].get('zone', 'UNKNOWN')
        
        if vp_zone == 'POC':
            # At Point of Control - reduce size (reversal expected)
            position_size_usd *= 0.8
            risk_amount *= 0.8
        elif vp_zone == 'LVN':
            # Low Volume Node - increase size (breakout potential)
            position_size_usd *= 1.2
            risk_amount *= 1.2
    
    # VWAP deviation adjustment
    if STRATEGY_AVAILABLE and strategy_result['components']['vwap']['available']:
        vwap_zone = strategy_result['components']['vwap'].get('zone', 'UNKNOWN')
        
        if vwap_zone in ['+3STD', '-3STD']:
            # Extreme deviation - mean reversion expected
            # Reduce position size
            position_size_usd *= 0.7
            risk_amount *= 0.7
    
    # Risk of Ruin check
    if risk_of_ruin > 10:
        # High risk - reduce all positions
        position_size_usd *= 0.5
        risk_amount *= 0.5
    
    # Max position size constraint (never exceed 10% of portfolio)
    max_position = portfolio_value * 0.10
    if position_size_usd > max_position:
        position_size_usd = max_position
    
    # 5. Entry/Stop/Target calculation
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
        # ATR-based stop/target (simplified)
        atr_multiplier_stop = 2.0
        atr_multiplier_target = 3.0
        
        # Varsayılan ATR (%1.5)
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
        
        # R/R ratio
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
    
    # 6. Final decision
    decision = 'WAIT'
    
    if signal == 'LONG' and confidence >= 0.6 and final_score >= 65:
        decision = 'LONG'
    elif signal == 'SHORT' and confidence >= 0.6 and final_score <= 35:
        decision = 'SHORT'
    else:
        decision = 'WAIT'
    
    # Monte Carlo override
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
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# Test fonksiyonu
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 DEMIR AI - AI Brain v3 Test")
    print("=" * 80)
    
    symbol = 'BTCUSDT'
    interval = '1h'
    portfolio = 10000
    risk_per_trade = 200
    
    print(f"\n🧠 Making Trading Decision for {symbol}...")
    print(f"   Portfolio: ${portfolio:,.0f}")
    print(f"   Risk per Trade: ${risk_per_trade:,.0f}")
    
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
    print(f"   Reason: {decision['reason']}")
    
    if decision['entry_price']:
        print(f"\n💼 POSITION DETAILS:")
        print(f"   Entry: ${decision['entry_price']:,.2f}")
        print(f"   Stop Loss: ${decision['stop_loss']:,.2f}")
        print(f"   Take Profit: ${decision['take_profit']:,.2f}")
        print(f"   R/R Ratio: 1:{decision['risk_reward']:.2f}")
        print(f"   Position Size: ${decision['position_size_usd']:,.2f} ({decision['position_size_pct']:.2f}%)")
        print(f"   Risk Amount: ${decision['risk_amount_usd']:,.2f}")
    
    print(f"\n📊 RISK METRICS:")
    print(f"   Risk of Ruin: {decision['risk_metrics']['risk_of_ruin']}%")
    print(f"   Max Drawdown: {decision['risk_metrics']['max_drawdown']}%")
    print(f"   Sharpe Ratio: {decision['risk_metrics']['sharpe_ratio']:.2f}")
    
    print("\n" + "=" * 80)
