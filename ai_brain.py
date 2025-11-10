# ============================================================================
# DEMIR AI - AI BRAIN & LAYER ORCHESTRATOR
# ============================================================================
# Date: November 10, 2025
# Purpose: Tüm layers'ı koordine et, signal üret, AI scoring
#
# 🔒 KURALLAR:
# - ZERO MOCK DATA - Tüm layer'lardan gerçek veri al
# - 17+ layer'ı ensemble olarak kombine et
# - Fallback logic: hatalı layer'ları skip et
# - Sinyal: LONG/SHORT/NEUTRAL döndür
# ============================================================================

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

class SignalType(Enum):
    """Sinyal türleri"""
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"

@dataclass
class LayerResult:
    """Her layer'dan dönen sonuç yapısı"""
    layer_name: str
    available: bool
    score: float  # 0-100
    signal: SignalType
    confidence: float  # 0-100
    error: Optional[str] = None
    timestamp: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'layer_name': self.layer_name,
            'available': self.available,
            'score': self.score,
            'signal': self.signal.value,
            'confidence': self.confidence,
            'error': self.error,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

@dataclass
class AISignal:
    """Final AI Signal sonucu"""
    signal: SignalType
    overall_score: float  # 0-100
    confidence: float  # 0-100
    active_layers: int
    layer_consensus: float  # Kaç % layer aynı sinyal vermişse
    layers_results: List[LayerResult]
    timestamp: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'signal': self.signal.value,
            'overall_score': self.overall_score,
            'confidence': self.confidence,
            'active_layers': self.active_layers,
            'layer_consensus': self.layer_consensus,
            'layers': [l.to_dict() for l in self.layers_results],
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

# ============================================================================
# LAYER ABSTRACTION
# ============================================================================

class BaseLayer:
    """
    Tüm layer'ların ana sınıfı
    - Gerçek API'den veri al
    - Fallback logic
    - Standard return format
    """
    
    def __init__(self, name: str, weight: float = 1.0):
        """
        Initialize layer
        
        Args:
            name: Layer adı (Layer Adı)
            weight: Ensemble'da ağırlığı (Ensemble'da ne kadar etkili)
        """
        self.name = name
        self.weight = weight
        self.last_result: Optional[LayerResult] = None
        
    def get_signal(self, market_data: Dict[str, Any]) -> LayerResult:
        """
        Layer'ın sinyalini al (Layer'ın kendi sinyalini al)
        
        Override this in subclasses
        """
        raise NotImplementedError
    
    def validate_market_data(self, market_data: Dict[str, Any]) -> bool:
        """Market verilerinin geçerli olup olmadığını kontrol et"""
        required_fields = ['btc_price', 'eth_price', 'timestamp']
        return all(field in market_data for field in required_fields)

# ============================================================================
# SAMPLE LAYER IMPLEMENTATIONS
# ============================================================================

class MomentumLayer(BaseLayer):
    """Momentum analiz layer (Hızlı trend analiz)"""
    
    def __init__(self):
        super().__init__("MomentumLayer", weight=1.2)
    
    def get_signal(self, market_data: Dict[str, Any]) -> LayerResult:
        """
        Momentum layer'ı hesapla (Trend hızını analiz et)
        
        Returns: LayerResult (signal, score, confidence)
        """
        try:
            if not self.validate_market_data(market_data):
                return LayerResult(
                    layer_name=self.name,
                    available=False,
                    score=50,
                    signal=SignalType.NEUTRAL,
                    confidence=0,
                    error="Invalid market data (Geçersiz pazar verisi)",
                    timestamp=datetime.now()
                )
            
            # Real data gelen momentum hesapla
            btc_price = market_data.get('btc_price', 0)
            btc_prev_price = market_data.get('btc_prev_price', btc_price)
            momentum = ((btc_price - btc_prev_price) / btc_prev_price * 100) if btc_prev_price else 0
            
            # Signal karar ver
            if momentum > 2:
                signal = SignalType.LONG
                score = min(100, 50 + abs(momentum) * 5)
            elif momentum < -2:
                signal = SignalType.SHORT
                score = min(100, 50 + abs(momentum) * 5)
            else:
                signal = SignalType.NEUTRAL
                score = 50
            
            confidence = min(100, abs(momentum) * 10)
            
            return LayerResult(
                layer_name=self.name,
                available=True,
                score=score,
                signal=signal,
                confidence=confidence,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"MomentumLayer hatası: {e}")
            return LayerResult(
                layer_name=self.name,
                available=False,
                score=50,
                signal=SignalType.NEUTRAL,
                confidence=0,
                error=str(e),
                timestamp=datetime.now()
            )

