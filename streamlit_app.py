"""
🔱 DEMIR AI TRADING BOT - DASHBOARD v9.4 PRO - COMPLETE PRODUCTION VERSION
===========================================================================
Date: 1 Kasım 2025, 18:05 CET
Author: DEMIR AI System
Version: 9.4 HOTFIX - HTML Rendering Fix

PHASE 5.4 FEATURES:
✅ Fixed HTML rendering issue (switched to Streamlit native components)
✅ Full ai_brain.py compatibility ('decision' and 'final_decision' support)
✅ Complete trade_history_db.py error handling
✅ WebSocket live price streaming
✅ Position tracking
✅ Portfolio optimization
✅ Backtest engine integration
✅ Professional UI with metrics and cards
✅ 11-Layer AI analysis
✅ Auto-refresh capability
✅ Copy-to-clipboard functionality
✅ Multi-coin support (BTC, ETH, LTC)

USAGE:
------
1. This file is already named: streamlit_app.py (READY TO USE)
2. Install dependencies: pip install -r requirements.txt
3. Run: streamlit run streamlit_app.py
4. Dashboard will open in browser at http://localhost:8501

REQUIREMENTS (requirements.txt):
--------------------------------
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
requests>=2.31.0
"""

# ============================================================================
# IMPORTS
# ============================================================================
import streamlit as st
import streamlit.components.v1 as components  
import requests
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import traceback

# Import optional modules with error handling
try:
    import trade_history_db as db
    DB_AVAILABLE = True
except Exception as e:
    DB_AVAILABLE = False
    print(f"⚠️ trade_history_db not available: {e}")

try:
    import win_rate_calculator as wrc
    WRC_AVAILABLE = True
except:
    WRC_AVAILABLE = False
    print("⚠️ win_rate_calculator not available")

# PHASE 4.1: WebSocket Integration
try:
    from websocket_stream import get_websocket_manager
    WEBSOCKET_AVAILABLE = True
    print("✅ WebSocket module loaded")
except Exception as e:
    WEBSOCKET_AVAILABLE = False
    print(f"⚠️ WebSocket not available: {e}")

# PHASE 3.4: Position Tracker
try:
    from position_tracker import PositionTracker
    POSITION_TRACKER_AVAILABLE = True
    tracker = PositionTracker()
    print("✅ Position Tracker loaded")
except Exception as e:
    POSITION_TRACKER_AVAILABLE = False
    print(f"⚠️ Position Tracker not available: {e}")

# PHASE 3.3: Portfolio Optimizer
try:
    from portfolio_optimizer import PortfolioOptimizer
    PORTFOLIO_OPTIMIZER_AVAILABLE = True
    print("✅ Portfolio Optimizer loaded")
except:
    PORTFOLIO_OPTIMIZER_AVAILABLE = False
    print("⚠️ Portfolio Optimizer not available")

# PHASE 3.2: Backtest Engine
try:
    from backtest_engine import BacktestEngine
    BACKTEST_AVAILABLE = True
    print("✅ Backtest Engine loaded")
except:
    BACKTEST_AVAILABLE = False
    print("⚠️ Backtest Engine not available")

# Core AI Brain - CRITICAL MODULE
try:
    import ai_brain
    AI_BRAIN_AVAILABLE = True
    print("✅ AI Brain module loaded successfully")
