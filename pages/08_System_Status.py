# ============================================================================
# pages/08_System_Status.py
# ============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="⚙️ System Status", layout="wide")

st.title("⚙️ System Status - Dashboard")
st.markdown("**Daemon ve Database Durumu**")

st.markdown("""
<div style="background: #1A1F2E; padding: 15px; border-radius: 8px;">
<strong>🔹 Ne Demek?</strong><br>
Daemon'un çalışma durumu, database boyutu, bugünün istatistikleri
</div>
""", unsafe_allow_html=True)

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Uptime", "24h 15m", "Active")

with col2:
    st.metric("Database", "2.5 GB", "Total")

with col3:
    st.metric("Signals Today", "45", "Sent")

with col4:
    st.metric("Trades Open", "5", "Active")

st.markdown("---")

stats = {
    'Component': ['Database', 'CPU', 'Memory', 'Disk', 'Network'],
    'Status': ['✅ OK', '✅ OK', '✅ OK', '✅ OK', '✅ OK'],
    'Value': ['2.5 GB', '12%', '340 MB', '45 GB', '250 Mbps']
}

df = pd.DataFrame(stats)
st.dataframe(df, use_container_width=True)
