"""
=================================================================
FILE 2: telegram_message_templates.py
Location: root/telegram_message_templates.py
PHASE 1.2 - MESSAGE TEMPLATES
=================================================================
Reusable message templates for all alerts
"""

from typing import Dict, Any
from datetime import datetime


class TelegramMessageTemplates:
    """Message Templates - Production Ready"""
    
    @staticmethod
    def hourly_report_template(prices: Dict, signals: Dict, support_resistance: Dict) -> str:
        """Hourly report message template"""
        return f"""
📊 <b>SAATLIK MARKET RAPORU</b> 📊
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

<b>💰 FIYATLAR (REAL-TIME):</b>
├─ BTC: ${prices.get('BTC', 'N/A'):,.0f}
├─ ETH: ${prices.get('ETH', 'N/A'):,.0f}
└─ LTC: ${prices.get('LTC', 'N/A'):,.0f}

<b>🟢 AI SİNYALLERİ (Son 1 Saat):</b>
├─ LONG: {signals.get('long_signals', 0)} 🟢
├─ SHORT: {signals.get('short_signals', 0)} 🔴
└─ Toplam Güven: {signals.get('avg_confidence', 0):.1f}%

<b>🔮 15-30 DK TAHMİNLER:</b>
├─ Yön: {signals.get('direction', 'NEUTRAL')}
├─ Güven: {signals.get('confidence', 0):.1f}%
└─ Target: ${signals.get('target', 'N/A'):,.0f}

<b>📌 BTC DESTEĞİ/DİRENCİ:</b>
├─ Direnç: ${support_resistance.get('resistance', 'N/A'):,.0f}
├─ Pivot: ${support_resistance.get('pivot', 'N/A'):,.0f}
└─ Destek: ${support_resistance.get('support', 'N/A'):,.0f}
        """
    
    @staticmethod
    def opportunity_alert_template(symbol: str, direction: str, confidence: float, current_price: float) -> str:
        """Opportunity alert template"""
        emoji = "🟢" if direction == "LONG" else "🔴"
        return f"""
{emoji} <b>⚡ ACIL FIRSAT ALERT ⚡</b> {emoji}

🪙 <b>Pair:</b> {symbol}
📈 <b>Yön:</b> {direction}
📊 <b>Güven:</b> {confidence:.1f}%
💰 <b>Mevcut Fiyat:</b> ${current_price:,.2f}

⏰ <b>Zaman:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
    
    @staticmethod
    def whale_alert_template(symbol: str, whale_type: str, size: float, value_usd: float) -> str:
        """Whale alert template"""
        emoji = "🟢🐋" if whale_type == "BUY" else "🔴🐋"
        return f"""
{emoji} <b>WHALE ACTIVITY DETECTED!</b> {emoji}

🐳 <b>İşlem:</b> {whale_type}
💰 <b>Size:</b> {size:,.0f} {symbol.replace('USDT', '')}
💵 <b>Değer:</b> ${value_usd:,.0f}

⏰ <b>Zaman:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
    
    @staticmethod
    def trade_opened_template(
        trade_id: str,
        symbol: str,
        direction: str,
        entry: float,
        tp1: float,
        tp2: float,
        sl: float,
        position_size: float,
        risk_reward: float
    ) -> str:
        """Trade opened template"""
        emoji = "🟢" if direction == "LONG" else "🔴"
        return f"""
{emoji} <b>TRADE AÇILDI ✅</b> {emoji}

Trade ID: <code>{trade_id}</code>
🪙 <b>Pair:</b> {symbol}
📈 <b>Yön:</b> {direction}
💰 <b>Entry:</b> ${entry:,.2f}

<b>HEDEFLER:</b>
├─ TP1: ${tp1:,.2f} (+{((tp1/entry - 1) * 100):.2f}%)
├─ TP2: ${tp2:,.2f} (+{((tp2/entry - 1) * 100):.2f}%)
└─ SL: ${sl:,.2f} ({((sl/entry - 1) * 100):.2f}%)

<b>POZİSYON:</b>
├─ Size: {position_size:.4f}
└─ Risk/Reward: {risk_reward:.2f}:1

⏰ <b>Zaman:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
    
    @staticmethod
    def trade_tp_hit_template(
        trade_id: str,
        symbol: str,
        tp_level: int,
        exit_price: float,
        pnl: float,
        pnl_percent: float
    ) -> str:
        """TP hit template"""
        return f"""
