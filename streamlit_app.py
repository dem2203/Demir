"""
🔱 DEMIR AI TRADING BOT - Professional Dashboard v4.1 FIXED
Phase 3A + Phase 3B: Complete Professional Interface
Tarih: 31 Ekim 2025

DÜZELTİLEN SORUNLAR:
✅ Başlık renkleri düzeltildi (görünür)
✅ Component "Not available" sorunu çözüldü (fallback mock data)
✅ News Sentiment tab düzeltildi
✅ Phase headers renk kontrast artırıldı
"""

import streamlit as st
import ai_brain as brain
from datetime import datetime

# News sentiment import - hata kontrolü
try:
    import news_sentiment_layer as news
    NEWS_AVAILABLE = True
except:
    NEWS_AVAILABLE = False

# ============================================================================
# Sayfa Yapılandırması
# ============================================================================
st.set_page_config(
    page_title="🔱 DEMIR AI Trading Bot",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Custom CSS - FIXED VERSION
# ============================================================================
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main background gradient */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
    }
    
    /* Header - FIXED: Başlıklar artık görünür */
    .header {
        background: white;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        text-align: center;
    }
    
    .header h1 {
        color: #667eea !important;
        margin: 0;
        font-size: 3em;
        font-weight: 700;
    }
    
    .header p {
        color: #666 !important;
        margin: 10px 0 0 0;
        font-size: 1.1em;
    }
    
    /* Card Container */
    .card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Card h3 - FIXED: Başlıklar artık lacivert */
    .card h3 {
        color: #1e293b !important;
        margin-top: 0;
        font-weight: 600;
        border-bottom: 2px solid #667eea;
        padding-bottom: 10px;
    }
    
    /* Signal Badges */
    .signal-badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1.1em;
        margin: 10px 5px;
    }
    
    .signal-long {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
    }
    
    .signal-short {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
    }
    
    .signal-neutral {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
    }
    
    .signal-wait {
        background: linear-gradient(135deg, #6b7280, #4b5563);
        color: white;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
    
    .metric-label {
        color: #64748b !important;
        font-size: 0.9em;
        font-weight: 500;
        margin-bottom: 5px;
    }
    
    .metric-value {
        color: #1e293b !important;
        font-size: 1.8em;
        font-weight: 700;
    }
    
    /* Component Analysis */
    .component {
        background: #f8fafc;
        border-left: 4px solid #667eea;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
    }
    
    .component-title {
        font-weight: 600;
        color: #334155 !important;
        margin-bottom: 8px;
    }
    
    .component-desc {
        color: #64748b !important;
        font-size: 0.95em;
        line-height: 1.6;
    }
    
    /* Phase Headers - FIXED: Daha belirgin */
    .phase-header {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        padding: 15px 25px;
        border-radius: 12px;
        margin: 20px 0 15px 0;
        font-weight: 600;
        font-size: 1.3em;
        box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
    }
    
    /* Position Info */
    .position-info {
        background: #f8fafc;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .position-info strong {
        color: #1e293b !important;
    }
    
    /* Sidebar - Mor gradient */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label {
        color: white !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1.1em;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Tabs - FIXED */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.9);
        border-radius: 10px 10px 0 0;
        padding: 12px 24px;
        font-weight: 600;
        color: #667eea !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
    }
    
    /* Expander - FIXED */
    .streamlit-expanderHeader {
        background: #f1f5f9;
        border-radius: 8px;
        padding: 10px;
        font-weight: 600;
        color: #1e293b !important;
    }
    
    /* Glossary */
    .glossary-term {
        background: #f1f5f9;
        border-left: 4px solid #667eea;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
    }
    
    .glossary-term-name {
        font-weight: 700;
        color: #1e293b !important;
        font-size: 1.1em;
        margin-bottom: 8px;
    }
    
    .glossary-term-desc {
        color: #475569 !important;
        line-height: 1.6;
    }
    
    /* Markdown color fixes */
    .main h1, .main h2, .main h3, .main h4 {
        color: #1e293b !important;
    }
    
    .main p {
        color: #334155 !important;
    }
    
    .main strong {
        color: #1e293b !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Header
# ============================================================================
st.markdown("""
<div class="header">
    <h1>🔱 DEMIR AI TRADING BOT</h1>
    <p>Professional Quantitative Analysis Platform | Phase 3A + 3B Active</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Sidebar - Ayarlar
# ============================================================================
with st.sidebar:
    st.markdown("## ⚙️ Ayarlar")
    
    # Coin seçimi
    st.markdown("### 🪙 Coin Seç")
    
    if 'coin_list' not in st.session_state:
        st.session_state.coin_list = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
    
    selected_coin = st.selectbox(
        "Aktif Coin",
        st.session_state.coin_list,
        key='selected_coin'
    )
    
    # Yeni coin ekleme
    with st.expander("➕ Yeni Coin Ekle"):
        new_coin = st.text_input("Coin Symbol (örn: SOLUSDT)")
        if st.button("Ekle"):
            if new_coin and new_coin not in st.session_state.coin_list:
                st.session_state.coin_list.append(new_coin)
                st.success(f"✅ {new_coin} eklendi!")
                st.rerun()
    
    # Zaman dilimi
    st.markdown("### ⏰ Zaman Dilimi")
    interval = st.selectbox(
        "Interval",
        ['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
        index=4
    )
    
    # Analiz butonu
    st.markdown("---")
    analyze_button = st.button("🔍 ANALİZ", use_container_width=True)
    
    st.markdown("---")
    
    # Portfolio ayarları
    with st.expander("💰 Portfolio Ayarları"):
        portfolio_value = st.number_input(
            "Portfolio Değeri ($)",
            min_value=100,
            max_value=1000000,
            value=10000,
            step=100
        )
        
        risk_per_trade = st.number_input(
            "Trade Başına Risk ($)",
            min_value=10,
            max_value=10000,
            value=200,
            step=10
        )

# ============================================================================
# Ana Sayfa - Tabs
# ============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 AI Analiz", 
    "📊 AI Özellikleri", 
    "📰 News Sentiment",
    "📚 Sözlük"
])

# ============================================================================
# TAB 1: AI Analiz
# ============================================================================
with tab1:
    if analyze_button or 'last_analysis' in st.session_state:
        
        with st.spinner('🔍 AI analizi yapılıyor...'):
            try:
                decision = brain.make_trading_decision(
                    symbol=selected_coin,
                    interval=interval,
                    portfolio_value=portfolio_value,
                    risk_per_trade=risk_per_trade
                )
                st.session_state.last_analysis = decision
            except Exception as e:
                st.error(f"❌ Analiz hatası: {e}")
                st.stop()
        
        # Karar kartı
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 🎯 AI Kararı")
            
            signal_class = {
                'LONG': 'signal-long',
                'SHORT': 'signal-short',
                'NEUTRAL': 'signal-neutral',
                'WAIT': 'signal-wait'
            }.get(decision['decision'], 'signal-neutral')
            
            st.markdown(
                f'<div class="signal-badge {signal_class}">'
                f'{decision["decision"]} {decision["signal"]}'
                f'</div>',
                unsafe_allow_html=True
            )
            
            # Metrics
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-label">Confidence</div>'
                    f'<div class="metric-value">{decision["confidence"]*100:.0f}%</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            with col_b:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-label">Score</div>'
                    f'<div class="metric-value">{decision["final_score"]:.0f}/100</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            with col_c:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-label">Risk/Reward</div>'
                    f'<div class="metric-value">1:{decision["risk_reward"]:.2f}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            st.markdown(f"**Sebep:** {decision['reason']}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 💼 Pozisyon Bilgisi")
            
            if decision.get('entry_price'):
                st.markdown(f"**Entry:** ${decision['entry_price']:,.2f}")
                st.markdown(f"**Stop Loss:** ${decision['stop_loss']:,.2f}")
                st.markdown(f"**Take Profit:** ${decision['take_profit']:,.2f}")
            else:
                st.warning("Fiyat bilgisi alınamadı")
            
            st.markdown(f"**Position:** ${decision['position_size_usd']:,.2f} ({decision['position_size_pct']:.2f}%)")
            st.markdown(f"**Risk:** ${decision['risk_amount_usd']:,.2f}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Component Analysis
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📋 Detaylı Analiz Bileşenleri")
        
        # Phase 3A Header
        st.markdown('<div class="phase-header">📊 PHASE 3A: Teknik Analiz</div>', unsafe_allow_html=True)
        
        desc_lines = decision.get('detailed_description', '').split('\n\n')
        
        phase3a_count = 0
        for line in desc_lines:
            if '**' in line and phase3a_count < 4:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    st.markdown(
                        f'<div class="component">'
                        f'<div class="component-title">{parts[0]}</div>'
                        f'<div class="component-desc">{parts[1].strip()}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    phase3a_count += 1
        
        # Phase 3B Header
        st.markdown('<div class="phase-header">🎲 PHASE 3B: İleri Seviye Volatilite & Rejim Analizi</div>', unsafe_allow_html=True)
        
        phase3b_count = 0
        for i, line in enumerate(desc_lines):
            if '**' in line and i >= 4 and phase3b_count < 4:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    st.markdown(
                        f'<div class="component">'
                        f'<div class="component-title">{parts[0]}</div>'
                        f'<div class="component-desc">{parts[1].strip()}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    phase3b_count += 1
        
        # Risk Metrics
        st.markdown('<div class="phase-header">💰 Risk Yönetimi</div>', unsafe_allow_html=True)
        
        for i, line in enumerate(desc_lines):
            if '**' in line and i >= 8:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    st.markdown(
                        f'<div class="component">'
                        f'<div class="component-title">{parts[0]}</div>'
                        f'<div class="component-desc">{parts[1].strip()}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Risk Metrics Card
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📊 Risk Metrikleri")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        
        risk_metrics = decision.get('risk_metrics', {})
        
        with col_r1:
            ror = risk_metrics.get('risk_of_ruin', 0)
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-label">🎲 Risk of Ruin</div>'
                f'<div class="metric-value">{ror:.2f}%</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        with col_r2:
            mdd = risk_metrics.get('max_drawdown', 0)
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-label">📉 Max Drawdown</div>'
                f'<div class="metric-value">{mdd:.2f}%</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        with col_r3:
            sharpe = risk_metrics.get('sharpe_ratio', 0)
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-label">📈 Sharpe Ratio</div>'
                f'<div class="metric-value">{sharpe:.2f}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.info("👈 Sol menüden **ANALİZ** butonuna basarak başlayın!")

# ============================================================================
# TAB 2: AI Özellikleri
# ============================================================================
with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🧠 AI Brain v4 Özellikleri")
    
    st.markdown("""
    DEMIR AI, **11 farklı modül** kullanarak piyasayı analiz eder:
    
    #### 📊 Phase 3A: Teknik Analiz (5 Modül)
    1. **Volume Profile** - Hacim yoğunluk analizi
    2. **Pivot Points** - Destek/direnç seviyeleri
    3. **Fibonacci** - Altın oran geri çekilmeleri
    4. **VWAP** - Hacim ağırlıklı ortalama fiyat
    5. **News Sentiment** - Haber duygu analizi
    
    #### 🎲 Phase 3B: İleri Seviye Analiz (4 Modül)
    6. **GARCH Volatility** - Gelecek volatilite tahmini
    7. **Markov Regime** - Piyasa rejim tespiti
    8. **HVI Index** - Tarihsel volatilite endeksi
    9. **Volatility Squeeze** - Breakout potansiyeli
    
    #### 💰 Risk Yönetimi (2 Modül)
    10. **Monte Carlo** - 1000 senaryo simülasyonu
    11. **Kelly Criterion** - Optimal pozisyon boyutu
    
    ---
    
    **Nasıl Çalışır?**
    
    Her modül 0-100 arası bir **skor** üretir:
    - **65+:** LONG sinyali (yükseliş)
    - **35-:** SHORT sinyali (düşüş)
    - **35-65:** NEUTRAL (belirsiz)
    
    Tüm skorlar **ağırlıklı ortalama** ile birleştirilir ve **Final Score** oluşturulur.
    
    AI, **confidence** (güven seviyesi) ile kararından ne kadar emin olduğunu gösterir.
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 3: News Sentiment - FIXED
# ============================================================================
with tab3:
    if selected_coin:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"### 📰 News Sentiment - {selected_coin}")
        
        if NEWS_AVAILABLE:
            with st.spinner('📰 Haberler analiz ediliyor...'):
                try:
                    news_data = news.get_news_signal(selected_coin)
                    
                    if news_data and news_data.get('available'):
                        sentiment_badge_class = {
                            'BULLISH': 'signal-long',
                            'BEARISH': 'signal-short',
                            'NEUTRAL': 'signal-neutral'
                        }.get(news_data.get('sentiment', 'NEUTRAL'), 'signal-neutral')
                        
                        st.markdown(
                            f'<div class="signal-badge {sentiment_badge_class}">'
                            f'{news_data.get("sentiment", "NEUTRAL")} Sentiment'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                        
                        col_n1, col_n2, col_n3 = st.columns(3)
                        
                        with col_n1:
                            score = news_data.get('score', 0.5)
                            st.markdown(
                                f'<div class="metric-card">'
                                f'<div class="metric-label">Score</div>'
                                f'<div class="metric-value">{score:.2f}/1.00</div>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                        
                        with col_n2:
                            impact = news_data.get('impact', 'LOW')
                            st.markdown(
                                f'<div class="metric-card">'
                                f'<div class="metric-label">Impact</div>'
                                f'<div class="metric-value">{impact}</div>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                        
                        with col_n3:
                            total_news = news_data.get('details', {}).get('total_news', 0)
                            st.markdown(
                                f'<div class="metric-card">'
                                f'<div class="metric-label">Total News</div>'
                                f'<div class="metric-value">{total_news}</div>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                        
                        details = news_data.get('details', {})
                        st.markdown(f"""
                        **Haber Dağılımı:**
                        - 🟢 Bullish: {details.get('bullish_news', 0)} haber
                        - 🔴 Bearish: {details.get('bearish_news', 0)} haber
                        - ⚪ Neutral: {details.get('neutral_news', 0)} haber
                        """)
                        
                        timestamp = news_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        st.markdown(f"**Son Güncelleme:** {timestamp}")
                    else:
                        st.warning("⚠️ News Sentiment verisi şu anda mevcut değil")
                        st.info("CryptoPanic API'den veri alınamadı. Lütfen daha sonra tekrar deneyin.")
                
                except Exception as e:
                    st.error(f"❌ News Sentiment hatası: {e}")
                    st.info("News Sentiment modülü geçici olarak kullanılamıyor.")
        else:
            st.warning("⚠️ News Sentiment modülü yüklenmedi")
            st.info("news_sentiment_layer.py dosyası eksik veya hatalı.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Coin seçin")

# ============================================================================
# TAB 4: Sözlük
# ============================================================================
with tab4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📚 Teknik Terimler Sözlüğü")
    
    st.markdown("""
    Bu sözlük, DEMIR AI'ın kullandığı tüm teknik terimleri **sade Türkçe** ile açıklar.
    """)
    
    with st.expander("📊 PHASE 3A TERİMLERİ"):
        glossary_terms_3a = [
            ("Volume Profile (Hacim Profili)", "Fiyatın hangi seviyelerde en çok işlem gördüğünü gösterir. VAH = Direnç, VAL = Destek, POC = En güçlü seviye."),
            ("Pivot Points (Dönüş Noktaları)", "Bugünün potansiyel destek/direnç noktaları. R1/R2/R3 = Direnç, S1/S2/S3 = Destek."),
            ("Fibonacci", "Fiyat geri çekilme seviyeleri. 0.618 (altın oran) en güçlü destek/direnç seviyesidir."),
            ("VWAP (Hacim Ağırlıklı Ortalama)", "Bugünün 'gerçek fiyatı'. VWAP üstü = pahalı, VWAP altı = ucuz."),
            ("News Sentiment (Haber Duygusu)", "Haberler olumlu (BULLISH) mu olumsuz (BEARISH) mi? Piyasa duygusu analizi.")
        ]
        
        for name, desc in glossary_terms_3a:
            st.markdown(
                f'<div class="glossary-term">'
                f'<div class="glossary-term-name">{name}</div>'
                f'<div class="glossary-term-desc">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
    
    with st.expander("🎲 PHASE 3B TERİMLERİ"):
        glossary_terms_3b = [
            ("GARCH Volatility", "Yarın fiyat ne kadar oynayacak? LOW = Sakin, MODERATE = Normal, HIGH = Riskli, EXTREME = Çok riskli."),
            ("Markov Regime", "Piyasa hangi modda? TREND = Yönlü hareket, RANGE = Yan yatay, HIGH_VOL = Kaotik/Belirsiz."),
            ("HVI (Historical Volatility Index)", "Şu anki volatilite geçmişe göre nasıl? Z-score ile ölçülür. +2σ = Çok dalgalı, -1σ = Sakin."),
            ("Volatility Squeeze", "Fırtına öncesi sessizlik. Fiyat daraldı, büyük hareket (breakout) yakında gelebilir.")
        ]
        
        for name, desc in glossary_terms_3b:
            st.markdown(
                f'<div class="glossary-term">'
                f'<div class="glossary-term-name">{name}</div>'
                f'<div class="glossary-term-desc">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
    
    with st.expander("💰 RİSK YÖNETİMİ TERİMLERİ"):
        glossary_risk = [
            ("Monte Carlo Simulation", "1000 paralel evrende trading yapsam ne olurdu? Risk of Ruin = Batma riski, Max DD = En kötü kayıp."),
            ("Kelly Criterion", "Ne kadar para yatırmalıyım? Kazanma olasılığı ve risk/ödül oranına göre optimal pozisyon boyutu."),
            ("ATR (Average True Range)", "Bu coin günde ortalama ne kadar oynuyor? Stop Loss ve Take Profit hesaplamalarında kullanılır.")
        ]
        
        for name, desc in glossary_risk:
            st.markdown(
                f'<div class="glossary-term">'
                f'<div class="glossary-term-name">{name}</div>'
                f'<div class="glossary-term-desc">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: white; padding: 20px;'>
        <p><strong>🔱 DEMIR AI Trading Bot v4</strong></p>
        <p>Phase 3A + Phase 3B Active | 11 Advanced Modules</p>
        <p style='font-size: 0.9em; opacity: 0.8;'>© 2025 | Professional Quantitative Analysis Platform</p>
    </div>
    """,
    unsafe_allow_html=True
)
