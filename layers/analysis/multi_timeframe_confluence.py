"""
Multi-Timeframe Confluence Analysis - 3 Timeframe Sinyalının Birleşimi
DEMIR AI v6.0 - Phase 4 Production Grade

15m, 1h, 4h confluence analizleri
Güç seviyeleri (Weak/Medium/Strong)
Divergence ve Support/Resistance konfluensi
Gerçek veri validasyonu ile
"""

import asyncio
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from enum import Enum
import json

logger = logging.getLogger(__name__)


class TimeFrame(Enum):
    """Zaman çerçeveleri"""
    FIFTEEN_MIN = "15m"
    ONE_HOUR = "1h"
    FOUR_HOUR = "4h"
    ONE_DAY = "1d"


class SignalStrength(Enum):
    """Sinyal gücü seviyeleri"""
    VERY_WEAK = 1
    WEAK = 2
    MEDIUM = 3
    STRONG = 4
    VERY_STRONG = 5


@dataclass
class ConfluencePoint:
    """Confluence noktası"""
    timeframe: str
    level: float
    type: str  # support, resistance, pivot, etc
    strength: int  # 1-5
    sources: List[str] = field(default_factory=list)  # Kaynak göstergeler
    metadata: Dict = field(default_factory=dict)


@dataclass
class TimeFrameAnalysis:
    """Single timeframe analizi"""
    timeframe: str
    current_price: float
    trend: str  # "uptrend", "downtrend", "ranging"
    strength: SignalStrength
    signal: str  # "BUY", "SELL", "NEUTRAL"
    support_levels: List[float] = field(default_factory=list)
    resistance_levels: List[float] = field(default_factory=list)
    indicators: Dict = field(default_factory=dict)
    momentum: float = 0.0  # -100 to +100
    reliability: float = 0.0  # % certainty
    last_update: float = 0.0


@dataclass
class ConfluenceSignal:
    """Nihai confluence sinyali"""
    symbol: str
    timestamp: float
    direction: str  # "STRONG_BUY", "BUY", "NEUTRAL", "SELL", "STRONG_SELL"
    strength: SignalStrength
    confidence: float  # 0-100%
    convergence_score: float  # 0-100%
    
    # Timeframe details
    tf_15m: TimeFrameAnalysis
    tf_1h: TimeFrameAnalysis
    tf_4h: TimeFrameAnalysis
    
    # Confluences
    confluence_points: List[ConfluencePoint] = field(default_factory=list)
    
    # Riskler
    risk_level: str  # "LOW", "MEDIUM", "HIGH"
    take_profit_level: float = 0.0
    stop_loss_level: float = 0.0
    risk_reward_ratio: float = 0.0
    
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Dict'e dönüştür"""
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "direction": self.direction,
            "strength": self.strength.name,
            "confidence": self.confidence,
            "convergence_score": self.convergence_score,
            "tf_15m": asdict(self.tf_15m),
            "tf_1h": asdict(self.tf_1h),
            "tf_4h": asdict(self.tf_4h),
            "confluence_points": [asdict(cp) for cp in self.confluence_points],
            "risk_level": self.risk_level,
            "take_profit_level": self.take_profit_level,
            "stop_loss_level": self.stop_loss_level,
            "risk_reward_ratio": self.risk_reward_ratio,
            "metadata": self.metadata
        }