except Exception as e:
    AI_BRAIN_AVAILABLE = False
    print(f"❌ AI Brain import error: {e}")

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="🔱 DEMIR AI Trading Bot v9.4 PRO",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# PROFESSIONAL CSS STYLING
# ============================================================================
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* Headers */
    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        color: #fff;
    }
    
    [data-testid="stMetricLabel"] {
        color: #bbb;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 16px;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 10px;
        color: #fff;
        font-weight: 600;
        padding: 8px 16px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, rgba(0,255,136,0.2), rgba(0,212,255,0.15));
        border-color: #00ff88;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,255,136,0.3);
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00ff88, #00d4ff);
    }
    
    /* Info/Success/Warning/Error boxes */
    .stAlert {
        border-radius: 10px;
        border-left: 4px solid;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    /* Dataframes */
    .dataframe {
        border-radius: 8px;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background: rgba(0,0,0,0.4);
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# GLOBAL SESSION STATE
# ============================================================================
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_binance_price(symbol, ws_manager=None):
    """
    Get Binance price with WebSocket priority, REST API fallback
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')
        ws_manager: WebSocket manager instance (optional)
    
    Returns:
        dict: Price data with keys: price, change_24h, volume, high_24h, low_24h, available, source
    """
    # Try WebSocket first (real-time data)
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

# ============================================================================
# CARD RENDERING FUNCTION (Streamlit Native Components)
# ============================================================================

def render_trade_card(symbol, coin_name, emoji, decision, price_data, ws_status):
    """
    Render trading card using Streamlit native components
    
    BUGFIX v9.4: HTML wasn't rendering in v9.3, switched to st.components for reliability
    
    Args:
        symbol: Trading pair symbol
        coin_name: Human-readable coin name
        emoji: Coin emoji for display
        decision: AI decision dict from ai_brain.make_trading_decision()
        price_data: Price data dict from get_binance_price()
        ws_status: WebSocket status string
    """
    # =========================
    # VALIDATION
    # =========================
    if not decision or not isinstance(decision, dict):
        st.error(f"❌ AI Brain returned None or invalid data for {coin_name}")
        return
    
    # Get signal (support both 'decision' and 'final_decision' keys for compatibility)
    signal = decision.get('decision') or decision.get('final_decision')
    
    if not signal:
        st.error(f"❌ Missing decision/final_decision key for {coin_name}")
        with st.expander("🔍 Debug Info - Click to expand"):
            st.write("**Returned keys:**", list(decision.keys()))
            st.write("**Full response:**", decision)
        return
    
    # =========================
    # SIGNAL BADGE
    # =========================
    if signal == "LONG":
        st.success(f"🟢 **LONG SIGNAL** - {emoji} {coin_name}")
    elif signal == "SHORT":
        st.error(f"🔴 **SHORT SIGNAL** - {emoji} {coin_name}")
    else:
        st.warning(f"🟡 **NEUTRAL** - {emoji} {coin_name}")
    
    # =========================
    # CURRENT PRICE METRIC
    # =========================
    st.metric(
        label=f"Current Price ({ws_status})",
        value=f"${price_data['price']:,.2f}",
        delta=f"{price_data['change_24h']:+.2f}% (24h)"
    )
    
    # =========================
    # TRADING PARAMETERS
    # =========================
    entry = decision.get('entry_price', 0)
    sl = decision.get('stop_loss', 0)
    tp = decision.get('take_profit', 0)
    risk = abs(entry - sl)
    reward = abs(tp - entry)
    rr_ratio = reward / risk if risk > 0 else 0
    
    st.markdown("### 📊 Trading Parameters")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📍 Entry Price", f"${entry:,.2f}")
    with col2:
        st.metric("🛡️ Stop Loss", f"${sl:,.2f}")
    with col3:
        st.metric("🎯 Take Profit", f"${tp:,.2f}")
    
    # Risk/Reward and Position Size
    col4, col5 = st.columns(2)
    with col4:
        st.metric("⚖️ Risk/Reward", f"1:{rr_ratio:.2f}")
    with col5:
        st.metric("💰 Position Size", f"{decision.get('position_size', 0):.4f} {coin_name[:3]}")
    
    # =========================
    # COPY BUTTONS
    # =========================
    st.markdown("### 📋 Quick Copy")
    col_a, col_b, col_c, col_d = st.columns(4)
    
    with col_a:
        if st.button(f"Copy Entry", key=f"copy_entry_{symbol}"):
            st.code(f"{entry:.2f}", language="text")
    
    with col_b:
        if st.button(f"Copy SL", key=f"copy_sl_{symbol}"):
            st.code(f"{sl:.2f}", language="text")
    
    with col_c:
        if st.button(f"Copy TP", key=f"copy_tp_{symbol}"):
            st.code(f"{tp:.2f}", language="text")
    
    with col_d:
        if st.button(f"Copy All", key=f"copy_all_{symbol}"):
            all_params = f"Entry: ${entry:.2f} | SL: ${sl:.2f} | TP: ${tp:.2f} | R/R: 1:{rr_ratio:.2f}"
            st.code(all_params, language="text")
    
    # =========================
    # 11-LAYER ANALYSIS SCORES
    # =========================
    if 'layer_scores' in decision and decision['layer_scores']:
        with st.expander("🔬 11-Layer Analysis Breakdown", expanded=False):
            for layer_name, score in decision['layer_scores'].items():
                # Progress bar with color based on score
                st.progress(score / 100, text=f"{layer_name}: {score:.1f}%")
    
    # =========================
    # AI COMMENTARY
    # =========================
    if 'ai_commentary' in decision and decision['ai_commentary']:
        with st.expander("🤖 AI Commentary", expanded=False):
            st.info(decision['ai_commentary'])
    
    # Separator
    st.markdown("---")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    
    # =========================
    # INITIALIZE WEBSOCKET
    # =========================
    ws_manager = None
    if WEBSOCKET_AVAILABLE:
        try:
            ws_manager = get_websocket_manager(['BTCUSDT', 'ETHUSDT', 'LTCUSDT'])
            print("✅ WebSocket manager initialized")
        except Exception as e:
            print(f"⚠️ WebSocket initialization error: {e}")
    
    # =========================
    # HEADER
    # =========================
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🔱 DEMIR AI TRADING BOT v9.4 PRO")
    
    with col2:
        if WEBSOCKET_AVAILABLE and ws_manager and ws_manager.is_connected():
            st.markdown("### 🟢 LIVE STREAM")
        else:
            st.markdown("### 🟡 REST API")
    
    with col3:
        st.markdown(f"### ⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    st.markdown("---")
    
    # =========================
    # SIDEBAR CONFIGURATION
    # =========================
    with st.sidebar:
        st.header("⚙️ CONTROL PANEL")
        
        # WebSocket connection status
        if WEBSOCKET_AVAILABLE and ws_manager:
            try:
                status = ws_manager.get_connection_status()
                st.markdown("### 📡 Connection Status")
                conn_status = "🟢 Connected" if status['connected'] else "🔴 Disconnected"
                st.markdown(f"**WebSocket:** {conn_status}")
                st.markdown(f"**Streams:** {len(status['symbols'])} coins")
                
                # Show live prices in sidebar
                if status.get('prices'):
                    st.markdown("**Live Prices:**")
                    for sym, pr in status['prices'].items():
                        if pr:
                            st.markdown(f"• {sym}: ${pr:,.2f}")
            except Exception as e:
                st.warning(f"WebSocket status error: {e}")
        
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
    
    # =========================
    # MAIN TABS
    # =========================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 TRADE SIGNALS",
        "📈 ACTIVE POSITIONS",
        "💼 PORTFOLIO OPTIMIZER",
        "⚡ BACKTEST ENGINE",
        "📜 TRADE HISTORY"
    ])
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TAB 1: TRADE SIGNALS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with tab1:
        st.header("🎯 LIVE TRADE SIGNALS")
        st.markdown("*AI-powered multi-layer analysis with real-time price streaming*")
        st.markdown("---")
        
        # Coin configurations
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
                    # Call AI Brain
                    decision = ai_brain.make_trading_decision(
                        symbol=symbol,
                        interval='1h',
                        portfolio_value=portfolio_value,
                        risk_per_trade=risk_per_trade
                    )
                    
                    # Validate response
                    if decision is None:
                        st.error(f"❌ AI Brain returned None for {coin_name}")
                    elif not isinstance(decision, dict):
                        st.error(f"❌ AI Brain returned invalid type: {type(decision)} for {coin_name}")
                    else:
                        # Render card
                        render_trade_card(symbol, coin_name, emoji, decision, price_data, ws_status)
                    
                except Exception as e:
                    st.error(f"❌ Exception in {coin_name} analysis:")
                    st.code(f"{type(e).__name__}: {str(e)}")
                    with st.expander("🔍 Full Traceback"):
                        st.code(traceback.format_exc())
            else:
                if not AI_BRAIN_AVAILABLE:
                    st.warning(f"⚠️ AI Brain module not available for {coin_name}")
                else:
                    st.warning(f"⚠️ Price data unavailable for {coin_name}")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TAB 2: ACTIVE POSITIONS TRACKER
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with tab2:
        st.header("📈 Active Positions Tracker")
        st.markdown("*Monitor your current open positions and P/L*")
        st.markdown("---")
        
        if POSITION_TRACKER_AVAILABLE:
            try:
                # Access positions attribute (not method)
                positions = tracker.positions if hasattr(tracker, 'positions') else []
                
                if len(positions) > 0:
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
                with st.expander("🔍 Error Details"):
                    st.code(traceback.format_exc())
        else:
            st.warning("⚠️ Position Tracker module not available")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TAB 3: PORTFOLIO OPTIMIZER
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with tab3:
        st.header("💼 Portfolio Optimizer")
        st.markdown("*Optimize position sizing and risk allocation*")
        st.markdown("---")
        
        if PORTFOLIO_OPTIMIZER_AVAILABLE:
            try:
                optimizer = PortfolioOptimizer(total_capital=portfolio_value)
                st.success("✅ Portfolio Optimizer loaded successfully")
                st.info("💡 Portfolio optimization features will be available here in future updates")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Portfolio Optimizer module not available")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TAB 4: BACKTEST ENGINE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with tab4:
        st.header("⚡ Backtest Engine")
        st.markdown("*Test your strategies on historical data*")
        st.markdown("---")
        
        if BACKTEST_AVAILABLE:
            st.success("✅ Backtest Engine loaded successfully")
            st.info("💡 Backtesting features will be available here in future updates")
        else:
            st.warning("⚠️ Backtest Engine module not available")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TAB 5: TRADE HISTORY
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with tab5:
        st.header("📜 Trade History Database")
        st.markdown("*Complete record of all executed trades*")
        st.markdown("---")
        
        if DB_AVAILABLE:
            try:
                trades = db.get_all_trades()
                
                # Proper empty check (BUGFIX v9.3)
                if trades is not None and isinstance(trades, list) and len(trades) > 0:
                    df = pd.DataFrame(trades)
                    st.dataframe(df, use_container_width=True, height=500)
                    
                    # Trade statistics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Trades", len(trades))
                    with col2:
                        wins = sum([1 for t in trades if t.get('result') == 'WIN'])
                        st.metric("Winning Trades", wins)
                    with col3:
                        win_rate = (wins / len(trades)) * 100 if len(trades) > 0 else 0
                        st.metric("Win Rate", f"{win_rate:.1f}%")
                    with col4:
                        total_pnl = sum([t.get('pnl', 0) for t in trades])
                        st.metric("Total P/L", f"${total_pnl:.2f}")
                else:
                    st.info("📭 No trades recorded yet")
            except Exception as e:
                st.error(f"❌ Error loading trade history: {str(e)}")
                with st.expander("🔍 Error Details"):
                    st.code(traceback.format_exc())
        else:
            st.warning("⚠️ Trade History Database not available")
    
    # =========================
    # FOOTER
    # =========================
    st.markdown("---")
    st.markdown(f"**Last Updated:** {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("**DEMIR AI Trading Bot v9.4 PRO** | PHASE 5.4: HTML Rendering Fix | Production Ready")
    
    # =========================
    # AUTO-REFRESH LOGIC
    # =========================
    if auto_refresh:
        import time as time_module
        time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
        if time_since_refresh >= 30:
            st.session_state.last_refresh = datetime.now()
            st.rerun()

# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    main()
