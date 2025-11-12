"""
FILE 9: 12_Backtesting.py
PHASE 4.2 - BACKTESTING DASHBOARD UI
Streamlit UI for backtesting
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import asyncio
from backtest_engine_enhanced import BacktestEngine

def show_backtesting_page():
    st.set_page_config(page_title="Backtesting", layout="wide")
    st.title("📊 Advanced Backtesting")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        symbol = st.selectbox("Symbol", ["BTCUSDT", "ETHUSDT", "LTCUSDT"])
    
    with col2:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    
    with col3:
        end_date = st.date_input("End Date", datetime.now())
    
    with col4:
        initial_capital = st.number_input("Initial Capital ($)", 10000, 1000000, 10000)
    
    if st.button("Run Backtest", key="run_backtest"):
        with st.spinner("Running backtest..."):
            backtest = BacktestEngine()
            results = asyncio.run(backtest.backtest_strategy(
                symbol,
                str(start_date),
                str(end_date),
                initial_capital
            ))
            
            if 'error' not in results:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Trades", results.get('total_trades', 0))
                with col2:
                    st.metric("Win Rate", f"{results.get('win_rate', 0):.1f}%")
                with col3:
                    st.metric("Total Return", f"{results.get('total_return', 0):.2f}%")
                with col4:
                    st.metric("Final Capital", f"${results.get('final_capital', 0):,.0f}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Best Trade", f"${results.get('best_trade', 0):.2f}")
                with col2:
                    st.metric("Worst Trade", f"${results.get('worst_trade', 0):.2f}")
                with col3:
                    st.metric("Profit Factor", f"{results.get('profit_factor', 0):.2f}")
                
                st.dataframe(pd.DataFrame([results]))
            else:
                st.error(f"Backtest error: {results.get('error')}")

if __name__ == "__main__":
    show_backtesting_page()
