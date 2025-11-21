# 🛤️ DEMIR AI v8.0 - RAILWAY ENVIRONMENT VARIABLES SETUP

## 🎯 OVERVIEW

Bu doküman DEMIR AI v8.0'u Railway'de deploy etmek için gerekli environment variable'larını içerir.

**⚠️ SECURITY NOTICE: Bu dosya sadece placeholder içerir. Gerçek API key'lerinizi ASLA GitHub'a yazmayin!**

**Toplam Variable Sayısı:** 35+
**Son Güncelleme:** 2025-11-21
**Versiyon:** 8.0

---

## 🔑 1. CORE APPLICATION SETTINGS

```bash
# Application Version & Mode
VERSION=8.0
APP_NAME="DEMIR AI"
ENVIRONMENT=production

# Operational Mode
ADVISORY_MODE=true              # true = sadece analiz, false = oto-trading
DEBUG_MODE=false                # Production'da mutlaka false

# System Configuration
MAX_THREADS=20                  # Background thread sayısı
MAX_PROCESSES=4                 # Process pool boyutu
CACHE_TTL=300                   # Cache süresi (saniye)
RATE_LIMIT_ENABLED=true         # API rate limiting
```

---

## 📊 2. DATABASE (PostgreSQL)

```bash
# PostgreSQL Connection
DATABASE_URL=postgresql://user:password@host:5432/demir_ai
# Railway otomatik sağlıyor, manuel set etmeyin

# Database Pool Settings (Optional)
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
```

---

## 🔄 3. REDIS CACHE (v8.0 NEW)

```bash
# Redis Connection
REDIS_URL=redis://localhost:6379/0
# Railway Redis eklersen otomatik set eder

# Cache Settings
REDIS_TTL=300                   # Default cache expiry (seconds)
REDIS_MAX_CONNECTIONS=50
```

---

## 💱 4. EXCHANGE APIs

```bash
# Binance
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_secret_here
BINANCE_TESTNET=false           # Production'da false

# Bybit
BYBIT_API_KEY=your_bybit_api_key_here
BYBIT_API_SECRET=your_bybit_secret_here
BYBIT_TESTNET=false

# Coinbase
COINBASE_API_KEY=your_coinbase_api_key_here
COINBASE_API_SECRET=your_coinbase_secret_here
```

---

## 🐳 5. v8.0 PHASE 1: SMART MONEY & RISK APIs

```bash
# Glassnode (On-Chain Data)
GLASSNODE_API_KEY=your_glassnode_key_here
# https://studio.glassnode.com/settings/api
# Plan: Basic ($39/mo) veya higher

# CoinGlass (Exchange Reserves)
COINGLASS_API_KEY=your_coinglass_key_here
# https://www.coinglass.com/pricing
# Plan: Pro ($99/mo)

# Whale Alert
WHALE_ALERT_API_KEY=your_whale_alert_key_here
# https://whale-alert.io/pricing
# Plan: Basic ($9/mo) veya higher
```

---

## 💬 6. v8.0 PHASE 1: SENTIMENT APIs

```bash
# CryptoPanic
CRYPTOPANIC_API_KEY=your_cryptopanic_key_here
# https://cryptopanic.com/developers/api/
# Plan: Free (limited) veya Pro ($59/mo)

# NewsAPI
NEWSAPI_API_KEY=your_newsapi_key_here
# https://newsapi.org/pricing
# Plan: Developer (Free) veya Business ($449/mo)
```

---

## 📊 7. v8.0 PHASE 4: ON-CHAIN & DEFI APIs

```bash
# Etherscan
ETHERSCAN_API_KEY=your_etherscan_key_here
# https://etherscan.io/apis
# Plan: Free (5 calls/sec)

# DeFiLlama (TVL Data)
# DeFiLlama is FREE - no API key needed
# But rate limited to 300 calls/5min
DEFILLAMA_RATE_LIMIT=300
```

---

## 📈 8. MARKET DATA APIs

```bash
# CoinMarketCap
CoinMarketCap_API_KEY=your_coinmarketcap_key_here
# https://coinmarketcap.com/api/pricing/
# Plan: Basic ($29/mo) recommended

# Alpha Vantage (Macro Data)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
# https://www.alphavantage.co/premium/
# Plan: Free (5 calls/min) or Premium

# Twelve Data (Market Data)
TWELVE_DATA_API_KEY=your_twelve_data_key_here
# https://twelvedata.com/pricing
# Plan: Basic ($49/mo) or higher
```

---

## 📢 9. TELEGRAM BOT

```bash
# Telegram Bot Settings
TELEGRAM_ENABLED=true
TELEGRAM_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Botı oluşturma: @BotFather ile konuş
# Chat ID bulma: @userinfobot ile mesajlaş
```

---

