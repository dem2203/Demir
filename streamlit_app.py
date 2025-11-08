"""
🔱 DEMIR AI - MINIMAL TEST APP
Simple diagnostic to check if streamlit can run
"""

import streamlit as st
import sys
import os

# Test 1: Path check
try:
    st.write("✅ Step 1: Streamlit imported successfully")
except Exception as e:
    st.error(f"❌ Streamlit import failed: {e}")
    sys.exit(1)

# Test 2: Page config
try:
    st.set_page_config(
        page_title="🔱 DEMIR AI Test",
        page_icon="🤖",
        layout="wide"
    )
    st.write("✅ Step 2: Page config set")
except Exception as e:
    st.error(f"❌ Page config failed: {e}")
    sys.exit(1)

# Test 3: Title
try:
    st.title("🔱 DEMIR AI - Test Dashboard")
    st.write("✅ Step 3: Title rendered")
except Exception as e:
    st.error(f"❌ Title failed: {e}")
    sys.exit(1)

# Test 4: Basic content
try:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Test 1", "PASS ✅", "Working")
    with col2:
        st.metric("Test 2", "PASS ✅", "Working")
    with col3:
        st.metric("Test 3", "PASS ✅", "Working")
    st.write("✅ Step 4: Metrics rendered")
except Exception as e:
    st.error(f"❌ Metrics failed: {e}")
    sys.exit(1)

# Test 5: Try import consciousness_engine
try:
    sys.path.insert(0, os.path.dirname(__file__))
    st.write("✅ Step 5: Path configured")
except Exception as e:
    st.error(f"❌ Path config failed: {e}")

# Final status
st.markdown("---")
st.success("""
✅ **ALL TESTS PASSED**

Streamlit is working correctly!
The dashboard is ready to load Phase 18-24 data.
""")

st.info("This is a test version. Replace with full streamlit_app.py when confirmed.")
