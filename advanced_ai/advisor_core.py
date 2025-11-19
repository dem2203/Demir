# advanced_ai/advisor_core.py

"""
DEMIR AI - Advisor Core
Tamamen gerçek veriye dayalı, emir açmayan, profesyonel trade danışmanı.

Bu çekirdek:
- Multi-exchange gerçek veriyi (RealtimeDataFetcher) kullanır
- SignalGroupOrchestrator + AdvancedSignalProcessor + OpportunityEngine ile
  her sembol için TradePlan üretir
- Anti-spam + değişim algılama ile sadece “anlamlı değişiklik” olduğunda
  Telegram’a trade plan yollar
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, List

from config import (
    ADVISORY_MODE,
    DEFAULT_TRACKED_SYMBOLS,
    OPPORTUNITY_THRESHOLDS,
)

from advanced_ai.signal_engine_integration import SignalGroupOrchestrator
from advanced_ai.opportunity_engine import OpportunityEngine, TradePlan
from utils.signal_processor_advanced import AdvancedSignalProcessor
from ui.data_fetcher_realtime import RealtimeDataFetcher
from ui.telegram_tradeplan_notifier import TelegramTradePlanNotifier
from analytics.advisor_opportunity_service import AdvisorOpportunityService
from database_manager_production import DatabaseManager

logger = logging.getLogger(__name__)


# ============================== Dataclass'lar ===============================

@dataclass
class AdvisorConfig:
    """
    Advisor davranışını kontrol eden ayarlar.
    İstersen bunları Config / env üzerinden de override edebilirsin.
    """
    symbols: List[str] = field(default_factory=lambda: list(DEFAULT_TRACKED_SYMBOLS))
    scan_interval_seconds: int = 300   # Her iterasyon arası bekleme (5 dk)
    min_conf_for_scan: float = OPPORTUNITY_THRESHOLDS["min_confidence"]
    min_conf_for_telegram: float = OPPORTUNITY_THRESHOLDS["min_telegram_confidence"]
    min_rr_for_alert: float = OPPORTUNITY_THRESHOLDS["min_rr"]

    # Anti-spam / değişim algılama
    min_notify_interval_seconds: int = 600  # Aynı sembol için min 10 dk
    min_level_change_pct: float = 0.002     # Entry/SL/TP'lerde min %0.2 değişim
    min_conf_delta: float = 0.05            # Güvende min +0.05 artış


@dataclass
class LastPlanInfo:
    """
    Bir sembol için en son üretilen ve opsiyonel olarak Telegram'a gönderilen plan.
    """
    plan: TradePlan
    sent_to_telegram: bool
    last_sent_at: float


# ============================== Advisor Core ================================

class DemirAIAdvisor:
    """
    DEMIR AI - Advisor Core

    - Emir atmaz, simülasyon yapmaz.
    - Sadece:
        * TradePlan üretir (OpportunityEngine)
        * Uygun gördüklerini Telegram'a bildirir (TelegramTradePlanNotifier)
        * İleride UI / dashboard için AdvisorOpportunityService ile DB tabanlı fırsat listesi sağlar.
    """

    def __init__(
        self,
        db: Optional[DatabaseManager],
        orchestrator: SignalGroupOrchestrator,
        opportunity_engine: OpportunityEngine,
        advanced_processor: AdvancedSignalProcessor,
        realtime_fetcher: RealtimeDataFetcher,
        telegram_notifier: TelegramTradePlanNotifier,
        advisor_service: Optional[AdvisorOpportunityService] = None,
        config: Optional[AdvisorConfig] = None,
    ) -> None:
        self.db = db
        self.orchestrator = orchestrator
        self.opportunity_engine = opportunity_engine
        self.advanced_processor = advanced_processor
        self.realtime_fetcher = realtime_fetcher
        self.telegram = telegram_notifier
        self.advisor_service = advisor_service

        self.config = config or AdvisorConfig()
        self._last_plans: Dict[str, LastPlanInfo] = {}

        if not ADVISORY_MODE:
            logger.warning("⚠️ DemirAIAdvisor created but ADVISORY_MODE=False")

        logger.info("✅ DemirAIAdvisor initialized with symbols: %s", self.config.symbols)

    # ----------------------------- Yardımcılar ------------------------------

    @staticmethod
    def _pct_change(a: float, b: float) -> float:
        """a -> b değişim oranını (mutlak) döndürür. a veya b <=0 ise 1.0 kabul eder."""
        try:
            if a <= 0 or b <= 0:
                return 1.0
            return abs(b - a) / a
        except Exception:
            return 1.0

    def _has_material_change(self, old: TradePlan, new: TradePlan) -> bool:
        """
        Yeni plan eskiye göre anlamlı şekilde farklı mı?
        - Yön değiştiyse → EVET
        - Entry/SL/TP1'de % min_level_change_pct'den fazla değişim → EVET
        - Confidence min_conf_delta'dan fazla arttıysa → EVET
        Aksi halde → HAYIR (tekrar spam yapma)
        """

        if old.side != new.side:
            return True

        level_thresh = self.config.min_level_change_pct
        if self._pct_change(old.entry, new.entry) >= level_thresh:
            return True
        if self._pct_change(old.stop_loss, new.stop_loss) >= level_thresh:
            return True
        if self._pct_change(old.tp1, new.tp1) >= level_thresh:
            return True

        if (new.confidence - old.confidence) >= self.config.min_conf_delta:
            return True

        # RR çok iyileşmişse de dikkate al
        if (new.rr_ratio - old.rr_ratio) >= 0.5:
            return True

        return False

    def _should_notify(self, symbol: str, plan: TradePlan, now_ts: float) -> bool:
        """
        Bu sembol için yeni planı Telegram'a göndermeli miyiz?
        - Confidence / RR threshold'ları sağlıyor mu?
        - Son gönderiden bu yana min_notify_interval_seconds geçti mi?
        - Eski plana göre anlamlı bir değişim var mı?
        """

        if plan.confidence < self.config.min_conf_for_telegram:
            logger.debug(
                "[ADVISOR] %s conf %.2f < min_conf_for_telegram %.2f",
                symbol, plan.confidence, self.config.min_conf_for_telegram
            )
            return False

        if plan.rr_ratio < self.config.min_rr_for_alert:
            logger.debug(
                "[ADVISOR] %s RR %.2f < min_rr_for_alert %.2f",
                symbol, plan.rr_ratio, self.config.min_rr_for_alert
            )
            return False

        last_info = self._last_plans.get(symbol)
        if not last_info:
            # Hiç plan yoksa ilkini gönderebiliriz
            return True

        # Zaman kontrolü
        elapsed = now_ts - last_info.last_sent_at
        if elapsed < self.config.min_notify_interval_seconds:
            # Çok sık uyarma; sadece çok radikal değişim varsa izin ver
            if not self._has_material_change(last_info.plan, plan):
                logger.debug(
                    "[ADVISOR] %s: only %ds since last alert, and no material change",
                    symbol, int(elapsed)
                )
                return False

        # Seviyelerde anlamlı değişim var mı?
        if not self._has_material_change(last_info.plan, plan):
            logger.debug(
                "[ADVISOR] %s: new plan ≈ old plan, no material change", symbol
            )
            return False

        return True

    def _remember_plan(self, symbol: str, plan: TradePlan, sent: bool, ts: float) -> None:
        """Yeni planı hafızaya al."""
        self._last_plans[symbol] = LastPlanInfo(
            plan=plan,
            sent_to_telegram=sent,
            last_sent_at=ts,
        )

    # ------------------------- Realtime tarama logic ------------------------

    def scan_symbol_realtime(self, symbol: str) -> Optional[TradePlan]:
        """
        Tek bir sembol için:
        - Gerçek OHLCV verisini çeker (şu an 15m ağırlıklı)
        - 5 grup sinyali üretir (SignalGroupOrchestrator)
        - AdvancedSignalProcessor ile entry/SL/TP setini çıkarır
        - OpportunityEngine ile son TradePlan'ı üretir
        """

        logger.info("[ADVISOR] 🔍 Scanning %s for realtime opportunity", symbol)

        # 1) Gerçek OHLCV verisi
        ohlcv_15m = self.realtime_fetcher.get_ohlcv(
            symbol=symbol,
            interval="15m",
            limit=200,
        )
        if not ohlcv_15m:
            logger.warning("[ADVISOR] No OHLCV(15m) data for %s", symbol)
            return None

        try:
            latest_price = float(ohlcv_15m[-1]["close"])
        except Exception:
            latest_price = float(ohlcv_15m[-1][4])  # [open, high, low, close, ...] formatı
        # 2) Grup sinyallerini üret
        group_result = self.orchestrator.orchestrate_group_signals(
            symbol=symbol,
            market_data={"15m": ohlcv_15m},
        )
        if not group_result:
            logger.warning("[ADVISOR] No group_result for %s", symbol)
            return None

        # 3) İleri sinyal işleme -> entry/SL/TP çıkar
        filtered_signal = self.advanced_processor.process_single_symbol(
            symbol=symbol,
            ohlcv_data=ohlcv_15m,
            group_result=group_result,
        )

        # 4) (Opsiyonel) Multi-timeframe confluence entegrasyonu için
        multi_tf_info = None  # İleride 1h/4h confluence eklemek istersen burayı genişletebiliriz

        # 5) TradePlan üret
        plan = self.opportunity_engine.build_from_group_result(
            symbol=symbol,
            latest_price=latest_price,
            group_result=group_result,
            filtered_signal=filtered_signal,
            multi_tf_info=multi_tf_info,
        )
        return plan

    # ------------------------- Public çalışma method'ları -------------------

    def run_single_iteration(self, iteration: int) -> None:
        """
        Tek bir advisor iterasyonu:
        - Her sembol için scan_symbol_realtime çalıştır
        - Uygun planları Telegram'a bildir
        - Planları hafızaya al
        """

        if not ADVISORY_MODE:
            logger.info("[ADVISOR] ADVISORY_MODE=False, iteration skipped")
            return

        logger.info(
            "\n[ADVISOR] 🔄 Iteration #%d for %d symbols",
            iteration,
            len(self.config.symbols),
        )

        now_ts = time.time()

        for symbol in self.config.symbols:
            try:
                plan = self.scan_symbol_realtime(symbol)
                if not plan:
                    continue

                # AdvisorOpportunityService'le UI/DB tarafına da entegre etmek istersen,
                # burada DB kayıtlarını da zenginleştirebilirsin.

                should_send = self._should_notify(symbol, plan, now_ts)
                if should_send:
                    logger.info(
                        "[ADVISOR] ✅ Sending plan for %s | side=%s RR=%.2f conf=%.2f",
                        symbol, plan.side, plan.rr_ratio, plan.confidence
                    )
                    self.telegram.send_trade_plan(plan)
                    self._remember_plan(symbol, plan, sent=True, ts=now_ts)
                else:
                    logger.info(
                        "[ADVISOR] ℹ️ Plan generated but not sent (filters) for %s",
                        symbol
                    )
                    self._remember_plan(symbol, plan, sent=False, ts=now_ts)

            except Exception as e:
                logger.error("[ADVISOR] Error while processing %s: %s", symbol, e)

    def run_forever(self) -> None:
        """
        Sonsuz döngü:
        - Her scan_interval_seconds'te bir run_single_iteration çalıştırır.
        - Arkaplanda thread olarak main.py içinden çağrılacak.
        """

        if not ADVISORY_MODE:
            logger.info("DemirAIAdvisor.run_forever aborted: ADVISORY_MODE=False")
            return

        logger.info("\n" + "=" * 80)
        logger.info("🧠 DEMIR AI Advisor - REALTIME SCANNER STARTED (NO AUTO TRADING)")
        logger.info("=" * 80 + "\n")

        iteration = 0
        while True:
            iteration += 1
            try:
                self.run_single_iteration(iteration)
            except Exception as e:
                logger.error("Fatal error in DemirAIAdvisor iteration #%d: %s", iteration, e)
            time.sleep(self.config.scan_interval_seconds)

       # ------------------------- DB tabanlı fırsatlar ------------------------

    def get_db_opportunities_for_api(self, limit: int = 20) -> List[Dict]:
        """
        API / dashboard için,
        AdvisorOpportunityService'i kullanarak DB'den en iyi fırsatları döndürür.
        """
        if not self.advisor_service:
            logger.warning("AdvisorOpportunityService not set in DemirAIAdvisor")
            return []
        
        opps = self.advisor_service.get_top_opportunities(limit=limit)
        return [o.to_dict() for o in opps]

# ============================================================================
# BACKWARD COMPATIBILITY ALIAS
# ============================================================================

# main.py'de "from advanced_ai.advisor_core import AdvisorCore" kullanıldığı için
AdvisorCore = DemirAIAdvisor

__all__ = ['DemirAIAdvisor', 'AdvisorCore', 'AdvisorConfig', 'LastPlanInfo']
