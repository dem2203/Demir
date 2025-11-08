# app.py
import streamlit as st

st.set_page_config(page_title="DEMIR AI", page_icon="🔱")

st.title("🔱 DEMIR AI v23.0")
st.markdown("Advanced Trading Intelligence")

with st.columns(4)[0]:
    st.metric("BTC", "$47,500", "+2.5%")

st.success("✅ Application is running!")
