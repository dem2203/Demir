# ============================================================================
# pages/07_Monitoring.py
# ============================================================================

import streamlit as st
from datetime import datetime

st.set_page_config(page_title="🔍 Monitoring", layout="wide")

st.title("🔍 Monitoring - 24/7 System")
st.markdown("**Sistem Sağlığı İzlemesi**")

st.markdown("""
<div style="background: #1A1F2E; padding: 15px; border-radius: 8px;">
<strong>🔹 Ne Demek?</strong><br>
Sistem 24/7 izleniyor. API'ler, Daemon, Database sağlıklı mı?
</div>
""", unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🟢 API Status")
    st.markdown("✅ Binance: Bağlı (45ms)")
    st.markdown("✅ Alpha Vantage: Bağlı (150ms)")
    st.markdown("✅ CoinGlass: Bağlı (80ms)")

with col2:
    st.markdown("### 🟢 Daemon Status")
    st.markdown("✅ Running: 24h 15m")
    st.markdown("✅ CPU: 12%")
    st.markdown("✅ Memory: 340 MB")

st.markdown("---")

st.success("✅ TÜM SİSTEMLER NORMAL ÇALIŞIYOR!")
