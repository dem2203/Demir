"""
=================================================================
FILE 1: telegram_alerts_advanced.py
Location: root/telegram_alerts_advanced.py
PHASE 1.1 - TELEGRAM ADVANCED ALERTS
=================================================================
Saatlik raporlar, strong signal alerts, whale activity, trade notifications
%100 REAL DATA - NO MOCK DATA
"""

import os
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class TelegramAlertsAdvanced:
    """Advanced Telegram Alert System - Production Ready"""
    
    def __init__(self):
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = int(os.getenv("TELEGRAM_CHAT_ID"))
        self.binance_key = os.getenv("BINANCE_API_KEY")
        self.coinglass_key = os.getenv("COINGLASS_API_KEY")
        
        if not all([self.token, self.chat_id]):
            raise ValueError("Missing TELEGRAM credentials")
        
        self.bot = Bot(token=self.token)
    
    # ========== SAATLIK RAPORLAR ==========
    
    async def send_hourly_report(self, signal_data: Dict) -> bool:
        """
        Saatlik raporlar:
        • BTC, ETH, LTC fiyatları (real-time Binance)
        • AI sinyalleri (LONG/SHORT count)
        • 15-30 dk tahminler
        • Destek/Direnç seviyeleri
        """
        try:
            # REAL prices from Binance
            prices = await self._fetch_real_binance_prices()
            
            # Get support/resistance
            support_resistance = await self._calculate_support_resistance()
            
            message = f"""
📊 <b>SAATLIK MARKET RAPORU</b> 📊
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

<b>💰 FIYATLAR (REAL-TIME):</b>
├─ BTC: ${prices.get('BTC', 'N/A'):,.0f}
├─ ETH: ${prices.get('ETH', 'N/A'):,.0f}
└─ LTC: ${prices.get('LTC', 'N/A'):,.0f}

<b>🟢 AI SİNYALLERİ (Son 1 Saat):</b>
├─ LONG: {signal_data.get('long_signals', 0)} 🟢
├─ SHORT: {signal_data.get('short_signals', 0)} 🔴
└─ Toplam Güven: {signal_data.get('avg_confidence', 0):.1f}%

<b>🔮 15-30 DK TAHMİNLER:</b>
├─ Yön: {signal_data.get('direction', 'NEUTRAL')}
├─ Güven: {signal_data.get('confidence', 0):.1f}%
└─ Target: ${signal_data.get('target', 'N/A'):,.0f}

<b>📌 BTC DESTEĞİ/DİRENCİ:</b>
├─ Direnç: ${support_resistance.get('resistance', 'N/A'):,.0f}
├─ Pivot: ${support_resistance.get('pivot', 'N/A'):,.0f}
└─ Destek: ${support_resistance.get('support', 'N/A'):,.0f}
            """
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info("✅ Hourly report sent")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending hourly report: {e}")
            return False
    
    # ========== ACIL FIRSAT ALERTS ==========
    
    async def send_urgent_opportunity_alert(
        self,
        symbol: str,
        direction: str,
        confidence: float
    ) -> bool:
        """
        Acil fırsat alerts:
        • %3+ fiyat hareketi
        • Güçlü SHORT sinyali (>80%)
        • Güçlü LONG sinyali (>80%)
        """
        try:
            if confidence < 80:
                return False
            
            emoji = "🟢" if direction == "LONG" else "🔴"
            current_price = await self._get_current_price(symbol)
            
            message = f"""
{emoji} <b>⚡ ACIL FIRSAT ALERT ⚡</b> {emoji}

🪙 <b>Pair:</b> {symbol}
📈 <b>Yön:</b> {direction}
📊 <b>Güven:</b> {confidence:.1f}%
💰 <b>Mevcut Fiyat:</b> ${current_price:,.2f}

⏰ <b>Zaman:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            keyboard = [
                [InlineKeyboardButton("✅ Trade Aç", callback_data=f"trade_{symbol}_{direction}")],
                [InlineKeyboardButton("📊 Detaylar", callback_data=f"details_{symbol}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            
            logger.info(f"✅ Opportunity alert: {symbol} {direction}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
    
    # ========== WHALE ACTIVITY ==========
    
    async def send_whale_alert(
        self,
        symbol: str,
        whale_type: str,
        size: float,
        value_usd: float
    ) -> bool:
        """Whale activity alerts"""
        try:
            emoji = "🟢🐋" if whale_type == "BUY" else "🔴🐋"
            
            message = f"""
{emoji} <b>WHALE ACTIVITY DETECTED!</b> {emoji}

