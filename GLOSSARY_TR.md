# 📚 DEMIR AI - Teknik Terimler Sözlüğü

## Genel Bakış
Bu belge, DEMIR AI Trading Bot'un kullandığı tüm teknik terimleri **sade Türkçe** ile açıklar.

---

## 🎯 PHASE 3A TERİMLERİ

### **Volume Profile (Hacim Profili)**
**Ne demek:** Belirli fiyat seviyelerinde ne kadar alım-satım yapıldığını gösteren analiz.

**Basit açıklama:** Fiyatın hangi seviyelerde en çok işlem gördüğünü gösterir. Örneğin BTC $69,000'de çok işlem görmüşse, burası önemli bir destek/direnç noktasıdır.

**Terimler:**
- **VAH (Value Area High):** En yoğun işlem gören alanın üst sınırı → Direnç noktası
- **VAL (Value Area Low):** En yoğun işlem gören alanın alt sınırı → Destek noktası
- **POC (Point of Control):** En fazla işlem yapılan fiyat seviyesi → Çok güçlü destek/direnç

**Kullanım:** Fiyat VAH'a yakınsa "direnç var, satış gelebilir" diye yorumlarız.

---

### **Pivot Points (Dönüş Noktaları)**
**Ne demek:** Önceki günün fiyat hareketlerine göre hesaplanan destek ve direnç seviyeleri.

**Basit açıklama:** Bugünün potansiyel dönüş noktalarını tahmin eder. Fiyat R2'ye gelirse "burada düşüş gelebilir", S1'e gelirse "burada yükseliş gelebilir" deriz.

**Terimler:**
- **PP (Pivot Point):** Orta nokta
- **R1, R2, R3:** Direnç seviyeleri (Resistance = Direnç)
- **S1, S2, S3:** Destek seviyeleri (Support = Destek)
- **Classic:** Standart hesaplama yöntemi

**Kullanım:** Fiyat R2'ye yaklaştıysa ve yukarı çıkmakta zorlanıyorsa, SHORT (satış) fırsatı olabilir.

---

### **Fibonacci (Fibonacci Seviyeleri)**
**Ne demek:** Doğada ve matematikte bulunan "altın oran" ile fiyat hareketlerinin olası dönüş noktalarını bulma.

**Basit açıklama:** Fiyat büyük bir hareket yaptıktan sonra nereye kadar geri çekilebilir? Fibonacci bu "geri çekilme" seviyelerini gösterir.

**Terimler:**
- **0.618 (Altın Oran):** En güçlü destek/direnç seviyesi
- **0.50:** Yarı yolun ortası
- **0.382:** Zayıf geri çekilme

**Kullanım:** BTC $70,000'den $68,000'e düştü. 0.618 seviyesi $68,500'de. Fiyat buraya gelirse "güçlü destek, buradan alım yapılabilir" deriz.

---

### **VWAP (Volume Weighted Average Price - Hacim Ağırlıklı Ortalama Fiyat)**
**Ne demek:** Gün içinde işlem gören tüm fiyatların hacim ağırlıklı ortalaması.

**Basit açıklama:** "Bugün bu coin'in gerçek değeri ne?" sorusunun cevabı. VWAP'ın üzerindeyse "pahalı", altındaysa "ucuz" demektir.

**Terimler:**
- **+1STD, +2STD, +3STD:** VWAP'tan yukarıya sapma (Standard Deviation = Standart Sapma)
- **-1STD, -2STD, -3STD:** VWAP'tan aşağıya sapma

**Kullanım:** Fiyat +2STD'deyse "çok pahalı, ortalamaya dönecek (düşecek)" tahmininde bulunuruz.

---

### **News Sentiment (Haber Duygusu)**
**Ne demek:** Piyasadaki haberlerin olumlu (bullish) veya olumsuz (bearish) olup olmadığını analiz etme.

**Basit açıklama:** "Bitcoin'le ilgili haberler iyi mi kötü mü?" sorusunun cevabı. Pozitif haberler çoksa fiyat yükselme eğilimindedir.

**Terimler:**
- **BULLISH (Boğa):** Olumlu haberler → Fiyat yükselecek
- **BEARISH (Ayı):** Olumsuz haberler → Fiyat düşecek
- **NEUTRAL (Nötr):** Karma/etkisiz haberler

---

## 🎲 PHASE 3B TERİMLERİ

### **GARCH Volatility (GARCH Volatilite Tahmini)**
**Ne demek:** Gelecek 24 saatte fiyatın ne kadar dalgalanacağını matematiksel modelle tahmin etme.

**Basit açıklama:** "Yarın fiyat çok mu oynayacak, az mı?" sorusuna cevap. Yüksek volatilite = Yüksek risk.

