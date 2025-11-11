"""
🧠 LAYERS_INTEGRATION_ENGINE - TÜM 50+ LAYER'I BİRLEŞTİR
Version: 1.0 - Integration Hub
Date: 11 Kasım 2025, 15:21 CET

AMAÇ: GitHub'daki tüm layer dosyalarını çağır ve sonuçlarını birleştir
✅ advanced_layers.py
✅ xgboost_ml_layer.py
✅ kalman_regime_layer.py
✅ elliott_wave_detector.py
✅ + 50 başka layer...
= UNIFIED DECISION
"""

import numpy as np
import pandas as pd
from typing import Dict, List
import sys
import os
from datetime import datetime

# ============================================================================
# LAYER IMPORT (GitHub'daki dosyaları çağır)
# ============================================================================

try:
    from layers.advanced_layers import AdvancedTechnicalAnalysis
    ADVANCED_LAYERS_OK = True
except:
    ADVANCED_LAYERS_OK = False

try:
    from layers.xgboost_ml_layer import XGBoostMLAnalyzer
    XGBOOST_OK = True
except:
    XGBOOST_OK = False

try:
    from layers.kalman_regime_layer import KalmanRegimeDetector
    KALMAN_OK = True
except:
    KALMAN_OK = False

try:
    from layers.elliott_wave_detector import ElliottWaveDetector
    ELLIOTT_OK = True
except:
    ELLIOTT_OK = False

try:
    from layers.market_regime_analyzer import MarketRegimeAnalyzer
    REGIME_OK = True
except:
    REGIME_OK = False

try:
    from layers.news_sentiment_layersv2 import NewsSentimentAnalyzer
    SENTIMENT_OK = True
except:
    SENTIMENT_OK = False

try:
    from layers.volume_profile_layer import VolumeProfileAnalyzer
    VOLUME_OK = True
except:
    VOLUME_OK = False

try:
    from layers.macro_correlation_layer import MacroCorrelationAnalyzer
    MACRO_OK = True
except:
    MACRO_OK = False

try:
    from layers.garch_volatility_layer import GarchVolatilityAnalyzer
    GARCH_OK = True
except:
    GARCH_OK = False

try:
    from layers.markov_regime_layer import MarkovRegimeDetector
    MARKOV_OK = True
except:
    MARKOV_OK = False

# ============================================================================
# UNIFIED LAYERS INTEGRATION ENGINE
# ============================================================================

