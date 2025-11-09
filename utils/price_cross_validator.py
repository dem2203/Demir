"""
=============================================================================
DEMIR AI v25.0 - PRICE CROSSCHECK & DATA VALIDATOR
=============================================================================
Purpose: Binance fiyatlarını CMC, TradingView ve diğer kaynaklarla doğrula
Location: /utils/ klasörü
Integrations: live_price_monitor.py, external_data.py, telegram_alert_system.py
=============================================================================
"""

import logging
import requests
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataQuality(Enum):
    """Fiyat verisi kalitesi"""
    VALID = "✅ VALID"
    WARNING = "⚠️ WARNING"
    CRITICAL = "🔴 CRITICAL"


@dataclass
class PriceData:
    """Kaynak başına fiyat verisi"""
    source: str  # "BINANCE", "CMC", "COINGECKO", "TV"
    symbol: str
    price: float
    timestamp: str = None
    volume: float = None
    change_24h: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class CrosscheckResult:
    """Crosscheck sonuçları"""
    symbol: str
    primary_source: str  # Usually BINANCE
    primary_price: float
    crosscheck_sources: Dict[str, float]  # {"CMC": 50100, "CG": 50050}
    average_price: float
    price_variance: float  # %
    data_quality: DataQuality
    timestamp: str = None
    alert_message: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class PriceCrossValidator:
    """
    Fiyat doğrulama motoru
    
    Features:
    - Binance vs CMC vs CoinGecko karşılaştırması
    - Veri kalitesi skoru
    - Anomali tespiti (flash crash vs gerçek hareket)
    - İstatistiksel doğrulama
    """
    
    # API configurations
    BINANCE_API = "https://api.binance.com/api/v3"
    CMC_API = "https://pro-api.coinmarketcap.com/v1"
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    
    # Tolerance levels
    TOLERANCE_WARNING = 2.0  # % deviation warning threshold
    TOLERANCE_CRITICAL = 5.0  # % deviation critical threshold
    
    def __init__(self):
        self.price_history: List[CrosscheckResult] = []
        self.error_count: int = 0
    
    # ========================================================================
    # PRICE FETCHING
    # ========================================================================
    
    def get_binance_price(self, symbol: str) -> Optional[PriceData]:
        """Binance'den fiyat al"""
        try:
            # Symbol format: BTCUSDT
            url = f"{self.BINANCE_API}/ticker/24hr"
            params = {"symbol": symbol}
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            price_data = PriceData(
                source="BINANCE",
                symbol=symbol,
                price=float(data["lastPrice"]),
                volume=float(data["quoteAssetVolume"]),
                change_24h=float(data["priceChangePercent"])
            )
            logger.info(f"✅ Binance {symbol}: ${price_data.price}")
            return price_data
        
        except Exception as e:
            logger.error(f"❌ Binance API error for {symbol}: {e}")
            self.error_count += 1
            return None
    
    def get_cmc_price(self, symbol: str, api_key: str) -> Optional[PriceData]:
        """CoinMarketCap'dan fiyat al"""
        try:
            # CMC coin mapping (simplified)
            coin_id_map = {
                "BTC": 1, "ETH": 1027, "LTC": 2, "ADA": 2010,
                "SOL": 5426, "DOGE": 74, "XRP": 52, "BNB": 1839
            }
            
            base_coin = symbol.replace("USDT", "").replace("USDC", "")
            if base_coin not in coin_id_map:
                logger.warning(f"⚠️ {base_coin} not in CMC mapping")
                return None
            
            coin_id = coin_id_map[base_coin]
            url = f"{self.CMC_API}/cryptocurrency/quotes/latest"
            headers = {"X-CMC_PRO_API_KEY": api_key}
            params = {"id": coin_id, "convert": "USD"}
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            cmc_data = data["data"][str(coin_id)]["quote"]["USD"]
            
            price_data = PriceData(
                source="CMC",
                symbol=symbol,
                price=cmc_data["price"],
                change_24h=cmc_data["percent_change_24h"]
            )
            logger.info(f"✅ CMC {symbol}: ${price_data.price}")
            return price_data
        
        except Exception as e:
            logger.error(f"⚠️ CMC API error: {e}")
            return None
    
    def get_coingecko_price(self, symbol: str) -> Optional[PriceData]:
        """CoinGecko'dan fiyat al (free API)"""
        try:
            coin_id_map = {
                "BTC": "bitcoin", "ETH": "ethereum", "LTC": "litecoin",
                "ADA": "cardano", "SOL": "solana", "DOGE": "dogecoin",
                "XRP": "ripple", "BNB": "binancecoin"
            }
            
            base_coin = symbol.replace("USDT", "").replace("USDC", "")
            if base_coin not in coin_id_map:
                return None
            
            coin_id = coin_id_map[base_coin]
            url = f"{self.COINGECKO_API}/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()[coin_id]
            price_data = PriceData(
                source="COINGECKO",
                symbol=symbol,
                price=data["usd"],
                change_24h=data.get("usd_24h_change", 0)
            )
            logger.info(f"✅ CoinGecko {symbol}: ${price_data.price}")
            return price_data
        
        except Exception as e:
            logger.warning(f"⚠️ CoinGecko error: {e}")
            return None
    
    # ========================================================================
    # CROSSCHECK LOGIC
    # ========================================================================
    
    def crosscheck_price(
        self,
        symbol: str,
        cmc_api_key: Optional[str] = None
    ) -> Optional[CrosscheckResult]:
        """
        Fiyat crosscheck yap - Binance, CMC, CoinGecko karşılaştır
        
        Args:
            symbol: Trading pair (BTCUSDT)
            cmc_api_key: CMC API key (optional)
        
        Returns:
            CrosscheckResult with validation status
        """
        # Get Binance price (primary source)
        binance_price = self.get_binance_price(symbol)
        if binance_price is None:
            return None
        
        # Get secondary sources
        crosscheck_prices = {"BINANCE": binance_price.price}
        
        # CMC
        if cmc_api_key:
            cmc_price = self.get_cmc_price(symbol, cmc_api_key)
            if cmc_price:
                crosscheck_prices["CMC"] = cmc_price.price
        
        # CoinGecko (always free)
        cg_price = self.get_coingecko_price(symbol)
        if cg_price:
            crosscheck_prices["COINGECKO"] = cg_price.price
        
        # Calculate variance
        if len(crosscheck_prices) < 2:
            # Yetersiz veri
            result = CrosscheckResult(
                symbol=symbol,
                primary_source="BINANCE",
                primary_price=binance_price.price,
                crosscheck_sources={"error": "Insufficient data sources"},
                average_price=binance_price.price,
                price_variance=0.0,
                data_quality=DataQuality.WARNING,
                alert_message="⚠️ Only one data source available"
            )
            return result
        
        # Calculate statistics
        prices = list(crosscheck_prices.values())
        avg_price = sum(prices) / len(prices)
        
        # Calculate max variance
        max_variance = max(abs(p - avg_price) / avg_price * 100 for p in prices)
        
        # Determine quality
        if max_variance > self.TOLERANCE_CRITICAL:
            data_quality = DataQuality.CRITICAL
            alert_msg = f"🔴 CRITICAL: {max_variance:.2f}% variance detected!"
        elif max_variance > self.TOLERANCE_WARNING:
            data_quality = DataQuality.WARNING
            alert_msg = f"⚠️ WARNING: {max_variance:.2f}% variance"
        else:
            data_quality = DataQuality.VALID
            alert_msg = f"✅ Data valid, variance: {max_variance:.2f}%"
        
        result = CrosscheckResult(
            symbol=symbol,
            primary_source="BINANCE",
            primary_price=binance_price.price,
            crosscheck_sources={k: v for k, v in crosscheck_prices.items() if k != "BINANCE"},
            average_price=round(avg_price, 2),
            price_variance=round(max_variance, 2),
            data_quality=data_quality,
            alert_message=alert_msg
        )
        
        # Store history
        self.price_history.append(result)
        logger.info(f"\n{alert_msg}")
        logger.info(f"  Binance: ${binance_price.price} | Avg: ${avg_price:.2f}")
        
        return result
    
    def detect_flash_crash(
        self,
        symbol: str,
        threshold_percent: float = 3.0
    ) -> Tuple[bool, str]:
        """
        Flash crash algıla - birdenbire fiyat düşüşü
        
        Args:
            symbol: Trading pair
            threshold_percent: Threshold % (default 3%)
        
        Returns:
            (is_flash_crash: bool, message: str)
        """
        # Get recent history
        recent = [r for r in self.price_history if r.symbol == symbol][-10:]
        
        if len(recent) < 2:
            return False, "Insufficient history"
        
        # Calculate 24h change
        if recent[-1].primary_price <= 0:
            return False, "Invalid price data"
        
        price_change = (recent[-1].primary_price - recent[0].primary_price) / recent[0].primary_price * 100
        
        if abs(price_change) > threshold_percent:
            return True, f"🔴 Possible flash crash: {price_change:.2f}% in 24h"
        
        return False, "No flash crash detected"
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def get_validation_report(self) -> Dict:
        """Crosscheck raporu"""
        return {
            "Total checks": len(self.price_history),
            "Valid": sum(1 for r in self.price_history if r.data_quality == DataQuality.VALID),
            "Warnings": sum(1 for r in self.price_history if r.data_quality == DataQuality.WARNING),
            "Critical": sum(1 for r in self.price_history if r.data_quality == DataQuality.CRITICAL),
            "Errors": self.error_count,
            "Last check": self.price_history[-1].timestamp if self.price_history else "Never"
        }


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    validator = PriceCrossValidator()
    
    # Test crosscheck
    result = validator.crosscheck_price("BTCUSDT")
    if result:
        print(f"\n📊 Crosscheck Result:")
        print(f"   Symbol: {result.symbol}")
        print(f"   Binance: ${result.primary_price}")
        print(f"   Average: ${result.average_price}")
        print(f"   Variance: {result.price_variance}%")
        print(f"   Quality: {result.data_quality.value}")
        print(f"   {result.alert_message}")
        
        # Check for flash crash
        is_crash, msg = validator.detect_flash_crash("BTCUSDT")
        print(f"\n🔍 Flash Crash Check: {msg}")