**Formül:** σ²(t) = ω + α·r²(t-1) + β·σ²(t-1)
- **σ (sigma):** Volatilite (dalgalanma)
- **α (alpha):** Kısa dönem şok etkisi
- **β (beta):** Uzun dönem kalıcılık

**Terimler:**
- **LOW:** Düşük volatilite (2% altı) → Sakin piyasa
- **MODERATE:** Orta volatilite (2-3.5%) → Normal
- **HIGH:** Yüksek volatilite (3.5-5%) → Riskli
- **EXTREME:** Aşırı volatilite (5%+) → Çok riskli

**Kullanım:** GARCH "HIGH" diyorsa, pozisyon boyutunu küçültürüz (daha az risk alırız).

---

### **Markov Regime (Markov Piyasa Rejimi)**
**Ne demek:** Piyasanın hangi "modda" olduğunu tespit etme (trend, yan yatay, ya da kaotik).

**Basit açıklama:** "Piyasa şu anda yükseliş trendinde mi, yoksa kararsız mı?" sorusuna cevap.

**3 Rejim:**
1. **TREND (Trend):** Güçlü yön var (Bullish = Yukarı, Bearish = Aşağı)
2. **RANGE (Yan Yatay):** Fiyat belli aralıkta gidip geliyor
3. **HIGH_VOL (Yüksek Volatilite):** Piyasa çok dalgalı, belirsiz

**Kullanım:**
- TREND (BULLISH) → LONG (al)
- TREND (BEARISH) → SHORT (sat)
- RANGE → NEUTRAL (bekle)
- HIGH_VOL → WAIT (risk azalt)

---

### **HVI (Historical Volatility Index - Tarihsel Volatilite Endeksi)**
**Ne demek:** Şu anki volatilitenin geçmiş ortalamalara göre ne durumda olduğunu gösteren Z-skoru.

**Basit açıklama:** "Son 20 gündeki dalgalanmaya göre bugün normal mi, çok mu dalgalı?" sorusuna cevap.

**Z-Score Yorumlama:**
- **Z > +2σ:** Çok yüksek volatilite (aşırı dalgalı)
- **Z > +1σ:** Yüksek volatilite
- **-1σ < Z < +1σ:** Normal
- **Z < -1σ:** Düşük volatilite (sakin, breakout potansiyeli)

**Kullanım:** HVI +2σ ise "piyasa çılgın, büyük hareket olabilir, dikkatli ol" deriz.

---

### **Volatility Squeeze (Volatilite Sıkışması)**
**Ne demek:** Fiyatın daraldığı, büyük hareket öncesi "sessizlik" dönemini tespit etme.

**Basit açıklama:** "Fırtına öncesi sessizlik". Bollinger Bands daraldığında ve Keltner Channel'ın içine girdiğinde, büyük bir hareket (breakout) gelebilir.

**Terimler:**
- **Squeeze ON:** Sıkışma aktif (fiyat dar aralıkta)
- **Squeeze OFF:** Breakout başladı (fiyat patladı)
- **Bullish Breakout:** Yukarı kırılım
- **Bearish Breakout:** Aşağı kırılım

**Kullanım:** Squeeze 10+ period sürmüşse, "büyük hareket yakında gelecek, hazır ol" deriz.

---

## 💰 RİSK YÖNETİMİ TERİMLERİ

### **Monte Carlo Simulation (Monte Carlo Simülasyonu)**
**Ne demek:** 1000 farklı senaryoda trade sonuçlarını simüle ederek riskleri ölçme.

**Basit açıklama:** "1000 paralel evrende trading yapsam ne olurdu?" sorusuna cevap. Ortalama kazanç/kaybı ve en kötü senaryoyu gösterir.

**Terimler:**
- **Risk of Ruin (Batma Riski):** Tüm sermayeyi kaybetme olasılığı
- **Max Drawdown (Maksimum Düşüş):** En kötü senaryo kaybı
- **Sharpe Ratio:** Kazanç/Risk oranı (yüksek = iyi)

**Kullanım:** Risk of Ruin %10'dan fazlaysa "çok riskli, pozisyon küçült" deriz.

---

### **Kelly Criterion (Kelly Kriteri)**
**Ne demek:** Optimal pozisyon boyutunu matematiksel olarak hesaplama.

**Basit açıklama:** "Ne kadar para yatırmalıyım?" sorusunun cevabı. Kazanma olasılığı ve kazanç/kayıp oranına göre ideal lot boyutu bulur.

**Formül:** f = (p × b - q) / b
- **p:** Kazanma olasılığı
- **b:** Kazanç/Kayıp oranı (R-multiple)
- **q:** Kaybetme olasılığı (1-p)

