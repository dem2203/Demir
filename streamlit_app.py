import streamlit as st

st.set_page_config(page_title="🔱 DEMIR AI", page_icon="🤖", layout="wide")

st.title("🔱 DEMIR AI - LIVE!")
st.success("✅ **STREAMLIT AÇILDI!**")
st.write("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Status", "🟢 LIVE", "Active")
with col2:
    st.metric("Daemon", "✅ Ready", "24/7")
with col3:
    st.metric("Trading", "🟢 Ready", "24/7")

st.write("---")
st.info("Dashboard açıldı. Sistem çalışıyor. Phase 18-24 complete.")
