"""
🔱 DEMIR AI TRADING BOT - STREAMLIT APP v8.0 PHASE 3 ULTIMATE
==============================================================
Date: 2 Kasım 2025, 14:35 CET
Version: 8.0 - FULL PHASE 3 INTEGRATION

NEW FEATURES (PHASE 3):
-----------------------
✅ Backtest Engine - Test AI on historical data
✅ Portfolio Optimizer - Multi-coin allocation
✅ Auto-Trade Manual - AI suggests, you approve
✅ Telegram Alerts - Real-time notifications

PAGES:
------
1. 📊 Live Analysis (Original + Enhanced)
2. 🧪 Backtest (Historical Testing)
3. 💼 Portfolio (Multi-Coin Optimization)
4. 🤖 Auto-Trade (Manual Confirmation System)

COMPATIBILITY:
--------------
✅ Works with existing ai_brain.py
✅ All original features preserved
✅ Phase 3 modules optional (graceful fallback)
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# Core imports
try:
    from ai_brain import make_trading_decision
    AI_BRAIN_AVAILABLE = True
except:
    AI_BRAIN_AVAILABLE = False
    st.error("❌ ai_brain.py not found!")

# Phase 3 imports (NEW)
try:
    from telegram_alert_system import TelegramAlertSystem
    TELEGRAM_AVAILABLE = True
except:
    TELEGRAM_AVAILABLE = False

try:
    from backtest_engine import BacktestEngine
    BACKTEST_AVAILABLE = True
except:
    BACKTEST_AVAILABLE = False

try:
    from portfolio_optimizer import PortfolioOptimizer
    PORTFOLIO_AVAILABLE = True
except:
    PORTFOLIO_AVAILABLE = False

try:
    from auto_trade_manual import AutoTradeManager
    AUTO_TRADE_AVAILABLE = True
except:
    AUTO_TRADE_AVAILABLE = False

# Config
try:
    from config import (
        BINANCE_API_KEY, 
        BINANCE_SECRET_KEY,
        TELEGRAM_BOT_TOKEN,
        TELEGRAM_CHAT_ID
    )
    CONFIG_AVAILABLE = True
except:
    CONFIG_AVAILABLE = False
    BINANCE_API_KEY = None
    BINANCE_SECRET_KEY = None
    TELEGRAM_BOT_TOKEN = None
    TELEGRAM_CHAT_ID = None

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="🔱 DEMIR AI Trading Bot v8.0",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SIDEBAR - NAVIGATION & SETTINGS
# ============================================================================

st.sidebar.title("🔱 DEMIR AI Trading Bot")
st.sidebar.markdown("**Version 8.0** - Phase 3 Ultimate")
st.sidebar.markdown("---")

# Coin selection (always visible)
st.sidebar.markdown("### 📊 Trading Pair")
symbol = st.sidebar.selectbox(
    "Select Coin:",
    ["BTCUSDT", "ETHUSDT", "LTCUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT"],
    index=0
)

interval = st.sidebar.selectbox(
    "Timeframe:",
    ["1m", "5m", "15m", "1h", "4h", "1d"],
    index=3
)

# Capital & Risk
st.sidebar.markdown("### 💰 Capital Settings")
capital = st.sidebar.number_input(
    "Total Capital ($):",
    min_value=100,
    max_value=1000000,
    value=10000,
    step=100
)

risk_per_trade = st.sidebar.number_input(
    "Risk Per Trade ($):",
    min_value=10,
    max_value=10000,
    value=200,
    step=10
)

# Page navigation (NEW)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Navigation")

page = st.sidebar.radio(
    "Select Module:",
    [
        "📊 Live Analysis",
        "🧪 Backtest Engine",
        "💼 Portfolio Optimizer",
        "🤖 Auto-Trade Manager"
    ],
    index=0
)

# Module status indicators
st.sidebar.markdown("---")
st.sidebar.markdown("### 📡 Module Status")

status_col1, status_col2 = st.sidebar.columns(2)

with status_col1:
    st.markdown(f"**AI Brain:** {'✅' if AI_BRAIN_AVAILABLE else '❌'}")
    st.markdown(f"**Telegram:** {'✅' if TELEGRAM_AVAILABLE else '❌'}")

with status_col2:
    st.markdown(f"**Backtest:** {'✅' if BACKTEST_AVAILABLE else '❌'}")
    st.markdown(f"**Portfolio:** {'✅' if PORTFOLIO_AVAILABLE else '❌'}")

st.markdown(f"**Auto-Trade:** {'✅' if AUTO_TRADE_AVAILABLE else '❌'}")

# ============================================================================
# PAGE 1: LIVE ANALYSIS (ORIGINAL + ENHANCED)
# ============================================================================

if page == "📊 Live Analysis":
    
    st.title("📊 Live AI Trading Analysis")
    st.markdown(f"**Symbol:** {symbol} | **Timeframe:** {interval}")
    st.markdown("---")
    
    # Analysis button
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        analyze_button = st.button("🧠 Run AI Analysis", use_container_width=True, type="primary")
    
    with col2:
        if TELEGRAM_AVAILABLE:
            send_telegram = st.checkbox("📱 Send to Telegram", value=False)
        else:
            send_telegram = False
            st.info("📱 Telegram not configured")
    
    with col3:
        auto_refresh = st.checkbox("🔄 Auto", value=False)
    
    # Auto refresh
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
    # Run analysis
    if analyze_button:
        
        with st.spinner("🧠 AI Brain analyzing..."):
            
            try:
                # Call AI Brain
                decision = make_trading_decision(
                    symbol=symbol,
                    interval=interval,
                    capital=capital,
                    risk_per_trade=risk_per_trade
                )
                
                # Store in session state
                st.session_state['last_decision'] = decision
                
                # Display results
                st.success("✅ Analysis Complete!")
                
                # === DECISION CARD ===
                st.markdown("### 🎯 AI Decision")
                
                dec_col1, dec_col2, dec_col3, dec_col4 = st.columns(4)
                
                with dec_col1:
                    decision_emoji = "🟢" if decision['decision'] == "LONG" else "🔴" if decision['decision'] == "SHORT" else "⚪"
                    st.metric("Decision", f"{decision_emoji} {decision['decision']}")
                
                with dec_col2:
                    st.metric("Score", f"{decision['final_score']:.1f}/100")
                
                with dec_col3:
                    st.metric("Confidence", f"{decision['confidence']*100:.0f}%")
                
                with dec_col4:
                    st.metric("R/R Ratio", f"1:{decision['risk_reward']:.2f}")
                
                # === PRICE LEVELS ===
                st.markdown("### 💰 Price Levels")
                
                price_col1, price_col2, price_col3, price_col4 = st.columns(4)
                
                with price_col1:
                    st.metric("Entry Price", f"${decision['entry_price']:,.2f}")
                
                with price_col2:
                    sl_pct = abs((decision['entry_price'] - decision['stop_loss']) / decision['entry_price'] * 100)
                    st.metric("Stop Loss", f"${decision['stop_loss']:,.2f}", f"-{sl_pct:.2f}%")
                
                with price_col3:
                    tp_pct = abs((decision['take_profit'] - decision['entry_price']) / decision['entry_price'] * 100)
                    st.metric("Take Profit", f"${decision['take_profit']:,.2f}", f"+{tp_pct:.2f}%")
                
                with price_col4:
                    st.metric("Position Size", f"${decision['position_size_usd']:,.2f}")
                
                # === REASON ===
                st.markdown("### 💡 Analysis Reason")
                st.info(decision.get('reason', 'No reason provided'))
                
                # === LAYER SCORES ===
                with st.expander("🔍 View All Layer Scores"):
                    
                    layer_scores = decision.get('layer_scores', {})
                    
                    if layer_scores:
                        # Create DataFrame
                        df_layers = pd.DataFrame([
                            {'Layer': k, 'Score': v, 'Signal': 'BULLISH' if v > 60 else 'BEARISH' if v < 40 else 'NEUTRAL'}
                            for k, v in layer_scores.items()
                        ])
                        
                        df_layers = df_layers.sort_values('Score', ascending=False)
                        
                        st.dataframe(
                            df_layers,
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.warning("No layer scores available")
                
                # === SEND TO TELEGRAM ===
                if send_telegram and TELEGRAM_AVAILABLE:
                    try:
                        telegram = TelegramAlertSystem(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
                        telegram.send_signal_alert(decision)
                        st.success("📱 Signal sent to Telegram!")
                    except Exception as e:
                        st.error(f"❌ Telegram send failed: {e}")
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")
                st.code(str(e))

# ============================================================================
# PAGE 2: BACKTEST ENGINE (NEW)
# ============================================================================

elif page == "🧪 Backtest Engine":
    
    st.title("🧪 Backtest Engine - Historical Testing")
    st.markdown("Test AI strategy performance on historical data")
    st.markdown("---")
    
    if not BACKTEST_AVAILABLE:
        st.error("❌ Backtest Engine not available. Please ensure backtest_engine.py is in the project.")
        st.stop()
    
    # Backtest settings
    col1, col2, col3 = st.columns(3)
    
    with col1:
        backtest_symbol = st.selectbox("Symbol:", ["BTCUSDT", "ETHUSDT", "LTCUSDT"], key="bt_symbol")
    
    with col2:
        backtest_interval = st.selectbox("Timeframe:", ["1h", "4h", "1d"], key="bt_interval")
    
    with col3:
        lookback_days = st.number_input("Lookback Days:", 7, 90, 30, key="bt_days")
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        bt_capital = st.number_input("Initial Capital ($):", 1000, 100000, 10000, step=1000, key="bt_capital")
    
    with col5:
        bt_risk = st.number_input("Risk/Trade ($):", 10, 1000, 200, step=10, key="bt_risk")
    
    with col6:
        max_trades = st.number_input("Max Trades:", 10, 500, 100, step=10, key="bt_trades")
    
    # Run backtest button
    run_backtest = st.button("🚀 Run Backtest", use_container_width=True, type="primary")
    
    if run_backtest:
        
        with st.spinner(f"🧪 Running backtest on {lookback_days} days of {backtest_symbol} data..."):
            
            try:
                # Initialize backtest engine
                engine = BacktestEngine(
                    symbol=backtest_symbol,
                    initial_capital=bt_capital,
                    risk_per_trade=bt_risk
                )
                
                # Import AI brain for backtest
                if not AI_BRAIN_AVAILABLE:
                    st.error("❌ AI Brain not available for backtest")
                    st.stop()
                
                import ai_brain
                
                # Run backtest
                results = engine.run_backtest(
                    ai_brain=ai_brain,
                    interval=backtest_interval,
                    lookback_days=lookback_days,
                    max_trades=max_trades
                )
                
                if 'error' in results:
                    st.error(f"❌ {results['error']}")
                else:
                    st.success("✅ Backtest Complete!")
                    
                    # === PERFORMANCE METRICS ===
                    st.markdown("### 📊 Performance Metrics")
                    
                    met_col1, met_col2, met_col3, met_col4 = st.columns(4)
                    
                    with met_col1:
                        st.metric("Total Trades", results['total_trades'])
                    
                    with met_col2:
                        st.metric("Win Rate", f"{results['win_rate']:.1f}%")
                    
                    with met_col3:
                        pnl_color = "normal" if results['total_pnl'] >= 0 else "inverse"
                        st.metric("Total P&L", f"${results['total_pnl']:+,.2f}", 
                                 f"{results['total_pnl_pct']:+.2f}%")
                    
                    with met_col4:
                        st.metric("Final Capital", f"${results['final_capital']:,.2f}")
                    
                    met_col5, met_col6, met_col7, met_col8 = st.columns(4)
                    
                    with met_col5:
                        st.metric("Profit Factor", f"{results['profit_factor']:.2f}")
                    
                    with met_col6:
                        st.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
                    
                    with met_col7:
                        st.metric("Max Drawdown", f"{results['max_drawdown']:.2f}%")
                    
                    with met_col8:
                        st.metric("Avg Win/Loss", f"${results['avg_win']:.2f} / ${results['avg_loss']:.2f}")
                    
                    # === EQUITY CURVE ===
                    st.markdown("### 📈 Equity Curve")
                    
                    equity_curve = results.get('equity_curve', [])
                    
                    if equity_curve:
                        df_equity = pd.DataFrame({
                            'Trade': range(len(equity_curve)),
                            'Capital': equity_curve
                        })
                        
                        st.line_chart(df_equity.set_index('Trade'))
                    
                    # === TRADE HISTORY ===
                    with st.expander("📋 View Trade History"):
                        trades_df = results.get('trades_df')
                        
                        if trades_df is not None and not trades_df.empty:
                            st.dataframe(
                                trades_df[[
                                    'timestamp', 'signal', 'entry_price', 'exit_price',
                                    'pnl', 'pnl_pct', 'result'
                                ]],
                                use_container_width=True
                            )
                        else:
                            st.warning("No trades executed")
                    
                    # === EXPORT ===
                    st.markdown("### 💾 Export Results")
                    
                    if st.button("📥 Export to CSV"):
                        success = engine.export_to_csv(f'backtest_{backtest_symbol}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
                        if success:
                            st.success("✅ Results exported!")
                
            except Exception as e:
                st.error(f"❌ Backtest failed: {e}")
                st.code(str(e))

# ============================================================================
# PAGE 3: PORTFOLIO OPTIMIZER (NEW)
# ============================================================================

elif page == "💼 Portfolio Optimizer":
    
    st.title("💼 Portfolio Optimizer - Multi-Coin Allocation")
    st.markdown("Optimize portfolio allocation using Kelly Criterion & Correlation Analysis")
    st.markdown("---")
    
    if not PORTFOLIO_AVAILABLE:
        st.error("❌ Portfolio Optimizer not available. Please ensure portfolio_optimizer.py is in the project.")
        st.stop()
    
    # Portfolio settings
    col1, col2 = st.columns(2)
    
    with col1:
        port_capital = st.number_input("Total Portfolio ($):", 1000, 1000000, 10000, step=1000, key="port_capital")
    
    with col2:
        port_risk = st.number_input("Risk/Trade ($):", 10, 10000, 200, step=10, key="port_risk")
    
    # Coin selection
    st.markdown("### 🪙 Select Coins for Portfolio")
    
    coin_col1, coin_col2, coin_col3, coin_col4 = st.columns(4)
    
    selected_coins = []
    coin_scores = {}
    
    with coin_col1:
        if st.checkbox("BTC", value=True, key="coin_btc"):
            selected_coins.append("BTCUSDT")
            coin_scores["BTCUSDT"] = st.slider("BTC AI Score:", 0, 100, 75, key="score_btc")
    
    with coin_col2:
        if st.checkbox("ETH", value=True, key="coin_eth"):
            selected_coins.append("ETHUSDT")
            coin_scores["ETHUSDT"] = st.slider("ETH AI Score:", 0, 100, 68, key="score_eth")
    
    with coin_col3:
        if st.checkbox("LTC", value=False, key="coin_ltc"):
            selected_coins.append("LTCUSDT")
            coin_scores["LTCUSDT"] = st.slider("LTC AI Score:", 0, 100, 55, key="score_ltc")
    
    with coin_col4:
        if st.checkbox("BNB", value=False, key="coin_bnb"):
            selected_coins.append("BNBUSDT")
            coin_scores["BNBUSDT"] = st.slider("BNB AI Score:", 0, 100, 62, key="score_bnb")
    
    if len(selected_coins) < 2:
        st.warning("⚠️ Please select at least 2 coins")
        st.stop()
    
    # Optimize button
    optimize_button = st.button("🎯 Optimize Portfolio", use_container_width=True, type="primary")
    
    if optimize_button:
        
        with st.spinner(f"💼 Optimizing portfolio for {len(selected_coins)} coins..."):
            
            try:
                # Initialize optimizer
                optimizer = PortfolioOptimizer(
                    total_capital=port_capital,
                    risk_per_trade=port_risk
                )
                
                # Fetch correlation data
                price_df = optimizer.fetch_correlation_data(
                    symbols=selected_coins,
                    interval='1d',
                    lookback_days=30
                )
                
                if price_df.empty:
                    st.error("❌ Failed to fetch price data")
                    st.stop()
                
                # Calculate correlation matrix
                corr_matrix = optimizer.calculate_correlation_matrix(price_df)
                
                # Calculate diversification score
                div_score = optimizer.calculate_diversification_score(corr_matrix)
                
                # Optimize weights
                weights = optimizer.optimize_portfolio_weights(selected_coins, coin_scores)
                
                st.success("✅ Optimization Complete!")
                
                # === DIVERSIFICATION SCORE ===
                st.markdown("### 📈 Diversification Score")
                
                div_col1, div_col2 = st.columns([1, 3])
                
                with div_col1:
                    st.metric("Score", f"{div_score:.1f}/100")
                
                with div_col2:
                    if div_score > 70:
                        st.success("✅ Excellent diversification!")
                    elif div_score > 50:
                        st.warning("⚠️ Good diversification")
                    else:
                        st.error("❌ Poor diversification - coins too correlated!")
                
                # === CORRELATION MATRIX ===
                st.markdown("### 🔗 Correlation Matrix")
                st.dataframe(corr_matrix.style.background_gradient(cmap='RdYlGn_r', vmin=-1, vmax=1), use_container_width=True)
                
                # === OPTIMAL ALLOCATION ===
                st.markdown("### 🎯 Optimal Allocation")
                
                alloc_data = []
                for coin, weight in weights.items():
                    alloc_usd = port_capital * weight
                    alloc_data.append({
                        'Coin': coin.replace('USDT', ''),
                        'Weight': f"{weight*100:.1f}%",
                        'Allocation ($)': f"${alloc_usd:,.2f}",
                        'AI Score': coin_scores.get(coin, 50)
                    })
                
                df_alloc = pd.DataFrame(alloc_data)
                st.dataframe(df_alloc, use_container_width=True, hide_index=True)
                
                # === RECOMMENDATIONS ===
                report = optimizer.generate_allocation_report()
                
                if report.get('recommendations'):
                    st.markdown("### 💡 Recommendations")
                    for rec in report['recommendations']:
                        if "✅" in rec:
                            st.success(rec)
                        elif "⚠️" in rec:
                            st.warning(rec)
                
            except Exception as e:
                st.error(f"❌ Optimization failed: {e}")
                st.code(str(e))
# ============================================================================
# PAGE 4: AUTO-TRADE MANAGER (NEW)
# ============================================================================

elif page == "🤖 Auto-Trade Manager":
    
    st.title("🤖 Auto-Trade Manager - Manual Confirmation")
    st.markdown("AI suggests trades → You approve → System executes on Binance")
    st.markdown("---")
    
    if not AUTO_TRADE_AVAILABLE:
        st.error("❌ Auto-Trade Manager not available. Please ensure auto_trade_manual.py is in the project.")
        st.stop()
    
    # API Configuration check
    st.markdown("### 🔐 Binance API Configuration")
    
    api_status_col1, api_status_col2 = st.columns(2)
    
    with api_status_col1:
        if BINANCE_API_KEY:
            st.success("✅ API Key configured")
        else:
            st.error("❌ API Key missing")
    
    with api_status_col2:
        if BINANCE_SECRET_KEY:
            st.success("✅ Secret Key configured")
        else:
            st.error("❌ Secret Key missing")
    
    if not (BINANCE_API_KEY and BINANCE_SECRET_KEY):
        st.warning("⚠️ Please configure Binance API keys in config.py")
        st.info("""
        **Setup Instructions:**
        1. Go to Binance API Management
        2. Create new API key
        3. Enable Futures Trading (if needed)
        4. Add API key and secret to config.py
        5. Restart Streamlit
        """)
    
    # Test mode toggle
    st.markdown("---")
    st.markdown("### ⚙️ Trading Mode")
    
    test_mode = st.checkbox("🧪 Test Mode (No Real Orders)", value=True, key="test_mode")
    
    if test_mode:
        st.info("🧪 Test Mode: Orders will be simulated (no real trades)")
    else:
        st.warning("⚠️ LIVE MODE: Real orders will be placed on Binance!")
    
    st.markdown("---")
    
    # Step 1: Generate AI Signal
    st.markdown("### 1️⃣ Generate AI Trading Signal")
    
    trade_col1, trade_col2 = st.columns(2)
    
    with trade_col1:
        trade_symbol = st.selectbox("Symbol:", ["BTCUSDT", "ETHUSDT", "LTCUSDT"], key="trade_symbol")
    
    with trade_col2:
        trade_interval = st.selectbox("Timeframe:", ["1h", "4h", "1d"], key="trade_interval")
    
    generate_signal_btn = st.button("🧠 Generate AI Signal", use_container_width=True, type="primary")
    
    if generate_signal_btn:
        
        with st.spinner("🧠 AI analyzing market..."):
            
            try:
                # Generate AI decision
                decision = make_trading_decision(
                    symbol=trade_symbol,
                    interval=trade_interval,
                    capital=capital,
                    risk_per_trade=risk_per_trade
                )
                
                # Store in session state
                st.session_state['pending_trade'] = decision
                
                st.success("✅ AI signal generated!")
                
            except Exception as e:
                st.error(f"❌ Signal generation failed: {e}")
                st.stop()
    
    # Step 2: Preview Trade
    if 'pending_trade' in st.session_state:
        
        st.markdown("---")
        st.markdown("### 2️⃣ Trade Preview")
        
        decision = st.session_state['pending_trade']
        
        # Initialize manager for preview
        try:
            manager = AutoTradeManager(
                api_key=BINANCE_API_KEY,
                api_secret=BINANCE_SECRET_KEY,
                test_mode=test_mode
            )
            
            preview = manager.preview_order(decision)
            
            # Display preview
            st.info("📋 Review trade details carefully before approval")
            
            prev_col1, prev_col2, prev_col3, prev_col4 = st.columns(4)
            
            with prev_col1:
                decision_emoji = "🟢" if preview['side'] == "BUY" else "🔴"
                st.metric("Direction", f"{decision_emoji} {preview['side']}")
            
            with prev_col2:
                st.metric("Entry Price", f"${preview['entry_price']:,.2f}")
            
            with prev_col3:
                st.metric("Quantity", f"{preview['quantity']:.4f}")
            
            with prev_col4:
                st.metric("Position Size", f"${preview['position_size_usd']:,.2f}")
            
            # Stop Loss & Take Profit
            st.markdown("**Stop Loss & Take Profit:**")
            
            tp_col1, tp_col2, tp_col3, tp_col4 = st.columns(4)
            
            with tp_col1:
                sl_pct = abs((preview['entry_price'] - preview['stop_loss']) / preview['entry_price'] * 100)
                st.metric("Stop Loss", f"${preview['stop_loss']:,.2f}", f"-{sl_pct:.2f}%")
            
            with tp_col2:
                tp1_pct = abs((preview['tp1'] - preview['entry_price']) / preview['entry_price'] * 100)
                st.metric("TP1 (50%)", f"${preview['tp1']:,.2f}", f"+{tp1_pct:.2f}%")
            
            with tp_col3:
                tp2_pct = abs((preview['tp2'] - preview['entry_price']) / preview['entry_price'] * 100)
                st.metric("TP2 (30%)", f"${preview['tp2']:,.2f}", f"+{tp2_pct:.2f}%")
            
            with tp_col4:
                tp3_pct = abs((preview['tp3'] - preview['entry_price']) / preview['entry_price'] * 100)
                st.metric("TP3 (20%)", f"${preview['tp3']:,.2f}", f"+{tp3_pct:.2f}%")
            
            # Risk Summary
            with st.expander("📊 Risk Analysis"):
                st.markdown(f"**Risk Amount:** ${preview['risk_amount_usd']:,.2f}")
                st.markdown(f"**Position Size:** ${preview['position_size_usd']:,.2f}")
                st.markdown(f"**% of Capital:** {(preview['position_size_usd']/capital*100):.1f}%")
                st.markdown(f"**Max Loss:** ${preview['risk_amount_usd']:,.2f} ({sl_pct:.2f}%)")
                st.markdown(f"**Potential Gain (TP3):** ${preview['position_size_usd'] * tp3_pct / 100:,.2f} ({tp3_pct:.2f}%)")
            
            # Step 3: Manual Approval
            st.markdown("---")
            st.markdown("### 3️⃣ Manual Approval")
            
            st.warning("⚠️ **YOU ARE IN FULL CONTROL** - Review all details before approving")
            
            approval_col1, approval_col2 = st.columns([1, 1])
            
            with approval_col1:
                approve_button = st.button(
                    "✅ APPROVE & EXECUTE TRADE",
                    use_container_width=True,
                    type="primary"
                )
            
            with approval_col2:
                reject_button = st.button(
                    "❌ REJECT TRADE",
                    use_container_width=True
                )
            
            # Execute trade
            if approve_button:
                
                with st.spinner("🚀 Executing trade on Binance..."):
                    
                    try:
                        result = manager.process_ai_signal(decision, user_approved=True)
                        
                        if result.get('success'):
                            st.success("✅ TRADE EXECUTED SUCCESSFULLY!")
                            
                            st.balloons()
                            
                            # Display result
                            st.markdown("### 📊 Execution Result")
                            
                            if result.get('test_mode'):
                                st.info("🧪 Test Mode: Trade simulated (no real execution)")
                            
                            res_col1, res_col2, res_col3 = st.columns(3)
                            
                            with res_col1:
                                st.metric("Order ID", result.get('order_id', 'N/A'))
                            
                            with res_col2:
                                st.metric("Fill Price", f"${result.get('fill_price', 0):,.2f}")
                            
                            with res_col3:
                                st.metric("Quantity", f"{result.get('quantity', 0):.4f}")
                            
                            # Send to Telegram
                            if TELEGRAM_AVAILABLE and TELEGRAM_BOT_TOKEN:
                                try:
                                    telegram = TelegramAlertSystem(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
                                    telegram.send_signal_alert(decision)
                                    st.success("📱 Trade notification sent to Telegram!")
                                except:
                                    pass
                            
                            # Clear pending trade
                            del st.session_state['pending_trade']
                            
                        else:
                            st.error(f"❌ Trade execution failed: {result.get('error', 'Unknown error')}")
                    
                    except Exception as e:
                        st.error(f"❌ Execution error: {e}")
                        st.code(str(e))
            
            # Reject trade
            if reject_button:
                del st.session_state['pending_trade']
                st.info("❌ Trade rejected by user")
                st.rerun()
        
        except Exception as e:
            st.error(f"❌ Manager initialization failed: {e}")
    
    else:
        st.info("👆 Generate an AI signal to start")
    
    # Open Positions
    st.markdown("---")
    st.markdown("### 📊 Open Positions")
    
    if st.button("🔄 Refresh Positions"):
        
        try:
            manager = AutoTradeManager(
                api_key=BINANCE_API_KEY,
                api_secret=BINANCE_SECRET_KEY,
                test_mode=test_mode
            )
            
            positions = manager.get_open_positions()
            
            if positions:
                st.success(f"✅ {len(positions)} open position(s)")
                
                for pos in positions:
                    with st.expander(f"{pos['symbol']} - {pos['positionAmt']}"):
                        st.json(pos)
            else:
                st.info("No open positions")
        
        except Exception as e:
            st.error(f"❌ Failed to fetch positions: {e}")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>🔱 DEMIR AI TRADING BOT v8.0 - PHASE 3 ULTIMATE</strong></p>
    <p>15-Layer AI Analysis | Backtest Engine | Portfolio Optimizer | Auto-Trade Manager</p>
    <p><em>⚠️ Trading involves risk. Use at your own discretion.</em></p>
</div>
""", unsafe_allow_html=True)

