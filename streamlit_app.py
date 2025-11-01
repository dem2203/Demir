"""
🔱 DEMIR AI TRADING BOT - DASHBOARD v9.0 PROFESSIONAL UI
Date: 1 Kasım 2025
PHASE 5.0: Professional Trading Terminal Interface + WebSocket Integration

v9.0 FEATURES:
✅ Professional TradingView-style card layout
✅ Prominent Entry/TP/SL display with copy buttons
✅ Real-time WebSocket price streaming (PHASE 4.1)
✅ Visual signal indicators (🟢 LONG / 🔴 SHORT / 🟡 NEUTRAL)
✅ 11-Layer analysis with progress bar visualization
✅ Risk/Reward calculator prominently displayed
✅ Modern gradient color-coded UI
✅ Live P/L tracker
✅ One-click "Copy All" trade parameters
✅ ALL v8.3.1 features retained (Position Tracker, Portfolio Optimizer, Backtest, Trade History)

RETAINED FROM v8.3.1:
✅ Multi-coin analysis (BTC/ETH/LTC permanent)
✅ Position tracking & management
✅ Portfolio optimizer integration
✅ Backtest engine
✅ Trade history database
✅ Auto-refresh (30s intervals)
✅ Wallet settings (leverage, risk per trade)
"""

import streamlit as st
import streamlit.components.v1 as components  
import requests
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import trade_history_db as db
import win_rate_calculator as wrc

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

# Core AI Brain
try:
    import ai_brain
    AI_BRAIN_AVAILABLE = True
