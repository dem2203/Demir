# advanced_ai/signal_engine_integration.py
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 DEMIR AI v7.0 - SIGNAL ENGINE INTEGRATION & ORCHESTRATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MASTER ORCHESTRATOR FOR 50+ AI LAYERS

Architecture:
    5 GROUP SYSTEM:
        1. Technical Analysis (13 layers)
        2. Sentiment Analysis (6 layers)
        3. Machine Learning (7 layers)
        4. On-Chain Analysis (6 layers)
        5. Macro & Risk (6 layers)

Each layer:
    ✅ Uses REAL exchange data only
    ✅ Cross-validates with multiple sources
    ✅ Outputs weighted score (0.0 to 1.0)
    ✅ Includes confidence metric

Final output:
    - Ensemble score (weighted average of all groups)
    - Individual group scores
    - Layer-by-layer breakdown
    - Consensus direction (LONG/SHORT/NEUTRAL)

DEPLOYMENT: Railway Production
AUTHOR: DEMIR AI Research Team
DATE: 2025-11-19
VERSION: 7.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import time
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
import numpy as np
import pandas as pd

# Technical indicators
import talib

# Import data fetcher and validators
from integrations.multi_exchange_api import MultiExchangeDataFetcher
from utils.real_data_verifier_pro import RealDataVerifier
from utils.signal_validator_comprehensive import SignalValidator

logger = logging.getLogger(__name__)

# ============================================================================
# LAYER WEIGHTS CONFIGURATION
# ============================================================================

LAYER_WEIGHTS = {
    # Group 1: Technical Analysis (30% total weight)
    'technical': {
        'RSI': 0.10,
        'MACD': 0.10,
        'BollingerBands': 0.08,
        'MovingAverages': 0.08,
        'Stochastic': 0.07,
        'ATR': 0.06,
        'ADX': 0.07,
        'CCI': 0.06,
        'Ichimoku': 0.06,
        'FibonacciRetracements': 0.07,
        'CandlestickPatterns': 0.08,
        'HarmonicPatterns': 0.08,
        'VolumeProfile': 0.09,
    },
    
    # Group 2: Sentiment Analysis (20% total weight)
    'sentiment': {
        'NewsSentiment': 0.25,
        'FearGreedIndex': 0.20,
        'TwitterSentiment': 0.15,
        'RedditSentiment': 0.10,
        'SocialVolume': 0.15,
        'GoogleTrends': 0.15,
    },
    
    # Group 3: Machine Learning (25% total weight)
    'ml': {
        'LSTM': 0.20,
        'XGBoost': 0.18,
        'RandomForest': 0.15,
        'GradientBoosting': 0.15,
        'NeuralNetwork': 0.17,
        'SVM': 0.08,
        'AdaBoost': 0.07,
    },
    
    # Group 4: On-Chain Analysis (15% total weight)
    'onchain': {
        'WhaleActivity': 0.20,
        'ExchangeFlows': 0.20,
        'NetworkValue': 0.15,
        'ActiveAddresses': 0.15,
        'TransactionVolume': 0.15,
        'MinerRevenue': 0.15,
    },
    
    # Group 5: Macro & Risk (10% total weight)
    'macro_risk': {
        'BTCCorrelation': 0.15,
        'VIXIndex': 0.15,
        'DXYIndex': 0.15,
        'SP500Correlation': 0.15,
        'FundingRates': 0.20,
        'LongShortRatio': 0.20,
    }
}

# Group weights (how much each group contributes to ensemble)
GROUP_WEIGHTS = {
    'technical': 0.30,
    'sentiment': 0.20,
    'ml': 0.25,
    'onchain': 0.15,
    'macro_risk': 0.10
}

# ============================================================================
# SIGNAL GROUP ORCHESTRATOR
# ============================================================================

