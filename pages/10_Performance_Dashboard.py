"""
FILE 4: pages/10_Performance_Dashboard.py
PHASE 2.2 - PERFORMANCE ANALYTICS DASHBOARD
Streamlit UI for performance tracking
"""

import streamlit as st
import pandas as pd
from performance_analyzer import PerformanceAnalyzer
from datetime import datetime, timedelta

def show_performance_dashboard():
    st.set_page_config(page_title="Performance Dashboard", layout="wide")
    st.title("📊 Performance Analytics Dashboard")
    
    analyzer = PerformanceAnalyzer()
    
    # Tab selection
    tab1, tab2, tab3 = st.tabs(["Trade Statistics", "Signal Accuracy", "Suggestions"])
    
    with tab1:
        st.subheader("📈 Trade Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        stats_7d = analyzer.get_trade_statistics(days=7)
        
        with col1:
            st.metric("Total Trades (7d)", stats_7d.get('total_trades', 0))
        with col2:
            st.metric("Win Rate", f"{stats_7d.get('win_rate_percent', 0):.1f}%")
        with col3:
            st.metric("Total P&L", f"${stats_7d.get('total_pnl', 0):,.2f}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Best Trade", f"${stats_7d.get('best_trade', 0):.2f}")
        with col2:
            st.metric("Worst Trade", f"${stats_7d.get('worst_trade', 0):.2f}")
        with col3:
            st.metric("Profit Factor", f"{stats_7d.get('profit_factor', 0):.2f}")
        with col4:
            st.metric("Avg P&L", f"${stats_7d.get('avg_pnl', 0):.2f}")
        
        st.dataframe(pd.DataFrame([stats_7d]))
    
    with tab2:
        st.subheader("🎯 Signal Accuracy")
        
        accuracy = analyzer.get_signal_accuracy(days=7)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Signals", accuracy.get('total_signals', 0))
        with col2:
            st.metric("Correct", accuracy.get('correct_signals', 0))
        with col3:
            st.metric("Accuracy %", f"{accuracy.get('accuracy_percent', 0):.1f}%")
        
        best_crypto = analyzer.get_best_performing_crypto()
        st.success(f"🏆 Best Performing Crypto: {best_crypto}")
    
    with tab3:
        st.subheader("💡 AI-Generated Improvement Suggestions")
        
        suggestions = analyzer.get_improvement_suggestions()
        
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                st.info(f"{i}. {suggestion}")
        else:
            st.warning("No suggestions at this time")

if __name__ == "__main__":
    show_performance_dashboard()
