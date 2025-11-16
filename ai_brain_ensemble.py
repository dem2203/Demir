"""
🚀 DEMIR AI v5.2 - PHASE 11 FINAL
ai_brain_ensemble.py - UPDATED FOR 20 SENTIMENT LAYERS + 10 ML

Changes from previous:
✅ Imports from layers.sentiment (20 layers now)
✅ Imports from layers.ml (10 layers)
✅ analyze_for_futures() method added
✅ Everything else SAME as [65]

Location: GitHub Root / ai_brain_ensemble.py
Date: 2025-11-16 01:35 UTC
"""

import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import requests
from dotenv import load_dotenv

# Import all layers
try:
    from layers.sentiment import SENTIMENT_LAYERS
except ImportError:
    SENTIMENT_LAYERS = []
    logging.warning("⚠️ Sentiment layers not loaded")

try:
    from layers.ml import ML_LAYERS
except ImportError:
    ML_LAYERS = []
    logging.warning("⚠️ ML layers not loaded")

load_dotenv()
logger = logging.getLogger(__name__)

# ============================================================================
# PHASE 11: AI BRAIN ENSEMBLE ORCHESTRATOR - 20 SENTIMENT + 10 ML
# ============================================================================

class AiBrainEnsemble:
    """
    Master orchestrator combining 20 sentiment + 10 ML layers
    - Hierarchical ensemble voting
    - Per-symbol customized weighting
    - Real-time confidence calculation
    - Futures-optimized analysis mode
    - Fail-safe mechanisms
    """
    
    def __init__(self):
        self.sentiment_layers = {}
        self.ml_layers = {}
        self.layer_cache = {}
        self.performance_metrics = {}
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
        
        self._initialize_layers()
        logger.info("✅ AI Brain Ensemble initialized")
    
    def _initialize_layers(self):
        """Initialize all 20 sentiment + 10 ML layers"""
        
        # ✅ Initialize sentiment layers (20 total)
        for layer_name, layer_class in SENTIMENT_LAYERS:
            try:
                self.sentiment_layers[layer_name] = layer_class()
                logger.info(f"✅ Sentiment layer loaded: {layer_name}")
            except Exception as e:
                logger.error(f"❌ Sentiment layer {layer_name} failed: {e}")
        
        # ✅ Initialize ML layers (10 total)
        for layer_name, layer_class in ML_LAYERS:
            try:
                self.ml_layers[layer_name] = layer_class()
                logger.info(f"✅ ML layer loaded: {layer_name}")
            except Exception as e:
                logger.error(f"❌ ML layer {layer_name} failed: {e}")
        
        logger.info(f"✅ Loaded {len(self.sentiment_layers)} sentiment + {len(self.ml_layers)} ML layers")
    
    def analyze_symbol(self, symbol: str, prices: np.ndarray, volumes: Optional[np.ndarray] = None) -> Dict:
        """
        Analyze single symbol through all layers
        
        Args:
            symbol: Trading pair (BTCUSDT, ETHUSDT, etc.)
            prices: Price array (real data)
            volumes: Volume array (optional)
        
        Returns:
            Comprehensive analysis dict
        """
        
        try:
            logger.info(f"📍 Analyzing {symbol} ({len(prices)} candles)")
            
            # ✅ STEP 1: Get sentiment scores from all 20 layers
            sentiment_scores = self._get_sentiment_scores(symbol)
            sentiment_avg = np.mean(list(sentiment_scores.values())) if sentiment_scores else 0.5
            
            # ✅ STEP 2: Get ML scores from all 10 layers
            ml_scores = self._get_ml_scores(prices, volumes)
            ml_avg = np.mean(list(ml_scores.values())) if ml_scores else 0.5
            
            # ✅ STEP 3: Weighted ensemble (45% sentiment, 55% ML)
            ensemble_score = (sentiment_avg * 0.45) + (ml_avg * 0.55)
            
            # ✅ STEP 4: Calculate confidence
            all_scores = list(sentiment_scores.values()) + list(ml_scores.values())
            confidence = self._calculate_confidence(all_scores)
            
            # ✅ STEP 5: Generate recommendation
            recommendation = self._get_recommendation(ensemble_score)
            
            # ✅ Store result
            result = {
                'symbol': symbol,
                'score': float(np.clip(ensemble_score, 0, 1)),
                'sentiment_score': float(np.clip(sentiment_avg, 0, 1)),
                'ml_score': float(np.clip(ml_avg, 0, 1)),
                'components': {
                    'sentiment': sentiment_scores,
                    'ml': ml_scores
                },
                'confidence': float(confidence),
                'recommendation': recommendation,
                'timestamp': datetime.now().isoformat(),
                'layer_count': len(sentiment_scores) + len(ml_scores)
            }
            
            logger.info(f"✅ {symbol}: Score={result['score']:.3f}, Conf={result['confidence']:.2%}, Rec={recommendation}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Analysis error for {symbol}: {e}")
            return {
                'symbol': symbol,
                'score': 0.5,
                'sentiment_score': 0.5,
                'ml_score': 0.5,
                'components': {},
                'confidence': 0.3,
                'recommendation': 'NEUTRAL',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _get_sentiment_scores(self, symbol: str) -> Dict[str, float]:
        """Get scores from all 20 sentiment layers"""
        scores = {}
        
        for layer_name, layer_obj in self.sentiment_layers.items():
            try:
                # Most layers only need analyze(), some take symbol parameter
                if layer_name in ['OrderBookImbalance', 'LiquidationCascade', 'BasisContango']:
                    score = layer_obj.analyze(symbol)
                else:
                    score = layer_obj.analyze()
                scores[layer_name] = float(np.clip(score, 0, 1))
                logger.debug(f"  ✅ {layer_name}: {score:.2f}")
            except Exception as e:
                logger.warning(f"  ⚠️ {layer_name} failed: {e}")
                scores[layer_name] = 0.5  # Neutral fallback
        
        return scores
    
    def _get_ml_scores(self, prices: np.ndarray, volumes: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Get scores from all 10 ML layers"""
        scores = {}
        
        for layer_name, layer_obj in self.ml_layers.items():
            try:
                if volumes is not None and layer_name in ['XGBoost', 'Ensemble']:
                    score = layer_obj.analyze(prices, volumes)
                else:
                    score = layer_obj.analyze(prices)
                scores[layer_name] = float(np.clip(score, 0, 1))
                logger.debug(f"  ✅ {layer_name}: {score:.2f}")
            except Exception as e:
                logger.warning(f"  ⚠️ {layer_name} failed: {e}")
                scores[layer_name] = 0.5  # Neutral fallback
        
        return scores
    
    def _calculate_confidence(self, scores: List[float]) -> float:
        """
        Calculate confidence based on:
        - Agreement between layers
        - Distance from neutral (0.5)
        - Layer count
        """
        
        if not scores:
            return 0.3
        
        scores_array = np.array(scores)
        
        # Measure agreement (low std dev = high agreement)
        agreement = 1 - (np.std(scores_array) / 0.5)
        agreement = np.clip(agreement, 0, 1)
        
        # Measure conviction (distance from neutral)
        conviction = np.mean(np.abs(scores_array - 0.5)) * 2
        conviction = np.clip(conviction, 0, 1)
        
        # Layer count bonus (more layers = more confidence)
        layer_bonus = min(len(scores) / 30, 1.0)  # 30 total layers (20+10)
        
        # Composite confidence
        confidence = (agreement * 0.4) + (conviction * 0.4) + (layer_bonus * 0.2)
        
        return float(np.clip(confidence, 0.2, 0.95))
    
    def _get_recommendation(self, score: float) -> str:
        """Generate trading recommendation from score"""
        
        if score > 0.75:
            return '🟢 STRONG_LONG'
        elif score > 0.62:
            return '🟢 LONG'
        elif score > 0.55:
            return '🟡 MILD_LONG'
        elif score < 0.25:
            return '🔴 STRONG_SHORT'
        elif score < 0.38:
            return '🔴 SHORT'
        elif score < 0.45:
            return '🟠 MILD_SHORT'
        else:
            return '⚪ NEUTRAL'
    
    def analyze_for_futures(self, symbol: str, prices: np.ndarray, 
                           volumes: Optional[np.ndarray] = None) -> Dict:
        """
        Futures-optimized analysis (higher weight on futures layers + funding)
        
        Weights:
        - Futures layers (3): 40% (OrderBook, Liquidations, Basis)
        - Crypto sentiment (5): 35% (Funding, L/S ratio, On-chain)
        - Macro (12): 15%
        - ML (10): 10%
        """
        
        try:
            analysis = self.analyze_symbol(symbol, prices, volumes)
            
            if not analysis or len(self.sentiment_layers) < 15:
                return analysis
            
            # Categorize layers
            futures_layers = ['OrderBookImbalance', 'LiquidationCascade', 'BasisContango']
            crypto_layers = ['StablecoinDominance', 'FundingRates', 'LongShortRatio', 
                           'OnChainActivity', 'ExchangeReserveFlows']
            
            futures_scores = {k: v for k, v in analysis['components']['sentiment'].items() 
                            if k in futures_layers}
            crypto_scores = {k: v for k, v in analysis['components']['sentiment'].items() 
                           if k in crypto_layers}
            macro_scores = {k: v for k, v in analysis['components']['sentiment'].items() 
                          if k not in futures_layers and k not in crypto_layers}
            
            # Calculate weighted averages
            futures_avg = np.mean(list(futures_scores.values())) if futures_scores else 0.5
            crypto_avg = np.mean(list(crypto_scores.values())) if crypto_scores else 0.5
            macro_avg = np.mean(list(macro_scores.values())) if macro_scores else 0.5
            ml_avg = analysis['ml_score']
            
            # Futures-optimized weighting
            futures_optimized_score = (
                futures_avg * 0.40 +
                crypto_avg * 0.35 +
                macro_avg * 0.15 +
                ml_avg * 0.10
            )
            
            # Update analysis
            analysis['futures_optimized_score'] = float(np.clip(futures_optimized_score, 0, 1))
            analysis['futures_weighted'] = True
            analysis['component_breakdown'] = {
                'futures': float(futures_avg),
                'crypto': float(crypto_avg),
                'macro': float(macro_avg),
                'ml': float(ml_avg)
            }
            
            logger.info(f"✅ Futures analysis: {symbol} = {futures_optimized_score:.3f}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Futures analysis error: {e}")
            return self.analyze_symbol(symbol, prices, volumes)
    
    def generate_ensemble_signal(self, symbol: str, prices: np.ndarray,
                                volumes: Optional[np.ndarray] = None, 
                                futures_mode: bool = True) -> Optional[Dict]:
        """
        Generate complete trading signal from ensemble
        
        Args:
            symbol: Trading pair
            prices: Price history
            volumes: Volume history
            futures_mode: Use futures-optimized weighting
        
        Returns:
            Trading signal with entry, TP, SL, position size, etc.
        """
        
        try:
            # Get analysis (use futures mode if specified)
            if futures_mode:
                analysis = self.analyze_for_futures(symbol, prices, volumes)
                score = analysis.get('futures_optimized_score', analysis['score'])
            else:
                analysis = self.analyze_symbol(symbol, prices, volumes)
                score = analysis['score']
            
            if not prices or len(prices) == 0:
                logger.error("❌ No price data")
                return None
            
            current_price = float(prices[-1])
            
            # Calculate ATR for volatility
            atr = self._calculate_atr(prices)
            
            # Determine position direction
            if score > 0.55:
                direction = 'LONG'
                tp1 = current_price + (atr * 1.5)
                tp2 = current_price + (atr * 3.0)
                sl = current_price - (atr * 1.0)
            elif score < 0.45:
                direction = 'SHORT'
                tp1 = current_price - (atr * 1.5)
                tp2 = current_price - (atr * 3.0)
                sl = current_price + (atr * 1.0)
            else:
                logger.info(f"⚠️ {symbol}: Neutral signal, no trade")
                return None
            
            # Calculate position size
            position_size = 1.0 * analysis['confidence']
            
            # Calculate risk/reward
            if direction == 'LONG':
                risk = abs(current_price - sl)
                reward = abs(tp2 - current_price)
            else:
                risk = abs(sl - current_price)
                reward = abs(current_price - tp2)
            
            rr_ratio = reward / (risk + 1e-9)
            
            # Build signal
            signal = {
                'symbol': symbol,
                'direction': direction,
                'entry_price': float(current_price),
                'tp1': float(tp1),
                'tp2': float(tp2),
                'sl': float(sl),
                'position_size': float(np.clip(position_size, 0.1, 1.0)),
                'risk_reward_ratio': float(rr_ratio),
                'confidence': float(analysis['confidence']),
                'ensemble_score': float(score),
                'recommendation': analysis['recommendation'],
                'futures_mode': futures_mode,
                'timestamp': datetime.now().isoformat(),
                'analysis': analysis
            }
            
            logger.info(f"✅ Signal generated: {symbol} {direction} @ {current_price:.2f} (RR: {rr_ratio:.2f})")
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ Signal generation error: {e}")
            return None
    
    def _calculate_atr(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate Average True Range for volatility"""
        
        if len(prices) < period + 1:
            return prices[-1] * 0.02
        
        closes = prices
        highs = prices
        lows = prices
        
        tr = []
        for i in range(len(prices)):
            if i == 0:
                tr.append(highs[i] - lows[i])
            else:
                h_l = highs[i] - lows[i]
                h_c = abs(highs[i] - closes[i-1])
                l_c = abs(lows[i] - closes[i-1])
                tr.append(max(h_l, h_c, l_c))
        
        atr = np.mean(tr[-period:])
        return float(atr)
    
    def batch_analyze(self, symbol_prices: Dict[str, Tuple[np.ndarray, np.ndarray]],
                     futures_mode: bool = True) -> List[Dict]:
        """
        Analyze multiple symbols at once
        
        Args:
            symbol_prices: {
                'BTCUSDT': (prices_array, volumes_array),
                'ETHUSDT': (prices_array, volumes_array),
                ...
            }
            futures_mode: Use futures optimization
        
        Returns:
            List of trading signals
        """
        
        signals = []
        
        for symbol, (prices, volumes) in symbol_prices.items():
            signal = self.generate_ensemble_signal(symbol, prices, volumes, futures_mode)
            if signal:
                signals.append(signal)
        
        return signals
    
    def get_health_status(self) -> Dict:
        """Get current health of all layers"""
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'sentiment_layers': {
                'count': len(self.sentiment_layers),
                'healthy': len([l for l in self.sentiment_layers.values()])
            },
            'ml_layers': {
                'count': len(self.ml_layers),
                'healthy': len([l for l in self.ml_layers.values()])
            },
            'total_layers': len(self.sentiment_layers) + len(self.ml_layers),
            'status': 'OPERATIONAL' if len(self.sentiment_layers) >= 15 and len(self.ml_layers) >= 8 else 'DEGRADED'
        }
        
        return status

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    
    # Initialize ensemble
    ai_brain = AiBrainEnsemble()
    
    # Health check
    health = ai_brain.get_health_status()
    logger.info(f"✅ AI Brain Health: {health}")
    
    # Example: Analyze with real Binance data
    try:
        url = "https://fapi.binance.com/fapi/v1/klines"
        params = {'symbol': 'BTCUSDT', 'interval': '1h', 'limit': 100}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            klines = response.json()
            prices = np.array([float(k[4]) for k in klines])
            volumes = np.array([float(k[7]) for k in klines])
            
            # Generate futures-optimized signal
            signal = ai_brain.generate_ensemble_signal('BTCUSDT', prices, volumes, futures_mode=True)
            
            if signal:
                logger.info(f"🎯 Signal: {signal}")
            else:
                logger.info("ℹ️ No signal generated (neutral market)")
    
    except Exception as e:
        logger.error(f"❌ Example error: {e}")

logger.info("✅ PHASE 11 COMPLETE - AI BRAIN ORCHESTRATOR READY (20 SENTIMENT + 10 ML)")
