"""
Advanced Signal Processor - Sinyal İşleme ve Validasyon
DEMIR AI v6.0 - Phase 4 Production Grade

Sinyal filtrasyonu, doğrulaması, false-positive tespiti
Risk-adjusted signal scoring, ensemble methods
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import json

logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Sinyal türü"""
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"


@dataclass
class RawSignal:
    """Ham sinyal"""
    symbol: str
    timestamp: float
    type: SignalType
    price: float
    source: str  # Indicator adı
    strength: float  # 0-100%
    metadata: Dict = field(default_factory=dict)


@dataclass
class FilteredSignal:
    """Filtrelenmiş sinyal"""
    symbol: str
    timestamp: float
    type: SignalType
    price: float
    
    raw_signals: List[RawSignal] = field(default_factory=list)
    agreement_count: int = 0
    
    composite_strength: float = 0.0  # 0-100%
    confidence: float = 0.0  # 0-100%
    
    is_valid: bool = True
    validity_reason: str = ""
    
    risk_score: float = 0.0  # 0-100% risk
    entry_point: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Dict'e dönüştür"""
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "type": self.type.value,
            "price": self.price,
            "agreement_count": self.agreement_count,
            "composite_strength": self.composite_strength,
            "confidence": self.confidence,
            "is_valid": self.is_valid,
            "validity_reason": self.validity_reason,
            "risk_score": self.risk_score,
            "entry_point": self.entry_point,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "metadata": self.metadata
        }


class SignalValidator:
    """Sinyal Doğrulayıcı"""
    
    def __init__(self):
        """Başlat"""
        self.signal_history: Dict[str, List[FilteredSignal]] = {}
        self.false_positive_count: Dict[str, int] = {}
        self.true_positive_count: Dict[str, int] = {}
    
    def validate_signal(
        self,
        signal: FilteredSignal,
        recent_history: List[FilteredSignal]
    ) -> Tuple[bool, str]:
        """
        Sinyal doğrula
        
        Returns:
            (is_valid, reason)
        """
        
        # Zaman validasyonu
        if signal.timestamp <= 0:
            return False, "Invalid timestamp"
        
        # Fiyat validasyonu
        if signal.price <= 0:
            return False, "Invalid price"
        
        # Güven seviyesi
        if signal.confidence < 30:
            return False, f"Low confidence: {signal.confidence}%"
        
        # Yönelim validasyonu
        if signal.type == SignalType.NEUTRAL:
            return False, "Neutral signal"
        
        # Çok hızlı sinyal tespiti (false positive)
        if len(recent_history) > 0:
            last_signal = recent_history[-1]
            time_diff = signal.timestamp - last_signal.timestamp
            
            if time_diff < 300:  # 5 dakika
                return False, f"Too frequent signal: {time_diff}s"
        
        # Zıt sinyal tespiti
        if len(recent_history) > 0:
            last_signal = recent_history[-1]
            if signal.type != last_signal.type:
                if signal.confidence < 60:
                    return False, "Reversal signal with low confidence"
        
        # Extreme price moves tespiti
        if len(recent_history) > 0:
            recent_prices = [s.price for s in recent_history[-10:]]
            avg_price = np.mean(recent_prices)
            price_deviation = abs(signal.price - avg_price) / avg_price
            
            if price_deviation > 0.05:  # 5%
                if signal.confidence < 70:
                    return False, f"Extreme price move: {price_deviation*100:.2f}%"
        
        return True, "Valid"
    
    def register_signal_result(
        self,
        symbol: str,
        signal_type: SignalType,
        was_profitable: bool
    ):
        """Sinyal sonuçunu kaydet"""
        
        key = f"{symbol}_{signal_type.value}"
        
        if was_profitable:
            self.true_positive_count[key] = self.true_positive_count.get(key, 0) + 1
        else:
            self.false_positive_count[key] = self.false_positive_count.get(key, 0) + 1


