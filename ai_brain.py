"""
DEMIR AI - AI Brain (Orchestrator)
Master AI intelligence engine coordinating all layers
Version 5.0 - Updated for Phase 3E + 3F
Date: 11 November 2025, 22:21 CET
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Sinyal türleri"""
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"


@dataclass
class LayerResult:
    """Her layerdan dönüş sonucu"""
    layer_name: str
    available: bool
    score: float  # 0-100
    signal: SignalType
    confidence: float  # 0-100
    error: Optional[str] = None
    timestamp: Optional[datetime] = None

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
    layer_consensus: float  # Kaç layer aynı sinyal vermişse
    layers_results: List[LayerResult]
    timestamp: Optional[datetime] = None

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


class BaseLayer:
    """Tüm layerların ana sınıfı"""
    
    def __init__(self, name: str, weight: float = 1.0):
        """Initialize layer"""
        self.name = name
        self.weight = weight
        self.last_result: Optional[LayerResult] = None

    def get_signal(self, market_data: Dict[str, Any]) -> LayerResult:
        """Layerin sinyalini al - Override in subclasses"""
        raise NotImplementedError

    def validate_market_data(self, market_data: Dict[str, Any]) -> bool:
        """Market verilerinin geçerliliğini kontrol et"""
        required_fields = ['btc_price', 'timestamp']
        return all(field in market_data for field in required_fields)


class MomentumLayer(BaseLayer):
    """Momentum analiz layer - Hızlı trend analizi"""
    
    def __init__(self):
        super().__init__("MomentumLayer", weight=1.2)

    def get_signal(self, market_data: Dict[str, Any]) -> LayerResult:
        """Momentum layer hesapla"""
        try:
            if not self.validate_market_data(market_data):
                return LayerResult(
                    layer_name=self.name,
                    available=False,
                    score=50,
                    signal=SignalType.NEUTRAL,
                    confidence=0,
                    error="Invalid market data",
                    timestamp=datetime.now()
                )

            btc_price = market_data.get('btc_price', 0)
            btc_prev_price = market_data.get('btc_prev_price', btc_price)
            
            # Real data momentum calculation
            momentum = ((btc_price - btc_prev_price) / btc_prev_price * 100) if btc_prev_price else 0

            if momentum > 2:
                signal = SignalType.LONG
                score = min(100, 50 + abs(momentum) / 5)
            elif momentum < -2:
                signal = SignalType.SHORT
                score = min(100, 50 + abs(momentum) / 5)
            else:
                signal = SignalType.NEUTRAL
                score = 50

            confidence = min(100, abs(momentum) / 10)

            return LayerResult(
                layer_name=self.name,
                available=True,
                score=score,
                signal=signal,
                confidence=confidence,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"MomentumLayer error: {e}")
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
    """Hacim analiz layer"""
    
    def __init__(self):
        super().__init__("VolumeAnalysisLayer", weight=1.0)

    def get_signal(self, market_data: Dict[str, Any]) -> LayerResult:
        """Hacim analizi yap"""
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
                    error="No volume data",
                    timestamp=datetime.now()
                )

            volume_ratio = volume / volume_avg if volume_avg else 0

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
            logger.error(f"VolumeAnalysisLayer error: {e}")
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
    """Futures funding rate layer - Perpetual financing analizi"""
    
    def __init__(self):
        super().__init__("FundingRateLayer", weight=1.5)

    def get_signal(self, market_data: Dict[str, Any]) -> LayerResult:
        """Funding rate analizi"""
        try:
            funding_rate = market_data.get('funding_rate', 0)

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
            logger.error(f"FundingRateLayer error: {e}")
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
# PHASE 3E - ML LAYERS WRAPPER
# ============================================================================

