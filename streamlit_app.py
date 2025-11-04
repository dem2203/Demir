# streamlit_app.py v16.0 - PHASE 7 QUANTUM (NO LOGIN)

"""
🔱 DEMIR AI TRADING BOT - Streamlit UI v14.3 ULTIMATE
====================================================================
Date: 4 Kasım 2025, 00:18 CET
Version: 16.0 - PHASE 7 QUANTUM + NO LOGIN + AI BRAIN FIXED

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
    from backtest_engine import run_backtest
    BACKTEST_AVAILABLE = True
    print("✅ Streamlit v16.0: Backtest Engine loaded")
except Exception as e:
    print(f"⚠️ Streamlit v16.0: Backtest import failed: {e}")
    run_backtest = None

# Chart Generator
CHART_AVAILABLE = False
try:
    from chart_generator import create_price_chart
    CHART_AVAILABLE = True
    print("✅ Streamlit v16.0: Chart Generator loaded")
except Exception as e:
    print(f"⚠️ Streamlit v16.0: Chart Generator import failed: {e}")
    create_price_chart = None

# Authentication - Not used in v16.0 (NO LOGIN)
AUTH_AVAILABLE = False
try:
    from auth_system import login, register, is_logged_in
    AUTH_AVAILABLE = True
    print("✅ Streamlit v16.0: Auth System loaded (not used)")
except Exception as e:
    print(f"⚠️ Streamlit v16.0: Auth import failed: {e}")

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = True  # ✅ v16.0: NO LOGIN REQUIRED

if 'username' not in st.session_state:
    st.session_state.username = 'demo_user'

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']

if 'selected_symbol' not in st.session_state:
    st.session_state.selected_symbol = 'BTCUSDT'

if 'selected_interval' not in st.session_state:
    st.session_state.selected_interval = '1h'

# ============================================================================
# SIDEBAR - GLOBAL SETTINGS
# ============================================================================
with st.sidebar:
    st.markdown("# 🔱 DEMIR AI Bot v16.0")
    st.markdown("*17-Layer Phase 7 System*")
    st.markdown("---")
    
    # User info
    st.markdown(f"👤 **User:** {st.session_state.username}")
    st.markdown(f"🔐 **Status:** {'Logged In' if st.session_state.logged_in else 'Guest'}")
    
    st.markdown("---")
    
    # Coin selection (GLOBAL)
    st.markdown("### 🪙 Global Coin Selection")
    st.markdown("*Bu seçim tüm sayfalarda geçerlidir*")
    
    selected_coin = st.selectbox(
        "Select Trading Pair",
        options=st.session_state.watchlist,
        index=st.session_state.watchlist.index(st.session_state.selected_symbol),
        key='sidebar_coin_selector'
    )
    
    # Update global state
    if selected_coin != st.session_state.selected_symbol:
        st.session_state.selected_symbol = selected_coin
        st.rerun()
    
    st.markdown("---")
    
    # Interval selection (GLOBAL)
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
    
    # Quick stats
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
    
    st.markdown("---")
    
    # Quick actions
    if st.button("🔄 Refresh All Data", use_container_width=True):
        st.rerun()
    
    if st.button("⚙️ Reset Settings", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ============================================================================
# MAIN APP - TABS
# ============================================================================

# Header
st.markdown(f"""
<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #26a69a 0%, #1e8378 100%); border-radius: 10px; margin-bottom: 20px;'>
    <h1 style='color: white; margin: 0;'>🔱 DEMIR AI TRADING BOT v16.0</h1>
    <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 16px;'>17-Layer Phase 7 Quantum - Deep AI System</p>
