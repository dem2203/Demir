"""
ERROR HANDLING FOUNDATION
- Tüm layer'lar bu sınıftan inherit eder
- Otomatik retry + exponential backoff
- Real veri fallback (İkinci kaynaktan real data çek)
- Unified error logging
"""

import asyncio
import logging
from typing import Any, Callable, Dict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class LayerStatus(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"

class BaseLayer:
    def __init__(self, layer_name: str, max_retries: int = 3):
        self.name = layer_name
        self.quality_score = 100.0
        self.last_error = None
        self.error_count = 0
        self.max_retries = max_retries
        self.status = LayerStatus.HEALTHY
        self.last_execution_time = None
        self.created_at = datetime.now()
    
    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Dict:
        """
        Retry logic + REAL data fallback (İkinci API kaynağından real veri)
        
        ⚠️ KURALLARA UYUM:
        - Fallback = ikinci real API kaynağından veri çek
        - ASLA fake/mock data döndürme
        - Her zaman real data verify et
        """
        
        start_time = datetime.now()
        
        for attempt in range(self.max_retries):
            try:
                result = await func(*args, **kwargs)
                
                if self.validate_result(result):
                    self.quality_score = 100.0
                    self.status = LayerStatus.HEALTHY
                    self.consecutive_failures = 0
                    self.last_error = None
                    
                    self.last_execution_time = (datetime.now() - start_time).total_seconds()
                    logger.debug(f"✅ {self.name}: Success (attempt {attempt+1})")
                    
                    return result
                else:
                    self.quality_score = 40.0
                    self.status = LayerStatus.DEGRADED
                    
            except asyncio.TimeoutError:
                self.last_error = "Timeout - retrying..."
                logger.warning(f"⏱️ {self.name}: Timeout (attempt {attempt+1}/{self.max_retries})")
                
            except Exception as e:
                self.last_error = str(e)
                self.error_count += 1
                logger.warning(f"❌ {self.name}: Error - {e}")
            
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
        
        # TÜM retry'lar başarısız = fallback'e geç
        # ⚠️ FALLBACK = İKİNCİ REAL API KAYNAĞINDAN VERİ ÇEK
        return await self.get_real_data_fallback()
    
    async def get_real_data_fallback(self) -> Dict:
        """
        REAL DATA FALLBACK
        Birinci API fail olursa, ikinci real API kaynağından veri çek
        
        Örn: Binance fail → CoinGecko/Kraken'den real veri
        ASLA mock data değil!
        """
        
        try:
            # Alternatif real API kaynağından veri çek
            logger.warning(f"⚠️ {self.name}: Primary source failed, using secondary real API...")
            
            # İkinci kaynaktan real data al
            fallback_data = await self._fetch_from_backup_real_source()
            
            if fallback_data and self.validate_result(fallback_data):
                logger.info(f"✅ {self.name}: Real data retrieved from backup source")
                self.quality_score = 75.0  # Slightly degraded kalite
                return fallback_data
            else:
                # İkinci kaynak da başarısız
                self.quality_score = 0
                self.status = LayerStatus.FAILED
                logger.critical(f"🚨 {self.name}: BOTH primary and backup sources failed!")
                
                return {
                    'available': False,
                    'signal': 'NEUTRAL',
                    'confidence': 0.0,
                    'error': 'No real data available from any source',
                    'layer': self.name,
                    'status': self.status.value
                }
        
        except Exception as e:
            logger.critical(f"🚨 {self.name}: Fallback error - {e}")
            return {
                'available': False,
                'signal': 'NEUTRAL',
                'error': str(e),
                'layer': self.name
            }
    
    async def _fetch_from_backup_real_source(self) -> Dict:
        """İkinci real API kaynağından veri çek"""
        # CoinGecko, Kraken, veya başka real exchange API'si
        # Bu fonksiyonu override et subclass'ta
        raise NotImplementedError("Override in subclass")
    
    def validate_result(self, result: Any) -> bool:
        """Sonuç real mi, valid mi?"""
        if result is None:
            return False
        
        if isinstance(result, dict):
            if 'error' in result and result['error'] is not None:
                return False
        
        return True
