"""
DEMIR AI - Opportunity Engine
Tamamen gerçek veriye dayalı trade plan üretimi (advisor mode)
"""

import logging
import time
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional, List, Literal

from config import OPPORTUNITY_THRESHOLDS
from utils.signal_processor_advanced import FilteredSignal
from utils.signal_validator_comprehensive import SignalValidator

logger = logging.getLogger(__name__)

Side = Literal["LONG", "SHORT", "NEUTRAL"]


@dataclass
class TradePlan:
    """Son kullanıcıya gidecek tam trade planı."""
    symbol: str
    side: Side
    entry: float
    stop_loss: float
    tp1: float
    tp2: Optional[float]
    tp3: Optional[float]
    rr_ratio: float
    confidence: float
    confluence_score: float
    risk_score: float
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    timeframes: List[str] = field(default_factory=list)
    reason_summary: str = ""
    group_breakdown: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=lambda: time.time())

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["created_at"] = float(self.created_at)
        return d


class OpportunityEngine:
    """
    DEMIR AI Opportunity Engine
    - 5 grup + multi-TF + risk skorlarından final trade plan üretir
    - Sadece gerçek veriye dayalı, validated sinyalleri kabul eder
    """

    def __init__(self):
        self.validator = SignalValidator()
        self.cfg = OPPORTUNITY_THRESHOLDS
        logger.info("✅ OpportunityEngine initialized")

    # ----------------- Yardımcı fonksiyonlar -----------------

    def _map_risk_level(self, risk_score: float) -> str:
        if risk_score <= 0.35:
            return "LOW"
        if risk_score <= 0.65:
            return "MEDIUM"
        return "HIGH"

    def _calculate_rr(self, side: Side, entry: float, sl: float, tp: float) -> float:
        """Risk:Reward oranı hesapla."""
        try:
            if entry <= 0 or sl <= 0 or tp <= 0:
                return 0.0

            if side == "LONG":
                risk = max(entry - sl, 1e-8)
                reward = max(tp - entry, 0.0)
            elif side == "SHORT":
                risk = max(sl - entry, 1e-8)
                reward = max(entry - tp, 0.0)
            else:
                return 0.0

            rr = max(reward / risk, 0.0)
            return float(rr)
        except Exception as e:
            logger.error(f"[RR CALC] error: {e}")
            return 0.0

    # ----------------- Ana API -----------------

    def build_from_group_result(
        self,
        symbol: str,
        latest_price: float,
        group_result: Dict[str, Any],
        filtered_signal: Optional[FilteredSignal] = None,
        multi_tf_info: Optional[Dict[str, Any]] = None,
    ) -> Optional[TradePlan]:
        """
        group_result: SignalGroupOrchestrator.orchestrate_group_signals(...) çıktısı
        filtered_signal: utils.signal_processor_advanced.FilteredSignal
        multi_tf_info: multi_timeframe_confluence çıktısı (opsiyonel)
        """
        try:
            consensus = group_result.get("consensus")
            risk = group_result.get("risk", {})
            groups = group_result.get("groups", {})

            if not consensus:
                logger.debug(f"[{symbol}] no consensus, skipping")
                return None

            direction = str(consensus.get("direction", "NEUTRAL")).upper()
            side: Side = (
                "LONG" if direction == "LONG"
                else "SHORT" if direction == "SHORT"
                else "NEUTRAL"
            )

            strength = float(consensus.get("strength", 0.5))
            confidence = float(consensus.get("confidence", abs(strength - 0.5) * 2))

            if side == "NEUTRAL":
                logger.debug(f"[{symbol}] consensus NEUTRAL, no plan")
                return None

            if confidence < self.cfg["min_confidence"]:
                logger.debug(
                    f"[{symbol}] confidence {confidence:.2f} < min_confidence "
                    f"{self.cfg['min_confidence']:.2f}"
                )
                return None

            # Risk score (0-1)
            risk_score = float(risk.get("risk_score", 0.5))
            if risk_score > self.cfg["max_risk_score"]:
                logger.info(
                    f"[{symbol}] high risk score {risk_score:.2f} > "
                    f"max_risk_score {self.cfg['max_risk_score']:.2f}, skipping"
                )
                return None

            # Entry / SL / TP'ler
            if filtered_signal:
                entry = float(filtered_signal.entry_price)
                sl = float(filtered_signal.stop_loss)
                tp1 = float(filtered_signal.tp1)
                tp2 = float(filtered_signal.tp2) if filtered_signal.tp2 else None
                tp3 = float(filtered_signal.tp3) if filtered_signal.tp3 else None
            else:
                # Fallback: ATR vs yoksa kaba bant – minimum ama gerçekçi
                entry = float(latest_price)
                if side == "LONG":
                    sl = entry * 0.985
                    tp1 = entry * 1.015
                else:
                    sl = entry * 1.015
                    tp1 = entry * 0.985
                tp2 = None
                tp3 = None

            rr = self._calculate_rr(side, entry, sl, tp1)
            if rr < self.cfg["min_rr"]:
                logger.info(
                    f"[{symbol}] RR {rr:.2f} < min_rr {self.cfg['min_rr']:.2f}, skipping"
                )
                return None

            # Multi-TF alignment & confluence
            tf_alignment: List[str] = []
            confluence_score = 0.5
            if multi_tf_info:
                tf_alignment = [
                    tf for tf, info in multi_tf_info.items()
                    if isinstance(info, dict)
                    and str(info.get("direction", "")).upper() == direction
                ]
                confluence_score = float(multi_tf_info.get("confluence", 0.5))

            risk_level = self._map_risk_level(risk_score)

            # Reason summary
            reasons: List[str] = []
            group_breakdown: Dict[str, Any] = {}
            for g_name, g_sig in groups.items():
                if not g_sig:
                    continue
                try:
                    g_dir = getattr(g_sig.direction, "value", None) if hasattr(g_sig, "direction") else g_sig.get("direction")
                    g_strength = getattr(g_sig, "strength", None) if hasattr(g_sig, "strength") else g_sig.get("strength")
                    g_conf = getattr(g_sig, "confidence", None) if hasattr(g_sig, "confidence") else g_sig.get("confidence")
                    reasons.append(f"{g_name.upper()}={g_dir} ({g_strength:.2f})")

                    group_breakdown[g_name] = {
                        "direction": g_dir,
                        "strength": g_strength,
                        "confidence": g_conf,
                    }
                except Exception:
                    continue

            reason_summary = (
                f"{symbol} {side} | "
                + ", ".join(reasons)
                + f" | RR≈{rr:.2f}, risk={risk_level}, conf={confidence:.2f}"
            )

            plan = TradePlan(
                symbol=symbol,
                side=side,
                entry=entry,
                stop_loss=sl,
                tp1=tp1,
                tp2=tp2,
                tp3=tp3,
                rr_ratio=rr,
                confidence=confidence,
                confluence_score=confluence_score,
                risk_score=risk_score,
                risk_level=risk_level,
                timeframes=tf_alignment,
                reason_summary=reason_summary,
                group_breakdown=group_breakdown,
            )

            # Son güvenlik: kapsamlı signal validator
            signal_for_validation = {
                "symbol": plan.symbol,
                "direction": plan.side,
                "entry_price": plan.entry,
                "tp1": plan.tp1,
                "tp2": plan.tp2 or plan.tp1,
                "sl": plan.stop_loss,
                "confidence": plan.confidence,
                "timestamp": plan.created_at,
                "strength": strength,
                "layer_scores": {},  # İstersek doldururuz
            }

            valid, errors = self.validator.validate_all(signal_for_validation)
            if not valid:
                logger.warning(
                    f"[{symbol}] TradePlan rejected by validator: {errors}"
                )
                return None

            logger.info(
                f"🎯 TradePlan created: {symbol} {side} | "
                f"RR={rr:.2f}, conf={confidence:.2f}, risk={risk_level}"
            )
            return plan

        except Exception as e:
            logger.error(f"[{symbol}] OpportunityEngine error: {e}")
            return None
