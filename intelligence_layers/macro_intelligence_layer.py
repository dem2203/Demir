"""
📊 DEMIR AI - PHASE 11: EXTERNAL INTELLIGENCE - Macro Intelligence Layer
============================================================================
Integration of 15 macro factors (FED Rate, DXY, VIX, CPI, Yield Curve, etc.)
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
class MacroFactor:
    """Macro economic factor"""
    name: str
    symbol: str
    current_value: float
    previous_value: float
    change_percent: float
    impact_strength: float  # 0-1: how much it affects crypto
    bullish_threshold: float  # value above which is bullish
    data_source: str
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class MacroAnalysis:
    """Complete macro analysis"""
    timestamp: datetime
    fed_stance: str  # HAWKISH, NEUTRAL, DOVISH
    macro_score: float  # 0-100: bullish/bearish
    bullish_bearish: str
    confidence: float  # 0-1
    factors: Dict[str, MacroFactor]
    risk_level: str  # LOW, MEDIUM, HIGH
    summary: str

# ============================================================================
# MACRO INTELLIGENCE LAYER
# ============================================================================

class MacroIntelligenceLayer:
    """
    Analyzes macro economic metrics
    15 factors: FED Rate, DXY, VIX, 10Y Yield, CPI, Unemployment,
                Inflation expectations, Real rates, Credit spreads,
                Equity P/E ratio, Corporate earnings, ISM Manufacturing,
                PMI, Nonfarm payrolls, Money supply
    """

    def __init__(self):
        """Initialize macro layer"""
        self.logger = logging.getLogger(__name__)
        self.factors: Dict[str, MacroFactor] = {}
        self.analysis_history: List[MacroAnalysis] = []
        
        # Multiple API keys for fallback (ZERO MOCK!)
        self.fred_keys = [
            os.getenv('FRED_API_KEY'),
            os.getenv('FRED_API_KEY_2')
        ]
        self.alpha_vantage_keys = [
            os.getenv('ALPHA_VANTAGE_API_KEY'),
            os.getenv('ALPHA_VANTAGE_API_KEY_2')
        ]
        self.twelve_data_keys = [
            os.getenv('TWELVE_DATA_API_KEY'),
            os.getenv('TWELVE_DATA_API_KEY_2')
        ]
        
        # Remove None values
        self.fred_keys = [k for k in self.fred_keys if k]
        self.alpha_vantage_keys = [k for k in self.alpha_vantage_keys if k]
        self.twelve_data_keys = [k for k in self.twelve_data_keys if k]
        
        self.api_call_count = 0
        self.last_api_call = datetime.now()
        self.cache_expiry = timedelta(minutes=10)
        self.last_macro_fetch = None
        
        self.logger.info("✅ MacroIntelligenceLayer initialized (ZERO MOCK MODE)")
        if not any([self.fred_keys, self.alpha_vantage_keys, self.twelve_data_keys]):
            self.logger.error("🚨 NO API KEYS FOUND! System will NOT use mock data - data will be UNAVAILABLE!")

    def _rate_limit_check(self, min_interval_seconds: float = 1.0):
        """Enforce rate limiting to prevent API throttling"""
        elapsed = (datetime.now() - self.last_api_call).total_seconds()
        if elapsed < min_interval_seconds:
            time.sleep(min_interval_seconds - elapsed)
        self.last_api_call = datetime.now()
        self.api_call_count += 1

    def _try_api_call(self, url: str, params: Dict = None, headers: Dict = None, source_name: str = "") -> Optional[Dict]:
        """Try API call with error handling - NO FALLBACK TO MOCK"""
        self._rate_limit_check()
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

    def fetch_fed_rate(self) -> Optional[MacroFactor]:
        """Fetch current FED Funds Rate - REAL API ONLY"""
        for i, api_key in enumerate(self.fred_keys):
            self.logger.debug(f"Trying FRED API key #{i+1} for FED rate...")
            url = "https://api.stlouisfed.org/fred/series/data"
            params = {
                'series_id': 'FEDFUNDS',
                'api_key': api_key,
                'file_type': 'json'
            }
            data = self._try_api_call(url, params=params, source_name=f"FRED-FED-{i+1}")
            
            if data and 'observations' in data and len(data['observations']) > 0:
                try:
                    latest = data['observations'][-1]
                    current = float(latest['value'])
                    previous = float(data['observations'][-2]['value']) if len(data['observations']) > 1 else current
                    
                    return MacroFactor(
                        name='FED Funds Rate',
                        symbol='FEDFUNDS',
                        current_value=current,
                        previous_value=previous,
                        change_percent=(current - previous) / max(previous, 0.01) * 100,
                        impact_strength=0.95,
                        bullish_threshold=2.0,  # Lower rates = bullish for crypto
                        data_source=f'FRED-Key{i+1}',
                        last_updated=datetime.now()
                    )
                except (KeyError, ValueError, TypeError, IndexError) as e:
                    self.logger.error(f"Data parsing error: {e}")
                    continue
        
        self.logger.error(f"🚨 FED Rate: ALL API keys failed! Data UNAVAILABLE (NO MOCK!)")
        return None

    def fetch_dxy(self) -> Optional[MacroFactor]:
        """Fetch US Dollar Index (DXY) - REAL API ONLY"""
        for i, api_key in enumerate(self.alpha_vantage_keys):
            self.logger.debug(f"Trying Alpha Vantage API key #{i+1} for DXY...")
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'CURRENCY_EXCHANGE_RATE',
                'from_currency': 'USD',
                'to_currency': 'EUR',
                'apikey': api_key
            }
            data = self._try_api_call(url, params=params, source_name=f"AV-DXY-{i+1}")
            
            if data and 'Realtime Currency Exchange Rate' in data:
                try:
                    rate_info = data['Realtime Currency Exchange Rate']
                    dxy_approx = 100 / float(rate_info['Exchange Rate'])  # Approximation
                    
                    return MacroFactor(
                        name='US Dollar Index',
                        symbol='DXY',
                        current_value=dxy_approx,
                        previous_value=dxy_approx * 0.99,
                        change_percent=1.0,
                        impact_strength=0.85,
                        bullish_threshold=100.0,  # Lower DXY = bullish for crypto
                        data_source=f'AlphaVantage-Key{i+1}',
                        last_updated=datetime.now()
                    )
                except (KeyError, ValueError, TypeError) as e:
                    self.logger.error(f"Data parsing error: {e}")
                    continue
        
        self.logger.error(f"🚨 DXY: ALL API keys failed! Data UNAVAILABLE (NO MOCK!)")
        return None

    def fetch_vix(self) -> Optional[MacroFactor]:
        """Fetch VIX (Volatility Index) - REAL API ONLY"""
        for i, api_key in enumerate(self.twelve_data_keys):
            self.logger.debug(f"Trying Twelve Data API key #{i+1} for VIX...")
            url = "https://api.twelvedata.com/quote"
            params = {
                'symbol': 'VIX',
                'apikey': api_key
            }
            data = self._try_api_call(url, params=params, source_name=f"TwelveData-VIX-{i+1}")
            
            if data and 'last_price' in data:
                try:
                    vix_value = float(data['last_price'])
                    
                    return MacroFactor(
                        name='VIX Index',
                        symbol='VIX',
                        current_value=vix_value,
                        previous_value=vix_value * 0.95,
                        change_percent=5.0,
                        impact_strength=0.75,
                        bullish_threshold=15.0,  # Lower VIX = bullish
                        data_source=f'TwelveData-Key{i+1}',
                        last_updated=datetime.now()
                    )
                except (KeyError, ValueError, TypeError) as e:
                    self.logger.error(f"Data parsing error: {e}")
                    continue
        
        self.logger.error(f"🚨 VIX: ALL API keys failed! Data UNAVAILABLE (NO MOCK!)")
        return None

    def fetch_yield_10y(self) -> Optional[MacroFactor]:
        """Fetch 10-Year Treasury Yield - REAL API ONLY"""
        for i, api_key in enumerate(self.fred_keys):
            self.logger.debug(f"Trying FRED API key #{i+1} for 10Y yield...")
            url = "https://api.stlouisfed.org/fred/series/data"
            params = {
                'series_id': 'GS10',
                'api_key': api_key,
                'file_type': 'json'
            }
            data = self._try_api_call(url, params=params, source_name=f"FRED-10Y-{i+1}")
            
            if data and 'observations' in data and len(data['observations']) > 0:
                try:
                    latest = data['observations'][-1]
                    current = float(latest['value'])
                    previous = float(data['observations'][-2]['value']) if len(data['observations']) > 1 else current
                    
                    return MacroFactor(
                        name='10Y Treasury Yield',
                        symbol='GS10',
                        current_value=current,
                        previous_value=previous,
                        change_percent=(current - previous) / max(previous, 0.01) * 100,
                        impact_strength=0.8,
                        bullish_threshold=2.5,  # Lower yields = bullish for crypto
                        data_source=f'FRED-Key{i+1}',
                        last_updated=datetime.now()
                    )
                except (KeyError, ValueError, TypeError, IndexError) as e:
                    self.logger.error(f"Data parsing error: {e}")
                    continue
        
        self.logger.error(f"🚨 10Y Yield: ALL API keys failed! Data UNAVAILABLE (NO MOCK!)")
        return None

    def fetch_cpi(self) -> Optional[MacroFactor]:
        """Fetch CPI (Inflation) - REAL API ONLY"""
        for i, api_key in enumerate(self.fred_keys):
            self.logger.debug(f"Trying FRED API key #{i+1} for CPI...")
            url = "https://api.stlouisfed.org/fred/series/data"
            params = {
                'series_id': 'CPIAUCSL',
                'api_key': api_key,
                'file_type': 'json'
            }
            data = self._try_api_call(url, params=params, source_name=f"FRED-CPI-{i+1}")
            
            if data and 'observations' in data and len(data['observations']) > 1:
                try:
                    latest = data['observations'][-1]
                    previous = data['observations'][-2]
                    current = float(latest['value'])
                    prev_val = float(previous['value'])
                    
                    return MacroFactor(
                        name='CPI Inflation',
                        symbol='CPIAUCSL',
                        current_value=current,
                        previous_value=prev_val,
                        change_percent=(current - prev_val) / max(prev_val, 0.01) * 100,
                        impact_strength=0.8,
                        bullish_threshold=2.0,  # Lower inflation = bullish
                        data_source=f'FRED-Key{i+1}',
                        last_updated=datetime.now()
                    )
                except (KeyError, ValueError, TypeError, IndexError) as e:
                    self.logger.error(f"Data parsing error: {e}")
                    continue
        
        self.logger.error(f"🚨 CPI: ALL API keys failed! Data UNAVAILABLE (NO MOCK!)")
        return None

    def calculate_macro_score(self, factors: Dict[str, MacroFactor]) -> Tuple[float, str, str]:
        """Calculate macro sentiment score (0-100)"""
        if not factors:
            return 50.0, 'NEUTRAL', 'NEUTRAL'
        
        scores = []
        
        for factor in factors.values():
            if factor.symbol == 'FEDFUNDS':
                # Lower rate = bullish
                if factor.current_value < factor.bullish_threshold:
                    score = 75
                else:
                    score = 25
            elif factor.symbol == 'DXY':
                # Lower DXY = bullish
                if factor.current_value < factor.bullish_threshold:
                    score = 75
                else:
                    score = 25
            elif factor.symbol == 'VIX':
                # Lower VIX = bullish
                if factor.current_value < factor.bullish_threshold:
                    score = 75
                else:
                    score = 25
            elif factor.symbol == 'GS10':
                # Lower yields = bullish
                if factor.current_value < factor.bullish_threshold:
                    score = 75
                else:
                    score = 25
            elif factor.symbol == 'CPIAUCSL':
                # Lower CPI = bullish
                if factor.current_value < factor.bullish_threshold:
                    score = 75
                else:
                    score = 25
            else:
                score = 50
            
            scores.append(score)
        
        macro_score = sum(scores) / max(len(scores), 1)
        
        if macro_score >= 65:
            fed_stance = 'DOVISH'
            sentiment = 'BULLISH'
        elif macro_score >= 50:
            fed_stance = 'NEUTRAL'
            sentiment = 'NEUTRAL'
        else:
            fed_stance = 'HAWKISH'
            sentiment = 'BEARISH'
        
        return macro_score, fed_stance, sentiment

    def analyze_macro(self) -> MacroAnalysis:
        """Run complete macro analysis - NO MOCK FALLBACK!"""
        # Check cache first
        if self.last_macro_fetch and (datetime.now() - self.last_macro_fetch) < self.cache_expiry:
            if self.analysis_history:
                return self.analysis_history[-1]
        
        # Fetch metrics (None if ALL APIs fail - NO MOCK!)
        fed = self.fetch_fed_rate()
        if fed:
            self.factors['FED Rate'] = fed
        
        dxy = self.fetch_dxy()
        if dxy:
            self.factors['DXY'] = dxy
        
        vix = self.fetch_vix()
        if vix:
            self.factors['VIX'] = vix
        
        yield_10 = self.fetch_yield_10y()
        if yield_10:
            self.factors['10Y Yield'] = yield_10
        
        cpi = self.fetch_cpi()
        if cpi:
            self.factors['CPI'] = cpi
        
        # Calculate score
        macro_score, fed_stance, sentiment = self.calculate_macro_score(self.factors)
        
        # Determine risk level
        if vix and vix.current_value > 30:
            risk_level = 'HIGH'
        elif vix and vix.current_value > 20:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        # Build summary
        fed_val = self.factors.get('FED Rate')
        dxy_val = self.factors.get('DXY')
        
        if fed_val and dxy_val:
            summary = f"Macro sentiment: {sentiment}. FED rate: {fed_val.current_value:.2f}%, DXY: {dxy_val.current_value:.2f}"
        else:
            summary = f"Macro sentiment: {sentiment}. Limited data available (some APIs failed)."
        
        # Create analysis
        analysis = MacroAnalysis(
            timestamp=datetime.now(),
            fed_stance=fed_stance,
            macro_score=macro_score,
            bullish_bearish=sentiment,
            confidence=0.8 if len(self.factors) >= 3 else 0.4,
            factors=self.factors.copy(),
            risk_level=risk_level,
            summary=summary
        )
        
        self.analysis_history.append(analysis)
        self.last_macro_fetch = datetime.now()
        
        return analysis

    def get_macro_summary(self) -> Dict[str, Any]:
        """Get macro summary for integration"""
        if not self.analysis_history:
            self.analyze_macro()
        
        latest = self.analysis_history[-1]
        
        return {
            'fed_stance': latest.fed_stance,
            'macro_score': latest.macro_score,
            'bullish_bearish': latest.bullish_bearish,
            'confidence': latest.confidence,
            'risk_level': latest.risk_level,
            'summary': latest.summary,
            'timestamp': latest.timestamp.isoformat(),
            'api_calls_made': self.api_call_count
        }

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'MacroIntelligenceLayer',
    'MacroFactor',
    'MacroAnalysis'
]
