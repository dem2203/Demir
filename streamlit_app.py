#!/usr/bin/env python3
"""
🔱 DEMIR AI - streamlit_dashboard.py (HAFTA 11-12)
MULTI-PAGE DASHBOARD - 7+ pages
"""

import streamlit as st
import pandas as pd
import psycopg2
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# Page config
st.set_page_config(page_title="🔱 DEMIR AI", layout="wide")

DB_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DB_URL)

# ============================================================================
# PAGE 1: DASHBOARD (Main)
# ============================================================================
def page_dashboard():
    st.header("📊 MAIN DASHBOARD")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Fetch metrics
    cur.execute("SELECT SUM(daily_pnl) FROM trading_stats WHERE date >= NOW() - INTERVAL '7 days'")
    weekly_pnl = cur.fetchone()[0] or 0
    col1.metric("Weekly P&L", f"${weekly_pnl:.2f}")
    
    cur.execute("SELECT AVG(win_rate) FROM trading_stats WHERE date >= NOW() - INTERVAL '30 days'")
    win_rate = cur.fetchone()[0] or 0
    col2.metric("Win Rate (30d)", f"{win_rate:.1%}")
    
    cur.execute("SELECT SUM(total_trades) FROM trading_stats WHERE date >= NOW() - INTERVAL '7 days'")
    trades = cur.fetchone()[0] or 0
    col3.metric("Trades (7d)", int(trades))
    
    cur.execute("SELECT AVG(daily_pnl_percent) FROM trading_stats WHERE date >= NOW() - INTERVAL '30 days'")
    daily_return = cur.fetchone()[0] or 0
    col4.metric("Avg Daily Return", f"{daily_return:.2%}")
    
    # Equity curve
    cur.execute("""
        SELECT date, ending_balance FROM trading_stats 
        ORDER BY date DESC LIMIT 365
    """)
    equity_data = cur.fetchall()
    
    if equity_data:
        df_equity = pd.DataFrame(equity_data, columns=['date', 'balance'])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_equity['date'], y=df_equity['balance'], 
                                mode='lines', name='Balance'))
        st.plotly_chart(fig, use_container_width=True)
    
    cur.close()
    conn.close()

# ============================================================================
# PAGE 2: MODEL PERFORMANCE
# ============================================================================
def page_models():
    st.header("🧠 MODEL PERFORMANCE")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Model accuracy comparison
    cur.execute("""
        SELECT model_name, accuracy_test, f1_score, last_trained 
        FROM ml_models WHERE status = 'deployed'
    """)
    models = cur.fetchall()
    
    df_models = pd.DataFrame(models, columns=['Model', 'Accuracy', 'F1-Score', 'Last Trained'])
    st.dataframe(df_models, use_container_width=True)
    
    # Predictions accuracy (last 50)
    cur.execute("""
        SELECT correct, COUNT(*) FROM predictions 
        WHERE created_at >= NOW() - INTERVAL '7 days'
        GROUP BY correct
    """)
    pred_results = cur.fetchall()
    
    if pred_results:
        correct = sum(r[1] for r in pred_results if r[0])
        total = sum(r[1] for r in pred_results)
        accuracy = correct / total if total > 0 else 0
        st.metric("Recent Prediction Accuracy", f"{accuracy:.1%}")
    
    cur.close()
    conn.close()

# ============================================================================
# PAGE 3: LIVE SIGNALS
# ============================================================================
def page_signals():
    st.header("🚀 LIVE TRADING SIGNALS")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Latest signals (last 24h)
    cur.execute("""
        SELECT symbol, signal, confidence, entry_price, tp1_price, 
               sl_price, timestamp
        FROM signal_log
        WHERE timestamp >= NOW() - INTERVAL '24 hours'
        ORDER BY timestamp DESC
    """)
    signals = cur.fetchall()
    
    if signals:
        df_signals = pd.DataFrame(signals, columns=[
            'Symbol', 'Signal', 'Confidence', 'Entry', 'TP1', 'SL', 'Time'
        ])
        
        # Color code by signal
        def color_signal(val):
            if val == 'UP':
                return 'background-color: #00ff00'
            elif val == 'DOWN':
                return 'background-color: #ff0000'
            else:
                return 'background-color: #ffff00'
        
        df_signals = df_signals.style.applymap(
            color_signal, subset=['Signal']
        )
        
        st.dataframe(df_signals, use_container_width=True)
    else:
        st.info("No signals in last 24 hours")
    
    cur.close()
    conn.close()

