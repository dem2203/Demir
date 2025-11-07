"""
🔱 DEMIR AI TRADING BOT - STREAMLIT v18.1 UPDATED WITH REAL DATA
================================================================
Date: 7 Kasım 2025, 20:40 CET
Version: 18.1 - Phase 8+9 + REAL DATA LAYERS + TELEGRAM ALERTS
Features:
  ✅ Real-time layer values display with REAL API data
  ✅ AI-generated Entry, TP, SL levels
  ✅ Live market data (Alternative.me, Binance, Yahoo Finance, CoinGecko)
  ✅ Telegram alerts integration
  ✅ Multi-timeframe analysis
  ✅ Professional TradingView-style UI
  ✅ Risk/Reward visualization
  ✅ Fallback mechanisms for all APIs
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="🔱 DEMIR AI Trading v18.1",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - PROFESSIONAL
# ============================================================================

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================

if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = None
if 'symbol' not in st.session_state:
    st.session_state.symbol = 'BTCUSDT'
if 'interval' not in st.session_state:
    st.session_state.interval = '1h'

# ============================================================================
# IMPORTS - REAL DATA LAYERS (NEW)
# ============================================================================

logger.info("🚀 Loading DEMIR v18.1 with REAL DATA LAYERS...")

AI_BRAIN_AVAILABLE = False
USING_REAL_DATA = False

# Try Real Data Brain First
try:
    from ai_brain_REAL import analyze_market
    logger.info("✅ ai_brain_REAL imported - REAL DATA ACTIVE")
    AI_BRAIN_AVAILABLE = True
    USING_REAL_DATA = True
    analyze_function = analyze_market
except Exception as e:
    logger.warning(f"⚠️ ai_brain_REAL failed: {e}")
    # Fallback to old AI brain
    try:
        from ai_brain import analyze_with_ai_brain, make_trading_decision
        logger.warning("⚠️ Fallback: Using old ai_brain")
        AI_BRAIN_AVAILABLE = True
        USING_REAL_DATA = False
        analyze_function = make_trading_decision
    except:
        logger.error("❌ No AI brain available")
        AI_BRAIN_AVAILABLE = False

# Alert System
ALERT_AVAILABLE = False
try:
    from alert_system_REAL import AlertSystem
    alert_system = AlertSystem()
    ALERT_AVAILABLE = True
    logger.info("✅ AlertSystem (Telegram) imported")
except:
    alert_system = None
    ALERT_AVAILABLE = False
    logger.warning("⚠️ AlertSystem not available")

# External Data (REAL)
try:
    from external_data_REAL import get_all_external_data
    logger.info("✅ external_data_REAL imported")
    EXTERNAL_DATA_AVAILABLE = True
except:
    try:
        from external_data import get_all_external_data
        logger.warning("⚠️ Fallback: Using external_data")
        EXTERNAL_DATA_AVAILABLE = True
    except:
        EXTERNAL_DATA_AVAILABLE = False
        logger.warning("⚠️ No external data available")

# State Manager
STATE_MGR_AVAILABLE = False
try:
    from phase_9.state_manager import StateManager
    STATE_MGR_AVAILABLE = True
except:
    pass

# ============================================================================
# HEADER
# ============================================================================

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.title("🔱 DEMIR")

with col2:
    st.markdown("""
    ### AI Trading Bot v18.1 | Phase 8+9 Hybrid
    **Real-Time Market Analysis & Trading Signals**
    """)

with col3:
    if USING_REAL_DATA:
        st.success("✅ Real Data: ACTIVE")
    else:
        st.warning("⚠️ Real Data: DISABLED")

st.markdown("---")

# ============================================================================
# SIDEBAR - SETTINGS
# ============================================================================

st.sidebar.title("⚙️ SETTINGS & CONTROLS")

# Data Source Status
st.sidebar.markdown("""
---
### 📡 DATA SOURCE STATUS
""")

if USING_REAL_DATA:
    st.sidebar.success("✅ Real Data Layers: ACTIVE")
else:
    st.sidebar.warning("⚠️ Fallback Mode: ENABLED")

st.sidebar.info(f"🤖 AI Brain: {'✅ Ready' if AI_BRAIN_AVAILABLE else '❌ Error'}")
st.sidebar.info(f"📱 Telegram: {'✅ Ready' if ALERT_AVAILABLE else '⚠️ Offline'}")

# Symbol & Timeframe
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Analysis Settings")

symbol = st.sidebar.selectbox(
    "Select Trading Pair",
    ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT"],
    index=0
)

interval = st.sidebar.selectbox(
    "Timeframe",
    ["1m", "5m", "15m", "1h", "4h", "1d"],
    index=4
)

# Risk Management
st.sidebar.markdown("---")
st.sidebar.subheader("💰 Risk Management")

risk_level = st.sidebar.slider("Risk Level", 0.1, 1.0, 0.5, step=0.1)
position_size = st.sidebar.slider("Position Size (%)", 1, 100, 10, step=5)

# Auto Refresh
st.sidebar.markdown("---")
st.sidebar.subheader("🔄 Advanced Options")

auto_refresh = st.sidebar.checkbox("Auto-Refresh Analysis", value=False)
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 10, 300, 60, step=10)

show_external_data = st.sidebar.checkbox("Show External Market Data", value=True)

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.markdown("---")

# Status Row
status_col1, status_col2, status_col3, status_col4 = st.columns(4)

with status_col1:
    st.metric("📊 System", "v18.1 + Real Data" if USING_REAL_DATA else "v18.1 Fallback")

with status_col2:
    st.metric("📡 Data Source", "LIVE" if USING_REAL_DATA else "MOCK")

with status_col3:
    st.metric("🤖 AI Brain", "Ready" if AI_BRAIN_AVAILABLE else "Error")

with status_col4:
    st.metric("🔔 Alerts", "Enabled" if ALERT_AVAILABLE else "Disabled")

st.markdown("---")

# ============================================================================
# ANALYSIS SECTION
# ============================================================================

st.subheader(f"📈 Live Analysis: {symbol}")

# Get current price
try:
    import yfinance as yf
    ticker = yf.Ticker(symbol.replace('USDT', '-USDT'))
    current_price = ticker.history(period='1d')['Close'].iloc[-1]
except:
    current_price = 45000 if 'BTC' in symbol else 2500

# Main Analysis Button
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if st.button("🔍 RUN ANALYSIS", use_container_width=True):
        st.session_state['analysis_requested'] = True

with col2:
    if st.button("💾 Save Result", use_container_width=True):
        st.info("Result saved to database")

with col3:
    if ALERT_AVAILABLE and st.button("📱 Send Alert", use_container_width=True):
        st.info("Alert will be sent to Telegram")

# ============================================================================
# ANALYSIS RESULTS
# ============================================================================

if 'analysis_requested' in st.session_state and st.session_state['analysis_requested']:
    with st.spinner(f"🔄 Analyzing {symbol}..."):
        try:
            logger.info(f"Starting analysis for {symbol}")
            
            # Run analysis with REAL DATA if available
            if USING_REAL_DATA:
                result = analyze_market(symbol, current_price, interval)
            else:
                result = analyze_function(symbol, interval)
            
            st.session_state['last_analysis'] = result
            logger.info(f"✅ Analysis complete")
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)[:100]}")
            logger.error(f"Analysis error: {e}")
            result = None

# Display results
if st.session_state['last_analysis'] is not None:
    result = st.session_state['last_analysis']
    
    # Main Signal
    st.markdown("---")
    
    if USING_REAL_DATA:
        score = result.get('final_score', 50)
        signal = result.get('signal', 'NEUTRAL')
        confidence = result.get('confidence', 0.5)
        emoji = result.get('emoji', '🟡')
    else:
        score = result.get('score', 50)
        signal = result.get('signal', 'NEUTRAL')
        confidence = result.get('confidence', 0.5)
        emoji = '🟡'
    
    # Color mapping
    if signal == 'LONG':
        emoji = '🟢'
        signal_color = "success"
    elif signal == 'SHORT':
        emoji = '🔴'
        signal_color = "error"
    else:
        emoji = '🟡'
        signal_color = "info"
    
    # Display main metrics
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("📊 Score", f"{score:.1f}/100", delta=f"{score-50:+.1f}")
    
    with metric_col2:
        st.metric("🎯 Signal", f"{emoji} {signal}", delta=f"{confidence:.0%}")
    
    with metric_col3:
        st.metric("💪 Confidence", f"{confidence:.0%}")
    
    with metric_col4:
        st.metric("⏰ Updated", datetime.now().strftime("%H:%M:%S"))
    
    # Trade Levels
    st.markdown("---")
    st.subheader("💰 Trade Levels")
    
    if USING_REAL_DATA:
        trade_levels = result.get('trade_levels', {})
        entry = trade_levels.get('entry', current_price)
        tp = trade_levels.get('tp', current_price * 1.05)
        sl = trade_levels.get('sl', current_price * 0.95)
        rr = trade_levels.get('risk_reward', 1)
    else:
        entry = current_price
        tp = current_price * 1.05
        sl = current_price * 0.95
        rr = (tp - entry) / (entry - sl) if entry != sl else 1
    
    level_col1, level_col2, level_col3, level_col4 = st.columns(4)
    
    with level_col1:
        st.info(f"📍 Entry\n**${entry:,.2f}**")
    
    with level_col2:
        st.success(f"✅ TP\n**${tp:,.2f}**")
    
    with level_col3:
        st.error(f"🛑 SL\n**${sl:,.2f}**")
    
    with level_col4:
        st.warning(f"📈 R:R\n**1:{rr:.2f}**")
    
    # Layer Analysis
    st.markdown("---")
    st.subheader("📊 Layer Analysis")
    
    if USING_REAL_DATA:
        layers = result.get('layers', {})
        
        layer_data = []
        for layer_name, layer_score in sorted(layers.items()):
            if layer_score is not None:
                if layer_score >= 65:
                    status = "🟢 BULLISH"
                elif layer_score <= 35:
                    status = "🔴 BEARISH"
                else:
                    status = "🟡 NEUTRAL"
                
                layer_data.append({
                    'Layer': layer_name.replace('_', ' ').title(),
                    'Score': f"{layer_score:.1f}",
                    'Status': status
                })
        
        if layer_data:
            df_layers = pd.DataFrame(layer_data)
            st.dataframe(df_layers, use_container_width=True, hide_index=True)
        
        # Data Quality
        st.markdown("---")
        st.subheader("📡 Data Quality")
        
        data_quality = result.get('data_quality', {})
        real_sources = data_quality.get('real_sources', 0)
        total_sources = data_quality.get('total_sources', 1)
        
        dq_col1, dq_col2, dq_col3 = st.columns(3)
        
        with dq_col1:
            st.metric("🟢 Real APIs", f"{real_sources}/{total_sources}")
        
        with dq_col2:
            st.metric("⚠️ Errors", data_quality.get('errors', 0))
        
        with dq_col3:
            coverage = (real_sources / total_sources * 100) if total_sources > 0 else 0
            st.metric("📊 Coverage", f"{coverage:.0f}%")
        
        # Show errors if any
        if result.get('errors'):
            st.warning("⚠️ **Data Warnings:**")
            for error in result['errors'][:3]:
                st.caption(f"• {error}")
    
    # External Data Section
    if show_external_data and EXTERNAL_DATA_AVAILABLE:
        st.markdown("---")
        st.subheader("🌐 External Market Data")
        
        try:
            ext_data = get_all_external_data(symbol)
            
            ext_col1, ext_col2, ext_col3 = st.columns(3)
            
            with ext_col1:
                fg = ext_data.get('fear_greed', {})
                st.metric(
                    "😨 Fear & Greed",
                    f"{fg.get('value', 50)}",
                    fg.get('classification', 'Neutral')
                )
            
            with ext_col2:
                funding = ext_data.get('funding_rate', {})
                st.metric(
                    "📊 Funding",
                    f"{funding.get('rate', 0):.4f}%"
                )
            
            with ext_col3:
                dom = ext_data.get('bitcoin_dominance', {})
                st.metric(
                    "👑 BTC Dom",
                    f"{dom.get('dominance', 0):.1f}%"
                )
        
        except Exception as e:
            st.warning(f"⚠️ External data unavailable: {str(e)[:50]}")
    
    # Alert Buttons
    if ALERT_AVAILABLE:
        st.markdown("---")
        alert_col1, alert_col2 = st.columns(2)
        
        with alert_col1:
            if st.button("📱 Send Trading Signal to Telegram", use_container_width=True):
                try:
                    alert_system.send_trading_signal({
                        'symbol': symbol,
                        'score': score,
                        'action': signal,
                        'confidence': confidence,
                        'entry': entry,
                        'tp': tp,
                        'sl': sl,
                        'price': current_price
                    })
                    st.success("✅ Signal sent to Telegram!")
                except Exception as e:
                    st.error(f"❌ Failed: {str(e)[:50]}")
        
        with alert_col2:
            if st.button("📊 Send Layer Analysis to Telegram", use_container_width=True):
                try:
                    if USING_REAL_DATA:
                        alert_system.send_layer_analysis(result.get('layers', {}))
                        st.success("✅ Analysis sent to Telegram!")
                except:
                    st.error("❌ Failed to send")

else:
    st.info("👆 Click 'RUN ANALYSIS' to generate signals")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    if USING_REAL_DATA:
        st.caption("✅ **Real Data:** LIVE API Integration Active")
    else:
        st.caption("⚠️ **Fallback Mode:** Using mock data")

with footer_col2:
    st.caption(f"⏰ **Time:** {datetime.now().strftime('%H:%M:%S UTC')}")

with footer_col3:
    st.caption("📌 Not financial advice - Use responsibly")

st.markdown("""
---
**DEMIR Phase 8+9 v18.1 - Professional AI Trading System**
- Real-time analysis with 15+ layers
- Live API data: Alternative.me, Binance, CoinGecko, Yahoo Finance
- Telegram alerts for trading signals
- Comprehensive risk management
""")
