# ui/telegram_tradeplan_notifier.py

"""
DEMIR AI - Telegram Trade Plan Notifier

- Sadece TradePlan objelerini gönderir.
- Emir açmaz, sinyal satmaz, sadece bilgilendirme yapar.
- Mesajlar Türkçe, insan gibi ama net ve sade.
"""

import logging
import os
from typing import Optional

import requests

from advanced_ai.opportunity_engine import TradePlan

logger = logging.getLogger(__name__)


class TelegramTradePlanNotifier:
    """TradePlan'leri Telegram'a profesyonel formatta gönderen notifier."""

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
                "⚠️ TelegramTradePlanNotifier: TOKEN veya CHAT_ID bulunamadı, "
                "planlar sadece log'a yazılacak."
            )
        else:
            logger.info(
                "✅ TelegramTradePlanNotifier initialized for chat %s",
                self.chat_id,
            )

    # -------------------- Mesaj formatlama yardımcıları --------------------

    def _format_risk_text(self, risk_level: str) -> str:
        lvl = (risk_level or "").upper()
        if lvl == "LOW":
            return "Düşük risk (daha sakin yapı, yine de stop şart)."
        if lvl == "HIGH":
            return "Yüksek risk (agresif bölge, kaldıraçta ekstra dikkat)."
        return "Orta risk (normal volatilite, risk yönetimi önemli)."

    def _format_confidence_text(self, confidence: float) -> str:
        if confidence >= 0.9:
            return "Yüksek güven (AI katmanlarının büyük kısmı aynı yönde)."
        if confidence >= 0.8:
            return "Güven seviyesi iyi (birçok sinyal aynı yönde)."
        if confidence >= 0.7:
            return "Orta üzeri güven (fırsat olabilir, risk kontrolü önemli)."
        return "Sınırlı güven (daha temkinli yaklaşmakta fayda var)."

    def _format_rr_text(self, rr: float) -> str:
        if rr >= 3.0:
            return f"Oldukça iyi bir Risk/Ödül oranı (~{rr:.2f}R)."
        if rr >= 2.0:
            return f"Sağlam bir Risk/Ödül oranı (~{rr:.2f}R)."
        if rr >= 1.5:
            return f"Ortalama bir Risk/Ödül oranı (~{rr:.2f}R)."
        return f"Risk/Ödül oranı (~{rr:.2f}R) çok cazip değil, dikkat."

    def _build_turkish_comment(self, plan: TradePlan) -> str:
        side_txt = "yukarı yönlü (LONG)" if plan.side == "LONG" else "aşağı yönlü (SHORT)"

        conf_txt = self._format_confidence_text(plan.confidence)
        risk_txt = self._format_risk_text(plan.risk_level)
        rr_txt = self._format_rr_text(plan.rr_ratio)

        tf_txt = ", ".join(plan.timeframes) if plan.timeframes else "Ana zaman dilimi"
        base = (
            f"{plan.symbol} için {side_txt} bir setup oluştu. "
            f"{tf_txt} bazında sinyaller aynı yönde kümelenmiş durumda. "
        )

        reason = plan.reason_summary or ""
        comment = (
            f"{base}\n\n"
            f"• Güven yorumu: {conf_txt}\n"
            f"• Risk yorumu: {risk_txt}\n"
            f"• R/R yorumu: {rr_txt}\n"
        )

        if reason:
            comment += f"\nAI özet notu: {reason}"

        return comment

    def _format_plan_message(self, plan: TradePlan) -> str:
        arrow = "🟢 LONG" if plan.side == "LONG" else "🔴 SHORT"
        rr_txt = f"{plan.rr_ratio:.2f}R"
        conf_pct = f"{plan.confidence * 100:.1f}%"
        tf_txt = ", ".join(plan.timeframes) if plan.timeframes else "N/A"

        comment = self._build_turkish_comment(plan)

        body = f"""
🤖 <b>DEMIR AI TRADE PLAN</b>
━━━━━━━━━━━━━━━━━━
📊 <b>Parite:</b> {plan.symbol}
🎯 <b>Yön:</b> {arrow}
💪 <b>Güven:</b> {conf_pct}
⚖️ <b>Risk Seviyesi:</b> {plan.risk_level}
📐 <b>Confluence:</b> {plan.confluence_score:.2f}
🧠 <b>Zaman Dilimleri:</b> {tf_txt}

💵 <b>Giriş (Entry):</b> {plan.entry:.6f}
🛑 <b>Stop Loss:</b> {plan.stop_loss:.6f}
🎫 <b>TP1:</b> {plan.tp1:.6f}
🎫 <b>TP2:</b> {plan.tp2:.6f if plan.tp2 else '-'}
🎫 <b>TP3:</b> {plan.tp3:.6f if plan.tp3 else '-'}

📈 <b>Risk / Ödül:</b> {rr_txt}

🧾 <b>AI Yorum:</b>
{comment}

━━━━━━━━━━━━━━━━━━
⚠️ Bu bir <b>bilgilendirme ve danışmanlık</b> mesajıdır.
Hiçbir şekilde otomatik emir açılmaz; tüm işlemler manuel ve senin sorumluluğunda.
"""
        return body

    # ------------------------- Public API ----------------------------------

    def send_trade_plan(self, plan: TradePlan) -> bool:
        """TradePlan objesini Telegram'a gönder (veya yoksa log'a dök)."""
        if not self.api_url or not self.chat_id:
            logger.warning(
                "TelegramTradePlanNotifier: Config eksik, plan sadece log'lanıyor: "
                "%s %s", plan.symbol, plan.side
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
                    "❌ Telegram trade plan send failed (%s): %s",
                    resp.status_code,
                    resp.text,
                )
                return False

            logger.info("📨 TradePlan sent to Telegram for %s", plan.symbol)
            return True
        except Exception as e:
            logger.error("❌ TelegramTradePlanNotifier error: %s", e)
            return False
