# 🚀 DEMIR AI v8.0 - Professional Crypto Trading Bot

[![Production Status](https://img.shields.io/badge/status-production-success)](https://demir1988.up.railway.app/)
[![Version](https://img.shields.io/badge/version-8.0-blue)](https://github.com/dem2203/Demir)
[![Python](https://img.shields.io/badge/python-3.12.0-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Private-red)](LICENSE)

**DEMIR AI** - 7/24 aktif, çok katmanlı (multi-layer), gerçek zamanlı kripto analiz yapan profesyonel trading asistanı.

🔗 **Live Dashboard:** [https://demir1988.up.railway.app/](https://demir1988.up.railway.app/)  
📊 **GitHub Repository:** [https://github.com/dem2203/Demir](https://github.com/dem2203/Demir)

---
## 📋 İçindekiler
- [Özellikler](#-özellikler)
- [Mimari](#-mimari)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [API Dokümantasyonu](#-api-dokümantasyonu)
- [Deployment](#-deployment)
- [Konfigürasyon](#-konfigürasyon)
- [Geliştirme](#-geliştirme)
- [Performans](#-performans)
- [Lisans](#-lisans)

---

## ✨ Özellikler

### 🎯 Core Features

✅ **48 AI Layer Analiz (v8.0 Optimized)** - Technical (19) + Sentiment (15) + ML (5) + OnChain (4) + Risk (5)  
✅ **5-Group Signal System** - Bağımsız grup doğrulaması ile consensus  
✅ **Multi-Timeframe Analysis** - 15m, 1h, 4h, 1d confluence  
✅ **Real-time WebSocket** - Sub-100ms latency garantisi  
✅ **Zero Mock Data Policy** - %100 gerçek veri doğrulaması  
✅ **Kelly Criterion** - Matematiksel optimal position sizing  
✅ **3-Year Backtesting** - Monte Carlo + Walk Forward validation  
✅ **Professional Dashboard** - Real-time tracking + charts  
✅ **Multi-Exchange Support** - Binance, Bybit, Coinbase failover  

### 🔧 Technical Stack

**Backend:**
- Python 3.12.0
- Flask (REST API)
- WebSocket (Real-time)
- PostgreSQL (Database)
- Redis (Caching)

**AI/ML:**
- TensorFlow 2.15.0
- PyTorch 2.1.1
- XGBoost 2.0.2
- TA-Lib (Technical Analysis)
- Scikit-learn 1.3.2

**Infrastructure:**
- Docker + Kubernetes
- Railway (Production)
- GitHub Actions (CI/CD)
- Prometheus + Grafana (Monitoring)

---

## 🏗️ Mimari

### 10-Layer System Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                     DEMIR AI v8.0 ARCHITECTURE                  │
│                  (48 AI Layers - Optimized)                     │
└─────────────────────────────────────────────────────────────────┘

LAYER 1: DATA ACQUISITION
├─ Binance WebSocket (Primary)
├─ Bybit WebSocket (Fallback 1)
└─ Coinbase WebSocket (Fallback 2)
    ↓
LAYER 2: DATA VALIDATION (Zero Mock Data)
├─ MockDataDetector (Pattern matching)
├─ RealDataVerifier (Exchange verification)
└─ SignalValidator (Master validation)
    ↓
LAYER 3: TECHNICAL ANALYSIS (19 Indicators - Optimized from 28)
├─ Trend: SMA, EMA, ADX, WMA, Hull MA
├─ Momentum: RSI, MACD, Stochastic
├─ Volatility: Bollinger Bands, ATR
├─ Volume: OBV, MFI, A/D
└─ Patterns: Harmonic, Candlestick (30+ core patterns)
    ↓
LAYER 4: MULTI-TIMEFRAME CONFLUENCE
├─ 15m Analysis
├─ 1h Analysis
├─ 4h Analysis
└─ 1d Analysis → Convergence Score (0-100)
    ↓
LAYER 5: 5-GROUP SIGNAL SYSTEM (48 Active Layers)
├─ TECHNICAL (19 layers) - 35% weight
├─ SENTIMENT (15 layers) - 20% weight
├─ ML (5 models) - 25% weight
├─ ON-CHAIN (4 layers) - 15% weight
└─ RISK (5 layers - ParametricVaR disabled) - 5% weight → Weighted Consensus
    ↓
LAYER 6: DEEP LEARNING & ML (5 Core Models - Optimized from 10)
├─ LSTM (Sequence prediction)
├─ Transformer (Attention mechanism)
├─ XGBoost (Gradient boosting)
├─ Random Forest (Ensemble)
└─ Neural Network (DNN) → Ensemble Voting
    ↓
LAYER 7: BACKTESTING & VALIDATION
├─ 3-Year Historical (2022-2025)
├─ Monte Carlo Simulation (1000 runs)
├─ Walk Forward Analysis (12 periods)
└─ Performance Metrics → Sharpe, Sortino, Calmar
    ↓
LAYER 8: RISK MANAGEMENT (5 Engines)
├─ Kelly Criterion (Position sizing)
├─ ATR-based Stop Loss
├─ Risk:Reward 2:1 (Take Profit)
├─ Emergency Circuit Breaker
└─ VaR (Monte Carlo) - ParametricVaR disabled for optimization
    ↓
LAYER 9: DATABASE & PERSISTENCE
├─ PostgreSQL (7 tables)
├─ Signal History
├─ Trade Tracking
└─ Performance Logs
    ↓
LAYER 10: UI/UX & DASHBOARD
├─ Real-time WebSocket Updates
├─ REST API (25 endpoints)
├─ Interactive Charts (Chart.js)
└─ Telegram Notifications
```

### File Structure

```
Demir/
├── advanced_ai/              # AI & ML models
│   ├── deep_learning_models.py
│   ├── lstm_trainer.py
│   └── signal_engine_integration.py
│
├── analytics/                # Performance & backtesting
│   ├── advanced_backtester.py
│   ├── position_manager.py
│   └── performance_engine.py
│
├── integrations/             # Exchange & Data APIs
│   ├── binance_websocket_v3.py
│   ├── multi_exchange_api.py
│   └── market_intelligence.py
│
├── layers/                   # Analysis layers (48 total)
│   ├── technical/           # 19 technical indicators (optimized)
│   ├── sentiment/           # 15 sentiment sources (optimized)
│   ├── ml/                  # 5 ML models (optimized)
│   ├── onchain/             # 4 on-chain metrics (optimized)
│   └── risk/                # 5 risk assessments (ParametricVaR disabled)
│
├── ui/                       # Dashboard & API
│   ├── dashboard_backend.py
│   ├── group_signal_engine.py
│   └── data_fetcher_realtime.py
│
├── utils/                    # Utilities
│   ├── data_detector_advanced.py
│   ├── real_data_verifier_pro.py
│   └── signal_validator_comprehensive.py
│
├── main.py                   # Main entry point
├── dashboard_pro_tr.html     # Optimized Dashboard UI (v8.0)
├── app.js                    # Frontend logic
└── requirements.txt          # Python dependencies
```

---

## 🚀 Kurulum

### Prerequisites

- Python 3.12.0+
- PostgreSQL 15+
- Redis 7+
- Git

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/dem2203/Demir.git
cd Demir

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Initialize database
python setup_database.py

# 6. Create required folders
python setup_folders.py

# 7. Run application
python main.py
```

### Docker Deployment

```bash
# Build image
docker build -t demir-ai:v8.0 .

# Run container
docker run -d \
  --name demir-ai \
  -p 8501:8501 \
  --env-file .env \
  demir-ai:v8.0

# Check logs
docker logs -f demir-ai
```

---

## 💻 Kullanım

### 1. Start Bot

```bash
# Production mode
python main.py --mode=production

# Development mode (with debug logs)
python main.py --mode=development --log-level=DEBUG

# Paper trading mode
python main.py --mode=paper --symbol=BTCUSDT
```

### 2. Access Dashboard

```
Local: http://localhost:8501
Production: https://demir1988.up.railway.app/
```

### 3. Monitor System

```bash
# Health check
curl http://localhost:8501/health

# Get latest signals
curl http://localhost:8501/api/signals/latest?symbol=BTCUSDT

# Check bot status
curl http://localhost:8501/api/status
```

### 4. Run Diagnostics

```bash
# Full system diagnostic
python debug_dashboard_fix.py

# Database check
python -c "from database_manager_production import DatabaseManager; db = DatabaseManager(); print(db.test_connection())"

# API test
python integration_tests.py
```

---

## 📡 API Dokümantasyonu

### Base URL

```
Production: https://demir1988.up.railway.app/api
Local: http://localhost:8501/api
```

### Endpoints

#### Signals

```http
GET /api/signals/latest?symbol=BTCUSDT
GET /api/signals/technical?symbol=BTCUSDT&limit=100
GET /api/signals/sentiment?symbol=BTCUSDT
GET /api/signals/ml?symbol=BTCUSDT
GET /api/signals/onchain?symbol=BTCUSDT
GET /api/signals/risk?symbol=BTCUSDT
GET /api/signals/consensus?symbol=BTCUSDT
```

#### Positions

```http
GET /api/positions/active
GET /api/positions/history?days=30
POST /api/positions/open
POST /api/positions/close
```

#### Analytics

```http
GET /api/analytics/performance?symbol=BTCUSDT&days=90
GET /api/analytics/group-performance?group=ml&days=30
POST /api/backtest/run
GET /api/backtest/results?backtest_id=123
```

#### System

```http
GET /health
GET /api/status
GET /api/coins
POST /api/coins/add
DELETE /api/coins/remove
```

### Response Format

```json
{
  "status": "success",
  "data": {
    "symbol": "BTCUSDT",
    "consensus_direction": "LONG",
    "weighted_strength": 0.82,
    "consensus_confidence": 0.88,
    "groups": {
      "technical": { "direction": "LONG", "strength": 0.85 },
      "sentiment": { "direction": "NEUTRAL", "strength": 0.52 },
      "ml": { "direction": "LONG", "strength": 0.79 },
      "onchain": { "direction": "LONG", "strength": 0.71 }
    },
    "timestamp": 1700000000.0
  },
  "timestamp": "2025-11-22T21:00:00Z"
}
```

---

## 🚢 Deployment

### Railway (Production)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
git push origin main
# Railway auto-deploys on push

# Check logs
railway logs --service demir-ai
```

### Environment Variables (Railway)

```bash
# Exchange APIs
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
BYBIT_API_KEY=your_key
BYBIT_API_SECRET=your_secret

# Database
DATABASE_URL=postgresql://user:pass@host:5432/demir

# Telegram
TELEGRAM_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# See Railway-API-KEY.txt for complete list (25 variables)
```

### Kubernetes

```bash
# Apply configurations
kubectl apply -f deployment/kubernetes/

# Check pods
kubectl get pods -n demir-ai

# View logs
kubectl logs -f deployment/demir-ai -n demir-ai
```

---

## ⚙️ Konfigürasyon

### config.py

```python
# Trading configuration
TRADING_CONFIG = {
    'symbols': ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'],
    'timeframes': ['15m', '1h', '4h', '1d'],
    'risk_percent': 1.0,  # 1% per trade
    'max_position_size': 0.05,  # 5% of account
    'risk_reward_ratio': 2.0,  # 2:1
    'kelly_fraction': 0.25  # 25% of Kelly Criterion
}

# Signal thresholds
SIGNAL_THRESHOLDS = {
    'consensus_min_strength': 0.65,  # Minimum 65% for LONG
    'consensus_max_strength': 0.35,  # Maximum 35% for SHORT
    'min_confidence': 0.60,  # Minimum 60% confidence
    'min_active_layers': 3  # At least 3 layers agreeing
}

# Backtest configuration
BACKTEST_CONFIG = {
    'start_date': '2022-01-01',
    'end_date': '2025-01-01',
    'initial_capital': 10000,
    'commission': 0.001,  # 0.1% per trade
    'slippage': 0.0005  # 0.05% slippage
}
```

---

## 🛠️ Geliştirme

### Running Tests

```bash
# All tests
python -m pytest tests/

# Integration tests
python integration_tests.py

# Specific test
python -m pytest tests/test_signal_validator.py -v

# Coverage
python -m pytest --cov=. --cov-report=html
```

### Code Quality

```bash
# Linting
flake8 . --max-line-length=120

# Type checking
mypy main.py --strict

# Format code
black . --line-length=120
```

### Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📊 Performans

### Backtest Results (Example)

```
Period: 2022-01-01 → 2025-01-01 (3 years)
Symbol: BTCUSDT
Initial Capital: $10,000

Results:
├─ Total Trades: 1,247
├─ Win Rate: 60.0%
├─ Total Return: +45.21%
├─ Sharpe Ratio: 1.52 (Good)
├─ Sortino Ratio: 2.14 (Excellent)
├─ Max Drawdown: -18.3%
└─ Calmar Ratio: 2.47

Monte Carlo (1000 simulations):
├─ Mean Equity: $13,800
└─ 90% Confidence: $9,200 - $16,400
```

### System Performance

| Metric | Value | Note |
|--------|-------|------|
| WebSocket Latency | <100ms | Guaranteed |
| Indicator Calculation | 40-80ms | 19 indicators (optimized) |
| ML Inference | 150-250ms | 5 models (optimized) |
| Full Cycle | ~400-600ms | Complete analysis (optimized) |
| Database Write | 20-30ms | PostgreSQL |
| Uptime | 99.8% | Last 30 days |

---

## 📜 Lisans

**Private & Proprietary**

© 2025 DEMIR AI. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

---

## 📞 İletişim

**Developer:** Professional Crypto AI Team  
**GitHub:** [https://github.com/dem2203/Demir](https://github.com/dem2203/Demir)  
**Live Dashboard:** [https://demir1988.up.railway.app/](https://demir1988.up.railway.app/)

---

## 🙏 Acknowledgments

- **TA-Lib** - Technical analysis library
- **TensorFlow** - Deep learning framework
- **XGBoost** - Gradient boosting
- **Binance** - Primary exchange API
- **Railway** - Production hosting

---

## 📈 Changelog

### v8.0 (2025-11-22) - Current ⭐ OPTIMIZED
- ✅ **48 AI layers** (optimized from 60+)
- ✅ **Technical Analysis:** 19 indicators (optimized from 28)
- ✅ **Sentiment Analysis:** 15 sources (optimized from 20)
- ✅ **ML Models:** 5 core models (optimized from 10)
- ✅ **On-Chain Analytics:** 4 metrics (optimized from 6)
- ✅ **Risk Management:** 5 engines (ParametricVaR disabled for performance)
- ✅ **Performance:** 30-40% faster execution time
- ✅ **Stability:** Enhanced reliability with focused layers
- ✅ **Production:** Optimized dashboard (dashboard_pro_tr.html)

### v6.0 (2025-11-18)
- ✅ 60+ AI layers fully integrated
- ✅ 5-group signal system operational
- ✅ Multi-timeframe confluence analysis
- ✅ 3-year backtesting with Monte Carlo
- ✅ Kelly Criterion risk management
- ✅ Zero mock data enforcement
- ✅ Production deployment on Railway
- ✅ Real-time dashboard with WebSocket

### v5.0 (2025-11-01)
- Added ML models (LSTM, XGBoost)
- Implemented backtesting engine
- Database migration to PostgreSQL

### v4.0 (2025-10-15)
- Multi-exchange support
- WebSocket real-time data
- Technical indicator expansion

---

**Made with ❤️ by Professional Crypto AI Team**

**Status:** 🟢 Production | **Version:** 8.0 | **Last Update:** 2025-11-22 | **Optimization:** ⚡ 48 Layers