**Kullanım:** Kelly "portföyün %5'i" diyorsa, $10,000 portföyde $500 riske atarız.

---

### **ATR (Average True Range - Ortalama Gerçek Aralık)**
**Ne demek:** Fiyatın günlük ortalama hareket mesafesi.

**Basit açıklama:** "Bu coin günde ortalama ne kadar oynuyor?" sorusuna cevap. ATR yüksekse volatilite yüksektir.

**Kullanım:**
- **Stop Loss:** ATR × 2 (fiyatın 2 ATR aşağısında)
- **Take Profit:** ATR × 3 (fiyatın 3 ATR yukarısında)

**Örnek:** BTC'nin ATR'si $1,000. Fiyat $69,000.
- Stop Loss: $69,000 - ($1,000 × 2) = $67,000
- Take Profit: $69,000 + ($1,000 × 3) = $72,000

---

## 🎯 SINYAL TERİMLERİ

### **LONG (Al / Yükseliş Beklentisi)**
Fiyatın yükseleceğini düşünüp alım yapma.

### **SHORT (Sat / Düşüş Beklentisi)**
Fiyatın düşeceğini düşünüp satış yapma (veya kısa pozisyon açma).

### **NEUTRAL (Nötr / Kararsız)**
Yön belli değil, beklemek en iyisi.

### **WAIT (Bekle / Risk Yüksek)**
Çok riskli, hiçbir pozisyon açma.

---

## 📊 SKOR SİSTEMİ

### **Final Score (0-100)**
Tüm analizlerin ağırlıklı ortalaması:
- **65+:** Güçlü LONG sinyali
- **35-65:** NEUTRAL (belirsiz)
- **35-:** Güçlü SHORT sinyali

### **Confidence (0.0-1.0)**
AI'ın kararından ne kadar emin olduğu:
- **0.8+:** Çok yüksek güven
- **0.6-0.8:** Yüksek güven
- **0.5-0.6:** Orta güven
- **0.5-:** Düşük güven (WAIT önerilir)

---

## 🔢 ÖRNEK SENARYO

**BTC Analizi:**
```
Final Score: 72/100
Signal: LONG
Confidence: 78%

Component Analysis:
📊 Volume Profile: VAH ($69,847) - Direnç bölgesi
   → Fiyat en yoğun işlem gören alanın üstünde, dikkatli ol

📍 Pivot Points: R2 ($71,585) - Güçlü direnç
   → Fiyat R2'ye yaklaşıyor, burada direnç görebilir

📐 Fibonacci: 0.618 ($69,152) - İdeal giriş noktası
   → Fiyat altın orana yakın, destek güçlü

📈 VWAP: +2STD ($70,056) - Aşırı alım
   → Fiyat günlük ortalamadan çok yukarıda, geri çekilme olabilir

🎲 GARCH: 2.35% volatilite (Orta)
   → Yarın fiyat %2.35 oynayabilir, normal risk

🔄 Markov: TREND (BULLISH) - %82 güven
   → Piyasa yükseliş trendinde, momentum var

📊 HVI: +1.25σ (Yüksek)
   → Geçmişe göre daha dalgalı, dikkat et

🎯 Squeeze: Breakout (Bullish)
   → Fiyat sıkışmadan çıktı, yukarı momentum başladı

Yorum: Score 72 ve LONG sinyali → Al
Ama VWAP +2STD → Aşırı alım var, geri çekilme gelebilir
Karar: Küçük pozisyonla gir veya geri çekilme bekle
```

---

## 📚 ÖZET TABLO

| Terim | Türkçe | Basit Açıklama |
|-------|--------|----------------|
| Volume Profile | Hacim Profili | Hangi fiyatlarda çok işlem yapıldı |
| Pivot Points | Dönüş Noktaları | Destek/direnç seviyeleri |
| Fibonacci | Fibonacci | Geri çekilme seviyeleri |
| VWAP | Hacim Ağırlıklı Ortalama | Bugünün gerçek fiyatı |
| GARCH | Volatilite Tahmini | Yarın ne kadar oynayacak |
| Markov | Piyasa Rejimi | Trend mi, yan mı, kaos mu |
| HVI | Volatilite Endeksi | Şu an geçmişe göre nasıl |
| Squeeze | Volatilite Sıkışması | Büyük hareket öncesi sessizlik |
| Monte Carlo | Risk Simülasyonu | 1000 senaryo testi |
| Kelly | Pozisyon Boyutu | Ne kadar para yatırmalıyım |

---

**Bu sözlüğü dashboard'a eklemek ister misiniz? Hover-over tooltips ile!** 💡
