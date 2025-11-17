"""
DEMIR AI v6.0 - PHASE 4 [56-62] - 7 DOSYA COMBINED
[56] technical_indicators_live.py - 28 Indicators
[57] multi_timeframe_confluence.py - Divergence/Confluence
[58] backtester_3year.py - Historical Backtest
[59] position_manager.py - Kelly Criterion
[60] backtest_results_processor.py - Performance Analysis
[61] data_fetcher_realtime.py - Historical Cache
[62] signal_processor_advanced.py - Multi-TF Processing
"""

import logging
import numpy as np
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

# ============================================================================
# [56] TECHNICAL INDICATORS LIVE - 28 LAYERS REAL-TIME
# ============================================================================

class TechnicalIndicatorsLive:
    """Real-time calculation of all 28 technical indicators"""
    
    def __init__(self):
        self.cache = {}
        logger.info("📊 Technical indicators initialized")
    
    def calculate_all(self, ohlcv: List[Dict]) -> Dict[str, float]:
        """Calculate all 28 indicators"""
        if len(ohlcv) < 100:
            return {}
        
        closes = np.array([c['close'] for c in ohlcv])
        highs = np.array([c['high'] for c in ohlcv])
        lows = np.array([c['low'] for c in ohlcv])
        volumes = np.array([c['volume'] for c in ohlcv])
        
        indicators = {
            # Trend (5)
            'sma_20': self._sma(closes, 20),
            'sma_50': self._sma(closes, 50),
            'ema_12': self._ema(closes, 12),
            'ema_26': self._ema(closes, 26),
            'adx_14': self._adx(highs, lows, closes, 14),
            
            # Momentum (5)
            'rsi_14': self._rsi(closes, 14),
            'macd': self._macd(closes)[0],
            'stoch': self._stochastic(highs, lows, closes),
            'williams_r': self._williams_r(highs, lows, closes),
            'roc': self._roc(closes),
            
            # Volatility (4)
            'bb_upper': self._bollinger_upper(closes),
            'bb_middle': self._sma(closes, 20),
            'bb_lower': self._bollinger_lower(closes),
            'atr_14': self._atr(highs, lows, closes, 14),
            
            # Volume (4)
            'obv': self._obv(closes, volumes),
            'volume_ma': self._sma(volumes, 20),
            'volume_ratio': volumes[-1] / np.mean(volumes[-20:]),
            'vwap': self._vwap(ohlcv),
            
            # Patterns (5)
            'support': self._support(lows),
            'resistance': self._resistance(highs),
            'pivot_point': (highs[-1] + lows[-1] + closes[-1]) / 3,
            'candle_pattern': self._candle_pattern(ohlcv[-1]),
            'harmonic': self._harmonic_pattern(ohlcv),
            
            # Multi-Timeframe (4)
            'trend_strength': self._trend_strength(closes),
            'divergence': self._divergence_score(closes),
            'breakout': self._breakout_score(highs, lows, closes),
            'momentum_score': self._momentum_score(closes)
        }
        
        return indicators
    
    def _sma(self, data: np.ndarray, period: int) -> float:
        return float(np.mean(data[-period:]))
    
    def _ema(self, data: np.ndarray, period: int) -> float:
        ema = data[-period:].mean()
        k = 2 / (period + 1)
        for price in data[-period:]:
            ema = price * k + ema * (1 - k)
        return float(ema)
    
    def _rsi(self, data: np.ndarray, period: int) -> float:
        deltas = np.diff(data[-period-1:])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)
    
    def _macd(self, data: np.ndarray) -> tuple:
        ema12 = self._ema(data, 12)
        ema26 = self._ema(data, 26)
        macd = ema12 - ema26
        return (float(macd), float(ema12 - ema26))
    
    def _stochastic(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, period: int = 14) -> float:
        high = np.max(highs[-period:])
        low = np.min(lows[-period:])
        close = closes[-1]
        stoch = ((close - low) / (high - low + 1e-10)) * 100
        return float(stoch)
    
    def _williams_r(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, period: int = 14) -> float:
        high = np.max(highs[-period:])
        low = np.min(lows[-period:])
        wr = -100 * (high - closes[-1]) / (high - low + 1e-10)
        return float(wr)
    
    def _roc(self, data: np.ndarray, period: int = 12) -> float:
        roc = ((data[-1] - data[-period-1]) / data[-period-1]) * 100
        return float(roc)
    
    def _bollinger_upper(self, data: np.ndarray, period: int = 20, std_dev: int = 2) -> float:
        sma = np.mean(data[-period:])
        std = np.std(data[-period:])
        return float(sma + (std_dev * std))
    
    def _bollinger_lower(self, data: np.ndarray, period: int = 20, std_dev: int = 2) -> float:
        sma = np.mean(data[-period:])
        std = np.std(data[-period:])
        return float(sma - (std_dev * std))
    
    def _atr(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, period: int = 14) -> float:
        tr = np.abs(highs[-period:] - lows[-period:])
        atr = np.mean(tr)
        return float(atr)
    
    def _obv(self, closes: np.ndarray, volumes: np.ndarray) -> float:
        obv = 0
        for i in range(len(closes)):
            if closes[i] > closes[i-1]:
                obv += volumes[i]
            elif closes[i] < closes[i-1]:
                obv -= volumes[i]
        return float(obv)
    
    def _vwap(self, ohlcv: List[Dict]) -> float:
        tp = np.array([c['volume'] for c in ohlcv]) * np.array([(c['high'] + c['low'] + c['close']) / 3 for c in ohlcv])
        vwap = np.sum(tp) / np.sum([c['volume'] for c in ohlcv])
        return float(vwap)
    
    def _support(self, lows: np.ndarray) -> float:
        return float(np.min(lows[-20:]))
    
    def _resistance(self, highs: np.ndarray) -> float:
        return float(np.max(highs[-20:]))
    
    def _candle_pattern(self, candle: Dict) -> float:
        o, h, l, c = candle['open'], candle['high'], candle['low'], candle['close']
        body = abs(c - o)
        range_val = h - l
        if range_val == 0:
            return 0.5
        return float(body / range_val)
    
    def _harmonic_pattern(self, ohlcv: List[Dict]) -> float:
        if len(ohlcv) < 4:
            return 0.5
        closes = [c['close'] for c in ohlcv[-4:]]
        return float(np.std(closes) / np.mean(closes))
    
    def _trend_strength(self, data: np.ndarray) -> float:
        sma20 = self._sma(data, 20)
        current = data[-1]
        strength = (current - sma20) / sma20 if sma20 != 0 else 0
        return float(np.clip(strength, -1, 1))
    
    def _divergence_score(self, data: np.ndarray) -> float:
        rsi = self._rsi(data, 14)
        momentum = self._roc(data, 12)
        divergence = np.corrcoef([rsi], [momentum])[0, 1]
        return float(divergence)
    
    def _breakout_score(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> float:
        recent_high = np.max(highs[-10:])
        recent_low = np.min(lows[-10:])
        current = closes[-1]
        if current > recent_high:
            return 1.0
        elif current < recent_low:
            return -1.0
        else:
            return 0.0
    
    def _momentum_score(self, data: np.ndarray) -> float:
        roc = self._roc(data, 12)
        rsi = self._rsi(data, 14)
        score = (roc / 100 + (rsi - 50) / 50) / 2
        return float(np.clip(score, -1, 1))


# ============================================================================
# [57] MULTI-TIMEFRAME CONFLUENCE - DIVERGENCE DETECTION
# ============================================================================

class MultiTimeframeConfluence:
    """Analyze confluence and divergence across timeframes"""
    
    @staticmethod
    def calculate_confluence(timeframes_data: Dict[str, List[Dict]]) -> Dict:
        """Calculate confluence score across timeframes"""
        scores = {}
        
        for tf, ohlcv in timeframes_data.items():
            if len(ohlcv) < 2:
                continue
            
            latest = ohlcv[-1]
            score = 1.0 if latest['close'] > latest['open'] else -1.0
            scores[tf] = score
        
        if not scores:
            return {'confluence': 0.5, 'alignment': 'UNKNOWN'}
        
        avg_score = np.mean(list(scores.values()))
        confluence = (avg_score + 1) / 2  # 0-1 range
        
        alignment = 'STRONG_UP' if confluence > 0.75 else 'STRONG_DOWN' if confluence < 0.25 else 'MIXED'
        
        return {
            'confluence': float(confluence),
            'alignment': alignment,
            'scores': scores
        }
    
    @staticmethod
    def calculate_divergence(timeframes_data: Dict[str, List[Dict]]) -> Dict:
        """Detect divergences"""
        divergences = []
        directions = {}
        
        for tf, ohlcv in timeframes_data.items():
            if len(ohlcv) < 2:
                continue
            latest = ohlcv[-1]
            directions[tf] = 'UP' if latest['close'] > latest['open'] else 'DOWN'
        
        tf_list = list(directions.keys())
        for i in range(len(tf_list) - 1):
            if directions[tf_list[i]] != directions[tf_list[i+1]]:
                divergences.append(f"{tf_list[i]}_vs_{tf_list[i+1]}")
        
        return {
            'has_divergence': len(divergences) > 0,
            'divergences': divergences,
            'directions': directions
        }


# ============================================================================
# [58] BACKTESTER 3-YEAR - HISTORICAL ANALYSIS
# ============================================================================

class Backtester3Year:
    """Backtest signals on 3 years of real data"""
    
    def __init__(self):
        self.results = {}
        logger.info("📈 3-year backtester initialized")
    
    def backtest(self, symbol: str, signals: List[Dict], ohlcv: List[Dict]) -> Dict:
        """Backtest signals"""
        if len(ohlcv) < 100:
            return {'error': 'Insufficient data'}
        
        wins = 0
        losses = 0
        total_pnl = 0
        
        for i, signal in enumerate(signals):
            if i + 1 >= len(ohlcv):
                break
            
            entry = signal.get('entry_price', ohlcv[i]['close'])
            exit_price = ohlcv[i+1]['close']
            
            pnl = (exit_price - entry) / entry if signal.get('direction') == 'LONG' else (entry - exit_price) / entry
            
            if pnl > 0:
                wins += 1
            else:
                losses += 1
            
            total_pnl += pnl * 100
        
        total_trades = wins + losses
        win_rate = wins / total_trades if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': float(win_rate),
            'total_pnl': float(total_pnl),
            'avg_pnl': float(total_pnl / total_trades) if total_trades > 0 else 0,
            'sharpe_ratio': self._calculate_sharpe(ohlcv),
            'max_drawdown': self._calculate_max_drawdown(ohlcv)
        }
    
    def _calculate_sharpe(self, ohlcv: List[Dict], rf_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        closes = np.array([c['close'] for c in ohlcv])
        returns = np.diff(closes) / closes[:-1]
        sharpe = (np.mean(returns) - rf_rate) / (np.std(returns) + 1e-10)
        return float(sharpe)
    
    def _calculate_max_drawdown(self, ohlcv: List[Dict]) -> float:
        """Calculate max drawdown"""
        closes = np.array([c['close'] for c in ohlcv])
        running_max = np.maximum.accumulate(closes)
        drawdown = (closes - running_max) / running_max
        return float(np.min(drawdown))


# ============================================================================
# [59] POSITION MANAGER - KELLY CRITERION
# ============================================================================

class PositionManager:
    """Smart position sizing using Kelly Criterion"""
    
    @staticmethod
    def calculate_kelly_fraction(win_rate: float, avg_win: float, avg_loss: float) -> float:
        """Calculate Kelly fraction: f = (bp - q) / b"""
        if avg_loss <= 0:
            return 0.1
        
        b = avg_win / avg_loss
        p = win_rate
        q = 1 - win_rate
        
        kelly = (b * p - q) / b if b > 0 else 0
        
        # Conservative: use half Kelly
        conservative_kelly = kelly / 2
        
        return float(np.clip(conservative_kelly, 0.01, 0.25))
    
    @staticmethod
    def calculate_position_size(account_balance: float, kelly_fraction: float, risk_per_trade: float = 0.02) -> Dict:
        """Calculate position size"""
        
        position_size = account_balance * kelly_fraction * risk_per_trade
        
        return {
            'kelly_fraction': float(kelly_fraction),
            'position_size': float(position_size),
            'risk_amount': float(account_balance * risk_per_trade),
            'leverage': int(position_size / (account_balance * risk_per_trade))
        }


# ============================================================================
# [60-62] REMAINING UTILITIES (COMPACT)
# ============================================================================

class BacktestResultsProcessor:
    """Process and export backtest results"""
    
    @staticmethod
    def export_csv(results: Dict, filename: str) -> bool:
        df = pd.DataFrame([results])
        df.to_csv(filename, index=False)
        return True


class DataFetcherRealtime:
    """Cache and serve historical data"""
    
    def __init__(self):
        self.cache = {}
    
    def cache_data(self, symbol: str, ohlcv: List[Dict]):
        self.cache[symbol] = ohlcv


class SignalProcessorAdvanced:
    """Process signals across multiple timeframes"""
    
    @staticmethod
    def process_multi_timeframe(signals_15m: Dict, signals_1h: Dict, signals_4h: Dict, signals_1d: Dict) -> Dict:
        """Aggregate signals"""
        
        weights = {'15m': 0.2, '1h': 0.3, '4h': 0.3, '1d': 0.2}
        
        total_score = (
            signals_15m.get('score', 0.5) * weights['15m'] +
            signals_1h.get('score', 0.5) * weights['1h'] +
            signals_4h.get('score', 0.5) * weights['4h'] +
            signals_1d.get('score', 0.5) * weights['1d']
        )
        
        return {
            'aggregated_score': float(total_score),
            'direction': 'LONG' if total_score > 0.5 else 'SHORT' if total_score < 0.5 else 'NEUTRAL',
            'confidence': float(abs(total_score - 0.5) * 2)
        }
