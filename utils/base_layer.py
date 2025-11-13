"""
UTILS - BASE LAYER (FIXED)
Base sınıfı - Tüm layer'lar bunu inherit eder
İndentation hataları düzeltildi!
"""

import logging
import asyncio
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseLayer:
    """
    Tüm AI layer'ların temel sınıfı
    Ortak metodlar ve error handling sağlar
    """
    
    def __init__(self, name: str = "BaseLayer"):
        """
        Base layer başlat
        
        Args:
            name: Layer adı (örn: "RiskManagementLayer")
        """
        self.name = name
        self.version = "1.0"
        self.created_at = datetime.now()
        logger.info(f"✅ {self.name} initialized")
    
    def analyze(self, data: Any) -> Dict[str, Any]:
        """
        Temel analiz metodu - Subclass tarafından override edilmeli
        
        Args:
            data: Analiz edilecek veri
            
        Returns:
            dict: Analiz sonucu
            
        Raises:
            NotImplementedError: Subclass implement etmemiş
        """
        raise NotImplementedError(f"{self.name} must implement analyze() method")
    
    async def get_signal(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """
        Async sinyal al
        
        Args:
            symbol: Trading pair (örn: "BTCUSDT")
            
        Returns:
            dict: Sinyal bilgileri
        """
        raise NotImplementedError(f"{self.name} must implement get_signal() method")
    
    def execute_with_retry(self, func, *args, max_retries: int = 3, **kwargs) -> Any:
        """
        Hata durumunda retry (tekrar deneme) ile fonksiyon çalıştır
        
        Args:
            func: Çalıştırılacak fonksiyon
            *args: Fonksiyon argümanları
            max_retries: Maksimum tekrar sayısı
            **kwargs: Keyword argümanları
            
        Returns:
            Fonksiyonun sonucu
        """
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
                continue
        
        return None
    
    async def execute_with_retry_async(self, func, *args, max_retries: int = 3, **kwargs) -> Any:
        """
        Async versiyonu - Hata durumunda retry ile fonksiyon çalıştır
        
        Args:
            func: Çalıştırılacak async fonksiyon
            *args: Fonksiyon argümanları
            max_retries: Maksimum tekrar sayısı
            **kwargs: Keyword argümanları
            
        Returns:
            Fonksiyonun sonucu
        """
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
                await asyncio.sleep(1)  # 1 saniye bekle
                continue
        
        return None
    
    def validate_price(self, price: float) -> bool:
        """
        Fiyat geçerli mi kontrol et
        
        Args:
            price: Kontrol edilecek fiyat
            
        Returns:
            bool: Fiyat geçerli mi
        """
        if price is None or price <= 0:
            logger.warning(f"❌ Geçersiz fiyat: {price}")
            return False
        return True
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Symbol geçerli mi kontrol et
        
        Args:
            symbol: Kontrol edilecek symbol (örn: "BTCUSDT")
            
        Returns:
            bool: Symbol geçerli mi
        """
        valid_symbols = [
            "BTCUSDT", "ETHUSDT", "LTCUSDT", "BNBUSDT",
            "ADAUSDT", "DOGEUSDT", "XRPUSDT", "MATICUSDT"
        ]
        
        if symbol not in valid_symbols:
            logger.warning(f"❌ Geçersiz symbol: {symbol}")
            return False
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """
        Layer hakkında bilgi al
        
        Returns:
            dict: Layer bilgileri
        """
        return {
            "name": self.name,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "type": self.__class__.__name__
        }
    
    def __repr__(self) -> str:
        """String gösterimi"""
        return f"<{self.name} v{self.version}>"
    
    def __str__(self) -> str:
        """İnsan okunabilir gösterim"""
        return f"{self.name} (v{self.version})"


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Base layer test
    base = BaseLayer("TestLayer")
    print(f"✅ {base}")
    print(f"ℹ️ {base.get_info()}")
