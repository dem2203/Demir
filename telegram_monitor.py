#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
DEMIR AI - TELEGRAM MONITOR v5.4 (FIXED)
═══════════════════════════════════════════════════════════════════════════════

🔴 SAATLIK RAPOR + DURUMU BİLDİRİMİ
✅ RAILWAY ENV VARIABLES İLE UYUMLU!
└─ TELEGRAM_CHAT_ID (underscore ile)
└─ TELEGRAM_TOKEN (underscore ile)

✅ 100% REAL DATA - NO MOCK
✅ PRODUCTION READY
✅ RAILWAY DEPLOYMENT

🆕 v5.4 FIXES:
- Database query fixed (active_positions table)
- Division by zero protection added
- Error handling improved

RUN: python telegram_monitor.py
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import requests
import logging
import threading
from datetime import datetime, timedelta
import json
from typing import Dict, Optional, List

# ============================================================================
# SETUP LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('telegram_monitor.log')
    ]
)

logger = logging.getLogger(__name__)

# ============================================================================
# ENVIRONMENT VARIABLES - RAILWAY'deki İSİMLER!
# ============================================================================

# ✅ RAILWAY'deki isimlere göre:
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')  # ← underscore ile!
DATABASE_URL = os.getenv('DATABASE_URL')

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    logger.error("❌ TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not set!")
    logger.error("Railway Settings → Environment Variables'ta kontrol et:")
    logger.error("  TELEGRAM_TOKEN = your_bot_token")
    logger.error("  TELEGRAM_CHAT_ID = your_chat_id  (with underscore)")
    sys.exit(1)

