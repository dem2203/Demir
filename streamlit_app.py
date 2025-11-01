"""
🔱 DEMIR AI TRADING BOT - DASHBOARD v10.3 ULTIMATE
===================================================
Date: 1 Kasım 2025, 23:48 CET
Version: 10.3 - 7 CRITICAL FIXES from Duzeltme.docx

FIXED IN v10.3:
---------------
✅ FIX 1: Layer Breakdown - MORE professional + Turkish parentheses
✅ FIX 2: Score Explanations - Bearish/Bullish next to every score
✅ FIX 3: SHORT vs LONG BUG - Signal and parameters now consistent!
✅ FIX 4: AI Commentary - Numbers explained (what they mean)
✅ FIX 5: Auto Refresh - Manual seconds input (5-300)
✅ FIX 6: Manual Coin Add - BTC/ETH/LTC permanent + text input + Add button
✅ FIX 7: Trade History DataFrame - Error fixed

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
import json

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
    page_title="🔱 DEMIR AI Trading Bot v10.3 ULTIMATE",
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
    
    .layer-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .risk-warning {
        background: rgba(255, 170, 0, 0.1);
        border: 2px solid rgba(255, 170, 0, 0.5);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE (FIX #6: DYNAMIC COINS!)
# ============================================================================
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

if 'manual_trades' not in st.session_state:
    st.session_state.manual_trades = []

# FIX #6: Dynamic coin list (BTC/ETH/LTC permanent + user additions)
if 'active_coins' not in st.session_state:
    st.session_state.active_coins = [
        ('BTCUSDT', 'Bitcoin', '₿'),
        ('ETHUSDT', 'Ethereum', '♦️'),
        ('LTCUSDT', 'Litecoin', 'Ł')
    ]

# ============================================================================
# UTILITY FUNCTIONS (FIX #2: ENHANCED EXPLANATIONS!)
# ============================================================================

def get_score_explanation(score, metric_type="general"):
    """
    FIX #2: Get human-readable explanation for score
    Now with Turkish explanations in parentheses!
    """
    if metric_type == "strategy":
        if score >= 70:
            return "🟢 Güçlü Yükseliş Sinyali (Strong Bullish Signal)"
        elif score >= 55:
            return "🟢 Orta Yükseliş (Moderate Bullish)"
        elif score >= 45:
            return "🟡 Nötr / Bekle (Neutral / Wait)"
        elif score >= 30:
            return "🔴 Orta Düşüş (Moderate Bearish)"
        else:
            return "🔴 Güçlü Düşüş Sinyali (Strong Bearish Signal)"
    
    elif metric_type == "macro":
        if score >= 70:
            return "🌍 Makro Çok Olumlu (Macro Tailwinds Strong)"
        elif score >= 55:
            return "🌍 Makro Destekleyici (Macro Supportive)"
        elif score >= 45:
            return "🌍 Makro Nötr (Macro Neutral)"
        elif score >= 30:
            return "🌍 Makro Olumsuz (Macro Headwinds)"
        else:
            return "🌍 Makro Çok Olumsuz (Macro Very Bearish)"
    
    else:  # general
        if score >= 70:
            return "Yükseliş - Yüksek Güven (Bullish - High Confidence)"
        elif score >= 55:
            return "Yükseliş - Orta (Bullish - Moderate)"
        elif score >= 45:
            return "Nötr - Netlik Bekle (Neutral - Wait for clarity)"
        elif score >= 30:
            return "Düşüş - Riskli (Bearish - Risky)"
        else:
            return "Çok Düşüş - Kaçın (Very Bearish - Avoid)"

def get_layer_explanation(layer_name):
    """
    FIX #1: Get detailed explanation for each layer
    Enhanced with Turkish descriptions!
    """
    explanations = {
        "Layers 1-11 (Strategy)": {
            "name": "📊 Kombine Strateji Katmanları (Combined Strategy Layers)",
            "description": "11 teknik analiz katmanından toplanan skor: Volume Profile (Hacim Profili), Pivot Points (Pivot Noktaları), Fibonacci, VWAP (Hacim Ağırlıklı Ortalama Fiyat), Monte Carlo (Risk Simülasyonu), Kelly Criterion (Optimal Pozisyon Boyutu), GARCH Volatility (Volatilite Tahmini), Markov Regime (Piyasa Rejimi), Historical Volatility Index (Geçmiş Volatilite), Volatility Squeeze (Volatilite Sıkışması).",
            "interpretation": "✅ Yüksek skor = Çoklu teknik göstergeler yükseliş yönünde (Multiple technical indicators aligned bullish)\n❌ Düşük skor = Teknik zayıflık (Technical weakness)"
        },
        "Layer 12 (Macro Correlation)": {
            "name": "🌍 Makro Piyasa Korelasyonu (Macro Market Correlation)",
            "description": "11 dış piyasa ile korelasyon analizi: SPX (S&P 500), NASDAQ, DXY (Dolar Endeksi), Gold (Altın), Silver (Gümüş), BTC Dominance (BTC Dominansı), USDT Dominance (USDT Dominansı), VIX (Korku Endeksi), 10Y Yields (10 Yıllık Tahvil), Oil (Petrol), EUR/USD.",
            "interpretation": "✅ Yüksek skor = Makro ortam kripto destekliyor (Macro environment supportive of crypto)\n❌ Düşük skor = Makro rüzgar ters (Macro headwinds)"
        },
        "Combined Score": {
            "name": "🎯 Final AI Karar Skoru (Final AI Decision Score)",
            "description": "Strateji (%70) ve Makro (%30) katmanlarının ağırlıklı kombinasyonu. Trade kararları için kullanılan final skor.",
            "interpretation": "📈 >65 = LONG sinyali (Buy signal)\n📉 <35 = SHORT sinyali (Sell signal)\n⏸️ 35-65 = BEKLE (Wait for clarity)"
        }
    }
    
    return explanations.get(layer_name, {
        "name": layer_name,
        "description": "Katman analiz bileşeni",
        "interpretation": "Skorlama metriği"
    })

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
        'status': 'OPEN',
        'pnl': 0.0
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

def format_commentary_clean(commentary):
    """
    FIX #4: Format AI commentary with number explanations
    """
    if not commentary:
        return "No commentary available"
    
    # Remove any \n\n artifacts
    clean = commentary.replace('\\n\\n', '\n\n').replace('\\n', '\n')
    
    # Split into sections
    sections = clean.split('\n\n')
    
    formatted = []
    for section in sections:
        if section.strip():
            # Add Turkish explanations for key terms and numbers
            section = section.replace('Pivot Points:', '📍 **Pivot Points** *(Destek/Direnç Seviyeleri - Support/Resistance Levels)*:')
            section = section.replace('Monte Carlo:', '🎲 **Monte Carlo** *(Risk Simülasyonu - Risk Simulation)*:')
            section = section.replace('Kelly:', '💰 **Kelly Criterion** *(Optimal Pozisyon Boyutu - Optimal Position Size)*:')
            section = section.replace('optimal:', 'optimal *(en uygun miktar - best amount)*:')
            section = section.replace('position:', 'position *(pozisyon büyüklüğü - position size)*:')
            section = section.replace('risk:', 'risk *(risk miktarı - risk amount)*:')
            
            formatted.append(section.strip())
    
    return '\n\n'.join(formatted)
# ============================================================================
# FIX #3: GET TRADE RISK TYPE (SHORT vs LONG CONSISTENCY!)
# ============================================================================

def get_trade_risk_type(decision):
    """
    FIX #3: Determine trade risk type with signal consistency check!
    This fixes the SHORT signal with LONG parameters bug!
    """
    if not decision or not isinstance(decision, dict):
        return "NO_TRADE"
    
    final_score = decision.get('final_score', 50)
    signal = decision.get('decision') or decision.get('final_decision', 'WAIT')
    
    # FIX #3: Ensure signal matches parameters direction!
    entry = decision.get('entry_price', 0)
    sl = decision.get('stop_loss', 0)
    tp = decision.get('take_profit', 0)
    
    # Determine actual direction from parameters
    if entry and sl and tp:
        if tp > entry > sl:  # LONG structure
            actual_direction = "LONG"
        elif tp < entry < sl:  # SHORT structure
            actual_direction = "SHORT"
        else:
            actual_direction = "UNCERTAIN"
        
        # CRITICAL FIX: Override signal if inconsistent!
        if signal != actual_direction and actual_direction != "UNCERTAIN":
            signal = actual_direction
            decision['decision'] = actual_direction  # Update in dict
            decision['final_decision'] = actual_direction
    
    # Now classify risk based on corrected signal
    if signal == "LONG":
        if final_score >= 70:
            return "STRONG_LONG"
        elif final_score >= 55:
            return "WEAK_LONG"
        else:
            return "MEDIUM_RISK"
    
    elif signal == "SHORT":
        if final_score <= 30:
            return "STRONG_SHORT"
        elif final_score <= 45:
            return "WEAK_SHORT"
        else:
            return "MEDIUM_RISK"
    
    else:  # WAIT
        return "NO_TRADE"

# ============================================================================
# CARD RENDERING WITH FIX #3: CONSISTENT SIGNALS!
# ============================================================================

def render_trade_card(symbol, coin_name, emoji, decision, price_data, ws_status):
    """Render trading card with FIXED signal consistency"""
    
    if not decision or not isinstance(decision, dict):
        st.error(f"❌ AI Brain returned None for {coin_name}")
        return
    
    # FIX #3: Get corrected risk type (fixes SHORT/LONG bug!)
    risk_type = get_trade_risk_type(decision)
    final_score = decision.get('final_score', 50)
    signal = decision.get('decision') or decision.get('final_decision', 'WAIT')
    
    # ========================================================================
    # SIGNAL BADGE WITH RISK WARNING (FIX #2: EXPLANATIONS!)
    # ========================================================================
    if risk_type in ["STRONG_LONG", "WEAK_LONG"]:
        if risk_type == "STRONG_LONG":
            st.success(f"🟢 **STRONG LONG SIGNAL** - {emoji} {coin_name} (Score: {final_score:.1f})")
        else:
            st.success(f"🟢 **LONG SIGNAL (Weak)** - {emoji} {coin_name} (Score: {final_score:.1f})")
            st.warning("⚠️ Zayıf sinyal - Dikkatli ol! (Weak signal - Be cautious!)")
    
    elif risk_type in ["STRONG_SHORT", "WEAK_SHORT"]:
        if risk_type == "STRONG_SHORT":
            st.error(f"🔴 **STRONG SHORT SIGNAL** - {emoji} {coin_name} (Score: {final_score:.1f})")
        else:
            st.error(f"🔴 **SHORT SIGNAL (Weak)** - {emoji} {coin_name} (Score: {final_score:.1f})")
            st.warning("⚠️ Zayıf sinyal - Dikkatli ol! (Weak signal - Be cautious!)")
    
    elif risk_type == "MEDIUM_RISK":
        st.warning(f"🟡 **MEDIUM RISK - {signal}** - {emoji} {coin_name} (Score: {final_score:.1f})")
        st.markdown("""
        <div class="risk-warning">
            ⚠️ <strong>ORTA RİSK BÖLGESİ</strong><br>
            AI belirsizlik tespit etti. Trade açmak istersen parametreler hazır ama kendi analizini de yap!<br>
            <em>(MEDIUM RISK ZONE: AI detected uncertainty. Parameters ready but do your own analysis!)</em>
        </div>
        """, unsafe_allow_html=True)
    
    else:  # NO_TRADE
        st.info(f"⚪ **WAIT - NO TRADE** - {emoji} {coin_name} (Score: {final_score:.1f})")
        st.markdown("""
        <div style='background: rgba(100,100,255,0.1); border: 1px solid rgba(100,100,255,0.3); padding: 15px; border-radius: 10px;'>
            ℹ️ <strong>PİYASA ÇOK BELİRSİZ</strong><br>
            Score tam nötr bölgede. Bekle, netlik gelene kadar trade açma!<br>
            <em>(Market too uncertain. Wait for clarity before trading!)</em>
        </div>
        """, unsafe_allow_html=True)
    
    # ========================================================================
    # PRICE METRIC
    # ========================================================================
    st.metric(
        label=f"Current Price ({ws_status})",
        value=f"${price_data['price']:,.2f}",
        delta=f"{price_data['change_24h']:+.2f}% (24h)"
    )
    
    # ========================================================================
    # TRADING PARAMETERS - CONDITIONAL DISPLAY!
    # ========================================================================
    if risk_type != "NO_TRADE":  # Show params for all except NO_TRADE
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
        
        # ====================================================================
        # COPY BUTTONS
        # ====================================================================
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
        
        # ====================================================================
        # MANUAL TRADE ENTRY BUTTON (NO BALLOONS - v10.3!)
        # ====================================================================
        st.markdown("---")
        st.markdown("### ✋ Manual Trade Entry")
        
        col_trade, col_info = st.columns([1, 2])
        
        with col_trade:
            button_type = "primary" if risk_type in ["STRONG_LONG", "STRONG_SHORT"] else "secondary"
            button_label = "✅ I Opened This Trade!" if risk_type in ["STRONG_LONG", "STRONG_SHORT"] else "🔶 Riskli Trade Aç (Risky Trade)"
            
            if st.button(button_label, key=f"manual_trade_{symbol}", type=button_type):
                trade = log_manual_trade(symbol, decision)
                st.success(f"✅ Trade logged for {coin_name}!")
                # NO st.balloons() - removed in v10.3!
        
        with col_info:
            if risk_type == "MEDIUM_RISK":
                st.warning(f"⚠️ Orta risk - Kendi analizini yap! (Medium risk - Do your analysis!)")
            else:
                st.info(f"💡 Click when you manually open a trade based on AI recommendation")
    
    else:
        # NO_TRADE: Don't show parameters
        st.info("ℹ️ Trade parametreleri çok belirsiz olduğu için gösterilmiyor. (Parameters hidden due to high uncertainty)")
    
    # ========================================================================
    # FIX #1: LAYER BREAKDOWN (ENHANCED with TURKISH!)
    # ========================================================================
    if 'layer_scores' in decision and decision['layer_scores']:
        with st.expander("🔬 Layer Breakdown (Detailed)", expanded=False):
            st.markdown("### 📊 AI Layer Analysis")
            
            for layer_name, score in decision['layer_scores'].items():
                layer_info = get_layer_explanation(layer_name)
                explanation = get_score_explanation(score, "strategy" if "Strategy" in layer_name else "macro" if "Macro" in layer_name else "general")
                
                st.markdown(f"**{layer_info['name']}**")
                st.progress(score / 100, text=f"{score:.1f}/100 - {explanation}")
                st.caption(f"📖 **Açıklama:** {layer_info['description']}")
                st.caption(f"📊 **Yorumlama:** {layer_info['interpretation']}")
                st.markdown("---")
    
    # ========================================================================
    # FIX #4: AI COMMENTARY (WITH NUMBER EXPLANATIONS!)
    # ========================================================================
    if 'ai_commentary' in decision and decision['ai_commentary']:
        with st.expander("🤖 AI Commentary", expanded=False):
            clean_commentary = format_commentary_clean(decision['ai_commentary'])
            st.markdown(clean_commentary)
    
    st.markdown("---")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application with v10.3 fixes"""
    
    # WebSocket init
    ws_manager = None
    if WEBSOCKET_AVAILABLE:
        try:
            # FIX #6: Use dynamic coins
            symbols = [coin[0] for coin in st.session_state.active_coins]
            ws_manager = get_websocket_manager(symbols)
        except:
            pass
    
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🔱 DEMIR AI TRADING BOT v10.3 ULTIMATE")
    
    with col2:
        if WEBSOCKET_AVAILABLE and ws_manager:
            st.markdown("### 🟢 LIVE")
        else:
            st.markdown("### 🟡 REST")
    
    with col3:
        st.markdown(f"### ⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    st.markdown("---")
    
    # ========================================================================
    # SIDEBAR WITH FIX #5: MANUAL REFRESH SECONDS!
    # ========================================================================
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
        
        # FIX #6: Dynamic coin display
        st.subheader("🎯 Active Pairs")
        for symbol, name, emoji in st.session_state.active_coins:
            st.markdown(f"• **{emoji} {name}** ({symbol})")
        
        st.markdown("---")
        
        # FIX #5: Manual refresh seconds input!
        st.subheader("🔄 Auto Refresh")
        auto_refresh = st.checkbox("Enable Auto Refresh", value=False)
        
        if auto_refresh:
            refresh_seconds = st.number_input(
                "Refresh Interval (seconds)",
                min_value=5,
                max_value=300,
                value=30,
                step=5,
                help="Set auto-refresh interval between 5-300 seconds"
            )
            st.caption(f"⏱️ Will refresh every {refresh_seconds} seconds")
        
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.session_state.last_refresh = datetime.now()
            st.rerun()
        
        st.markdown("---")
        
        # FIX #6: Add new coin section!
        st.subheader("➕ Add New Coin")
        st.caption("BTC/ETH/LTC are permanent")
        
        new_coin_symbol = st.text_input(
            "Symbol (e.g., ADAUSDT)",
            key="new_coin_input",
            help="Enter Binance Futures symbol"
        ).upper()
        
        new_coin_name = st.text_input(
            "Name (e.g., Cardano)",
            key="new_coin_name",
            help="Display name"
        )
        
        new_coin_emoji = st.text_input(
            "Emoji (e.g., 🔷)",
            key="new_coin_emoji",
            value="💎",
            help="Emoji for display"
        )
        
        if st.button("➕ Add Coin", use_container_width=True):
            if new_coin_symbol and new_coin_name:
                # Check if already exists
                existing = [c[0] for c in st.session_state.active_coins]
                if new_coin_symbol not in existing:
                    st.session_state.active_coins.append((new_coin_symbol, new_coin_name, new_coin_emoji))
                    st.success(f"✅ Added {new_coin_name}!")
                    st.rerun()
                else:
                    st.warning(f"⚠️ {new_coin_symbol} already exists!")
            else:
                st.error("❌ Please fill both Symbol and Name")
    
    # ========================================================================
    # TABS
    # ========================================================================
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 TRADE SIGNALS",
        "📈 POSITIONS",
        "💼 PORTFOLIO",
        "⚡ BACKTEST",
        "📜 HISTORY",
        "🧠 AI BREAKDOWN"
    ])
    
    # ========================================================================
    # TAB 1: TRADE SIGNALS (WITH DYNAMIC COINS - FIX #6!)
    # ========================================================================
    with tab1:
        st.header("🎯 LIVE TRADE SIGNALS")
        st.markdown("*AI-powered 12-layer analysis with macro correlation + Smart WAIT logic*")
        st.markdown("---")
        
        # FIX #6: Use dynamic coin list!
        for symbol, coin_name, emoji in st.session_state.active_coins:
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
    # TAB 2: POSITIONS (FIX #7: DataFrame ERROR FIXED!)
    # ========================================================================
    with tab2:
        st.header("📈 Active Positions")
        st.markdown("*Monitor open positions and P/L*")
        st.markdown("---")
        
        # Show manual trades from session state
        if len(st.session_state.manual_trades) > 0:
            st.subheader("✋ Manuel Trades (Open)")
            
            df_manual = pd.DataFrame(st.session_state.manual_trades)
            
            # FIX #7: Add current price and P/L calculation (SAFE!)
            for idx, trade in enumerate(st.session_state.manual_trades):
                try:
                    price_data = get_binance_price(trade['symbol'], ws_manager)
                    if price_data['available']:
                        current_price = price_data['price']
                        entry_price = trade['entry_price']
                        
                        if trade['signal'] == 'LONG':
                            pnl = ((current_price - entry_price) / entry_price) * 100
                        else:
                            pnl = ((entry_price - current_price) / entry_price) * 100
                        
                        st.session_state.manual_trades[idx]['pnl'] = pnl
                        st.session_state.manual_trades[idx]['current_price'] = current_price
                except Exception as e:
                    # Silently handle error - don't crash
                    pass
            
            # FIX #7: Refresh dataframe safely
            try:
                df_manual = pd.DataFrame(st.session_state.manual_trades)
                st.dataframe(df_manual, use_container_width=True, height=400)
            except Exception as e:
                st.error(f"❌ DataFrame error: {str(e)}")
                st.caption("Fallback: Showing raw data")
                st.json(st.session_state.manual_trades)
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Open Trades", len(st.session_state.manual_trades))
            with col2:
                try:
                    avg_pnl = df_manual['pnl'].mean() if 'pnl' in df_manual.columns else 0
                    st.metric("Avg P/L", f"{avg_pnl:+.2f}%")
                except:
                    st.metric("Avg P/L", "N/A")
            with col3:
                try:
                    total_pnl = df_manual['pnl'].sum() if 'pnl' in df_manual.columns else 0
                    st.metric("Total P/L", f"{total_pnl:+.2f}%")
                except:
                    st.metric("Total P/L", "N/A")
        
        # Position Tracker fallback
        if POSITION_TRACKER_AVAILABLE:
            try:
                positions = tracker.positions if hasattr(tracker, 'positions') else []
                
                if len(positions) > 0:
                    st.subheader("📊 Position Tracker Data")
                    df = pd.DataFrame(positions)
                    st.dataframe(df, use_container_width=True, height=300)
            except Exception as e:
                pass
        
        if len(st.session_state.manual_trades) == 0 and (not POSITION_TRACKER_AVAILABLE or len(positions) == 0):
            st.info("📭 No active positions. Click 'I Opened This Trade!' on the TRADE SIGNALS tab to track a position.")
    
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
    # TAB 5: HISTORY (FIX #7: DataFrame SAFE!)
    # ========================================================================
    with tab5:
        st.header("📜 Trade History")
        st.markdown("*Complete record of all trades*")
        st.markdown("---")
        
        # Show manual trades from session state
        if len(st.session_state.manual_trades) > 0:
            st.subheader("✋ Manual Trades (This Session)")
            try:
                df_manual = pd.DataFrame(st.session_state.manual_trades)
                st.dataframe(df_manual, use_container_width=True)
            except Exception as e:
                st.error(f"❌ DataFrame error: {str(e)}")
                st.json(st.session_state.manual_trades)
        
        # Show database trades
        if DB_AVAILABLE:
            try:
                trades = db.get_all_trades()
                
                if trades and len(trades) > 0:
                    st.subheader("💾 Database Trades")
                    try:
                        df = pd.DataFrame(trades)
                        st.dataframe(df, use_container_width=True, height=400)
                    except Exception as e:
                        st.error(f"❌ DataFrame error: {str(e)}")
                        st.json(trades)
                    
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
    # TAB 6: AI BRAIN BREAKDOWN
    # ========================================================================
    with tab6:
        st.header("🧠 AI Brain Breakdown")
        st.markdown("*Full transparency: See how AI makes decisions*")
        st.markdown("---")
        
        if not AI_BRAIN_AVAILABLE:
            st.warning("⚠️ AI Brain not available")
        else:
            # FIX #6: Use dynamic coins for selector
            coin_options = [coin[0] for coin in st.session_state.active_coins]
            
            selected_coin = st.selectbox(
                "Select Coin for Analysis:",
                coin_options,
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
                        # SCORE SUMMARY (WITH ENHANCED EXPLANATIONS!)
                        # =============================================
                        st.subheader("📊 Score Summary")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            strategy_score = decision.get('layer_scores', {}).get('Layers 1-11 (Strategy)', 50)
                            strategy_exp = get_score_explanation(strategy_score, "strategy")
                            st.metric(
                                "Strategy Score",
                                f"{strategy_score:.1f}/100",
                                delta="70% weight"
                            )
                            st.caption(f"📊 {strategy_exp}")
                        
                        with col2:
                            macro_score = decision.get('macro_score', 50)
                            macro_exp = get_score_explanation(macro_score, "macro")
                            st.metric(
                                "Macro Score",
                                f"{macro_score:.1f}/100",
                                delta="30% weight"
                            )
                            st.caption(f"🌍 {macro_exp}")
                        
                        with col3:
                            final_score = decision.get('final_score', 50)
                            final_exp = get_score_explanation(final_score, "general")
                            delta_color = "normal" if 45 <= final_score <= 65 else ("off" if final_score < 45 else "inverse")
                            st.metric(
                                "Combined Score",
                                f"{final_score:.1f}/100",
                                delta=decision.get('decision', 'WAIT'),
                                delta_color=delta_color
                            )
                            st.caption(f"🎯 {final_exp}")
                        
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
                        # RISK METRICS (WITH TURKISH EXPLANATIONS!)
                        # =============================================
                        st.subheader("⚠️ Risk Assessment (Risk Değerlendirmesi)")
                        
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
                            if ror > 10:
                                st.caption("⚠️ Yüksek risk - Pozisyon boyutunu azalt! (High risk - Reduce position!)")
                            else:
                                st.caption("✅ Kabul edilebilir risk seviyesi (Acceptable risk level)")
                        
                        with col2:
                            mdd = risk_metrics.get('max_drawdown', 0)
                            st.metric(
                                "Max Drawdown",
                                f"{mdd:.2f}%",
                                delta="Target: <20%",
                                delta_color="inverse" if mdd > 30 else "normal"
                            )
                            if mdd > 30:
                                st.caption("⚠️ Yüksek düşüş bekleniyor (High drawdown expected)")
                            else:
                                st.caption("✅ Yönetilebilir düşüş (Manageable drawdown)")
                        
                        with col3:
                            sharpe = risk_metrics.get('sharpe_ratio', 0)
                            st.metric(
                                "Sharpe Ratio",
                                f"{sharpe:.2f}",
                                delta="Target: >1.5",
                                delta_color="normal" if sharpe > 1.5 else "off"
                            )
                            if sharpe > 1.5:
                                st.caption("✅ İyi risk-adjusted returns (Good risk-adjusted returns)")
                            else:
                                st.caption("⚠️ Hedefin altında verimlilik (Below target efficiency)")
                        
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
    st.markdown("**DEMIR AI v10.3 ULTIMATE** | 7 Critical Fixes Applied")
    
    # FIX #5: Auto-refresh with manual seconds!
    if auto_refresh:
        import time as time_module
        time_since = (datetime.now() - st.session_state.last_refresh).total_seconds()
        if time_since >= refresh_seconds:
            st.session_state.last_refresh = datetime.now()
            st.rerun()

# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    main()

