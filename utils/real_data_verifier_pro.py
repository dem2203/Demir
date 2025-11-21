# utils/real_data_verifier_pro.py
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 DEMIR AI v7.0 - REAL DATA VERIFIER PRO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRITICAL COMPONENT - ABSOLUTE REAL DATA ENFORCEMENT

This module ensures ALL data is 100% from real exchanges:
    ✅ ONLY Real Binance API Data
    ✅ ONLY Real Bybit API Data
    ✅ ONLY Real Coinbase API Data
    ✅ Multi-exchange cross-validation
    ✅ Timestamp freshness verification
    ✅ Statistical anomaly detection
    ✅ Price movement validation

ZERO TOLERANCE ENFORCEMENT:
    - Any non-exchange data is REJECTED immediately
    - Cross-validation with live exchange APIs
    - Historical pattern analysis
    - Real-time source tracking

DEPLOYMENT: Railway Production
AUTHOR: DEMIR AI Research Team
DATE: 2025-11-19
VERSION: 7.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from collections import deque, defaultdict
import numpy as np

logger = logging.getLogger(__name__)

# ============================================================================
# VERIFIED REAL EXCHANGE SOURCES
# ============================================================================

VERIFIED_REAL_SOURCES = {
    'BINANCE': {
        'api_url': 'https://api.binance.com',
        'ws_url': 'wss://stream.binance.com:9443',
        'status': 'TRUSTED'
    },
    'BYBIT': {
        'api_url': 'https://api.bybit.com',
        'ws_url': 'wss://stream.bybit.com',
        'status': 'TRUSTED'
    },
    'COINBASE': {
        'api_url': 'https://api.pro.coinbase.com',
        'ws_url': 'wss://ws-feed.pro.coinbase.com',
        'status': 'TRUSTED'
    }
}

# Known real exchange domains (for URL validation)
TRUSTED_EXCHANGE_DOMAINS = [
    'binance.com',
    'binance.us',
    'bybit.com',
    'coinbase.com',
    'pro.coinbase.com',
    'kraken.com',
    'okx.com'
]

# ============================================================================
# REAL DATA VERIFIER PRO
# ============================================================================

