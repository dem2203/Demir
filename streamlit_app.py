"""
🔱 DEMIR AI TRADING BOT - STREAMLIT v18.0 PROFESSIONAL
================================================================

Date: 7 Kasım 2025, 16:05 CET
Version: 18.0 - Phase 8+9 + PROFESSIONAL TRADING UI

✅ FEATURES:
- Real-time layer values display
- AI-generated Entry, TP, SL levels
- Live market data (Binance)
- Trade history & statistics
- Phase 9 daemon status
- Multi-timeframe analysis
- Professional TradingView-style UI
- Risk/Reward visualization
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import json

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="🔱 DEMIR AI Trading v18.0",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - PROFESSIONAL
# ============================================================================

st.markdown("""
<style>
    /* Dark theme */
    :root { --primary: #00ff00; --danger: #ff0000; --warning: #ffaa00; }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #0f2847 100%);
        border-left: 4px solid #00ff00;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .signal-long {
        background: linear-gradient(135deg, #003d00 0%, #001a00 100%);
        border-left: 4px solid #00ff00;
        color: #00ff00;
        font-weight: bold;
    }
    
    .signal-short {
        background: linear-gradient(135deg, #3d0000 0%, #1a0000 100%);
        border-left: 4px solid #ff0000;
        color: #ff0000;
        font-weight: bold;
    }
    
    .signal-neutral {
        background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
        border-left: 4px solid #ffaa00;
        color: #ffaa00;
        font-weight: bold;
    }
    
    /* Headers */
    h1, h2, h3 { color: #00ff00; text-shadow: 0 0 10px rgba(0,255,0,0.3); }
    
    /* Data quality */
    .dq-real { color: #00ff00; }
    .dq-fallback { color: #ffaa00; }
    .dq-error { color: #ff0000; }
    
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
# IMPORTS
# ============================================================================

AI_BRAIN_AVAILABLE = False
try:
    from ai_brain import analyze_with_ai_brain, make_trading_decision
    AI_BRAIN_AVAILABLE = True
except:
    pass

STATE_MGR_AVAILABLE = False
try:
    from phase_9.state_manager import StateManager
    STATE_MGR_AVAILABLE = True
except:
    pass

ALERT_AVAILABLE = False
try:
    from phase_9.alert_system import AlertSystem
    ALERT_AVAILABLE = True
except:
    pass

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div style='text-align: center; margin-bottom: 30px;'>
    <h1 style='color: #00ff00; font-size: 48px; text-shadow: 0 0 20px rgba(0,255,0,0.5);'>
        🔱 DEMIR AI TRADING BOT v18.0
    </h1>
    <p style='font-size: 16px; color: #aaa;'>
        Phase 8+9 Hybrid Autonomous | Professional Trading System
    </p>
    <hr style='border: 1px solid #00ff00; opacity: 0.3;'>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - CONTROLS
# ============================================================================

with st.sidebar:
    st.markdown("## ⚙️ Controls")
    
    # Symbol selection
    symbol = st.selectbox(
        "📊 Select Symbol",
        ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT'],
        index=0
    )
    
    # Interval
    interval = st.selectbox(
        "⏱️ Timeframe",
        ['5m', '15m', '1h', '4h', '1d']
    )
    
    st.markdown("---")
    
    # Current price input
    current_price = st.number_input(
        "💰 Current Price ($)",
        value=45000.0,
        min_value=0.0,
        step=1.0
    )
    
    st.markdown("---")
    
    # Run analysis
    if st.button("🚀 RUN AI ANALYSIS", use_container_width=True):
        with st.spinner("🧠 AI Brain analyzing..."):
            try:
                result = analyze_with_ai_brain(symbol, interval, current_price)
                st.session_state.last_analysis = result
                st.session_state.symbol = symbol
                st.session_state.interval = interval
                st.success("✅ Analysis complete!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)[:100]}")
    
    st.markdown("---")
    
    # System status
    st.markdown("## 📡 System Status")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "AI Brain",
            "✅ v16.6" if AI_BRAIN_AVAILABLE else "❌ Offline",
            "Ready"
        )
    with col2:
        st.metric(
            "Phase 9",
            "✅ Hybrid" if STATE_MGR_AVAILABLE else "❌ Offline",
            "Autonomous"
        )

# ============================================================================
# MAIN TABS
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 LIVE ANALYSIS",
    "📈 LAYERS & SCORES",
    "💡 TRADE SIGNALS",
    "📉 HISTORY & STATS"
])

# ============================================================================
# TAB 1: LIVE ANALYSIS
# ============================================================================

with tab1:
    if st.session_state.last_analysis:
        result = st.session_state.last_analysis
        
        # Header metrics
        st.markdown("## 🎯 AI Analysis Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            score = result['final_score']
            signal = result['signal']
            
            if signal == 'LONG':
                color = "🟢"
                style = "signal-long"
            elif signal == 'SHORT':
                color = "🔴"
                style = "signal-short"
            else:
                color = "⚪"
                style = "signal-neutral"
            
            st.markdown(f"""
            <div class='{style}'>
            <div style='font-size: 24px; margin-bottom: 10px;'>{color} {signal}</div>
            <div style='font-size: 14px;'>Score: {score}/100</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            confidence = result['confidence']
            st.metric(
                "Confidence",
                f"{confidence:.1%}",
                delta="High" if confidence > 0.7 else "Med" if confidence > 0.5 else "Low"
            )
        
        with col3:
            regime = result['regime']
            st.metric("Market Regime", regime, "Status")
        
        with col4:
            timestamp = result['timestamp']
            time_ago = datetime.now() - datetime.fromisoformat(timestamp)
            st.metric(
                "Last Updated",
                f"{time_ago.seconds}s ago",
                "Just now" if time_ago.seconds < 60 else "Ago"
            )
        
        st.markdown("---")
        
        # Trade Levels
        st.markdown("## 💰 TRADE LEVELS (AI Generated)")
        
        trade_levels = result.get('trade_levels')
        if trade_levels:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    "ENTRY",
                    f"${trade_levels['entry']:,.2f}",
                    "Buy/Sell"
                )
            
            with col2:
                st.metric(
                    "TAKE PROFIT",
                    f"${trade_levels['tp']:,.2f}",
                    f"+{((trade_levels['tp'] - trade_levels['entry'])/trade_levels['entry']*100):.2f}%"
                )
            
            with col3:
                st.metric(
                    "STOP LOSS",
                    f"${trade_levels['sl']:,.2f}",
                    f"{((trade_levels['sl'] - trade_levels['entry'])/trade_levels['entry']*100):.2f}%"
                )
            
            with col4:
                st.metric(
                    "RISK/REWARD",
                    f"1:{trade_levels['risk_reward']}",
                    "Ratio"
                )
            
            with col5:
                st.metric(
                    "RISK AMOUNT",
                    f"${trade_levels['risk_amount']:,.2f}",
                    "Per unit"
                )
            
            # Visual: Risk/Reward chart
            st.markdown("### 📊 Risk/Reward Visualization")
            
            fig = go.Figure()
            
            if result['signal'] == 'LONG':
                # LONG visual
                fig.add_trace(go.Scatter(
                    x=['Entry', 'TP', 'SL'],
                    y=[trade_levels['entry'], trade_levels['tp'], trade_levels['sl']],
                    mode='markers+lines',
                    marker=dict(size=15, color=['yellow', 'green', 'red']),
                    line=dict(dash='dash', color='gray'),
                    name='Price Levels'
                ))
            else:
                # SHORT visual
                fig.add_trace(go.Scatter(
                    x=['Entry', 'TP', 'SL'],
                    y=[trade_levels['entry'], trade_levels['tp'], trade_levels['sl']],
                    mode='markers+lines',
                    marker=dict(size=15, color=['yellow', 'red', 'green']),
                    line=dict(dash='dash', color='gray'),
                    name='Price Levels'
                ))
            
            fig.update_layout(
                height=300,
                template='plotly_dark',
                hovermode='x unified',
                title="Entry → TP / SL Levels"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Market Info
        st.markdown("## 📈 Market Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Current Price")
            st.markdown(f"""
            <div style='text-align: center; font-size: 32px; color: #00ff00; font-weight: bold;'>
                ${result['current_price']:,.2f}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🎯 Target Zones")
            if trade_levels:
                dist_to_tp = ((trade_levels['tp'] - result['current_price']) / result['current_price'] * 100)
                dist_to_sl = ((trade_levels['sl'] - result['current_price']) / result['current_price'] * 100)
                
                st.markdown(f"""
                **Distance to TP:** {dist_to_tp:+.2f}% \n
                **Distance to SL:** {dist_to_sl:+.2f}% \n
                **P/L Ratio:** {abs(dist_to_tp/dist_to_sl) if dist_to_sl != 0 else 0:.2f}:1
                """)
    
    else:
        st.info("👈 Select parameters and click 'RUN AI ANALYSIS' to start")

# ============================================================================
# TAB 2: LAYERS & SCORES
# ============================================================================

with tab2:
    st.markdown("## 🧠 Layer Analysis (15-Layer Ensemble)")
    
    if st.session_state.last_analysis:
        result = st.session_state.last_analysis
        
        # Layer scores table
        st.markdown("### 📊 Individual Layer Scores")
        
        layers_df = pd.DataFrame([
            {
                'Layer': k.replace('_', ' ').title(),
                'Score': f"{v:.1f}/100" if v else "N/A",
                'Source': result['sources'].get(k, 'Unknown')
            }
            for k, v in result['layers'].items()
        ])
        
        st.dataframe(layers_df, use_container_width=True, hide_index=True)
        
        # Layer visualization
        st.markdown("### 📈 Score Distribution")
        
        fig = go.Figure()
        
        layer_names = list(result['layers'].keys())
        layer_scores = list(result['layers'].values())
        
        fig.add_trace(go.Bar(
            x=layer_names,
            y=layer_scores,
            marker=dict(
                color=layer_scores,
                colorscale='RdYlGn',
                cmid=50,
                cmin=0,
                cmax=100,
                colorbar=dict(title="Score")
            ),
            text=[f"{s:.0f}" for s in layer_scores],
            textposition='outside'
        ))
        
        fig.update_layout(
            title="15-Layer Score Distribution",
            xaxis_title="Layer",
            yaxis_title="Score (0-100)",
            height=400,
            template='plotly_dark',
            hovermode='x'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data quality
        st.markdown("### 🔍 Data Quality")
        
        dq = result['data_quality']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style='text-align: center;'>
            <div style='font-size: 32px; color: #00ff00;'>{dq['real']}</div>
            <div style='color: #999;'>Real Data</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='text-align: center;'>
            <div style='font-size: 32px; color: #ffaa00;'>{dq['fallback']}</div>
            <div style='color: #999;'>Fallback</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style='text-align: center;'>
            <div style='font-size: 32px; color: #ff0000;'>{dq['error']}</div>
            <div style='color: #999;'>Error</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            quality_pct = (dq['real'] + dq['fallback']) / 15 * 100
            st.markdown(f"""
            <div style='text-align: center;'>
            <div style='font-size: 32px; color: #00ff00;'>{quality_pct:.0f}%</div>
            <div style='color: #999;'>Quality</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Adaptive weights
        st.markdown("### ⚖️ Adaptive Weights Used")
        
        weights_df = pd.DataFrame([
            {
                'Layer': k.replace('_', ' ').title(),
                'Weight': f"{v:.4f}"
            }
            for k, v in result['weights_used'].items()
        ])
        
        st.dataframe(weights_df, use_container_width=True, hide_index=True)
    
    else:
        st.info("No analysis data yet")

# ============================================================================
# TAB 3: TRADE SIGNALS
# ============================================================================

with tab3:
    st.markdown("## 🚀 Trading Signals & Recommendations")
    
    if st.session_state.last_analysis:
        result = st.session_state.last_analysis
        
        # Signal explanation
        signal = result['signal']
        score = result['final_score']
        confidence = result['confidence']
        
        st.markdown("### 📋 AI Recommendation")
        
        if signal == 'LONG':
            st.success(f"""
            ### 🟢 BUY SIGNAL - LONG POSITION
            
            **Score:** {score}/100 (High confidence: {confidence:.1%})
            
            **Recommendation:**
            - Enter LONG position at provided ENTRY price
            - Set TP and SL at calculated levels
            - Manage risk per position sizing rules
            - Monitor for signal changes every candle close
            
            **Trigger:** Multiple layers show bullish confluence
            """)
        
        elif signal == 'SHORT':
            st.error(f"""
            ### 🔴 SELL SIGNAL - SHORT POSITION
            
            **Score:** {score}/100 (High confidence: {confidence:.1%})
            
            **Recommendation:**
            - Enter SHORT position at provided ENTRY price
            - Set TP and SL at calculated levels
            - Manage risk per position sizing rules
            - Monitor for signal changes every candle close
            
            **Trigger:** Multiple layers show bearish confluence
            """)
        
        else:
            st.warning(f"""
            ### ⚪ NEUTRAL SIGNAL - NO CLEAR DIRECTION
            
            **Score:** {score}/100 (Confidence: {confidence:.1%})
            
            **Recommendation:**
            - Wait for clearer signal (score > 65 or < 35)
            - Monitor market regime changes
            - Prepare orders at key support/resistance
            - Avoid choppy market conditions
            """)
        
        # Entry checklist
        st.markdown("### ✅ Pre-Trade Checklist")
        
        st.checkbox("✅ Confirm AI signal on chart", value=True)
        st.checkbox("✅ Check market news/events", value=False)
        st.checkbox("✅ Verify volume & volatility", value=False)
        st.checkbox("✅ Set stops & limits", value=False)
        st.checkbox("✅ Check account balance", value=False)
        st.checkbox("✅ Risk < 2% per trade", value=False)
        
        # Alerts
        st.markdown("---")
        st.markdown("### 🔔 Phase 9 Hybrid Alerts")
        
        if ALERT_AVAILABLE:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📧 Send Email Alert"):
                    try:
                        alerts = AlertSystem()
                        msg = f"Signal: {signal}\nScore: {score}/100\nEntry: ${result['trade_levels']['entry']}"
                        alerts.send_email(msg)
                        st.success("✅ Email sent!")
                    except:
                        st.error("❌ Email send failed")
            
            with col2:
                if st.button("📱 Send SMS Alert"):
                    try:
                        alerts = AlertSystem()
                        msg = f"{signal} @ {score}/100"
                        alerts.send_sms(msg)
                        st.success("✅ SMS sent!")
                    except:
                        st.error("❌ SMS send failed")
        
        else:
            st.info("Phase 9 alert system not configured")
    
    else:
        st.info("No signals yet - run analysis first")

# ============================================================================
# TAB 4: HISTORY & STATS
# ============================================================================

with tab4:
    st.markdown("## 📊 Trading History & Statistics")
    
    if STATE_MGR_AVAILABLE:
        try:
            state_mgr = StateManager()
            
            # Get stats
            stats = state_mgr.get_statistics()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Trades", stats.get('total_trades', 0), "All-time")
            
            with col2:
                st.metric("Win Rate", f"{stats.get('win_rate', 0):.1f}%", "Closed trades")
            
            with col3:
                st.metric("Avg P&L", f"{stats.get('avg_pnl', 0):.2f}%", "Per trade")
            
            with col4:
                st.metric("Max P&L", f"{stats.get('max_pnl', 0):.2f}%", "Best trade")
            
            # Trade history
            st.markdown("### 📈 Recent Trades")
            
            trades = state_mgr.get_trade_history(days=7)
            
            if trades:
                trades_df = pd.DataFrame(trades)
                st.dataframe(trades_df, use_container_width=True)
            else:
                st.info("No trades yet")
            
            # Trend analysis
            st.markdown("### 📊 24h Trend")
            
            trend = state_mgr.get_trend(hours=24)
            
            if trend.get('trend') != 'INSUFFICIENT_DATA':
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Trend Direction",
                        trend.get('trend', 'N/A'),
                        f"{trend.get('percent_change', 0):+.2f}%"
                    )
                
                with col2:
                    st.metric("First Score", f"{trend.get('first_score', 0):.1f}", "24h ago")
                
                with col3:
                    st.metric("Last Score", f"{trend.get('last_score', 0):.1f}", "Now")
            
        except Exception as e:
            st.error(f"Failed to load stats: {str(e)[:100]}")
    
    else:
        st.info("Phase 9 state manager not available")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px; padding: 20px;'>
    <p>🔱 DEMIR AI Trading Bot v18.0 | Phase 8+9 Hybrid Autonomous System</p>
    <p>Last Updated: 7 Nov 2025 | © Professional Trading AI</p>
</div>
""", unsafe_allow_html=True)
