# ============================================================================
# pages/04_Intelligence.py
# ============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="🤖 Intelligence", layout="wide")

st.title("🤖 Intelligence - Global Analysis")
st.markdown("**Makro + On-Chain + Sentiment Analizi**")

st.markdown("""
<div style="background: #1A1F2E; padding: 15px; border-radius: 8px;">
<strong>🔹 Ne Demek?</strong><br>
Piyasanın 3 boyutlu analizi:
• Makro: Ekonomi (SPX, DXY, Gold, Oil)
• On-Chain: Blockchain (Whale, Exchange)
• Sentiment: Duygu (Twitter, News, Fear)
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("## 📊 Intelligence Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📈 Makro")
    st.markdown("SPX: ✅ Bullish")
    st.markdown("DXY: ✅ Weak")
    st.markdown("Gold: ✅ Safe Haven")
    st.markdown("Oil: ⚠️ Mixed")

with col2:
    st.markdown("### ⛓️ On-Chain")
    st.markdown("Whale: ✅ Buying")
    st.markdown("Exchange: ⚠️ Inflow")
    st.markdown("MVRV: ⚠️ Neutral")
    st.markdown("SOPR: ✅ Positive")

with col3:
    st.markdown("### 💬 Sentiment")
    st.markdown("Twitter: ✅ Bullish")
    st.markdown("News: ✅ Positive")
    st.markdown("Fear: ✅ Greedy")
    st.markdown("Social: ✅ Volume Up")

st.markdown("---")

st.markdown("## 🎯 Global Signal")

st.success("🟢 **OVERALL: BULLISH BIAS** (Makro + On-Chain + Sentiment uyumlu)")

st.markdown(f"<small>Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>", unsafe_allow_html=True)