class VolumeAnalysisLayer(BaseLayer):
    """Hacim analiz layer (İşlem hacmi trenini analiz et)"""
    
    def __init__(self):
        super().__init__("VolumeAnalysisLayer", weight=1.0)
    
    def get_signal(self, market_data: Dict[str, Any]) -> LayerResult:
        """Hacim analizi yap (Volume analysis)"""
        try:
            volume = market_data.get('volume_24h', 0)
            volume_avg = market_data.get('volume_7d_avg', 0)
            
            if volume == 0 or volume_avg == 0:
                return LayerResult(
                    layer_name=self.name,
                    available=False,
                    score=50,
                    signal=SignalType.NEUTRAL,
                    confidence=0,
                    error="No volume data (Hacim verisi yok)",
                    timestamp=datetime.now()
                )
            
            volume_ratio = volume / volume_avg
            
            if volume_ratio > 1.2:
                signal = SignalType.LONG
                score = min(100, 50 + (volume_ratio - 1.0) * 50)
            elif volume_ratio < 0.8:
                signal = SignalType.SHORT
                score = min(100, 50 + (1.0 - volume_ratio) * 50)
            else:
                signal = SignalType.NEUTRAL
                score = 50
            
            confidence = min(100, abs(volume_ratio - 1.0) * 100)
            
            return LayerResult(
                layer_name=self.name,
                available=True,
                score=score,
                signal=signal,
                confidence=confidence,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"VolumeAnalysisLayer hatası: {e}")
            return LayerResult(
                layer_name=self.name,
                available=False,
                score=50,
                signal=SignalType.NEUTRAL,
                confidence=0,
                error=str(e),
                timestamp=datetime.now()
            )

class FundingRateLayer(BaseLayer):
    """Funding rate layer (Futures funding rate analizi)"""
    
    def __init__(self):
        super().__init__("FundingRateLayer", weight=1.5)
    
    def get_signal(self, market_data: Dict[str, Any]) -> LayerResult:
        """Funding rate analizi (Perpetual funding oranı)"""
        try:
            funding_rate = market_data.get('funding_rate', 0)
            
            # Yüksek positive funding = long'lar ödüyor = short kurucular = SHORT sinyal
            # Düşük/negative funding = short'lar ödüyor = long kurucular = LONG sinyal
            
            if funding_rate > 0.05:
                signal = SignalType.SHORT
                score = min(100, 50 + funding_rate * 500)
            elif funding_rate < -0.05:
                signal = SignalType.LONG
                score = min(100, 50 + abs(funding_rate) * 500)
            else:
                signal = SignalType.NEUTRAL
                score = 50
            
            confidence = min(100, abs(funding_rate) * 1000)
            
            return LayerResult(
                layer_name=self.name,
                available=True,
                score=score,
                signal=signal,
                confidence=confidence,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"FundingRateLayer hatası: {e}")
            return LayerResult(
                layer_name=self.name,
                available=False,
                score=50,
                signal=SignalType.NEUTRAL,
                confidence=0,
                error=str(e),
                timestamp=datetime.now()
            )

# ============================================================================
# AI BRAIN - ORCHESTRATOR
# ============================================================================

