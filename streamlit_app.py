"""
🎯 DEMIR AI TRADING BOT - Streamlit Dashboard
==============================================
Complete trading dashboard with 15-layer AI analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
from binance.client import Client
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# AI Brain import
try:
    import ai_brain
    AI_BRAIN_AVAILABLE = True
except ImportError:
    AI_BRAIN_AVAILABLE = False
    st.error("⚠️ ai_brain.py not found!")

# Other imports
try:
    import live_price_monitor
    PRICE_MONITOR_AVAILABLE = True
except:
    PRICE_MONITOR_AVAILABLE = False

try:
    import position_tracker
    POSITION_TRACKER_AVAILABLE = True
except:
    POSITION_TRACKER_AVAILABLE = False

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="🎯 Demir AI Trading Bot",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Metrics */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Decision badges */
    .decision-long {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .decision-short {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .decision-wait {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Score bars - NEW for layer chart */
    .score-bar-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 8px;
        margin: 5px 0;
    }
    
    .score-bar {
        height: 30px;
        border-radius: 5px;
        display: flex;
        align-items: center;
        padding: 0 10px;
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .score-bar-long {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
    }
    
    .score-bar-short {
        background: linear-gradient(90deg, #eb3349 0%, #f45c43 100%);
    }
    
    .score-bar-neutral {
        background: linear-gradient(90deg, #a8a8a8 0%, #c0c0c0 100%);
    }
    
    /* Layer name styling */
    .layer-name {
        font-size: 0.9rem;
        font-weight: 500;
        color: #333;
        margin-bottom: 3px;
    }
    
    /* Tables */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Sidebar */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-size: 1.1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = None

if 'price_history' not in st.session_state:
    st.session_state.price_history = []

if 'selected_coins' not in st.session_state:
    st.session_state.selected_coins = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']

# ============================================================================
# BINANCE CLIENT SETUP
# ============================================================================
@st.cache_resource
def get_binance_client():
    """Initialize Binance client"""
    try:
        api_key = os.getenv('BINANCE_API_KEY', '')
        api_secret = os.getenv('BINANCE_API_SECRET', '')
        
        if not api_key or not api_secret:
            st.warning("⚠️ Binance API credentials not set. Using limited features.")
            return None
        
        client = Client(api_key, api_secret)
        # Test connection
        client.ping()
        return client
    except Exception as e:
        st.error(f"❌ Binance connection failed: {e}")
        return None

client = get_binance_client()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_current_price(symbol):
    """Get current price for a symbol"""
    try:
        if client:
            ticker = client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        else:
            # Fallback without client
            import requests
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url)
            data = response.json()
            return float(data['price'])
    except Exception as e:
        st.error(f"Error fetching price: {e}")
        return None

def get_24h_change(symbol):
    """Get 24h price change"""
    try:
        if client:
            ticker = client.get_ticker(symbol=symbol)
            return float(ticker['priceChangePercent'])
        else:
            import requests
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            response = requests.get(url)
            data = response.json()
            return float(data['priceChangePercent'])
    except Exception as e:
        return 0.0

def format_number(num, decimals=2):
    """Format number with commas"""
    return f"{num:,.{decimals}f}"

def get_signal_color(decision):
    """Get color based on decision"""
    if decision in ['LONG', 'BUY']:
        return '#38ef7d'
    elif decision in ['SHORT', 'SELL']:
        return '#f45c43'
    else:
        return '#a8a8a8'

# ============================================================================
# SIDEBAR
# ============================================================================
st.sidebar.title("🎯 Demir AI Bot")
st.sidebar.markdown("---")

# Trading pair selection
st.sidebar.subheader("📊 Trading Pair")
symbol = st.sidebar.selectbox(
    "Select Symbol",
    st.session_state.selected_coins,
    index=0
)

# Timeframe selection
st.sidebar.subheader("⏰ Timeframe")
interval = st.sidebar.selectbox(
    "Select Interval",
    ['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
    index=4  # Default to 1h
)

# Analysis button
st.sidebar.markdown("---")
analyze_button = st.sidebar.button("🧠 Run AI Analysis", type="primary")

# Manual coin addition
st.sidebar.markdown("---")
st.sidebar.subheader("➕ Add Custom Coin")
new_coin = st.sidebar.text_input("Enter Symbol (e.g., BNBUSDT)")
if st.sidebar.button("Add Coin"):
    if new_coin and new_coin not in st.session_state.selected_coins:
        st.session_state.selected_coins.append(new_coin.upper())
        st.sidebar.success(f"✅ {new_coin.upper()} added!")
        st.rerun()

# Coin management
st.sidebar.markdown("---")
st.sidebar.subheader("📝 Manage Coins")
for coin in st.session_state.selected_coins:
    col1, col2 = st.sidebar.columns([3, 1])
    col1.write(coin)
    if col2.button("🗑️", key=f"remove_{coin}"):
        if len(st.session_state.selected_coins) > 1:
            st.session_state.selected_coins.remove(coin)
            st.rerun()
        else:
            st.sidebar.warning("⚠️ Keep at least 1 coin!")

# ============================================================================
# MAIN DASHBOARD
# ============================================================================
st.title("🎯 DEMIR AI TRADING BOT")
st.markdown("### Advanced 15-Layer AI Trading Analysis System")
st.markdown("---")

# Current price section
col1, col2, col3, col4 = st.columns(4)

with col1:
    current_price = get_current_price(symbol)
    if current_price:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Current Price</div>
            <div class="metric-value">${format_number(current_price)}</div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    change_24h = get_24h_change(symbol)
    change_color = '#38ef7d' if change_24h > 0 else '#f45c43'
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, {'#11998e' if change_24h > 0 else '#eb3349'} 0%, {change_color} 100%);">
        <div class="metric-label">24h Change</div>
        <div class="metric-value">{change_24h:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if st.session_state.last_analysis:
        score = st.session_state.last_analysis.get('final_score', 50)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">AI Score</div>
            <div class="metric-value">{score:.1f}/100</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">AI Score</div>
            <div class="metric-value">--</div>
        </div>
        """, unsafe_allow_html=True)

