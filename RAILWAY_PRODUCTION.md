# 🚀 RAILWAY PRODUCTION SETUP - Sadece GitHub → Railway
# Streamlit Dashboard UI Railway'de çalışıyor
# Tüm backend services Railway'de 7/24 yaşıyor

## RAILWAY'DE ÇALIŞTIR (GitHub Integration)

---

## AŞAMA 1: GITHUB'A PUSH ET

```bash
cd demir-ai
git add [136] [137] [138] [139] [140] [141] [142] [143] [144] [145]
git commit -m "feat: Add all 27 files - production ready"
git push origin main
```

✅ GitHub'da şimdi var:
- 22 Python files
- 5 Config files
- 2 Guides

---

## AŞAMA 2: RAILWAY SERVICES KONFIGÜRASYONU

Railway Dashboard'da 5 Service oluştur:

### **SERVICE 1: Streamlit Dashboard (Main UI)**

```
Name: demir-streamlit
Root Directory: /
Start Command: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0

Environment Variables:
  PORT=8501
  DATABASE_URL=postgresql://...
  BINANCE_API_KEY=...
  BINANCE_API_SECRET=...
  TELEGRAM_BOT_TOKEN=...
  FRED_API_KEY=...

Health Check: http://localhost:8501
```

✅ **Bu çalışacak → http://your-domain.railway.app**

---

### **SERVICE 2: Flask API Server**

```
Name: demir-api
Root Directory: /
Start Command: pip install gunicorn flask flask-cors && gunicorn --workers 1 --threads 4 --worker-class gthread --bind 0.0.0.0:$PORT api_server:app

Environment Variables:
  PORT=5000
  DATABASE_URL=postgresql://...
  FLASK_HOST=0.0.0.0
  FLASK_PORT=5000
  BINANCE_API_KEY=...
  (Diğer API keys)

Health Check: http://localhost:5000/health
```

✅ **Bu çalışacak → http://api-domain.railway.app**

---

### **SERVICE 3: Bot Orchestrator (Background)**

```
Name: demir-bot
Root Directory: /
Start Command: python main.py

Environment Variables:
  DATABASE_URL=postgresql://...
  BINANCE_API_KEY=...
  BINANCE_API_SECRET=...
  FRED_API_KEY=...
  TELEGRAM_BOT_TOKEN=...
  (Tüm API keys)

Memory: 512MB
CPU: 0.5
```