class AIBrain:
    """
    AI orchestrator - Tüm layer'ları koordine et ve final signal üret
    (Yapay Zeka Beyni - Tüm analiz katmanlarını kontrol et)
    """
    
    def __init__(self):
        """Initialize AI Brain with all layers"""
        self.layers: List[BaseLayer] = [
            MomentumLayer(),
            VolumeAnalysisLayer(),
            FundingRateLayer(),
            # Burada diğer 14+ layer'ı da ekleyebilirsin
            # TODO: Tüm layers/ klasöründeki layer'ları import et
        ]
        
        self.logger = logger
        self.last_signal: Optional[AISignal] = None
    
    def add_layer(self, layer: BaseLayer):
        """Yeni layer ekle"""
        self.layers.append(layer)
        logger.info(f"✅ Layer eklendi: {layer.name}")
    
    def get_all_layer_signals(self, market_data: Dict[str, Any]) -> List[LayerResult]:
        """
        Tüm layer'lardan sinyalleri al (Get signals from all layers)
        
        Args:
            market_data: Pazar verisi (Market data dictionary)
        
        Returns:
            List[LayerResult]: Tüm layer sonuçları
        """
        results = []
        
        for layer in self.layers:
            try:
                result = layer.get_signal(market_data)
                results.append(result)
                
                if result.available:
                    logger.info(
                        f"✅ {layer.name}: {result.signal.value} "
                        f"(score={result.score:.1f}, confidence={result.confidence:.1f})"
                    )
                else:
                    logger.warning(f"⚠️ {layer.name}: {result.error}")
                    
            except Exception as e:
                logger.error(f"❌ {layer.name} çalıştırırken hata: {e}")
                results.append(LayerResult(
                    layer_name=layer.name,
                    available=False,
                    score=50,
                    signal=SignalType.NEUTRAL,
                    confidence=0,
                    error=str(e),
                    timestamp=datetime.now()
                ))
        
        return results
    
    def calculate_final_signal(self, layer_results: List[LayerResult]) -> AISignal:
        """
        Layer sonuçlarından final signal hesapla (Calculate final signal from layers)
        
        Uses:
        - Weighted ensemble (Ağırlıklı ensemble)
        - Consensus voting (Oy birliği)
        - Confidence filtering (Güven filtreleme)
        """
        
        if not layer_results:
            return AISignal(
                signal=SignalType.NEUTRAL,
                overall_score=50,
                confidence=0,
                active_layers=0,
                layer_consensus=0,
                layers_results=[]
            )
        
        # Filter available layers
        available_results = [r for r in layer_results if r.available]
        
        if not available_results:
            logger.warning("⚠️ Hiçbir layer mevcut değil (No available layers)")
            return AISignal(
                signal=SignalType.NEUTRAL,
                overall_score=50,
                confidence=0,
                active_layers=0,
                layer_consensus=0,
                layers_results=layer_results
            )
        
        # Calculate weighted average score
        total_weight = sum(
            next((l.weight for l in self.layers if l.name == r.layer_name), 1.0)
            for r in available_results
        )
        
        weighted_score = sum(
            r.score * next((l.weight for l in self.layers if l.name == r.layer_name), 1.0)
            for r in available_results
        ) / total_weight
        
        # Calculate consensus (Oy birliğini hesapla)
        long_votes = sum(1 for r in available_results if r.signal == SignalType.LONG)
        short_votes = sum(1 for r in available_results if r.signal == SignalType.SHORT)
        neutral_votes = sum(1 for r in available_results if r.signal == SignalType.NEUTRAL)
        
        total_votes = len(available_results)
        max_consensus = max(long_votes, short_votes, neutral_votes) / total_votes * 100
        
        # Determine final signal
        if long_votes > short_votes and long_votes > neutral_votes:
            final_signal = SignalType.LONG
        elif short_votes > long_votes and short_votes > neutral_votes:
            final_signal = SignalType.SHORT
        else:
            final_signal = SignalType.NEUTRAL
        
        # Calculate confidence
        avg_confidence = np.mean([r.confidence for r in available_results])
        final_confidence = (weighted_score / 100) * (avg_confidence / 100) * max_consensus
        
        logger.info(f"📊 FINAL SIGNAL: {final_signal.value}")
        logger.info(f"   Score: {weighted_score:.1f}/100")
        logger.info(f"   Confidence: {final_confidence:.1f}%")
        logger.info(f"   Consensus: {max_consensus:.1f}% ({max(long_votes, short_votes, neutral_votes)}/{total_votes})")
        
        ai_signal = AISignal(
            signal=final_signal,
            overall_score=weighted_score,
            confidence=final_confidence,
            active_layers=len(available_results),
            layer_consensus=max_consensus,
            layers_results=layer_results,
            timestamp=datetime.now()
        )
        
        self.last_signal = ai_signal
        return ai_signal
    
    def analyze(self, market_data: Dict[str, Any]) -> AISignal:
        """
        Tam analiz yapıp final signal döndür (Complete analysis pipeline)
        
        Args:
            market_data: Tüm pazar verisi
        
        Returns:
            AISignal: Final AI sinyali
        """
        logger.info("🔄 AI Analizi başlatıldı...")
        
        # Get all layer signals
        layer_results = self.get_all_layer_signals(market_data)
        
        # Calculate final signal
        final_signal = self.calculate_final_signal(layer_results)
        
        return final_signal
    
    def get_status(self) -> Dict[str, Any]:
        """AI Brain durumunu al (Get AI Brain status)"""
        return {
            'layers_count': len(self.layers),
            'last_signal': self.last_signal.to_dict() if self.last_signal else None,
            'timestamp': datetime.now().isoformat()
        }

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'AIBrain',
    'BaseLayer',
    'MomentumLayer',
    'VolumeAnalysisLayer',
    'FundingRateLayer',
    'AISignal',
    'LayerResult',
    'SignalType'
]

# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    # Test AI Brain
    ai = AIBrain()
    
    # Sample market data (GERÇEK veriler buraya gelecek)
    test_market_data = {
        'btc_price': 43250.50,
        'btc_prev_price': 42100.00,
        'eth_price': 2150.25,
        'volume_24h': 25e9,
        'volume_7d_avg': 20e9,
        'funding_rate': 0.0025,
        'timestamp': datetime.now()
    }
    
    # Analyze
    signal = ai.analyze(test_market_data)
    
    print(f"\n✅ AI Brain Test Completed")
    print(f"Signal: {signal.signal.value}")
    print(f"Score: {signal.overall_score:.1f}/100")
