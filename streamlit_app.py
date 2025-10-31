"""
DEMIR AI Trading Bot - Streamlit Dashboard
Phase 2 UPDATE: News Sentiment Integration
Tarih: 31 Ekim 2025

GÜNCELLEMELER:
- News Sentiment bölümü eklendi
- CryptoPanic API entegrasyonu
- Real-time haber analizi
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Mevcut modüller
try:
    import analysis_layer
    import strategy_layer
    import ai_brain
    import external_data
except ImportError as e:
    st.error(f"⚠️ Modül yüklenemedi: {e}")

# YENİ: News Sentiment modülü
try:
    import news_sentiment_layer
    NEWS_AVAILABLE = True
except ImportError:
    NEWS_AVAILABLE = False
    st.warning("⚠️ News Sentiment modülü yüklenemedi. Phase 2 özellikleri devre dışı.")


# Sayfa yapılandırması
st.set_page_config(
    page_title="🔱 DEMIR AI Trading Bot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling
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
    /* YENİ: News Sentiment Styling */
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

# Header
st.markdown("""
<div class="main-header">
    <h1>⚡ DEMIR AI TRADING</h1>
    <p>Güven: 31% | $109,450.00</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🎛️ Ayarlar")
    
    # Coin seçimi
    coin = st.selectbox(
        "Coin ekle",
        ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        key="coin_select"
    )
    
    # Zaman dilimi
    timeframe = st.selectbox(
        "Zaman",
        ["1h", "4h", "1d"],
        index=0,
        key="timeframe_select"
    )
    
    # Analiz butonu
    analyze_btn = st.button("🚀 ANALİZ", use_container_width=True, type="primary")
    
    st.markdown("---")
    
    # AI Toggle (YENİ: News dahil)
    st.markdown("### 🤖 AI Özellikleri")
    ai_enabled = st.toggle("AI", value=True)
    
    # YENİ: News Sentiment Toggle
    if NEWS_AVAILABLE:
        news_enabled = st.toggle("📰 News Sentiment", value=True)
    else:
        news_enabled = False
        st.info("📰 News özelliği Phase 2'de aktif olacak")

# Ana container
col1, col2 = st.columns([2, 1])

with col1:
    # AI Recommendation Card (Mevcut)
    st.markdown("### 💬 Açıklama")
    
    if analyze_btn or st.session_state.get('last_analysis'):
        with st.spinner("🧠 AI analiz yapıyor..."):
            time.sleep(1)  # Simülasyon
            
            # Mock AI response (gerçek analiziniz buraya gelecek)
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
    # Position Details (Mevcut)
    st.markdown("### 💼 Pozisyon")
    
    st.metric("Pozisyon", "$200")
    st.metric("Stop", "$108324.00")
    st.metric("Target", "$113752.81")
    st.metric("R/R", "1:3.82")

# YENİ: News Sentiment Section
if NEWS_AVAILABLE and news_enabled:
    st.markdown("---")
    st.markdown("## 📰 News Sentiment Analysis")
    
    # News verisini çek
    if analyze_btn or st.session_state.get('show_news'):
        with st.spinner("📡 Haberler yükleniyor..."):
            try:
                # News sentiment sinyali al
                news_signal = news_sentiment_layer.get_news_signal(coin)
                
                # Sentiment'e göre renk seç
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
                
                # News kartı göster
                st.markdown(f"""
                <div class="{card_class}">
                    <h3>{emoji} {sentiment} Sentiment</h3>
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
                
                # Detaylı haber listesi (opsiyonel - genişletilebilir)
                with st.expander("📜 Son Haberler (Top 10)"):
                    coin_symbol = coin.replace('USDT', '')
                    news_list = news_sentiment_layer.fetch_news(currencies=coin_symbol, limit=10)
                    
                    if news_list:
                        for idx, news in enumerate(news_list[:10], 1):
                            title = news.get('title', 'No title')
                            url = news.get('url', '#')
                            published_at = news.get('published_at', 'Unknown time')
                            
                            votes = news.get('votes', {})
                            positive = votes.get('positive', 0)
                            negative = votes.get('negative', 0)
                            
                            # Sentiment emoji
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
                        st.info("Haber bulunamadı.")
                
                st.session_state['show_news'] = True
                
            except Exception as e:
                st.error(f"❌ News sentiment alınamadı: {str(e)}")

# Market Data Section (Mevcut - değişiklik yok)
st.markdown("---")
st.markdown("## 📊 Market Data")

# Tabs
tab1, tab2, tab3 = st.tabs(["BTCUSDT", "ETHUSDT", "SOLUSDT"])

with tab1:
    st.info("BTC market data burada gösterilecek")

with tab2:
    st.info("ETH market data burada gösterilecek")

with tab3:
    st.info("SOL market data burada gösterilecek")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; opacity: 0.6;">
    🔱 DEMIR AI Trading Bot v2.0 | Phase 2: News Sentiment Integration ✅
</div>
""", unsafe_allow_html=True)
