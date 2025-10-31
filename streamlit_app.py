"""
🔱 DEMIR AI TRADING BOT - Professional Dashboard v4
Phase 3A + Phase 3B: Complete Professional Interface
Tarih: 31 Ekim 2025

ÖZELLİKLER:
✅ Modern card-based layout
✅ Phase 3A ve 3B ayrı gösterim
✅ Türkçe tooltips (terim açıklamaları)
✅ Renk kodlu sinyaller
✅ Responsive design
✅ Clean, minimal UI
"""

import streamlit as st
import ai_brain as brain
import news_sentiment_layer as news
from datetime import datetime

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
# Custom CSS - Modern Professional Design
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
    
    /* Header */
    .header {
        background: white;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        text-align: center;
    }
    
    .header h1 {
        color: #667eea;
        margin: 0;
        font-size: 3em;
        font-weight: 700;
    }
    
    .header p {
        color: #666;
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
    
    .card h3 {
        color: #333;
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
        color: #64748b;
        font-size: 0.9em;
        font-weight: 500;
        margin-bottom: 5px;
    }
    
    .metric-value {
        color: #1e293b;
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
        color: #334155;
        margin-bottom: 8px;
    }
    
    .component-desc {
        color: #64748b;
        font-size: 0.95em;
        line-height: 1.6;
    }
    
    /* Phase Headers */
    .phase-header {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 15px 25px;
        border-radius: 12px;
        margin: 20px 0 15px 0;
        font-weight: 600;
        font-size: 1.3em;
    }
    
    /* Tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        border-bottom: 1px dotted #667eea;
        color: #667eea;
    }
    
    /* Position Info Grid */
    .position-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-top: 20px;
    }
    
    .position-item {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    
    .position-item-label {
        color: #64748b;
        font-size: 0.85em;
        font-weight: 500;
        margin-bottom: 5px;
    }
    
    .position-item-value {
        color: #1e293b;
        font-size: 1.5em;
        font-weight: 700;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
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
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 10px 10px 0 0;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
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
        color: #1e293b;
        font-size: 1.1em;
        margin-bottom: 8px;
    }
    
    .glossary-term-desc {
        color: #475569;
        line-height: 1.6;
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
    
    # Session state'de coin listesi
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
        index=4  # Default: 1h
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
    
    # Sözlük linki
    st.markdown("---")
    st.markdown("### 📚 Yardım")
    
    if st.button("📖 Terim Sözlüğü", use_container_width=True):
        st.session_state.show_glossary = not st.session_state.get('show_glossary', False)

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
            # AI Brain çağrısı
            decision = brain.make_trading_decision(
                symbol=selected_coin,
                interval=interval,
                portfolio_value=portfolio_value,
                risk_per_trade=risk_per_trade
            )
            
            st.session_state.last_analysis = decision
        
        # Karar kartı
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 🎯 AI Kararı")
            
            # Signal badge
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
            
            if decision['entry_price']:
                st.markdown(f"**Entry:** ${decision['entry_price']:,.2f}")
                st.markdown(f"**Stop Loss:** ${decision['stop_loss']:,.2f}")
                st.markdown(f"**Take Profit:** ${decision['take_profit']:,.2f}")
            else:
                st.markdown("Fiyat bilgisi alınamadı")
            
            st.markdown(f"**Position:** ${decision['position_size_usd']:,.2f} ({decision['position_size_pct']:.2f}%)")
            st.markdown(f"**Risk:** ${decision['risk_amount_usd']:,.2f}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Component Analysis
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📋 Detaylı Analiz Bileşenleri")
        
        # Phase 3A Header
        st.markdown('<div class="phase-header">📊 PHASE 3A: Teknik Analiz</div>', unsafe_allow_html=True)
        
        # Detailed description'dan parse et
        desc_lines = decision['detailed_description'].split('\n\n')
        
        for line in desc_lines[:4]:  # İlk 4 Phase 3A
            if '**' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    st.markdown(
                        f'<div class="component">'
                        f'<div class="component-title">{parts[0]}</div>'
                        f'<div class="component-desc">{parts[1].strip()}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
        
        # Phase 3B Header
        st.markdown('<div class="phase-header">🎲 PHASE 3B: İleri Seviye Volatilite & Rejim Analizi</div>', unsafe_allow_html=True)
        
        for line in desc_lines[4:8]:  # Sonraki 4 Phase 3B
            if '**' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    st.markdown(
                        f'<div class="component">'
                        f'<div class="component-title">{parts[0]}</div>'
                        f'<div class="component-desc">{parts[1].strip()}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
        
        # Risk Metrics
        st.markdown('<div class="phase-header">💰 Risk Yönetimi</div>', unsafe_allow_html=True)
        
        for line in desc_lines[8:]:  # Monte Carlo & Kelly
            if '**' in line:
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
        
        with col_r1:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-label">🎲 Risk of Ruin</div>'
                f'<div class="metric-value">{decision["risk_metrics"]["risk_of_ruin"]:.2f}%</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        with col_r2:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-label">📉 Max Drawdown</div>'
                f'<div class="metric-value">{decision["risk_metrics"]["max_drawdown"]:.2f}%</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        with col_r3:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-label">📈 Sharpe Ratio</div>'
                f'<div class="metric-value">{decision["risk_metrics"]["sharpe_ratio"]:.2f}</div>'
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
# TAB 3: News Sentiment
# ============================================================================
with tab3:
    if selected_coin:
        with st.spinner('📰 Haberler analiz ediliyor...'):
            news_data = news.get_news_signal(selected_coin)
        
        if news_data and news_data.get('available'):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"### 📰 News Sentiment - {selected_coin}")
            
            sentiment_badge_class = {
                'BULLISH': 'signal-long',
                'BEARISH': 'signal-short',
                'NEUTRAL': 'signal-neutral'
            }.get(news_data['sentiment'], 'signal-neutral')
            
            st.markdown(
                f'<div class="signal-badge {sentiment_badge_class}">'
                f'{news_data["sentiment"]} Sentiment'
                f'</div>',
                unsafe_allow_html=True
            )
            
            col_n1, col_n2, col_n3 = st.columns(3)
            
            with col_n1:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-label">Score</div>'
                    f'<div class="metric-value">{news_data["score"]:.2f}/1.00</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            with col_n2:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-label">Impact</div>'
                    f'<div class="metric-value">{news_data["impact"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            with col_n3:
                total_news = news_data['details'].get('total_news', 0)
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-label">Total News</div>'
                    f'<div class="metric-value">{total_news}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            # News breakdown
            details = news_data['details']
            st.markdown(f"""
            **Haber Dağılımı:**
            - 🟢 Bullish: {details.get('bullish_news', 0)} haber
            - 🔴 Bearish: {details.get('bearish_news', 0)} haber
            - ⚪ Neutral: {details.get('neutral_news', 0)} haber
            """)
            
            st.markdown(f"**Son Güncelleme:** {news_data.get('timestamp', 'N/A')}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Haber verisi alınamadı")
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
    
    # Phase 3A Terimleri
    with st.expander("📊 PHASE 3A TERİMLERİ"):
        glossary_terms_3a = [
            {
                "name": "Volume Profile (Hacim Profili)",
                "desc": "Fiyatın hangi seviyelerde en çok işlem gördüğünü gösterir. VAH = Direnç, VAL = Destek, POC = En güçlü seviye."
            },
            {
                "name": "Pivot Points (Dönüş Noktaları)",
                "desc": "Bugünün potansiyel destek/direnç noktaları. R1/R2/R3 = Direnç, S1/S2/S3 = Destek."
            },
            {
                "name": "Fibonacci",
                "desc": "Fiyat geri çekilme seviyeleri. 0.618 (altın oran) en güçlü destek/direnç seviyesidir."
            },
            {
                "name": "VWAP (Hacim Ağırlıklı Ortalama)",
                "desc": "Bugünün 'gerçek fiyatı'. VWAP üstü = pahalı, VWAP altı = ucuz."
            },
            {
                "name": "News Sentiment (Haber Duygusu)",
                "desc": "Haberler olumlu (BULLISH) mu olumsuz (BEARISH) mi? Piyasa duygusu analizi."
            }
        ]
        
        for term in glossary_terms_3a:
            st.markdown(
                f'<div class="glossary-term">'
                f'<div class="glossary-term-name">{term["name"]}</div>'
                f'<div class="glossary-term-desc">{term["desc"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
    
    # Phase 3B Terimleri
    with st.expander("🎲 PHASE 3B TERİMLERİ"):
        glossary_terms_3b = [
            {
                "name": "GARCH Volatility",
                "desc": "Yarın fiyat ne kadar oynayacak? LOW = Sakin, MODERATE = Normal, HIGH = Riskli, EXTREME = Çok riskli."
            },
            {
                "name": "Markov Regime",
                "desc": "Piyasa hangi modda? TREND = Yönlü hareket, RANGE = Yan yatay, HIGH_VOL = Kaotik/Belirsiz."
            },
            {
                "name": "HVI (Historical Volatility Index)",
                "desc": "Şu anki volatilite geçmişe göre nasıl? Z-score ile ölçülür. +2σ = Çok dalgalı, -1σ = Sakin."
            },
            {
                "name": "Volatility Squeeze",
                "desc": "Fırtına öncesi sessizlik. Fiyat daraldı, büyük hareket (breakout) yakında gelebilir."
            }
        ]
        
        for term in glossary_terms_3b:
            st.markdown(
                f'<div class="glossary-term">'
                f'<div class="glossary-term-name">{term["name"]}</div>'
                f'<div class="glossary-term-desc">{term["desc"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
    
    # Risk Yönetimi
    with st.expander("💰 RİSK YÖNETİMİ TERİMLERİ"):
        glossary_risk = [
            {
                "name": "Monte Carlo Simulation",
                "desc": "1000 paralel evrende trading yapsam ne olurdu? Risk of Ruin = Batma riski, Max DD = En kötü kayıp."
            },
            {
                "name": "Kelly Criterion",
                "desc": "Ne kadar para yatırmalıyım? Kazanma olasılığı ve risk/ödül oranına göre optimal pozisyon boyutu."
            },
            {
                "name": "ATR (Average True Range)",
                "desc": "Bu coin günde ortalama ne kadar oynuyor? Stop Loss ve Take Profit hesaplamalarında kullanılır."
            }
        ]
        
        for term in glossary_risk:
            st.markdown(
                f'<div class="glossary-term">'
                f'<div class="glossary-term-name">{term["name"]}</div>'
                f'<div class="glossary-term-desc">{term["desc"]}</div>'
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