class AdvancedSignalProcessor:
    """İleri Sinyal İşlemci"""
    
    def __init__(self, min_agreement: int = 2):
        """
        Args:
            min_agreement: Minimum sinyal uyumu (kaç indicator anlaşmalı)
        """
        self.min_agreement = min_agreement
        self.validator = SignalValidator()
        self.processed_signals: Dict[str, List[FilteredSignal]] = {}
        
        # Weighted scoring
        self.indicator_weights = {
            "RSI": 1.0,
            "MACD": 1.2,
            "BB": 0.9,
            "ADX": 1.1,
            "Stochastic": 0.8,
            "ATR": 0.7
        }
    
    def process_raw_signals(
        self,
        symbol: str,
        raw_signals: List[RawSignal],
        current_price: float
    ) -> Optional[FilteredSignal]:
        """
        Ham sinyalleri işle
        
        Args:
            symbol: Trading pair
            raw_signals: Ham sinyal listesi
            current_price: Mevcut fiyat
        
        Returns:
            Filtrelenmiş sinyal veya None
        """
        
        if not raw_signals:
            logger.warning(f"No raw signals for {symbol}")
            return None
        
        try:
            # Sinyalleri grupla
            buy_signals = [s for s in raw_signals if s.type == SignalType.BUY]
            sell_signals = [s for s in raw_signals if s.type == SignalType.SELL]
            
            # Hangi yön daha güçlü?
            buy_strength = self._calculate_group_strength(buy_signals)
            sell_strength = self._calculate_group_strength(sell_signals)
            
            if buy_strength > sell_strength:
                dominant_type = SignalType.BUY
                dominant_signals = buy_signals
                agreement_count = len(buy_signals)
            elif sell_strength > buy_strength:
                dominant_type = SignalType.SELL
                dominant_signals = sell_signals
                agreement_count = len(sell_signals)
            else:
                return self._create_neutral_signal(symbol, current_price, raw_signals)
            
            # Minimum anlaşma kontrolü
            if agreement_count < self.min_agreement:
                logger.debug(f"Insufficient agreement for {symbol}: {agreement_count} < {self.min_agreement}")
                return None
            
            # Composite strength hesapla
            composite_strength = self._calculate_composite_strength(dominant_signals)
            
            # Confidence hesapla
            confidence = self._calculate_confidence(
                agreement_count,
                len(raw_signals),
                composite_strength
            )
            
            # Risk score
            risk_score = self._calculate_risk_score(dominant_signals, current_price)
            
            # Entry, SL, TP
            entry, sl, tp = self._calculate_entry_sl_tp(
                current_price,
                dominant_type,
                dominant_signals
            )
            
            filtered_signal = FilteredSignal(
                symbol=symbol,
                timestamp=datetime.now().timestamp(),
                type=dominant_type,
                price=current_price,
                raw_signals=dominant_signals,
                agreement_count=agreement_count,
                composite_strength=composite_strength,
                confidence=confidence,
                is_valid=True,
                risk_score=risk_score,
                entry_point=entry,
                stop_loss=sl,
                take_profit=tp,
                metadata={
                    "buy_count": len(buy_signals),
                    "sell_count": len(sell_signals),
                    "raw_signal_count": len(raw_signals)
                }
            )
            
            # Doğrulama
            is_valid, reason = self.validator.validate_signal(
                filtered_signal,
                self.processed_signals.get(symbol, [])
            )
            
            filtered_signal.is_valid = is_valid
            filtered_signal.validity_reason = reason
            
            if not is_valid:
                logger.debug(f"Signal validation failed for {symbol}: {reason}")
                return None
            
            # History'ye ekle
            if symbol not in self.processed_signals:
                self.processed_signals[symbol] = []
            
            self.processed_signals[symbol].append(filtered_signal)
            
            logger.info(f"Processed signal for {symbol}: {dominant_type.value} "
                       f"(strength={composite_strength:.1f}%, confidence={confidence:.1f}%)")
            
            return filtered_signal
        
        except Exception as e:
            logger.error(f"Error processing raw signals: {e}")
            return None
    
    def _calculate_group_strength(self, signals: List[RawSignal]) -> float:
        """Grup sinyal gücü hesapla"""
        
        if not signals:
            return 0
        
        weighted_strength = 0
        total_weight = 0
        
        for signal in signals:
            weight = self.indicator_weights.get(signal.source, 1.0)
            weighted_strength += signal.strength * weight
            total_weight += weight
        
        return weighted_strength / total_weight if total_weight > 0 else 0
    
    def _calculate_composite_strength(self, signals: List[RawSignal]) -> float:
        """Composite strength hesapla"""
        
        if not signals:
            return 0
        
        strengths = [s.strength for s in signals]
        mean_strength = np.mean(strengths)
        std_strength = np.std(strengths) if len(strengths) > 1 else 0
        
        # Consistency bonus
        consistency_bonus = (1 - (std_strength / 100)) * 10 if std_strength > 0 else 5
        
        return min(mean_strength + consistency_bonus, 100)
    
    def _calculate_confidence(
        self,
        agreement_count: int,
        total_signals: int,
        composite_strength: float
    ) -> float:
        """Güven seviyesi hesapla"""
        
        # Agreement oranı
        agreement_ratio = agreement_count / total_signals if total_signals > 0 else 0
        agreement_score = agreement_ratio * 50
        
        # Strength katkısı
        strength_score = composite_strength * 0.5
        
        return agreement_score + strength_score
    
    def _calculate_risk_score(
        self,
        signals: List[RawSignal],
        current_price: float
    ) -> float:
        """Risk puanı hesapla (0-100)"""
        
        if not signals:
            return 50
        
        # Volatility tespiti
        volatility_indicator = any(s.source == "ATR" for s in signals)
        volatility_score = 30 if volatility_indicator else 50
        
        # Signal consistency
        strengths = [s.strength for s in signals]
        consistency = (1 - (np.std(strengths) / 100)) * 50 if len(strengths) > 1 else 50
        
        return (volatility_score + consistency) / 2
    
    def _calculate_entry_sl_tp(
        self,
        current_price: float,
        signal_type: SignalType,
        signals: List[RawSignal]
    ) -> Tuple[float, float, float]:
        """Entry, Stop Loss, Take Profit hesapla"""
        
        # Temel hesaplama
        if signal_type == SignalType.BUY or signal_type == SignalType.STRONG_BUY:
            entry = current_price * 1.0005  # 0.05% slippage
            stop_loss = current_price * 0.97  # 3% below
            take_profit = current_price * 1.05  # 5% above
        else:  # SELL
            entry = current_price * 0.9995
            stop_loss = current_price * 1.03
            take_profit = current_price * 0.95
        
        return entry, stop_loss, take_profit
    
    def _create_neutral_signal(
        self,
        symbol: str,
        current_price: float,
        raw_signals: List[RawSignal]
    ) -> Optional[FilteredSignal]:
        """Neutral sinyal oluştur"""
        
        signal = FilteredSignal(
            symbol=symbol,
            timestamp=datetime.now().timestamp(),
            type=SignalType.NEUTRAL,
            price=current_price,
            raw_signals=raw_signals,
            agreement_count=0,
            composite_strength=0,
            confidence=0,
            is_valid=False,
            validity_reason="No dominant signal"
        )
        
        return signal
    
    def get_signal_history(self, symbol: str) -> List[FilteredSignal]:
        """Sinyal geçmişi al"""
        
        return self.processed_signals.get(symbol, [])
    
    def get_latest_signal(self, symbol: str) -> Optional[FilteredSignal]:
        """Son sinyali al"""
        
        history = self.get_signal_history(symbol)
        return history[-1] if history else None
    
    def get_signal_statistics(self, symbol: str) -> Dict:
        """Sinyal istatistikleri"""
        
        history = self.get_signal_history(symbol)
        
        if not history:
            return {}
        
        buy_signals = [s for s in history if s.type == SignalType.BUY]
        sell_signals = [s for s in history if s.type == SignalType.SELL]
        
        return {
            "total_signals": len(history),
            "buy_signals": len(buy_signals),
            "sell_signals": len(sell_signals),
            "avg_confidence": np.mean([s.confidence for s in history]),
            "avg_composite_strength": np.mean([s.composite_strength for s in history]),
            "last_signal": history[-1].to_dict() if history else None
        }


# Kullanım örneği
async def main():
    """Test"""
    
    processor = AdvancedSignalProcessor(min_agreement=2)
    
    # Test sinyalleri
    raw_signals = [
        RawSignal(
            symbol="BTCUSDT",
            timestamp=datetime.now().timestamp(),
            type=SignalType.BUY,
            price=50000,
            source="RSI",
            strength=75
        ),
        RawSignal(
            symbol="BTCUSDT",
            timestamp=datetime.now().timestamp(),
            type=SignalType.BUY,
            price=50000,
            source="MACD",
            strength=80
        ),
        RawSignal(
            symbol="BTCUSDT",
            timestamp=datetime.now().timestamp(),
            type=SignalType.BUY,
            price=50000,
            source="ADX",
            strength=70
        )
    ]
    
    filtered = processor.process_raw_signals("BTCUSDT", raw_signals, 50000)
    
    if filtered:
        print(json.dumps(filtered.to_dict(), indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
