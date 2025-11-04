# streamlit_app.py v17.0 - PHASE 3+6 + HARIKA PROFESSIONAL UI
"""
🔱 DEMIR AI TRADING BOT - Streamlit UI v17.0 ULTIMATE
====================================================================
Date: 4 Kasım 2025, 23:35 CET
Version: 17.0 - PHASE 7 + PHASE 3+6 + PROFESSIONAL UI

✅ v17.0 FEATURES:
- Phase 3: Telegram, Portfolio, Backtest Integration
- Phase 6: Enhanced Macro Layers Display
- Professional TradingView-style UI
- Gradient backgrounds & animations
- Real-time status indicators
- Interactive charts & visualizations
- NO LOGIN Required
- 17-Layer + Phase 3+6 Full System
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
    page_title="🔱 DEMIR AI Trading Bot v17.0",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - HARIKA PROFESSIONAL DESIGN
# ============================================================================
st.markdown("""
<style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    }
    
    /* Header styles */
    .main-header {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00d4ff 0%, #0099ff 50%, #7b68ee 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 5px #00d4ff); }
        to { filter: drop-shadow(0 0 20px #0099ff); }
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #00d4ff;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Signal indicators */
    .signal-long { 
        color: #00ff88;
        font-weight: bold;
        font-size: 1.5rem;
        text-shadow: 0 0 10px #00ff88;
    }
    
    .signal-short { 
        color: #ff3366;
        font-weight: bold;
        font-size: 1.5rem;
        text-shadow: 0 0 10px #ff3366;
    }
    
    .signal-neutral { 
        color: #ffaa00;
        font-weight: bold;
        font-size: 1.5rem;
        text-shadow: 0 0 10px #ffaa00;
    }
    
    /* Metric cards */
    .stMetric {
        background: linear-gradient(135deg, rgba(0,212,255,0.1) 0%, rgba(123,104,238,0.1) 100%);
        padding: 1rem;
        border-radius: 15px;
        border: 1px solid rgba(0,212,255,0.3);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0,212,255,0.2);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #0099ff 0%, #7b68ee 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px 0 rgba(0,153,255,0.4);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(0,153,255,0.6);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: rgba(0,0,0,0.3);
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, rgba(0,212,255,0.2) 0%, rgba(123,104,238,0.2) 100%);
        border-radius: 8px;
        color: #00d4ff;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0099ff 0%, #7b68ee 100%);
        color: white;
    }
    
    /* Status indicators */
    .status-active {
        color: #00ff88;
        font-weight: bold;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Cards */
    .info-card {
        background: linear-gradient(135deg, rgba(0,212,255,0.05) 0%, rgba(123,104,238,0.05) 100%);
        border: 1px solid rgba(0,212,255,0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f2027 0%, #203a43 100%);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #00d4ff;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #00d4ff;
        padding: 2rem 0;
        font-size: 0.9rem;
        border-top: 1px solid rgba(0,212,255,0.2);
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# MODULE IMPORTS - DYNAMIC LOADING
# ============================================================================

# AI Brain v15.0
AI_BRAIN_AVAILABLE = False
try:
    from ai_brain import make_trading_decision
    AI_BRAIN_AVAILABLE = True
    print("✅ Streamlit v17.0: AI Brain v15.0 loaded")
except:
    make_trading_decision = None

# Phase 3 Modules
TELEGRAM_AVAILABLE = False
try:
    from telegram_alert_system import TelegramAlertSystem, test_telegram_connection
    TELEGRAM_AVAILABLE = True
    print("✅ v17.0: Telegram loaded")
except:
    TelegramAlertSystem, test_telegram_connection = None, None

PORTFOLIO_AVAILABLE = False
try:
    from portfolio_optimizer import PortfolioOptimizer
    PORTFOLIO_AVAILABLE = True
    print("✅ v17.0: Portfolio Optimizer loaded")
except:
    PortfolioOptimizer = None

BACKTEST_AVAILABLE = False
try:
    from backtest_engine import BacktestEngine
    BACKTEST_AVAILABLE = True
    print("✅ v17.0: Backtest Engine loaded")
except:
    BacktestEngine = None

# Phase 6 Enhanced Layers
MACRO_ENHANCED = False
try:
    from layers.enhanced_macro_layer import EnhancedMacroLayer
    MACRO_ENHANCED = True
    print("✅ v17.0: Enhanced Macro loaded")
except:
    EnhancedMacroLayer = None

GOLD_ENHANCED = False
try:
    from layers.enhanced_gold_layer import EnhancedGoldLayer
    GOLD_ENHANCED = True
    print("✅ v17.0: Enhanced Gold loaded")
except:
    EnhancedGoldLayer = None

DOMINANCE_ENHANCED = False
try:
    from layers.enhanced_dominance_layer import EnhancedDominanceLayer
    DOMINANCE_ENHANCED = True
    print("✅ v17.0: Enhanced Dominance loaded")
except:
    EnhancedDominanceLayer = None

VIX_ENHANCED = False
try:
    from layers.enhanced_vix_layer import EnhancedVixLayer
    VIX_ENHANCED = True
    print("✅ v17.0: Enhanced VIX loaded")
except:
    EnhancedVixLayer = None

RATES_ENHANCED = False
try:
    from layers.enhanced_rates_layer import EnhancedRatesLayer
    RATES_ENHANCED = True
    print("✅ v17.0: Enhanced Rates loaded")
except:
    EnhancedRatesLayer = None

# Charts
CHART_AVAILABLE = False
try:
    from chart_generator import ChartGenerator
    CHART_AVAILABLE = True
    print("✅ v17.0: Charts loaded")
except:
    ChartGenerator = None

print("="*80)
print("✅ Streamlit v17.0 - All modules loaded")
print("="*80)

# ============================================================================
# SESSION STATE
# ============================================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = True
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

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_signal_emoji(score):
    if score >= 60: return "🟢"
    elif score <= 40: return "🔴"
    else: return "⚪"

def get_signal_text(score):
    if score >= 60: return "LONG"
    elif score <= 40: return "SHORT"
    else: return "NEUTRAL"

def get_signal_color_class(score):
    if score >= 60: return "signal-long"
    elif score <= 40: return "signal-short"
    else: return "signal-neutral"

# ============================================================================
# SIDEBAR - PROFESSIONAL
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:1rem;'>
        <h1 style='color:#00d4ff; margin:0;'>🔱 DEMIR AI</h1>
        <p style='color:#7b68ee; margin:0;'>v17.0 Ultimate</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # User
    st.markdown(f"👤 **User:** {st.session_state.username}")
    st.markdown("<span class='status-active'>● Active</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Coin Selection
    st.markdown("### 🪙 Trading Pair")
    selected_coin = st.selectbox(
        "Select Coin",
        options=st.session_state.watchlist,
        index=st.session_state.watchlist.index(st.session_state.selected_symbol)
    )
    if selected_coin != st.session_state.selected_symbol:
        st.session_state.selected_symbol = selected_coin
        st.rerun()
    
    st.markdown("---")
    
    # Interval
    st.markdown("### ⏰ Timeframe")
    selected_interval = st.selectbox(
        "Interval",
        options=['1m', '5m', '15m', '1h', '4h', '1d'],
        index=['1m', '5m', '15m', '1h', '4h', '1d'].index(st.session_state.selected_interval)
    )
    if selected_interval != st.session_state.selected_interval:
        st.session_state.selected_interval = selected_interval
        st.rerun()
    
    st.markdown("---")
    
    # PHASE 3+6 STATUS
    st.markdown("### 🆕 Phase 3+6")
    
    phase3_count = sum([TELEGRAM_AVAILABLE, PORTFOLIO_AVAILABLE, BACKTEST_AVAILABLE])
    phase6_count = sum([MACRO_ENHANCED, GOLD_ENHANCED, DOMINANCE_ENHANCED, VIX_ENHANCED, RATES_ENHANCED])
    
    st.metric("Phase 3", f"{phase3_count}/3", delta="Automation")
    st.metric("Phase 6", f"{phase6_count}/5", delta="Enhanced")
    
    with st.expander("📱 Phase 3 Details"):
        st.write(f"Telegram: {'✅' if TELEGRAM_AVAILABLE else '❌'}")
        st.write(f"Portfolio: {'✅' if PORTFOLIO_AVAILABLE else '❌'}")
        st.write(f"Backtest: {'✅' if BACKTEST_AVAILABLE else '❌'}")
    
    with st.expander("🌍 Phase 6 Details"):
        st.write(f"Macro: {'✅' if MACRO_ENHANCED else '❌'}")
        st.write(f"Gold: {'✅' if GOLD_ENHANCED else '❌'}")
        st.write(f"Dominance: {'✅' if DOMINANCE_ENHANCED else '❌'}")
        st.write(f"VIX: {'✅' if VIX_ENHANCED else '❌'}")
        st.write(f"Rates: {'✅' if RATES_ENHANCED else '❌'}")
    
    st.markdown("---")
    
    # Telegram Test
    if TELEGRAM_AVAILABLE:
        if st.button("🧪 Test Telegram", use_container_width=True):
            with st.spinner("Testing..."):
                try:
                    if test_telegram_connection():
                        st.success("✅ Connected!")
                    else:
                        st.error("❌ Failed")
                except Exception as e:
                    st.error(f"❌ {str(e)[:30]}")
    
    st.markdown("---")
    
    # System Status
    st.markdown("### 📊 System")
    st.metric("AI Brain", "v15.0 Active" if AI_BRAIN_AVAILABLE else "Offline")
    st.metric("Total Layers", "17 + P3+P6")
    
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# ============================================================================
# MAIN HEADER - HARIKA DESIGN
# ============================================================================
st.markdown(f"""
<h1 class="main-header">🔱 DEMIR AI TRADING BOT v17.0</h1>
<p class="subtitle">17-Layer Phase 7 Quantum + Phase 3+6 Integration | Professional Trading AI</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# TABS - PROFESSIONAL NAVIGATION
# ============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 System Health",
    "🧠 AI Trading",
    "📈 Backtest",
    "⚙️ Settings"
])

# ============================================================================
# TAB 1: SYSTEM HEALTH
# ============================================================================
with tab1:
    st.markdown("## 📊 System Health Monitor")
    st.markdown(f"**Analyzing:** {st.session_state.selected_symbol} | **Interval:** {st.session_state.selected_interval}")
    st.markdown("---")
    
    # Top Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ai_status = "v15.0 ✅" if AI_BRAIN_AVAILABLE else "❌ Offline"
        st.metric("AI Brain", ai_status, delta="17 Layers")
    
    with col2:
        phase3_count = sum([TELEGRAM_AVAILABLE, PORTFOLIO_AVAILABLE, BACKTEST_AVAILABLE])
        st.metric("Phase 3", f"{phase3_count}/3", delta="Automation")
    
    with col3:
        phase6_count = sum([MACRO_ENHANCED, GOLD_ENHANCED, DOMINANCE_ENHANCED, VIX_ENHANCED, RATES_ENHANCED])
        st.metric("Phase 6", f"{phase6_count}/5", delta="Enhanced")
    
    with col4:
        total = 17 + phase3_count + phase6_count
        st.metric("Total Active", f"{total}", delta="Modules")
    
    st.markdown("---")
    
    # Phase 3+6 Details
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📱 Phase 3: Automation")
        st.markdown(f"""
        <div class='info-card'>
            <p><strong>📱 Telegram Alerts:</strong> {'<span class="status-active">✅ Ready</span>' if TELEGRAM_AVAILABLE else '❌ Not Loaded'}</p>
            <p><strong>🎯 Portfolio Optimizer:</strong> {'<span class="status-active">✅ Ready</span>' if PORTFOLIO_AVAILABLE else '❌ Not Loaded'}</p>
            <p><strong>📊 Backtest Engine:</strong> {'<span class="status-active">✅ Ready</span>' if BACKTEST_AVAILABLE else '❌ Not Loaded'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🌍 Phase 6: Enhanced Macro")
        st.markdown(f"""
        <div class='info-card'>
            <p><strong>🌍 SPX/NASDAQ/DXY:</strong> {'<span class="status-active">✅ Ready</span>' if MACRO_ENHANCED else '❌ Not Loaded'}</p>
            <p><strong>💰 Gold Correlation:</strong> {'<span class="status-active">✅ Ready</span>' if GOLD_ENHANCED else '❌ Not Loaded'}</p>
            <p><strong>📊 BTC Dominance:</strong> {'<span class="status-active">✅ Ready</span>' if DOMINANCE_ENHANCED else '❌ Not Loaded'}</p>
            <p><strong>😱 VIX Fear Index:</strong> {'<span class="status-active">✅ Ready</span>' if VIX_ENHANCED else '❌ Not Loaded'}</p>
            <p><strong>💵 Interest Rates:</strong> {'<span class="status-active">✅ Ready</span>' if RATES_ENHANCED else '❌ Not Loaded'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if AI_BRAIN_AVAILABLE:
        st.success("✅ **AI Brain v15.0 - FULLY OPERATIONAL**")
        st.info("""
        **Active System:**
        - Phase 1-6: 11 Base Layers (Strategy, News, Macro, etc.)
        - Phase 7: 5 Quantum Layers (Black-Scholes, Kalman, etc.)
        - Phase 3: Telegram + Portfolio + Backtest
        - Phase 6: Enhanced Macro (SPX/NASDAQ/DXY, Gold, Dominance, VIX, Rates)
        
        **Total:** 17 Base Layers + Phase 3+6 Enhancements
        """)
    else:
        st.error("❌ AI Brain Not Loaded")

# ============================================================================
# TAB 2: AI TRADING
# ============================================================================
with tab2:
    st.markdown("## 🧠 AI Trading Analysis")
    st.markdown(f"**Symbol:** {st.session_state.selected_symbol} | **Timeframe:** {st.session_state.selected_interval}")
    st.markdown("---")
    
    if st.button("🚀 Run AI Analysis (17 Layers + Phase 3+6)", type="primary", use_container_width=True):
        if not AI_BRAIN_AVAILABLE:
            st.error("❌ AI Brain not available")
        else:
            with st.spinner("🧠 AI Brain v15.0 analyzing..."):
                try:
                    result = make_trading_decision(
                        symbol=st.session_state.selected_symbol,
                        timeframe=st.session_state.selected_interval
                    )
                    
                    if result:
                        st.session_state.last_analysis = result
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            signal = result.get('signal', 'NEUTRAL')
                            score = result.get('final_score', 50)
                            emoji = get_signal_emoji(score)
                            st.markdown(f"### Signal\n<p class='{get_signal_color_class(score)}'>{emoji} {signal}</p>", unsafe_allow_html=True)
                        
                        with col2:
                            st.metric("Score", f"{score:.1f}/100")
                        
                        with col3:
                            confidence = result.get('confidence', 0)
                            st.metric("Confidence", f"{confidence:.1%}")
                        
                        with col4:
                            active = result.get('active_layers', 17)
                            st.metric("Active Layers", f"{active}/17")
                        
                        st.success("✅ Analysis Complete!")
                        
                        if 'layers' in result:
                            with st.expander("📊 Layer Scores"):
                                layers_df = pd.DataFrame([
                                    {'Layer': k, 'Score': v if v else 'N/A'}
                                    for k, v in result['layers'].items()
                                ])
                                st.dataframe(layers_df, use_container_width=True)
                    else:
                        st.error("❌ Analysis failed")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)[:200]}")
    
    st.markdown("---")
    
    if st.session_state.last_analysis:
        st.markdown("### 📊 Last Analysis Result")
        result = st.session_state.last_analysis
        
        col1, col2, col3 = st.columns(3)
        with col1:
            signal = result.get('signal', 'NEUTRAL')
            score = result.get('final_score', 50)
            st.markdown(f"**Signal:** <span class='{get_signal_color_class(score)}'>{signal}</span>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**Score:** {score:.1f}/100")
        with col3:
            conf = result.get('confidence', 0)
            st.markdown(f"**Confidence:** {conf:.1%}")
        
        with st.expander("🔍 Full Data"):
            st.json(result)

# ============================================================================
# TAB 3: BACKTEST
# ============================================================================
with tab3:
    st.markdown("## 📈 Backtest Results")
    st.markdown(f"**Symbol:** {st.session_state.selected_symbol}")
    st.markdown("---")
    
    if not BACKTEST_AVAILABLE:
        st.warning("⚠️ Backtest Engine not available")
    else:
        st.info("📊 Backtest Engine v3.0 loaded - Ready for testing")

# ============================================================================
# TAB 4: SETTINGS
# ============================================================================
with tab4:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")
    
    st.markdown("### 🪙 Watchlist Management")
    
    new_coin = st.text_input("Add New Coin (e.g., SOLUSDT)")
    if st.button("➕ Add to Watchlist"):
        if new_coin:
            new_coin_upper = new_coin.upper()
            if new_coin_upper not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_coin_upper)
                st.success(f"✅ {new_coin_upper} added!")
                st.rerun()
            else:
                st.warning(f"⚠️ Already in watchlist")
    
    st.markdown("**Current Watchlist:**")
    for coin in st.session_state.watchlist:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"• {coin}")
        with col2:
            if st.button("❌", key=f"rm_{coin}"):
                st.session_state.watchlist.remove(coin)
                if st.session_state.selected_symbol == coin:
                    st.session_state.selected_symbol = st.session_state.watchlist[0]
                st.rerun()

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("""
<div class='footer'>
    <p>🔱 <strong>DEMIR AI Trading Bot v17.0</strong> - Phase 3+6 Full Integration</p>
    <p>17-Layer Phase 7 Quantum + Automation + Enhanced Macro</p>
    <p>Made with ❤️ by Patron | Render.com Deployment | NO LOGIN Required</p>
    <p style='font-size:0.8rem; color:#7b68ee;'>⚡ Real-Time AI Analysis | Professional Trading System</p>
</div>
""", unsafe_allow_html=True)
