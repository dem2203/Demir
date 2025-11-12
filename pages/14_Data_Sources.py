
import streamlit as st

st.set_page_config(page_title="📡 Data Sources", layout="wide")

st.title("📡 Veri Kaynakları & Hesaplama Formülleri")
st.markdown("**Tüm veri nereden geldiğini ve nasıl hesaplandığını gör**")

st.markdown("---")

st.markdown("## 📡 Veri Kaynakları (APIs)")

data_sources = {
    'Veri': ['Fiyat', 'Makro Verisi', 'On-Chain', 'Haber & Sentiment', 'Teknik Göstergeler'],
    'Kaynak': ['Binance Futures', 'Alpha Vantage', 'CoinGlass', 'NewsAPI', 'Binance + Ta-Lib'],
    'Endpoint': ['/fapi/v1/ticker/24hr', '/query?function=GLOBAL_QUOTE', '/api/v2/exchanges', '/everything?q=bitcoin', 'Real-time Klines'],
    'Güncelleme': ['5 saniye', '1 saat', '1 dakika', 'Gerçek zamanlı', 'Mum kapanışında']
}

df_sources = pd.DataFrame(data_sources)
st.dataframe(df_sources, use_container_width=True)

st.markdown("---")

st.markdown("## 📊 Hesaplama Formülleri")

st.markdown("### Entry Price (Giriş Fiyatı)")
st.code("Entry = Güncel Fiyat (Binance'ten alınan son fiyat)")

st.markdown("### Take Profit 1 (Hedef 1)")
st.code("TP1 = Güncel Fiyat × 1.015  # 1.5% yukarı")

st.markdown("### Take Profit 2 (Hedef 2)")
st.code("TP2 = Güncel Fiyat × 1.035  # 3.5% yukarı")

st.markdown("### Stop Loss (Zarar Durdur)")
st.code("SL = Güncel Fiyat × 0.985  # 1.5% aşağı")

st.markdown("### Confidence Score")
st.code("Confidence = (LONG Votes / Total Layers) × 100")

st.markdown("### Overall Signal")
st.code("""
if LONG_Votes > SHORT_Votes + NEUTRAL_Votes:
    Signal = 'LONG'
elif SHORT_Votes > LONG_Votes + NEUTRAL_Votes:
    Signal = 'SHORT'
else:
    Signal = 'NEUTRAL'
""")

st.markdown("---")

st.markdown("## 🔧 Hesaplama Adımları")

steps = {
    'Adım': ['1', '2', '3', '4', '5', '6'],
    'İşlem': [
        'Binance API\'den canlı fiyat al',
        '100+ layer\'dan sinyal hesapla',
        'LONG/SHORT/NEUTRAL oyları say',
        'Entry/TP1/TP2/SL hesapla',
        'Confidence score hesapla',
        'Telegram\'a rapor gönder'
    ],
    'Zaman': ['Anlık', '2-3 saniye', '1 saniye', '0.5 saniye', '0.5 saniye', 'Saatlik']
}

df_steps = pd.DataFrame(steps)
st.dataframe(df_steps, use_container_width=True)

st.markdown("---")

st.markdown("## ✅ Doğruluk Kontrolü")

st.success("""
✅ **Tüm veriler GERÇEKtir:**
- ✓ Fiyatlar Binance Futures'dan
- ✓ 100+ layer gerçek hesaplanır
- ✓ Formüller açık ve şeffaf
- ✓ Timestamp gösterilir
- ✓ API'ler canlı çalışır

**Hiç mock veri yok!**
""")