## 🔒 10. SECURITY & SESSION

```bash
# Flask Secret Key
FLASK_SECRET_KEY=generate_random_64_char_string_here
# Python ile: import os; os.urandom(32).hex()

# JWT Token (Optional - gelecek için)
JWT_SECRET_KEY=another_random_string_here
```

---

## 🎓 11. FEATURE FLAGS

```bash
# Module Enable/Disable Flags
ENABLE_SMART_MONEY=true
ENABLE_RISK_ENGINE=true
ENABLE_SENTIMENT_V2=true
ENABLE_ARBITRAGE=true
ENABLE_ONCHAIN_PRO=true
ENABLE_PATTERN_RECOGNITION=true

# Performance Optimization
ENABLE_REDIS_CACHE=true
ENABLE_ULTRA_LOW_LATENCY=true

# AI Features
ENABLE_REINFORCEMENT_LEARNING=true
ENABLE_ENSEMBLE_MODEL=true
```

---

## 🚦 12. THRESHOLDS & LIMITS

```bash
# Trading Opportunity Thresholds
MIN_OPPORTUNITY_CONFIDENCE=0.75
MIN_RISK_REWARD_RATIO=2.0
MAX_POSITION_SIZE=0.05          # 5% of portfolio

# Smart Money Thresholds
WHALE_MIN_TRANSACTION=10000000  # $10M minimum
ORDERBOOK_WHALE_THRESHOLD=500000 # $500K

# Flow Detection
FLOW_STALE_LIMIT_MINUTES=30

# Arbitrage
MIN_ARBITRAGE_SPREAD=0.005      # 0.5% minimum
```

---

## ⚙️ 13. ADVANCED CONFIGURATION

```bash
# WebSocket Settings
WS_PING_INTERVAL=25
WS_PING_TIMEOUT=60
WS_MAX_RECONNECT_ATTEMPTS=Infinity

# Backtest Settings
BACKTEST_START_DATE=2022-01-01
BACKTEST_INITIAL_CAPITAL=10000
BACKTEST_COMMISSION=0.001       # 0.1%

# ML Training
ML_RETRAIN_INTERVAL=86400       # 24 hours
ML_MIN_TRAINING_SAMPLES=1000
```

---

## 📝 14. LOGGING & MONITORING

```bash
# Logging
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json                 # json or text
LOG_TO_FILE=true

# Sentry (Optional Error Tracking)
SENTRY_DSN=your_sentry_dsn_here
SENTRY_ENVIRONMENT=production

# Prometheus (Optional Metrics)
PROMETHEUS_ENABLED=false
PROMETHEUS_PORT=9090
```

---

## 🛠️ RAILWAY DEPLOYMENT CHECKLIST

### 1. Railway Project Setup

1. **Create New Project**
   - Go to https://railway.app/new
   - Connect GitHub repo: `dem2203/Demir`
   - Select `main` branch

2. **Add PostgreSQL**
   - Click "New" → "Database" → "PostgreSQL"
   - Railway otomatik `DATABASE_URL` set eder

3. **Add Redis (Optional but Recommended)**
   - Click "New" → "Database" → "Redis"
   - Railway otomatik `REDIS_URL` set eder

### 2. Environment Variables Ekleme

**Railway Dashboard'da:**

1. Project Settings → Variables sekmesi
2. Senin API key'lerin zaten orada olmalı!
3. Eksikse sadece şunları ekle:
   - `VERSION=8.0`
   - `ENVIRONMENT=production`
   - `ADVISORY_MODE=true`
   - `DEBUG_MODE=false`

### 3. Build & Deploy Settings

**Railway Project Settings:**

- **Root Directory:** `/` (default)
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py`
- **Port:** Railway otomatik PORT assign eder
- **Health Check Path:** `/health`

### 4. Domain Setup (Optional)

1. Settings → Networking
2. "Generate Domain" veya custom domain ekle
3. SSL otomatik aktif olur

### 5. Deploy!

- Git push yaptığında Railway otomatik deploy eder
- Deploy loglarını izle: Deploy sekmesi
- Beklenen log: "DEMIR AI v8.0 - LOGGING SYSTEM INITIALIZED"

---

## ⚠️ ÖNEMLİ NOTLAR

### 🔒 Güvenlik En İyileri

1. **ASLA GitHub'a API key yazma**
   - ✅ Railway Variables kullan
   - ✅ Environment variables olarak sakla
   - ❌ config.py'ye hardcode etme
   - ❌ README'ye yazma
   - ❌ .env dosyasını commit etme

2. **API Key'leri Koruma**
   - Railway Variables private
   - Sadece deployment'ta kullanılır
   - Git history'de görünmez
   - Log'larda maskelenir

3. **.gitignore Kontrol**
   ```
   .env
   .env.local
   API.txt
   *_API_KEY*
   ```

### API Key'leri Nereden Alınır?

1. **Ücretsiz (Limitsiz veya Çok Düşük Limit):**
   - DeFiLlama (Free)
   - Etherscan (Free)
   - Alpha Vantage (Free, 5 call/min)
   - NewsAPI Developer (Free, limited)

2. **Düşük Maliyet ($10-50/mo):**
   - Whale Alert Basic ($9/mo)
   - CoinMarketCap Basic ($29/mo)
   - Glassnode Basic ($39/mo)
   - Twelve Data Basic ($49/mo)

3. **Yüksek Maliyet ($99+/mo):**
   - CoinGlass Pro ($99/mo)
   - NewsAPI Business ($449/mo)

### Minimum Gerekli API'ler

**Sadece temel fonksiyonlar için:**

```bash
# Exchanges (ZORUNLU)
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret

# Diğer API'ler optional
# Sistem graceful degradation yapar
```

### Production Hardening

1. **Rate Limiting:**
   - Railway'de Cloudflare kullan
   - DDoS protection aktif et

2. **Monitoring:**
   - Railway Metrics üzerinden CPU/RAM izle
   - Sentry ekle error tracking için

3. **Backup:**
   - PostgreSQL otomatik backup (Railway Pro)
   - Manuel backup: `pg_dump`

4. **Scaling:**
   - Railway otomatik scale yapar
   - High traffic için Pro plan gerekli

---

## 🐛 TROUBLESHOOTING

### 1. Build Fails

**Hata:** `ModuleNotFoundError`
- **Çözüm:** requirements.txt güncelle
- Check: `pip freeze > requirements.txt`

### 2. Database Connection Error

**Hata:** `psycopg2.OperationalError`
- **Çözüm:** Railway PostgreSQL eklenmiş mi kontrol et
- `DATABASE_URL` otomatik set olmalı

### 3. API Key Errors

**Hata:** `401 Unauthorized` veya `403 Forbidden`
- **Çözüm:** API key doğru mu kontrol et
- Quota aşıldı mı check et
- Railway Variables'da doğru tanımlı mı?

### 4. Redis Connection Error

**Hata:** `redis.exceptions.ConnectionError`
- **Çözüm:** Railway Redis eklenmemiş olabilir
- Sistem Redis olmadan da çalışır (graceful fallback)

### 5. Import Errors

**Hata:** `NameError: name 'Tuple' is not defined`
- **Çözüm:** ✅ Düzeltildi! Latest commit'i deploy et

### 6. High CPU Usage

- `MAX_THREADS` azalt (20 → 10)
- `MAX_PROCESSES` azalt (4 → 2)
- Gereksiz feature'ları disable et

---

## 📞 SUPPORT

**Issues:** https://github.com/dem2203/Demir/issues

**Email:** idemir2203@gmail.com

**Live Dashboard:** https://demir1988.up.railway.app/

---

## ✅ FINAL CHECKLIST

Deploy etmeden önce:

- [ ] Railway project oluşturuldu
- [ ] GitHub repo bağlandı (dem2203/Demir)
- [ ] PostgreSQL database eklendi
- [ ] Redis eklendi (optional)
- [ ] **API key'ler Railway Variables'da** (GitHub'da DEĞİL!)
- [ ] `ADVISORY_MODE=true` set edildi
- [ ] `DEBUG_MODE=false` set edildi
- [ ] Core settings eklendi (VERSION, ENVIRONMENT, etc.)
- [ ] Build & Deploy ayarları doğru
- [ ] Latest commit deployed (Tuple fix)

**Railway deploy'dan sonra:**

- [ ] Logs kontrol et: "DEMIR AI v7.0/8.0 initialized" görünmeli
- [ ] Dashboard açılıyor mu test et
- [ ] WebSocket bağlantısı çalışıyor mu
- [ ] API endpoints test et
- [ ] Telegram notifications çalışıyor mu (opsiyonel)

---

## 🔑 SENİN API KEY'LERİN

**✅ Railway Variables'da zaten mevcut:**

- Binance
- Bybit
- Coinbase
- CoinMarketCap
- Alpha Vantage
- Twelve Data
- Yahoo Finance
- CoinGlass
- DexCheck
- OpenSea
- News API
- Crypto Alert
- Finnhub
- FRED
- Twitter/X (optional)
- Telegram

**Toplam: 20+ API key güvende! 🔒**

**Eksikse sadece core settings ekle:**
```bash
VERSION=7.0
ENVIRONMENT=production
ADVISORY_MODE=true
DEBUG_MODE=false
```

---

**Made with ❤️ by DEMIR AI Team**

**Version:** 8.0 | **Date:** 2025-11-21 | **Status:** 🟢 Secure & Production Ready