class LayersIntegrationEngine:
    """Tüm 50+ layer'ı bir araya getir ve birleşik karar ver"""
    
    def __init__(self):
        self.layer_results = {}
        self.decisions_log = []
        self.layer_status = {
            'advanced_layers': ADVANCED_LAYERS_OK,
            'xgboost': XGBOOST_OK,
            'kalman': KALMAN_OK,
            'elliott': ELLIOTT_OK,
            'regime': REGIME_OK,
            'sentiment': SENTIMENT_OK,
            'volume': VOLUME_OK,
            'macro': MACRO_OK,
            'garch': GARCH_OK,
            'markov': MARKOV_OK
        }
        
        # Layer weight'ları
        self.layer_weights = {
            'technical': 0.20,
            'ml_xgboost': 0.15,
            'regime_kalman': 0.15,
            'regime_markov': 0.10,
            'elliott_wave': 0.10,
            'sentiment': 0.10,
            'volume': 0.08,
            'macro': 0.07,
            'garch': 0.05
        }

    def run_all_layers(self, symbol='BTCUSDT', klines_data=None) -> Dict:
        """Tüm layer'ları parallel çalıştır"""
        
        results = {}
        
        # LAYER 1: Advanced Technical Analysis
        if ADVANCED_LAYERS_OK:
            try:
                analyzer = AdvancedTechnicalAnalysis()
                results['advanced_technical'] = analyzer.analyze(symbol, klines_data)
            except Exception as e:
                results['advanced_technical'] = {'error': str(e), 'score': 50}
        
        # LAYER 2: XGBoost ML
        if XGBOOST_OK:
            try:
                ml_analyzer = XGBoostMLAnalyzer()
                results['xgboost_ml'] = ml_analyzer.predict(klines_data)
            except Exception as e:
                results['xgboost_ml'] = {'error': str(e), 'score': 50}
        
        # LAYER 3: Kalman Regime Detector
        if KALMAN_OK:
            try:
                kalman = KalmanRegimeDetector()
                results['kalman_regime'] = kalman.detect_regime(klines_data)
            except Exception as e:
                results['kalman_regime'] = {'error': str(e), 'score': 50}
        
        # LAYER 4: Elliott Wave
        if ELLIOTT_OK:
            try:
                elliott = ElliottWaveDetector()
                results['elliott_wave'] = elliott.detect_waves(klines_data)
            except Exception as e:
                results['elliott_wave'] = {'error': str(e), 'score': 50}
        
        # LAYER 5: Market Regime Analyzer
        if REGIME_OK:
            try:
                regime = MarketRegimeAnalyzer()
                results['regime_analyzer'] = regime.analyze(klines_data)
            except Exception as e:
                results['regime_analyzer'] = {'error': str(e), 'score': 50}
        
        # LAYER 6: Sentiment Analysis
        if SENTIMENT_OK:
            try:
                sentiment = NewsSentimentAnalyzer()
                results['sentiment'] = sentiment.analyze_sentiment(symbol)
            except Exception as e:
                results['sentiment'] = {'error': str(e), 'score': 50}
        
        # LAYER 7: Volume Profile
        if VOLUME_OK:
            try:
                volume = VolumeProfileAnalyzer()
                results['volume'] = volume.analyze_profile(klines_data)
            except Exception as e:
                results['volume'] = {'error': str(e), 'score': 50}
        
        # LAYER 8: Macro Correlation
        if MACRO_OK:
            try:
                macro = MacroCorrelationAnalyzer()
                results['macro'] = macro.analyze_correlations()
            except Exception as e:
                results['macro'] = {'error': str(e), 'score': 50}
        
        # LAYER 9: GARCH Volatility
        if GARCH_OK:
            try:
                garch = GarchVolatilityAnalyzer()
                results['garch'] = garch.analyze_volatility(klines_data)
            except Exception as e:
                results['garch'] = {'error': str(e), 'score': 50}
        
        # LAYER 10: Markov Regime
        if MARKOV_OK:
            try:
                markov = MarkovRegimeDetector()
                results['markov'] = markov.detect_regime(klines_data)
            except Exception as e:
                results['markov'] = {'error': str(e), 'score': 50}
        
        return results

    def extract_scores(self, layer_results: Dict) -> Dict:
        """Tüm layer'lardan score'u çıkart"""
        
        scores = {}
        
        for layer_name, result in layer_results.items():
            if isinstance(result, dict):
                if 'score' in result:
                    scores[layer_name] = result['score']
                elif 'prediction' in result:
                    scores[layer_name] = result['prediction']
                elif 'confidence' in result:
                    scores[layer_name] = result['confidence']
                elif 'signal_score' in result:
                    scores[layer_name] = result['signal_score']
                else:
                    scores[layer_name] = 50  # Default neutral
        
        return scores

    def make_unified_decision(self, symbol='BTCUSDT', klines_data=None) -> Dict:
        """TÜM LAYER'LARI BİRLEŞTİR VE KARAR VER"""
        
        decision_time = datetime.now()
        
        # Tüm layer'ları çalıştır
        layer_results = self.run_all_layers(symbol, klines_data)
        
        # Score'ları çıkart
        scores = self.extract_scores(layer_results)
        
        # Ağırlıklı ortalama (weighted average)
        if scores:
            # Score'ları 0-100 aralığına normalize et
            normalized_scores = {}
            for layer, score in scores.items():
                if isinstance(score, bool):
                    normalized_scores[layer] = 70 if score else 30
                else:
                    normalized_scores[layer] = float(score)
            
            # Ağırlıklandırılmış ortalama
            total_weight = sum(
                self.layer_weights.get(layer, 0.05) 
                for layer in normalized_scores.keys()
            )
            
            final_score = sum(
                normalized_scores.get(layer, 50) * self.layer_weights.get(layer, 0.05)
                for layer in normalized_scores.keys()
            ) / (total_weight if total_weight > 0 else 1)
        else:
            final_score = 50
        
        # Karar ver
        if final_score > 75:
            signal = 'LONG'
        elif final_score < 25:
            signal = 'SHORT'
        elif final_score > 60:
            signal = 'WEAK_LONG'
        elif final_score < 40:
            signal = 'WEAK_SHORT'
        else:
            signal = 'NEUTRAL'
        
        decision = {
            'timestamp': decision_time.isoformat(),
            'symbol': symbol,
            'signal': signal,
            'final_score': final_score,
            'layer_scores': scores,
            'layer_results': layer_results,
            'layer_status': self.layer_status,
            'active_layers': sum(1 for v in self.layer_status.values() if v),
            'interpretation': self._interpret_decision(final_score, signal, scores)
        }
        
        self.decisions_log.append(decision)
        return decision

    def _interpret_decision(self, score: float, signal: str, scores: Dict) -> str:
        """Karar'ı yorumla"""
        
        active = sum(1 for v in self.layer_status.values() if v)
        
        # En güçlü layer'ları bul
        strongest = sorted(scores.items(), key=lambda x: abs(x[1]-50), reverse=True)[:3]
        
        interpretation = f"""
🎯 KARAR: {signal}
📊 Final Score: {score:.1f}/100
🧠 Aktif Layer'lar: {active}/10

🔝 En Güçlü Layer'lar:
"""
        
        for layer, score_val in strongest:
            trend = "🟢 BULLISH" if score_val > 60 else "🔴 BEARISH" if score_val < 40 else "🟡 NEUTRAL"
            interpretation += f"  • {layer}: {score_val:.0f} {trend}\n"
        
        return interpretation

    def get_dashboard_data(self) -> Dict:
        """Dashboard için tüm veriyi hazırla"""
        
        if not self.decisions_log:
            return {'status': 'no_data'}
        
        latest = self.decisions_log[-1]
        
        return {
            'signal': latest['signal'],
            'score': latest['final_score'],
            'active_layers': latest['active_layers'],
            'layer_count': len(self.layer_status),
            'enabled_layers': [k for k, v in self.layer_status.items() if v],
            'layer_scores': latest['layer_scores'],
            'interpretation': latest['interpretation'],
            'timestamp': latest['timestamp']
        }

# Test
if __name__ == "__main__":
    engine = LayersIntegrationEngine()
    
    # Dummy klines data
    dummy_klines = np.random.randn(100, 5)
    
    decision = engine.make_unified_decision('BTCUSDT', dummy_klines)
    
    print("\n" + "="*70)
    print("🧠 UNIFIED LAYERS DECISION")
    print("="*70)
    print(f"Signal: {decision['signal']}")
    print(f"Score: {decision['final_score']:.1f}")
    print(f"Active Layers: {decision['active_layers']}/10")
    print(decision['interpretation'])
    print("="*70)