🐳 <b>İşlem:</b> {whale_type}
💰 <b>Size:</b> {size:,.0f} {symbol.replace('USDT', '')}
💵 <b>Değer:</b> ${value_usd:,.0f}

⏰ <b>Zaman:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info(f"✅ Whale alert: {symbol} {whale_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
    
    # ========== TRADE NOTIFICATIONS ==========
    
    async def notify_trade_opened(
        self,
        trade_id: str,
        symbol: str,
        direction: str,
        entry: float,
        tp1: float,
        tp2: float,
        sl: float
    ) -> bool:
        """Trade eklendi bildirimi"""
        try:
            emoji = "🟢" if direction == "LONG" else "🔴"
            
            message = f"""
{emoji} <b>TRADE AÇILDI ✅</b> {emoji}

Trade ID: <code>{trade_id}</code>
🪙 <b>Pair:</b> {symbol}
📈 <b>Yön:</b> {direction}
💰 <b>Entry:</b> ${entry:,.2f}

<b>HEDEFLER:</b>
├─ TP1: ${tp1:,.2f}
├─ TP2: ${tp2:,.2f}
└─ SL: ${sl:,.2f}

⏰ <b>Zaman:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
    
    async def notify_trade_tp_hit(
        self,
        trade_id: str,
        symbol: str,
        tp_level: int,
        exit_price: float,
        pnl: float,
        pnl_percent: float
    ) -> bool:
        """TP hedefe ulaştı"""
        try:
            message = f"""
🎯 <b>TP HEDEFE ULAŞTI! 🎯</b>

Trade ID: <code>{trade_id}</code>
🪙 <b>Pair:</b> {symbol}
🎯 <b>TP Level:</b> {tp_level}
📈 <b>Exit:</b> ${exit_price:,.2f}

💰 <b>P&L: ${pnl:+,.2f} ({pnl_percent:+.2f}%)</b>

⏰ <b>Zaman:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
    
    async def notify_trade_sl_hit(
        self,
        trade_id: str,
        symbol: str,
        exit_price: float,
        pnl: float,
        pnl_percent: float
    ) -> bool:
        """SL triggered"""
        try:
            message = f"""
❌ <b>STOP LOSS TRIGGERED ❌</b>

Trade ID: <code>{trade_id}</code>
🪙 <b>Pair:</b> {symbol}
📉 <b>Exit:</b> ${exit_price:,.2f}

💰 <b>P&L: ${pnl:+,.2f} ({pnl_percent:+.2f}%)</b>

⏰ <b>Zaman:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
    
    # ========== HELPER METHODS ==========
    
    async def _fetch_real_binance_prices(self) -> Dict[str, float]:
        """Fetch REAL prices - NO MOCK DATA"""
        try:
            prices = {}
            for symbol in ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']:
                url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            data = await response.json()
                            clean = symbol.replace('USDT', '')
                            prices[clean] = float(data['price'])
            return prices
        except Exception as e:
            logger.error(f"Error: {e}")
            return {}
    
    async def _get_current_price(self, symbol: str) -> float:
        """Get current price"""
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data['price'])
            return None
        except Exception as e:
            logger.error(f"Error: {e}")
            return None
    
    async def _calculate_support_resistance(self) -> Dict:
        """Calculate S/R from real data"""
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {"symbol": "BTCUSDT", "interval": "1h", "limit": 100}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        highs = [float(c[2]) for c in data]
                        lows = [float(c[3]) for c in data]
                        closes = [float(c[4]) for c in data]
                        
                        high = max(highs)
                        low = min(lows)
                        close = closes[-1]
                        
                        pivot = (high + low + close) / 3
                        resistance = (2 * pivot) - low
                        support = (2 * pivot) - high
                        
                        return {
                            'resistance': resistance,
                            'pivot': pivot,
                            'support': support
                        }
        except Exception as e:
            logger.error(f"Error: {e}")
            return {}


if __name__ == "__main__":
    alerts = TelegramAlertsAdvanced()
    print("✅ TelegramAlertsAdvanced initialized")