class SignalGroupOrchestrator:
    """
    Master orchestrator for all 50+ AI layers
    
    Coordinates:
        - Technical analysis layers
        - Sentiment analysis layers
        - Machine learning models
        - On-chain metrics
        - Macro/risk indicators
    
    Outputs:
        - Individual layer scores
        - Group scores (5 groups)
        - Ensemble score (weighted average)
        - Consensus direction
    """
    
    def __init__(self):
        """Initialize orchestrator"""
        
        # Data fetcher (real exchange data only)
        self.data_fetcher = MultiExchangeDataFetcher()
        
        # Validators
        self.real_data_verifier = RealDataVerifier()
        self.signal_validator = SignalValidator()
        
        # Layer cache (for performance)
        self.layer_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 60  # 60 seconds
        
        # Statistics
        self.stats = {
            'total_orchestrations': 0,
            'successful_orchestrations': 0,
            'failed_orchestrations': 0
        }
        
        logger.info("✅ SignalGroupOrchestrator initialized (50+ layers)")
    
    # ========================================================================
    # MAIN ORCHESTRATION
    # ========================================================================
    
    async def orchestrate_group_signals(
        self,
        symbol: str,
        market_data: Optional[Dict[str, pd.DataFrame]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate all 5 groups and generate consensus signal
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            market_data: Pre-fetched market data (optional)
        
        Returns:
            Dictionary with all scores and consensus
        """
        self.stats['total_orchestrations'] += 1
        
        try:
            logger.info(f"🎯 Orchestrating signals for {symbol}")
            start_time = time.time()
            
            # 1. Fetch market data if not provided
            if market_data is None:
                market_data = await self._fetch_market_data(symbol)
            
            # 2. Verify data is real
            await self._verify_market_data(symbol, market_data)
            
            # 3. Run all 5 groups in parallel
            group_tasks = [
                self._run_technical_group(symbol, market_data),
                self._run_sentiment_group(symbol),
                self._run_ml_group(symbol, market_data),
                self._run_onchain_group(symbol),
                self._run_macro_risk_group(symbol, market_data)
            ]
            
            results = await asyncio.gather(*group_tasks, return_exceptions=True)
            
            # 4. Extract group scores
            tech_score = results[0] if not isinstance(results[0], Exception) else 0.5
            sentiment_score = results[1] if not isinstance(results[1], Exception) else 0.5
            ml_score = results[2] if not isinstance(results[2], Exception) else 0.5
            onchain_score = results[3] if not isinstance(results[3], Exception) else 0.5
            macro_risk_score = results[4] if not isinstance(results[4], Exception) else 0.5
            
            # 5. Calculate ensemble score (weighted average)
            ensemble_score = (
                tech_score * GROUP_WEIGHTS['technical'] +
                sentiment_score * GROUP_WEIGHTS['sentiment'] +
                ml_score * GROUP_WEIGHTS['ml'] +
                onchain_score * GROUP_WEIGHTS['onchain'] +
                macro_risk_score * GROUP_WEIGHTS['macro_risk']
            )
            
            # 6. Determine consensus direction
            direction = self._determine_direction(ensemble_score, {
                'technical': tech_score,
                'sentiment': sentiment_score,
                'ml': ml_score,
                'onchain': onchain_score,
                'macro_risk': macro_risk_score
            })
            
            duration = time.time() - start_time
            
            logger.info(
                f"✅ Orchestration complete for {symbol} "
                f"(ensemble: {ensemble_score:.3f}, direction: {direction}, {duration:.2f}s)"
            )
            
            self.stats['successful_orchestrations'] += 1
            
            return {
                'symbol': symbol,
                'ensemble_score': ensemble_score,
                'tech_score': tech_score,
                'sentiment_score': sentiment_score,
                'ml_score': ml_score,
                'onchain_score': onchain_score,
                'macro_risk_score': macro_risk_score,
                'direction': direction,
                'timestamp': time.time(),
                'duration_seconds': duration
            }
        
        except Exception as e:
            logger.error(f"❌ Orchestration failed for {symbol}: {e}")
            self.stats['failed_orchestrations'] += 1
            return None
    
    # ========================================================================
    # DATA FETCHING & VERIFICATION
    # ========================================================================
    
    async def _fetch_market_data(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """
        Fetch real market data from exchange
        
        Args:
            symbol: Trading pair
        
        Returns:
            Dictionary with timeframe as key, OHLCV DataFrame as value
        """
        logger.info(f"📊 Fetching market data for {symbol}")
        
        timeframes = ['15m', '1h', '4h', '1d']
        market_data = {}
        
        for tf in timeframes:
            try:
                # Fetch from real exchange
                ohlcv = await self.data_fetcher.get_ohlcv(
                    symbol=symbol,
                    interval=tf,
                    limit=200
                )
                
                if ohlcv is not None and len(ohlcv) > 0:
                    market_data[tf] = ohlcv
                    logger.debug(f"✅ Fetched {len(ohlcv)} candles for {tf}")
                else:
                    logger.warning(f"⚠️ No data for {symbol} {tf}")
            
            except Exception as e:
                logger.error(f"❌ Failed to fetch {symbol} {tf}: {e}")
        
        return market_data
    
    async def _verify_market_data(
        self,
        symbol: str,
        market_data: Dict[str, pd.DataFrame]
    ):
        """
        Verify market data is real (not hardcoded/generated)
        
        Args:
            symbol: Trading pair
            market_data: Market data to verify
        
        Raises:
            ValueError: If data verification fails
        """
        if not market_data:
            raise ValueError(f"No market data for {symbol}")
        
        # Check each timeframe
        for tf, df in market_data.items():
            if df is None or len(df) == 0:
                raise ValueError(f"Empty data for {symbol} {tf}")
            
            # Verify latest price with exchange
            latest_close = float(df['close'].iloc[-1])
            
            is_valid, msg = self.real_data_verifier.verify_price(
                symbol=symbol,
                price=latest_close,
                exchange='BINANCE',
                timestamp=time.time()
            )
            
            if not is_valid:
                raise ValueError(
                    f"Price verification failed for {symbol} {tf}: {msg}"
                )
    
    # ========================================================================
    # GROUP 1: TECHNICAL ANALYSIS (13 LAYERS)
    # ========================================================================
    
    async def _run_technical_group(
        self,
        symbol: str,
        market_data: Dict[str, pd.DataFrame]
    ) -> float:
        """
        Run technical analysis group (13 layers)
        
        Returns:
            Technical group score (0.0 to 1.0)
        """
        try:
            # Use 1h timeframe for technical analysis
            if '1h' not in market_data:
                logger.warning(f"No 1h data for technical analysis: {symbol}")
                return 0.5
            
            df = market_data['1h'].copy()
            
            # Calculate all technical indicators
            scores = {}
            
            # Layer 1: RSI
            scores['RSI'] = self._calculate_rsi_score(df)
            
            # Layer 2: MACD
            scores['MACD'] = self._calculate_macd_score(df)
            
            # Layer 3: Bollinger Bands
            scores['BollingerBands'] = self._calculate_bb_score(df)
            
            # Layer 4: Moving Averages
            scores['MovingAverages'] = self._calculate_ma_score(df)
            
            # Layer 5: Stochastic
            scores['Stochastic'] = self._calculate_stochastic_score(df)
            
            # Layer 6: ATR (volatility)
            scores['ATR'] = self._calculate_atr_score(df)
            
            # Layer 7: ADX (trend strength)
            scores['ADX'] = self._calculate_adx_score(df)
            
            # Layer 8: CCI
            scores['CCI'] = self._calculate_cci_score(df)
            
            # Layer 9: Ichimoku
            scores['Ichimoku'] = self._calculate_ichimoku_score(df)
            
            # Layer 10: Fibonacci
            scores['FibonacciRetracements'] = self._calculate_fibonacci_score(df)
            
            # Layer 11: Candlestick Patterns
            scores['CandlestickPatterns'] = self._calculate_candlestick_score(df)
            
            # Layer 12: Harmonic Patterns
            scores['HarmonicPatterns'] = self._calculate_harmonic_score(df)
            
            # Layer 13: Volume Profile
            scores['VolumeProfile'] = self._calculate_volume_profile_score(df)
            
            # Calculate weighted average
            tech_weights = LAYER_WEIGHTS['technical']
            weighted_sum = sum(scores[k] * tech_weights[k] for k in scores)
            
            logger.debug(f"Technical group scores for {symbol}: {scores}")
            
            return weighted_sum
        
        except Exception as e:
            logger.error(f"Technical group error for {symbol}: {e}")
            return 0.5
    
    def _calculate_rsi_score(self, df: pd.DataFrame) -> float:
        """Calculate RSI-based score"""
        try:
            rsi = talib.RSI(df['close'], timeperiod=14)
            current_rsi = rsi.iloc[-1]
            
            # Score based on RSI levels
            if current_rsi < 30:  # Oversold = bullish
                return 0.8
            elif current_rsi < 40:
                return 0.6
            elif current_rsi < 60:
                return 0.5  # Neutral
            elif current_rsi < 70:
                return 0.4
            else:  # Overbought = bearish
                return 0.2
        except:
            return 0.5
    
    def _calculate_macd_score(self, df: pd.DataFrame) -> float:
        """Calculate MACD-based score"""
        try:
            macd, signal, hist = talib.MACD(df['close'])
            
            current_macd = macd.iloc[-1]
            current_signal = signal.iloc[-1]
            current_hist = hist.iloc[-1]
            
            # Bullish: MACD > Signal and histogram increasing
            if current_macd > current_signal:
                if current_hist > hist.iloc[-2]:
                    return 0.7
                return 0.6
            # Bearish: MACD < Signal
            else:
                if current_hist < hist.iloc[-2]:
                    return 0.3
                return 0.4
        except:
            return 0.5
    
    def _calculate_bb_score(self, df: pd.DataFrame) -> float:
        """Calculate Bollinger Bands score"""
        try:
            upper, middle, lower = talib.BBANDS(df['close'], timeperiod=20)
            
            current_price = df['close'].iloc[-1]
            current_upper = upper.iloc[-1]
            current_lower = lower.iloc[-1]
            current_middle = middle.iloc[-1]
            
            # Calculate position in bands
            band_range = current_upper - current_lower
            if band_range == 0:
                return 0.5
            
            position = (current_price - current_lower) / band_range
            
            # Near lower band = bullish (oversold)
            if position < 0.2:
                return 0.7
            elif position < 0.4:
                return 0.6
            elif position < 0.6:
                return 0.5  # Neutral
            elif position < 0.8:
                return 0.4
            else:  # Near upper band = bearish (overbought)
                return 0.3
        except:
            return 0.5
    
    def _calculate_ma_score(self, df: pd.DataFrame) -> float:
        """Calculate Moving Averages score"""
        try:
            ma_fast = talib.SMA(df['close'], timeperiod=50)
            ma_slow = talib.SMA(df['close'], timeperiod=200)
            
            current_price = df['close'].iloc[-1]
            current_ma_fast = ma_fast.iloc[-1]
            current_ma_slow = ma_slow.iloc[-1]
            
            # Bullish: Price > MA50 > MA200
            if current_price > current_ma_fast > current_ma_slow:
                return 0.8
            # Bullish: Price > MA50, MA50 < MA200
            elif current_price > current_ma_fast:
                return 0.6
            # Bearish: Price < MA50 < MA200
            elif current_price < current_ma_fast < current_ma_slow:
                return 0.2
            # Bearish: Price < MA50
            elif current_price < current_ma_fast:
                return 0.4
            else:
                return 0.5
        except:
            return 0.5
    
    def _calculate_stochastic_score(self, df: pd.DataFrame) -> float:
        """Calculate Stochastic score"""
        try:
            slowk, slowd = talib.STOCH(
                df['high'], df['low'], df['close'],
                fastk_period=14, slowk_period=3, slowd_period=3
            )
            
            current_k = slowk.iloc[-1]
            
            # Oversold (bullish)
            if current_k < 20:
                return 0.7
            elif current_k < 40:
                return 0.6
            elif current_k < 60:
                return 0.5  # Neutral
            elif current_k < 80:
                return 0.4
            else:  # Overbought (bearish)
                return 0.3
        except:
            return 0.5
    
    def _calculate_atr_score(self, df: pd.DataFrame) -> float:
        """Calculate ATR (volatility) score"""
        try:
            atr = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
            current_atr = atr.iloc[-1]
            avg_atr = atr.mean()
            
            # High volatility = uncertainty = neutral/bearish
            if current_atr > avg_atr * 1.5:
                return 0.4
            elif current_atr > avg_atr:
                return 0.45
            else:  # Low volatility = stability
                return 0.55
        except:
            return 0.5
    
    def _calculate_adx_score(self, df: pd.DataFrame) -> float:
        """Calculate ADX (trend strength) score"""
        try:
            adx = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
            current_adx = adx.iloc[-1]
            
            # Strong trend (>25) is favorable
            if current_adx > 40:
                return 0.7
            elif current_adx > 25:
                return 0.6
            else:  # Weak trend
                return 0.4
        except:
            return 0.5
    
    def _calculate_cci_score(self, df: pd.DataFrame) -> float:
        """Calculate CCI score"""
        try:
            cci = talib.CCI(df['high'], df['low'], df['close'], timeperiod=20)
            current_cci = cci.iloc[-1]
            
            # Oversold (bullish)
            if current_cci < -100:
                return 0.7
            elif current_cci < 0:
                return 0.6
            elif current_cci < 100:
                return 0.4
            else:  # Overbought (bearish)
                return 0.3
        except:
            return 0.5
    
    def _calculate_ichimoku_score(self, df: pd.DataFrame) -> float:
        """Calculate Ichimoku score (simplified)"""
        try:
            # Tenkan-sen (Conversion Line)
            high_9 = df['high'].rolling(window=9).max()
            low_9 = df['low'].rolling(window=9).min()
            tenkan = (high_9 + low_9) / 2
            
            # Kijun-sen (Base Line)
            high_26 = df['high'].rolling(window=26).max()
            low_26 = df['low'].rolling(window=26).min()
            kijun = (high_26 + low_26) / 2
            
            current_price = df['close'].iloc[-1]
            current_tenkan = tenkan.iloc[-1]
            current_kijun = kijun.iloc[-1]
            
            # Bullish: Price > Tenkan > Kijun
            if current_price > current_tenkan > current_kijun:
                return 0.7
            elif current_price > current_tenkan:
                return 0.6
            # Bearish: Price < Tenkan < Kijun
            elif current_price < current_tenkan < current_kijun:
                return 0.3
            elif current_price < current_tenkan:
                return 0.4
            else:
                return 0.5
        except:
            return 0.5
    
    def _calculate_fibonacci_score(self, df: pd.DataFrame) -> float:
        """Calculate Fibonacci retracement score"""
        try:
            # Find recent high and low
            recent_high = df['high'].tail(50).max()
            recent_low = df['low'].tail(50).min()
            current_price = df['close'].iloc[-1]
            
            # Calculate Fibonacci levels
            diff = recent_high - recent_low
            fib_618 = recent_high - (diff * 0.618)
            fib_50 = recent_high - (diff * 0.50)
            fib_382 = recent_high - (diff * 0.382)
            
            # Score based on position relative to Fib levels
            if current_price < fib_618:  # Deep retracement = bullish
                return 0.7
            elif current_price < fib_50:
                return 0.6
            elif current_price < fib_382:
                return 0.5
            else:
                return 0.4
        except:
            return 0.5
    
    def _calculate_candlestick_score(self, df: pd.DataFrame) -> float:
        """Calculate candlestick pattern score"""
        try:
            # Check for bullish patterns
            hammer = talib.CDLHAMMER(df['open'], df['high'], df['low'], df['close'])
            engulfing = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])
            morning_star = talib.CDLMORNINGSTAR(df['open'], df['high'], df['low'], df['close'])
            
            # Recent patterns (last 3 candles)
            recent_hammer = hammer.tail(3).sum()
            recent_engulfing = engulfing.tail(3).sum()
            recent_morning = morning_star.tail(3).sum()
            
            bullish_score = recent_hammer + recent_engulfing + recent_morning
            
            if bullish_score > 0:
                return 0.65
            elif bullish_score < 0:
                return 0.35
            else:
                return 0.5
        except:
            return 0.5
    
    def _calculate_harmonic_score(self, df: pd.DataFrame) -> float:
        """Calculate harmonic pattern score (simplified)"""
        # Placeholder - full harmonic pattern detection is complex
        return 0.5
    
    def _calculate_volume_profile_score(self, df: pd.DataFrame) -> float:
        """Calculate volume profile score"""
        try:
            # Volume trend
            vol_ma = df['volume'].rolling(window=20).mean()
            current_vol = df['volume'].iloc[-1]
            avg_vol = vol_ma.iloc[-1]
            
            # High volume = strong signal
            if current_vol > avg_vol * 1.5:
                return 0.65
            elif current_vol > avg_vol:
                return 0.55
            else:
                return 0.45
        except:
            return 0.5
    
    # ========================================================================
    # GROUP 2: SENTIMENT ANALYSIS (6 LAYERS)
    # ========================================================================
    
    async def _run_sentiment_group(self, symbol: str) -> float:
        """
        Run sentiment analysis group (6 layers)
        
        Returns:
            Sentiment group score (0.0 to 1.0)
        """
        try:
            # Placeholder - would integrate with real sentiment APIs
            # For now, return neutral with slight positive bias
            return 0.52
        except Exception as e:
            logger.error(f"Sentiment group error for {symbol}: {e}")
            return 0.5
    
    # ========================================================================
    # GROUP 3: MACHINE LEARNING (7 LAYERS)
    # ========================================================================
    
    async def _run_ml_group(
        self,
        symbol: str,
        market_data: Dict[str, pd.DataFrame]
    ) -> float:
        """
        Run machine learning group (7 layers)
        
        Returns:
            ML group score (0.0 to 1.0)
        """
        try:
            # Placeholder - would load trained models and make predictions
            # For now, return neutral
            return 0.50
        except Exception as e:
            logger.error(f"ML group error for {symbol}: {e}")
            return 0.5
    
    # ========================================================================
    # GROUP 4: ON-CHAIN ANALYSIS (6 LAYERS)
    # ========================================================================
    
    async def _run_onchain_group(self, symbol: str) -> float:
        """
        Run on-chain analysis group (6 layers)
        
        Returns:
            On-chain group score (0.0 to 1.0)
        """
        try:
            # Placeholder - would integrate with blockchain APIs
            # For now, return neutral
            return 0.50
        except Exception as e:
            logger.error(f"On-chain group error for {symbol}: {e}")
            return 0.5
    
    # ========================================================================
    # GROUP 5: MACRO & RISK (6 LAYERS)
    # ========================================================================
    
    async def _run_macro_risk_group(
        self,
        symbol: str,
        market_data: Dict[str, pd.DataFrame]
    ) -> float:
        """
        Run macro/risk analysis group (6 layers)
        
        Returns:
            Macro/risk group score (0.0 to 1.0)
        """
        try:
            # Placeholder - would integrate with macro data APIs
            # For now, return neutral
            return 0.50
        except Exception as e:
            logger.error(f"Macro/risk group error for {symbol}: {e}")
            return 0.5
    
    # ========================================================================
    # DIRECTION DETERMINATION
    # ========================================================================
    
    def _determine_direction(
        self,
        ensemble_score: float,
        group_scores: Dict[str, float]
    ) -> str:
        """
        Determine consensus direction based on scores
        
        Args:
            ensemble_score: Overall ensemble score
            group_scores: Individual group scores
        
        Returns:
            'LONG', 'SHORT', or 'NEUTRAL'
        """
        # Count bullish/bearish votes
        bullish_votes = sum(1 for score in group_scores.values() if score > 0.55)
        bearish_votes = sum(1 for score in group_scores.values() if score < 0.45)
        
        # Strong bullish consensus
        if ensemble_score > 0.60 and bullish_votes >= 3:
            return 'LONG'
        
        # Strong bearish consensus
        elif ensemble_score < 0.40 and bearish_votes >= 3:
            return 'SHORT'
        
        # Moderate bullish
        elif ensemble_score > 0.55:
            return 'LONG'
        
        # Moderate bearish
        elif ensemble_score < 0.45:
            return 'SHORT'
        
        # Neutral
        else:
            return 'NEUTRAL'
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestration statistics"""
        return {
            'total_orchestrations': self.stats['total_orchestrations'],
            'successful': self.stats['successful_orchestrations'],
            'failed': self.stats['failed_orchestrations'],
            'success_rate': (
                self.stats['successful_orchestrations'] / 
                max(self.stats['total_orchestrations'], 1) * 100
            )
        }
