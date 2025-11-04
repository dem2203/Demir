# streamlit_app.py v16.0 - PHASE 7 QUANTUM (NO LOGIN - FIXED)

"""
🔱 DEMIR AI TRADING BOT - Streamlit UI v14.3 ULTIMATE
====================================================================
Date: 4 Kasım 2025, 00:18 CET
Version: 16.0 - PHASE 7 + NO LOGIN + AI BRAIN FIXED + FUNCTION ORDER FIXED

✅ v14.3 FEATURES:
------------------
✅ COIN-SPECIFIC: Everything based on selected coin
✅ NO MOCK DATA: 100% real AI Brain calculations
✅ System Health: Real layer scores for selected coin
✅ AI Trading: Dynamic coin selection
✅ Backtest: Coin-specific historical testing
✅ Charts: Real-time coin data
✅ Authentication: User login/register
✅ Professional UI: TradingView-style

CRITICAL RULES:
---------------
RULE #1: NO MOCK/DEMO DATA - EVER!
RULE #2: COIN-SPECIFIC OPERATION - EVERYTHING!
RULE #3: REAL-TIME SYNCHRONIZATION

TABS:
-----
1. 🔐 Login/Register (if auth available)
2. 📊 System Health (17-Layer Phase 7 Quantum - COIN SPECIFIC)
3. 🧠 AI Trading (Live analysis + charts - COIN SPECIFIC)
4. 📈 Backtest Results (Performance analysis - COIN SPECIFIC)
5. ⚙️ Settings
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import plotly.graph_objects as go
import plotly.express as px
import os

# ============================================================================
# PAGE CONFIG - MUST BE FIRST!
# ============================================================================
st.set_page_config(
    page_title="🔱 DEMIR AI Trading Bot v16.0",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - PROFESSIONAL DESIGN
# ============================================================================
st.markdown("""
<style>
    /* Main container */
    .main {
        background-color: #0e1117;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #26a69a !important;
        font-weight: 600;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 600;
    }
    
    /* Success/Error boxes */
    .stSuccess {
        background-color: rgba(38, 166, 154, 0.1);
        border-left: 4px solid #26a69a;
    }
    
    .stError {
        background-color: rgba(239, 83, 80, 0.1);
        border-left: 4px solid #ef5350;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #26a69a;
        color: white;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #1e8378;
        transform: translateY(-2px);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
    }
    
    /* DataFrame */
    .dataframe {
        font-size: 12px;
    }
    
    /* Layer Cards */
    .layer-card {
        background: linear-gradient(135deg, rgba(38, 166, 154, 0.1), rgba(30, 131, 120, 0.05));
        border: 1px solid rgba(38, 166, 154, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .layer-header {
        font-size: 16px;
        font-weight: 600;
        color: #26a69a;
        margin-bottom: 8px;
    }
    
    .layer-score {
        font-size: 32px;
        font-weight: 700;
        margin: 8px 0;
    }
    
    .signal-long { color: #26a69a; }
    .signal-short { color: #ef5350; }
    .signal-neutral { color: #aaa; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# MODULE IMPORTS - DYNAMIC LOADING
# ============================================================================

# AI Brain - ✅ FIXED: make_trading_decision (not analyze_with_ai)
AI_BRAIN_AVAILABLE = False
try:
    from ai_brain import make_trading_decision
    AI_BRAIN_AVAILABLE = True
    print("✅ Streamlit v16.0: AI Brain loaded (make_trading_decision)")
except Exception as e:
    print(f"⚠️ Streamlit v16.0: AI Brain import failed: {e}")
    make_trading_decision = None

# Backtest
BACKTEST_AVAILABLE = False
try:
    from backtest_engine import BacktestEngine
    BACKTEST_AVAILABLE = True
    print("✅ Streamlit v16.0: Backtest Engine loaded")
except:
    try:
        from backtest_engine import run_backtest
        BACKTEST_AVAILABLE = True
        print("✅ Streamlit v16.0: Backtest (run_backtest) loaded")
    except:
        BACKTEST_AVAILABLE = False
        print("⚠️ Streamlit v16.0: Backtest Engine not available")

# Charts
CHART_AVAILABLE = False
try:
    from chart_generator import ChartGenerator
    CHART_AVAILABLE = True
    print("✅ Streamlit v16.0: Chart Generator loaded")
except:
    try:
        from chart_generator import create_price_chart
        CHART_AVAILABLE = True
        print("✅ Streamlit v16.0: Chart (create_price_chart) loaded")
    except:
        CHART_AVAILABLE = False
        print("⚠️ Streamlit v16.0: Chart Generator not available")

# Auth (not used in v16.0)
AUTH_AVAILABLE = False
try:
    from auth_system import AuthSystem, init_streamlit_auth
    AUTH_AVAILABLE = True
    print("✅ Streamlit v16.0: Auth System loaded (not used)")
except:
    AUTH_AVAILABLE = False
    print("⚠️ Streamlit v16.0: Auth System not available")

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = True  # ✅ v16.0: NO LOGIN

if 'username' not in st.session_state:
    st.session_state.username = 'demo_user'

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'ADAUSDT']

if 'selected_symbol' not in st.session_state:
    st.session_state.selected_symbol = 'BTCUSDT'

if 'selected_interval' not in st.session_state:
    st.session_state.selected_interval = '1h'

if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = None

if 'health_data' not in st.session_state:
    st.session_state.health_data = None

if 'backtest_results' not in st.session_state:
    st.session_state.backtest_results = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_signal_emoji(score):
    """Get emoji for score"""
    if score >= 60:
        return "🟢"
    elif score <= 40:
        return "🔴"
    else:
        return "⚪"

def get_signal_text(score):
    """Get text signal"""
    if score >= 60:
        return "LONG"
    elif score <= 40:
        return "SHORT"
    else:
        return "NEUTRAL"

def get_signal_color_class(score):
    """Get CSS class"""
    if score >= 60:
        return "signal-long"
    elif score <= 40:
        return "signal-short"
    else:
        return "signal-neutral"

def get_layer_weight(layer_name):
    """Get weight percentage for layer - PHASE 7 QUANTUM"""
    weights = {
        # Phase 1-6 (70%)
        'strategy': 15, 'multi_timeframe': 6, 'macro': 6, 'gold': 4,
        'dominance': 5, 'cross_asset': 8, 'vix': 5, 'rates': 5,
        'trad_markets': 6, 'news': 8, 'monte_carlo': 8, 'kelly': 8,
        # Phase 7 Quantum (30%)
        'black_scholes': 8, 'kalman': 7, 'fractal': 6, 'fourier': 5, 'copula': 4
    }
    return weights.get(layer_name, 1)

def format_percentage(value):
    """Format percentage value"""
    return f"{value:.2f}%"

def format_currency(value):
    """Format currency value"""
    return f"${value:,.2f}"

# ============================================================================
# AUTHENTICATION FUNCTIONS (Not used but keep for compatibility)
# ============================================================================

def render_login():
    """Render login form (deprecated in v16.0)"""
    st.warning("⚠️ Login not required in v16.0")

def render_register():
    """Render register form (deprecated in v16.0)"""
    st.warning("⚠️ Registration not required in v16.0")

# ============================================================================
# SIDEBAR - GLOBAL COIN & INTERVAL SELECTION
# ============================================================================
with st.sidebar:
    st.markdown("# 🔱 DEMIR AI Bot")
    st.markdown("*17-Layer Phase 7 System*")
    st.markdown("---")
    
    # User info
    st.markdown(f"👤 **User:** {st.session_state.username}")
    st.markdown(f"🔐 **Status:** Logged In")
    st.markdown("---")
    
    # ✅ CRITICAL: Global coin selection
    st.markdown("### 🪙 Global Coin Selection")
    st.markdown("*Bu seçim TÜM sayfalarda geçerlidir*")
    
    selected_coin = st.selectbox(
        "Select Trading Pair",
        options=st.session_state.watchlist,
        index=st.session_state.watchlist.index(st.session_state.selected_symbol) if st.session_state.selected_symbol in st.session_state.watchlist else 0,
        key='sidebar_coin_selector'
    )
    
    # Update global state if changed
    if selected_coin != st.session_state.selected_symbol:
        st.session_state.selected_symbol = selected_coin
        st.rerun()
    
    st.markdown("---")
    
    # ✅ CRITICAL: Global interval selection
    st.markdown("### ⏰ Global Timeframe")
    selected_interval = st.selectbox(
        "Select Interval",
        options=['1m', '5m', '15m', '1h', '4h', '1d'],
        index=['1m', '5m', '15m', '1h', '4h', '1d'].index(st.session_state.selected_interval),
        key='sidebar_interval_selector'
    )
    
    if selected_interval != st.session_state.selected_interval:
        st.session_state.selected_interval = selected_interval
        st.rerun()
    
    st.markdown("---")
    
    # System status
    st.markdown("### 📊 System Status")
    st.metric(
        "AI Brain",
        "Active" if AI_BRAIN_AVAILABLE else "Offline",
        delta="17 Layers (Phase 7)" if AI_BRAIN_AVAILABLE else "Not Loaded"
    )
    
    st.metric(
        "Backtest",
        "Ready" if BACKTEST_AVAILABLE else "Offline"
    )
    
    st.metric(
        "Charts",
        "Ready" if CHART_AVAILABLE else "Offline"
    )
    
    st.markdown("---")
    
    # Quick actions
    if st.button("🔄 Refresh All Data", use_container_width=True):
        st.rerun()
    
    if st.button("⚙️ Reset Settings", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ============================================================================
# MAIN APP HEADER
# ============================================================================
st.markdown(f"""
<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #26a69a 0%, #1e8378 100%); border-radius: 10px; margin-bottom: 20px;'>
    <h1 style='color: white; margin: 0;'>🔱 DEMIR AI TRADING BOT v16.0</h1>
    <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 16px;'>17-Layer Phase 7 Quantum - Deep AI System</p>
</div>
""", unsafe_allow_html=True)

# Current selection display
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    st.metric("📊 Selected Coin", st.session_state.selected_symbol)
with col2:
    st.metric("⏰ Timeframe", st.session_state.selected_interval)
with col3:
    st.metric("🔮 AI Version", "Phase 7 - 17 Layers")

st.markdown("---")

# ============================================================================
# RENDER FUNCTIONS (✅ DEFINED BEFORE TABS)
# ============================================================================

def render_system_health():
    """Render system health monitoring page - COIN SPECIFIC"""
    st.markdown("# 📊 System Health & Layer Monitoring")
    st.markdown("**17-Layer Phase 7 AI System Status & Data Flow Monitoring**")
    st.markdown(f"*Monitoring coin: **{st.session_state.selected_symbol}** ({st.session_state.selected_interval})*")
    
    if not AI_BRAIN_AVAILABLE:
        st.error("❌ AI Brain not loaded. Cannot show system health.")
        st.info("💡 Make sure ai_brain.py is in the same directory and contains make_trading_decision() function.")
        return
    
    # Health check settings
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("### ⚙️ Health Check Settings")
        health_coin = st.selectbox(
            "Coin to Monitor",
            options=st.session_state.watchlist,
            index=st.session_state.watchlist.index(st.session_state.selected_symbol),
            key='health_coin'
        )
        
        health_interval = st.selectbox(
            "Interval",
            options=['1h', '4h', '1d'],
            index=0,
            key='health_interval'
        )
        
        if st.button("🔍 Run Health Check", use_container_width=True):
            st.session_state['run_health_check'] = True
    
    with col2:
        st.markdown(f"## 📊 17-Layer Data Status (Phase 7) - {health_coin} ({health_interval})")
        
        if st.session_state.get('run_health_check', False):
            with st.spinner(f"🔄 Analyzing {health_coin} with 17-Layer Phase 7 system..."):
                try:
                    # ✅ FIXED: Call make_trading_decision (not analyze_with_ai)
                    result = make_trading_decision(
                        symbol=health_coin,
                        timeframe=health_interval,
                        portfolio_value=10000
                    )
                    
                    if result and isinstance(result, dict):
                        # Overall status
                        st.success(f"✅ AI Analysis Complete for {health_coin}")
                        
                        # Key metrics
                        col_a, col_b, col_c, col_d = st.columns(4)
                        
                        with col_a:
                            score = result.get('final_score', 50)
                            st.metric(
                                "Final Score",
                                f"{score:.1f}/100",
                                delta=f"{score-50:.1f} from neutral"
                            )
                        
                        with col_b:
                            signal = result.get('signal', 'NEUTRAL')
                            color = "🟢" if signal == "LONG" else "🔴" if signal == "SHORT" else "⚪"
                            st.metric("Signal", f"{color} {signal}")
                        
                        with col_c:
                            confidence = result.get('confidence', 0)
                            st.metric(
                                "Confidence",
                                f"{confidence:.1%}",
                                delta="High" if confidence > 0.7 else "Moderate" if confidence > 0.5 else "Low"
                            )
                        
                        with col_d:
                            layer_scores = result.get('layer_scores', {})
                            active_layers = sum(1 for score in layer_scores.values() if score is not None)
                            st.metric(
                                "Active Layers",
                                f"{active_layers}/17",
                                delta=f"{(active_layers/17)*100:.0f}%"
                            )
                        
                        st.markdown("---")
                        
                        # Layer breakdown
                        st.markdown("### 🔍 Layer-by-Layer Status")
                        
                        if layer_scores:
                            # Create DataFrame
                            layer_data = []
                            for layer_name, score in layer_scores.items():
                                if score is not None:
                                    status = "✅ Active"
                                    signal_emoji = get_signal_emoji(score)
                                    signal_text = get_signal_text(score)
                                    weight = get_layer_weight(layer_name)
                                    
                                    layer_data.append({
                                        'Layer': layer_name.replace('_', ' ').title(),
                                        'Score': f"{score:.1f}",
                                        'Signal': f"{signal_emoji} {signal_text}",
                                        'Weight': f"{weight}%",
                                        'Status': status
                                    })
                                else:
                                    layer_data.append({
                                        'Layer': layer_name.replace('_', ' ').title(),
                                        'Score': 'N/A',
                                        'Signal': '❌ Failed',
                                        'Weight': f"{get_layer_weight(layer_name)}%",
                                        'Status': '❌ Unavailable'
                                    })
                            
                            df = pd.DataFrame(layer_data)
                            st.dataframe(df, use_container_width=True, height=600)
                            
                            # Summary
                            active_count = sum(1 for s in layer_scores.values() if s is not None)
                            failed_count = len(layer_scores) - active_count
                            
                            st.info(f"""
                            📊 **Summary for {health_coin}:**
                            - Active Layers: {active_count}/17
                            - Failed/Unavailable: {failed_count}
                            - System Health: {(active_count/17)*100:.0f}%
                            - Phase 7 Quantum Layers: 5 layers (Black-Scholes, Kalman, Fractal, Fourier, Copula)
                            """)
                        else:
                            st.warning("⚠️ No layer scores available in result")
                    
                    else:
                        st.error(f"❌ Analysis failed for {health_coin}. Result is None or invalid format.")
                
                except Exception as e:
                    st.error(f"❌ Health check error: {e}")
                    import traceback
                    with st.expander("🔍 See error details"):
                        st.code(traceback.format_exc())
        
        else:
            st.info("ℹ️ Click 'Run Health Check' to analyze 17-layer system status")

def render_ai_trading():
    """Render AI trading analysis page - COIN SPECIFIC"""
    st.markdown("# 🧠 AI Trading Analysis")
    st.markdown("**17-Layer Phase 7 Quantum AI tarafından üretilen real-time trading sinyalleri**")
    st.markdown(f"*Analyzing: **{st.session_state.selected_symbol}** ({st.session_state.selected_interval})*")
    
    if not AI_BRAIN_AVAILABLE:
        st.error("❌ AI Brain not available. Cannot generate trading signals.")
        st.info("💡 Make sure ai_brain.py is in the same directory and contains make_trading_decision() function.")
        return
    
    # Analysis controls
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📊 Current Analysis")
    
    with col2:
        if st.button("🔄 Refresh Analysis", use_container_width=True, type="primary"):
            st.session_state['refresh_trading'] = True
    
    # Run analysis
    with st.spinner(f"🧠 AI analyzing {st.session_state.selected_symbol}..."):
        try:
            # ✅ FIXED: Call make_trading_decision (not analyze_with_ai)
            result = make_trading_decision(
                symbol=st.session_state.selected_symbol,
                timeframe=st.session_state.selected_interval,
                portfolio_value=10000
            )
            
            if not result or not isinstance(result, dict):
                st.error("❌ AI analysis failed. No result returned or invalid format.")
                return
            
            # Store in session
            st.session_state.last_analysis = result
            
            # Display results
            st.markdown("---")
            
            # Main signal box
            signal = result.get('signal', 'NEUTRAL')
            score = result.get('final_score', 50)
            confidence = result.get('confidence', 0)
            
            if signal == "LONG":
                st.success(f"""
                ### 🟢 LONG SIGNAL
                **AI Score:** {score:.1f}/100  
                **Confidence:** {confidence:.1%}  
                **Recommendation:** Consider BUY position for {st.session_state.selected_symbol}
                """)
            
            elif signal == "SHORT":
                st.error(f"""
                ### 🔴 SHORT SIGNAL
                **AI Score:** {score:.1f}/100  
                **Confidence:** {confidence:.1%}  
                **Recommendation:** Consider SELL position for {st.session_state.selected_symbol}
                """)
            
            else:
                st.info(f"""
                ### ⚪ NEUTRAL
                **AI Score:** {score:.1f}/100  
                **Confidence:** {confidence:.1%}  
                **Recommendation:** No strong signal detected for {st.session_state.selected_symbol}
                """)
            
            # Key metrics
            col_a, col_b, col_c, col_d = st.columns(4)
            
            with col_a:
                entry = result.get('entry_price', 0)
                st.metric("Entry Price", f"${entry:.2f}" if entry > 0 else "N/A")
            
            with col_b:
                sl = result.get('stop_loss', 0)
                st.metric("Stop Loss", f"${sl:.2f}" if sl > 0 else "N/A")
            
            with col_c:
                tp1 = result.get('tp1', 0)
                st.metric("Take Profit 1", f"${tp1:.2f}" if tp1 > 0 else "N/A")
            
            with col_d:
                risk_reward = result.get('risk_reward_ratio', 0)
                st.metric("Risk/Reward", f"{risk_reward:.2f}" if risk_reward > 0 else "N/A")
            
            st.markdown("---")
            
            # Detailed layer breakdown
            st.markdown("### 📊 17-Layer Detailed Breakdown (Phase 7)")
            st.markdown(f"*Her layer'ın katkısı ve sinyali - **{result['symbol']}** ({result.get('interval', '1h')}) için*")
            
            layer_scores = result.get('layer_scores', {})
            
            if layer_scores:
                # Create layer data
                layers_data = []
                for layer_name, score in layer_scores.items():
                    if score is not None:
                        weight = get_layer_weight(layer_name)
                        signal_emoji = get_signal_emoji(score)
                        signal_text = get_signal_text(score)
                        
                        layers_data.append({
                            'Layer': layer_name.replace('_', ' ').title(),
                            'Score': f"{score:.1f}",
                            'Weight': f"{weight}%",
                            'Signal': f"{signal_emoji} {signal_text}",
                            'Status': '✅ Active'
                        })
                    else:
                        layers_data.append({
                            'Layer': layer_name.replace('_', ' ').title(),
                            'Score': 'N/A',
                            'Weight': f"{get_layer_weight(layer_name)}%",
                            'Signal': '❌ Failed',
                            'Status': '❌ Unavailable'
                        })
                
                df_layers = pd.DataFrame(layers_data)
                df_layers = df_layers.sort_values('Score', ascending=False)
                
                st.dataframe(df_layers, use_container_width=True, height=500)
                
                # Layer health summary
                active_count = sum(1 for s in layer_scores.values() if s is not None)
                st.info(f"""
                📊 **Layer Health:**
                - Active Layers: {active_count}/17
                - System Health: {(active_count/17)*100:.0f}%
                """)
            
            else:
                st.warning("⚠️ Layer scores not available in result")
            
            # Trading recommendations
            if signal != "NEUTRAL":
                st.markdown("---")
                st.markdown("### 💡 Trading Recommendations")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Entry Strategy:**")
                    st.markdown(f"- Entry: ${result.get('entry_price', 0):.2f}")
                    st.markdown(f"- Position Size: {result.get('position_size', 0):.2%} of portfolio")
                    st.markdown(f"- Leverage: {result.get('leverage', 1):.1f}x (if applicable)")
                
                with col2:
                    st.markdown("**Exit Strategy:**")
                    st.markdown(f"- Stop Loss: ${result.get('stop_loss', 0):.2f}")
                    st.markdown(f"- TP1: ${result.get('tp1', 0):.2f}")
                    st.markdown(f"- TP2: ${result.get('tp2', 0):.2f}")
                    st.markdown(f"- TP3: ${result.get('tp3', 0):.2f}")
    
    # Chart display
    if CHART_AVAILABLE:
        st.markdown("---")
        st.markdown("### 📈 Interactive Price Chart")
        
        try:
            chart_gen = ChartGenerator(theme='dark')
            df = chart_gen.fetch_ohlcv(
                result['symbol'], 
                interval=result.get('interval', '1h'), 
                days=7
            )
            
            if not df.empty:
                fig = chart_gen.create_candlestick_chart(
                    df,
                    symbol=result['symbol'],
                    show_volume=True,
                    indicators=['RSI', 'MACD', 'Bollinger'],
                    height=600
                )
                
                # Add trade levels (only if valid trade)
                if decision != "NEUTRAL" and entry > 0:
                    chart_gen.add_trade_levels(
                        fig,
                        entry_price=result.get('entry_price', 0),
                        stop_loss=result.get('stop_loss', 0),
                        take_profits=[tp1, tp2, tp3],
                        signal=decision
                    )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Chart data not available")
                
        except Exception as e:
            st.error(f"❌ Chart generation failed: {e}")
        
        except Exception as e:
            st.error(f"❌ Analysis error: {e}")
            import traceback
            with st.expander("🔍 See error details"):
                st.code(traceback.format_exc())

def render_backtest():
    """Render backtest results page - COIN SPECIFIC"""
    st.markdown("# 📈 Backtest Results - Performance Analysis")
    st.markdown("**Historical testing - Geçmiş verilerde AI performansı**")
    st.markdown(f"*Selected: **{st.session_state.selected_symbol}** ({st.session_state.selected_interval})*")
    
    if not BACKTEST_AVAILABLE:
        st.warning("⚠️ Backtest Engine not loaded")
        st.info("💡 Make sure backtest_engine.py is available")
        return
    
    # Backtest settings
    st.markdown("---")
    st.markdown("### ⚙️ Backtest Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        backtest_coin = st.selectbox(
            "Coin to Backtest",
            options=st.session_state.watchlist,
            index=st.session_state.watchlist.index(st.session_state.selected_symbol),
            key='backtest_coin'
        )
    
    with col2:
        backtest_days = st.number_input(
            "Days to Test",
            min_value=7,
            max_value=365,
            value=30,
            step=7,
            key='backtest_days'
        )
    
    with col3:
        backtest_interval = st.selectbox(
            "Interval",
            options=['1h', '4h', '1d'],
            index=0,
            key='backtest_interval'
        )
    
    if st.button("▶️ Run Backtest", type="primary", use_container_width=True):
        with st.spinner(f"🔄 Running backtest for {backtest_coin}..."):
            try:
                # Run backtest
                if hasattr(BacktestEngine, '__call__'):
                    engine = BacktestEngine()
                    results = engine.run(
                        symbol=backtest_coin,
                        interval=backtest_interval,
                        days=backtest_days
                    )
                else:
                    from backtest_engine import run_backtest
                    results = run_backtest(
                        symbol=backtest_coin,
                        interval=backtest_interval,
                        days=backtest_days
                    )
                
                if results and isinstance(results, dict):
                    st.session_state.backtest_results = results
                    st.success(f"✅ Backtest complete for {backtest_coin}")
                    
                    # Display metrics
                    st.markdown("---")
                    st.markdown("### 📊 Performance Metrics")
                    
                    col_a, col_b, col_c, col_d = st.columns(4)
                    
                    with col_a:
                        win_rate = results.get('win_rate', 0)
                        st.metric("Win Rate", f"{win_rate:.1%}")
                    
                    with col_b:
                        total_return = results.get('total_return', 0)
                        st.metric("Total Return", f"{total_return:.2%}")
                    
                    with col_c:
                        sharpe = results.get('sharpe_ratio', 0)
                        st.metric("Sharpe Ratio", f"{sharpe:.2f}")
                    
                    with col_d:
                        max_dd = results.get('max_drawdown', 0)
                        st.metric("Max Drawdown", f"{max_dd:.2%}")
                    
                    # More details
                    st.markdown("---")
                    st.markdown("### 📋 Detailed Results")
                    
                    results_df = pd.DataFrame([results])
                    st.dataframe(results_df, use_container_width=True)
                
                else:
                    st.error(f"❌ Backtest failed for {backtest_coin}")
            
            except Exception as e:
                st.error(f"❌ Backtest error: {e}")
                import traceback
                with st.expander("🔍 See error details"):
                    st.code(traceback.format_exc())

def render_settings():
    """Render settings page"""
    st.markdown("# ⚙️ Settings & Configuration")
    st.markdown("**System settings and watchlist management**")
    
    # Watchlist management
    st.markdown("---")
    st.markdown("### 🪙 Watchlist Management")
    
    # Add new coin
    col1, col2 = st.columns([3, 1])
    with col1:
        new_coin = st.text_input("Add New Coin", placeholder="BTCUSDT", key='new_coin_input')
    with col2:
        if st.button("➕ Add", use_container_width=True, key='add_coin_btn'):
            if new_coin and new_coin.upper() not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_coin.upper())
                st.success(f"✅ {new_coin.upper()} added!")
                st.rerun()
            elif new_coin.upper() in st.session_state.watchlist:
                st.warning(f"⚠️ {new_coin.upper()} already in watchlist")
    
    # Current watchlist
    st.markdown("**Current Watchlist:**")
    for idx, coin in enumerate(st.session_state.watchlist):
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.text(f"{idx+1}. {coin}")
        with col_b:
            if st.button("🗑️ Remove", key=f"remove_{coin}_{idx}"):
                if len(st.session_state.watchlist) > 1:  # Keep at least one
                    st.session_state.watchlist.remove(coin)
                    if st.session_state.selected_symbol == coin:
                        st.session_state.selected_symbol = st.session_state.watchlist[0]
                    st.rerun()
                else:
                    st.warning("⚠️ Cannot remove last coin")
    
    st.markdown("---")
    
    # System info
    st.markdown("### 📊 System Information")
    st.info(f"""
    **Version:** v16.0 - Phase 7 Quantum  
    **AI Brain:** {'✅ Active (make_trading_decision)' if AI_BRAIN_AVAILABLE else '❌ Inactive'}  
    **Backtest:** {'✅ Active' if BACKTEST_AVAILABLE else '❌ Inactive'}  
    **Charts:** {'✅ Active' if CHART_AVAILABLE else '❌ Inactive'}  
    **Selected Coin:** {st.session_state.selected_symbol}  
    **Interval:** {st.session_state.selected_interval}  
    **Login:** NO LOGIN REQUIRED (v16.0)  
    **Total Layers:** 17 (Phase 7 Quantum)
    """)
    
    # Advanced settings
    st.markdown("---")
    st.markdown("### 🔧 Advanced Settings")
    
    if st.button("🔄 Clear Cache & Restart", use_container_width=True):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("✅ Cache cleared!")
        time.sleep(1)
        st.rerun()
    
    if st.button("⚠️ Reset All Settings", use_container_width=True, type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("✅ All settings reset!")
        time.sleep(1)
        st.rerun()

# ============================================================================
# MAIN APP - TABS (✅ CALLED AFTER FUNCTION DEFINITIONS)
# ============================================================================

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 System Health",
    "🧠 AI Trading",
    "📈 Backtest",
    "⚙️ Settings"
])

# Render tabs
with tab1:
    render_system_health()

with tab2:
    render_ai_trading()

with tab3:
    render_backtest()

with tab4:
    render_settings()

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    <p>🔱 DEMIR AI Trading Bot v16.0 - Phase 7 Quantum</p>
    <p><em>17-Layer Phase 7 System | NO LOGIN Required | Made with ❤️ by Patron</em></p>
    <p style='font-size: 12px; margin-top: 10px;'>
        AI Brain: make_trading_decision() | 
        All Fixes Applied: Phase 7 ✅ | NO LOGIN ✅ | Function Order ✅
    </p>
</div>
""", unsafe_allow_html=True)