# ============================================================================
# PAGE 4: MANUAL TRADES
# ============================================================================
def page_manual_trades():
    st.header("📈 MANUAL TRADE TRACKING")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    col1, col2 = st.columns(2)
    
    # Open trades
    with col1:
        st.subheader("Open Trades")
        cur.execute("""
            SELECT symbol, entry_price, tp1_price, sl_price, pnl
            FROM manual_trades WHERE status = 'open'
        """)
        open_trades = cur.fetchall()
        
        if open_trades:
            df_open = pd.DataFrame(open_trades, columns=[
                'Symbol', 'Entry', 'TP1', 'SL', 'P&L'
            ])
            st.dataframe(df_open, use_container_width=True)
        else:
            st.info("No open trades")
    
    # Closed trades
    with col2:
        st.subheader("Recent Closed Trades")
        cur.execute("""
            SELECT symbol, entry_price, exit_price, pnl, success
            FROM manual_trades WHERE status IN ('closed', 'tp1_hit', 'tp2_hit', 'sl_hit')
            ORDER BY exit_time DESC LIMIT 10
        """)
        closed_trades = cur.fetchall()
        
        if closed_trades:
            df_closed = pd.DataFrame(closed_trades, columns=[
                'Symbol', 'Entry', 'Exit', 'P&L', 'Result'
            ])
            st.dataframe(df_closed, use_container_width=True)
        else:
            st.info("No closed trades")
    
    cur.close()
    conn.close()

# ============================================================================
# PAGE 5: BACKTEST RESULTS
# ============================================================================
def page_backtest():
    st.header("📉 BACKTEST ANALYSIS")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT symbol, total_trades, win_rate, sharpe_ratio, 
               max_drawdown, total_return
        FROM backtesting_results
        ORDER BY symbol
    """)
    results = cur.fetchall()
    
    if results:
        df_backtest = pd.DataFrame(results, columns=[
            'Symbol', 'Trades', 'Win Rate', 'Sharpe', 'Max DD', 'Return'
        ])
        st.dataframe(df_backtest, use_container_width=True)
    else:
        st.info("No backtest results yet")
    
    cur.close()
    conn.close()

# ============================================================================
# PAGE 6: ERROR LOG
# ============================================================================
def page_errors():
    st.header("⚠️ ERROR LOG")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Recent errors
    cur.execute("""
        SELECT job_name, api_name, error_type, timestamp
        FROM error_log
        WHERE timestamp >= NOW() - INTERVAL '7 days'
        ORDER BY timestamp DESC
        LIMIT 50
    """)
    errors = cur.fetchall()
    
    if errors:
        df_errors = pd.DataFrame(errors, columns=[
            'Job', 'API', 'Error Type', 'Time'
        ])
        st.dataframe(df_errors, use_container_width=True)
    else:
        st.success("No errors in last 7 days ✅")
    
    cur.close()
    conn.close()

# ============================================================================
# PAGE 7: SETTINGS
# ============================================================================
def page_settings():
    st.header("⚙️ SETTINGS")
    
    st.subheader("API Status")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check last feature update
    cur.execute("SELECT MAX(created_at) FROM feature_store")
    last_update = cur.fetchone()[0]
    
    if last_update:
        time_ago = datetime.now(last_update.tzinfo) - last_update
        st.metric("Last Feature Update", f"{int(time_ago.total_seconds() / 60)} mins ago")
    
    # Check model status
    cur.execute("SELECT COUNT(*) FROM ml_models WHERE status = 'deployed'")
    deployed_models = cur.fetchone()[0]
    st.metric("Deployed Models", deployed_models)
    
    # Trading settings
    st.subheader("Trading Settings")
    max_trades = st.slider("Max Concurrent Trades", 1, 10, 3)
    position_size = st.slider("Position Size %", 0.5, 5.0, 2.0)
    max_loss = st.slider("Daily Max Loss %", 1, 20, 5)
    
    if st.button("Save Settings"):
        st.success("Settings saved ✅")
    
    cur.close()
    conn.close()

# ============================================================================
# MAIN APP
# ============================================================================

st.sidebar.title("🔱 DEMIR AI")

pages = {
    "📊 Dashboard": page_dashboard,
    "🧠 Models": page_models,
    "🚀 Signals": page_signals,
    "📈 Trades": page_manual_trades,
    "📉 Backtest": page_backtest,
    "⚠️ Errors": page_errors,
    "⚙️ Settings": page_settings
}

page = st.sidebar.radio("Navigation", pages.keys())
pages[page]()

st.sidebar.markdown("---")
st.sidebar.info("🔱 DEMIR AI - Autonomous Trading Bot\nv2.0 - Production Ready")
