"""
FILE 7: 11_Opportunity_Scanner.py
PHASE 3.3 - OPPORTUNITY SCANNER UI
Streamlit dashboard for patterns & whales
"""

import streamlit as st
import pandas as pd
from pattern_recognition import PatternRecognizer
from whale_detector import WhaleDetector
import asyncio

def show_opportunity_scanner():
    st.set_page_config(page_title="Opportunity Scanner", layout="wide")
    st.title("🎯 Opportunity Scanner")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        symbols = st.multiselect("Select Symbols", ["BTCUSDT", "ETHUSDT", "LTCUSDT"], default=["BTCUSDT"])
    
    with col2:
        timeframe = st.selectbox("Timeframe", ["1h", "4h", "1d"])
    
    with col3:
        refresh = st.slider("Refresh (seconds)", 60, 3600, 300)
    
    st.subheader("📊 Pattern Recognition")
    recognizer = PatternRecognizer()
    
    for symbol in symbols:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"Scan {symbol}"):
                with st.spinner(f"Scanning {symbol}..."):
                    h_s = asyncio.run(recognizer.detect_head_and_shoulders(symbol, timeframe))
                    db = asyncio.run(recognizer.detect_double_bottom(symbol, timeframe))
                    bo = asyncio.run(recognizer.detect_breakout(symbol, timeframe))
                    
                    if h_s.get('pattern_found'):
                        st.success(f"✅ H&S Pattern: {h_s.get('confidence', 0):.1f}% confidence")
                    
                    if db.get('pattern_found'):
                        st.success(f"✅ Double Bottom: {db.get('confidence', 0):.1f}% confidence")
                    
                    if bo.get('breakout'):
                        st.warning(f"⚡ Breakout {bo.get('direction')}: {bo.get('current_price')}")
    
    st.subheader("🐋 Whale Activity")
    detector = WhaleDetector()
    
    for symbol in symbols:
        if st.button(f"Whale Check {symbol}"):
            with st.spinner(f"Checking whales for {symbol}..."):
                whales = asyncio.run(detector.detect_large_transactions(symbol))
                
                if whales.get('large_buys', 0) > 0 or whales.get('large_sells', 0) > 0:
                    st.warning(f"🐋 Detected: {whales.get('large_buys')} buys, {whales.get('large_sells')} sells")
                    st.dataframe(pd.DataFrame(whales.get('transactions', [])))

if __name__ == "__main__":
    show_opportunity_scanner()
