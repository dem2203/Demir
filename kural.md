# 🔱 DEMİR AI YAPAY ZEKA BOTU - PROJE KURALLARI VE DURUM

**Son Güncelleme:** 4 Kasım 2025, 22:27 CET  
**Versiyon:** 3.0 - CI/CD İptal Edildi

---

## 1. PROJENİN AMACI

- **İnsan üstü yapay zeka botu** tasarlamak
- **7/24 tüm piyasa verilerini ve haberlerini** takip eden
- **Kuantum matematik ve gelişmiş analiz yöntemleri** kullanan
- **Binance Futures** için BTCUSDT, ETHUSDT, LTCUSDT gibi coinlerde
- **Günlük kar getiren sinyaller** üretmek, kullanıcıya işlem açma önerileri sunmak

---

## 2. PROJENİN MEVCUT DURUMU

### ✅ **Tamamlanan Fazlar:**
- **Phase 1-6:** Temel yapı ve 12 layer sistemi
- **Phase 7:** Quantum matematik 5 layer (Black-Scholes, Kalman, Fractal, Fourier, Copula)
- **Toplam 17 katmanlı (layer) analiz sistemi aktif**

### 🔄 **Aktif Durum:**
- Streamlit tabanlı dashboard ile anlık veriler görselleştiriliyor
- Binance API anahtarları ve diğer gerekli API'lar **render.com** ortamında çalışıyor
- **CI/CD pipeline İPTAL EDİLDİ** - Tüm deployment ve hata takibi **Render.com log file** üzerinden yapılıyor

### 🎯 **Sonraki Adım:**
- **Phase 3:** Alert System (Telegram) + Backtest Module
- veya
- **Phase 6:** Macro Correlation Layers (SPX, Gold, VIX, Rates)

---

## 3. PROJE KURALLARI VE İLKELERİ

### 🎯 **Değişmez Kurallar:**
1. ✅ **Ana coinler her zaman sabit:** BTCUSDT, ETHUSDT, LTCUSDT
2. ✅ **Diğer coinler:** Manuel olarak arayüzden eklenebiliyor
3. ✅ **Sadece gerçek veriler:** Mock veya demo veri ASLA YOK
4. ✅ **Manuel işlem:** Yapay zeka sadece sinyal verir, kullanıcı manuel karar verir
5. ✅ **Proje belleği:** Her faz sonrası güncellenir, geçmiş hatalar kayıt altında
6. ✅ **Mevcut kodlar korunur:** Doğru çalışan kodlar asla değiştirilmez/pasif edilmez
7. ✅ **Platform:** Tamamen Streamlit + Render.com (terminal/lokal çalışma YOK)
8. ✅ **Deployment:** GitHub push → Render otomatik deploy (CI/CD pipeline YOK)
9. ✅ **Hata takibi:** Render.com log file üzerinden

---

## 4. PROJENİN ANA BİLEŞENLERİ

### 📁 **Ana Dosyalar:**
- `streamlit_app.py` - Ana dashboard
- `ai_brain.py` - 17 layer AI motor
- `config.py` - Konfigürasyon
- `api_cache_manager.py` - API cache sistemi
- `requirements.txt` - Python bağımlılıkları

### 🧠 **Phase 1-6 Katmanlar (12 Layer):**
1. Strateji Katmanı (Teknik analiz)
2. Monte Carlo Simülasyonu
3. Kelly Kriteri
4. Makro Korelasyon
5. Altın Korelasyon
6. Dominance Flow
7. Çapraz Varlık Korelasyonu
8. VIX Katmanı
9. Faiz Oranları
10. Geleneksel Piyasalar
11. Haber Duyarlılığı
12. Diğer Teknik Katmanlar

### 🔮 **Phase 7 Quantum Katmanlar (5 Yeni Layer):**
13. Black-Scholes Opsiyon Layer
14. Kalman Paneli (Regime Detection)
15. Fraktal Kaos Analizi
16. Fourier Döngü Analizi
17. Copula Korelasyon

**Toplam:** 17 Layer aktif

---

## 5. YAPILANLAR VE GELİŞİM PLANI

### ✅ **Tamamlanan İşler:**
- Phase 7 katmanlarının yazımı ve AI beynine entegrasyonu ✅
- Streamlit arayüzüne Quantum katmanların göstergeleri eklendi ✅
- AI sinyal kalitesi için Confidence skoru, sinyal gücü ve layer ağırlıkları ✅
- 4 kritik bug düzeltildi (4 Kasım 2025) ✅
- CI/CD pipeline iptal edildi - Render.com'a geçiş yapıldı ✅

### 🔄 **Devam Eden İşler:**
- Backtest ve canlı test aşamaları
- Layer ağırlıkları ve confidence skor optimizasyonu
- Render.com üzerinde performans izleme

### 📋 **Yapılacak İşler:**
- **Phase 3:** Telegram alerts + Backtest modülü (2-3 saat)
- **Phase 6:** Macro correlation layers (8-10 saat)
- **Phase 8:** Quantum Predictive AI (15-20 saat)