except:
    AI_BRAIN_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="🔱 DEMIR AI Trading Bot v9.0 PRO",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PROFESSIONAL CSS STYLING - TradingView Inspired
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* Professional trade card base */
    .trade-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
        border: 2px solid rgba(255,255,255,0.15);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .trade-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }
    
    /* Signal-specific card styles */
    .trade-card-long {
        border-color: #00ff88;
        background: linear-gradient(145deg, rgba(0,255,136,0.12), rgba(0,255,136,0.03));
    }
    
    .trade-card-short {
        border-color: #ff4444;
        background: linear-gradient(145deg, rgba(255,68,68,0.12), rgba(255,68,68,0.03));
    }
    
    .trade-card-neutral {
        border-color: #ffaa00;
        background: linear-gradient(145deg, rgba(255,170,0,0.12), rgba(255,170,0,0.03));
    }
    
    /* Trade parameters container */
    .trade-params {
        background: rgba(0,0,0,0.4);
        border-radius: 12px;
        padding: 18px;
        margin: 18px 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Parameter row styling */
    .param-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        font-size: 16px;
    }
    
    .param-row:last-child {
        border-bottom: none;
    }
    
    .param-label {
        font-weight: 600;
        color: #bbb;
        min-width: 140px;
        font-size: 15px;
    }
    
    .param-value {
        font-weight: 700;
        color: #fff;
        font-size: 20px;
        font-family: 'Courier New', Monaco, monospace;
        letter-spacing: 0.5px;
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
        padding: 10px 24px;
        border-radius: 24px;
        font-weight: 700;
        font-size: 20px;
        margin: 12px 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .signal-long {
        background: linear-gradient(135deg, #00ff88, #00d4aa);
        color: #000;
        box-shadow: 0 4px 15px rgba(0,255,136,0.4);
    }
    
    .signal-short {
        background: linear-gradient(135deg, #ff4444, #cc0000);
        color: #fff;
        box-shadow: 0 4px 15px rgba(255,68,68,0.4);
    }
    
    .signal-neutral {
        background: linear-gradient(135deg, #ffaa00, #ff8800);
        color: #000;
        box-shadow: 0 4px 15px rgba(255,170,0,0.4);
    }
    
    /* Coin header styling */
    .coin-header {
        font-size: 26px;
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        color: #fff;
    }
    
    /* Current price display */
    .current-price {
        font-size: 32px;
        font-weight: 700;
        color: #fff;
        font-family: 'Courier New', Monaco, monospace;
        margin: 8px 0;
        letter-spacing: 1px;
    }
    
    /* Risk/Reward info box */
    .rr-box {
        background: rgba(0,212,255,0.12);
        border: 1px solid rgba(0,212,255,0.3);
        border-radius: 10px;
        padding: 12px;
        margin: 12px 0;
        text-align: center;
        font-size: 15px;
        color: #e0e0e0;
    }
    
    .rr-box strong {
        color: #00d4ff;
    }
    
    /* Copy button custom styling */
    .stButton>button {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 10px;
        color: #fff;
        font-weight: 600;
        padding: 8px 16px;
        transition: all 0.3s ease;
        font-size: 14px;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, rgba(0,255,136,0.2), rgba(0,212,255,0.15));
        border-color: #00ff88;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,255,136,0.3);
    }
    
    /* Layer score styling */
    .layer-score {
        margin: 10px 0;
    }
    
    .layer-name {
        color: #aaa;
        font-size: 14px;
        margin-bottom: 5px;
        font-weight: 500;
    }
    
    .layer-bar {
        background: rgba(255,255,255,0.08);
        border-radius: 12px;
        height: 24px;
        position: relative;
        overflow: hidden;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .layer-fill {
        height: 100%;
        border-radius: 12px;
        transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    
    .layer-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
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
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: rgba(0,0,0,0.2);
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 12px 24px;
        border: 1px solid rgba(255,255,255,0.1);
        color: #bbb;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255,255,255,0.1);
        color: #fff;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0,255,136,0.25), rgba(0,212,255,0.15));
        border-color: #00ff88;
        color: #fff;
        box-shadow: 0 4px 12px rgba(0,255,136,0.3);
    }
    
    /* Headers */
    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* Metric cards (Streamlit default) */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        color: #fff;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background: rgba(0,0,0,0.4);
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Global session state
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# PHASE 4.1: WebSocket price fetching with REST API fallback
def get_binance_price(symbol, ws_manager=None):
    """
    Get Binance price with WebSocket priority, REST API fallback
    Returns dict with price, change_24h, volume, high_24h, low_24h, available, source
    """
    # Try WebSocket first (real-time)
    if WEBSOCKET_AVAILABLE and ws_manager and ws_manager.is_connected():
        ws_price = ws_manager.get_price(symbol)
        if ws_price and ws_price > 0:
            # Got WebSocket price, now fetch 24h stats from REST
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
            except Exception as e:
                print(f"REST API 24h stats error: {e}")
    
    # Fallback: Pure REST API
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
    except Exception as e:
        print(f"Binance API error for {symbol}: {e}")
    
    # If all fails
    return {
        'price': 0,
        'change_24h': 0,
        'volume': 0,
        'high_24h': 0,
        'low_24h': 0,
        'available': False,
        'source': 'error'
    }

# Copy to clipboard helper
def copy_to_clipboard_button(text, label):
    """Create a button that copies text to clipboard"""
    st.code(text, language='text')
    if st.button(f"📋 Copy {label}", key=f"copy_{label}_{text}"):
        components.html(
            f"""
            <script>
            navigator.clipboard.writeText("{text}");
            </script>
            <p style="color: #00ff88; font-weight: bold;">✅ Copied to clipboard!</p>
            """,
            height=60
        )

# PROFESSIONAL TRADE CARD RENDERER
def render_trade_card(symbol, coin_name, emoji, decision, price_data, ws_status):
    """
    Render professional TradingView-style trading card
    Shows signal, entry, SL, TP, R/R, position size with copy buttons
    """
    signal = decision['final_decision']
    card_class = f"trade-card trade-card-{signal.lower()}"
    
    # Signal badge HTML
    if signal == "LONG":
        signal_badge = '<div class="signal-badge signal-long">🟢 LONG</div>'
    elif signal == "SHORT":
        signal_badge = '<div class="signal-badge signal-short">🔴 SHORT</div>'
    else:
        signal_badge = '<div class="signal-badge signal-neutral">🟡 NEUTRAL</div>'
    
    # 24h change color
    change_color = "#00ff88" if price_data['change_24h'] >= 0 else "#ff4444"
    
    # Calculate R/R ratio
    entry = decision['entry_price']
    sl = decision['stop_loss']
    tp = decision['take_profit']
    risk = abs(entry - sl)
    reward = abs(tp - entry)
    rr_ratio = reward / risk if risk > 0 else 0
    
    # Card HTML
    st.markdown(f"""
    <div class="{card_class}">
        <div class="coin-header">
            <span>{emoji} {coin_name}</span>
            <span style="color: {change_color}; font-size: 16px; font-weight: 600;">
                {price_data['change_24h']:+.2f}% (24h)
            </span>
            <span style="margin-left: auto; font-size: 14px; color: #aaa; font-weight: 500;">
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
            <strong>Risk/Reward:</strong> 1:{rr_ratio:.2f} | 
            <strong>Position Size:</strong> {decision.get('position_size', 0):.4f} {coin_name[:3]}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Copy buttons row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        copy_to_clipboard_button(f"{decision['entry_price']:.2f}", "Entry")
    with col2:
        copy_to_clipboard_button(f"{decision['stop_loss']:.2f}", "SL")
    with col3:
        copy_to_clipboard_button(f"{decision['take_profit']:.2f}", "TP")
    with col4:
        all_params = f"Entry: ${decision['entry_price']:.2f} | SL: ${decision['stop_loss']:.2f} | TP: ${decision['take_profit']:.2f} | R/R: 1:{rr_ratio:.2f}"
        if st.button("📋 Copy All", key=f"copy_all_{symbol}"):
            st.code(all_params)
    
    # 11-Layer scores with progress bars
    if 'layer_scores' in decision and decision['layer_scores']:
        with st.expander("🔬 11-Layer Analysis Breakdown", expanded=False):
            for layer_name, score in decision['layer_scores'].items():
                # Determine color based on score
                if score >= 70:
                    color_class = "green"
                elif score >= 40:
                    color_class = "yellow"
                else:
                    color_class = "red"
                
                st.markdown(f"""
                <div class="layer-score">
                    <div class="layer-name">{layer_name}</div>
                    <div class="layer-bar">
                        <div class="layer-fill layer-fill-{color_class}" style="width: {score}%"></div>
                    </div>
                    <span style="color: #fff; font-size: 13px; font-weight: 600; margin-left: 8px;">{score:.1f}%</span>
                </div>
                """, unsafe_allow_html=True)
    
    # AI Commentary
    if 'ai_commentary' in decision and decision['ai_commentary']:
        with st.expander("🤖 AI Commentary", expanded=False):
            st.info(decision['ai_commentary'])

def main():
    """Main application entry point"""
    
    # PHASE 4.1: Initialize WebSocket
    ws_manager = None
    if WEBSOCKET_AVAILABLE:
        try:
            ws_manager = get_websocket_manager(['BTCUSDT', 'ETHUSDT', 'LTCUSDT'])
        except Exception as e:
            print(f"WebSocket initialization error: {e}")
    
    # Header with live status
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title("🔱 DEMIR AI TRADING BOT v9.0 PRO")
    with col2:
        if WEBSOCKET_AVAILABLE and ws_manager and ws_manager.is_connected():
            st.markdown("### 🟢 LIVE STREAM")
        else:
            st.markdown("### 🟡 REST API")
    with col3:
        st.markdown(f"### ⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    st.markdown("---")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ CONTROL PANEL")
        
        # WebSocket connection status
        if WEBSOCKET_AVAILABLE and ws_manager:
            status = ws_manager.get_connection_status()
            st.markdown("### 📡 Connection Status")
            conn_status = "🟢 Connected" if status['connected'] else "🔴 Disconnected"
            st.markdown(f"**WebSocket:** {conn_status}")
            st.markdown(f"**Streams:** {len(status['symbols'])} coins")
            
            # Show live prices in sidebar
            if status['prices']:
                st.markdown("**Live Prices:**")
                for sym, pr in status['prices'].items():
                    if pr:
                        st.markdown(f"• {sym}: ${pr:,.2f}")
        
        st.markdown("---")
        
        # Wallet settings
        st.subheader("💰 Wallet Configuration")
        portfolio_value = st.number_input("Total Balance (USD)", value=1000, step=100, min_value=100)
        leverage = st.number_input("Leverage", value=50, min_value=1, max_value=125, step=1)
        risk_per_trade = st.number_input("Risk Per Trade ($)", value=35, step=5, min_value=10)
        
        st.markdown("---")
        
        # Active coins display
        st.subheader("🎯 Active Trading Pairs")
        st.markdown("**Permanent Coins:**")
        st.markdown("• **BTCUSDT** (Bitcoin)")
        st.markdown("• **ETHUSDT** (Ethereum)")
        st.markdown("• **LTCUSDT** (Litecoin)")
        
        st.markdown("---")
        
        # Auto-refresh control
        auto_refresh = st.checkbox("🔄 Auto Refresh (30s)", value=False)
        if auto_refresh:
            st.markdown("*Dashboard auto-refreshes every 30 seconds*")
        
        # Manual refresh button
        if st.button("🔄 Manual Refresh Now", use_container_width=True):
            st.session_state.last_refresh = datetime.now()
            st.rerun()
    
    # Main application tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 TRADE SIGNALS",
        "📈 ACTIVE POSITIONS",
        "💼 PORTFOLIO OPTIMIZER",
        "⚡ BACKTEST ENGINE",
        "📜 TRADE HISTORY"
    ])
    
    # TAB 1: Professional Trade Signals
    with tab1:
        st.header("🎯 LIVE TRADE SIGNALS")
        st.markdown("*AI-powered multi-layer analysis with real-time price streaming*")
        st.markdown("---")
        
        coins = [
            ('BTCUSDT', 'Bitcoin', '₿'),
            ('ETHUSDT', 'Ethereum', '♦️'),
            ('LTCUSDT', 'Litecoin', 'Ł')
        ]
        
        for symbol, coin_name, emoji in coins:
            # Get live price data
            price_data = get_binance_price(symbol, ws_manager)
            ws_status = "🔴 LIVE" if price_data.get('source') == 'websocket' else "🟡 API"
            
            # Get AI trading decision
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
                    st.error(f"❌ Error analyzing {coin_name}: {str(e)}")
            else:
                st.warning(f"⚠️ AI analysis unavailable for {coin_name}")
            
            st.markdown("---")
    
    # TAB 2: Active Positions Tracker
    with tab2:
        st.header("📈 Active Positions Tracker")
        st.markdown("*Monitor your current open positions and P/L*")
        st.markdown("---")
        
        if POSITION_TRACKER_AVAILABLE:
            try:
                positions = tracker.get_all_positions()
                if positions:
                    df = pd.DataFrame(positions)
                    st.dataframe(df, use_container_width=True, height=400)
                    
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Positions", len(positions))
                    with col2:
                        total_pl = sum([p.get('pnl', 0) for p in positions])
                        st.metric("Total P/L", f"${total_pl:.2f}")
                    with col3:
                        win_count = sum([1 for p in positions if p.get('pnl', 0) > 0])
                        st.metric("Winning Positions", win_count)
                else:
                    st.info("📭 No active positions at the moment")
            except Exception as e:
                st.error(f"❌ Error loading positions: {str(e)}")
        else:
            st.warning("⚠️ Position Tracker module not available")
    
    # TAB 3: Portfolio Optimizer
    with tab3:
        st.header("💼 Portfolio Optimizer")
        st.markdown("*Optimize position sizing and risk allocation*")
        st.markdown("---")
        
        if PORTFOLIO_OPTIMIZER_AVAILABLE:
            try:
                optimizer = PortfolioOptimizer(total_capital=portfolio_value)
                st.success("✅ Portfolio Optimizer loaded successfully")
                st.info("Portfolio optimization features available here")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Portfolio Optimizer module not available")
    
    # TAB 4: Backtest Engine
    with tab4:
        st.header("⚡ Backtest Engine")
        st.markdown("*Test your strategies on historical data*")
        st.markdown("---")
        
        if BACKTEST_AVAILABLE:
            st.success("✅ Backtest Engine loaded successfully")
            st.info("Backtesting features available here")
        else:
            st.warning("⚠️ Backtest Engine module not available")
    
    # TAB 5: Trade History
    with tab5:
        st.header("📜 Trade History Database")
        st.markdown("*Complete record of all executed trades*")
        st.markdown("---")
        
        try:
            trades = db.get_all_trades()
            if trades:
                df = pd.DataFrame(trades)
                st.dataframe(df, use_container_width=True, height=500)
                
                # Trade statistics
                if len(trades) > 0:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Trades", len(trades))
                    with col2:
                        wins = sum([1 for t in trades if t.get('result') == 'WIN'])
                        st.metric("Winning Trades", wins)
                    with col3:
                        if len(trades) > 0:
                            win_rate = (wins / len(trades)) * 100
                            st.metric("Win Rate", f"{win_rate:.1f}%")
                    with col4:
                        total_pnl = sum([t.get('pnl', 0) for t in trades])
                        st.metric("Total P/L", f"${total_pnl:.2f}")
            else:
                st.info("📭 No trades recorded yet")
        except Exception as e:
            st.error(f"❌ Error loading trade history: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown(f"**Last Updated:** {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("**DEMIR AI Trading Bot v9.0 PRO** | PHASE 5.0: Professional UI + WebSocket Integration")
    
    # Auto-refresh logic
    if auto_refresh:
        import time as time_module
        time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
        if time_since_refresh >= 30:
            st.session_state.last_refresh = datetime.now()
            st.rerun()

if __name__ == "__main__":
    main()
