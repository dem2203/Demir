# analytics/advisor_opportunity_service.py

import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime
import time

from database_manager_production import DatabaseManager

logger = logging.getLogger(__name__)


@dataclass
class AdvisorOpportunity:
    """
    Tek bir AI trade fırsatını temsil eder.
    Bot hiçbir zaman bu trade'i açmaz, sadece sana öneri sunar.
    """
    symbol: str
    direction: str           # LONG / SHORT / NEUTRAL
    entry_price: float
    tp1: float
    tp2: float
    sl: float

    confidence: float        # 0-1 arası
    ensemble_score: float    # 0-1 arası (overall strength)

    risk_score: float        # 0-1 arası (varsa, yoksa 0.5)
    risk_level: str          # LOW / MEDIUM / HIGH

    rr_ratio_tp1: float      # Risk:Reward (TP1)
    rr_ratio_tp2: float      # Risk:Reward (TP2)

    created_at: float        # Unix timestamp

    def to_dict(self) -> Dict:
        """Frontend + API için dict formatı"""
        d = asdict(self)
        # Datetime olarak da dönmek istersen:
        d["created_at_iso"] = datetime.utcfromtimestamp(self.created_at).isoformat() + "Z"
        return d


class AdvisorOpportunityService:
    """
    AI Advisor Servisi
    - Veritabanındaki son sinyallerden "trade fırsatları" üretir
    - Hiçbir yerde order açmaz, sadece analiz & öneri verir
    """

    def __init__(self, db: DatabaseManager):
        self.db = db
        if not self.db:
            logger.error("❌ AdvisorOpportunityService: DatabaseManager is None!")
        else:
            logger.info("✅ AdvisorOpportunityService initialized")

    @staticmethod
    def _calc_risk_level(risk_score: float, confidence: float) -> str:
        """
        Basit risk seviyesi:
        - confidence yüksek ama risk_score yüksek → HIGH
        - orta seviye → MEDIUM
        - düşük risk + makul güven → LOW
        """
        # Korunaklı, biraz konservatif mantık
        if risk_score >= 0.7 or confidence < 0.6:
            return "HIGH"
        if risk_score <= 0.4 and confidence >= 0.7:
            return "LOW"
        return "MEDIUM"

    @staticmethod
    def _calc_rr(entry: float, tp: float, sl: float, direction: str) -> float:
        """
        Risk:Reward oranını hesapla.
        LONG:
            risk = entry - sl
            reward = tp - entry
        SHORT:
            risk = sl - entry
            reward = entry - tp
        """
        try:
            if entry <= 0 or sl <= 0 or tp <= 0:
                return 0.0

            if direction.upper() == "LONG":
                risk = max(entry - sl, 0.0000001)
                reward = max(tp - entry, 0.0)
            elif direction.upper() == "SHORT":
                risk = max(sl - entry, 0.0000001)
                reward = max(entry - tp, 0.0)
            else:
                return 0.0

            if risk <= 0:
                return 0.0

            return round(reward / risk, 2)
        except Exception as e:
            logger.error(f"RR calculation error: {e}")
            return 0.0

    def _row_to_opportunity(self, row: Dict) -> Optional[AdvisorOpportunity]:
        """
        DatabaseManager.get_recent_signals() satırını AdvisorOpportunity'ye çevirir.
        """
        try:
            symbol = row.get("symbol")
            direction = row.get("direction", "NEUTRAL").upper()

            entry = float(row.get("entry_price", 0.0) or 0.0)
            tp1 = float(row.get("tp1", 0.0) or 0.0)
            tp2 = float(row.get("tp2", 0.0) or 0.0)
            sl = float(row.get("sl", 0.0) or 0.0)

            if entry <= 0 or sl <= 0 or tp1 <= 0:
                # Eksik seviye varsa trade fırsatı üretmeyelim
                logger.debug(f"Skipping {symbol}: invalid levels (entry/sl/tp1 missing)")
                return None

            confidence = float(row.get("confidence", 0.0) or 0.0)
            ensemble = float(row.get("ensemble_score", 0.0) or 0.0)

            # Risk skoru yoksa orta risk kabul et
            risk_score = float(row.get("macro_risk_group_score", 0.5) or 0.5)

            created_raw = row.get("timestamp", time.time())
            if hasattr(created_raw, "timestamp"):
                created_ts = float(created_raw.timestamp())
            else:
                created_ts = float(created_raw)

            rr1 = self._calc_rr(entry, tp1, sl, direction)
            rr2 = self._calc_rr(entry, tp2 if tp2 > 0 else tp1, sl, direction)
            risk_level = self._calc_risk_level(risk_score, confidence)

            return AdvisorOpportunity(
                symbol=symbol,
                direction=direction,
                entry_price=entry,
                tp1=tp1,
                tp2=tp2 if tp2 > 0 else tp1,
                sl=sl,
                confidence=confidence,
                ensemble_score=ensemble,
                risk_score=risk_score,
                risk_level=risk_level,
                rr_ratio_tp1=rr1,
                rr_ratio_tp2=rr2,
                created_at=created_ts
            )
        except Exception as e:
            logger.error(f"Error converting row to opportunity: {e}")
            return None

    def get_top_opportunities(
        self,
        limit: int = 20,
        min_confidence: float = 0.65,
        min_ensemble: float = 0.60
    ) -> List[AdvisorOpportunity]:
        """
        En iyi trade fırsatlarını döndürür:
        - Her symbol için en güncel sinyal
        - Confidence + ensemble filtresi
        """

        if not self.db:
            logger.error("AdvisorOpportunityService called without DB")
            return []

        try:
            # Daha geniş bir liste çek (limit * 5)
            rows = self.db.get_recent_signals(limit=limit * 5)
        except Exception as e:
            logger.error(f"Error fetching signals from DB: {e}")
            return []

        opportunities: List[AdvisorOpportunity] = []
        seen_symbols = set()

        for row in rows:
            symbol = row.get("symbol")
            if not symbol or symbol in seen_symbols:
                continue

            confidence = float(row.get("confidence", 0.0) or 0.0)
            ensemble = float(row.get("ensemble_score", 0.0) or 0.0)

            if confidence < min_confidence or ensemble < min_ensemble:
                # Zayıf sinyal → trade planı üretme
                continue

            opp = self._row_to_opportunity(row)
            if opp is None:
                continue

            opportunities.append(opp)
            seen_symbols.add(symbol)

        # Skor: ensemble * confidence * (1 + rr_tp1/3) gibi bir ağırlıkla sıralayalım
        def score(o: AdvisorOpportunity) -> float:
            return (o.ensemble_score * o.confidence * (1.0 + o.rr_ratio_tp1 / 3.0))

        opportunities.sort(key=score, reverse=True)

        # İlk N tanesini döndür
        return opportunities[:limit]
