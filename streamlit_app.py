"""
🔱 DEMIR AI TRADING BOT - STREAMLIT APP v8.1 PHASE 3 ULTIMATE
============================================================
Date: 2 Kasım 2025, 19:40 CET
Version: 8.1 - 3 SABİT COİN + MANUEL EKLE SİSTEMİ

YENİ ÖZELLIK (v8.1):
--------------------
✅ 3 Sabit Coin (Silinemez): BTCUSDT, ETHUSDT, LTCUSDT
✅ Manuel Coin Ekleme Sistemi (Text Input)
✅ Eklenen Coinleri Silme (Sabit coinler hariç)

PHASE 3 FEATURES:
-----------------
• Backtest Engine - Test AI on historical data
• Portfolio Optimizer - Multi-coin allocation
• Auto-Trade Manual - AI suggests, you approve
• Telegram Alerts - Real-time notifications

PAGES:
------
1. 📊 Live Analysis (Original - Enhanced)
2. 🔙 Backtest (Historical Testing)
3. 💼 Portfolio (Multi-Coin Optimization)
4. 🤖 Auto-Trade (Manual Confirmation System)
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# =====================================================
# CORE IMPORTS - AI BRAIN
# =====================================================

try:
    import ai_brain
    from ai_brain import make_trading_decision
    AI_BRAIN_AVAILABLE = True
    print("✅ Streamlit: ai_brain module imported successfully!")
except Exception as e:
    AI_BRAIN_AVAILABLE = False
    st.error(f"❌ ai_brain.py not found! Error: {e}")
    st.stop()

# =====================================================
# PHASE 3 IMPORTS (Optional)
# =====================================================

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

try:
    from telegram_alert_system import TelegramAlertSystem
    TELEGRAM_AVAILABLE = True
except:
    TELEGRAM_AVAILABLE = False

# =====================================================
# SESSION STATE INITIALIZATION
# =====================================================

if 'custom_coins' not in st.session_state:
    st.session_state.custom_coins = []

if 'auto_trade' not in st.session_state:
    st.session_state.auto_trade = False

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="🔱 DEMIR AI Trading Bot v8.1",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {background-color: #0e1117;}
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border-radius: 10px;
        padding: 10px;
        font-weight: bold;
    }
    .stButton>button:hover {background-color: #145a8f;}
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #3d3d3d;
    }
    .fixed-coin {
        background-color: #1a472a;
        padding: 5px 10px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
    }
    .custom-coin {
        background-color: #2d3748;
        padding: 5px 10px;
        border-radius: 5px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# TITLE & HEADER
# =====================================================

st.title("🔱 DEMIR AI TRADING BOT v8.1")
st.markdown("### **PHASE 3 ULTIMATE** - 18-Layer AI Analysis System")

auto_trade_enabled = st.checkbox(
    "Auto-Trade: ☑️" if st.session_state.get('auto_trade', False) else "Auto-Trade:", 
    key='auto_trade'
)

st.markdown("---")

# =====================================================
# SIDEBAR - PAGE NAVIGATION
# =====================================================

st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Select Page:",
    ["📊 Live AI Trading Analysis", 
     "🔙 Backtest Engine" if BACKTEST_AVAILABLE else "🔙 Backtest (Unavailable)",
     "💼 Portfolio Optimizer" if PORTFOLIO_AVAILABLE else "💼 Portfolio (Unavailable)",
     "🤖 Auto-Trade Manager" if AUTO_TRADE_AVAILABLE else "🤖 Auto-Trade (Unavailable)"],
    index=0
)

st.sidebar.markdown("---")

# =====================================================
# SIDEBAR - COIN SELECTION SYSTEM (NEW v8.1!)
# =====================================================

st.sidebar.header("💰 Coin Selection")

# 3 FIXED COINS (Cannot be deleted)
FIXED_COINS = ["BTCUSDT", "ETHUSDT", "LTCUSDT"]

# Display Fixed Coins
st.sidebar.markdown("**🔒 Fixed Coins (Permanent):**")
for coin in FIXED_COINS:
    st.sidebar.markdown(f'<div class="fixed-coin">🟢 {coin}</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")

# Manual Coin Addition
st.sidebar.markdown("**➕ Add Custom Coin:**")

col1, col2 = st.sidebar.columns([3, 1])

with col1:
    new_coin = st.text_input(
        "Coin Symbol (e.g., SOLUSDT)",
        key="new_coin_input",
        placeholder="Enter coin symbol..."
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Spacing
    if st.button("➕"):
        if new_coin:
            new_coin_upper = new_coin.upper().strip()
            
            # Validation
            if new_coin_upper in FIXED_COINS:
                st.sidebar.error(f"❌ {new_coin_upper} is a fixed coin!")
            elif new_coin_upper in st.session_state.custom_coins:
                st.sidebar.warning(f"⚠️ {new_coin_upper} already added!")
            elif not new_coin_upper.endswith("USDT"):
                st.sidebar.error("❌ Coin must end with 'USDT'!")
            else:
                st.session_state.custom_coins.append(new_coin_upper)
                st.sidebar.success(f"✅ {new_coin_upper} added!")
                st.rerun()

# Display Custom Coins (with delete button)
if st.session_state.custom_coins:
    st.sidebar.markdown("**📋 Custom Coins:**")
    
    coins_to_remove = []
    
    for coin in st.session_state.custom_coins:
        col1, col2 = st.sidebar.columns([4, 1])
        
        with col1:
            st.markdown(f'<div class="custom-coin">{coin}</div>', unsafe_allow_html=True)
        
        with col2:
            if st.button("🗑️", key=f"delete_{coin}"):
                coins_to_remove.append(coin)
    
    # Remove coins after iteration
    for coin in coins_to_remove:
        st.session_state.custom_coins.remove(coin)
        st.sidebar.success(f"✅ {coin} removed!")
        st.rerun()

st.sidebar.markdown("---")

# =====================================================
# SIDEBAR - SETTINGS
# =====================================================

st.sidebar.header("⚙️ Settings")

# ALL COINS LIST (Fixed + Custom)
ALL_COINS = FIXED_COINS + st.session_state.custom_coins

# Symbol Selection
symbol = st.sidebar.selectbox(
    "Trading Pair",
    ALL_COINS,
    index=0
)

# Timeframe Selection
timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"],
    index=4  # Default: 1h
)

# Portfolio Value
portfolio_value = st.sidebar.number_input(
    "Portfolio Value (USDT)",
    min_value=100.0,
    max_value=1000000.0,
    value=10000.0,
    step=100.0
)

# Lookback Period
lookback_periods = st.sidebar.slider(
    "Lookback Periods",
    min_value=50,
    max_value=500,
    value=100,
    step=10
)

st.sidebar.markdown("---")

# System Status
st.sidebar.header("🔌 System Status")
status_container = st.sidebar.container()

with status_container:
    st.write(f"✅ AI Brain: {'Active' if AI_BRAIN_AVAILABLE else 'Inactive'}")
    st.write(f"{'✅' if BACKTEST_AVAILABLE else '⚠️'} Backtest: {'Active' if BACKTEST_AVAILABLE else 'Unavailable'}")
    st.write(f"{'✅' if PORTFOLIO_AVAILABLE else '⚠️'} Portfolio: {'Active' if PORTFOLIO_AVAILABLE else 'Unavailable'}")
    st.write(f"{'✅' if AUTO_TRADE_AVAILABLE else '⚠️'} Auto-Trade: {'Active' if AUTO_TRADE_AVAILABLE else 'Unavailable'}")
    st.write(f"{'✅' if TELEGRAM_AVAILABLE else '⚠️'} Telegram: {'Active' if TELEGRAM_AVAILABLE else 'Unavailable'}")

st.sidebar.markdown("---")
st.sidebar.markdown("**🔱 DEMIR AI v8.1** - 18-Layer AI | 3 Fixed + Custom Coins")
# =====================================================
# PAGE 1: LIVE AI TRADING ANALYSIS (DEVAM)
# =====================================================

if page == "📊 Live AI Trading Analysis":
    
    st.header("📊 Live AI Trading Analysis")
    st.markdown(f"**Symbol:** {symbol} | **Timeframe:** {timeframe}")
    
    # Run Analysis Button
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        analyze_button = st.button("🧠 Run AI Analysis", type="primary", use_container_width=True)
    
    with col2:
        send_telegram = st.checkbox("📱 Send to Telegram", value=False)
    
    with col3:
        auto_refresh = st.checkbox("🔄 Auto", value=False)
    
    st.markdown("---")
    
    # Analysis Logic
    if analyze_button or auto_refresh:
        
        with st.spinner("🔍 Analyzing market data with 18-layer AI system..."):
            
            try:
                # Call AI Brain with CORRECT parameters
                decision = make_trading_decision(
                    symbol=symbol,
                    timeframe=timeframe,           # ✅ CORRECT: timeframe parameter
                    capital=portfolio_value,       # ✅ CORRECT: capital parameter
                    lookback=lookback_periods      # ✅ CORRECT: lookback parameter
                )
                
                # Display Results
                if decision:
                    
                    signal = decision.get('signal', 'HOLD')
                    score = decision.get('score', 50)
                    confidence = decision.get('confidence', 0.5)
                    entry_price = decision.get('entry_price', 0)
                    stop_loss = decision.get('stop_loss', 0)
                    take_profit = decision.get('take_profit', 0)
                    position_size = decision.get('position_size', 0)
                    
                    # Signal Alert Box
                    if signal in ['STRONG BUY', 'BUY']:
                        st.success(f"✅ **{signal}** - Score: {score:.1f}/100 ({confidence*100:.0f}% confidence)")
                    elif signal == 'HOLD':
                        st.info(f"⏸️ **{signal}** - Score: {score:.1f}/100 ({confidence*100:.0f}% confidence)")
                    else:
                        st.error(f"⛔ **{signal}** - Score: {score:.1f}/100 ({confidence*100:.0f}% confidence)")
                    
                    # Metrics Row
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Entry Price", f"${entry_price:,.2f}")
                    
                    with col2:
                        st.metric("Stop Loss", f"${stop_loss:,.2f}")
                    
                    with col3:
                        st.metric("Take Profit", f"${take_profit:,.2f}")
                    
                    with col4:
                        st.metric("Position Size", f"${position_size:,.2f}")
                    
                    st.markdown("---")
                    
                    # Layer Scores Breakdown
                    st.subheader("📊 Layer Scores Breakdown (18 Total)")
                    
                    layer_scores = decision.get('layer_scores', {})
                    
                    cols = st.columns(3)
                    
                    layer_names = [
                        ('strategy', 'Strategy (L1-11)'),
                        ('macro_correlation', 'Macro (L12)'),
                        ('gold_correlation', 'Gold (L13)'),
                        ('dominance_flow', 'Dominance (L14)'),
                        ('cross_asset', 'Cross-Asset (L15)'),
                        ('vix_fear', 'VIX (L16)'),
                        ('interest_rates', 'Rates (L17)'),
                        ('traditional_markets', 'Markets (L18)')
                    ]
                    
                    for idx, (key, label) in enumerate(layer_names):
                        with cols[idx % 3]:
                            layer_score = layer_scores.get(key, 50)
                            st.metric(label, f"{layer_score:.1f}/100")
                    
                    st.markdown("---")
                    
                    # AI Commentary
                    st.subheader("🧠 AI Commentary")
                    commentary = decision.get('commentary', 'No commentary available')
                    st.text_area("Analysis Details:", commentary, height=400)
                    
                    # Telegram Send
                    if send_telegram and TELEGRAM_AVAILABLE:
                        try:
                            telegram_bot = TelegramAlertSystem()
                            telegram_bot.send_trade_alert(decision)
                            st.success("✅ Alert sent to Telegram!")
                        except Exception as e:
                            st.error(f"❌ Telegram send failed: {e}")
                    
                else:
                    st.error("❌ Analysis failed: No decision returned")
                    
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.code(f"Error details:\n{str(e)}")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(60)
        st.rerun()

# =====================================================
# PAGE 2: BACKTEST ENGINE
# =====================================================

elif page == "🔙 Backtest Engine" or page == "🔙 Backtest (Unavailable)":
    
    st.header("🔙 Backtest Engine")
    
    if not BACKTEST_AVAILABLE:
        st.warning("⚠️ Backtest Engine module not available. Please ensure backtest_engine.py is installed.")
        st.info("📝 This feature allows you to test the AI trading system on historical data.")
    else:
        st.markdown("Test the AI trading system on historical data to evaluate performance.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            bt_symbol = st.selectbox("Backtest Symbol", ALL_COINS, key="bt_symbol")
            bt_start_date = st.date_input("Start Date", datetime.now() - timedelta(days=90))
        
        with col2:
            bt_interval = st.selectbox("Interval", ["1h", "4h", "1d"], key="bt_interval")
            bt_end_date = st.date_input("End Date", datetime.now())
        
        bt_capital = st.number_input("Initial Capital (USDT)", min_value=1000, value=10000, step=1000)
        
        if st.button("🔙 Run Backtest", type="primary", use_container_width=True):
            with st.spinner("Running backtest... This may take a minute."):
                try:
                    backtest_engine = BacktestEngine()
                    results = backtest_engine.run_backtest(
                        symbol=bt_symbol,
                        start_date=bt_start_date.strftime('%Y-%m-%d'),
                        end_date=bt_end_date.strftime('%Y-%m-%d'),
                        interval=bt_interval,
                        initial_capital=bt_capital
                    )
                    
                    if results:
                        st.success("✅ Backtest completed!")
                        
                        # Summary Metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Return", f"{results.get('total_return', 0):.2f}%")
                        
                        with col2:
                            st.metric("Win Rate", f"{results.get('win_rate', 0):.1f}%")
                        
                        with col3:
                            st.metric("Total Trades", results.get('total_trades', 0))
                        
                        with col4:
                            st.metric("Sharpe Ratio", f"{results.get('sharpe_ratio', 0):.2f}")
                        
                        # Equity Curve
                        if 'equity_curve' in results:
                            st.line_chart(results['equity_curve'])
                        
                        # Trade History
                        if 'trade_history' in results:
                            st.subheader("📜 Trade History")
                            st.dataframe(results['trade_history'])
                    
                    else:
                        st.error("❌ Backtest failed to return results")
                        
                except Exception as e:
                    st.error(f"❌ Backtest failed: {str(e)}")

# =====================================================
# PAGE 3: PORTFOLIO OPTIMIZER
# =====================================================

elif page == "💼 Portfolio Optimizer" or page == "💼 Portfolio (Unavailable)":
    
    st.header("💼 Portfolio Optimizer")
    
    if not PORTFOLIO_AVAILABLE:
        st.warning("⚠️ Portfolio Optimizer module not available.")
        st.info("📝 This feature allows you to optimize capital allocation across multiple coins.")
    else:
        st.markdown("Optimize capital allocation across multiple cryptocurrencies using AI analysis.")
        
        # Multi-select coins
        selected_coins = st.multiselect(
            "Select Coins for Portfolio",
            ALL_COINS,
            default=FIXED_COINS[:2]  # Default: BTC and ETH
        )
        
        pf_capital = st.number_input("Total Portfolio Value (USDT)", min_value=1000, value=10000, step=1000, key="pf_capital")
        
        if st.button("💼 Optimize Portfolio", type="primary", use_container_width=True):
            if len(selected_coins) < 2:
                st.error("❌ Please select at least 2 coins for portfolio optimization")
            else:
                with st.spinner("Optimizing portfolio allocation..."):
                    try:
                        optimizer = PortfolioOptimizer()
                        allocation = optimizer.optimize(
                            coins=selected_coins,
                            total_capital=pf_capital
                        )
                        
                        if allocation:
                            st.success("✅ Portfolio optimized!")
                            
                            # Display allocation
                            st.subheader("📊 Recommended Allocation")
                            
                            alloc_df = pd.DataFrame(allocation)
                            st.dataframe(alloc_df)
                            
                            # Pie chart
                            st.subheader("📈 Allocation Chart")
                            st.bar_chart(alloc_df.set_index('symbol')['allocation'])
                        
                        else:
                            st.error("❌ Portfolio optimization failed")
                            
                    except Exception as e:
                        st.error(f"❌ Optimization failed: {str(e)}")

# =====================================================
# PAGE 4: AUTO-TRADE MANAGER
# =====================================================

elif page == "🤖 Auto-Trade Manager" or page == "🤖 Auto-Trade (Unavailable)":
    
    st.header("🤖 Auto-Trade Manager")
    
    if not AUTO_TRADE_AVAILABLE:
        st.warning("⚠️ Auto-Trade Manager module not available.")
        st.info("📝 This feature allows the AI to suggest trades that you manually approve.")
    else:
        st.markdown("AI suggests trades - you manually approve or reject them.")
        
        trade_symbol = st.selectbox("Symbol", ALL_COINS, key="trade_symbol")
        trade_interval = st.selectbox("Interval", ["1h", "4h"], key="trade_interval")
        
        if st.button("🔍 Get AI Trade Suggestion", type="primary", use_container_width=True):
            with st.spinner("Getting AI suggestion..."):
                try:
                    suggestion = make_trading_decision(
                        symbol=trade_symbol,
                        timeframe=trade_interval,
                        capital=portfolio_value,
                        lookback=100
                    )
                    
                    if suggestion:
                        signal = suggestion.get('signal', 'HOLD')
                        
                        if signal in ['STRONG BUY', 'BUY']:
                            st.success(f"✅ AI Recommendation: **{signal}**")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("Entry", f"${suggestion.get('entry_price', 0):,.2f}")
                                st.metric("Stop Loss", f"${suggestion.get('stop_loss', 0):,.2f}")
                            
                            with col2:
                                st.metric("Take Profit", f"${suggestion.get('take_profit', 0):,.2f}")
                                st.metric("Position Size", f"${suggestion.get('position_size', 0):,.2f}")
                            
                            # Approval buttons
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.button("✅ Approve & Execute", type="primary", use_container_width=True):
                                    st.success("✅ Trade approved! (Manual execution required)")
                            
                            with col2:
                                if st.button("❌ Reject", use_container_width=True):
                                    st.info("Trade rejected")
                        
                        else:
                            st.info(f"⏸️ AI Recommendation: **{signal}** - No action suggested")
                    
                    else:
                        st.error("❌ Failed to get suggestion")
                        
                except Exception as e:
                    st.error(f"❌ Suggestion failed: {str(e)}")

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")
st.markdown("**🔱 DEMIR AI TRADING BOT v8.1** | 18-Layer AI Analysis System | Phase 3 Complete")
st.markdown("Built with ❤️ for professional crypto trading")
# =====================================================
# END OF FILE
# =====================================================

# No additional code needed - file is complete!

print("\n✅ streamlit_app.py v8.1 loaded successfully!")
print("🔱 3 Fixed Coins (BTCUSDT, ETHUSDT, LTCUSDT) + Custom Coin System")
print("📊 18-Layer AI Analysis | Phase 3 Complete | Auto-Trade Ready!")
