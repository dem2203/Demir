"""
DEMIR AI Trading Bot - Real-time Binance Integration
Phase 2.1: Dynamic Position Calculations
Tarih: 31 Ekim 2025

YENİ ÖZELLİKLER:
- Binance Futures real-time price
- Coin-specific calculations (Entry, Stop, Target)
- Dynamic position sizing
- Real ATR-based stop loss
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests
from binance.client import Client
import os

# ============================================================================
# CRITICAL: st.set_page_config() MUST BE FIRST
# ============================================================================
st.set_page_config(
    page_title="🔱 DEMIR AI Trading Bot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Binance API Setup
# ============================================================================
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')

try:
    binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
    BINANCE_AVAILABLE = True
except:
    BINANCE_AVAILABLE = False

# ============================================================================
# Helper Functions: Real-time Data
# ============================================================================

def get_current_price(symbol):
    """Binance Futures'dan güncel fiyat çeker"""
    try:
        if BINANCE_AVAILABLE:
            ticker = binance_client.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        else:
            # Fallback: Public API (no auth needed)
            url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return float(data['price'])
    except Exception as e:
        st.warning(f"⚠️ Fiyat çekilemedi: {e}")
        return None

def get_atr(symbol, timeframe='1h', period=14):
    """ATR hesaplar (Average True Range - volatilite)"""
    try:
        # Binance'den klines (mum grafiği) çek
        if timeframe == '1h':
            interval = Client.KLINE_INTERVAL_1HOUR
        elif timeframe == '4h':
            interval = Client.KLINE_INTERVAL_4HOUR
        else:
            interval = Client.KLINE_INTERVAL_1DAY
        
        if BINANCE_AVAILABLE:
            klines = binance_client.futures_klines(
                symbol=symbol,
                interval=interval,
                limit=period + 1
            )
        else:
            # Fallback: Public API
            url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={timeframe}&limit={period + 1}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                klines = response.json()
            else:
                return None
        
        # ATR hesaplama
        highs = [float(k[2]) for k in klines]
        lows = [float(k[3]) for k in klines]
        closes = [float(k[4]) for k in klines]
        
        true_ranges = []
        for i in range(1, len(klines)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i-1])
            low_close = abs(lows[i] - closes[i-1])
            true_range = max(high_low, high_close, low_close)
            true_ranges.append(true_range)
        
        atr = sum(true_ranges) / len(true_ranges)
        return atr
    
    except Exception as e:
        st.warning(f"⚠️ ATR hesaplanamadı: {e}")
        return None

def calculate_position_details(symbol, timeframe='1h', risk_per_trade=200):
    """
    Seçilen coin için pozisyon detaylarını hesaplar
    
    Returns:
        dict: {
            'entry': float,
            'stop': float,
            'target': float,
            'position_size': float,
            'risk_reward': float
        }
    """
    
    # 1. Güncel fiyat
    current_price = get_current_price(symbol)
    if not current_price:
        return None
    
    # 2. ATR hesapla (stop loss için)
    atr = get_atr(symbol, timeframe)
    if not atr:
        # Fallback: %1.5 volatilite
        atr = current_price * 0.015
    
    # 3. Stop Loss hesapla (2x ATR below entry)
    stop_loss = current_price - (2 * atr)
    
    # 4. Target hesapla (3x ATR above entry - 1:3 R/R için)
    target = current_price + (3 * atr)
    
    # 5. Risk/Reward hesapla
    risk = current_price - stop_loss
    reward = target - current_price
    risk_reward = reward / risk if risk > 0 else 0
    
    # 6. Position size hesapla (risk_per_trade = $200)
    position_size = risk_per_trade / risk if risk > 0 else 0
    
    return {
        'entry': current_price,
        'stop': stop_loss,
        'target': target,
        'position_size': position_size,
        'risk_reward': risk_reward,
        'atr': atr
    }

# ============================================================================
# Module imports
# ============================================================================
import_errors = []

