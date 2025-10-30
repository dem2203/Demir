# config.py
#! v63.0: LTCUSDT varsayılan listeye eklendi.
# v48.0: v58.0 Trailing Stop-Loss ayarları eklendi.
# v47.0: Tüm yapılandırma ayarları, sabitler ve API anahtarları

import os
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

# ----------------------------
# ⚙️ API Anahtarları ve Ortam Değişkenleri
# ----------------------------
API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

COINGLASS_API_KEY = os.getenv("COINGLASS_API_KEY", "")
CRYPTOPANIC_KEY = os.getenv("CRYPTOPANIC_KEY", "")

WHALE_ADDRESS = os.getenv("WHALE_ADDRESS", "0xc2a30212a8DdAc9e123944d6e29FADdCe994E5f2") # Varsayılan balina adresi
HYPERLIQUID_API_URL = "https://api.hyperliquid.xyz/info"

# ----------------------------
# ⚙️ Strateji Sabitleri
# ----------------------------
TF_ENTRY = "15m"
#! v63.0: Kullanıcı isteği üzerine LTCUSDT eklendi.
TRADE_SYMBOLS_DEFAULT = ["BTC/USDT", "ETH/USDT", "LTCUSDT"] 
EMA_FAST = 12
EMA_SLOW = 26
EMA_MED = 50
EMA_LONG = 200
INITIAL_CAPITAL_DEFAULT = 10000.0
RISK_PER_TRADE_PERCENT = 0.01 # Her işlemde sermayenin %1'i risk edilir
MAX_HOLD_BARS = 5

# ----------------------------
# ⚙️ v58.0: Trailing Stop-Loss Ayarları (A.docx'ten)
# ----------------------------
TRAILING_SL_ENABLED = True # Takip eden stop-loss'u etkinleştirir
TRAILING_SL_ACTIVATION_R = 1.0 # TSL'nin 1R kâra ulaşıldığında devreye girmesini sağlar
TRAILING_SL_ATR_MULTIPLIER = 2.0 # Fiyatı kaç ATR geriden takip edeceği

# ----------------------------
# ⚙️ Diğer Sabitler
# ----------------------------
BINANCE_FEE_RATE = 0.0004
DB_NAME = "demir_memory.db"

# ----------------------------
# ⚙️ Global Cache'ler
# ----------------------------
model_cache = {}
scaler_cache = {}

print("✅ config.py v63.0 (LTCUSDT Eklendi) yüklendi.") # Yükleme onayı