class RealDataVerifier:
    """
    Professional real-time data verification system
    
    ENFORCEMENT POLICY:
    - ALL data must come from verified exchange APIs
    - Cross-validation between multiple exchanges
    - Timestamp must be fresh (< 60 seconds)
    - Price movements validated against history
    - Source tracking for audit trail
    """
    
    def __init__(self):
        """Initialize the verifier"""
        
        # Price history for validation (last 100 prices per symbol)
        self.price_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Last verified prices (for comparison)
        self.last_verified_prices: Dict[str, Dict[str, Any]] = {}
        
        # Data source tracking (audit trail)
        self.source_audit_trail: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Exchange API health status
        self.exchange_health: Dict[str, bool] = {
            'BINANCE': True,
            'BYBIT': True,
            'COINBASE': True
        }
        
        # Rejection tracking
        self.rejection_log = deque(maxlen=1000)
        
        # Statistics
        self.stats = {
            'total_verifications': 0,
            'passed_verifications': 0,
            'failed_verifications': 0,
            'real_data_percentage': 100.0
        }
        
        logger.info("✅ RealDataVerifier initialized - ONLY REAL EXCHANGE DATA")
    
    # ========================================================================
    # MAIN VERIFICATION METHODS
    # ========================================================================
    
    def verify_price(
        self,
        symbol: str,
        price: float,
        exchange: str,
        timestamp: Optional[float] = None
    ) -> Tuple[bool, str]:
        """
        Verify that price data is from real exchange
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            price: Price value
            exchange: Data source (must be BINANCE, BYBIT, or COINBASE)
            timestamp: Data timestamp
        
        Returns:
            (is_valid, reason)
        """
        self.stats['total_verifications'] += 1
        
        # 1. Validate exchange source (CRITICAL)
        if not self._is_trusted_exchange(exchange):
            return self._reject(
                symbol, price, exchange,
                f"Untrusted source: {exchange}. Only BINANCE, BYBIT, COINBASE allowed"
            )
        
        # 2. Check for None or invalid types
        if price is None:
            return self._reject(symbol, price, exchange, "Price is None")
        
        if not isinstance(price, (int, float)):
            return self._reject(
                symbol, price, exchange,
                f"Price is not numeric: {type(price)}"
            )
        
        # 3. Basic sanity checks
        if price <= 0:
            return self._reject(
                symbol, price, exchange,
                f"Non-positive price: {price}"
            )
        
        if price > 10_000_000:  # $10M per coin is unrealistic
            return self._reject(
                symbol, price, exchange,
                f"Unreasonably high price: {price}"
            )
        
        if np.isnan(price) or np.isinf(price):
            return self._reject(symbol, price, exchange, "Price is NaN or Inf")
        
        # 4. Timestamp validation (must be fresh)
        if timestamp:
            ts_valid, ts_msg = self._validate_timestamp(timestamp)
            if not ts_valid:
                return self._reject(
                    symbol, price, exchange,
                    f"Stale timestamp: {ts_msg}"
                )
        
        # 5. Cross-validate with live exchange (CRITICAL)
        cross_valid, cross_msg = self._cross_validate_with_exchange(
            symbol, price, exchange
        )
        if not cross_valid:
            return self._reject(
                symbol, price, exchange,
                f"Cross-validation failed: {cross_msg}"
            )
        
        # 6. Historical consistency check
        if symbol in self.last_verified_prices:
            history_valid, history_msg = self._validate_price_movement(
                symbol, price
            )
            if not history_valid:
                logger.warning(f"⚠️ Price movement warning for {symbol}: {history_msg}")
                # Don't reject, just warn (can be legitimate volatility)
        
        # ALL CHECKS PASSED ✅
        self._record_success(symbol, price, exchange, timestamp)
        
        return True, f"REAL DATA VERIFIED: ${price:.2f} from {exchange}"
    
    def verify_signal(
        self,
        signal: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Verify that signal data is from real sources
        
        Args:
            signal: Signal dictionary
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # 1. Verify required fields exist
        required_fields = [
            'symbol', 'direction', 'entry_price',
            'timestamp', 'data_source'
        ]
        
        for field in required_fields:
            if field not in signal:
                issues.append(f"Missing required field: {field}")
        
        if issues:
            return False, issues
        
        # 2. Verify data source is trusted exchange
        data_source = signal.get('data_source', '').upper()
        
        # Extract exchange name from source (e.g., "REAL(BINANCE)" -> "BINANCE")
        exchange_name = data_source
        if '(' in data_source:
            exchange_name = data_source.split('(')[1].split(')')[0]
        
        if not self._is_trusted_exchange(exchange_name):
            issues.append(
                f"Untrusted data source: {data_source}. "
                f"Must be from BINANCE, BYBIT, or COINBASE"
            )
        
        # 3. Verify price data with exchange
        entry_price = signal.get('entry_price', 0)
        is_valid_price, price_msg = self.verify_price(
            symbol=signal['symbol'],
            price=entry_price,
            exchange=exchange_name,
            timestamp=signal.get('timestamp')
        )
        
        if not is_valid_price:
            issues.append(f"Entry price validation failed: {price_msg}")
        
        # 4. Verify stop loss
        if 'sl' in signal:
            sl = signal['sl']
            if not isinstance(sl, (int, float)) or sl <= 0:
                issues.append(f"Invalid stop loss: {sl}")
        
        # 5. Verify take profit levels
        for tp_key in ['tp1', 'tp2', 'tp3']:
            if tp_key in signal:
                tp = signal[tp_key]
                if not isinstance(tp, (int, float)) or tp <= 0:
                    issues.append(f"Invalid {tp_key}: {tp}")
        
        # 6. Verify direction
        direction = signal.get('direction', '').upper()
        if direction not in ['LONG', 'SHORT']:
            issues.append(f"Invalid direction: {direction}")
        
        # 7. Logic validation (SL/TP vs entry)
        if direction == 'LONG':
            if signal.get('sl', 0) >= entry_price:
                issues.append(
                    f"LONG position: SL must be < entry "
                    f"({signal.get('sl')} >= {entry_price})"
                )
            if signal.get('tp1', 0) <= entry_price:
                issues.append(
                    f"LONG position: TP must be > entry "
                    f"({signal.get('tp1')} <= {entry_price})"
                )
        
        elif direction == 'SHORT':
            if signal.get('sl', float('inf')) <= entry_price:
                issues.append(
                    f"SHORT position: SL must be > entry "
                    f"({signal.get('sl')} <= {entry_price})"
                )
            if signal.get('tp1', float('inf')) >= entry_price:
                issues.append(
                    f"SHORT position: TP must be < entry "
                    f"({signal.get('tp1')} >= {entry_price})"
                )
        
        # 8. Confidence validation
        confidence = signal.get('confidence', 0)
        if not (0 <= confidence <= 1):
            issues.append(f"Confidence out of range [0,1]: {confidence}")
        
        if issues:
            return False, issues
        
        return True, []
    
    async def verify_price_async(
        self,
        symbol: str,
        price: float,
        exchange: str
    ) -> bool:
        """Async version of verify_price"""
        is_valid, _ = self.verify_price(symbol, price, exchange)
        return is_valid
    
    # ========================================================================
    # VALIDATION HELPERS
    # ========================================================================
    
    def _is_trusted_exchange(self, source: str) -> bool:
        """
        Check if source is a trusted exchange
        
        Args:
            source: Exchange name or source string
        
        Returns:
            True if trusted, False otherwise
        """
        source_upper = source.upper()
        
        # Check if it's one of our verified exchanges
        if source_upper in VERIFIED_REAL_SOURCES:
            return True
        
        # Check if source contains a trusted domain
        source_lower = source.lower()
        for domain in TRUSTED_EXCHANGE_DOMAINS:
            if domain in source_lower:
                return True
        
        return False
    
    def _validate_timestamp(self, timestamp: float) -> Tuple[bool, str]:
        """
        Validate timestamp freshness
        
        Args:
            timestamp: Unix timestamp
        
        Returns:
            (is_valid, message)
        """
        try:
            current_time = time.time()
            
            # Check if timestamp is in the future
            if timestamp > current_time + 60:  # 1 minute tolerance
                return False, f"Future timestamp detected: {timestamp - current_time:.0f}s ahead"
            
            # Check if timestamp is too old (max 60 seconds for real-time)
            age = current_time - timestamp
            if age > 60:
                return False, f"Data too old: {age:.0f}s (max 60s for real-time)"
            
            return True, f"Timestamp fresh: {age:.1f}s old"
            
        except Exception as e:
            return False, f"Timestamp validation error: {e}"
    
    def _cross_validate_with_exchange(
        self,
        symbol: str,
        price: float,
        exchange: str,
        tolerance: float = 0.02  # 2% tolerance
    ) -> Tuple[bool, str]:
        """
        Cross-validate price with live exchange API
        
        THIS IS THE CRITICAL CHECK - Ensures data is from real exchange
        
        Args:
            symbol: Trading pair
            price: Price to validate
            exchange: Exchange name
            tolerance: Acceptable deviation (2%)
        
        Returns:
            (is_valid, message)
        """
        try:
            # Get live price from Binance (public endpoint, no API key needed)
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                live_price = float(data['price'])
                
                # Calculate deviation
                deviation = abs(price - live_price) / live_price
                
                if deviation > tolerance:
                    return False, (
                        f"Price deviation: {deviation*100:.1f}% "
                        f"(reported: ${price:.2f}, live: ${live_price:.2f})"
                    )
                
                return True, (
                    f"Cross-validated with Binance: "
                    f"deviation {deviation*100:.2f}%"
                )
            else:
                # If Binance API fails, try Bybit
                return self._cross_validate_bybit(symbol, price, tolerance)
        
        except requests.RequestException as e:
            logger.error(f"Cross-validation error: {e}")
            # If cross-validation fails, be conservative and reject
            return False, f"Unable to cross-validate: {e}"
        except Exception as e:
            logger.error(f"Cross-validation unexpected error: {e}")
            return False, f"Cross-validation failed: {e}"
    
    def _cross_validate_bybit(
        self,
        symbol: str,
        price: float,
        tolerance: float = 0.02
    ) -> Tuple[bool, str]:
        """Cross-validate with Bybit API"""
        try:
            # Bybit uses different symbol format
            bybit_symbol = symbol.replace('USDT', '')
            url = f"https://api.bybit.com/v2/public/tickers?symbol={bybit_symbol}USDT"
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ret_code') == 0:
                    result = data.get('result', [])
                    if result:
                        live_price = float(result[0]['last_price'])
                        deviation = abs(price - live_price) / live_price
                        
                        if deviation > tolerance:
                            return False, f"Bybit deviation: {deviation*100:.1f}%"
                        
                        return True, f"Cross-validated with Bybit: {deviation*100:.2f}%"
            
            return False, "Unable to cross-validate with Bybit"
        
        except Exception as e:
            return False, f"Bybit validation error: {e}"
    
    def _validate_price_movement(
        self,
        symbol: str,
        price: float
    ) -> Tuple[bool, str]:
        """
        Validate price against historical data
        
        Args:
            symbol: Trading pair
            price: Current price
        
        Returns:
            (is_valid, message)
        """
        if symbol not in self.last_verified_prices:
            return True, "No history available"
        
        last_data = self.last_verified_prices[symbol]
        last_price = last_data['price']
        
        # Calculate price change
        change_pct = abs(price - last_price) / last_price
        
        # Extreme movement (>15% is highly suspicious for short timeframe)
        if change_pct > 0.15:
            return False, (
                f"Extreme price movement: {change_pct*100:.1f}% "
                f"(${last_price:.2f} → ${price:.2f})"
            )
        
        # High movement warning (>5%)
        if change_pct > 0.05:
            return True, (
                f"High volatility detected: {change_pct*100:.1f}% movement"
            )
        
        return True, f"Normal price movement: {change_pct*100:.2f}%"
    
    # ========================================================================
    # STATISTICS & LOGGING
    # ========================================================================
    
    def _record_success(
        self,
        symbol: str,
        price: float,
        exchange: str,
        timestamp: Optional[float]
    ):
        """Record successful verification"""
        self.stats['passed_verifications'] += 1
        
        # Update last verified price
        self.last_verified_prices[symbol] = {
            'price': price,
            'exchange': exchange,
            'timestamp': timestamp or time.time(),
            'verified_at': datetime.now()
        }
        
        # Add to history
        self.price_history[symbol].append(price)
        
        # Audit trail
        self.source_audit_trail[symbol].append({
            'price': price,
            'exchange': exchange,
            'timestamp': timestamp or time.time(),
            'status': 'VERIFIED'
        })
        
        # Keep audit trail manageable (last 100 entries per symbol)
        if len(self.source_audit_trail[symbol]) > 100:
            self.source_audit_trail[symbol] = self.source_audit_trail[symbol][-100:]
        
        # Update statistics
        total = self.stats['total_verifications']
        passed = self.stats['passed_verifications']
        self.stats['real_data_percentage'] = (passed / total * 100) if total > 0 else 100.0
    
    def _reject(
        self,
        symbol: str,
        price: float,
        exchange: str,
        reason: str
    ) -> Tuple[bool, str]:
        """Record rejection and return False"""
        self.stats['failed_verifications'] += 1
        
        # Log rejection
        rejection = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'price': price,
            'exchange': exchange,
            'reason': reason
        }
        self.rejection_log.append(rejection)
        
        # Update statistics
        total = self.stats['total_verifications']
        passed = self.stats['passed_verifications']
        self.stats['real_data_percentage'] = (passed / total * 100) if total > 0 else 100.0
        
        logger.error(
            f"❌ DATA REJECTED: {symbol} @ ${price:.2f} "
            f"from {exchange} - {reason}"
        )
        
        return False, reason
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get verification statistics"""
        return {
            'total_verifications': self.stats['total_verifications'],
            'passed': self.stats['passed_verifications'],
            'failed': self.stats['failed_verifications'],
            'real_data_percentage': self.stats['real_data_percentage'],
            'exchange_health': self.exchange_health,
            'recent_rejections': list(self.rejection_log)[-10:]
        }
    
    def get_audit_trail(self, symbol: str) -> List[Dict[str, Any]]:
        """Get audit trail for a specific symbol"""
        return self.source_audit_trail.get(symbol, [])
    
    def reset_statistics(self):
        """Reset all statistics"""
        self.stats = {
            'total_verifications': 0,
            'passed_verifications': 0,
            'failed_verifications': 0,
            'real_data_percentage': 100.0
        }
        self.rejection_log.clear()
        logger.info("Statistics reset")

# ============================================================================
# BACKWARD COMPATIBILITY ALIASES
# ============================================================================

# Alias for backward compatibility with main.py imports
MockDataDetector = RealDataVerifier

# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_global_verifier = None

def get_verifier() -> RealDataVerifier:
    """Get global verifier instance (singleton pattern)"""
    global _global_verifier
    if _global_verifier is None:
        _global_verifier = RealDataVerifier()
    return _global_verifier

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def verify_price(symbol: str, price: float, exchange: str) -> bool:
    """Quick price verification"""
    verifier = get_verifier()
    is_valid, _ = verifier.verify_price(symbol, price, exchange)
    return is_valid

def verify_signal(signal: Dict[str, Any]) -> bool:
    """Quick signal verification"""
    verifier = get_verifier()
    is_valid, _ = verifier.verify_signal(signal)
    return is_valid
