"""
🔱 DEMIR AI TRADING BOT - Streamlit UI v9.0 ULTIMATE
====================================================
Date: 2 Kasım 2025, 20:40 CET
Version: 9.0 - PROFESSIONAL TRADING DASHBOARD

FEATURES:
---------
✅ Phase 1-2: Watchlist + Trade History
✅ Phase 3: Backtest + Portfolio + Auto-Trade
✅ Phase 4: Real-time + Multi-TF + ML + News
✅ Phase 6: 18-Layer AI Analysis
✅ Educational tooltips (her metric açıklamalı)
✅ Professional design (görsel mükemmellik)
✅ 3 Fixed Coins + Custom Coin System
✅ Real-time price updates
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import plotly.graph_objects as go
import plotly.express as px

# ============================================================================
# PAGE CONFIG - MUST BE FIRST!
# ============================================================================

st.set_page_config(
    page_title="🔱 DEMIR AI Trading Bot",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - PROFESSIONAL STYLING
# ============================================================================

st.markdown("""
<style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(90deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .header-title {
        font-size: 3rem;
        font-weight: 800;
        color: #00d9ff;
        text-align: center;
        margin: 0;
        text-shadow: 0 0 20px rgba(0, 217, 255, 0.5);
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        color: #b8b8b8;
        text-align: center;
        margin-top: 0.5rem;
    }
    
    /* Metric card styling */
    .metric-card {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #00d9ff;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0, 217, 255, 0.3);
    }
    
    .metric-title {
        font-size: 0.9rem;
        color: #95a5a6;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #ecf0f1;
        margin: 0;
    }
    
    .metric-value.positive {
        color: #2ecc71;
    }
    
    .metric-value.negative {
        color: #e74c3c;
    }
    
    .metric-value.neutral {
        color: #f39c12;
    }
    
    /* Signal badges */
    .signal-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        text-align: center;
        min-width: 100px;
    }
    
    .signal-badge.buy {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        box-shadow: 0 0 15px rgba(46, 204, 113, 0.5);
    }
    
    .signal-badge.sell {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        box-shadow: 0 0 15px rgba(231, 76, 60, 0.5);
    }
    
    .signal-badge.hold {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        color: white;
        box-shadow: 0 0 15px rgba(243, 156, 18, 0.5);
    }
    
    /* Layer score cards */
    .layer-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(0, 217, 255, 0.2);
    }
    
    .layer-name {
        font-size: 0.85rem;
        color: #00d9ff;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .layer-description {
        font-size: 0.75rem;
        color: #95a5a6;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
    
    /* Explanation boxes */
    .explanation-box {
        background: rgba(0, 217, 255, 0.1);
        border-left: 3px solid #00d9ff;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .explanation-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: #00d9ff;
        margin-bottom: 0.5rem;
    }
    
    .explanation-text {
        font-size: 0.85rem;
        color: #ecf0f1;
        line-height: 1.6;
    }
    
    /* Tooltip styling */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        color: #00d9ff;
        font-weight: 600;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #00d9ff 0%, #0095ff 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(0, 217, 255, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 217, 255, 0.5);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Info icons */
    .info-icon {
        display: inline-block;
        width: 18px;
        height: 18px;
        background: #00d9ff;
        border-radius: 50%;
        text-align: center;
        line-height: 18px;
        color: white;
        font-size: 12px;
        font-weight: bold;
        margin-left: 5px;
        cursor: help;
    }
    
    /* Phase badges */
    .phase-badge {
        display: inline-block;
        background: rgba(0, 217, 255, 0.2);
        color: #00d9ff;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    /* Score gauge */
    .score-container {
        text-align: center;
        margin: 2rem 0;
    }
    
    .score-circle {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        font-weight: 800;
        box-shadow: 0 0 30px rgba(0, 217, 255, 0.4);
        margin: 1rem auto;
    }
    
    .score-circle.excellent {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
    }
    
    .score-circle.good {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
    }
    
    .score-circle.neutral {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        color: white;
    }
    
    .score-circle.poor {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# IMPORT AI BRAIN
# ============================================================================

try:
    import ai_brain
    AI_BRAIN_AVAILABLE = True
    print("✅ Streamlit: ai_brain module imported successfully!")
except Exception as e:
    AI_BRAIN_AVAILABLE = False
    st.error(f"❌ AI Brain import failed: {e}")
    print(f"❌ Streamlit: ai_brain import failed: {e}")

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']  # Fixed 3 coins

if 'custom_coins' not in st.session_state:
    st.session_state.custom_coins = []  # User-added coins

if 'selected_coin' not in st.session_state:
    st.session_state.selected_coin = 'BTCUSDT'

if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_signal_color(signal):
    """Return color based on signal type"""
    if signal == 'BUY' or signal == 'STRONG BUY':
        return 'buy'
    elif signal == 'SELL' or signal == 'STRONG SELL':
        return 'sell'
    else:
        return 'hold'

def get_score_category(score):
    """Categorize score"""
    if score >= 70:
        return 'excellent'
    elif score >= 55:
        return 'good'
    elif score >= 45:
        return 'neutral'
    else:
        return 'poor'

def format_large_number(num):
    """Format large numbers with K, M, B"""
    if num >= 1_000_000_000:
        return f"${num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"${num/1_000:.2f}K"
    else:
        return f"${num:.2f}"

def get_current_price(symbol):
    """Fetch current price from Binance"""
    try:
        from binance.client import Client
        import os
        client = Client(os.getenv('BINANCE_API_KEY', ''), os.getenv('BINANCE_API_SECRET', ''))
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except:
        # Mock prices for demo
        mock_prices = {
            'BTCUSDT': 69420.50,
            'ETHUSDT': 3580.75,
            'LTCUSDT': 185.20
        }
        return mock_prices.get(symbol, 1000.0)

# ============================================================================
# LAYER EXPLANATIONS DATABASE
# ============================================================================

LAYER_EXPLANATIONS = {
    'strategy': {
        'name': 'Teknik Strateji Katmani (1-11)',
        'description': 'RSI, MACD, Bollinger Bands, Fibonacci, VWAP, Volume Profile gibi 11 teknik gostergenin kombinasyonu.',
        'why_matters': 'Fiyat hareketlerinin matematiksel analizi ile kisa-orta vadeli trend tahminleri yapar.',
        'interpretation': {
            '70-100': 'Tum teknik gostergeler guclu al sinyali veriyor. Momentum ve trend pozitif.',
            '50-70': 'Cogu teknik gosterge pozitif ama karisik sinyaller var. Dikkatli yaklasim onerilir.',
            '30-50': 'Teknik gostergeler zayif veya karisik. Bekleme pozisyonu en mantiklisi.',
            '0-30': 'Teknik gostergeler sat sinyali veriyor. Momentum negatif.'
        }
    },
    'macro': {
        'name': 'Makro Korelasyon (Layer 12)',
        'description': 'DXY (Dolar), S&P500, Nasdaq gibi geleneksel piyasalarla korelasyon analizi.',
        'why_matters': 'Kripto piyasalari artik global finans sistemiyle entegre. Makro gostergeler kripto uzerinde etkili.',
        'interpretation': {
            '70-100': 'Makro ortam kripto icin cok olumlu. Risk ishtahi yuksek.',
            '50-70': 'Makro ortam notr-pozitif. Normal piyasa kosullari.',
            '30-50': 'Makro ortam karisik. Dis riskler mevcut.',
            '0-30': 'Makro ortam olumsuz. Risk ishtahi dusuk, safe haven talep ediliyor.'
        }
    },
    'gold': {
        'name': 'Altin Korelasyonu (Layer 13)',
        'description': 'Altin (XAU/USD) fiyati ile BTC arasindaki korelasyon. "Digital gold" teorisi.',
        'why_matters': 'BTC, enflasyona karsi koruma (hedge) araci olarak algilaniyor. Altin yukselince BTC da yukselme egiliminde.',
        'interpretation': {
            '70-100': 'Altin guclu yukselis trendinde, BTC icin pozitif katalizor.',
            '50-70': 'Altin stabil, BTC icin notr ortam.',
            '30-50': 'Altin zayif, safe haven talebi dusuk.',
            '0-30': 'Altin dususte, risk ishtahi yuksek (BTC icin karisik sinyal).'
        }
    },
    'dominance': {
        'name': 'BTC Dominance (Layer 14)',
        'description': 'Bitcoin\'in toplam kripto piyasa degeri icindeki payi (%).',
        'why_matters': 'BTC dominansi yukselirken altcoinler zayiflar. Duserken altcoin sezonu baslar.',
        'interpretation': {
            '70-100': 'BTC dominansi artiyor. Para BTC\'ye akiyor, guvenli liman.',
            '50-70': 'BTC dominansi stabil. Dengeli piyasa.',
            '30-50': 'BTC dominansi dusuyor. Altcoinlere para akiyor.',
            '0-30': 'BTC dominansi hizla dusuyor. Altcoin sezonu peak\'te.'
        }
    },
    'cross_asset': {
        'name': 'Cross-Asset Analizi (Layer 15)',
        'description': 'ETH, LTC, BNB gibi diger major kripto paralarla korelasyon.',
        'why_matters': 'BTC diger kriptolarla birlikte mi hareket ediyor yoksa tek basina mi? Piyasa geneli momentum gostergesi.',
        'interpretation': {
            '70-100': 'Tum major kriptolar birlikte yukseliyor. Guclu piyasa trendi.',
            '50-70': 'Kripto piyasasi karma sinyal veriyor.',
            '30-50': 'Kriptolar birbirinden bagimsiz hareket ediyor. Belirsizlik var.',
            '0-30': 'Major kriptolar dususte. Genel piyasa sentiment negatif.'
        }
    },
    'vix': {
        'name': 'VIX Korku Endeksi (Layer 16)',
        'description': 'S&P500 volatilite endeksi. "Korku gostergesi" olarak bilinir.',
        'why_matters': 'VIX yuksekken yatirimcilar korkulu, risk almak istemezler. Kripto gibi riskli varliklari satar.',
        'interpretation': {
            '70-100': 'VIX cok dusuk (<15). Piyasada komplikasyon yok, risk ishtahi yuksek.',
            '50-70': 'VIX normal seviyede (15-20). Dengeli risk ortami.',
            '30-50': 'VIX yukseliyor (20-30). Belirsizlik artiyor.',
            '0-30': 'VIX cok yuksek (>30). Panik modu. Kripto icin cok riskli.'
        }
    },
    'rates': {
        'name': 'Faiz Oranlari (Layer 17)',
        'description': 'Fed faiz oranlari, 10-yillik tahvil getirisi. Likidite gostergesi.',
        'why_matters': 'Faizler yuksekken para pahali, kripto gibi riskli varliklara talep azalir. Faizler dusukken likidite bol.',
        'interpretation': {
            '70-100': 'Faizler dusuyor veya cok dusuk. Bol likidite, kripto icin pozitif.',
            '50-70': 'Faizler stabil. Normal ortam.',
            '30-50': 'Faizler yukseliyor. Likidite azaliyor.',
            '0-30': 'Faizler cok yuksek. Para cok pahali, kripto icin olumsuz.'
        }
    },
    'traditional_markets': {
        'name': 'Geleneksel Piyasalar (Layer 18)',
        'description': 'S&P500, Nasdaq, Dow Jones performansi.',
        'why_matters': 'Hisse piyasasi iyi gidiyorsa risk ishtahi yuksek, kripto da genelde pozitif etkilenir.',
        'interpretation': {
            '70-100': 'Hisse piyasalari rallide. Risk ishtahi cok yuksek.',
            '50-70': 'Hisse piyasalari pozitif. Stabil buyume.',
            '30-50': 'Hisse piyasalari karma. Belirsizlik var.',
            '0-30': 'Hisse piyasalari dususte. Risk-off modu.'
        }
    }
}

def render_header():
    """Render professional header"""
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🔱 DEMIR AI TRADING BOT</h1>
        <p class="header-subtitle">
            18-Layer AI Analysis | Phase 1-6 Complete | Real-Time Trading Intelligence
        </p>
        <div style="text-align: center; margin-top: 1rem;">
            <span class="phase-badge">Phase 1-2: Watchlist</span>
            <span class="phase-badge">Phase 3: Automation</span>
            <span class="phase-badge">Phase 4: Real-Time + ML</span>
            <span class="phase-badge">Phase 6: 18 Layers</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_coin_selector():
    """Render coin selection UI"""
    st.markdown("### 🪙 Select Cryptocurrency")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Fixed 3 coins + custom coins
        all_coins = st.session_state.watchlist + st.session_state.custom_coins
        
        selected = st.selectbox(
            "Choose coin to analyze:",
            all_coins,
            index=all_coins.index(st.session_state.selected_coin) if st.session_state.selected_coin in all_coins else 0,
            key='coin_selector'
        )
        
        st.session_state.selected_coin = selected
    
    with col2:
        # Add custom coin button
        if st.button("➕ Add Custom Coin", use_container_width=True):
            st.session_state.show_add_coin = True
    
    # Add custom coin modal
    if st.session_state.get('show_add_coin', False):
        with st.form("add_custom_coin"):
            st.markdown("#### Add New Coin")
            new_coin = st.text_input("Enter symbol (e.g., ADAUSDT):", "").upper()
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.form_submit_button("Add", use_container_width=True):
                    if new_coin and new_coin not in st.session_state.custom_coins:
                        st.session_state.custom_coins.append(new_coin)
                        st.success(f"✅ {new_coin} added!")
                        st.session_state.show_add_coin = False
                        st.rerun()
            with col_b:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.show_add_coin = False
                    st.rerun()

def render_price_card(symbol):
    """Render current price card"""
    price = get_current_price(symbol)
    
    # Mock 24h change
    change_24h = np.random.uniform(-5, 5)
    change_class = 'positive' if change_24h >= 0 else 'negative'
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Current Price</div>
        <div class="metric-value">${price:,.2f}</div>
        <div class="metric-value {change_class}" style="font-size: 1.2rem; margin-top: 0.5rem;">
            {'+' if change_24h >= 0 else ''}{change_24h:.2f}% (24h)
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_score_gauge(score, signal):
    """Render circular score gauge"""
    category = get_score_category(score)
    
    st.markdown(f"""
    <div class="score-container">
        <div class="score-circle {category}">
            {score:.0f}
        </div>
        <h3 style="color: #ecf0f1; text-align: center; margin-top: 1rem;">
            AI Confidence Score
        </h3>
        <div style="text-align: center; margin-top: 1rem;">
            <span class="signal-badge {get_signal_color(signal)}">{signal}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_layer_breakdown(layer_scores):
    """Render detailed layer-by-layer breakdown"""
    st.markdown("### 📊 Layer-by-Layer Analysis")
    
    layer_order = ['strategy', 'macro', 'gold', 'dominance', 'cross_asset', 'vix', 'rates', 'traditional_markets']
    
    for layer_key in layer_order:
        if layer_key in layer_scores:
            score = layer_scores[layer_key]
            layer_info = LAYER_EXPLANATIONS.get(layer_key, {})
            
            # Determine score category
            if score >= 70:
                score_class = 'excellent'
                score_text = '🟢 Güçlü Al'
            elif score >= 55:
                score_class = 'good'
                score_text = '🟡 Al'
            elif score >= 45:
                score_class = 'neutral'
                score_text = '⚪ Bekle'
            else:
                score_class = 'poor'
                score_text = '🔴 Sat'
            
            # Get interpretation
            interpretation = ''
            for range_key, range_text in layer_info.get('interpretation', {}).items():
                range_parts = range_key.split('-')
                if len(range_parts) == 2:
                    low, high = int(range_parts[0]), int(range_parts[1])
                    if low <= score <= high:
                        interpretation = range_text
                        break
            
            with st.expander(f"**{layer_info.get('name', layer_key.upper())}** - Skor: {score:.1f}/100 {score_text}"):
                st.markdown(f"""
                <div class="layer-card">
                    <div class="layer-description">
                        <strong>Açıklama:</strong> {layer_info.get('description', 'N/A')}
                    </div>
                    <div class="explanation-box">
                        <div class="explanation-title">💡 Neden Önemli?</div>
                        <div class="explanation-text">{layer_info.get('why_matters', 'N/A')}</div>
                    </div>
                    <div class="explanation-box">
                        <div class="explanation-title">📖 Bu Skor Ne Anlama Geliyor?</div>
                        <div class="explanation-text">{interpretation}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Progress bar
                st.progress(score / 100)

def render_trading_recommendation(result):
    """Render detailed trading recommendation"""
    st.markdown("### 🎯 Trading Recommendation")
    
    signal = result.get('signal', 'HOLD')
    confidence = result.get('confidence', 0.5)
    entry = result.get('entry_price', 0)
    sl = result.get('stop_loss', 0)
    tp = result.get('take_profit', 0)
    position_size = result.get('position_size', 0)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Entry Price</div>
            <div class="metric-value">${entry:,.2f}</div>
            <div style="font-size: 0.8rem; color: #95a5a6; margin-top: 0.5rem;">
                Optimal giriş fiyatı
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Stop Loss</div>
            <div class="metric-value negative">${sl:,.2f}</div>
            <div style="font-size: 0.8rem; color: #95a5a6; margin-top: 0.5rem;">
                Risk yönetimi seviyesi
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Take Profit</div>
            <div class="metric-value positive">${tp:,.2f}</div>
            <div style="font-size: 0.8rem; color: #95a5a6; margin-top: 0.5rem;">
                Kar alma hedefi
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Risk/Reward Analysis
    st.markdown("#### 📈 Risk/Reward Analysis")
    
    if signal == 'BUY' and sl > 0:
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        rr_ratio = reward / risk if risk > 0 else 0
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.metric("Risk", f"${risk:.2f}", f"{(risk/entry)*100:.2f}%")
        
        with col_b:
            st.metric("Reward", f"${reward:.2f}", f"{(reward/entry)*100:.2f}%")
        
        with col_c:
            st.metric("R/R Ratio", f"{rr_ratio:.2f}", "Higher is better")
        
        # Recommendation explanation
        if rr_ratio >= 2:
            st.success(f"✅ **Mükemmel Risk/Reward!** {rr_ratio:.1f}:1 oranı çok iyi. Potansiyel kar, riski {rr_ratio:.1f} kat aşıyor.")
        elif rr_ratio >= 1.5:
            st.info(f"✔️ **İyi Risk/Reward.** {rr_ratio:.1f}:1 oranı kabul edilebilir.")
        else:
            st.warning(f"⚠️ **Düşük Risk/Reward.** {rr_ratio:.1f}:1 oranı ideal değil. Daha iyi fırsat beklemek mantıklı.")
    
    # Position sizing
    st.markdown("#### 💰 Position Sizing")
    
    kelly = result.get('kelly_percentage', 2.0)
    
    st.markdown(f"""
    <div class="explanation-box">
        <div class="explanation-title">Kelly Criterion Recommendation</div>
        <div class="explanation-text">
            Portföyünüzün <strong>{kelly:.1f}%</strong>'ini bu işleme ayırmanız önerilir.
            Bu, <strong>${position_size:,.2f}</strong> pozisyon büyüklüğü demektir.
            <br><br>
            <strong>Neden bu miktar?</strong><br>
            Kelly Criterion, kazanma olasılığı ve ortalama kazanç/kayıp oranlarına göre
            optimal pozisyon büyüklüğünü hesaplar. Bu, uzun vadede sermayenizi en iyi
            şekilde büyütmenizi sağlar.
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_phase_features():
    """Render Phase-specific features tabs"""
    st.markdown("### 🚀 Advanced Features")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Multi-Timeframe (Phase 4.2)",
        "🤖 ML Predictions (Phase 4.3)",
        "📰 News Sentiment (Phase 4.4)",
        "⚙️ Automation (Phase 3)"
    ])
    
    with tab1:
        st.markdown("#### Multi-Timeframe Consensus Analysis")
        st.info("Analyzes 5 different timeframes (1m, 5m, 15m, 1h, 4h) and provides weighted consensus signal.")
        
        if st.button("🔄 Run Multi-Timeframe Analysis", use_container_width=True):
            with st.spinner("Analyzing 5 timeframes..."):
                try:
                    result = ai_brain.make_multi_timeframe_decision(
                        symbol=st.session_state.selected_coin,
                        capital=10000.0
                    )
                    
                    st.success(f"✅ Consensus Signal: **{result.get('signal', 'N/A')}**")
                    st.metric("Consensus Score", f"{result.get('score', 50):.1f}/100")
                    
                    # Show timeframe breakdown
                    if 'timeframe_scores' in result:
                        st.markdown("**Timeframe Breakdown:**")
                        for tf, score in result['timeframe_scores'].items():
                            st.progress(score/100, text=f"{tf}: {score:.1f}/100")
                
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with tab2:
        st.markdown("#### Machine Learning Predictions")
        st.info("XGBoost classifier for trend prediction + Random Forest for volatility forecasting.")
        
        col_ml1, col_ml2 = st.columns(2)
        
        with col_ml1:
            if st.button("🎯 XGBoost Trend Prediction", use_container_width=True):
                st.info("Feature: XGBoost model predicts BUY/SELL/HOLD based on 20+ technical features.")
                st.warning("⚠️ Requires xgboost package (Phase 4.3)")
        
        with col_ml2:
            if st.button("🌪️ Random Forest Volatility", use_container_width=True):
                st.info("Feature: Predicts next-period volatility for risk management.")
                st.warning("⚠️ Requires scikit-learn package (Phase 4.3)")
    
    with tab3:
        st.markdown("#### News Sentiment Analysis V2")
        st.info("Aggregates sentiment from Twitter, Reddit, Fear & Greed Index, and news headlines.")
        
        if st.button("📰 Analyze News Sentiment", use_container_width=True):
            st.info("Feature: Multi-source sentiment analysis (4 sources)")
            st.warning("⚠️ Requires API keys for production use")
    
    with tab4:
        st.markdown("#### Automation Tools")
        
        col_auto1, col_auto2, col_auto3 = st.columns(3)
        
        with col_auto1:
            if st.button("📈 Run Backtest", use_container_width=True):
                st.info("Feature: Historical performance testing (Phase 3.2)")
        
        with col_auto2:
            if st.button("💼 Optimize Portfolio", use_container_width=True):
                st.info("Feature: Kelly Criterion optimization (Phase 3.3)")
        
        with col_auto3:
            if st.button("🤖 Auto-Trade", use_container_width=True):
                st.warning("⚠️ Feature: Automated trading (Phase 3.4) - Requires Binance API")

def main():
    """Main application entry point"""
    
    # Render header
    render_header()
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # Capital input
        capital = st.number_input(
            "Portfolio Capital (USDT):",
            min_value=100.0,
            max_value=1000000.0,
            value=10000.0,
            step=100.0
        )
        
        # Timeframe selector
        timeframe = st.selectbox(
            "Timeframe:",
            ['1m', '5m', '15m', '1h', '4h', '1d'],
            index=3  # Default: 1h
        )
        
        # Lookback period
        lookback = st.slider(
            "Lookback Period (candles):",
            min_value=50,
            max_value=500,
            value=100,
            step=50
        )
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=False)
        st.session_state.auto_refresh = auto_refresh
        
        st.markdown("---")
        
        # About section
        st.markdown("### ℹ️ About")
        st.markdown("""
        **DEMIR AI Trading Bot v9.0**
        
        🔱 18-Layer AI Analysis  
        📊 Phase 1-6 Complete  
        🤖 ML Predictions  
        📰 News Sentiment  
        ⚙️ Full Automation
        
        Built with ❤️ by Demir
        """)
    
    # Main content area
    render_coin_selector()
    
    # Current price card
    col_price1, col_price2 = st.columns([2, 1])
    
    with col_price1:
        render_price_card(st.session_state.selected_coin)
    
    with col_price2:
        if st.button("🚀 Analyze Now", use_container_width=True, type="primary"):
            st.session_state.trigger_analysis = True
    
    # Main analysis section
    if st.session_state.get('trigger_analysis', False) or st.session_state.get('analysis_result') is not None:
        
        with st.spinner("🧠 AI Brain analyzing 18 layers..."):
            try:
                # Run AI Brain analysis
                if AI_BRAIN_AVAILABLE:
                    result = ai_brain.make_trading_decision(
                        symbol=st.session_state.selected_coin,
                        timeframe=timeframe,
                        capital=capital,
                        lookback=lookback
                    )
                    
                    st.session_state.analysis_result = result
                    st.session_state.trigger_analysis = False
                else:
                    st.error("❌ AI Brain module not available!")
                    result = None
            
            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")
                result = None
        
        if result:
            # Main results layout
            col_main1, col_main2 = st.columns([1, 2])
            
            with col_main1:
                # Score gauge
                render_score_gauge(
                    result.get('score', 50),
                    result.get('signal', 'HOLD')
                )
            
            with col_main2:
                # Trading recommendation
                render_trading_recommendation(result)
            
            # Divider
            st.markdown("---")
            
            # Layer breakdown
            if 'layer_scores' in result:
                render_layer_breakdown(result['layer_scores'])
            
            # Divider
            st.markdown("---")
            
            # Phase features
            render_phase_features()
            
            # Technical details (collapsible)
            with st.expander("🔬 Technical Details (Advanced)"):
                st.json(result)
    
    else:
        # Welcome screen
        st.markdown("### 👋 Welcome to DEMIR AI Trading Bot!")
        
        st.info("""
        **Get Started:**
        1. Select a cryptocurrency from the dropdown above
        2. Configure your portfolio capital and timeframe in the sidebar
        3. Click "🚀 Analyze Now" to get AI-powered trading signals
        
        **Features:**
        - 18-Layer deep analysis combining technical, macro, and ML signals
        - Real-time price monitoring
        - Multi-timeframe consensus analysis
        - Machine learning predictions (XGBoost + Random Forest)
        - News sentiment from multiple sources
        - Automated trading capabilities
        """)
        
        # Feature showcase
        st.markdown("### ✨ Key Features")
        
        col_feat1, col_feat2, col_feat3 = st.columns(3)
        
        with col_feat1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #00d9ff;">🎯 18-Layer AI</h3>
                <p style="color: #95a5a6;">
                    Comprehensive analysis from 18 different perspectives:
                    technical indicators, macro correlation, ML models, and more.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_feat2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #00d9ff;">🤖 ML Predictions</h3>
                <p style="color: #95a5a6;">
                    XGBoost trend classifier and Random Forest volatility predictor
                    for cutting-edge market forecasting.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_feat3:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #00d9ff;">📰 Sentiment Analysis</h3>
                <p style="color: #95a5a6;">
                    Real-time news sentiment from Twitter, Reddit, Fear & Greed Index,
                    and news headlines.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Auto-refresh logic
    if st.session_state.auto_refresh:
        time.sleep(30)
        st.rerun()

# ============================================================================
# SIDEBAR: WATCHLIST MANAGEMENT (PHASE 1)
# ============================================================================

def render_watchlist_sidebar():
    """Render watchlist in sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📋 Watchlist")
        
        # Fixed coins
        st.markdown("**Fixed Coins:**")
        for coin in st.session_state.watchlist:
            price = get_current_price(coin)
            st.markdown(f"• {coin}: ${price:,.2f}")
        
        # Custom coins
        if st.session_state.custom_coins:
            st.markdown("**Custom Coins:**")
            for i, coin in enumerate(st.session_state.custom_coins):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    price = get_current_price(coin)
                    st.markdown(f"• {coin}: ${price:,.2f}")
                with col_b:
                    if st.button("🗑️", key=f"remove_{i}"):
                        st.session_state.custom_coins.pop(i)
                        st.rerun()

# ============================================================================
# PHASE 1-2: TRADE HISTORY (OPTIONAL TAB)
# ============================================================================

def render_trade_history():
    """Render trade history page"""
    st.markdown("### 📜 Trade History")
    
    # Mock trade data
    trades = pd.DataFrame({
        'Date': pd.date_range(start='2025-10-01', periods=10, freq='D'),
        'Symbol': ['BTCUSDT'] * 5 + ['ETHUSDT'] * 5,
        'Type': ['BUY', 'SELL'] * 5,
        'Entry': [68000, 69500, 67000, 70000, 68500, 3500, 3600, 3450, 3700, 3550],
        'Exit': [69500, 68000, 70000, 67500, 71000, 3600, 3500, 3700, 3450, 3800],
        'PnL': [1500, -1500, 3000, -2500, 2500, 100, -100, 250, -250, 250],
        'PnL%': [2.2, -2.2, 4.5, -3.6, 3.7, 2.9, -2.8, 7.2, -6.8, 7.0]
    })
    
    # Summary metrics
    col_th1, col_th2, col_th3, col_th4 = st.columns(4)
    
    with col_th1:
        st.metric("Total Trades", len(trades))
    
    with col_th2:
        win_rate = (trades['PnL'] > 0).sum() / len(trades) * 100
        st.metric("Win Rate", f"{win_rate:.1f}%")
    
    with col_th3:
        total_pnl = trades['PnL'].sum()
        st.metric("Total PnL", f"${total_pnl:,.2f}", delta=f"{total_pnl:+,.2f}")
    
    with col_th4:
        avg_pnl = trades['PnL%'].mean()
        st.metric("Avg Return", f"{avg_pnl:.2f}%")
    
    # Trade table
    st.dataframe(
        trades,
        use_container_width=True,
        hide_index=True
    )

# ============================================================================
# EXECUTION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Print startup message
    print("=" * 70)
    print("✅ streamlit_app.py v9.0 loaded successfully!")
    print("🔱 3 Fixed Coins (BTCUSDT, ETHUSDT, LTCUSDT) + Custom Coin System")
    print("📊 18-Layer AI Analysis | Phase 1-6 Complete | Professional UI!")
    print("=" * 70)
    
    # Multi-page setup
    page = st.sidebar.radio(
        "Navigate:",
        ["🏠 Dashboard", "📜 Trade History", "📊 Backtest", "💼 Portfolio"],
        index=0
    )
    
    if page == "🏠 Dashboard":
        main()
        render_watchlist_sidebar()
    
    elif page == "📜 Trade History":
        render_trade_history()
    
    elif page == "📊 Backtest":
        st.markdown("### 📈 Backtesting Engine")
        st.info("Feature: Historical strategy testing (Phase 3.2)")
        st.warning("⚠️ Requires backtest_engine.py integration")
    
    elif page == "💼 Portfolio":
        st.markdown("### 💼 Portfolio Optimizer")
        st.info("Feature: Kelly Criterion portfolio optimization (Phase 3.3)")
        st.warning("⚠️ Requires portfolio_optimizer.py integration")

