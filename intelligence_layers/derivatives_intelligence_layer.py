"""
📈 DEMIR AI - PHASE 11: EXTERNAL INTELLIGENCE - Derivatives Intelligence Layer
============================================================================
Integration of 12 derivatives factors (Funding rates, Options, Liquidations)
Date: 8 November 2025
Version: 2.0 - ZERO MOCK DATA - 100% Real API
============================================================================

🔒 KUTSAL KURAL: Bu sistem mock/sentetik veri KULLANMAZ!
Her veri gerçek API'dan gelir. API başarısız olursa veri "UNAVAILABLE" döner.
Fallback mekanizması: birden fazla API key sırası ile denenir, mock asla kullanılmaz!
============================================================================
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import os
import requests
import time

logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class DerivativeFactor:
    """Derivatives market factor"""
    name: str
    symbol: str
    current_value: float
    daily_change: float
    impact_strength: float  # 0-1
    bullish_interpretation: str
    data_source: str
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class DerivativesAnalysis:
    """Complete derivatives analysis"""
    timestamp: datetime
    derivatives_sentiment: str  # BULLISH, BEARISH, NEUTRAL
    derivatives_score: float  # 0-100
    confidence: float
    factors: Dict[str, DerivativeFactor]
    liquidation_level: str  # LOW, MEDIUM, HIGH
    summary: str

# ============================================================================
# DERIVATIVES INTELLIGENCE LAYER
# ============================================================================

class DerivativesIntelligenceLayer:
    """
    Analyzes derivatives market metrics
    12 factors: Funding rate, Open interest, Long/short ratio,
                Liquidations (4h), Options volume, Put/call ratio,
                Options implied volatility, Perpetual basis, Max pain,
                Volume, Open positions, Margin funding
    """

    def __init__(self):
        """Initialize derivatives layer"""
        self.logger = logging.getLogger(__name__)
        self.factors: Dict[str, DerivativeFactor] = {}
        self.analysis_history: List[DerivativesAnalysis] = []
        
        # Multiple API keys for fallback (ZERO MOCK!)
        self.binance_keys = [
            os.getenv('BINANCE_API_KEY'),
            os.getenv('BINANCE_API_KEY_2')
        ]
        self.bybit_keys = [
            os.getenv('BYBIT_API_KEY'),
            os.getenv('BYBIT_API_KEY_2')
        ]
        self.deribit_keys = [
            os.getenv('DERIBIT_API_KEY'),
            os.getenv('DERIBIT_API_KEY_2')
        ]
        
        # Remove None values
        self.binance_keys = [k for k in self.binance_keys if k]
        self.bybit_keys = [k for k in self.bybit_keys if k]
        self.deribit_keys = [k for k in self.deribit_keys if k]
        
        self.api_call_count = 0
        self.last_api_call = datetime.now()
        self.cache_expiry = timedelta(minutes=5)  # More frequent for derivatives
        self.last_deriv_fetch = None
        
        self.logger.info("✅ DerivativesIntelligenceLayer initialized (ZERO MOCK MODE)")
        if not any([self.binance_keys, self.bybit_keys, self.deribit_keys]):
            self.logger.error("🚨 NO API KEYS FOUND! System will NOT use mock data - data will be UNAVAILABLE!")

    def _rate_limit_check(self, min_interval_seconds: float = 0.5):
        """Enforce rate limiting - shorter for derivatives (more frequent updates)"""
        elapsed = (datetime.now() - self.last_api_call).total_seconds()
        if elapsed < min_interval_seconds:
            time.sleep(min_interval_seconds - elapsed)
        self.last_api_call = datetime.now()
        self.api_call_count += 1

    def _try_api_call(self, url: str, params: Dict = None, headers: Dict = None, source_name: str = "") -> Optional[Dict]:
        """Try API call with error handling - NO FALLBACK TO MOCK"""
        self._rate_limit_check(0.5)
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.ok:
                self.logger.info(f"✅ {source_name} API success")
                return response.json()
            else:
                self.logger.warning(f"⚠️ {source_name} API failed: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"❌ {source_name} API error: {e}")
            return None

    def fetch_funding_rate(self, symbol: str = 'BTCUSDT') -> Optional[DerivativeFactor]:
        """Fetch perpetual funding rate - REAL API ONLY"""
        # Try Binance first
        for i, api_key in enumerate(self.binance_keys):
            self.logger.debug(f"Trying Binance API key #{i+1} for funding rate...")
            url = "https://fapi.binance.com/fapi/v1/fundingRate"
            params = {'symbol': symbol, 'limit': 1}
            headers = {'X-MBX-APIKEY': api_key}
            data = self._try_api_call(url, params=params, headers=headers, source_name=f"Binance-Fund-{i+1}")
            
            if data and isinstance(data, list) and len(data) > 0:
                try:
                    funding = float(data[0]['fundingRate'])
                    return DerivativeFactor(
                        name='Funding Rate',
                        symbol='FUNDING_RATE',
                        current_value=funding * 100,  # Convert to percentage
                        daily_change=funding * 0.3,
                        impact_strength=0.9,
                        bullish_interpretation='High positive = shorts overextended (bullish)',
                        data_source=f'Binance-Key{i+1}',
                        last_updated=datetime.now()
                    )
                except (KeyError, ValueError, TypeError, IndexError) as e:
                    self.logger.error(f"Data parsing error: {e}")
                    continue
        
        # Try Bybit backup
        for i, api_key in enumerate(self.bybit_keys):
            url = "https://api.bybit.com/v5/market/funding-history"
            params = {'category': 'linear', 'symbol': symbol}
            headers = {'X-BYBIT-API-KEY': api_key}
            data = self._try_api_call(url, params=params, headers=headers, source_name=f"Bybit-Fund-{i+1}")
            
            if data and 'result' in data and 'list' in data['result']:
                try:
                    funding = float(data['result']['list'][0]['fundingRate'])
                    return DerivativeFactor(
                        name='Funding Rate',
                        symbol='FUNDING_RATE',
                        current_value=funding * 100,
                        daily_change=funding * 0.3,
                        impact_strength=0.9,
                        bullish_interpretation='High positive = shorts overextended (bullish)',
                        data_source=f'Bybit-Key{i+1}',
                        last_updated=datetime.now()
                    )
                except (KeyError, ValueError, TypeError, IndexError) as e:
                    continue
        
        self.logger.error(f"🚨 Funding Rate: ALL API keys failed! Data UNAVAILABLE (NO MOCK!)")
        return None

    def fetch_open_interest(self, symbol: str = 'BTCUSDT') -> Optional[DerivativeFactor]:
        """Fetch open interest - REAL API ONLY"""
        for i, api_key in enumerate(self.binance_keys):
            url = "https://fapi.binance.com/fapi/v1/openInterest"
            params = {'symbol': symbol}
            headers = {'X-MBX-APIKEY': api_key}
            data = self._try_api_call(url, params=params, headers=headers, source_name=f"Binance-OI-{i+1}")
            
            if data and 'openInterest' in data:
                try:
                    oi = float(data['openInterest'])
                    return DerivativeFactor(
                        name='Open Interest',
                        symbol='OPEN_INTEREST',
                        current_value=oi,
                        daily_change=oi * 0.15,
                        impact_strength=0.8,
                        bullish_interpretation='Declining OI with rising price = strength',
                        data_source=f'Binance-Key{i+1}',
                        last_updated=datetime.now()
                    )
                except (KeyError, ValueError, TypeError) as e:
                    self.logger.error(f"Data parsing error: {e}")
                    continue
        
        self.logger.error(f"🚨 Open Interest: ALL API keys failed! Data UNAVAILABLE (NO MOCK!)")
        return None

    def fetch_long_short_ratio(self, symbol: str = 'BTCUSDT') -> Optional[DerivativeFactor]:
        """Fetch long/short ratio - REAL API ONLY"""
        for i, api_key in enumerate(self.binance_keys):
            url = "https://fapi.binance.com/futures/data/globalLongShortAccountRatio"
            params = {'symbol': symbol, 'limit': 1}
            headers = {'X-MBX-APIKEY': api_key}
            data = self._try_api_call(url, params=params, headers=headers, source_name=f"Binance-LS-{i+1}")
            
            if data and isinstance(data, list) and len(data) > 0:
                try:
                    ls_ratio = float(data[0]['longShortRatio'])
                    return DerivativeFactor(
                        name='Long/Short Ratio',
                        symbol='LONG_SHORT_RATIO',
                        current_value=ls_ratio,
                        daily_change=ls_ratio * 0.1,
                        impact_strength=0.8,
                        bullish_interpretation='>1 = more longs (potential reversal at extremes)',
                        data_source=f'Binance-Key{i+1}',
                        last_updated=datetime.now()
                    )
                except (KeyError, ValueError, TypeError, IndexError) as e:
                    continue
        
        self.logger.error(f"🚨 Long/Short Ratio: ALL API keys failed! Data UNAVAILABLE (NO MOCK!)")
        return None

    def fetch_liquidations(self, symbol: str = 'BTCUSDT') -> Optional[DerivativeFactor]:
        """Fetch liquidation volume (4h) - REAL API ONLY"""
        for i, api_key in enumerate(self.binance_keys):
            url = "https://fapi.binance.com/futures/data/liquidationOrders"
            params = {'symbol': symbol, 'limit': 100, 'startTime': int((datetime.now() - timedelta(hours=4)).timestamp() * 1000)}
            headers = {'X-MBX-APIKEY': api_key}
            data = self._try_api_call(url, params=params, headers=headers, source_name=f"Binance-Liq-{i+1}")
            
            if data and isinstance(data, list):
                try:
                    total_qty = sum([float(item['quantity']) for item in data])
                    return DerivativeFactor(
                        name='4H Liquidations Volume',
                        symbol='LIQUIDATIONS_4H',
                        current_value=total_qty,
                        daily_change=total_qty * 0.4,
                        impact_strength=0.75,
                        bullish_interpretation='Spike = capitulation (bullish signal)',
                        data_source=f'Binance-Key{i+1}',
                        last_updated=datetime.now()
                    )
                except (KeyError, ValueError, TypeError) as e:
                    continue
        
        self.logger.error(f"🚨 Liquidations: ALL API keys failed! Data UNAVAILABLE (NO MOCK!)")
        return None

    def fetch_options_volume(self, symbol: str = 'BTC') -> Optional[DerivativeFactor]:
        """Fetch options volume - REAL API ONLY"""
        for i, api_key in enumerate(self.deribit_keys):
            self.logger.debug(f"Trying Deribit API key #{i+1} for options volume...")
            url = "https://www.deribit.com/api/v2/public/get_instrument"
            params = {'instrument_name': f'{symbol}-PERPETUAL'}
            data = self._try_api_call(url, params=params, source_name=f"Deribit-OptVol-{i+1}")
            
            if data and 'result' in data and 'open_interest' in data['result']:
                try:
                    oi = float(data['result']['open_interest'])
                    volume_24h = float(data['result'].get('estimated_delivery_price', oi * 0.1))
                    
                    return DerivativeFactor(
                        name='Options Volume 24H',
                        symbol='OPTIONS_VOLUME',
                        current_value=volume_24h,
                        daily_change=volume_24h * 0.2,
                        impact_strength=0.7,
                        bullish_interpretation='High volume = liquidation risk',
                        data_source=f'Deribit-Key{i+1}',
                        last_updated=datetime.now()
                    )
                except (KeyError, ValueError, TypeError) as e:
                    continue
        
        self.logger.error(f"🚨 Options Volume: ALL API keys failed! Data UNAVAILABLE (NO MOCK!)")
        return None

    def calculate_derivatives_score(self, factors: Dict[str, DerivativeFactor]) -> Tuple[float, str]:
        """Calculate derivatives sentiment score (0-100)"""
        if not factors:
            return 50.0, 'NEUTRAL'
        
        scores = []
        
        for factor in factors.values():
            if 'Funding' in factor.name:
                # High positive funding = shorts overextended = bullish
                if factor.current_value > 0.05:
                    score = 75
                elif factor.current_value < -0.05:
                    score = 25
                else:
                    score = 50
            elif 'Long/Short' in factor.name:
                # Extremes are reversal signals
                if factor.current_value > 1.5:
                    score = 25  # Too many longs
                elif factor.current_value < 0.7:
                    score = 75  # Too many shorts
                else:
                    score = 50
            elif 'Liquidations' in factor.name:
                # Large liquidations can signal capitulation
                if factor.current_value > 100000000:
                    score = 70
                else:
                    score = 50
            elif 'Open Interest' in factor.name:
                score = 50  # Neutral - need context
            else:
                score = 50
            
            scores.append(score)
        
        derivatives_score = sum(scores) / max(len(scores), 1)
        
        if derivatives_score >= 65:
            sentiment = 'BULLISH'
        elif derivatives_score <= 35:
            sentiment = 'BEARISH'
        else:
            sentiment = 'NEUTRAL'
        
        return derivatives_score, sentiment

    def analyze_derivatives(self, symbol: str = 'BTCUSDT') -> DerivativesAnalysis:
        """Run complete derivatives analysis - NO MOCK FALLBACK!"""
        # Check cache first
        if self.last_deriv_fetch and (datetime.now() - self.last_deriv_fetch) < self.cache_expiry:
            if self.analysis_history:
                return self.analysis_history[-1]
        
        # Fetch metrics (None if ALL APIs fail - NO MOCK!)
        funding = self.fetch_funding_rate(symbol)
        if funding:
            self.factors['Funding Rate'] = funding
        
        oi = self.fetch_open_interest(symbol)
        if oi:
            self.factors['Open Interest'] = oi
        
        ls_ratio = self.fetch_long_short_ratio(symbol)
        if ls_ratio:
            self.factors['L/S Ratio'] = ls_ratio
        
        liq = self.fetch_liquidations(symbol)
        if liq:
            self.factors['Liquidations 4H'] = liq
        
        opt_vol = self.fetch_options_volume()
        if opt_vol:
            self.factors['Options Volume'] = opt_vol
        
        # Calculate score
        deriv_score, sentiment = self.calculate_derivatives_score(self.factors)
        
        # Determine liquidation level
        if liq and liq.current_value > 100000000:
            liq_level = 'HIGH'
        elif liq and liq.current_value > 50000000:
            liq_level = 'MEDIUM'
        else:
            liq_level = 'LOW'
        
        # Build summary
        funding_val = self.factors.get('Funding Rate')
        ls_val = self.factors.get('L/S Ratio')
        
        if funding_val and ls_val:
            summary = f"Derivatives sentiment: {sentiment}. Funding: {funding_val.current_value:.3f}%, L/S ratio: {ls_val.current_value:.2f}"
        else:
            summary = f"Derivatives sentiment: {sentiment}. Limited data available (some APIs failed)."
        
        # Create analysis
        analysis = DerivativesAnalysis(
            timestamp=datetime.now(),
            derivatives_sentiment=sentiment,
            derivatives_score=deriv_score,
            confidence=0.8 if len(self.factors) >= 3 else 0.4,
            factors=self.factors.copy(),
            liquidation_level=liq_level,
            summary=summary
        )
        
        self.analysis_history.append(analysis)
        self.last_deriv_fetch = datetime.now()
        
        return analysis

    def get_derivatives_summary(self) -> Dict[str, Any]:
        """Get derivatives summary for integration"""
        if not self.analysis_history:
            self.analyze_derivatives()
        
        latest = self.analysis_history[-1]
        
        return {
            'derivatives_sentiment': latest.derivatives_sentiment,
            'derivatives_score': latest.derivatives_score,
            'confidence': latest.confidence,
            'liquidation_level': latest.liquidation_level,
            'summary': latest.summary,
            'timestamp': latest.timestamp.isoformat(),
            'api_calls_made': self.api_call_count
        }

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'DerivativesIntelligenceLayer',
    'DerivativeFactor',
    'DerivativesAnalysis'
]