🎯 <b>TP HEDEFE ULAŞTI! 🎯</b>

Trade ID: <code>{trade_id}</code>
🪙 <b>Pair:</b> {symbol}
🎯 <b>TP Level:</b> {tp_level}
📈 <b>Exit Fiyatı:</b> ${exit_price:,.2f}

💰 <b>P&L: ${pnl:+,.2f} ({pnl_percent:+.2f}%)</b>

⏰ <b>Zaman:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ Kâr alındı!
        """
    
    @staticmethod
    def trade_sl_hit_template(
        trade_id: str,
        symbol: str,
        exit_price: float,
        pnl: float,
        pnl_percent: float
    ) -> str:
        """SL hit template"""
        return f"""
❌ <b>STOP LOSS TRIGGERED ❌</b>

Trade ID: <code>{trade_id}</code>
🪙 <b>Pair:</b> {symbol}
📉 <b>Exit Fiyatı:</b> ${exit_price:,.2f}

💰 <b>P&L: ${pnl:+,.2f} ({pnl_percent:+.2f}%)</b>

⏰ <b>Zaman:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🛡️ Riski kontrol ettik, bir dahaki fırsata hazır!
        """
    
    @staticmethod
    def daily_performance_template(
        trades_today: int,
        wins: int,
        losses: int,
        total_pnl: float,
        best_trade: Dict,
        worst_trade: Dict,
        accuracy: float
    ) -> str:
        """Daily performance template"""
        win_rate = (wins / trades_today * 100) if trades_today > 0 else 0
        return f"""
📊 <b>GÜNLÜK PERFORMANCE RAPORU</b> 📊

📈 <b>İSTATİSTİKLER:</b>
├─ Toplam Trades: {trades_today}
├─ Kazanan: {wins} ✅
├─ Kaybeden: {losses} ❌
├─ Win Rate: {win_rate:.1f}%
└─ Toplam P&L: ${total_pnl:+,.2f}

🏆 <b>EN İYİ TRADE:</b>
├─ Pair: {best_trade.get('symbol', 'N/A')}
├─ Kâr: ${best_trade.get('pnl', 0):+,.2f}
└─ Type: {best_trade.get('signal_type', 'N/A')}

📉 <b>EN KÖTÜ TRADE:</b>
├─ Pair: {worst_trade.get('symbol', 'N/A')}
├─ Zarar: ${worst_trade.get('pnl', 0):+,.2f}
└─ Type: {worst_trade.get('signal_type', 'N/A')}

🎯 <b>AI ACCURACY: {accuracy:.1f}%</b>

⏰ <b>Rapor Zamanı:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
    
    @staticmethod
    def approval_request_template(
        signal_id: str,
        symbol: str,
        direction: str,
        confidence: float,
        entry: float,
        tp1: float,
        tp2: float,
        sl: float
    ) -> str:
        """Manual approval request template"""
        emoji = "🟢" if direction == "LONG" else "🔴"
        return f"""
{emoji} <b>MANUEL ONAY GEREKLİ</b> {emoji}

Signal ID: <code>{signal_id}</code>
🪙 <b>Pair:</b> {symbol}
📈 <b>Yön:</b> {direction}
📊 <b>Güven:</b> {confidence:.1f}%

<b>SEVİYELER:</b>
├─ Entry: ${entry:,.2f}
├─ TP1: ${tp1:,.2f}
├─ TP2: ${tp2:,.2f}
└─ SL: ${sl:,.2f}

⏰ <b>Onay için 5 dakikanız var!</b>

<i>Aşağıdaki butonları kullanarak karar ver</i>
        """


if __name__ == "__main__":
    templates = TelegramMessageTemplates()
    print("✅ TelegramMessageTemplates initialized")