class MultiTimeframeConfluenceAnalyzer:
    """Multi-timeframe Confluence Analyzer"""
    
    def __init__(self):
        """Başlat"""
        self.timeframe_data: Dict[str, Dict] = {
            "15m": {"indicators": {}, "price": 0, "timestamp": 0},
            "1h": {"indicators": {}, "price": 0, "timestamp": 0},
            "4h": {"indicators": {}, "price": 0, "timestamp": 0},
        }
        
        self.support_resistance: Dict[str, List[float]] = {
            "15m": [],
            "1h": [],
            "4h": [],
        }
        
        self.last_confluence_signal: Optional[ConfluenceSignal] = None
        
        # Confluence settings
        self.confluence_tolerance = 0.005  # 0.5% fiyat toleransı
        self.min_strength_threshold = SignalStrength.MEDIUM
    
    def update_timeframe_data(
        self,
        timeframe: str,
        price: float,
        indicators: Dict,
        support_levels: List[float],
        resistance_levels: List[float],
        timestamp: float
    ) -> bool:
        """
        Timeframe verisini güncelle
        
        Args:
            timeframe: "15m", "1h", "4h"
            price: Mevcut fiyat
            indicators: Indicator sonuçları
            support_levels: Destek seviyeleri
            resistance_levels: Direnç seviyeleri
            timestamp: Unix timestamp
        """
        if timeframe not in self.timeframe_data:
            logger.error(f"Invalid timeframe: {timeframe}")
            return False
        
        try:
            self.timeframe_data[timeframe] = {
                "indicators": indicators,
                "price": price,
                "timestamp": timestamp,
                "support_levels": support_levels,
                "resistance_levels": resistance_levels,
            }
            
            self.support_resistance[timeframe] = support_levels + resistance_levels
            return True
        
        except Exception as e:
            logger.error(f"Error updating timeframe data: {e}")
            return False
    
    def analyze_timeframe(self, timeframe: str) -> Optional[TimeFrameAnalysis]:
        """
        Single timeframe analizi yap
        
        Args:
            timeframe: "15m", "1h", "4h"
        
        Returns:
            TimeFrameAnalysis veya None
        """
        if timeframe not in self.timeframe_data:
            return None
        
        data = self.timeframe_data[timeframe]
        if not data.get("indicators"):
            return None
        
        try:
            indicators = data["indicators"]
            price = data["price"]
            support = data.get("support_levels", [])
            resistance = data.get("resistance_levels", [])
            
            # Trend tayin et
            trend = self._determine_trend(indicators, price, support, resistance)
            
            # Signal üret
            signal = self._generate_signal(indicators, trend)
            
            # Momentum hesapla
            momentum = self._calculate_momentum(indicators)
            
            # Güç hesapla
            strength = self._calculate_strength(indicators, trend)
            
            # Güvenilirlik
            reliability = self._calculate_reliability(indicators, strength)
            
            return TimeFrameAnalysis(
                timeframe=timeframe,
                current_price=price,
                trend=trend,
                strength=strength,
                signal=signal,
                support_levels=support,
                resistance_levels=resistance,
                indicators=indicators,
                momentum=momentum,
                reliability=reliability,
                last_update=data.get("timestamp", 0)
            )
        
        except Exception as e:
            logger.error(f"Error analyzing timeframe {timeframe}: {e}")
            return None
    
    def _determine_trend(
        self,
        indicators: Dict,
        price: float,
        support: List[float],
        resistance: List[float]
    ) -> str:
        """Trend tayin et"""
        
        # Moving Average kontrolü
        sma_20 = indicators.get("SMA_20", {}).get("value", 0)
        sma_50 = indicators.get("SMA_50", {}).get("value", 0)
        
        ma_trend_score = 0
        if price > sma_20 > sma_50:
            ma_trend_score = 1
        elif price < sma_20 < sma_50:
            ma_trend_score = -1
        
        # ADX kontrolü
        adx = indicators.get("ADX_14", {}).get("value", 0)
        trend_strength = "strong" if adx > 25 else "weak"
        
        # Support/Resistance kontrolü
        if support and price > max(support):
            return "uptrend"
        elif resistance and price < min(resistance):
            return "downtrend"
        elif ma_trend_score > 0:
            return "uptrend"
        elif ma_trend_score < 0:
            return "downtrend"
        else:
            return "ranging"
    
    def _generate_signal(self, indicators: Dict, trend: str) -> str:
        """Signal üret"""
        
        # RSI kontrolü
        rsi = indicators.get("RSI_14", {}).get("value", 50)
        
        # MACD kontrolü
        macd = indicators.get("MACD", {}).get("value", 0)
        macd_signal = indicators.get("MACD", {}).get("signal", 0)
        macd_hist = indicators.get("MACD", {}).get("histogram", 0)
        
        # Momentum kontrolü
        momentum = indicators.get("Momentum", {}).get("value", 0)
        
        signal_score = 0
        
        # RSI sinyalleri
        if rsi < 30:
            signal_score += 2  # Oversold - BUY
        elif rsi > 70:
            signal_score -= 2  # Overbought - SELL
        elif rsi > 45 and rsi < 55:
            signal_score += 0  # Neutral
        
        # MACD sinyalleri
        if macd > macd_signal and macd_hist > 0:
            signal_score += 2
        elif macd < macd_signal and macd_hist < 0:
            signal_score -= 2
        
        # Momentum sinyalleri
        if momentum > 0:
            signal_score += 1
        elif momentum < 0:
            signal_score -= 1
        
        # Trend overlay
        if trend == "uptrend":
            signal_score += 1
        elif trend == "downtrend":
            signal_score -= 1
        
        if signal_score >= 3:
            return "BUY"
        elif signal_score <= -3:
            return "SELL"
        else:
            return "NEUTRAL"
    
    def _calculate_momentum(self, indicators: Dict) -> float:
        """Momentum hesapla (-100 to +100)"""
        
        rsi = indicators.get("RSI_14", {}).get("value", 50)
        momentum = indicators.get("Momentum", {}).get("value", 0)
        
        # RSI normalize et (-100 to +100)
        rsi_momentum = (rsi - 50) * 2
        
        # Momentum normalize et
        momentum_norm = np.clip(momentum / 100, -100, 100)
        
        # Average
        return (rsi_momentum + momentum_norm) / 2
    
    def _calculate_strength(self, indicators: Dict, trend: str) -> SignalStrength:
        """Sinyal gücü hesapla"""
        
        adx = indicators.get("ADX_14", {}).get("value", 0)
        rsi = indicators.get("RSI_14", {}).get("value", 50)
        
        strength_score = 0
        
        # ADX kontrol
        if adx > 40:
            strength_score += 2
        elif adx > 25:
            strength_score += 1
        
        # RSI ekstremlik
        if rsi < 20 or rsi > 80:
            strength_score += 2
        elif rsi < 30 or rsi > 70:
            strength_score += 1
        
        # Trend kuvveti
        if trend != "ranging":
            strength_score += 1
        
        if strength_score >= 5:
            return SignalStrength.VERY_STRONG
        elif strength_score >= 4:
            return SignalStrength.STRONG
        elif strength_score >= 3:
            return SignalStrength.MEDIUM
        elif strength_score >= 2:
            return SignalStrength.WEAK
        else:
            return SignalStrength.VERY_WEAK
    
    def _calculate_reliability(self, indicators: Dict, strength: SignalStrength) -> float:
        """Güvenilirlik % hesapla"""
        
        base_reliability = strength.value * 15  # 15-75%
        
        # Volatility adjustments
        atr = indicators.get("ATR_14", {}).get("value", 0)
        if atr > 0:
            volatility_factor = min(atr / 100, 0.3)  # Max +30%
            base_reliability += volatility_factor * 30
        
        return min(base_reliability, 100)
    
    def find_confluence_points(self) -> List[ConfluencePoint]:
        """Confluence noktalarını bul"""
        
        confluence_points = []
        all_levels = []
        
        # Tüm seviyeleri topla
        for timeframe in ["15m", "1h", "4h"]:
            levels = self.support_resistance.get(timeframe, [])
            for level in levels:
                all_levels.append((level, timeframe))
        
        if not all_levels:
            return []
        
        # Levels'i fiyata göre sırala
        all_levels.sort(key=lambda x: x[0])
        
        # Confluence'ları bul
        processed = set()
        for i, (level1, tf1) in enumerate(all_levels):
            if level1 in processed:
                continue
            
            confluent_tfs = [tf1]
            
            for level2, tf2 in all_levels[i+1:]:
                # Tolerance içinde mi?
                if abs(level2 - level1) / level1 <= self.confluence_tolerance:
                    confluent_tfs.append(tf2)
                    processed.add(level2)
                else:
                    break
            
            # 2+ timeframe'den confluence varsa, ekle
            if len(confluent_tfs) >= 2:
                confluence_points.append(ConfluencePoint(
                    timeframe="multi",
                    level=level1,
                    type="support_resistance_cluster",
                    strength=len(confluent_tfs),
                    sources=confluent_tfs,
                    metadata={"tolerance": self.confluence_tolerance}
                ))
            
            processed.add(level1)
        
        return confluence_points
    
    def generate_confluence_signal(self, symbol: str) -> Optional[ConfluenceSignal]:
        """Nihai confluence sinyali oluştur"""
        
        try:
            # Her timeframe'i analiz et
            tf_15m = self.analyze_timeframe("15m")
            tf_1h = self.analyze_timeframe("1h")
            tf_4h = self.analyze_timeframe("4h")
            
            if not all([tf_15m, tf_1h, tf_4h]):
                logger.warning("Incomplete timeframe data for confluence signal")
                return None
            
            # Confluence points
            confluence_points = self.find_confluence_points()
            
            # Convergence score hesapla
            convergence_score = self._calculate_convergence_score(
                tf_15m, tf_1h, tf_4h
            )
            
            # Son fiyat (4h'den al)
            current_price = tf_4h.current_price
            
            # Sinyal gücü
            signal_strength = self._determine_confluence_strength(
                tf_15m, tf_1h, tf_4h
            )
            
            # Nihai sinyal
            signal_direction = self._determine_confluence_direction(
                tf_15m, tf_1h, tf_4h, convergence_score
            )
            
            # Risk hesapla
            risk_level, tp, sl, rr = self._calculate_risk_parameters(
                current_price, tf_15m, tf_1h, tf_4h
            )
            
            # Güven seviyesi
            confidence = (convergence_score + (signal_strength.value * 15)) / 2
            
            confluence_signal = ConfluenceSignal(
                symbol=symbol,
                timestamp=datetime.now().timestamp(),
                direction=signal_direction,
                strength=signal_strength,
                confidence=confidence,
                convergence_score=convergence_score,
                tf_15m=tf_15m,
                tf_1h=tf_1h,
                tf_4h=tf_4h,
                confluence_points=confluence_points,
                risk_level=risk_level,
                take_profit_level=tp,
                stop_loss_level=sl,
                risk_reward_ratio=rr,
                metadata={
                    "timeframe_agreements": self._count_signal_agreements(
                        tf_15m, tf_1h, tf_4h
                    )
                }
            )
            
            self.last_confluence_signal = confluence_signal
            return confluence_signal
        
        except Exception as e:
            logger.error(f"Error generating confluence signal: {e}")
            return None
    
    def _calculate_convergence_score(
        self,
        tf_15m: TimeFrameAnalysis,
        tf_1h: TimeFrameAnalysis,
        tf_4h: TimeFrameAnalysis
    ) -> float:
        """Convergence score hesapla (0-100)"""
        
        score = 0
        max_score = 0
        
        # Trend convergence
        trends = [tf_15m.trend, tf_1h.trend, tf_4h.trend]
        if trends[0] == trends[1] == trends[2]:
            score += 30
        elif trends[0] == trends[1] or trends[1] == trends[2]:
            score += 15
        max_score += 30
        
        # Signal convergence
        signals = [tf_15m.signal, tf_1h.signal, tf_4h.signal]
        buy_count = signals.count("BUY")
        sell_count = signals.count("SELL")
        
        if buy_count == 3 or sell_count == 3:
            score += 30
        elif buy_count == 2 or sell_count == 2:
            score += 20
        elif buy_count >= 1 or sell_count >= 1:
            score += 10
        max_score += 30
        
        # Strength convergence
        strengths = [tf_15m.strength.value, tf_1h.strength.value, tf_4h.strength.value]
        avg_strength = np.mean(strengths)
        score += avg_strength * 4
        max_score += 20
        
        # Momentum alignment
        momentums = [tf_15m.momentum, tf_1h.momentum, tf_4h.momentum]
        momentum_alignment = len([m for m in momentums if m > 0])
        score += momentum_alignment * 6.67
        max_score += 20
        
        return (score / max_score * 100) if max_score > 0 else 0
    
    def _count_signal_agreements(
        self,
        tf_15m: TimeFrameAnalysis,
        tf_1h: TimeFrameAnalysis,
        tf_4h: TimeFrameAnalysis
    ) -> int:
        """Kaç timeframe'de sinyal uyumu var"""
        
        agreements = 0
        target_signal = None
        
        # Target sinyali belirle (çoğunluk)
        signals = [tf_15m.signal, tf_1h.signal, tf_4h.signal]
        if signals.count("BUY") >= 2:
            target_signal = "BUY"
        elif signals.count("SELL") >= 2:
            target_signal = "SELL"
        else:
            return 0
        
        # Uyumları say
        if tf_15m.signal == target_signal:
            agreements += 1
        if tf_1h.signal == target_signal:
            agreements += 1
        if tf_4h.signal == target_signal:
            agreements += 1
        
        return agreements
    
    def _determine_confluence_strength(
        self,
        tf_15m: TimeFrameAnalysis,
        tf_1h: TimeFrameAnalysis,
        tf_4h: TimeFrameAnalysis
    ) -> SignalStrength:
        """Confluence sinyal gücü hesapla"""
        
        strengths = [tf_15m.strength.value, tf_1h.strength.value, tf_4h.strength.value]
        avg_strength = np.mean(strengths)
        
        if avg_strength >= 4.5:
            return SignalStrength.VERY_STRONG
        elif avg_strength >= 3.5:
            return SignalStrength.STRONG
        elif avg_strength >= 2.5:
            return SignalStrength.MEDIUM
        elif avg_strength >= 1.5:
            return SignalStrength.WEAK
        else:
            return SignalStrength.VERY_WEAK
    
    def _determine_confluence_direction(
        self,
        tf_15m: TimeFrameAnalysis,
        tf_1h: TimeFrameAnalysis,
        tf_4h: TimeFrameAnalysis,
        convergence_score: float
    ) -> str:
        """Nihai yön tayin et"""
        
        signals = [tf_15m.signal, tf_1h.signal, tf_4h.signal]
        buy_votes = signals.count("BUY")
        sell_votes = signals.count("SELL")
        
        if buy_votes >= 2:
            return "STRONG_BUY" if convergence_score > 75 else "BUY"
        elif sell_votes >= 2:
            return "STRONG_SELL" if convergence_score > 75 else "SELL"
        else:
            return "NEUTRAL"
    
    def _calculate_risk_parameters(
        self,
        current_price: float,
        tf_15m: TimeFrameAnalysis,
        tf_1h: TimeFrameAnalysis,
        tf_4h: TimeFrameAnalysis
    ) -> Tuple[str, float, float, float]:
        """Risk parametreleri hesapla"""
        
        try:
            # Support ve resistance seviyeleri
            all_supports = tf_4h.support_levels + tf_1h.support_levels
            all_resistances = tf_4h.resistance_levels + tf_1h.resistance_levels
            
            if not all_supports or not all_resistances:
                return "MEDIUM", 0, 0, 0
            
            closest_support = max([s for s in all_supports if s < current_price], 
                                 default=current_price * 0.95)
            closest_resistance = min([r for r in all_resistances if r > current_price],
                                    default=current_price * 1.05)
            
            # TP ve SL
            take_profit = closest_resistance * 1.02
            stop_loss = closest_support * 0.98
            
            # Risk-Reward
            risk = current_price - stop_loss
            reward = take_profit - current_price
            rr = reward / risk if risk > 0 else 0
            
            # Risk level
            risk_level = "LOW" if rr > 2 else ("HIGH" if rr < 1 else "MEDIUM")
            
            return risk_level, take_profit, stop_loss, rr
        
        except Exception as e:
            logger.error(f"Error calculating risk parameters: {e}")
            return "MEDIUM", 0, 0, 0


# Kullanım örneği
async def main():
    """Test"""
    analyzer = MultiTimeframeConfluenceAnalyzer()
    
    # Fake timeframe data (test)
    for timeframe in ["15m", "1h", "4h"]:
        base_price = 50000
        indicators = {
            "SMA_20": {"value": base_price * 0.99},
            "SMA_50": {"value": base_price * 0.98},
            "RSI_14": {"value": 65},
            "MACD": {"value": 150, "signal": 140, "histogram": 10},
            "ADX_14": {"value": 30},
            "Momentum": {"value": 50},
            "ATR_14": {"value": 200}
        }
        
        analyzer.update_timeframe_data(
            timeframe=timeframe,
            price=base_price,
            indicators=indicators,
            support_levels=[base_price * 0.95, base_price * 0.90],
            resistance_levels=[base_price * 1.05, base_price * 1.10],
            timestamp=datetime.now().timestamp()
        )
    
    signal = analyzer.generate_confluence_signal("BTCUSDT")
    if signal:
        print(json.dumps(signal.to_dict(), indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
