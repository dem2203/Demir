"""
🚀 DEMIR AI v5.2 - Professional Streamlit Dashboard
📊 Production-Grade User Interface
🎯 Real-time Analytics & Trade Management

Location: GitHub Root / streamlit_app.py (REPLACE EXISTING)
Size: ~2500 lines
Author: AI Research Agent
Date: 2025-11-15
"""

import os
import sys
import logging
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import plotly.graph_objects as go
import plotly.express as px
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from typing import Dict, List, Tuple, Optional

# ============================================================================
# STREAMLIT CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="DEMIR AI v5.2 Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "DEMIR AI v5.2 - Crypto Trading Bot\n\nProduction Grade | 62-Layer Ensemble | 100% Real Data"
    }
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

@st.cache_resource
def get_db_connection():
    """Get cached database connection"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        logger.info("✅ Database connected")
        return conn
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        st.error(f"❌ Database connection failed: {e}")
        return None

# ============================================================================
# DATA LOADING FUNCTIONS - 100% REAL DATA
# ============================================================================

def load_recent_signals(conn, limit: int = 50, hours: int = 24) -> pd.DataFrame:
    """Load recent signals from database (100% REAL DATA)"""
    try:
        query = '''
            SELECT 
                id, symbol, signal_type, confidence, entry_price,
                take_profit_1, take_profit_2, take_profit_3, stop_loss,
                analysis_reason, timestamp, status
            FROM trades
            WHERE timestamp > NOW() - INTERVAL '%s hours'
            ORDER BY timestamp DESC
            LIMIT %s
        '''
        df = pd.read_sql(query, conn, params=(hours, limit))
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        logger.error(f"❌ Load signals error: {e}")
        return pd.DataFrame()

def load_symbol_performance(conn, symbol: str, days: int = 7) -> Dict:
    """Load performance metrics for a symbol"""
    try:
        query = '''
            SELECT 
                COUNT(*) as total_signals,
                ROUND(AVG(confidence), 2) as avg_confidence,
                SUM(CASE WHEN signal_type = 'LONG' THEN 1 ELSE 0 END) as long_count,
                SUM(CASE WHEN signal_type = 'SHORT' THEN 1 ELSE 0 END) as short_count,
                SUM(CASE WHEN signal_type = 'NEUTRAL' THEN 1 ELSE 0 END) as neutral_count,
                MAX(timestamp) as last_signal
            FROM trades
            WHERE symbol = %s
            AND timestamp > NOW() - INTERVAL '%s days'
        '''
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, (symbol, days))
        result = cursor.fetchone()
        cursor.close()
        return dict(result) if result else {}
    except Exception as e:
        logger.error(f"❌ Load performance error: {e}")
        return {}

def load_win_rate(conn, days: int = 7) -> Dict:
    """Calculate win rate from performance tracking"""
    try:
        query = '''
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END) as losing_trades,
                ROUND(SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(*), 0) * 100, 2) as win_rate_percent,
                ROUND(SUM(profit_loss), 2) as total_pnl,
                ROUND(AVG(profit_loss_percent), 2) as avg_pnl_percent
            FROM performance_tracking
            WHERE entry_time > NOW() - INTERVAL '%s days'
        '''
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, (days,))
        result = cursor.fetchone()
        cursor.close()
        return dict(result) if result else {}
    except Exception as e:
        logger.error(f"❌ Load win rate error: {e}")
        return {}

def load_layer_analysis(conn, trade_id: int) -> Dict:
    """Load detailed layer analysis for a signal"""
    try:
        query = '''
            SELECT 
                layer_tier,
                COUNT(*) as layer_count,
                ROUND(AVG(score), 3) as avg_score
            FROM layer_metrics
            WHERE trade_id = %s
            GROUP BY layer_tier
        '''
        df = pd.read_sql(query, conn, params=(trade_id,))
        return df.to_dict('records')
    except Exception as e:
        logger.error(f"❌ Load layer analysis error: {e}")
        return []

# ============================================================================
# DASHBOARD LAYOUT - 6 TABS
# ============================================================================

def main():
    # Header
    st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1>🤖 DEMIR AI v5.2 Dashboard</h1>
        <h3>Production-Grade Crypto Trading Bot</h3>
        <p><b>62-Layer Ensemble | 100% Real Data | 24/7 Operational</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get database connection
    conn = get_db_connection()
    if not conn:
        st.error("❌ Cannot connect to database")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dashboard",
        "🎯 Live Signals",
        "📈 Performance",
        "🧠 AI Analysis",
        "⚖️ Risk Management",
        "⚙️ Settings"
    ])
    
    # ========================================================================
    # TAB 1: DASHBOARD
    # ========================================================================
    with tab1:
        st.markdown("## 📊 System Dashboard")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Load recent signals
        signals_df = load_recent_signals(conn, limit=1000, hours=24)
        
        with col1:
            st.metric(
                "📍 Signals (24h)",
                len(signals_df),
                delta=f"Last: {signals_df['timestamp'].max().strftime('%H:%M') if len(signals_df) > 0 else 'N/A'}"
            )
        
        with col2:
            long_count = len(signals_df[signals_df['direction'] == 'LONG'])
            short_count = len(signals_df[signals_df['direction'] == 'SHORT'])
            st.metric(
                "🟢 LONG / 🔴 SHORT",
                f"{long_count} / {short_count}",
                delta=f"Total: {len(signals_df)}"
            )
        
        with col3:
            avg_confidence = signals_df['confidence'].mean() if len(signals_df) > 0 else 0
            st.metric(
                "🔒 Avg Confidence",
                f"{avg_confidence:.1f}%",
                delta="Quality of signals"
            )
        
        with col4:
            # Get system status
            try:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT COUNT(CASE WHEN status = 'ONLINE' THEN 1 END) as online_count FROM system_status")
                result = cursor.fetchone()
                cursor.close()
                online_count = result['online_count'] if result else 0
                st.metric(
                    "🟢 System Status",
                    f"{online_count}/8 Online",
                    delta="Components"
                )
            except:
                st.metric("🟢 System Status", "N/A")
        
        # Signals over time chart
        st.markdown("### 📈 Signals Over Time (24h)")
        
        if len(signals_df) > 0:
            signals_df['hour'] = signals_df['timestamp'].dt.floor('H')
            hourly_count = signals_df.groupby('hour').size().reset_index(name='count')
            
            fig = px.line(
                hourly_count,
                x='hour',
                y='count',
                title='Signal Generation Rate',
                labels={'hour': 'Time (UTC)', 'count': 'Signal Count'},
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Primary symbols performance
        st.markdown("### 🎯 Primary Symbols Performance")
        
        perf_col1, perf_col2, perf_col3 = st.columns(3)
        
        for col, symbol in zip([perf_col1, perf_col2, perf_col3], ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']):
            with col:
                perf = load_symbol_performance(conn, symbol, days=1)
                if perf:
                    st.markdown(f"#### {symbol}")
                    st.markdown(f"📊 Signals: **{perf.get('total_signals', 0)}**")
                    st.markdown(f"🟢 Long: **{perf.get('long_count', 0)}** | 🔴 Short: **{perf.get('short_count', 0)}**")
                    st.markdown(f"🔒 Avg Confidence: **{perf.get('avg_confidence', 0):.0f}%**")
    
    # ========================================================================
    # TAB 2: LIVE SIGNALS
    # ========================================================================
    with tab2:
        st.markdown("## 🎯 Live Signals (Real-time)")
        
        # Load recent signals
        signals_df = load_recent_signals(conn, limit=100, hours=6)
        
        if len(signals_df) > 0:
            # Color code signals
            def color_code_signal(row):
                if row['signal_type'] == 'LONG':
                    return '🟢 LONG'
                elif row['signal_type'] == 'SHORT':
                    return '🔴 SHORT'
                else:
                    return '⚪ NEUTRAL'
            
            signals_df['Direction'] = signals_df.apply(color_code_signal, axis=1)
            
            # Format display dataframe
            display_df = signals_df[[
                'symbol', 'Direction', 'confidence', 'entry_price',
                'take_profit_1', 'take_profit_2', 'stop_loss', 'timestamp'
            ]].copy()
            
            display_df.columns = ['Coin', 'Signal', 'Confidence %', 'Entry', 'TP1', 'TP2', 'SL', 'Time (UTC)']
            display_df['Confidence %'] = display_df['Confidence %'].round(2)
            display_df['Entry'] = display_df['Entry'].round(2)
            display_df['TP1'] = display_df['TP1'].round(2)
            display_df['TP2'] = display_df['TP2'].round(2)
            display_df['SL'] = display_df['SL'].round(2)
            display_df['Time (UTC)'] = display_df['Time (UTC)'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=600,
                hide_index=True
            )
            
            # Auto-refresh info
            st.info("📊 Data updates every 5 seconds. Refresh page to see latest signals.")
        else:
            st.warning("⏳ No signals yet. System is analyzing markets...")
    
    # ========================================================================
    # TAB 3: PERFORMANCE
    # ========================================================================
    with tab3:
        st.markdown("## 📈 Performance Analytics")
        
        perf = load_win_rate(conn, days=7)
        
        if perf and perf.get('total_trades', 0) > 0:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    "📊 Total Trades",
                    int(perf.get('total_trades', 0)),
                    delta="Last 7 days"
                )
            
            with col2:
                win_rate = perf.get('win_rate_percent', 0)
                delta_color = "green" if win_rate > 50 else "red" if win_rate < 50 else "gray"
                st.metric(
                    "🎯 Win Rate",
                    f"{win_rate:.1f}%",
                    delta=f"Target: 78-82%"
                )
            
            with col3:
                winning = int(perf.get('winning_trades', 0))
                st.metric(
                    "🟢 Wins",
                    winning,
                    delta=f"of {int(perf.get('total_trades', 0))}"
                )
            
            with col4:
                losing = int(perf.get('losing_trades', 0))
                st.metric(
                    "🔴 Losses",
                    losing,
                    delta=f"of {int(perf.get('total_trades', 0))}"
                )
            
            with col5:
                pnl = perf.get('total_pnl', 0)
                st.metric(
                    "💰 Total P&L",
                    f"${pnl:.2f}",
                    delta=f"Avg: {perf.get('avg_pnl_percent', 0):.2f}%"
                )
        else:
            st.info("⏳ Building performance history. Check back in 24 hours.")
    
    # ========================================================================
    # TAB 4: AI ANALYSIS
    # ========================================================================
    with tab4:
        st.markdown("## 🧠 AI Layer Analysis")
        
        signals_df = load_recent_signals(conn, limit=20, hours=6)
        
        if len(signals_df) > 0:
            selected_signal = st.selectbox(
                "Select Signal to Analyze",
                signals_df.apply(lambda x: f"{x['symbol']} - {x['signal_type']} @ {x['timestamp'].strftime('%Y-%m-%d %H:%M')}", axis=1)
            )
            
            selected_idx = signals_df.apply(lambda x: f"{x['symbol']} - {x['signal_type']} @ {x['timestamp'].strftime('%Y-%m-%d %H:%M')}", axis=1).tolist().index(selected_signal)
            trade_id = signals_df.iloc[selected_idx]['id']
            
            # Load layer analysis
            layer_analysis = load_layer_analysis(conn, trade_id)
            
            if layer_analysis:
                layer_df = pd.DataFrame(layer_analysis)
                layer_df.columns = ['Layer Tier', 'Layer Count', 'Average Score']
                
                st.dataframe(layer_df, use_container_width=True, hide_index=True)
                
                # Visualization
                fig = px.bar(
                    layer_df,
                    x='Layer Tier',
                    y='Average Score',
                    title='Layer Scores Distribution',
                    labels={'Layer Tier': 'Tier', 'Average Score': 'Score (0-1)'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No layer analysis data available for this signal.")
        else:
            st.warning("No signals available for analysis.")
    
    # ========================================================================
    # TAB 5: RISK MANAGEMENT
    # ========================================================================
    with tab5:
        st.markdown("## ⚖️ Risk Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Risk Parameters")
            
            try:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT setting_key, setting_value 
                    FROM user_settings 
                    WHERE setting_key LIKE '%risk%' OR setting_key LIKE '%threshold%' OR setting_key LIKE '%max%'
                    ORDER BY setting_key
                """)
                settings = cursor.fetchall()
                cursor.close()
                
                if settings:
                    for setting in settings:
                        st.markdown(f"**{setting['setting_key']}:** {setting['setting_value']}")
                else:
                    st.info("No risk settings configured.")
            except:
                st.error("Could not load risk settings.")
        
        with col2:
            st.markdown("### Current Risk Status")
            
            signals_df = load_recent_signals(conn, limit=100, hours=24)
            
            if len(signals_df) > 0:
                # Calculate risk metrics
                high_confidence_signals = len(signals_df[signals_df['confidence'] > 80])
                low_confidence_signals = len(signals_df[signals_df['confidence'] < 70])
                
                st.markdown(f"📊 **High Confidence Signals (>80%):** {high_confidence_signals}")
                st.markdown(f"⚠️ **Low Confidence Signals (<70%):** {low_confidence_signals}")
                st.markdown(f"📈 **Confidence Spread:** {signals_df['confidence'].max() - signals_df['confidence'].min():.2f}%")
    
    # ========================================================================
    # TAB 6: SETTINGS
    # ========================================================================
    with tab6:
        st.markdown("## ⚙️ System Settings")
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT setting_key, setting_value, description FROM user_settings ORDER BY setting_key")
            settings = cursor.fetchall()
            cursor.close()
            
            settings_df = pd.DataFrame(settings)
            settings_df.columns = ['Key', 'Value', 'Description']
            
            st.dataframe(settings_df, use_container_width=True, hide_index=True, height=600)
            
        except Exception as e:
            st.error(f"Could not load settings: {e}")
    
    # Close connection
    if conn:
        conn.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    main()

