"""
DEMIR AI - Telegram Trade Plan Notifier
Sadece TradePlan objelerini gönderen, advisor-mode odaklı bildirim sistemi
"""

import logging
import os
from typing import Optional

import requests

from advanced_ai.opportunity_engine import TradePlan

logger = logging.getLogger(__name__)


class TelegramTradePlanNotifier:
    """TradePlan'leri Telegram'a şık formatta gönderen notifier."""

    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        self.token = token or os.getenv("TELEGRAM_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.api_url = (
            f"https://api.telegram.org/bot{self.token}"
            if self.token
            else None
        )

        if not self.api_url or not self.chat_id:
            logger.warning(
                "⚠️ TelegramTradePlanNotifier: TOKEN veya CHAT_ID yok, "
                "mesaj gönderilmeyecek."
            )
        else:
            logger.info(f"✅ TelegramTradePlanNotifier initialized for chat {self.chat_id}")

    def _format_plan_message(self, plan: TradePlan) -> str:
        arrow = "🟢 LONG" if plan.side == "LONG" else "🔴 SHORT"
        rr_txt = f"{plan.rr_ratio:.2f}R"
        conf_pct = f"{plan.confidence * 100:.1f}%"
        tf_txt = ", ".join(plan.timeframes) if plan.timeframes else "N/A"

        body = f"""
🤖 <b>DEMIR AI TRADE PLAN</b>
━━━━━━━━━━━━━━━━━━
📊 <b>Symbol:</b> {plan.symbol}
🎯 <b>Direction:</b> {arrow}
💪 <b>Confidence:</b> {conf_pct}
⚖️ <b>Risk Level:</b> {plan.risk_level}
📐 <b>Confluence:</b> {plan.confluence_score:.2f}
🧠 <b>Timeframes:</b> {tf_txt}

💵 <b>Entry:</b> {plan.entry:.6f}
🛑 <b>Stop Loss:</b> {plan.stop_loss:.6f}
🎫 <b>TP1:</b> {plan.tp1:.6f}
🎫 <b>TP2:</b> {plan.tp2:.6f if plan.tp2 else '-'}
🎫 <b>TP3:</b> {plan.tp3:.6f if plan.tp3 else '-'}

📈 <b>Risk / Reward:</b> {rr_txt}

🧾 <b>Reason:</b> {plan.reason_summary}
━━━━━━━━━━━━━━━━━━
⚠️ Bu bir <b>DANIŞMANLIK</b> sinyalidir, otomatik emir YOK.
"""
        return body

    def send_trade_plan(self, plan: TradePlan) -> bool:
        """TradePlan objesini Telegram'a gönder."""
        if not self.api_url or not self.chat_id:
            logger.warning(
                f"TelegramTradePlanNotifier: Config eksik, plan sadece log'landı: "
                f"{plan.symbol} {plan.side}"
            )
            logger.info(self._format_plan_message(plan))
            return False

        try:
            text = self._format_plan_message(plan)
            params = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            }
            resp = requests.post(
                f"{self.api_url}/sendMessage",
                data=params,
                timeout=5,
            )
            if resp.status_code != 200:
                logger.error(
                    f"❌ Telegram trade plan send failed ({resp.status_code}): "
                    f"{resp.text}"
                )
                return False

            logger.info(f"📨 TradePlan sent to Telegram for {plan.symbol}")
            return True
        except Exception as e:
            logger.error(f"❌ TelegramTradePlanNotifier error: {e}")
            return False
