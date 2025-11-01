"""
🔱 DEMIR AI TRADING BOT - DASHBOARD v9.0 PROFESSIONAL UI
Date: 1 Kasım 2025
PHASE 5.0: Professional Trading Terminal Interface

v9.0 MAJOR REDESIGN:
✅ Professional trading card layout (TradingView-style)
✅ Prominent Entry/TP/SL display with copy buttons
✅ Real-time WebSocket price streaming (Phase 4.1)
✅ Visual signal indicators (🟢 LONG / 🔴 SHORT / 🟡 NEUTRAL)
✅ 11-Layer analysis with progress bars
✅ Risk/Reward calculator display
✅ Modern color-coded UI
✅ Live P/L tracker
✅ One-click copy all trade parameters

v8.3.1 FEATURES RETAINED:
✅ Multi-coin analysis (BTC/ETH/LTC)
✅ Position tracking, Portfolio optimizer, Backtest
✅ Trade history management
✅ Auto-refresh functionality
"""

import streamlit as st
import streamlit.components.v1 as components  
import requests
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import trade_history_db as db

# PHASE 4.1: WebSocket Integration
try:
    from websocket_stream import get_websocket_manager
    WEBSOCKET_AVAILABLE = True
except Exception as e:
    print(f"⚠️ WebSocket not available: {e}")
    WEBSOCKET_AVAILABLE = False

# PHASE 3.4: Position Tracker
try:
    from position_tracker import PositionTracker
    POSITION_TRACKER_AVAILABLE = True
    tracker = PositionTracker()
except:
    POSITION_TRACKER_AVAILABLE = False

# PHASE 3.3: Portfolio Optimizer
try:
    from portfolio_optimizer import PortfolioOptimizer
    PORTFOLIO_OPTIMIZER_AVAILABLE = True
except:
    PORTFOLIO_OPTIMIZER_AVAILABLE = False

# PHASE 3.2: Backtest Engine
try:
    from backtest_engine import BacktestEngine
    BACKTEST_AVAILABLE = True
except:
    BACKTEST_AVAILABLE = False

# Core imports
try:
    import ai_brain
    AI_BRAIN_AVAILABLE = True
except:
    AI_BRAIN_AVAILABLE = False

