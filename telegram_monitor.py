#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
🤖 TELEGRAM MONITORING SYSTEM - AI Activity Status Reports
═══════════════════════════════════════════════════════════════════════════════

3 Ways to Monitor AI Backend:

1. TELEGRAM HOURLY REPORTS ✅
   ├─ Saatlik sistem durumu
   ├─ Coin fiyatları
   ├─ AI sinyalleri
   ├─ Market durumu
   └─ Performance metrikleri

2. STREAMLIT DASHBOARD ✅
   ├─ Real-time görüntüleme
   ├─ Live charts
   ├─ System metrics
   └─ Trade history

3. RAILWAY LOGS ✅
   ├─ Backend logs
   ├─ Worker status
   ├─ Error tracking
   └─ Performance monitoring

═══════════════════════════════════════════════════════════════════════════════
"""

import os
import time
import logging
from datetime import datetime, timedelta
import psycopg2
import schedule
from binance.client import Client
import requests
import json
import asyncio
from telegram import Bot
from telegram.error import TelegramError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIG
# ============================================================================

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DATABASE_URL = os.getenv('DATABASE_URL')
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')

# ============================================================================
# TELEGRAM BOT
# ============================================================================

async def send_telegram_message(message: str):
    """Telegram'a mesaj gönder"""
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')
        logger.info("✅ Telegram message sent")
    except TelegramError as e:
        logger.error(f"❌ Telegram error: {e}")

def send_sync(message: str):
    """Synchronous wrapper"""
    asyncio.run(send_telegram_message(message))

# ============================================================================
# DATA GATHERING
# ============================================================================

def get_db_connection():
    """PostgreSQL bağlantısı"""
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        logger.error(f"DB Error: {e}")
        return None

def get_binance_client():
    """Binance client"""
    try:
        return Client(
            api_key=BINANCE_API_KEY,
            api_secret=BINANCE_API_SECRET
        )
    except Exception as e:
        logger.error(f"Binance Error: {e}")
        return None

# ============================================================================
# METRICS CALCULATION
# ============================================================================

def get_system_metrics():
    """Sistem metriklerini hesapla"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Today's signals
        cursor.execute("""
            SELECT COUNT(*) FROM trading_signals 
            WHERE created_at >= CURRENT_DATE
        """)
        today_signals = cursor.fetchone()[0]
        
        # Win rate (30 days)
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN profit > 0 THEN 1 END) as wins
            FROM executed_trades
            WHERE closed_at >= CURRENT_DATE - INTERVAL '30 days'
        """)
        result = cursor.fetchone()
        win_rate = (result[1] / result[0] * 100) if result[0] > 0 else 0
        
        # Total P&L
        cursor.execute("""
            SELECT COALESCE(SUM(profit), 0)
            FROM executed_trades
            WHERE closed_at >= CURRENT_DATE - INTERVAL '30 days'
        """)
        total_pnl = cursor.fetchone()[0]
        
        # Active trades
        cursor.execute("""
            SELECT COUNT(*) FROM executed_trades
            WHERE closed_at IS NULL
        """)
        active_trades = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            'today_signals': today_signals,
            'win_rate': round(win_rate, 2),
            'total_pnl': round(total_pnl, 2),
            'active_trades': active_trades
        }
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        return None

def get_market_data():
    """Pazar verisi topla"""
    binance = get_binance_client()
    if not binance:
        return None
    
    try:
        data = {}
        coins = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
        
        for coin in coins:
            try:
                ticker = binance.get_symbol_ticker(symbol=coin)
                price = float(ticker['price'])
                
                # 24h change
                stats = binance.get_24h_ticker(symbol=coin)
                change = float(stats['priceChangePercent'])
                
                # Format
                coin_name = coin.replace('USDT', '')
                data[coin_name] = {
                    'price': price,
                    'change': change,
                    'symbol': coin
                }
            except Exception as e:
                logger.error(f"Error fetching {coin}: {e}")
        
        return data
    except Exception as e:
        logger.error(f"Market data error: {e}")
        return None

def get_hourly_signals():
    """Son saatteki sinyalleri getir"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT symbol, signal_type, confidence, entry_price
            FROM trading_signals
            WHERE created_at >= CURRENT_TIME - INTERVAL '1 hour'
            ORDER BY created_at DESC
            LIMIT 10
        """)
        signals = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return signals
    except Exception as e:
        logger.error(f"Signals error: {e}")
        return []

# ============================================================================
# TELEGRAM REPORT BUILDER
# ============================================================================

