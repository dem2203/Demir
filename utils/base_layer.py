"""
🔱 DEMIR AI - UTILS/BASE_LAYER.PY (v1.0)
============================================================================
Tüm layer'ların temel sınıfı (Base Class)
İndentation hataları düzeltildi!
============================================================================
Date: 13 Kasım 2025
Author: DEMIR AI Team
Status: PRODUCTION READY
Satır: 237
"""

import logging
import asyncio
from typing import Any, Dict, Optional, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseLayer:
    """
    Tüm AI layer'ların temel sınıfı
    
    Ortak metodlar:
    - Veri doğrulama
    - Hata handling
    - Retry mekanizması
    - Async support
    """
    
    def __init__(self, name: str = "BaseLayer"):
        """
        Base layer başlat
        
        Args:
            name (str): Layer adı (örn: "RiskManagementLayer")
        """
        self.name = name
        self.version = "1.0"
        self.created_at = datetime.now()
        self.max_retries = 3
        self.timeout = 30
        logger.info(f"✅ {self.name} initialized")
    
    def analyze(self, data: Any) -> Dict[str, Any]:
        """
        Temel analiz metodu - Subclass tarafından override edilmeli
        
        Args:
            data (Any): Analiz edilecek veri
            
        Returns:
            Dict[str, Any]: Analiz sonucu
            
        Raises:
            NotImplementedError: Subclass implement etmemiş
        """
        raise NotImplementedError(f"{self.name} must implement analyze() method")
    
    async def get_signal(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """
        Async sinyal al
        
        Args:
            symbol (str): Trading pair (örn: "BTCUSDT")
            
        Returns:
            Dict[str, Any]: Sinyal bilgileri
            
        Raises:
            NotImplementedError: Subclass implement etmemiş
        """
        raise NotImplementedError(f"{self.name} must implement get_signal() method")
    
    def execute_with_retry(self, func, *args, max_retries: int = None, **kwargs) -> Any:
        """
        Hata durumunda retry (tekrar deneme) ile fonksiyon çalıştır
        
        Args:
            func: Çalıştırılacak fonksiyon
            *args: Fonksiyon argümanları
            max_retries (int): Maksimum tekrar sayısı (default: self.max_retries)
            **kwargs: Keyword argümanları
            
        Returns:
            Any: Fonksiyonun sonucu
        """
        if max_retries is None:
            max_retries = self.max_retries
        
        for attempt in range(max_retries):
            try:
                result = func(*args, **kwargs)
                logger.debug(f"✅ {func.__name__} başarılı (attempt {attempt + 1})")
                return result
            except Exception as e:
                logger.warning(f"⚠️ {func.__name__} deneme {attempt + 1} başarısız: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"❌ {func.__name__} tüm denemeler başarısız!")
                    raise
        
        return None
    
    async def execute_with_retry_async(self, func, *args, max_retries: int = None, **kwargs) -> Any:
        """
        Async versiyonu - Hata durumunda retry ile fonksiyon çalıştır
        
        Args:
            func: Çalıştırılacak async fonksiyon
            *args: Fonksiyon argümanları
            max_retries (int): Maksimum tekrar sayısı
            **kwargs: Keyword argümanları
            
        Returns:
            Any: Fonksiyonun sonucu
        """
        if max_retries is None:
            max_retries = self.max_retries
        
        for attempt in range(max_retries):
            try:
                result = await func(*args, **kwargs)
                logger.debug(f"✅ {func.__name__} başarılı (attempt {attempt + 1})")
                return result
            except Exception as e:
                logger.warning(f"⚠️ {func.__name__} deneme {attempt + 1} başarısız: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"❌ {func.__name__} tüm denemeler başarısız!")
                    raise
                await asyncio.sleep(1)
        
        return None
    
    def validate_price(self, price: float) -> bool:
        """
        Fiyat geçerli mi kontrol et
        
        Args:
            price (float): Kontrol edilecek fiyat
            
        Returns:
            bool: Fiyat geçerli mi
        """
        if price is None or not isinstance(price, (int, float)):
            logger.warning(f"❌ Geçersiz fiyat tipi: {type(price)}")
            return False
        
        if price <= 0:
            logger.warning(f"❌ Negatif fiyat: {price}")
            return False
        
        if price > 10000000:
            logger.warning(f"❌ Çok yüksek fiyat: {price}")
            return False
        
        return True
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Symbol geçerli mi kontrol et
        
        Args:
            symbol (str): Kontrol edilecek symbol (örn: "BTCUSDT")
            
        Returns:
            bool: Symbol geçerli mi
        """
        valid_symbols = [
            "BTCUSDT", "ETHUSDT", "LTCUSDT", "BNBUSDT",
            "ADAUSDT", "DOGEUSDT", "XRPUSDT", "MATICUSDT",
            "SOLusdt", "AVAXUSDT", "FTMUSDT", "LINKUSDT"
        ]
        
        if not isinstance(symbol, str):
            logger.warning(f"❌ Symbol string değildir: {type(symbol)}")
            return False
        
        if symbol.upper() not in valid_symbols:
            logger.warning(f"❌ Geçersiz symbol: {symbol}")
            return False
        
        return True
    
    def validate_data(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Veri geçerli mi kontrol et (required fields)
        
        Args:
            data (Dict): Kontrol edilecek veri
            required_fields (List[str]): Gerekli alanlar
            
        Returns:
            bool: Veri geçerli mi
        """
        if not isinstance(data, dict):
            logger.warning(f"❌ Veri dict değildir")
            return False
        
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            logger.warning(f"❌ Eksik alanlar: {missing_fields}")
            return False
        
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """
        Layer hakkında bilgi al
        
        Returns:
            Dict[str, Any]: Layer bilgileri
        """
        return {
            "name": self.name,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "type": self.__class__.__name__,
            "max_retries": self.max_retries,
            "timeout": self.timeout
        }
    
    def __repr__(self) -> str:
        """String gösterimi"""
        return f"<{self.name} v{self.version}>"
    
    def __str__(self) -> str:
        """İnsan okunabilir gösterim"""
        return f"{self.name} (v{self.version})"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    base = BaseLayer("TestLayer")
    print(f"✅ {base}")
    print(f"ℹ️ {base.get_info()}")