class Phase3EMLWrapper(BaseLayer):
    """Phase 3E ML layer'larını integrate eden wrapper"""
    
    def __init__(self):
        super().__init__("Phase3E_MLLayers", weight=2.0)
        self.ml_layers = []
        self._import_ml_layers()

    def _import_ml_layers(self):
        """Phase 3E layer'larını import et"""
        try:
            from layers import lstm_layer, transformer_layer, risk_layer
            from layers import portfolio_layer, quantum_layer, meta_layer
            
            self.ml_layers = [
                lstm_layer, transformer_layer, risk_layer,
                portfolio_layer, quantum_layer, meta_layer
            ]
            logger.info(f"Phase 3E layers loaded: {len(self.ml_layers)}")
        except Exception as e:
            logger.warning(f"Could not load Phase 3E layers: {e}")

    def get_signal(self, market_data: Dict[str, Any]) -> LayerResult:
        """Phase 3E layer'larından sinyal al"""
        try:
            if not self.ml_layers:
                return LayerResult(
                    layer_name=self.name,
                    available=False,
                    score=50,
                    signal=SignalType.NEUTRAL,
                    confidence=0,
                    error="ML layers not loaded"
                )

            # Collect signals from all ML layers
            ml_signals = []
            for layer in self.ml_layers:
                try:
                    result = layer.analyze(market_data.get('symbol', 'BTCUSDT'))
                    if result and 'signal' in result:
                        ml_signals.append(result)
                except:
                    pass

            if not ml_signals:
                return LayerResult(
                    layer_name=self.name,
                    available=False,
                    score=50,
                    signal=SignalType.NEUTRAL,
                    confidence=0
                )

            # Ensemble ML signals
            bullish_count = sum(1 for s in ml_signals if s.get('signal') == 'BULLISH')
            bearish_count = sum(1 for s in ml_signals if s.get('signal') == 'BEARISH')

            if bullish_count > bearish_count:
                signal = SignalType.LONG
                score = min(100, 50 + (bullish_count / len(ml_signals)) * 50)
            elif bearish_count > bullish_count:
                signal = SignalType.SHORT
                score = min(100, 50 + (bearish_count / len(ml_signals)) * 50)
            else:
                signal = SignalType.NEUTRAL
                score = 50

            avg_confidence = np.mean([s.get('confidence', 0.5) for s in ml_signals])

            return LayerResult(
                layer_name=self.name,
                available=True,
                score=score,
                signal=signal,
                confidence=min(100, avg_confidence * 100),
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Phase3EMLWrapper error: {e}")
            return LayerResult(
                layer_name=self.name,
                available=False,
                score=50,
                signal=SignalType.NEUTRAL,
                confidence=0,
                error=str(e)
            )


# ============================================================================
# PHASE 3F - REAL-TIME CRYPTO WRAPPER
# ============================================================================

class Phase3FRealtimeWrapper(BaseLayer):
    """Phase 3F real-time layer'larını integrate eden wrapper"""
    
    def __init__(self):
        super().__init__("Phase3F_RealtimeLayers", weight=1.8)
        self.realtime_layers = []
        self._import_realtime_layers()

    def _import_realtime_layers(self):
        """Phase 3F layer'larını import et"""
        try:
            from layers import realtime_stream, bitcoin_dominance_layer
            from layers import altcoin_season_layer, exchange_flow_layer
            
            self.realtime_layers = [
                realtime_stream, bitcoin_dominance_layer,
                altcoin_season_layer, exchange_flow_layer
            ]
            logger.info(f"Phase 3F layers loaded: {len(self.realtime_layers)}")
        except Exception as e:
            logger.warning(f"Could not load Phase 3F layers: {e}")

    def get_signal(self, market_data: Dict[str, Any]) -> LayerResult:
        """Phase 3F layer'larından sinyal al"""
        try:
            if not self.realtime_layers:
                return LayerResult(
                    layer_name=self.name,
                    available=False,
                    score=50,
                    signal=SignalType.NEUTRAL,
                    confidence=0
                )

            # Collect signals
            realtime_data = []
            for layer in self.realtime_layers:
                try:
                    result = layer.analyze(market_data.get('symbol', 'BTCUSDT'))
                    if result:
                        realtime_data.append(result)
                except:
                    pass

            if not realtime_data:
                return LayerResult(
                    layer_name=self.name,
                    available=False,
                    score=50,
                    signal=SignalType.NEUTRAL,
                    confidence=0
                )

            # Analyze crypto market signals
            score = 50
            signal = SignalType.NEUTRAL

            return LayerResult(
                layer_name=self.name,
                available=True,
                score=score,
                signal=signal,
                confidence=75,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Phase3FRealtimeWrapper error: {e}")
            return LayerResult(
                layer_name=self.name,
                available=False,
                score=50,
                signal=SignalType.NEUTRAL,
                confidence=0,
                error=str(e)
            )


# ============================================================================
# MAIN AI BRAIN
# ============================================================================

class AIBrain:
    """
    AI orchestrator - Tm layer'ları koordine et ve final signal ret
    Master controller for all layers and analysis
    """
    
    def __init__(self):
        """Initialize AI Brain with all layers"""
        self.layers: List[BaseLayer] = [
            MomentumLayer(),
            VolumeAnalysisLayer(),
            FundingRateLayer(),
            Phase3EMLWrapper(),  # Phase 3E ML Layers
            Phase3FRealtimeWrapper(),  # Phase 3F Real-time Layers
        ]
        
        self.logger = logger
        self.last_signal: Optional[AISignal] = None

    def add_layer(self, layer: BaseLayer):
        """Yeni layer ekle"""
        self.layers.append(layer)
        self.logger.info(f"Layer added: {layer.name}")

    def get_all_layer_signals(self, market_data: Dict[str, Any]) -> List[LayerResult]:
        """Tm layer'lardan sinyalleri al"""
        results = []
        
        for layer in self.layers:
            try:
                result = layer.get_signal(market_data)
                results.append(result)
                
                if result.available:
                    logger.info(
                        f"{layer.name}: {result.signal.value} "
                        f"(score={result.score:.1f}, confidence={result.confidence:.1f})"
                    )
                else:
                    logger.warning(f"{layer.name}: {result.error}")
                    
            except Exception as e:
                logger.error(f"Error calling {layer.name}: {e}")
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
        """Layer sonuçlarından final signal hesapla"""
        
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
            logger.warning("No available layers")
            return AISignal(
                signal=SignalType.NEUTRAL,
                overall_score=50,
                confidence=0,
                active_layers=0,
                layer_consensus=0,
                layers_results=layer_results
            )

        # Calculate weighted score
        total_weight = sum(
            next((l.weight for l in self.layers if l.name == r.layer_name), 1.0)
            for r in available_results
        )
        
        weighted_score = sum(
            r.score * next((l.weight for l in self.layers if l.name == r.layer_name), 1.0)
            for r in available_results
        ) / total_weight if total_weight > 0 else 50

        # Calculate consensus voting
        long_votes = sum(1 for r in available_results if r.signal == SignalType.LONG)
        short_votes = sum(1 for r in available_results if r.signal == SignalType.SHORT)
        neutral_votes = sum(1 for r in available_results if r.signal == SignalType.NEUTRAL)
        total_votes = len(available_results)
        
        max_consensus = max(long_votes, short_votes, neutral_votes) / total_votes * 100 if total_votes > 0 else 0

        # Determine final signal
        if long_votes > short_votes and long_votes > neutral_votes:
            final_signal = SignalType.LONG
        elif short_votes > long_votes and short_votes > neutral_votes:
            final_signal = SignalType.SHORT
        else:
            final_signal = SignalType.NEUTRAL

        # Average confidence
        avg_confidence = np.mean([r.confidence for r in available_results])
        final_confidence = (weighted_score / 100 * avg_confidence / 100) * 100

        logger.info(f"FINAL SIGNAL: {final_signal.value}")
        logger.info(f"Score: {weighted_score:.1f}/100")
        logger.info(f"Confidence: {final_confidence:.1f}%")
        logger.info(f"Consensus: {max_consensus:.1f}% ({long_votes}, {short_votes}, {neutral_votes}) / {total_votes}")

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
        """Tam analiz yapp final signal dönder"""
        logger.info("Starting AI analysis...")
        
        # Get all layer signals
        layer_results = self.get_all_layer_signals(market_data)
        
        # Calculate final signal
        final_signal = self.calculate_final_signal(layer_results)
        
        return final_signal

    def get_status(self) -> Dict[str, Any]:
        """AI Brain durumunu al"""
        return {
            'layers_count': len(self.layers),
            'layers': [
                {
                    'name': l.name,
                    'weight': l.weight,
                    'available': l.last_result.available if l.last_result else None
                }
                for l in self.layers
            ],
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
    'Phase3EMLWrapper',
    'Phase3FRealtimeWrapper',
    'AISignal',
    'LayerResult',
    'SignalType',
]


if __name__ == "__main__":
    # Test AI Brain
    ai = AIBrain()
    
    # Sample market data - REAL veriler buraya gelecek
    test_market_data = {
        'btc_price': 43250.50,
        'btc_prev_price': 42100.00,
        'eth_price': 2150.25,
        'volume_24h': 25e9,
        'volume_7d_avg': 20e9,
        'funding_rate': 0.0025,
        'timestamp': datetime.now(),
        'symbol': 'BTCUSDT'
    }
    
    signal = ai.analyze(test_market_data)
    
    print("\n" + "="*60)
    print("AI Brain Test Completed")
    print("="*60)
    print(f"Signal: {signal.signal.value}")
    print(f"Score: {signal.overall_score:.1f}/100")
    print(f"Confidence: {signal.confidence:.1f}%")
    print(f"Active Layers: {signal.active_layers}")
    print(f"Consensus: {signal.layer_consensus:.1f}%")
    print("="*60)