⚙️ **Bu 7/24 arka planda çalışır** (Streamlit'ten görülmez)

---

### **SERVICE 4: Market Stream (Background)**

```
Name: demir-stream
Root Directory: /
Start Command: python market_stream.py

Environment Variables:
  DATABASE_URL=postgresql://...

Memory: 256MB
CPU: 0.25
```

⚙️ **Real-time WebSocket, 7/24 veri akışı**

---

### **SERVICE 5: PostgreSQL Database**

```
Name: demir-postgres
Type: PostgreSQL
Version: 15

Environment:
  POSTGRES_USER=demir_user
  POSTGRES_PASSWORD=your_secure_password
  POSTGRES_DB=demir_ai
```

✅ **Database bağlantı stringi:**
```
postgresql://demir_user:your_password@demir-postgres:5432/demir_ai
```

---

## AŞAMA 3: DATABASE INITIALIZATION

Railway PostgreSQL bağlan ve çalıştır:

```bash
# Railway terminal'de
psql $DATABASE_URL -f database_init.py

# Veya manuel
psql -U demir_user -d demir_ai < database_init.py
```

Tablolar oluşturulacak:
- feature_store
- manual_trades
- signal_log
- performance_metrics
- backtesting_results
- macro_indicators

---

## AŞAMA 4: VERİFİKASYON

### **Kontrol 1: Streamlit Dashboard**

```
Browser açınız:
https://your-domain.railway.app

✅ Dashboard görünmeli
   - Real-time charts
   - Trading signals
   - Portfolio metrics
   - Performance stats
```

### **Kontrol 2: API Health**

```bash
curl https://api-domain.railway.app/health

CEVAP (200 OK):
{
  "status": "healthy",
  "service": "DEMIR AI API Server",
  "version": "1.0",
  "running": true
}
```

### **Kontrol 3: Test Endpoints**

```bash
# Signal üret
curl -X POST https://api-domain.railway.app/api/signal/generate \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT"}'

# Tüm signals
curl https://api-domain.railway.app/api/signals/all

# Portfolio stats
curl https://api-domain.railway.app/api/portfolio/stats

# Bot status
curl https://api-domain.railway.app/api/status
```

### **Kontrol 4: Bot Logs**

Railway Dashboard → demir-bot → Logs

Beklenen output:
```
🚀 DEMIR AI - MASTER ORCHESTRATOR
✅ All components initialized
📅 Scheduling jobs...
✅ Jobs scheduled successfully
✅ Orchestrator started successfully
📡 Bot is now 7/24 active!

🎯 Generating signals...
✅ BTCUSDT: BUY (78%)
✅ ETHUSDT: SELL (65%)
...
```

---

## AŞAMA 5: CANLIYA GEÇME

### **Testnet (Recommended) - Riskli değil**

```
Railway dashboard → demir-api → Environment:
  USE_TESTNET=True  ← Varsayılan (güvenli)
```

**Binance Testnet hesabı:**
- https://testnet.binancefuture.com
- Fake money, gerçek komutlar

### **Mainnet (Gerçek Para) - İLERİ**

```
SADECE eğer 1000+ işlem başarısız geçti ise:

Railway dashboard → demir-api → Environment:
  USE_TESTNET=False  ← ⚠️ GERÇEK PARA!
```

---

## AŞAMA 6: MONİTORİNG (7/24)

### **Railway Dashboard Kontrol**

```
✅ Deployment Status: Active
✅ Memory Usage: 15-30%
✅ CPU Usage: 5-15%
✅ No crashes
✅ Uptime: 99.9%
```

### **Logs Kontrol**

```
Railway → Services → demir-bot → Logs
Saat başına kontrol et
```

### **Database Check**

```bash
# Railway PostgreSQL ile connect et
SELECT COUNT(*) FROM manual_trades;
SELECT COUNT(*) FROM signal_log;
SELECT * FROM performance_metrics ORDER BY timestamp DESC LIMIT 1;
```

---

## AŞAMA 7: TELEGRAM NOTIFICATIONS

Railway özel ayar:

```
Environment Variable:
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

Bot her şey yapabilir:
✅ Signal üretildi → Telegram mesaj
✅ Trade açıldı → Telegram mesaj
✅ SL/TP hit → Telegram mesaj
✅ Error oluştu → Telegram alert
```

---

## HATA ÇÖZÜMÜ (Railway Production)

### **Problem: Streamlit çöktü**

```bash
# Railway Dashboard
Services → demir-streamlit → Restart

# Logs kontrol et
Services → demir-streamlit → Logs
```

### **Problem: API çöktü**

```bash
Services → demir-api → Restart
curl https://api-domain.railway.app/health
```

### **Problem: Bot durdu**

```bash
# Logs kontrol
Services → demir-bot → Logs

# Restart
Services → demir-bot → Restart
```

### **Problem: Database bağlantı hatası**

```bash
# PostgreSQL status
Services → demir-postgres → Active?

# CONNECTION_STRING kontrol et
Tüm services'de DATABASE_URL değişkeni doğru mu?
```

### **Problem: API rate limit**

```bash
# Trafikten ötürü error
Railway → demir-api → Add more workers

Start Command:
gunicorn --workers 4 --threads 4 ... api_server:app
```

---

## RAILWAY PRODUCTION CHECKLIST

```
✅ 5 Services created
✅ GitHub repo connected
✅ All environment variables set
✅ PostgreSQL initialized
✅ Streamlit dashboard running
✅ API server healthy
✅ Bot scheduler active
✅ Market stream connected
✅ Telegram notifications working
✅ Logs monitored
✅ Uptime tracking active
✅ Auto-restart enabled
✅ Backups configured
✅ Domain configured (if custom)
```

---

## AKIŞ ŞEMASI (Railway Production)

```
┌──────────────────────┐
│   GitHub Repository  │
│   (22 Python files)  │
└──────────┬───────────┘
           │ git push
           ▼
┌──────────────────────────────────────┐
│        RAILWAY PLATFORM              │
├──────────────────────────────────────┤
│                                      │
│  ┌──────────────────────────────┐   │
│  │ demir-streamlit (Port 8501)  │   │ ← YOU SEE THIS
│  │ - Live Dashboard             │   │ ← Arayüz burada
│  └──────────────────────────────┘   │
│           │ calls                    │
│           ▼                          │
│  ┌──────────────────────────────┐   │
│  │ demir-api (Port 5000)        │   │ ← API Backend
│  │ - Signal endpoints           │   │
│  │ - Trading endpoints          │   │
│  │ - Metrics endpoints          │   │
│  └──────────────────────────────┘   │
│                                      │
│  ┌──────────────────────────────┐   │
│  │ demir-bot (Background)       │   │ ← 7/24 çalışan
│  │ - Scheduler                  │   │ ← Bot yaşıyor
│  │ - Signal generation          │   │
│  │ - Trade execution            │   │
│  └──────────────────────────────┘   │
│                                      │
│  ┌──────────────────────────────┐   │
│  │ demir-stream (Background)    │   │ ← Real-time data
│  │ - WebSocket stream           │   │
│  │ - Live prices                │   │
│  └──────────────────────────────┘   │
│                                      │
│  ┌──────────────────────────────┐   │
│  │ demir-postgres (Database)    │   │ ← Tüm veriler
│  │ - All trades                 │   │
│  │ - All signals                │   │
│  │ - All metrics                │   │
│  └──────────────────────────────┘   │
│                                      │
└──────────────────────────────────────┘
           │
           ├─→ Binance API (Real trading)
           ├─→ FRED API (Macro data)
           ├─→ Telegram Bot (Notifications)
           └─→ Your Browser (Dashboard viewing)
```

---

## RAILWAY DEPLOYMENT COMMANDS

```bash
# GitHub'a push (Railway otomatik deploy)
git push origin main

# Railway CLI ile manual deploy
npm install -g @railway/cli
railway login
railway link  (select project)
railway up

# Logs görüntüle
railway logs -s demir-bot
railway logs -s demir-api
railway logs -s demir-streamlit

# Environment variables
railway variables

# Services status
railway status
```

---

## 🎯 SONUÇ

**YOU SEE:**
- ✅ Streamlit dashboard (your-domain.railway.app)
- ✅ Real-time charts + signals
- ✅ Portfolio metrics

**BUT BEHIND THE SCENES:**
- ✅ Bot scheduler (7/24 running)
- ✅ API endpoints (signal + trading)
- ✅ Market stream (live data)
- ✅ Database (all history saved)
- ✅ Telegram alerts (instant notifications)

**ALL ON RAILWAY - ZERO LOCAL SETUP** 🚀

GitHub push → Railway auto-deploy → Bot yaşıyor! 🤖
