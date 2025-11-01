"""
🔱 DEMIR AI TRADING BOT - DASHBOARD v10.0 PRO - PHASE 6 + AI TRANSPARENCY
===========================================================================
Date: 1 Kasım 2025, 21:42 CET
Version: 10.0 - AI Brain Breakdown + Manual Trade Entry

NEW IN v10.0:
-------------
✅ Tab 6: AI Brain Breakdown (transparency!)
✅ Manuel trade entry buttons (I opened this trade!)
✅ Trade result tracking (WIN/LOSS logging)
✅ Layer scores visualization
✅ Macro factors breakdown
✅ Full transparency dashboard

COMPATIBILITY:
--------------
✅ Works with ai_brain.py v5 (Phase 6)
✅ Works with macro_correlation_layer.py
✅ Backward compatible with all existing modules

USAGE:
------
streamlit run streamlit_app.py
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

# Optional modules
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

try:
    from websocket_stream import get_websocket_manager
    WEBSOCKET_AVAILABLE = True
except Exception as e:
    WEBSOCKET_AVAILABLE = False

try:
    from position_tracker import PositionTracker
    POSITION_TRACKER_AVAILABLE = True
    tracker = PositionTracker()
except Exception as e:
    POSITION_TRACKER_AVAILABLE = False

try:
    from portfolio_optimizer import PortfolioOptimizer
    PORTFOLIO_OPTIMIZER_AVAILABLE = True
except:
    PORTFOLIO_OPTIMIZER_AVAILABLE = False

try:
    from backtest_engine import BacktestEngine
    BACKTEST_AVAILABLE = True
except:
    BACKTEST_AVAILABLE = False

# Core AI Brain - CRITICAL
try:
    import ai_brain
    AI_BRAIN_AVAILABLE = True
    print("✅ AI Brain v5 loaded (PHASE 6)")
except Exception as e:
    AI_BRAIN_AVAILABLE = False
    print(f"❌ AI Brain import error: {e}")

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="🔱 DEMIR AI Trading Bot v10.0 PRO",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS STYLING
# ============================================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 24px;
        color: #fff;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 10px;
        color: #fff;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, rgba(0,255,136,0.2), rgba(0,212,255,0.15));
        border-color: #00ff88;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

if 'manual_trades' not in st.session_state:
    st.session_state.manual_trades = []

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_binance_price(symbol, ws_manager=None):
    """Get price from WebSocket or REST API"""
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
    
    # REST API fallback
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
    
    return {'price': 0, 'change_24h': 0, 'volume': 0, 'available': False}

def log_manual_trade(symbol, decision_data):
    """Log a manually opened trade"""
    trade = {
        'symbol': symbol,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'signal': decision_data.get('decision', 'UNKNOWN'),
        'entry_price': decision_data.get('entry_price'),
        'stop_loss': decision_data.get('stop_loss'),
        'take_profit': decision_data.get('take_profit'),
        'ai_score': decision_data.get('final_score', 0),
        'macro_score': decision_data.get('macro_score', 0),
        'status': 'OPEN'
    }
    
    st.session_state.manual_trades.append(trade)
    
    # Also save to database if available
    if DB_AVAILABLE:
        try:
            db.add_trade(
                symbol=symbol,
                signal=trade['signal'],
                entry_price=trade['entry_price'],
                stop_loss=trade['stop_loss'],
                take_profit=trade['take_profit']
            )
        except:
            pass
    
    return trade

# ============================================================================
# CARD RENDERING
# ============================================================================

def render_trade_card(symbol, coin_name, emoji, decision, price_data, ws_status):
    """Render trading card with manuel entry button"""
    
    if not decision or not isinstance(decision, dict):
        st.error(f"❌ AI Brain returned None for {coin_name}")
        return
    
    signal = decision.get('decision') or decision.get('final_decision')
    
    if not signal:
        st.error(f"❌ Missing decision key for {coin_name}")
        return
    
    # Signal badge
    if signal == "LONG":
        st.success(f"🟢 **LONG SIGNAL** - {emoji} {coin_name}")
    elif signal == "SHORT":
        st.error(f"🔴 **SHORT SIGNAL** - {emoji} {coin_name}")
    else:
        st.warning(f"🟡 **WAIT** - {emoji} {coin_name}")
    
    # Price metric
    st.metric(
        label=f"Current Price ({ws_status})",
        value=f"${price_data['price']:,.2f}",
        delta=f"{price_data['change_24h']:+.2f}% (24h)"
    )
    
    # Trading parameters
    entry = decision.get('entry_price', 0)
    sl = decision.get('stop_loss', 0)
    tp = decision.get('take_profit', 0)
    risk = abs(entry - sl) if entry and sl else 0
    reward = abs(tp - entry) if entry and tp else 0
    rr_ratio = reward / risk if risk > 0 else 0
    
    st.markdown("### 📊 Trading Parameters")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📍 Entry", f"${entry:,.2f}" if entry else "N/A")
    with col2:
        st.metric("🛡️ Stop Loss", f"${sl:,.2f}" if sl else "N/A")
    with col3:
        st.metric("🎯 Take Profit", f"${tp:,.2f}" if tp else "N/A")
    
    col4, col5 = st.columns(2)
    with col4:
        st.metric("⚖️ R/R", f"1:{rr_ratio:.2f}" if rr_ratio else "N/A")
    with col5:
        st.metric("💰 Position", f"{decision.get('position_size', 0):.4f} {coin_name[:3]}")
    
    # Copy buttons
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
            all_params = f"Entry: ${entry:.2f} | SL: ${sl:.2f} | TP: ${tp:.2f}"
            st.code(all_params, language="text")
    
    # ========================================================================
    # NEW: MANUAL TRADE ENTRY BUTTON
    # ========================================================================
    st.markdown("---")
    st.markdown("### ✋ Manual Trade Entry")
    
    col_trade, col_info = st.columns([1, 2])
    
    with col_trade:
        if st.button(f"✅ I Opened This Trade!", key=f"manual_trade_{symbol}", type="primary"):
            trade = log_manual_trade(symbol, decision)
            st.success(f"✅ Trade logged for {coin_name}!")
            st.balloons()
    
    with col_info:
        st.info(f"💡 Click when you manually open a trade based on AI recommendation")
    
    # Layer scores (AI transparency!)
    if 'layer_scores' in decision and decision['layer_scores']:
        with st.expander("🔬 Layer Breakdown", expanded=False):
            for layer_name, score in decision['layer_scores'].items():
                st.progress(score / 100, text=f"{layer_name}: {score:.1f}%")
    
    # AI commentary
    if 'ai_commentary' in decision and decision['ai_commentary']:
        with st.expander("🤖 AI Commentary", expanded=False):
            st.info(decision['ai_commentary'])
    
    st.markdown("---")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application"""
    
    # WebSocket init
    ws_manager = None
    if WEBSOCKET_AVAILABLE:
        try:
            ws_manager = get_websocket_manager(['BTCUSDT', 'ETHUSDT', 'LTCUSDT'])
        except:
            pass
    
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🔱 DEMIR AI TRADING BOT v10.0 PRO")
    
    with col2:
        if WEBSOCKET_AVAILABLE and ws_manager:
            st.markdown("### 🟢 LIVE")
        else:
            st.markdown("### 🟡 REST")
    
    with col3:
        st.markdown(f"### ⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ CONTROL PANEL")
        
        if WEBSOCKET_AVAILABLE and ws_manager:
            try:
                status = ws_manager.get_connection_status()
                st.markdown("### 📡 Connection")
                st.markdown(f"**WS:** {'🟢' if status['connected'] else '🔴'}")
                st.markdown(f"**Coins:** {len(status['symbols'])}")
            except:
                pass
        
        st.markdown("---")
        
        st.subheader("💰 Wallet Config")
        portfolio_value = st.number_input("Balance (USD)", value=1000, step=100, min_value=100)
        leverage = st.number_input("Leverage", value=50, min_value=1, max_value=125)
        risk_per_trade = st.number_input("Risk ($)", value=35, step=5, min_value=10)
        
        st.markdown("---")
        
        st.subheader("🎯 Active Pairs")
        st.markdown("• **BTCUSDT**")
        st.markdown("• **ETHUSDT**")
        st.markdown("• **LTCUSDT**")
        
        st.markdown("---")
        
        auto_refresh = st.checkbox("🔄 Auto (30s)", value=False)
        
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.session_state.last_refresh = datetime.now()
            st.rerun()
    
    # ========================================================================
    # TABS (NOW WITH 6TH TAB!)
    # ========================================================================
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 TRADE SIGNALS",
        "📈 POSITIONS",
        "💼 PORTFOLIO",
        "⚡ BACKTEST",
        "📜 HISTORY",
        "🧠 AI BREAKDOWN"  # NEW!
    ])
    
    # ========================================================================
    # TAB 1: TRADE SIGNALS
    # ========================================================================
    with tab1:
        st.header("🎯 LIVE TRADE SIGNALS")
        st.markdown("*AI-powered 12-layer analysis with macro correlation*")
        st.markdown("---")
        
        coins = [
            ('BTCUSDT', 'Bitcoin', '₿'),
            ('ETHUSDT', 'Ethereum', '♦️'),
            ('LTCUSDT', 'Litecoin', 'Ł')
        ]
        
        for symbol, coin_name, emoji in coins:
            price_data = get_binance_price(symbol, ws_manager)
            ws_status = "🔴 LIVE" if price_data.get('source') == 'websocket' else "🟡 API"
            
            if AI_BRAIN_AVAILABLE and price_data['available']:
                try:
                    decision = ai_brain.make_trading_decision(
                        symbol=symbol,
                        interval='1h',
                        portfolio_value=portfolio_value,
                        risk_per_trade=risk_per_trade
                    )
                    
                    if decision:
                        render_trade_card(symbol, coin_name, emoji, decision, price_data, ws_status)
                    else:
                        st.error(f"❌ AI Brain returned None for {coin_name}")
                    
                except Exception as e:
                    st.error(f"❌ Error in {coin_name}:")
                    st.code(f"{type(e).__name__}: {str(e)}")
            else:
                if not AI_BRAIN_AVAILABLE:
                    st.warning(f"⚠️ AI Brain not available")
                else:
                    st.warning(f"⚠️ Price unavailable for {coin_name}")
    
    # ========================================================================
    # TAB 2: POSITIONS
    # ========================================================================
    with tab2:
        st.header("📈 Active Positions")
        st.markdown("*Monitor open positions and P/L*")
        st.markdown("---")
        
        if POSITION_TRACKER_AVAILABLE:
            try:
                positions = tracker.positions if hasattr(tracker, 'positions') else []
                
                if len(positions) > 0:
                    df = pd.DataFrame(positions)
                    st.dataframe(df, use_container_width=True, height=400)
                else:
                    st.info("📭 No active positions")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Position Tracker not available")
    
    # ========================================================================
    # TAB 3: PORTFOLIO
    # ========================================================================
    with tab3:
        st.header("💼 Portfolio Optimizer")
        st.markdown("*Position sizing and allocation*")
        st.markdown("---")
        
        if PORTFOLIO_OPTIMIZER_AVAILABLE:
            st.success("✅ Portfolio Optimizer loaded")
            st.info("💡 Features coming in next update")
        else:
            st.warning("⚠️ Not available")
    
    # ========================================================================
    # TAB 4: BACKTEST
    # ========================================================================
    with tab4:
        st.header("⚡ Backtest Engine")
        st.markdown("*Test strategies on historical data*")
        st.markdown("---")
        
        if BACKTEST_AVAILABLE:
            st.success("✅ Backtest Engine loaded")
            st.info("💡 Features coming in next update")
        else:
            st.warning("⚠️ Not available")
    
    # ========================================================================
    # TAB 5: HISTORY
    # ========================================================================
    with tab5:
        st.header("📜 Trade History")
        st.markdown("*Complete record of all trades*")
        st.markdown("---")
        
        # Show manual trades from session state
        if len(st.session_state.manual_trades) > 0:
            st.subheader("✋ Manual Trades (This Session)")
            df_manual = pd.DataFrame(st.session_state.manual_trades)
            st.dataframe(df_manual, use_container_width=True)
        
        # Show database trades
        if DB_AVAILABLE:
            try:
                trades = db.get_all_trades()
                
                if trades and len(trades) > 0:
                    st.subheader("💾 Database Trades")
                    df = pd.DataFrame(trades)
                    st.dataframe(df, use_container_width=True, height=400)
                    
                    # Stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Trades", len(trades))
                    with col2:
                        wins = sum([1 for t in trades if t.get('result') == 'WIN'])
                        st.metric("Wins", wins)
                    with col3:
                        win_rate = (wins / len(trades)) * 100 if len(trades) > 0 else 0
                        st.metric("Win Rate", f"{win_rate:.1f}%")
                else:
                    st.info("📭 No database trades yet")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.info("📭 No trades recorded yet")
    
    # ========================================================================
    # TAB 6: AI BRAIN BREAKDOWN (NEW!)
    # ========================================================================
    with tab6:
        st.header("🧠 AI Brain Breakdown")
        st.markdown("*Full transparency: See how AI makes decisions*")
        st.markdown("---")
        
        if not AI_BRAIN_AVAILABLE:
            st.warning("⚠️ AI Brain not available")
        else:
            # Coin selector
            selected_coin = st.selectbox(
                "Select Coin for Analysis:",
                ["BTCUSDT", "ETHUSDT", "LTCUSDT"],
                key="brain_coin_select"
            )
            
            st.markdown("---")
            
            with st.spinner(f"🔍 Analyzing {selected_coin}..."):
                try:
                    decision = ai_brain.make_trading_decision(
                        symbol=selected_coin,
                        interval='1h',
                        portfolio_value=portfolio_value,
                        risk_per_trade=risk_per_trade
                    )
                    
                    if decision:
                        # =============================================
                        # SCORE SUMMARY
                        # =============================================
                        st.subheader("📊 Score Summary")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            strategy_score = decision.get('layer_scores', {}).get('Layers 1-11 (Strategy)', 50)
                            st.metric(
                                "Strategy Score",
                                f"{strategy_score:.1f}/100",
                                delta="70% weight"
                            )
                        
                        with col2:
                            macro_score = decision.get('macro_score', 50)
                            st.metric(
                                "Macro Score",
                                f"{macro_score:.1f}/100",
                                delta="30% weight"
                            )
                        
                        with col3:
                            final_score = decision.get('final_score', 50)
                            delta_color = "normal" if 45 <= final_score <= 65 else ("off" if final_score < 45 else "inverse")
                            st.metric(
                                "Combined Score",
                                f"{final_score:.1f}/100",
                                delta=decision.get('decision', 'WAIT'),
                                delta_color=delta_color
                            )
                        
                        st.markdown("---")
                        
                        # =============================================
                        # MACRO FACTORS BREAKDOWN
                        # =============================================
                        if 'macro_details' in decision and decision['macro_details']:
                            st.subheader("🌍 Macro Factors (11 External Indicators)")
                            
                            macro_details = decision['macro_details']
                            factor_scores = macro_details.get('factor_scores', {})
                            
                            if factor_scores:
                                # Create dataframe for plotting
                                df_macro = pd.DataFrame({
                                    'Factor': list(factor_scores.keys()),
                                    'Score': list(factor_scores.values())
                                })
                                
                                # Horizontal bar chart
                                fig = go.Figure()
                                
                                colors = ['#00ff88' if score >= 65 else '#ff5555' if score <= 35 else '#ffaa00' 
                                          for score in df_macro['Score']]
                                
                                fig.add_trace(go.Bar(
                                    y=df_macro['Factor'],
                                    x=df_macro['Score'],
                                    orientation='h',
                                    marker=dict(color=colors),
                                    text=df_macro['Score'].apply(lambda x: f"{x:.1f}"),
                                    textposition='auto'
                                ))
                                
                                fig.update_layout(
                                    title="Macro Factor Scores (0-100)",
                                    xaxis_title="Score",
                                    yaxis_title="Factor",
                                    height=500,
                                    template="plotly_dark"
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Correlation values
                                st.markdown("#### 📈 Correlation Values")
                                
                                correlations = macro_details.get('correlations', {})
                                
                                if correlations:
                                    df_corr = pd.DataFrame({
                                        'Factor': list(correlations.keys()),
                                        'Correlation': list(correlations.values())
                                    })
                                    
                                    st.dataframe(df_corr, use_container_width=True, height=400)
                        
                        st.markdown("---")
                        
                        # =============================================
                        # RISK METRICS
                        # =============================================
                        st.subheader("⚠️ Risk Assessment")
                        
                        risk_metrics = decision.get('risk_metrics', {})
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            ror = risk_metrics.get('risk_of_ruin', 0)
                            st.metric(
                                "Risk of Ruin",
                                f"{ror:.2f}%",
                                delta="Target: <5%",
                                delta_color="inverse" if ror > 10 else "normal"
                            )
                        
                        with col2:
                            mdd = risk_metrics.get('max_drawdown', 0)
                            st.metric(
                                "Max Drawdown",
                                f"{mdd:.2f}%",
                                delta="Target: <20%",
                                delta_color="inverse" if mdd > 30 else "normal"
                            )
                        
                        with col3:
                            sharpe = risk_metrics.get('sharpe_ratio', 0)
                            st.metric(
                                "Sharpe Ratio",
                                f"{sharpe:.2f}",
                                delta="Target: >1.5",
                                delta_color="normal" if sharpe > 1.5 else "off"
                            )
                        
                        st.markdown("---")
                        
                        # =============================================
                        # FULL DECISION DETAILS
                        # =============================================
                        st.subheader("📋 Full Decision Details")
                        
                        with st.expander("🔍 View Complete Decision Object", expanded=False):
                            st.json(decision)
                    
                    else:
                        st.error("❌ AI Brain returned None")
                
                except Exception as e:
                    st.error(f"❌ Error analyzing {selected_coin}:")
                    st.code(traceback.format_exc())
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    st.markdown("---")
    st.markdown(f"**Last Updated:** {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("**DEMIR AI v10.0 PRO** | Phase 6: Macro Correlation + AI Transparency")
    
    # Auto-refresh
    if auto_refresh:
        import time as time_module
        time_since = (datetime.now() - st.session_state.last_refresh).total_seconds()
        if time_since >= 30:
            st.session_state.last_refresh = datetime.now()
            st.rerun()

# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    main()