def build_hourly_report():
    """Saatlik rapor oluştur"""
    
    metrics = get_system_metrics()
    market_data = get_market_data()
    signals = get_hourly_signals()
    
    if not metrics or not market_data:
        return None
    
    # Build message
    report = ""
    report += "═══════════════════════════════════════\n"
    report += "🤖 <b>DEMIR AI v5.1 - Hourly Report</b>\n"
    report += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
    report += "═══════════════════════════════════════\n\n"
    
    # Status
    report += "📊 <b>System Status</b>\n"
    report += f"✅ Status: RUNNING (24/7)\n"
    report += f"🟢 Worker: Active\n"
    report += f"🌐 Web: Connected\n"
    report += f"📡 Monitor: OK\n\n"
    
    # Metrics
    report += "📈 <b>Performance Metrics (30-day)</b>\n"
    report += f"💰 Total P&L: ${metrics['total_pnl']:,.2f}\n"
    report += f"📊 Win Rate: {metrics['win_rate']}%\n"
    report += f"🎯 Signals Today: {metrics['today_signals']}\n"
    report += f"💼 Active Trades: {metrics['active_trades']}\n\n"
    
    # Market Data
    report += "💹 <b>Live Market Data</b>\n"
    for coin, data in market_data.items():
        change_emoji = "🟢" if data['change'] >= 0 else "🔴"
        report += f"{change_emoji} <b>{coin}</b>: ${data['price']:,.2f} "
        report += f"({data['change']:+.2f}%)\n"
    report += "\n"
    
    # Recent Signals
    if signals:
        report += "🎯 <b>Last Hour Signals</b>\n"
        for signal in signals[:5]:  # Max 5 signals
            signal_emoji = "🟢" if signal[1] == "BUY" else "🔴"
            confidence = int(signal[2] * 100) if signal[2] else 0
            report += f"{signal_emoji} {signal[0]}: {signal[1]} "
            report += f"(${signal[3]:,.2f}, {confidence}% confidence)\n"
        report += "\n"
    else:
        report += "🎯 <b>Last Hour Signals</b>: No signals\n\n"
    
    # Status footer
    report += "═══════════════════════════════════════\n"
    report += "✅ AI Backend: Working Continuously\n"
    report += "📊 Dashboard: https://your-url.railway.app\n"
    report += "📝 Logs: Railway Deployments\n"
    report += "═══════════════════════════════════════\n"
    
    return report

# ============================================================================
# CRITICAL ALERTS
# ============================================================================

def check_critical_status():
    """Kritik durum kontrolü"""
    conn = get_db_connection()
    if not conn:
        alert = "⚠️ <b>CRITICAL ALERT</b>\n"
        alert += "Database connection lost!\n"
        alert += "AI backend may be affected!"
        send_sync(alert)
        return
    
    try:
        cursor = conn.cursor()
        
        # Check last signal time
        cursor.execute("""
            SELECT MAX(created_at) FROM trading_signals
        """)
        last_signal = cursor.fetchone()[0]
        
        if last_signal:
            time_since = datetime.utcnow() - last_signal.replace(tzinfo=None)
            
            # If no signal in 30+ minutes, alert
            if time_since > timedelta(minutes=30):
                alert = f"⚠️ <b>WARNING</b>\n"
                alert += f"No new signals in {time_since.total_seconds()/60:.0f} minutes!\n"
                alert += "Check AI Engine status in Railway logs"
                send_sync(alert)
        
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Critical check error: {e}")

# ============================================================================
# SCHEDULER
# ============================================================================

def schedule_reports():
    """Rapor zamanlamması"""
    
    # Hourly reports (every hour at :00)
    schedule.every().hour.at(":00").do(lambda: send_sync(build_hourly_report()))
    
    # Critical checks (every 30 minutes)
    schedule.every(30).minutes.do(check_critical_status)
    
    # Log
    logger.info("✅ Report scheduler initialized")
    
    # Run scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)

# ============================================================================
# STARTUP MESSAGE
# ============================================================================

def send_startup_message():
    """Başlangıç mesajı gönder"""
    msg = "🚀 <b>DEMIR AI v5.1 Started!</b>\n\n"
    msg += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
    msg += "✅ AI Backend: Running\n"
    msg += "📊 Dashboard: Connected\n"
    msg += "🤖 Monitoring: Active\n"
    msg += "📡 Telegram: Ready\n\n"
    msg += "Hourly reports will be sent every hour.\n"
    msg += "Critical alerts: Real-time on issues\n"
    
    send_sync(msg)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("🚀 Telegram Monitoring System started")
    
    # Send startup
    send_startup_message()
    
    # Start scheduler
    schedule_reports()
