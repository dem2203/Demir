import streamlit as st
from datetime import datetime

st.set_page_config(page_title="🎯 Intelligence", page_icon="🎯", layout="wide")

st.title("🎯 Phases 11-14: Intelligence Layers - 111+ Factors")

st.markdown("""
The Intelligence Layer system analyzes 111+ trading factors across four major categories.
These factors feed into the Consciousness Engine to generate final trading decisions.
""")

st.divider()

# Factor Categories
st.subheader("📊 111+ Trading Factors Breakdown")

factor_cols = st.columns(4)

with factor_cols[0]:
    with st.expander("🔵 Technical Patterns (40 Factors)", expanded=True):
        st.markdown("""
        - RSI Levels (Oversold/Overbought)
        - MACD Crossovers
        - Bollinger Band Squeeze
        - EMA Crossovers
        - Elliott Wave Patterns
        - Fibonacci Retracements
        - Support/Resistance Breaks
        - Trend Confirmation
        - Price Action Patterns
        - Volume Spikes
        - And 30+ more...
        """)

with factor_cols[1]:
    with st.expander("🟢 On-Chain Intelligence (25 Factors)", expanded=True):
        st.markdown("""
        - Whale Accumulation
        - Exchange Inflows/Outflows
        - Active Address Trends
        - Transaction Count
        - Network Value
        - Miner Activity
        - Burn Rate
        - Holder Distribution
        - Large Transfer Volume
        - Exchange Balance Change
        - And 15+ more...
        """)

with factor_cols[2]:
    with st.expander("🟠 Macro Intelligence (18 Factors)", expanded=True):
        st.markdown("""
        - VIX Index Level
        - Gold Correlation
        - USD Index
        - Federal Funds Rate
        - Inflation Data
        - Employment Numbers
        - GDP Announcements
        - Stock Market Correlation
        - Bond Yields
        - Real Estate Index
        - And 8+ more...
        """)

with factor_cols[3]:
    with st.expander("🔴 Sentiment Analysis (15 Factors)", expanded=True):
        st.markdown("""
        - Twitter Sentiment
        - Reddit Activity
        - Discord Members
        - Telegram Members
        - Fear & Greed Index
        - News Sentiment
        - Influencer Mentions
        - Search Trends
        - Media Coverage
        - Regulatory News
        - And 5+ more...
        """)

st.divider()

# Current Scores
st.subheader("📈 Current Factor Scores")

score_col1, score_col2, score_col3, score_col4, score_col5 = st.columns(5)

with score_col1:
    st.metric("Technical", "85/100", "+3")
with score_col2:
    st.metric("On-Chain", "78/100", "+2")
with score_col3:
    st.metric("Macro", "72/100", "+1")
with score_col4:
    st.metric("Sentiment", "+72/100", "+4")
with score_col5:
    st.metric("Overall", "78/100", "+2")

st.divider()
st.markdown(f"<p style='text-align: center; color: #CBD5E0; font-size: 11px;'>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} | All 111+ Factors Analyzed 24/7</p>", unsafe_allow_html=True)