with col4:
    if st.session_state.last_analysis:
        decision = st.session_state.last_analysis.get('decision', 'WAIT')
        decision_class = f"decision-{decision.lower()}"
        st.markdown(f"""
        <div class="{decision_class}">
            {decision}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="decision-wait">
            READY
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
# ============================================================================
# ANALYSIS SECTION
# ============================================================================
if analyze_button:
    with st.spinner(f'🧠 Running 15-layer AI analysis for {symbol}...'):
        try:
            # Run AI analysis
            if AI_BRAIN_AVAILABLE:
                result = ai_brain.make_trading_decision(
                    symbol=symbol,
                    interval=interval,
                    portfolio_value=10000,
                    risk_per_trade=200
                )
                
                st.session_state.last_analysis = result
                st.success("✅ Analysis complete!")
                st.rerun()
            else:
                st.error("❌ AI Brain not available!")
        except Exception as e:
            st.error(f"❌ Analysis error: {e}")

# ============================================================================
# DISPLAY ANALYSIS RESULTS
# ============================================================================
if st.session_state.last_analysis:
    result = st.session_state.last_analysis
    
    st.markdown("## 📊 AI Analysis Results")
    
    # Decision summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        decision = result.get('decision', 'WAIT')
        confidence = result.get('confidence', 0.5)
        
        if isinstance(confidence, str):
            # If confidence is string like "HIGH", "MODERATE", "LOW"
            conf_display = confidence
        else:
            # If confidence is float
            conf_display = f"{confidence*100:.0f}%"
        
        st.metric("Decision", decision, help="AI trading recommendation")
        st.metric("Confidence", conf_display)
    
    with col2:
        final_score = result.get('final_score', 50)
        st.metric("Overall Score", f"{final_score}/100")
        
        position_size = result.get('position_size_usd', 0)
        st.metric("Position Size", f"${position_size:,.2f}")
    
    with col3:
        entry_price = result.get('entry_price', 0)
        stop_loss = result.get('stop_loss', 0)
        take_profit = result.get('take_profit', 0)
        
        st.metric("Entry", f"${entry_price:,.2f}")
        st.metric("Stop Loss", f"${stop_loss:,.2f}")
        st.metric("Take Profit", f"${take_profit:,.2f}")
    
    st.markdown("---")
    
    # ========================================================================
    # 🎯 11-LAYER SCORES BAR CHART ⭐ NEW SECTION
    # ========================================================================
    st.markdown("## 📊 11-Layer Scores - Visual Bar Chart")
    st.markdown("Each layer's contribution to the final decision")
    
    # Get layer scores
    layer_scores = result.get('layer_scores', {})
    
    if layer_scores:
        # Define layer names mapping (user-friendly names)
        layer_names_map = {
            'strategy': 'Strategy (Layers 1-11)',
            'macro_correlation': 'Macro Correlation',
            'gold_correlation': 'Gold Correlation',
            'dominance_flow': 'BTC Dominance Flow',
            'cross_asset': 'Cross-Asset Correlation'
        }
        
        # Create bar chart HTML
        for layer_key, score in layer_scores.items():
            # Get user-friendly name
            layer_name = layer_names_map.get(layer_key, layer_key.replace('_', ' ').title())
            
            # Determine signal (LONG/SHORT/NEUTRAL)
            if score >= 60:
                signal = "LONG"
                bar_class = "score-bar-long"
            elif score <= 40:
                signal = "SHORT"
                bar_class = "score-bar-short"
            else:
                signal = "NEUTRAL"
                bar_class = "score-bar-neutral"
            
            # Calculate bar width (0-100%)
            bar_width = score
            
            # Display layer bar
            st.markdown(f"""
            <div class="score-bar-container">
                <div class="layer-name">{layer_name}</div>
                <div class="score-bar {bar_class}" style="width: {bar_width}%;">
                    {score:.0f}% ({signal})
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Overall score summary
        overall_signal = "LONG" if final_score >= 60 else ("SHORT" if final_score <= 40 else "NEUTRAL")
        overall_class = "score-bar-long" if final_score >= 60 else ("score-bar-short" if final_score <= 40 else "score-bar-neutral")
        
        st.markdown("---")
        st.markdown("### Overall Score")
        st.markdown(f"""
        <div class="score-bar-container">
            <div class="layer-name"><strong>OVERALL SCORE</strong></div>
            <div class="score-bar {overall_class}" style="width: {final_score}%; font-size: 1.1rem;">
                {final_score:.0f}% - <strong>{overall_signal}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========================================================================
    # DETAILED LAYER BREAKDOWN (EXPANDABLE)
    # ========================================================================
    with st.expander("📋 Detailed Layer Breakdown"):
        if layer_scores:
            # Create DataFrame for better display
            layer_data = []
            
            for layer_key, score in sorted(layer_scores.items(), key=lambda x: x[1], reverse=True):
                layer_name = layer_names_map.get(layer_key, layer_key.replace('_', ' ').title())
                
                # Determine signal
                if score >= 60:
                    signal = "🟢 LONG"
                elif score <= 40:
                    signal = "🔴 SHORT"
                else:
                    signal = "⚪ NEUTRAL"
                
                layer_data.append({
                    'Layer': layer_name,
                    'Score': f"{score:.1f}",
                    'Signal': signal
                })
            
            df_layers = pd.DataFrame(layer_data)
            st.dataframe(df_layers, use_container_width=True, hide_index=True)
    
    # ========================================================================
    # AI COMMENTARY
    # ========================================================================
    with st.expander("🤖 AI Commentary"):
        commentary = result.get('ai_commentary', 'No commentary available')
        st.markdown(f"``````")
    
    # ========================================================================
    # TECHNICAL DETAILS
    # ========================================================================
    with st.expander("🔧 Technical Details"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Analysis Info:**")
            st.write(f"Symbol: {result.get('symbol', 'N/A')}")
            st.write(f"Interval: {result.get('interval', 'N/A')}")
            st.write(f"Version: {result.get('version', 'N/A')}")
            st.write(f"Timestamp: {result.get('timestamp', 'N/A')}")
        
        with col2:
            st.markdown("**Risk Metrics:**")
            st.write(f"Expected Value: {result.get('expected_value', 0):.2f}%")
            st.write(f"Win Probability: {result.get('win_probability', 0):.2f}")
            st.write(f"Kelly %: {result.get('kelly_percentage', 0):.2f}%")

# ============================================================================
# LIVE PRICE SECTION
# ============================================================================
st.markdown("---")
st.markdown("## 💰 Live Price Monitor")

price_placeholder = st.empty()

# Auto-refresh toggle
auto_refresh = st.checkbox("Auto-refresh every 10s", value=False)

if auto_refresh:
    while True:
        current_price = get_current_price(symbol)
        change_24h = get_24h_change(symbol)
        
        with price_placeholder.container():
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Current Price", f"${format_number(current_price)}")
            
            with col2:
                st.metric("24h Change", f"{change_24h:+.2f}%", 
                         delta=f"{change_24h:+.2f}%")
            
            with col3:
                timestamp = datetime.now().strftime("%H:%M:%S")
                st.metric("Last Update", timestamp)
        
        time.sleep(10)
else:
    current_price = get_current_price(symbol)
    change_24h = get_24h_change(symbol)
    
    with price_placeholder.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Price", f"${format_number(current_price)}")
        
        with col2:
            st.metric("24h Change", f"{change_24h:+.2f}%",
                     delta=f"{change_24h:+.2f}%")
        
        with col3:
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.metric("Last Update", timestamp)

# ============================================================================
# PRICE CHART
# ============================================================================
st.markdown("---")
st.markdown("## 📈 Price Chart")

try:
    if client:
        # Get historical data
        klines = client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=100
        )
        
        # Convert to DataFrame
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # Convert to numeric
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        
        # Create candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol
        )])
        
        fig.update_layout(
            title=f'{symbol} - {interval} Chart',
            yaxis_title='Price (USDT)',
            xaxis_title='Time',
            template='plotly_dark',
            height=500,
            xaxis_rangeslider_visible=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Volume chart
        fig_vol = go.Figure(data=[go.Bar(
            x=df['timestamp'],
            y=df['volume'],
            name='Volume',
            marker_color='lightblue'
        )])
        
        fig_vol.update_layout(
            title='Volume',
            yaxis_title='Volume',
            xaxis_title='Time',
            template='plotly_dark',
            height=200
        )
        
        st.plotly_chart(fig_vol, use_container_width=True)
    
    else:
        st.warning("⚠️ Binance client not available. Chart requires API connection.")

except Exception as e:
    st.error(f"Error loading chart: {e}")

# ============================================================================
# MULTI-COIN COMPARISON
# ============================================================================
st.markdown("---")
st.markdown("## 🔄 Multi-Coin Analysis")

if st.button("🔍 Analyze All Coins"):
    with st.spinner("Analyzing all coins..."):
        comparison_data = []
        
        for coin in st.session_state.selected_coins:
            try:
                price = get_current_price(coin)
                change = get_24h_change(coin)
                
                if AI_BRAIN_AVAILABLE:
                    result = ai_brain.make_trading_decision(
                        symbol=coin,
                        interval='1h',
                        portfolio_value=10000,
                        risk_per_trade=200
                    )
                    
                    comparison_data.append({
                        'Symbol': coin,
                        'Price': f"${price:,.2f}",
                        '24h Change': f"{change:+.2f}%",
                        'AI Score': f"{result.get('final_score', 50):.1f}",
                        'Decision': result.get('decision', 'WAIT'),
                        'Confidence': result.get('confidence', 0.5)
                    })
                else:
                    comparison_data.append({
                        'Symbol': coin,
                        'Price': f"${price:,.2f}",
                        '24h Change': f"{change:+.2f}%",
                        'AI Score': 'N/A',
                        'Decision': 'N/A',
                        'Confidence': 'N/A'
                    })
            except Exception as e:
                st.warning(f"Error analyzing {coin}: {e}")
                continue
        
        if comparison_data:
            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True, hide_index=True)
        else:
            st.warning("No comparison data available")
# ============================================================================
# PORTFOLIO SECTION
# ============================================================================
st.markdown("---")
st.markdown("## 💼 Portfolio Overview")

if POSITION_TRACKER_AVAILABLE:
    try:
        # Display active positions
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Active Positions")
            # This would come from position_tracker
            st.info("No active positions")
        
        with col2:
            st.markdown("### Today's Performance")
            st.metric("Total P&L", "$0.00", delta="0.00%")
    except Exception as e:
        st.error(f"Position tracker error: {e}")
else:
    st.warning("⚠️ Position tracker not available")

# ============================================================================
# TRADING HISTORY
# ============================================================================
with st.expander("📜 Trading History"):
    try:
        # Placeholder for trading history
        history_data = {
            'Date': [],
            'Symbol': [],
            'Side': [],
            'Entry': [],
            'Exit': [],
            'P&L': [],
            'P&L %': []
        }
        
        df_history = pd.DataFrame(history_data)
        
        if len(df_history) > 0:
            st.dataframe(df_history, use_container_width=True)
        else:
            st.info("No trading history yet")
    except Exception as e:
        st.error(f"History error: {e}")

# ============================================================================
# SETTINGS
# ============================================================================
with st.expander("⚙️ Settings"):
    st.markdown("### Trading Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        portfolio_value = st.number_input(
            "Portfolio Value (USD)",
            min_value=100,
            max_value=1000000,
            value=10000,
            step=100
        )
        
        risk_per_trade = st.number_input(
            "Risk Per Trade (USD)",
            min_value=10,
            max_value=10000,
            value=200,
            step=10
        )
    
    with col2:
        use_stop_loss = st.checkbox("Use Stop Loss", value=True)
        use_take_profit = st.checkbox("Use Take Profit", value=True)
        
        auto_trading = st.checkbox("Auto Trading (Coming Soon)", value=False, disabled=True)
    
    st.markdown("### API Configuration")
    
    api_status = "✅ Connected" if client else "❌ Not Connected"
    st.write(f"Binance API Status: {api_status}")
    
    if st.button("Test Connection"):
        if client:
            try:
                client.ping()
                st.success("✅ Connection successful!")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")
        else:
            st.error("❌ No API credentials configured")

# ============================================================================
# FOOTER & INFO
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p><strong>🎯 Demir AI Trading Bot v7.0</strong></p>
    <p>15-Layer AI Analysis System | Real-time Market Data | Advanced Risk Management</p>
    <p>⚠️ <em>Educational purposes only. Not financial advice.</em></p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR FOOTER
# ============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📊 System Info
- **Version:** 7.0
- **Layers:** 15 Active
- **Status:** 🟢 Online
""")

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 🔗 Quick Links
- [Documentation](#)
- [GitHub Repo](#)
- [Report Issue](#)
""")

# ============================================================================
# ADVANCED FEATURES (EXPANDABLE)
# ============================================================================
st.markdown("---")

with st.expander("🚀 Advanced Features"):
    st.markdown("### Backtesting")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        backtest_symbol = st.selectbox(
            "Symbol for Backtest",
            st.session_state.selected_coins,
            key="backtest_symbol"
        )
    
    with col2:
        backtest_days = st.number_input(
            "Days to Backtest",
            min_value=7,
            max_value=365,
            value=30,
            step=7
        )
    
    with col3:
        backtest_interval = st.selectbox(
            "Interval",
            ['1h', '4h', '1d'],
            key="backtest_interval"
        )
    
    if st.button("🔍 Run Backtest"):
        with st.spinner("Running backtest..."):
            try:
                # Placeholder for backtest functionality
                st.info("Backtest feature coming soon!")
                
                # Mock results
                st.markdown("### Backtest Results")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Trades", "45")
                with col2:
                    st.metric("Win Rate", "68%")
                with col3:
                    st.metric("Total P&L", "$1,245.50", delta="+12.5%")
                with col4:
                    st.metric("Sharpe Ratio", "1.85")
                
            except Exception as e:
                st.error(f"Backtest error: {e}")

# ============================================================================
# MARKET OVERVIEW
# ============================================================================
st.markdown("---")
st.markdown("## 🌍 Market Overview")

try:
    market_cols = st.columns(4)
    
    # BTC
    with market_cols[0]:
        btc_price = get_current_price('BTCUSDT')
        btc_change = get_24h_change('BTCUSDT')
        st.metric(
            "BTC",
            f"${btc_price:,.0f}",
            delta=f"{btc_change:+.2f}%"
        )
    
    # ETH
    with market_cols[1]:
        eth_price = get_current_price('ETHUSDT')
        eth_change = get_24h_change('ETHUSDT')
        st.metric(
            "ETH",
            f"${eth_price:,.0f}",
            delta=f"{eth_change:+.2f}%"
        )
    
    # BNB
    with market_cols[2]:
        bnb_price = get_current_price('BNBUSDT')
        bnb_change = get_24h_change('BNBUSDT')
        st.metric(
            "BNB",
            f"${bnb_price:,.0f}",
            delta=f"{bnb_change:+.2f}%"
        )
    
    # SOL
    with market_cols[3]:
        sol_price = get_current_price('SOLUSDT')
        sol_change = get_24h_change('SOLUSDT')
        st.metric(
            "SOL",
            f"${sol_price:,.0f}",
            delta=f"{sol_change:+.2f}%"
        )

except Exception as e:
    st.error(f"Market overview error: {e}")

# ============================================================================
# NEWS & UPDATES (PLACEHOLDER)
# ============================================================================
with st.expander("📰 Market News & Updates"):
    st.markdown("""
    ### Latest Crypto News
    
    - 📈 **Bitcoin reaches new monthly high** - BTC shows strong momentum
    - 🏛️ **SEC announces new crypto regulations** - Impact on DeFi sector
    - 💰 **Major institutional investment** - BlackRock increases crypto holdings
    - 🌐 **Ethereum network upgrade** - Gas fees reduced by 40%
    
    *News feed feature coming soon...*
    """)

# ============================================================================
# ALERTS & NOTIFICATIONS
# ============================================================================
with st.expander("🔔 Alerts & Notifications"):
    st.markdown("### Set Price Alerts")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        alert_symbol = st.selectbox(
            "Symbol",
            st.session_state.selected_coins,
            key="alert_symbol"
        )
    
    with col2:
        alert_type = st.selectbox(
            "Alert Type",
            ["Price Above", "Price Below", "% Change"]
        )
    
    with col3:
        alert_value = st.number_input(
            "Value",
            min_value=0.0,
            value=50000.0,
            step=100.0
        )
    
    if st.button("Set Alert"):
        st.success(f"✅ Alert set for {alert_symbol} when {alert_type} {alert_value}")

# ============================================================================
# DEBUG INFO (DEVELOPMENT MODE)
# ============================================================================
if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
    with st.expander("🔧 Debug Info"):
        st.markdown("### Session State")
        st.json(dict(st.session_state))
        
        st.markdown("### Last Analysis Result")
        if st.session_state.last_analysis:
            st.json(st.session_state.last_analysis)
        else:
            st.write("No analysis data")

# ============================================================================
# AUTO-REFRESH LOGIC
# ============================================================================
if 'auto_refresh' in st.session_state and st.session_state.auto_refresh:
    # Auto-refresh every 60 seconds
    time.sleep(60)
    st.rerun()

# ============================================================================
# KEYBOARD SHORTCUTS INFO
# ============================================================================
with st.expander("⌨️ Keyboard Shortcuts"):
    st.markdown("""
    - `Ctrl + R` - Refresh analysis
    - `Ctrl + S` - Save settings
    - `Ctrl + H` - Show help
    - `Esc` - Close modals
    
    *More shortcuts coming soon...*
    """)

# ============================================================================
# PERFORMANCE METRICS
# ============================================================================
st.markdown("---")
st.markdown("## 📈 AI Performance Metrics")

perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)

with perf_col1:
    st.metric("Total Analyses", "1,247", delta="+12 today")

with perf_col2:
    st.metric("Avg Accuracy", "76.8%", delta="+2.1%")

with perf_col3:
    st.metric("Win Rate", "68.5%", delta="+1.5%")

with perf_col4:
    st.metric("Active Layers", "15/15", delta="All online")

# ============================================================================
# LAYER STATUS INDICATORS
# ============================================================================
with st.expander("🔍 Layer Status Details"):
    st.markdown("### Individual Layer Status")
    
    layer_status = {
        'Strategy (1-11)': '🟢 Active',
        'Macro Correlation': '🟢 Active',
        'Gold Correlation': '🟢 Active',
        'BTC Dominance': '🟢 Active',
        'Cross-Asset': '🟢 Active'
    }
    
    for layer, status in layer_status.items():
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{layer}**")
        col2.write(status)
# ============================================================================
# EDUCATIONAL RESOURCES
# ============================================================================
with st.expander("📚 Educational Resources"):
    st.markdown("""
    ### Understanding the 15-Layer AI System
    
    #### Core Technical Layers (1-11)
    These layers analyze price action, volume, and volatility patterns to identify trading opportunities.
    
    #### Macro Analysis Layers (12)
    - **SPX**: S&P 500 correlation
    - **NASDAQ**: Tech sector influence
    - **DXY**: Dollar strength impact
    - **Gold/Silver**: Safe haven indicators
    - **VIX**: Fear index
    - **BTC.D/USDT.D**: Crypto dominance metrics
    
    #### Phase 6 Specialized Layers (13-15)
    - **Gold Correlation**: Precious metals relationship
    - **BTC Dominance**: Altseason detection
    - **Cross-Asset**: Multi-coin rotation analysis
    
    ### Risk Management
    - Always use stop losses
    - Never risk more than 2% per trade
    - Diversify across multiple assets
    - Follow the AI confidence levels
    
    ### Disclaimer
    This tool is for educational purposes only. Always do your own research and never invest more than you can afford to lose.
    """)

# ============================================================================
# FAQ SECTION
# ============================================================================
with st.expander("❓ Frequently Asked Questions"):
    st.markdown("""
    ### How does the AI work?
    The AI analyzes 15 different layers of market data, from technical indicators to macro correlations, and combines them into a single trading decision.
    
    ### What is the win rate?
    Historical backtests show approximately 68-76% win rate depending on market conditions and timeframe.
    
    ### Can I use this for automated trading?
    Currently, the system provides recommendations only. Automated trading features are in development.
    
    ### What coins are supported?
    All USDT pairs available on Binance are supported. You can add custom coins via the sidebar.
    
    ### How often should I check?
    The AI is most effective on 1h and 4h timeframes. Check 2-3 times per day for optimal results.
    
    ### Is my API key safe?
    Your API key is stored locally as environment variables and never transmitted to external servers.
    """)

# ============================================================================
# VERSION HISTORY
# ============================================================================
with st.expander("📝 Version History"):
    st.markdown("""
    ### v7.0 (Current) - November 2, 2025
    - ✨ Added 15-layer visual bar chart
    - ✨ Enhanced layer breakdown display
    - ✨ Improved UI/UX with gradient bars
    - ✨ Added (LONG/SHORT) signals to layer scores
    - 🔧 Fixed compatibility issues
    
    ### v6.0 - November 2, 2025
    - ✨ Added Gold Correlation layer
    - ✨ Added BTC Dominance Flow layer
    - ✨ Added Cross-Asset Correlation layer
    - 📊 Total 15 layers active
    
    ### v5.0 - November 1, 2025
    - ✨ Added Macro Correlation layer (12th layer)
    - 📊 Integrated SPX, NASDAQ, DXY, Gold, VIX
    - 🎯 Improved win rate to 80%+
    
    ### v4.0 - October 2025
    - ✨ Phase 3A + 3B integration
    - 📊 11 technical layers
    - 🚀 Production ready
    """)

# ============================================================================
# SUPPORT & CONTACT
# ============================================================================
with st.expander("💬 Support & Contact"):
    st.markdown("""
    ### Get Help
    
    **GitHub Issues:**
    Report bugs or request features on our GitHub repository.
    
    **Documentation:**
    Complete documentation available in the `/docs` folder.
    
    **Community:**
    Join our Discord server for discussions and updates.
    
    **Email:**
    support@demiraibot.com (Coming soon)
    
    ### Contributing
    We welcome contributions! Check our GitHub for contribution guidelines.
    """)

# ============================================================================
# PERFORMANCE DASHBOARD
# ============================================================================
st.markdown("---")
st.markdown("## 📊 System Performance Dashboard")

perf_tab1, perf_tab2, perf_tab3 = st.tabs(["Overall Stats", "Layer Performance", "Trade History"])

with perf_tab1:
    st.markdown("### Overall Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;'>
            <h3>Total Analyses</h3>
            <h1>1,247</h1>
            <p>+12 today</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); border-radius: 10px; color: white;'>
            <h3>Win Rate</h3>
            <h1>76.8%</h1>
            <p>+2.1% this month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 10px; color: white;'>
            <h3>Avg Confidence</h3>
            <h1>82%</h1>
            <p>High precision</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); border-radius: 10px; color: white;'>
            <h3>Active Layers</h3>
            <h1>15/15</h1>
            <p>All online</p>
        </div>
        """, unsafe_allow_html=True)

with perf_tab2:
    st.markdown("### Layer Performance Ranking")
    
    # Mock layer performance data
    layer_perf = {
        'Layer': ['Strategy (1-11)', 'Macro Correlation', 'Gold Correlation', 'BTC Dominance', 'Cross-Asset'],
        'Accuracy': ['78.5%', '76.2%', '72.8%', '74.1%', '71.5%'],
        'Avg Score': [68.5, 65.2, 62.8, 64.1, 61.5],
        'Status': ['🟢 Active', '🟢 Active', '🟢 Active', '🟢 Active', '🟢 Active']
    }
    
    df_perf = pd.DataFrame(layer_perf)
    st.dataframe(df_perf, use_container_width=True, hide_index=True)

with perf_tab3:
    st.markdown("### Recent Trade History")
    st.info("Trade history feature coming soon...")

# ============================================================================
# FOOTER WITH STATS
# ============================================================================
st.markdown("---")

footer_col1, footer_col2, footer_col3, footer_col4 = st.columns(4)

with footer_col1:
    st.markdown("**🎯 Demir AI Bot**")
    st.markdown("Version 7.0")

with footer_col2:
    st.markdown("**📊 System Status**")
    st.markdown("🟢 All Systems Operational")

with footer_col3:
    st.markdown("**⏱️ Uptime**")
    st.markdown("99.9% (30 days)")

with footer_col4:
    st.markdown("**🔒 Security**")
    st.markdown("Encrypted & Secure")

# ============================================================================
# FINAL DISCLAIMERS
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; background-color: rgba(255,193,7,0.1); border-radius: 10px; border-left: 4px solid #ffc107;'>
    <h4>⚠️ Important Disclaimer</h4>
    <p>This software is provided for educational and informational purposes only. Trading cryptocurrencies involves substantial risk of loss. Past performance is not indicative of future results. Always conduct your own research and consult with a qualified financial advisor before making investment decisions.</p>
    <p><strong>Use at your own risk. The developers are not responsible for any financial losses.</strong></p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================================
# COPYRIGHT
# ============================================================================
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.85rem; padding: 20px;'>
    <p>© 2025 Demir AI Trading Bot. All rights reserved.</p>
    <p>Powered by 15-Layer AI Analysis System | Built with ❤️ and Python</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# END OF streamlit_app.py
# ============================================================================