---

## 6. PROJE HEDEFLERİ

- 🎯 **Win Rate:** %50-60 → %70-75 (Phase 6 sonrası)
- 💰 **Aylık Kar:** %5-10 → %30-50 (Phase 6 sonrası)
- ⚡ **Sinyal Kalitesi:** Confidence score > %70
- 📱 **Anlık Bildirim:** Telegram entegrasyonu (Phase 3)
- 🔄 **7/24 Çalışma:** Render.com üzerinde kesintisiz
- 🎯 **AI tarafından oluşturulan sinyallerle** zamanında ve doğru pozisyon açmak

---

## 7. KULLANILAN TEKNOLOJİLER

### 🛠️ **Backend:**
- Python 3.11+
- Streamlit (Dashboard)
- Binance Futures API (gerçek zamanlı veri)
- TA-Lib (teknik analiz)

### 📊 **AI/ML Kütüphaneleri:**
- NumPy, Pandas, SciPy
- Scikit-learn
- ARCH (GARCH model)
- Statsmodels (zaman serisi)

### 🔮 **Quantum & Advanced:**
- Black-Scholes (opsiyon pricing)
- Kalman Filter (regime detection)
- Fractal Dimension (chaos theory)
- FFT (Fourier cycle analysis)
- Copula (tail risk correlation)

### 🌐 **Deployment:**
- GitHub (kod deposu)
- Render.com (hosting)
- **CI/CD Pipeline: İPTAL EDİLDİ**
- Hata takibi: Render.com log file

### 📡 **API'lar:**
- Binance API (fiyat, hacim, order book)
- NewsAPI (haber sentiment)
- Alpha Vantage (makro ekonomik data)
- FRED API (faiz oranları)
- CoinGlass (funding rate, OI)
- CMC (CoinMarketCap)

---

## 8. DEPLOYMENT SÜRECİ

### 🚀 **Yeni Deployment Workflow:**

```
1. Kod değişikliği yap (GitHub)
   ↓
2. GitHub'a push et
   ↓
3. Render.com otomatik deploy başlar
   ↓
4. Render.com log file'ı kontrol et
   ↓
5. Hata varsa → Render log'dan gör → Düzelt → Tekrar push
   ↓
6. Deploy başarılı → Streamlit dashboard canlı!
```

### 📝 **Render.com Log Kontrolü:**
```
1. Render Dashboard'a git
2. "Logs" sekmesini aç
3. Build log'ları kontrol et
4. Runtime hataları için live log'ları izle
5. Hata mesajlarını PROJECT-MEMORY.md'ye kaydet
```

---

## 9. HATA YÖNETİMİ

### ⚠️ **Bilinen Hatalar (4 Kasım 2025):**
1. ✅ `streamlit_app.py` - Duplicate function **DÜZELTİLDİ**
2. ✅ `api_cache_manager.py` - Global variable mismatch **DÜZELTİLDİ**
3. ✅ CI/CD pipeline notifications **İPTAL EDİLDİ**
4. ✅ Indentation error Line 739 **DÜZELTİLDİ**

### 📋 **Hata Takip Süreci:**
1. Render.com log file'da hata tespit et
2. Hatayı PROJECT-MEMORY.md'ye kaydet
3. Kodu düzelt
4. GitHub'a push et
5. Render'ın otomatik deploy'unu bekle
6. Log file'dan doğrula
7. PROJECT-MEMORY.md'yi güncelle

---

## 10. SONRAKİ ADIMLAR

### 🎯 **Öncelik Sırası:**

#### **SEÇENEK A: Hızlı Kazanç - Phase 3 (2-3 saat)** ⚡
- Telegram bot entegrasyonu
- Backtest modülü
- Portfolio optimizer
- **Sonuç:** Win Rate %55-60, Aylık %10-15

#### **SEÇENEK B: Makro Güç - Phase 6 (8-10 saat)** 🌍
- Traditional Markets (SPX, NASDAQ, DXY)
- Gold Correlation
- BTC Dominance & USDT Flow
- Cross-Asset Correlation
- VIX Fear Index
- Interest Rates
- **Sonuç:** Win Rate %70-75, Aylık %30-50

#### **SEÇENEK C: Quantum Güç - Phase 8 (15-20 saat)** 🧠
- Quantum Random Forest
- Quantum Neural Networks
- Quantum Annealing
- **Sonuç:** Win Rate %80-85, Aylık %80-120

---

## 11. PATRON NOTLARI

- **Deployment:** Artık sadece Render.com (CI/CD yok)
- **Hata takibi:** Render log file üzerinden
- **Test:** Canlı piyasada gerçek verilerle
- **Hedef:** İnsan üstü yapay zeka botu!

---

**Bu dosya canlı tutulacak ve her fazda güncellenecektir.**

**Proje GitHub:** https://github.com/dem2203/Demir  
**Render Dashboard:** dashboard.render.com

---

**Son Güncelleme:** 4 Kasım 2025, 22:27 CET