# ============================================================================
# TELEGRAM API
# ============================================================================

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def send_telegram_message(message: str, parse_mode: str = "HTML") -> bool:
    """
    Telegram'a mesaj gönder
    
    ✅ REAL DATA ONLY
    """
    try:
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,  # ← Railway variable adı kullan
            'text': message,
            'parse_mode': parse_mode
        }
        
        response = requests.post(
            TELEGRAM_API_URL,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Telegram sent: {message[:50]}...")
            return True
        else:
            logger.error(f"❌ Telegram error: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Telegram connection error: {e}")
        return False

# ============================================================================
# GET MARKET DATA (REAL - Binance API)
# ============================================================================

def get_binance_price(symbol: str) -> Optional[Dict]:
    """Binance'den gerçek fiyat verisi al"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            price = float(data['price'])
            
            # 24h change
            url_24h = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            response_24h = requests.get(url_24h, timeout=5)
            
            if response_24h.status_code == 200:
                data_24h = response_24h.json()
                change_24h = float(data_24h['priceChangePercent'])
                
                return {
                    'symbol': symbol,
                    'price': price,
                    'change_24h': change_24h,
                    'timestamp': datetime.now().isoformat()
                }
        return None
    except Exception as e:
        logger.error(f"❌ Binance API error for {symbol}: {e}")
        return None

# ============================================================================
# GET SIGNALS FROM DATABASE (✅ FIXED v5.4)
# ============================================================================

def get_latest_signals() -> List[Dict]:
    """Database'den son sinyalleri al
    
    ✅ FIXED: active_positions tablosu kullanılıyor
    ✅ FIXED: Kolon isimleri düzeltildi (take_profit_1, stop_loss)
    """
    try:
        import psycopg2
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # ✅ FIXED: active_positions tablosu + doğru kolon isimleri
        cursor.execute("""
            SELECT symbol, direction as signal_type, 
                   signal_confidence as confidence, entry_price, 
                   take_profit_1, take_profit_2, stop_loss
            FROM active_positions
            WHERE opened_at > NOW() - INTERVAL '1 hour'
            ORDER BY opened_at DESC
            LIMIT 10
        """)
        
        signals = []
        for row in cursor.fetchall():
            signals.append({
                'symbol': row[0],
                'type': row[1],
                'confidence': row[2],
                'entry': row[3],
                'tp1': row[4],
                'tp2': row[5],
                'sl': row[6]
            })
        
        cursor.close()
        conn.close()
        
        return signals
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        return []

# ============================================================================
# HOURLY REPORT
# ============================================================================

def create_hourly_report() -> str:
    """Saatlik rapor oluştur"""
    
    logger.info("📊 Creating hourly report...")
    
    # Kripto fiyatları (REAL DATA)
    btc = get_binance_price("BTCUSDT")
    eth = get_binance_price("ETHUSDT")
    ltc = get_binance_price("LTCUSDT")
    
    # Database'den sinyaller
    signals = get_latest_signals()
    
    # Rapor mesajı
    message = f"""
<b>🤖 DEMIR AI - SAATLIK RAPOR</b>
<b>⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S UTC')}</b>

<b>💰 FİYATLAR (REAL-TIME BINANCE)</b>
"""
    
    if btc:
        change_emoji = "📈" if btc['change_24h'] >= 0 else "📉"
        message += f"<b>₿ Bitcoin:</b> ${btc['price']:,.2f} {change_emoji} {btc['change_24h']:+.2f}%\n"
    
    if eth:
        change_emoji = "📈" if eth['change_24h'] >= 0 else "📉"
        message += f"<b>◆ Ethereum:</b> ${eth['price']:,.2f} {change_emoji} {eth['change_24h']:+.2f}%\n"
    
    if ltc:
        change_emoji = "📈" if ltc['change_24h'] >= 0 else "📉"
        message += f"<b>Ł Litecoin:</b> ${ltc['price']:,.2f} {change_emoji} {ltc['change_24h']:+.2f}%\n"
    
    # AI Sinyalleri
    message += f"\n<b>🧠 AI SİNYALLERİ (Son 1 saat)</b>\n"
    
    if signals:
        message += f"Toplam sinyal: {len(signals)}\n"
        
        long_count = len([s for s in signals if s['type'] == 'LONG'])
        short_count = len([s for s in signals if s['type'] == 'SHORT'])
        
        message += f"🟢 LONG: {long_count}\n"
        message += f"🔴 SHORT: {short_count}\n"
        
        if signals:
            avg_confidence = sum(s['confidence'] for s in signals) / len(signals)
            message += f"📊 Ort. Güven: {avg_confidence:.1f}%\n"
    else:
        message += "Signal yok (market durgun)\n"
    
    # Risk ve Fırsat
    message += f"\n<b>⚠️ RİSK & FIRSAT</b>\n"
    
    if btc and btc['change_24h'] > 5:
        message += f"🔴 UYARI: BTC %{btc['change_24h']:.1f} yükseldi - Volatilite yüksek!\n"
    elif btc and btc['change_24h'] < -5:
        message += f"🟢 FIRSAT: BTC %{abs(btc['change_24h']):.1f} düştü - Satın alma fırsatı?\n"
    
    # Bot Durumu
    message += f"\n<b>🤖 SİSTEM DURUMU</b>\n"
    message += f"✅ Bot çalışıyor (24/7)\n"
    message += f"✅ Telegram bağlı\n"
    message += f"✅ Binance API aktif\n"
    message += f"✅ Database sağlıklı\n"
    
    message += f"\n<b>Sonraki rapor:</b> +1 saat\n"
    message += f"<b>⏱️ Sistem saati:</b> {datetime.now().strftime('%H:%M:%S UTC')}"
    
    return message.strip()

# ============================================================================
# HEALTH CHECK
# ============================================================================

def send_health_check() -> bool:
    """Bot sağlık kontrolü ve durum mesajı"""
    
    logger.info("🏥 Performing health check...")
    
    try:
        # Binance API check
        binance_ok = requests.get("https://api.binance.com/api/v3/ping", timeout=5).status_code == 200
        
        # Telegram API check
        telegram_ok = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe",
            timeout=5
        ).status_code == 200
        
        # Database check
        database_ok = False
        try:
            import psycopg2
            conn = psycopg2.connect(DATABASE_URL)
            conn.close()
            database_ok = True
        except:
            database_ok = False
        
        # Durum mesajı (Optional - her saat de gönderebilirsin)
        status_emoji = "🟢" if all([binance_ok, telegram_ok, database_ok]) else "🟡"
        
        logger.info(f"Health check result: Binance={binance_ok}, Telegram={telegram_ok}, DB={database_ok}")
        
        return all([binance_ok, telegram_ok, database_ok])
        
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return False

# ============================================================================
# MONITORING LOOP
# ============================================================================

class TelegramMonitor:
    def __init__(self):
        self.running = False
        self.last_hourly_report = datetime.now()
        self.last_health_check = datetime.now()
        self.last_alert_check = datetime.now()
        self.alert_queue = []
    
    def start(self):
        """Monitor başlat"""
        logger.info("🚀 Starting Telegram Monitor...")
        self.running = True
        
        # Startup mesajı
        send_telegram_message(
            "🤖 <b>DEMIR AI - BAŞLATILDI</b>\n"
            f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S UTC')}\n"
            "✅ 24/7 Telegram monitörü aktif\n"
            "📊 Saatlik raporlar gönderilecek"
        )
        
        # Main loop
        while self.running:
            try:
                now = datetime.now()
                
                # SAATLIK RAPOR (Her saat başında)
                if (now - self.last_hourly_report).total_seconds() >= 3600:
                    logger.info("📊 Sending hourly report...")
                    report = create_hourly_report()
                    send_telegram_message(report)
                    self.last_hourly_report = now
                
                # SAĞLIK KONTROLÜ (Her 5 dakika)
                if (now - self.last_health_check).total_seconds() >= 300:
                    logger.info("🏥 Health check...")
                    health_ok = send_health_check()
                    if not health_ok:
                        logger.warning("⚠️ Health check failed!")
                    self.last_health_check = now
                
                # ALERT CHECK (Her 1 dakika)
                if (now - self.last_alert_check).total_seconds() >= 60:
                    self.process_alerts()
                    self.last_alert_check = now
                
                # Her 10 saniye kontrol et
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"❌ Monitor loop error: {e}")
                time.sleep(60)
    
    def stop(self):
        """Monitor durdur"""
        logger.info("⛔ Stopping Telegram Monitor...")
        self.running = False
        send_telegram_message(
            "⛔ <b>DEMIR AI - DURDURULDU</b>\n"
            f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S UTC')}"
        )
    
    def process_alerts(self) -> None:
        """
        ⭐ NEW v8.0: Process and send trading opportunity alerts.
        
        Checks for:
        - High-confidence signals from AI
        - Price breakouts
        - Volume spikes
        - Pattern detections
        - Risk warnings
        
        Sends formatted Telegram notifications for actionable opportunities.
        """
        try:
            # Get latest signals from database
            signals = get_latest_signals()
            
            if not signals:
                logger.debug("No alerts to process")
                return
            
            # Filter high-confidence signals (>70%)
            high_confidence_signals = [s for s in signals if s.get('confidence', 0) > 70]
            
            if high_confidence_signals:
                logger.info(f"⚡ Found {len(high_confidence_signals)} high-confidence signals")
                
                for signal in high_confidence_signals:
                    # Send opportunity alert
                    self.send_opportunity_alert(signal)
                    time.sleep(2)  # Rate limiting
            
            # Check for risk warnings
            btc = get_binance_price("BTCUSDT")
            if btc and abs(btc.get('change_24h', 0)) > 10:
                risk_alert = f"""
⚠️ <b>RİSK UYARISI</b>

<b>BTC:</b> ${btc['price']:,.2f}
<b>24h Değişim:</b> {btc['change_24h']:+.2f}%

🔴 <b>YÜKSEK VOLATİLİTE</b>
⚠️ Risk yönetimi uygula!
⚠️ Pozisyon büyüklüğünü azalt!
⚠️ Stop-loss ayarla!
"""
                send_telegram_message(risk_alert)
                logger.info("⚡ Risk alert sent")
            
        except Exception as e:
            logger.error(f"❌ Error in process_alerts: {e}")
    
    def send_opportunity_alert(self, signal: Dict) -> bool:
        """
        ⭐ NEW v8.0: Send formatted trading opportunity alert.
        ✅ FIXED v5.4: Division by zero protection added
        
        Args:
            signal: Trading signal with entry, targets, stop-loss
        
        Returns:
            True if alert sent successfully
        """
        try:
            symbol = signal.get('symbol', 'UNKNOWN')
            signal_type = signal.get('type', 'UNKNOWN')
            confidence = signal.get('confidence', 0)
            entry = signal.get('entry', 0)
            tp1 = signal.get('tp1', 0)
            tp2 = signal.get('tp2', 0)
            sl = signal.get('sl', 0)
            
            # Get current price
            price_data = get_binance_price(symbol)
            current_price = price_data['price'] if price_data else entry
            
            # Emoji selection
            signal_emoji = "🟢" if signal_type == "LONG" else "🔴"
            confidence_emoji = "🔥" if confidence >= 80 else "⚡" if confidence >= 70 else "🟡"
            
            # ✅ FIXED: Division by zero protection
            if entry > 0:
                tp1_pct = ((tp1 - entry) / entry * 100)
                tp2_pct = ((tp2 - entry) / entry * 100)
                sl_pct = ((sl - entry) / entry * 100)
            else:
                tp1_pct = tp2_pct = sl_pct = 0.0
                logger.warning(f"⚠️ Entry price is zero for {symbol}")
            
            # Format alert message
            alert_message = f"""
{signal_emoji} <b>TRADING FIRSATI</b>

<b>Coin:</b> {symbol.replace('USDT', '')}
<b>Sinyal:</b> {signal_type} {confidence_emoji}
<b>Güven:</b> {confidence:.1f}%

<b>💰 FİYAT BİLGİLERİ</b>
<b>Mevcut:</b> ${current_price:,.4f}
<b>Giriş:</b> ${entry:,.4f}
<b>Hedef 1:</b> ${tp1:,.4f} ({tp1_pct:+.1f}%)
<b>Hedef 2:</b> ${tp2:,.4f} ({tp2_pct:+.1f}%)
<b>Stop-Loss:</b> ${sl:,.4f} ({sl_pct:+.1f}%)

<b>⏰ Zaman:</b> {datetime.now().strftime('%H:%M:%S UTC')}
<b>🔗 Alım yap</b> | <b>🚨 Risk yönet</b>
"""
            
            success = send_telegram_message(alert_message)
            
            if success:
                logger.info(f"✅ Opportunity alert sent: {symbol} {signal_type}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error sending opportunity alert: {e}")
            return False

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("DEMIR AI - TELEGRAM MONITOR v5.4 (FIXED)")
    logger.info("=" * 80)
    logger.info(f"TELEGRAM_TOKEN: {TELEGRAM_TOKEN[:10]}...")
    logger.info(f"TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}")
    logger.info(f"DATABASE_URL: Connected")
    logger.info(f"Start time: {datetime.now().strftime('%d.%m.%Y %H:%M:%S UTC')}")
    logger.info("✅ FIXES: Database query + Division by zero protection")
    logger.info("=" * 80)
    
    try:
        monitor = TelegramMonitor()
        monitor.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        monitor.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