</div>
""", unsafe_allow_html=True)

# Show current selection prominently
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    st.metric("📊 Selected Coin", st.session_state.selected_symbol)
with col2:
    st.metric("⏰ Timeframe", st.session_state.selected_interval)
with col3:
    st.metric("🔮 AI Version", "Phase 7 - 17 Layers")

st.markdown("---")

# Main application tabs (NO LOGIN REQUIRED)
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 System Health",
    "🧠 AI Trading",
    "📈 Backtest",
    "⚙️ Settings"
])

with tab1:
    render_system_health()

with tab2:
    render_ai_trading()

with tab3:
    render_backtest()

with tab4:
    render_settings()

# ============================================================================
# SYSTEM HEALTH PAGE
# ============================================================================

def render_system_health():
    """Render system health monitoring page - COIN SPECIFIC"""
    st.markdown("# 📊 System Health & Layer Monitoring")
    st.markdown("**17-Layer Phase 7 AI System Status & Data Flow Monitoring**")
    st.markdown(f"*Monitoring coin: **{st.session_state.selected_symbol}** ({st.session_state.selected_interval})*")
    
    if not AI_BRAIN_AVAILABLE:
        st.error("❌ AI Brain not loaded. Cannot show system health.")
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
            with st.spinner(f"🔄 Analyzing {health_coin} with 17 layers..."):
                try:
                    # Run AI analysis
                    result = make_trading_decision(health_coin, health_interval)
                    
                    if result:
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
                                delta="High" if confidence > 0.7 else "Low"
                            )
                        
                        with col_d:
                            active_layers = result.get('active_layers', 0)
                            total_layers = result.get('total_layers', 17)
                            st.metric(
                                "Active Layers",
                                f"{active_layers}/{total_layers}",
                                delta=f"{active_layers/total_layers:.0%}"
                            )
                        
                        st.markdown("---")
                        
                        # Layer breakdown
                        st.markdown("### 🔍 Layer-by-Layer Status")
                        
                        layer_scores = result.get('layers', {})
                        
                        if layer_scores:
                            # Create DataFrame
                            layer_data = []
                            for layer_name, score in layer_scores.items():
                                if score is not None:
                                    status = "✅ Active" if score > 0 else "⚠️ Neutral"
                                    signal_emoji = "🟢" if score > 60 else "🔴" if score < 40 else "⚪"
                                    
                                    layer_data.append({
                                        'Layer': layer_name.replace('_', ' ').title(),
                                        'Score': f"{score:.1f}",
                                        'Signal': signal_emoji,
                                        'Status': status
                                    })
                                else:
                                    layer_data.append({
                                        'Layer': layer_name.replace('_', ' ').title(),
                                        'Score': 'N/A',
                                        'Signal': '❌',
                                        'Status': '❌ Failed'
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
                            """)
                        
                        else:
                            st.warning("⚠️ No layer scores available")
                    
                    else:
                        st.error(f"❌ Analysis failed for {health_coin}")
                
                except Exception as e:
                    st.error(f"❌ Health check error: {e}")
                    import traceback
                    st.code(traceback.format_exc())
        
        else:
            st.info("ℹ️ Click 'Run Health Check' to analyze layer status")

# ============================================================================
# AI TRADING PAGE
# ============================================================================

def render_ai_trading():
    """Render AI trading analysis page - COIN SPECIFIC"""
    st.markdown("# 🧠 AI Trading Analysis")
    st.markdown("**17-Layer Phase 7 Quantum AI tarafından üretilen real-time trading sinyalleri**")
    st.markdown(f"*Analyzing: **{st.session_state.selected_symbol}** ({st.session_state.selected_interval})*")
    
    if not AI_BRAIN_AVAILABLE:
        st.error("❌ AI Brain not available. Cannot generate trading signals.")
        st.info("💡 Make sure ai_brain.py is in the same directory.")
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
            result = make_trading_decision(
                st.session_state.selected_symbol,
                st.session_state.selected_interval
            )
            
            if not result:
                st.error("❌ AI analysis failed. No result returned.")
                return
            
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
                st.info("ℹ️ No trade signal generated (NEUTRAL decision). Layer breakdown available below.")
            
            # Detailed metrics
            st.markdown("### 📊 17-Layer Detailed Breakdown (Phase 7)")
            st.markdown(f"*Her layer'ın katkısı ve sinyali - **{result['symbol']}** ({result['interval']}) için*")
            
            layer_scores = result.get('layer_scores', {})
            
            if layer_scores:
                # Create layerdata
                layers_data = []
                for layer_name, score in layer_scores.items():
                    if score is not None:
                        # Get weight
                        weight = get_layer_weight(layer_name)
                        layers_data.append({
                            'Layer': layer_name.replace('_', ' ').title(),
                            'Score': score,
                            'Weight': weight,
                            'Signal': '🟢 LONG' if score >= 60 else '🔴 SHORT' if score <= 40 else '⚪ NEUTRAL'
                        })
                
                df_layers = pd.DataFrame(layers_data)
                df_layers = df_layers.sort_values('Score', ascending=False)
                
                st.dataframe(df_layers, use_container_width=True, height=450)
            
            else:
                st.warning("⚠️ Layer scores not available in result")
            
            # Chart (if available)
            if CHART_AVAILABLE:
                st.markdown("---")
                st.markdown(f"### 📈 Price Chart - {st.session_state.selected_symbol}")
                
                try:
                    chart = create_price_chart(
                        st.session_state.selected_symbol,
                        st.session_state.selected_interval
                    )
                    st.plotly_chart(chart, use_container_width=True)
                except Exception as e:
                    st.warning(f"⚠️ Chart generation failed: {e}")
        
        except Exception as e:
            st.error(f"❌ Analysis error: {e}")
            import traceback
            st.code(traceback.format_exc())

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_layer_weight(layer_name):
    """Get weight percentage for layer - PHASE 7 QUANTUM"""
    weights = {
        # Phase 1-6 Layers (70%)
        'strategy': 15,
        'multi_timeframe': 6,
        'macro': 6,
        'gold': 4,
        'dominance': 5,
        'cross_asset': 8,
        'vix': 5,
        'rates': 5,
        'trad_markets': 6,
        'news': 8,
        'monte_carlo': 8,
        'kelly': 8,
        
        # Phase 7 Quantum Layers (30%)
        'black_scholes': 8,
        'kalman': 7,
        'fractal': 6,
        'fourier': 5,
        'copula': 4
    }
    return weights.get(layer_name, 1)

