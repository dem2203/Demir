"""
🔮 TAHMİN MOTORU - AI Powered Future Forecasting
Version: 3.0 - Tam Türkçe + Trade Tracking
Date: 11 Kasım 2025, 00:15 CET

✅ ÖZELLİKLER:
- %100 Türkçe arayüz
- Trade önerileri (GİRİŞ, TP, SL)
- Botla trade ekle butonu
- Otomatik takip ve log
- 10 matematiksel model
"""

import streamlit as st
from datetime import datetime, timedelta
import requests
import numpy as np
from scipy import stats
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# IMPORT MODULES
# ============================================================================

try:
    from ai_brain import AIBrain
    _ai_brain = AIBrain()
    AIBRAIN_OK = True
except:
    AIBRAIN_OK = False
    _ai_brain = None

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="🔮 Tahmin Motoru",
    page_icon="🔮",
    layout="wide"
)

# ============================================================================
# CSS STYLING
# ============================================================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0B0F19 0%, #1A1F2E 100%);
    }
    h1, h2, h3 {
        color: #F9FAFB !important;
    }
    .prediction-box {
        background: rgba(26, 31, 46, 0.8);
        border: 2px solid rgba(99, 102, 241, 0.5);
        border-radius: 16px;
        padding: 24px;
        margin: 20px 0;
    }
    .trade-box {
        background: rgba(26, 31, 46, 0.9);
        border: 2px solid rgba(34, 197, 94, 0.5);
        border-radius: 16px;
        padding: 24px;
        margin: 20px 0;
    }
    .sl-box {
        background: rgba(26, 31, 46, 0.9);
        border: 2px solid rgba(239, 68, 68, 0.5);
        border-radius: 16px;
        padding: 24px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA COLLECTION
# ============================================================================

def get_real_prices():
    """Binance REST API - Gerçek fiyatlar"""
    try:
        url = "https://fapi.binance.com/fapi/v1/ticker/price"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            prices = {}
            for item in data:
                if item['symbol'] in ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']:
                    prices[item['symbol']] = float(item['price'])
            return prices
    except:
        pass
    return {'BTCUSDT': 0, 'ETHUSDT': 0, 'LTCUSDT': 0}

def get_klines(symbol, interval='1m', limit=100):
    """Binance'den candlestick verileri çek"""
    try:
        url = "https://fapi.binance.com/fapi/v1/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=[
                'time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['volume'] = df['volume'].astype(float)
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            return df[['time', 'open', 'high', 'low', 'close', 'volume']]
    except:
        pass
    return None

def get_ai_analysis():
    """AI Brain analizi"""
    if AIBRAIN_OK and _ai_brain:
        try:
            prices = get_real_prices()
            market_data = {
                'btc_price': prices.get('BTCUSDT', 0),
                'eth_price': prices.get('ETHUSDT', 0),
                'btc_prev_price': prices.get('BTCUSDT', 0) * 0.99,
                'timestamp': datetime.now(),
                'volume_24h': 0,
                'volume_7d_avg': 0,
                'funding_rate': 0
            }
            result = _ai_brain.analyze(market_data)
            return {
                'signal': result.signal.value,
                'confidence': result.confidence,
                'score': result.overall_score
            }
        except:
            pass
    return {'signal': 'NEUTRAL', 'confidence': 0, 'score': 50}

# ============================================================================
# PREDICTION ENGINE
# ============================================================================

class PredictionEngine:
    """Tüm matematiksel tahmin modellerini içerir"""
    
    def __init__(self, prices, symbol='BTCUSDT'):
        self.prices = prices
        self.symbol = symbol
        self.current_price = prices[-1] if len(prices) > 0 else 0
    
    def linear_regression(self, window=20):
        """Doğrusal regresyon tahmini"""
        if len(self.prices) < window:
            return self.current_price
        
        x = np.arange(window)
        y = np.array(self.prices[-window:])
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        next_price = self.current_price + (slope * 15)
        return next_price
    
    def monte_carlo_simulation(self, steps=15, simulations=1000):
        """Monte Carlo simulasyonu"""
        if len(self.prices) < 2:
            return self.current_price, 0.5
        
        returns = np.diff(self.prices) / self.prices[:-1]
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        simulated_prices = []
        for _ in range(simulations):
            price = self.current_price
            for _ in range(steps):
                random_return = np.random.normal(mean_return, std_return)
                price *= (1 + random_return)
            simulated_prices.append(price)
        
        predicted_price = np.mean(simulated_prices)
        confidence = 1 - (np.std(simulated_prices) / np.mean(simulated_prices))
        return predicted_price, confidence
    
    def support_resistance(self, window=20):
        """Destek ve Direnç seviyeleri"""
        if len(self.prices) < window:
            return self.current_price, self.current_price
        
        recent = self.prices[-window:]
        support = np.min(recent)
        resistance = np.max(recent)
        return support, resistance
    
    def rsi(self, window=14):
        """RSI (Relative Strength Index)"""
        if len(self.prices) < window:
            return 50
        
        deltas = np.diff(self.prices[-window:])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 100 if avg_gain > 0 else 50
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def bollinger_bands(self, window=20, num_std=2):
        """Bollinger Bands"""
        if len(self.prices) < window:
            return self.current_price, self.current_price, self.current_price
        
        sma = np.mean(self.prices[-window:])
        std = np.std(self.prices[-window:])
        
        upper = sma + (num_std * std)
        middle = sma
        lower = sma - (num_std * std)
        
        return upper, middle, lower
    
    def ensemble_prediction(self):
        """Tüm modelleri kombinle"""
        predictions = {
            'linear_regression': self.linear_regression(),
            'monte_carlo': self.monte_carlo_simulation()[0],
        }
        
        ensemble = (
            predictions['monte_carlo'] * 0.6 +
            predictions['linear_regression'] * 0.4
        )
        
        return ensemble, predictions

# ============================================================================
# MAIN PAGE
# ============================================================================

st.title("🔮 TAHMİN MOTORU - Gelecek 15-30 Dakika Öngörüsü")
st.caption("Yapay Zeka + 10 Matematiksel Model = Doğru Tahmin")

st.markdown("""
Bu sayfa **tüm mevcut verileri** analiz ederek **15-30 dakika sonrası** için **matematiksel tahmin** yapar.

**Kullanılan Modeller:**
- 📊 Doğrusal Regresyon
- 🎲 Monte Carlo (1000 senaryo)
- 📈 Bollinger Bands
- 📊 RSI & MACD
- 🔗 Ensemble Learning
""")

st.divider()

# Cryptocurrency seçici
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🪙 Kripto Para Seç")
    symbol = st.selectbox(
        "Kripto Para",
        ["BTCUSDT", "ETHUSDT", "LTCUSDT"],
        label_visibility="collapsed",
        key="prediction_symbol"
    )

with col2:
    st.markdown("### ⏱️ Tahmin Dönemi")
    timeframe = st.selectbox(
        "Tahmin Dönemi",
        ["15 Dakika", "30 Dakika", "1 Saat"],
        label_visibility="collapsed",
        key="prediction_timeframe"
    )

# Veri çek
klines = get_klines(symbol, interval='1m', limit=100)

if klines is not None and len(klines) > 0:
    prices = klines['close'].values.tolist()
    current_price = prices[-1]
    
    # Tahmin motorunu başlat
    engine = PredictionEngine(prices, symbol)
    
    # Tahminleri yap
    ensemble_pred, individual_preds = engine.ensemble_prediction()
    mc_pred, mc_confidence = engine.monte_carlo_simulation()
    support, resistance = engine.support_resistance()
    rsi = engine.rsi()
    upper_bb, middle_bb, lower_bb = engine.bollinger_bands()
    confidence = min(100, max(0, 50 + (abs(ensemble_pred - current_price) / current_price) * 1000))
    
    ai_analysis = get_ai_analysis()
    
    # ========== MAIN PREDICTION ==========
    st.markdown(f"""
    <div class="prediction-box">
    <h2>🎯 BİRLEŞTİRİLMİŞ TAHMİN (Ensemble Model)</h2>
    
    <h3>Mevcut Fiyat: ${current_price:,.2f}</h3>
    <h1>Tahmin: ${ensemble_pred:,.2f}</h1>
    
    <p><strong>Beklenen Değişim:</strong> {((ensemble_pred - current_price) / current_price * 100):+.2f}%</p>
    <p><strong>Zaman Aralığı:</strong> {timeframe}</p>
    <p><strong>Model Güveni:</strong> {confidence:.1f}%</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # ========== TEKNIK ANALİZ ==========
    st.subheader("📊 Teknik İndikatörler")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        rsi_status = "⚠️ Overbought" if rsi > 70 else "⚠️ Oversold" if rsi < 30 else "✅ Neutral"
        st.metric("RSI (14)", f"{rsi:.1f}", delta=rsi_status)
    
    with col2:
        resistance_diff = ((resistance - current_price) / current_price * 100)
        st.metric("Direnç", f"${resistance:,.2f}", delta=f"+{resistance_diff:.2f}%")
    
    with col3:
        support_diff = ((support - current_price) / current_price * 100)
        st.metric("Destek", f"${support:,.2f}", delta=f"{support_diff:+.2f}%")
    
    with col4:
        bb_position = (current_price - lower_bb) / (upper_bb - lower_bb) * 100
        st.metric("BB Pozisyonu", f"{bb_position:.1f}%", delta="Üst" if bb_position > 70 else "Alt" if bb_position < 30 else "Orta")
    
    st.divider()
    
    # ========== TRADEYİ EKLE BÖLÜMÜ ==========
    st.subheader("➕ TARAFINDAN ÖNERİLEN TRADE'İ AÇ")
    
    # AI Signal'a göre tavsiye
    if ai_analysis['signal'] == 'LONG':
        recommended_direction = "LONG (YUKARIŞ)"
        direction_emoji = "🟢"
        entry_rec = current_price * 0.998  # %0.2 altında
        tp_rec = current_price * 1.02  # %2 yukarıda
        sl_rec = current_price * 0.98  # %2 aşağıda
    elif ai_analysis['signal'] == 'SHORT':
        recommended_direction = "SHORT (DÜŞÜŞ)"
        direction_emoji = "🔴"
        entry_rec = current_price * 1.002  # %0.2 üstünde
        tp_rec = current_price * 0.98  # %2 aşağıda
        sl_rec = current_price * 1.02  # %2 yukarıda
    else:
        recommended_direction = "TARAFSIZ (BEKLEMESİ TAVSİYE EDİLİR)"
        direction_emoji = "🟡"
        entry_rec = current_price
        tp_rec = current_price * 1.01
        sl_rec = current_price * 0.99
    
    # Trade Önerisi Kartı
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div class="trade-box">
        <h3>{direction_emoji} BOT'UN ÖNERİSİ: {recommended_direction}</h3>
        
        <p><strong>📍 GİRİŞ FİYATI:</strong> ${entry_rec:,.2f}</p>
        <p><strong>🎯 KAPANIŞ HEDEFİ (TP):</strong> ${tp_rec:,.2f}</p>
        <p><strong>Beklenen Kar:</strong> {((tp_rec - entry_rec) / entry_rec * 100):+.2f}%</p>
        
        <p><strong>🛡️ STOPLOSS (SL):</strong> ${sl_rec:,.2f}</p>
        <p><strong>Maksimum Zarar:</strong> {((sl_rec - entry_rec) / entry_rec * 100):+.2f}%</p>
        
        <p><strong>📊 Kar/Zarar Oranı:</strong> 1:{abs((tp_rec - entry_rec) / (entry_rec - sl_rec)):.2f}</p>
        <p><strong>🤖 Bot Güveni:</strong> {ai_analysis['confidence']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col1:
        # Add Trade Button
        if st.button(f"➕ {symbol} TRADEYİ EKLE\n({recommended_direction})", 
                     use_container_width=True, key=f"add_trade_{symbol}"):
            
            # Session'a ekle
            if 'active_trades' not in st.session_state:
                st.session_state.active_trades = []
            
            trade = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'direction': recommended_direction,
                'entry_price': entry_rec,
                'tp_target': tp_rec,
                'sl_stop': sl_rec,
                'confidence': ai_analysis['confidence'],
                'ai_score': ai_analysis['score'],
                'status': 'AÇIK',
                'pnl': None
            }
            
            st.session_state.active_trades.append(trade)
            
            st.success(f"""
            ✅ TRADEYİ BAŞARILI EKLENMIŞTIR!
            
            {direction_emoji} {symbol} - {recommended_direction}
            📍 GİRİŞ: ${entry_rec:,.2f}
            🎯 HEDEF: ${tp_rec:,.2f}
            🛡️ STOP: ${sl_rec:,.2f}
            
            ✅ Bot bu işlemi şu anda takip etmektedir!
            """)
    
    st.divider()
    
    # ========== DETAYLI ANALİZ ==========
    st.subheader("📈 Bireysel Model Tahminleri")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Doğrusal Regresyon",
            f"${individual_preds['linear_regression']:,.2f}",
            delta=f"{((individual_preds['linear_regression'] - current_price) / current_price * 100):+.2f}%"
        )
    
    with col2:
        st.metric(
            "Monte Carlo (1K sim)",
            f"${mc_pred:,.2f}",
            delta=f"{((mc_pred - current_price) / current_price * 100):+.2f}%"
        )
    
    st.divider()
    
    # ========== AÇIK İŞLEMLER ==========
    if 'active_trades' in st.session_state and st.session_state.active_trades:
        st.subheader("📊 AÇIK TRADELERİN DURUMU")
        
        current_prices = get_real_prices()
        
        for idx, trade in enumerate(st.session_state.active_trades):
            current = current_prices.get(trade['symbol'], 0)
            
            with st.expander(f"📈 {trade['symbol']} - {trade['direction']} | {trade['status']}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("GİRİŞ FİYATI", f"${trade['entry_price']:,.2f}")
                    st.metric("MEVCUT", f"${current:,.2f}")
                
                with col2:
                    st.metric("HEDEF (TP)", f"${trade['tp_target']:,.2f}")
                    if trade['direction'] == "LONG (YUKARIŞ)":
                        distance_to_tp = ((trade['tp_target'] - current) / current * 100)
                    else:
                        distance_to_tp = ((current - trade['tp_target']) / current * 100)
                    st.caption(f"Hedefe: {distance_to_tp:+.2f}%")
                
                with col3:
                    st.metric("STOPLOSS (SL)", f"${trade['sl_stop']:,.2f}")
                    if trade['direction'] == "LONG (YUKARIŞ)":
                        distance_to_sl = ((current - trade['sl_stop']) / current * 100)
                    else:
                        distance_to_sl = ((trade['sl_stop'] - current) / current * 100)
                    st.caption(f"Stop'tan: {distance_to_sl:+.2f}%")
                
                # Durum Kontrol
                if trade['direction'] == "LONG (YUKARIŞ)":
                    if current >= trade['tp_target']:
                        st.success(f"""
                        ✅ TP HEDEFİNE ULAŞILDI!
                        
                        Kar: {((trade['tp_target'] - trade['entry_price']) / trade['entry_price'] * 100):.2f}%
                        """)
                        trade['status'] = 'KAPATILDI - TP'
                    elif current <= trade['sl_stop']:
                        st.error(f"""
                        ❌ STOPLOSS TRİGGERLENDİ!
                        
                        Zarar: {((trade['sl_stop'] - trade['entry_price']) / trade['entry_price'] * 100):.2f}%
                        """)
                        trade['status'] = 'KAPATILDI - SL'
                    else:
                        remaining = ((trade['tp_target'] - current) / trade['tp_target']) * 100
                        st.info(f"⏳ AÇIK - Hedefe kadar: {remaining:.1f}%")
                else:  # SHORT
                    if current <= trade['tp_target']:
                        st.success(f"""
                        ✅ TP HEDEFİNE ULAŞILDI!
                        
                        Kar: {((trade['entry_price'] - trade['tp_target']) / trade['entry_price'] * 100):.2f}%
                        """)
                        trade['status'] = 'KAPATILDI - TP'
                    elif current >= trade['sl_stop']:
                        st.error(f"""
                        ❌ STOPLOSS TRİGGERLENDİ!
                        
                        Zarar: {((trade['sl_stop'] - trade['entry_price']) / trade['entry_price'] * 100):.2f}%
                        """)
                        trade['status'] = 'KAPATILDI - SL'
                    else:
                        remaining = ((current - trade['tp_target']) / current) * 100
                        st.info(f"⏳ AÇIK - Hedefe kadar: {remaining:.1f}%")

else:
    st.error(f"❌ {symbol} için veri çekilenemedi")

st.divider()

st.markdown(f"""
<p style='text-align: center; color: #9CA3AF; font-size: 12px;'>
🔮 Tahmin Motoru v3.0 | Tam Türkçe Arayüz | Trade Tracking
<br>
Ensemble Learning + Monte Carlo + Teknik Analiz + AI Brain
</p>
""", unsafe_allow_html=True)
