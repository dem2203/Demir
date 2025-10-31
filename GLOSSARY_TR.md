# 📚 DEMIR AI TRADING BOT - TEKNİK TERİMLER KILAVUZU
**Tarih:** 31 Ekim 2025  
**Versiyon:** v4 (Phase 1)

Dashboard'daki **tüm terimlerin** ne anlama geldiği ve nasıl yorumlanacağı.

---

## 📖 İÇİNDEKİLER

1. [AI Analiz Sonuçları](#ai-analiz-sonuçları)
2. [Pozisyon Planı](#pozisyon-planı)
3. [Take Profit Seviyeleri](#take-profit-seviyeleri)
4. [Performance Dashboard](#performance-dashboard)
5. [Trade History](#trade-history)
6. [İleri Seviye Metrikler](#ileri-seviye-metrikler)
7. [Gerçek Örnekler](#gerçek-örnekler)

---

## 🎯 AI ANALİZ SONUÇLARI

### Temel Terimler

```
🎯 AI KARARI: LONG BTCUSDT
Confidence: 76% | Score: 72/100 | R/R: 1:2.62
```

| Terim | Ne Demek? | Örnek | Nasıl Yorumlanır? |
|-------|-----------|-------|-------------------|
| **LONG** | Al (yükseliş bekliyoruz) | BTC $69,500'dan AL | Fiyat yükselirse kazanırsın |
| **SHORT** | Sat (düşüş bekliyoruz) | BTC $69,500'dan SAT | Fiyat düşerse kazanırsın |
| **NEUTRAL** | Bekle (belirsiz) | Trade açma | Sinyal zayıf, bekle |
| **WAIT** | Hiçbir şey yapma | Piyasa uygun değil | Market durumu kötü |

### Confidence (Güven Seviyesi)

**Tanım:** AI'ın kararından ne kadar emin olduğu (0-100%)

| Değer | Anlamı | Ne Yapmalı? |
|-------|--------|-------------|
| **≥ 70%** | Çok emin | Güçlü sinyal, trade açabilirsin |
| **50-70%** | Orta emin | Dikkatli ol, risk yönet |
| **< 50%** | Emin değil | Trade açma! |

**Örnek:**
```
Confidence: 76%
→ AI %76 oranında emin ki fiyat yükselecek
→ Güçlü sinyal!
```

### Score (Final Skor)

**Tanım:** AI'ın 11 modülden aldığı toplam puan (0-100)

| Skor | Karar | Açıklama |
|------|-------|----------|
| **≥ 65** | LONG | Yükseliş beklentisi |
| **35-65** | NEUTRAL | Belirsiz, bekle |
| **≤ 35** | SHORT | Düşüş beklentisi |

**Nasıl Hesaplanır?**
```
Score = (Volume Profile × 0.12) + (Pivot × 0.10) + (Fib × 0.10) + 
        (VWAP × 0.08) + (News × 0.08) + (GARCH × 0.15) + 
        (Markov × 0.15) + (HVI × 0.12) + (Squeeze × 0.10)

Örnek: Score = 72/100
→ 11 modülden weighted average = 72
→ 72 ≥ 65 → LONG sinyali!
```

### R/R (Risk/Reward Oranı)

**Tanım:** Risk ettiğin her $1 için kaç $ kazanabilirsin?

| R/R | Anlamı | İyi mi? |
|-----|--------|---------|
| **1:3+** | Mükemmel | $1 risk → $3+ kazanç |
| **1:2** | İyi | $1 risk → $2 kazanç |
| **1:1.5** | Orta | $1 risk → $1.5 kazanç |
| **1:1** | Zayıf | $1 risk → $1 kazanç (riskli) |
| **< 1:1** | Kötü | Trade açma! |

**Örnek:**
```
R/R: 1:2.62
→ $10 risk ediyorsun
→ $26.20 kazanabilirsin
→ Mükemmel oran! ✅
```

---

## 💼 POZİSYON PLANI

### Temel Terimler

```
Entry: $69,500
SL: $68,200 (-1.87%)
Position: $485
Risk: $9.36
```

| Terim | Ne Demek? | Örnek | Neden Önemli? |
|-------|-----------|-------|---------------|
| **Entry** | Giriş fiyatı | $69,500 | Trade'i bu fiyattan aç |
| **SL** | Stop Loss (zarar durdur) | $68,200 | Fiyat buraya gelirse otomatik kapat |
| **Position** | Pozisyon büyüklüğü | $485 | Trade için toplam yatırım |
| **Risk** | Maksimum zarar | $9.36 | SL'e vurursa kaybedersin |

### Stop Loss (SL) Detayı

**Tanım:** Maksimum kaybını sınırlamak için otomatik kapanma fiyatı

**Nasıl Hesaplanır?**
```
LONG örnek:
Entry: $69,500
SL: $68,200
Risk: $69,500 - $68,200 = $1,300 per BTC
SL %: ($68,200 - $69,500) / $69,500 = -1.87%

Position: $485
Position size: $485 / $69,500 = 0.00698 BTC
Max loss: 0.00698 × $1,300 = $9.07
```

**Neden Gerekli?**
- ❌ SL yoksa → Sınırsız kayıp riski
- ✅ SL varsa → Maksimum kaybın belli ($9.36)

---

## 🎯 TAKE PROFIT SEVİYELERİ

### TP1, TP2, TP3 Nedir?

**Tanım:** Kar almak için belirlenen hedef fiyatlar

```
TP1: $70,800 (+1.87%) [1:1] → Close 50%
TP2: $71,902 (+3.12%) [1:1.62] → Close 30%
TP3: $73,904 (+6.34%) [1:2.62] → Close 20%
```

| Seviye | Ne Zaman Gelir? | Ne Yapmalı? | Neden? |
|--------|-----------------|-------------|--------|
| **TP1** | Entry + 1× Risk | Pozisyonun %50'sini kapat | Kar garantiye al |
| **TP2** | Entry + 1.618× Risk | %30'unu daha kapat | Fibonacci golden ratio |
| **TP3** | Entry + 2.618× Risk | Kalan %20'yi kapat | Maksimum kar hedefi |

### Hesaplama Örneği

```
Entry: $69,500
SL: $68,200
Risk: $1,300

TP1 = Entry + (Risk × 1.0) = $69,500 + $1,300 = $70,800
TP2 = Entry + (Risk × 1.618) = $69,500 + $2,103 = $71,603
TP3 = Entry + (Risk × 2.618) = $69,500 + $3,404 = $72,904
```

### Fibonacci Mantığı

**Neden 1.618 ve 2.618?**

- **1.618** = Fibonacci golden ratio (doğada ve piyasada tekrarlanan oran)
- **2.618** = Fibonacci extension (güçlü direnç seviyeleri)

**Örnek:**
```
Tarihte BTC'nin %70'i:
- TP1'e ulaştı (1:1)
- %45'i TP2'ye ulaştı (1:1.62)
- %20'si TP3'e ulaştı (1:2.62)

Bu yüzden pozisyon kademeli kapatılır:
TP1: %50 (çoğu buraya gelir)
TP2: %30 (daha az gelir)
TP3: %20 (çok az gelir)
```

### Trailing Stop Nedir?

```
📈 Trailing Stop: TP1 sonrası SL'i entry'e çek.
                  TP2 sonrası SL'i TP1'e çek.
```

**Tanım:** Stop Loss'u kar ettikçe yukarı çekmek

**Örnek:**
```
1. Trade açtın: Entry $69,500, SL $68,200
2. TP1 geldi ($70,800) → SL'i $69,500'a çek (breakeven)
   → Artık kayıp riski YOK! ✅
3. TP2 geldi ($71,902) → SL'i $70,800'a çek (TP1)
   → Minimum kar garantilendi! ✅
```

---

## 📊 PERFORMANCE DASHBOARD

### Sidebar Widget

```
📊 Win Rate: 65.2%
   15W / 8L

💰 Total PNL: $2,485.50
   23 Trades

📈 Sharpe Ratio: 3.29
   Profit Factor: 2.15
```

### Win Rate (Kazanma Oranı)

**Tanım:** Kaç trade kazandın? (%)

**Formül:**
```
Win Rate = (Kazanan Trade Sayısı / Toplam Trade) × 100

Örnek:
15 kazanan, 8 kaybeden, 23 total
Win Rate = (15 / 23) × 100 = 65.2%
```

| Win Rate | Yorumu | Durumu |
|----------|--------|--------|
| **≥ 60%** | Çok iyi | Başarılı sistem ✅ |
| **50-60%** | İyi | Kabul edilebilir |
| **40-50%** | Orta | Risk yönetimi kritik |
| **< 40%** | Kötü | Stratejiyi gözden geçir ❌ |

**Önemli Not:**
```
%50 win rate bile karlı olabilir!
Neden? → R/R oranı 1:2+ ise

Örnek:
Win Rate: %50 (5 kazanan, 5 kaybeden)
Avg Win: $100
Avg Loss: $50
Net PNL: (5 × $100) - (5 × $50) = $250 ✅
```

### Total PNL (Toplam Kar/Zarar)

**Tanım:** Şimdiye kadar toplam kazandığın/kaybettiğin para

**Hesaplama:**
```
Total PNL = Σ(Her trade'in PNL'i)

Örnek:
Trade 1: +$120
Trade 2: -$45
Trade 3: +$85
Total PNL = $120 - $45 + $85 = $160
```

### Sharpe Ratio (Risk-Adjusted Getiri)

**Tanım:** Her birim risk için ne kadar getiri elde ettin?

**Formül:**
```
Sharpe = (Ortalama Getiri - Risk-Free Rate) / Standart Sapma

Basitçe:
Sharpe = Ortalama PNL / PNL Volatilitesi
```

| Sharpe | Yorumu | Durumu |
|--------|--------|--------|
| **> 3** | Mükemmel | Az risk, çok kar ✅ |
| **2-3** | Çok iyi | İyi risk/getiri dengesi |
| **1-2** | İyi | Kabul edilebilir |
| **0-1** | Zayıf | Risk yüksek |
| **< 0** | Kötü | Risk > Getiri ❌ |

**Örnek:**
```
Sharpe: 3.29
→ Her 1 birim risk için 3.29 birim getiri
→ Warren Buffett ~0.76 (karşılaştırma için!)
→ 3.29 = Profesyonel seviye! ✅
```

### Profit Factor (Kar Faktörü)

**Tanım:** Toplam karın / Toplam zarara oranı

**Formül:**
```
Profit Factor = Σ(Kazanan Trade'ler) / Σ(Kaybeden Trade'ler)

Örnek:
Kazançlar: $500 + $300 + $200 = $1,000
Zararlar: $150 + $100 + $200 = $450
Profit Factor = $1,000 / $450 = 2.22
```

| Profit Factor | Yorumu | Durumu |
|---------------|--------|--------|
| **> 2.0** | Mükemmel | Her $1 kayıp için $2+ kazanç ✅ |
| **1.5-2.0** | İyi | Karlı sistem |
| **1.0-1.5** | Orta | Barely profitable |
| **< 1.0** | Kötü | Zarar ediyorsun ❌ |

**Örnek:**
```
Profit Factor: 2.15
→ Kaybettiğin her $1 için $2.15 kazanıyorsun
→ %115 net kar yapıyorsun! ✅
```

---

## 📜 TRADE HISTORY

### Tablo Sütunları

| Sütun | Açıklama | Örnek |
|-------|----------|-------|
| **ID** | Trade numarası | #5 |
| **Timestamp** | Trade zamanı | 2025-10-31 23:15:00 |
| **Symbol** | Hangi coin | BTCUSDT |
| **Signal** | LONG/SHORT | LONG |
| **Confidence** | AI güven (0-1) | 0.76 = %76 |
| **Final Score** | AI skor (0-100) | 72.5/100 |
| **Entry Price** | Giriş fiyatı | $69,500 |
| **Stop Loss** | SL fiyatı | $68,200 |
| **Position Size** | Yatırım miktarı | $485 |
| **Status** | Durum | PENDING/WIN/LOSS |
| **PNL USD** | Kar/zarar ($) | +$23.80 |
| **PNL %** | Kar/zarar (%) | +4.91% |

### Status Değerleri

| Status | Anlamı | Ne Zaman? |
|--------|--------|-----------|
| **PENDING** | Açık trade | Henüz kapanmadı |
| **WIN** | Kazandı | TP seviyelerine ulaştı |
| **LOSS** | Kaybetti | SL'e vurdu |
| **BREAKEVEN** | Başabaş | Kar/zarar = $0 |

---

## 🧮 İLERİ SEVİYE METRİKLER

### Average Win / Average Loss

**Tanım:** Ortalama kazanç ve kayıp miktarları

**Formül:**
```
Avg Win = Σ(Kazanan trade'ler) / Kazanan trade sayısı
Avg Loss = Σ(Kaybeden trade'ler) / Kaybeden trade sayısı
```

**Örnek:**
```
Kazananlar: $85, $120, $95
Avg Win = ($85 + $120 + $95) / 3 = $100

Kaybedenler: -$40, -$35, -$50
Avg Loss = (-$40 - $35 - $50) / 3 = -$41.67
```

**İdeal Oran:**
```
Avg Win / |Avg Loss| ≥ 2.0
$100 / $41.67 = 2.40 ✅ (Mükemmel!)
```

### Max Drawdown (Maksimum Düşüş)

**Tanım:** Portföyündeki en büyük tepe-dip düşüşü

**Örnek:**
```
Portfolio değeri:
$10,000 (başlangıç)
→ $12,500 (tepe)
→ $10,200 (dip)
→ $13,000 (şimdi)

Max Drawdown = ($12,500 - $10,200) / $12,500 = 18.4%
```

**Yorumu:**
```
Max DD: 18.4%
→ En kötü durumda portfolio %18.4 düştü
→ <20% = Kabul edilebilir ✅
→ >30% = Çok riskli ❌
```

---

## 🎓 GERÇEK ÖRNEKLER

### Örnek 1: Başarılı LONG Trade

```
📈 AI ANALİZ:
LONG BTCUSDT | Confidence: 76% | Score: 72/100 | R/R: 1:2.62

💼 POZİSYON:
Entry: $69,500
SL: $68,200 (-1.87%)
Position: $485 (0.00698 BTC)
Risk: $9.07

🎯 TP SEVİYELERİ:
TP1: $70,800 (+1.87%) ✅ HIT!
  → Close 50% ($242.50) → Kar: $9.07
  → SL'i $69,500'a çek (breakeven)

TP2: $71,902 (+3.12%) ✅ HIT!
  → Close 30% ($145.50) → Kar: $6.98
  → SL'i $70,800'a çek (TP1 seviyesi)

TP3: $73,904 (+6.34%) ✅ HIT!
  → Close 20% ($97) → Kar: $8.50
  → Tüm pozisyon kapandı

SONUÇ:
Toplam Kar: $9.07 + $6.98 + $8.50 = $24.55
Risk: $9.07
Actual R/R: $24.55 / $9.07 = 1:2.71 ✅
Status: WIN 🎉
```

### Örnek 2: Stop Loss'a Vuran Trade

```
📉 AI ANALİZ:
SHORT ETHUSDT | Confidence: 58% | Score: 42/100 | R/R: 1:2.0

💼 POZİSYON:
Entry: $3,850
SL: $3,920 (+1.82%)
Position: $485 (0.126 ETH)
Risk: $8.82

Fiyat Hareketi:
$3,850 (entry)
→ $3,870 (+0.52%)
→ $3,900 (+1.30%)
→ $3,920 (SL HIT) ❌

SONUÇ:
Kayıp: -$8.82
Risk: $8.82
Loss = Tam risk miktarı (beklendiği gibi)
Status: LOSS ❌

DERS:
✅ SL çalıştı → Kayıp sınırlandı
✅ Daha fazla kaybetmedi ($8.82'den fazla)
✅ Risk yönetimi başarılı!
```

---

## 📈 PERFORMANS YORUMLAMA ÖRNEĞİ

### 1 Aylık Sonuçlar

```
📊 PERFORMANCE SUMMARY:

Total Trades: 47
Winning: 31 (66.0%)
Losing: 16 (34.0%)

Total PNL: $3,285.50
Avg Win: $142.30
Avg Loss: $52.80
Max Win: $384.20
Max Loss: $95.60

Sharpe Ratio: 3.45
Profit Factor: 2.28
Max Drawdown: 15.2%
```

**YORUM:**

✅ **Win Rate: 66%** = Mükemmel! (>60%)

✅ **Profit Factor: 2.28** = Her $1 kayıp için $2.28 kazanç

✅ **Sharpe: 3.45** = Profesyonel seviye risk-adjusted getiri

✅ **Max DD: 15.2%** = Kabul edilebilir düşüş (<20%)

✅ **Avg Win/Loss: 2.69** = Kazançlar kayıpların 2.69 katı

**SONUÇ:** Sistem çok başarılı çalışıyor! 🎯✅

---

## 🎯 HİZLI REFERANS TABLOSU

### Hangi Değer İyi/Kötü?

| Metrik | 🔥 Mükemmel | ✅ İyi | ⚠️ Orta | ❌ Kötü |
|--------|-------------|--------|---------|---------|
| **Win Rate** | ≥60% | 50-60% | 40-50% | <40% |
| **R/R** | ≥1:2.5 | 1:2 | 1:1.5 | <1:1 |
| **Sharpe** | >3 | 2-3 | 1-2 | <1 |
| **Profit Factor** | >2 | 1.5-2 | 1-1.5 | <1 |
| **Max DD** | <15% | 15-20% | 20-30% | >30% |
| **Confidence** | ≥70% | 60-70% | 50-60% | <50% |

---

## 📚 SÖZLÜK (A-Z)

| Terim | Türkçe | Açıklama |
|-------|--------|----------|
| **Entry** | Giriş | Trade açma fiyatı |
| **Exit** | Çıkış | Trade kapama fiyatı |
| **LONG** | Al | Yükseliş beklentisi |
| **SHORT** | Sat | Düşüş beklentisi |
| **SL** | Stop Loss | Zarar durdur |
| **TP** | Take Profit | Kar al |
| **PNL** | Profit & Loss | Kar/Zarar |
| **R/R** | Risk/Reward | Risk/Kazanç oranı |
| **DD** | Drawdown | Düşüş |
| **Win Rate** | Kazanma Oranı | Kazanan trade % |
| **Confidence** | Güven | AI'ın emin olma oranı |
| **Score** | Skor | AI final puanı |

---

## ❓ SIKÇA SORULAN SORULAR

### S1: Win rate %50 altı olabilir mi?

**C:** Evet! R/R yüksekse karlı olabilir.

Örnek:
```
Win Rate: %40 (4 kazanan, 6 kaybeden)
Avg Win: $100, Avg Loss: $30
Net: (4×$100) - (6×$30) = $400 - $180 = $220 ✅ KAR!
```

### S2: Sharpe ratio ne kadar olmalı?

**C:** 
- **>2.0** = İyi
- **>3.0** = Mükemmel
- Warren Buffett'in Sharpe: ~0.76

### S3: Profit factor 1.5 yeterli mi?

**C:** Evet, ama ideal >2.0

```
PF: 1.5 → Her $1 kayıp için $1.50 kazanç (%50 net kar)
PF: 2.0 → Her $1 kayıp için $2.00 kazanç (%100 net kar) ✅
```

### S4: TP3'e hiç ulaşmıyor, normal mi?

**C:** Evet! Normal.

```
Tarihte:
TP1: %70 ulaşır
TP2: %40 ulaşır
TP3: %15 ulaşır

Bu yüzden:
TP1: %50 pozisyon kapat (çoğu gelir)
TP2: %30 kapat (daha az gelir)
TP3: %20 kapat (az gelir ama çok kar)
```

---

**🔱 DEMIR AI Trading Bot v4**  
**Phase 1: Trade History + Performance Tracking**  
**© 2025 | Tüm terimler açıklandı!**