# ============================================================================
# BACKTEST RESULTS PAGE
# ============================================================================

def render_backtest():
    """Render backtest results page - COIN SPECIFIC"""
    st.markdown("# 📈 Backtest Results - Performance Analysis")
    st.markdown("**Historical testing geçmiş verilerde AI performansı**")
    
    if not BACKTEST_AVAILABLE:
        st.warning("⚠️ Backtest Engine not loaded")
        return
    
    # Backtest settings - CRITICAL: Coin selection
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
            step=7
        )
    
    with col3:
        backtest_interval = st.selectbox(
            "Interval",
            options=['1h', '4h', '1d'],
            index=0
        )
    
    if st.button("▶️ Run Backtest", type="primary", use_container_width=True):
        with st.spinner(f"🔄 Running backtest for {backtest_coin}..."):
            try:
                results = run_backtest(
                    symbol=backtest_coin,
                    interval=backtest_interval,
                    days=backtest_days
                )
                
                if results:
                    st.success(f"✅ Backtest complete for {backtest_coin}")
                    
                    # Display metrics
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
                    st.markdown("### 📊 Detailed Results")
                    
                    results_df = pd.DataFrame([results])
                    st.dataframe(results_df, use_container_width=True)
                
                else:
                    st.error(f"❌ Backtest failed for {backtest_coin}")
            
            except Exception as e:
                st.error(f"❌ Backtest error: {e}")

# ============================================================================
# SETTINGS PAGE
# ============================================================================

def render_settings():
    """Render settings page"""
    st.markdown("# ⚙️ Settings & Configuration")
    
    st.markdown("### 🪙 Watchlist Management")
    
    # Add coin
    col1, col2 = st.columns([3, 1])
    with col1:
        new_coin = st.text_input("Add New Coin", placeholder="BTCUSDT")
    with col2:
        if st.button("➕ Add", use_container_width=True):
            if new_coin and new_coin not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_coin.upper())
                st.success(f"✅ {new_coin} added!")
                st.rerun()
    
    # Current watchlist
    st.markdown("**Current Watchlist:**")
    for coin in st.session_state.watchlist:
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.text(coin)
        with col_b:
            if st.button("🗑️", key=f"remove_{coin}"):
                st.session_state.watchlist.remove(coin)
                st.rerun()
    
    st.markdown("---")
    
    # System info
    st.markdown("### 📊 System Information")
    st.info(f"""
    **Version:** v16.0 - Phase 7 Quantum  
    **AI Brain:** {'✅ Active' if AI_BRAIN_AVAILABLE else '❌ Inactive'}  
    **Backtest:** {'✅ Active' if BACKTEST_AVAILABLE else '❌ Inactive'}  
    **Charts:** {'✅ Active' if CHART_AVAILABLE else '❌ Inactive'}  
    **Selected Coin:** {st.session_state.selected_symbol}  
    **Interval:** {st.session_state.selected_interval}
    """)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    <p>🔱 DEMIR AI Trading Bot v16.0 - Phase 7 Quantum</p>
    <p>*17-Layer Phase 7 System* | Made with ❤️ by Patron</p>
</div>
""", unsafe_allow_html=True)
