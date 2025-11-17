"""
DEMIR AI v6.0 - PHASE 4 [55]
Multi-Timeframe Manager - 15m/1h/4h/1d Synchronization
Sliding window OHLCV storage, timeframe aggregation, convergence detection
Production-grade timeframe handler for multi-timeframe analysis
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from collections import deque
import json

logger = logging.getLogger(__name__)


class TimeframeOHLCV:
    """OHLCV container for single timeframe"""
    
    def __init__(self, timeframe: str, max_candles: int = 5000):
        """Initialize timeframe storage"""
        self.timeframe = timeframe
        self.max_candles = max_candles
        self.candles = deque(maxlen=max_candles)
        self.last_update = None
        
    def add_candle(self, candle: Dict) -> bool:
        """Add OHLCV candle"""
        try:
            if candle['timestamp'] <= self.last_update:
                return False  # Duplicate or older
            
            self.candles.append(candle)
            self.last_update = candle['timestamp']
            return True
        except Exception as e:
            logger.error(f"Error adding candle: {e}")
            return False
    
    def get_recent(self, count: int = 100) -> List[Dict]:
        """Get recent candles"""
        return list(self.candles)[-count:] if self.candles else []
    
    def get_all(self) -> List[Dict]:
        """Get all candles"""
        return list(self.candles)
    
    def get_latest(self) -> Optional[Dict]:
        """Get latest candle"""
        return self.candles[-1] if self.candles else None
    
    def count(self) -> int:
        """Get candle count"""
        return len(self.candles)


class MultiTimeframeManager:
    """Manage multiple timeframes for symbol"""
    
    def __init__(self, symbol: str):
        """Initialize multi-timeframe manager"""
        self.symbol = symbol
        self.timeframes = {
            '15m': TimeframeOHLCV('15m', 5000),
            '1h': TimeframeOHLCV('1h', 2000),
            '4h': TimeframeOHLCV('4h', 1000),
            '1d': TimeframeOHLCV('1d', 365)
        }
        self.sync_status = {}
        logger.info(f"📊 Multi-timeframe manager created for {symbol}")
    
    def add_1m_candle(self, candle_1m: Dict) -> Dict[str, bool]:
        """Add 1-minute candle and aggregate to higher timeframes"""
        results = {'1m': True}
        
        try:
            timestamp = candle_1m['timestamp']
            
            # Aggregate 1m → 15m
            tf_15m = self._aggregate_to_15m(timestamp, candle_1m)
            if tf_15m and self.timeframes['15m'].add_candle(tf_15m):
                results['15m'] = True
            
            # Aggregate 1m → 1h
            tf_1h = self._aggregate_to_1h(timestamp, candle_1m)
            if tf_1h and self.timeframes['1h'].add_candle(tf_1h):
                results['1h'] = True
            
            # Aggregate 1m → 4h
            tf_4h = self._aggregate_to_4h(timestamp, candle_1m)
            if tf_4h and self.timeframes['4h'].add_candle(tf_4h):
                results['4h'] = True
            
            # Aggregate 1m → 1d
            tf_1d = self._aggregate_to_1d(timestamp, candle_1m)
            if tf_1d and self.timeframes['1d'].add_candle(tf_1d):
                results['1d'] = True
            
            return results
        
        except Exception as e:
            logger.error(f"Error adding 1m candle: {e}")
            return results
    
    def _aggregate_to_15m(self, timestamp: int, candle_1m: Dict) -> Optional[Dict]:
        """Aggregate 1m candles to 15m"""
        # 15m = 900 seconds
        tf_timestamp = (timestamp // 900000) * 900000
        
        recent_1m = self.timeframes['15m'].get_recent(15)
        if not recent_1m or recent_1m[-1].get('timestamp', 0) != tf_timestamp:
            return None
        
        # Aggregate
        opens = [c['open'] for c in recent_1m]
        highs = [c['high'] for c in recent_1m]
        lows = [c['low'] for c in recent_1m]
        closes = [c['close'] for c in recent_1m]
        volumes = [c['volume'] for c in recent_1m]
        
        return {
            'timestamp': tf_timestamp,
            'symbol': self.symbol,
            'open': opens[0] if opens else 0,
            'high': max(highs) if highs else 0,
            'low': min(lows) if lows else 0,
            'close': closes[-1] if closes else 0,
            'volume': sum(volumes) if volumes else 0
        }
    
    def _aggregate_to_1h(self, timestamp: int, candle_1m: Dict) -> Optional[Dict]:
        """Aggregate 1m candles to 1h"""
        tf_timestamp = (timestamp // 3600000) * 3600000
        
        recent_1m = self.timeframes['1h'].get_recent(60)
        if not recent_1m or recent_1m[-1].get('timestamp', 0) != tf_timestamp:
            return None
        
        opens = [c['open'] for c in recent_1m]
        highs = [c['high'] for c in recent_1m]
        lows = [c['low'] for c in recent_1m]
        closes = [c['close'] for c in recent_1m]
        volumes = [c['volume'] for c in recent_1m]
        
        return {
            'timestamp': tf_timestamp,
            'symbol': self.symbol,
            'open': opens[0] if opens else 0,
            'high': max(highs) if highs else 0,
            'low': min(lows) if lows else 0,
            'close': closes[-1] if closes else 0,
            'volume': sum(volumes) if volumes else 0
        }
    
    def _aggregate_to_4h(self, timestamp: int, candle_1m: Dict) -> Optional[Dict]:
        """Aggregate 1m candles to 4h"""
        tf_timestamp = (timestamp // 14400000) * 14400000
        
        recent_1m = self.timeframes['4h'].get_recent(240)
        if not recent_1m or recent_1m[-1].get('timestamp', 0) != tf_timestamp:
            return None
        
        opens = [c['open'] for c in recent_1m]
        highs = [c['high'] for c in recent_1m]
        lows = [c['low'] for c in recent_1m]
        closes = [c['close'] for c in recent_1m]
        volumes = [c['volume'] for c in recent_1m]
        
        return {
            'timestamp': tf_timestamp,
            'symbol': self.symbol,
            'open': opens[0] if opens else 0,
            'high': max(highs) if highs else 0,
            'low': min(lows) if lows else 0,
            'close': closes[-1] if closes else 0,
            'volume': sum(volumes) if volumes else 0
        }
    
    def _aggregate_to_1d(self, timestamp: int, candle_1m: Dict) -> Optional[Dict]:
        """Aggregate 1m candles to 1d"""
        tf_timestamp = (timestamp // 86400000) * 86400000
        
        recent_1m = self.timeframes['1d'].get_recent(1440)
        if not recent_1m or recent_1m[-1].get('timestamp', 0) != tf_timestamp:
            return None
        
        opens = [c['open'] for c in recent_1m]
        highs = [c['high'] for c in recent_1m]
        lows = [c['low'] for c in recent_1m]
        closes = [c['close'] for c in recent_1m]
        volumes = [c['volume'] for c in recent_1m]
        
        return {
            'timestamp': tf_timestamp,
            'symbol': self.symbol,
            'open': opens[0] if opens else 0,
            'high': max(highs) if highs else 0,
            'low': min(lows) if lows else 0,
            'close': closes[-1] if closes else 0,
            'volume': sum(volumes) if volumes else 0
        }
    
    def get_timeframe_data(self, timeframe: str, count: int = 100) -> List[Dict]:
        """Get timeframe data"""
        if timeframe not in self.timeframes:
            return []
        return self.timeframes[timeframe].get_recent(count)
    
    def get_confluence(self) -> Dict[str, any]:
        """Get multi-timeframe confluence analysis"""
        try:
            latest_15m = self.timeframes['15m'].get_latest()
            latest_1h = self.timeframes['1h'].get_latest()
            latest_4h = self.timeframes['4h'].get_latest()
            latest_1d = self.timeframes['1d'].get_latest()
            
            if not all([latest_15m, latest_1h, latest_4h, latest_1d]):
                return {'confluence': 0, 'alignment': 'INSUFFICIENT_DATA'}
            
            # Calculate direction for each timeframe
            dir_15m = 'UP' if latest_15m['close'] > latest_15m['open'] else 'DOWN'
            dir_1h = 'UP' if latest_1h['close'] > latest_1h['open'] else 'DOWN'
            dir_4h = 'UP' if latest_4h['close'] > latest_4h['open'] else 'DOWN'
            dir_1d = 'UP' if latest_1d['close'] > latest_1d['open'] else 'DOWN'
            
            # Count alignment
            directions = [dir_15m, dir_1h, dir_4h, dir_1d]
            up_count = directions.count('UP')
            down_count = directions.count('DOWN')
            
            # Confluence score (0-100)
            confluence = max(up_count, down_count) * 25
            alignment = 'STRONG_UP' if up_count == 4 else 'STRONG_DOWN' if down_count == 4 else 'MIXED'
            
            return {
                'confluence': confluence,
                'alignment': alignment,
                'directions': {
                    '15m': dir_15m,
                    '1h': dir_1h,
                    '4h': dir_4h,
                    '1d': dir_1d
                },
                'latest': {
                    '15m': latest_15m['close'],
                    '1h': latest_1h['close'],
                    '4h': latest_4h['close'],
                    '1d': latest_1d['close']
                }
            }
        
        except Exception as e:
            logger.error(f"Error calculating confluence: {e}")
            return {'confluence': 0, 'alignment': 'ERROR'}
    
    def get_divergence(self) -> Dict[str, any]:
        """Detect divergences between timeframes"""
        try:
            confluence = self.get_confluence()
            directions = confluence.get('directions', {})
            
            divergences = []
            
            # Check 15m vs 1h
            if directions.get('15m') != directions.get('1h'):
                divergences.append('15m_vs_1h')
            
            # Check 1h vs 4h
            if directions.get('1h') != directions.get('4h'):
                divergences.append('1h_vs_4h')
            
            # Check 4h vs 1d
            if directions.get('4h') != directions.get('1d'):
                divergences.append('4h_vs_1d')
            
            return {
                'has_divergence': len(divergences) > 0,
                'divergences': divergences,
                'severity': len(divergences) / 3  # 0-1
            }
        
        except Exception as e:
            logger.error(f"Error detecting divergence: {e}")
            return {'has_divergence': False, 'divergences': [], 'severity': 0}
    
    def get_status(self) -> Dict[str, any]:
        """Get manager status"""
        return {
            'symbol': self.symbol,
            'timeframes': {
                tf: self.timeframes[tf].count()
                for tf in self.timeframes
            },
            'confluence': self.get_confluence(),
            'divergence': self.get_divergence()
        }


class GlobalTimeframeManager:
    """Manage timeframes for all symbols"""
    
    def __init__(self, symbols: List[str] = None):
        """Initialize global manager"""
        self.symbols = symbols or ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
        self.managers = {symbol: MultiTimeframeManager(symbol) for symbol in self.symbols}
        logger.info(f"🌍 Global timeframe manager created for {len(self.symbols)} symbols")
    
    def add_1m_candle(self, symbol: str, candle_1m: Dict) -> bool:
        """Add 1m candle for symbol"""
        if symbol not in self.managers:
            self.managers[symbol] = MultiTimeframeManager(symbol)
        
        results = self.managers[symbol].add_1m_candle(candle_1m)
        return results.get('1m', False)
    
    def get_manager(self, symbol: str) -> Optional[MultiTimeframeManager]:
        """Get manager for symbol"""
        return self.managers.get(symbol)
    
    def get_all_confluence(self) -> Dict[str, Dict]:
        """Get confluence for all symbols"""
        return {
            symbol: self.managers[symbol].get_confluence()
            for symbol in self.symbols
        }
    
    def get_all_divergence(self) -> Dict[str, Dict]:
        """Get divergence for all symbols"""
        return {
            symbol: self.managers[symbol].get_divergence()
            for symbol in self.symbols
        }


# Singleton
_global_manager = None

def get_global_timeframe_manager(symbols: List[str] = None) -> GlobalTimeframeManager:
    """Get or create singleton"""
    global _global_manager
    if _global_manager is None:
        _global_manager = GlobalTimeframeManager(symbols)
    return _global_manager