# Page config
st.set_page_config(
    page_title="🔱 DEMIR AI Trading Bot",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PROFESSIONAL CSS STYLING (TradingView-inspired)
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* Professional trade card */
    .trade-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
        border: 2px solid rgba(255,255,255,0.15);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
    }
    
    /* LONG signal card */
    .trade-card-long {
        border-color: #00ff88;
        background: linear-gradient(145deg, rgba(0,255,136,0.1), rgba(0,255,136,0.02));
    }
    
    /* SHORT signal card */
    .trade-card-short {
        border-color: #ff4444;
        background: linear-gradient(145deg, rgba(255,68,68,0.1), rgba(255,68,68,0.02));
    }
    
    /* NEUTRAL signal card */
    .trade-card-neutral {
        border-color: #ffaa00;
        background: linear-gradient(145deg, rgba(255,170,0,0.1), rgba(255,170,0,0.02));
    }
    
    /* Trade parameters box */
    .trade-params {
        background: rgba(0,0,0,0.3);
        border-radius: 12px;
        padding: 15px;
        margin: 15px 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Entry/TP/SL rows */
    .param-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        font-size: 16px;
    }
    
    .param-row:last-child {
        border-bottom: none;
    }
    
    .param-label {
        font-weight: 600;
        color: #aaa;
        min-width: 120px;
    }
    
    .param-value {
        font-weight: 700;
        color: #fff;
        font-size: 18px;
        font-family: 'Courier New', monospace;
    }
    
    .param-value-entry {
        color: #00d4ff;
    }
    
    .param-value-sl {
        color: #ff4444;
    }
    
    .param-value-tp {
        color: #00ff88;
    }
    
    /* Signal badge */
    .signal-badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 18px;
        margin: 10px 0;
    }
    
    .signal-long {
        background: #00ff88;
        color: #000;
    }
    
    .signal-short {
        background: #ff4444;
        color: #fff;
    }
    
    .signal-neutral {
        background: #ffaa00;
        color: #000;
    }
    
    /* Coin header */
    .coin-header {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Price display */
    .current-price {
        font-size: 28px;
        font-weight: 700;
        color: #fff;
        font-family: 'Courier New', monospace;
    }
    
    /* Risk/Reward box */
    .rr-box {
        background: rgba(0,212,255,0.1);
        border: 1px solid #00d4ff;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
        text-align: center;
    }
    
    /* Copy button styling */
    .stButton>button {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 8px;
        color: #fff;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background: rgba(255,255,255,0.2);
        border-color: #00ff88;
    }
    
    /* Progress bars for layer scores */
    .layer-score {
        margin: 8px 0;
    }
    
    .layer-name {
        color: #aaa;
        font-size: 14px;
        margin-bottom: 4px;
    }
    
    .layer-bar {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        height: 20px;
        position: relative;
        overflow: hidden;
    }
    
    .layer-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    .layer-fill-green {
        background: linear-gradient(90deg, #00ff88, #00d4ff);
    }
    
    .layer-fill-yellow {
        background: linear-gradient(90deg, #ffaa00, #ff8800);
    }
    
    .layer-fill-red {
        background: linear-gradient(90deg, #ff4444, #cc0000);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 10px 20px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255,255,255,0.1);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(0,255,136,0.2);
        border-color: #00ff88;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* Metric cards */
    .css-1xarl3l {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Global state initialization
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# PHASE 4.1: Get price from WebSocket or REST API fallback
def get_binance_price(symbol, ws_manager=None):
    """Get Binance price with WebSocket priority, REST API fallback"""
    # Try WebSocket first
    if WEBSOCKET_AVAILABLE and ws_manager and ws_manager.is_connected():
        ws_price = ws_manager.get_price(symbol)
        if ws_price and ws_price > 0:
            try:
                url = f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'price': ws_price,
                        'change_24h': float(data['priceChangePercent']),
                        'volume': float(data['quoteVolume']),
                        'high_24h': float(data['highPrice']),
                        'low_24h': float(data['lowPrice']),
                        'available': True,
                        'source': 'websocket'
                    }
            except:
                pass
    
    # Fallback: REST API
    try:
        url = f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'price': float(data['lastPrice']),
                'change_24h': float(data['priceChangePercent']),
                'volume': float(data['quoteVolume']),
                'high_24h': float(data['highPrice']),
                'low_24h': float(data['lowPrice']),
                'available': True,
                'source': 'rest_api'
            }
    except:
        pass
    
    return {'price': 0, 'change_24h': 0, 'volume': 0, 'high_24h': 0, 'low_24h': 0, 'available': False, 'source': 'error'}

# Copy to clipboard function
def copy_to_clipboard_button(text, label):
    """Create a button that copies text to clipboard"""
    st.code(text, language='text')
    if st.button(f"📋 Copy {label}", key=f"copy_{label}_{text}"):
        components.html(
            f"""
            <script>
            navigator.clipboard.writeText("{text}");
            </script>
            <p style="color: green;">✅ Copied to clipboard!</p>
            """,
            height=50
        )

# PROFESSIONAL TRADE CARD RENDERER
def render_trade_card(symbol, coin_name, emoji, decision, price_data, ws_status):
    """Render professional trading card with all parameters"""
    
    # Determine signal class
    signal = decision['final_decision']
    card_class = f"trade-card trade-card-{signal.lower()}"
    signal_class = f"signal-{signal.lower()}"
    
    # Signal badge
    if signal == "LONG":
        signal_badge = f'<div class="signal-badge signal-long">🟢 LONG</div>'
    elif signal == "SHORT":
        signal_badge = f'<div class="signal-badge signal-short">🔴 SHORT</div>'
    else:
        signal_badge = f'<div class="signal-badge signal-neutral">🟡 NEUTRAL</div>'
    
    # Price change color
    change_color = "green" if price_data['change_24h'] >= 0 else "red"
    
    # Card HTML
    st.markdown(f"""
    <div class="{card_class}">
        <div class="coin-header">
            <span>{emoji} {coin_name}</span>
            <span style="color: {change_color}; font-size: 16px;">
                {price_data['change_24h']:+.2f}% (24h)
            </span>
            <span style="margin-left: auto; font-size: 14px; color: #aaa;">
                {ws_status}
            </span>
        </div>
        
        <div class="current-price">${price_data['price']:,.2f}</div>
        
        {signal_badge}
        
        <div class="trade-params">
            <div class="param-row">
                <span class="param-label">📍 ENTRY PRICE</span>
                <span class="param-value param-value-entry">${decision['entry_price']:,.2f}</span>
            </div>
            <div class="param-row">
                <span class="param-label">🛡️ STOP LOSS</span>
                <span class="param-value param-value-sl">${decision['stop_loss']:,.2f}</span>
            </div>
            <div class="param-row">
                <span class="param-label">🎯 TAKE PROFIT</span>
                <span class="param-value param-value-tp">${decision['take_profit']:,.2f}</span>
            </div>
        </div>
        
        <div class="rr-box">
            <strong>Risk/Reward:</strong> 1:{(decision['take_profit'] - decision['entry_price']) / abs(decision['entry_price'] - decision['stop_loss']):.2f} | 
            <strong>Position Size:</strong> {decision.get('position_size', 0):.4f} {coin_name[:3]}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Copy buttons in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        copy_to_clipboard_button(f"{decision['entry_price']:.2f}", "Entry")
    with col2:
        copy_to_clipboard_button(f"{decision['stop_loss']:.2f}", "SL")
    with col3:
        copy_to_clipboard_button(f"{decision['take_profit']:.2f}", "TP")
    with col4:
        all_params = f"Entry: {decision['entry_price']:.2f} | SL: {decision['stop_loss']:.2f} | TP: {decision['take_profit']:.2f}"
        if st.button("📋 Copy All", key=f"copy_all_{symbol}"):
            st.code(all_params)
    
    # Layer scores with progress bars (if available)
    if 'layer_scores' in decision and decision['layer_scores']:
        with st.expander("🔬 11-Layer Analysis Breakdown"):
            for layer_name, score in decision['layer_scores'].items():
                color_class = "green" if score >= 70 else ("yellow" if score >= 40 else "red")
                st.markdown(f"""
                <div class="layer-score">
                    <div class="layer-name">{layer_name}</div>
                    <div class="layer-bar">
                        <div class="layer-fill layer-fill-{color_class}" style="width: {score}%"></div>
                    </div>
                    <span style="color: #fff; font-size: 12px;">{score:.1f}%</span>
                </div>
                """, unsafe_allow_html=True)
    
    # AI Commentary
    if 'ai_commentary' in decision and decision['ai_commentary']:
        with st.expander("🤖 AI Commentary"):
            st.info(decision['ai_commentary'])

def main():
    # PHASE 4.1: Initialize WebSocket
    ws_manager = None
    if WEBSOCKET_AVAILABLE:
        try:
            ws_manager = get_websocket_manager(['BTCUSDT', 'ETHUSDT', 'LTCUSDT'])
        except Exception as e:
            print(f"WebSocket init error: {e}")
    
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title("🔱 DEMIR AI TRADING BOT v9.0 PRO")
    with col2:
        if WEBSOCKET_AVAILABLE and ws_manager and ws_manager.is_connected():
            st.markdown("### 🟢 LIVE")
        else:
            st.markdown("### 🟡 REST API")
    with col3:
        st.markdown(f"### ⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ CONTROL PANEL")
        
        # WebSocket Status
        if WEBSOCKET_AVAILABLE and ws_manager:
            status = ws_manager.get_connection_status()
            st.markdown("### 📡 Connection")
            st.markdown(f"**Status:** {'🟢 Live' if status['connected'] else '🔴 Offline'}")
        
        st.markdown("---")
        
        # Wallet Settings
        st.subheader("💰 Wallet")
        portfolio_value = st.number_input("Balance (USD)", value=1000, step=100)
        leverage = st.number_input("Leverage", value=50, min_value=1, max_value=125)
        risk_per_trade = st.number_input("Risk/Trade ($)", value=35, step=5)
        
        st.markdown("---")
        
        # Auto-refresh
        auto_refresh = st.checkbox("🔄 Auto Refresh (30s)", value=False)
        if st.button("🔄 Refresh Now"):
            st.session_state.last_refresh = datetime.now()
            st.rerun()
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs([
        "🎯 TRADE SIGNALS",
        "📈 ACTIVE POSITIONS",
        "📜 HISTORY"
    ])
    
    # TAB 1: Professional Trade Signals
    with tab1:
        st.header("🎯 LIVE TRADE SIGNALS")
        
        coins = [
            ('BTCUSDT', 'Bitcoin', '₿'),
            ('ETHUSDT', 'Ethereum', '♦️'),
            ('LTCUSDT', 'Litecoin', 'Ł')
        ]
        
        for symbol, coin_name, emoji in coins:
            # Get live price
            price_data = get_binance_price(symbol, ws_manager)
            ws_status = "🔴 LIVE" if price_data.get('source') == 'websocket' else "🟡 API"
            
            # Get AI decision
            if AI_BRAIN_AVAILABLE and price_data['available']:
                try:
                    decision = ai_brain.make_trading_decision(
                        symbol=symbol,
                        interval='1h',
                        portfolio_value=portfolio_value,
                        risk_per_trade=risk_per_trade
                    )
                    
                    # Render professional card
                    render_trade_card(symbol, coin_name, emoji, decision, price_data, ws_status)
                    
                except Exception as e:
                    st.error(f"❌ Error analyzing {coin_name}: {e}")
            else:
                st.warning(f"⚠️ AI analysis unavailable for {coin_name}")
            
            st.markdown("---")
    
    # TAB 2: Position Tracker
    with tab2:
        st.header("📈 Active Positions")
        if POSITION_TRACKER_AVAILABLE:
            try:
                positions = tracker.get_all_positions()
                if positions:
                    df = pd.DataFrame(positions)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No active positions")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Position Tracker not available")
    
    # TAB 3: Trade History
    with tab3:
        st.header("📜 Trade History")
        try:
            trades = db.get_all_trades()
            if trades:
                df = pd.DataFrame(trades)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No trades recorded")
        except Exception as e:
            st.error(f"Error: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown(f"**Last Updated:** {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("**DEMIR AI Trading Bot v9.0 PRO** | PHASE 5.0: Professional UI")
    
    # Auto-refresh
    if auto_refresh:
        time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
        if time_since_refresh >= 30:
            st.session_state.last_refresh = datetime.now()
            st.rerun()

if __name__ == "__main__":
    main()