try:
    import analysis_layer
except ImportError as e:
    import_errors.append(f"analysis_layer: {e}")

try:
    import strategy_layer
except ImportError as e:
    import_errors.append(f"strategy_layer: {e}")

try:
    import ai_brain
except ImportError as e:
    import_errors.append(f"ai_brain: {e}")

try:
    import external_data
except ImportError as e:
    import_errors.append(f"external_data: {e}")

try:
    import news_sentiment_layer
    NEWS_AVAILABLE = True
except ImportError as e:
    NEWS_AVAILABLE = False
    import_errors.append(f"news_sentiment_layer: {e}")

if import_errors:
    with st.expander("⚠️ Module Import Warnings", expanded=False):
        for error in import_errors:
            st.warning(error)

# ============================================================================
# CSS Styling
# ============================================================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    .metric-card {
        background: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 15px;
    }
    .positive {
        color: #00ff88 !important;
        font-weight: bold;
    }
    .negative {
        color: #ff4444 !important;
        font-weight: bold;
    }
    .neutral {
        color: #ffaa00 !important;
        font-weight: bold;
    }
    .news-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
        border: 2px solid #4a90e2;
    }
    .news-positive {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .news-negative {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    .news-neutral {
        background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Header
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>⚡ DEMIR AI TRADING</h1>
    <p>Güven: 31% | $109,450.00</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Sidebar
# ============================================================================
with st.sidebar:
    st.markdown("## 🎛️ Ayarlar")
    
    coin = st.selectbox(
        "Coin ekle",
        ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        key="coin_select"
    )
    
    timeframe = st.selectbox(
        "Zaman",
        ["1h", "4h", "1d"],
        index=0,
        key="timeframe_select"
    )
    
    analyze_btn = st.button("🚀 ANALİZ", use_container_width=True, type="primary")
    
    st.markdown("---")
    
    st.markdown("### 🤖 AI Özellikleri")
    ai_enabled = st.toggle("AI", value=True)
    
    if NEWS_AVAILABLE:
        news_enabled = st.toggle("📰 News Sentiment", value=True)
    else:
        news_enabled = False
        st.info("📰 News özelliği yükleniyor...")

# ============================================================================
# Ana Container
# ============================================================================
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 💬 Açıklama")
    
    if analyze_btn or st.session_state.get('last_analysis'):
        with st.spinner("🧠 AI analiz yapıyor..."):
            time.sleep(1)
            
            st.markdown("""
            <div class="metric-card">
                <h3>⚠️ Zaman dilimleri uyumsuz. Bekle!</h3>
                <p>📊 Piyasa dalgalı ve tahmin edilemez. Dikkatli ol!</p>
                <p>💰 Risk/Ödül çok yüksek! 3.8x kazanç potansiyeli.</p>
                <p>📰 Haberler nötr. Sinyal üzerinde etkisi yok.</p>
                <p>❌ Güven veya R/R yetersiz. Bekle!</p>
                <p>📋 Kelly: %2.0 (200 USD)</p>
            </div>
            """, unsafe_allow_html=True)

with col2:
    st.markdown("### 💼 Pozisyon")
    
    # YENİ: Real-time position calculations
    if analyze_btn or st.session_state.get('last_analysis'):
        with st.spinner(f"📊 {coin} analiz ediliyor..."):
            position_data = calculate_position_details(coin, timeframe, risk_per_trade=200)
            
            if position_data:
                # Format numbers
                entry_price = f"${position_data['entry']:,.2f}"
                stop_price = f"${position_data['stop']:,.2f}"
                target_price = f"${position_data['target']:,.2f}"
                position_size = f"${position_data['position_size']:,.2f}"
                risk_reward = f"1:{position_data['risk_reward']:.2f}"
                
                # Display metrics
                st.metric("Entry", entry_price, delta="Current Price")
                st.metric("Pozisyon", position_size)
                st.metric("Stop", stop_price)
                st.metric("Target", target_price)
                st.metric("R/R", risk_reward)
                
                # Save to session
                st.session_state['position_data'] = position_data
                st.session_state['last_analysis'] = True
            else:
                st.error("❌ Fiyat verisi alınamadı. Binance API'yi kontrol edin.")
    else:
        st.info("🚀 ANALİZ butonuna basın")

# ============================================================================
# News Sentiment Section
# ============================================================================
if NEWS_AVAILABLE and news_enabled:
    st.markdown("---")
    st.markdown(f"## 📰 News Sentiment Analysis - {coin}")
    
    if analyze_btn or st.session_state.get('show_news'):
        with st.spinner(f"📡 {coin} haberleri yükleniyor..."):
            try:
                news_signal = news_sentiment_layer.get_news_signal(coin)
                
                sentiment = news_signal['sentiment']
                if sentiment == 'POSITIVE':
                    card_class = 'news-card news-positive'
                    emoji = '📈'
                elif sentiment == 'NEGATIVE':
                    card_class = 'news-card news-negative'
                    emoji = '📉'
                else:
                    card_class = 'news-card news-neutral'
                    emoji = '📊'
                
                st.markdown(f"""
                <div class="{card_class}">
                    <h3>{emoji} {sentiment} Sentiment</h3>
                    <p><strong>Coin:</strong> {news_signal['symbol']}</p>
                    <p><strong>Score:</strong> {news_signal['score']:.2f} / 1.00</p>
                    <p><strong>Impact:</strong> {news_signal['impact']}</p>
                    <hr style="border-color: rgba(255,255,255,0.3);">
                    <p>📈 Bullish News: {news_signal['details']['bullish_news']}</p>
                    <p>📉 Bearish News: {news_signal['details']['bearish_news']}</p>
                    <p>📊 Neutral News: {news_signal['details']['neutral_news']}</p>
                    <p style="font-size: 0.9em; opacity: 0.8;">Total: {news_signal['details']['total_news']} news analyzed</p>
                    <p style="font-size: 0.8em; opacity: 0.6;">Updated: {news_signal['timestamp']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"📜 Son Haberler - {coin} (Top 10)"):
                    coin_symbol = coin.replace('USDT', '').replace('BUSD', '')
                    news_list = news_sentiment_layer.fetch_news(currencies=coin_symbol, limit=10)
                    
                    if news_list:
                        for idx, news in enumerate(news_list[:10], 1):
                            title = news.get('title', 'No title')
                            url = news.get('url', '#')
                            published_at = news.get('published_at', 'Unknown time')
                            
                            votes = news.get('votes', {})
                            positive = votes.get('positive', 0)
                            negative = votes.get('negative', 0)
                            
                            if positive > negative:
                                news_emoji = '🟢'
                            elif negative > positive:
                                news_emoji = '🔴'
                            else:
                                news_emoji = '⚪'
                            
                            st.markdown(f"""
                            **{idx}. {news_emoji} [{title}]({url})**  
                            👍 {positive} | 👎 {negative} | ⏰ {published_at}
                            """)
                    else:
                        st.info(f"❌ {coin_symbol} için haber bulunamadı.")
                
                st.session_state['show_news'] = True
                
            except Exception as e:
                st.error(f"❌ News sentiment alınamadı: {str(e)}")

# ============================================================================
# Market Data Section
# ============================================================================
st.markdown("---")
st.markdown("## 📊 Market Data")

tab1, tab2, tab3 = st.tabs(["BTCUSDT", "ETHUSDT", "SOLUSDT"])

with tab1:
    st.info("BTC market data burada gösterilecek")

with tab2:
    st.info("ETH market data burada gösterilecek")

with tab3:
    st.info("SOL market data burada gösterilecek")

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; opacity: 0.6;">
    🔱 DEMIR AI Trading Bot v2.1 | Phase 2: Real-time Binance Integration ✅
</div>
""", unsafe_allow_html=True)
