
# DEMİR AI YAPAY ZEKA BOTU - PROJE ÖZETİ

## 1. Projenin Amacı

- [translate:İnsan üstü yapay zeka botu tasarlamak]
- 7/24 tüm piyasa verilerini ve haberlerini takip eden,
- Kuantum matematik ve gelişmiş analiz yöntemleri kullanan,
- Binance Futures için BTCUSDT, ETHUSDT, LTCUSDT gibi coinlerde
- Günlük kar getiren sinyaller üretmek, kullanıcıya işlem açma önerileri sunmak.

## 2. Projenin Mevcut Durumu

- Phase 1'den Phase 7'ye kadar süreçler tamamlandı.
- Toplam 17 katmanlı (layer) analiz sistemi aktif durumda.
- Phase 7'de Quantum matematik tabanlı 5 yeni layer eklendi:
  - Black-Scholes opsiyon fiyatlama
  - Kalman Regime Detection
  - Fractal Chaos Analizi
  - Fourier Cycle Detection
  - Copula Correlation
- Streamlit tabanlı bir dashboard ile anlık veriler görselleştiriliyor.
- Binance API anahtarları ve diğer gerekli API'lar render.com ortamında çalışıyor.
- CI/CD pipeline aktif, otomatik deploy yapılıyor.

## 3. Proje Kuralları ve İlkeleri

- Ana coinler her zaman sabit (BTCUSDT, ETHUSDT, LTCUSDT).
- Diğer coinler manuel olarak arayüzden eklenebiliyor.
- Tamamen gerçek ve güncel piyasa verileri kullanılır; mock veya demo veri asla yok.
- Otomatik işlem yok, yapay zeka sadece bilgi ve sinyal verir, kullanıcı manuel karar verir.
- Proje belleği her faz tamamlandıktan sonra güncellenir ve geçmiş hatalar kayıt altına alınır.
- Mevcut doğru çalışan kodlar kesinlikle değiştirilmez veya pasif edilmez.
- Proje tamamen Streamlit platformunda render.com üzerinden çalışır, terminal veya lokal çalışma yok.

## 4. Projenin Ana Bileşenleri (Dosyalar ve Katmanlar)

### Phase 1-6 Katmanlar (Toplam 12 Layer yaklaşık)
- Strateji Katmanı
- Monte Carlo Simülasyonu
- Kelly Kriteri
- Makro Korelasyon
- Altın Korelasyon
- Dominance Flow
- Çapraz Varlık Korelasyonu
- VIX Katmanı
- Faiz Oranları
- Geleneksel Piyasalar
- Haber Duyarlılığı
- Diğer Teknik Katmanlar

### Phase 7 Quantum Katmanlar (5 Yeni Layer)
- Black-Scholes Opsiyon Layer
- Kalman Paneli (Regime Detection)
- Fraktal Kaos Analizi
- Fourier Döngü Analizi
- Copula Korelasyon

## 5. Yapılacak İşler ve Gelişim Planı

- Phase 7 katmanlarının yazımı ve mevcut AI beynine entegrasyonu tamamlandı.
- Streamlit arayüzüne Quantum Katmanların göstergeleri eklendi.
- AI sinyal kalitesi için Confidence skoru, sinyal gücü ve layer ağırlıkları kullanılmakta.
- Backtest ve canlı test aşamaları devam ediyor.
- Ek API'lar ve zincir üstü veri entegrasyonları Phase 8 ve sonrası için planlanmakta.

## 6. Proje Hedefleri

- %50-60 win rate hedefiyle ortalama %5-10 aylık kar sağlayacak stabil sinyaller oluşturmak.
- AI tarafından oluşturulan sinyallerle zamanında ve doğru pozisyon açmak.
- Yeni layerlar ekleyerek piyasa adaptasyonunu ve tahmin doğruluğunu artırmak.
- Render.com üzerinde 7/24 stabil çalışan, kullanıcı dostu arayüz düzenlemeleri yapmak.

## 7. Kullanılan Teknolojiler

- Python 3
- Streamlit
- Binance Futures API (gerçek zamanlı veri)
- TA-Lib ve diğer teknik analiz kütüphaneleri
- Kuantum matematik ve istatistiksel modellemeler (GARCH, Kalman, Monte Carlo, Fourier)
- CI/CD (GitHub Actions)
- Render.com barındırma

