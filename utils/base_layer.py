"""
BASE LAYER CLASS - FOUNDATION
Tüm layer'ların kalıtım aldığı temel sınıf
Unified error handling + Real data fallback (NO MOCK!)

⚠️ GOLDEN RULE:
- Fallback = İkinci REAL API kaynağından veri çek
- ASLA mock/fake/hardcoded data
- Tüm hesaplamalar gerçek değerler üzerinde
"""

import asyncio
import logging
from typing import Any, Callable, Dict, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class LayerStatus(Enum):
    """Layer durumları"""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    RECOVERING = "RECOVERING"


class BaseLayer:
    """
    Tüm layer'ların kalıtım aldığı base class
    
    Features:
    - Unified error handling
    - Automatic retry (exponential backoff)
    - Real data fallback (ikinci API kaynağı)
    - Quality scoring (0-100)
    - Health monitoring
    - NO MOCK DATA - Golden rule!
    """
    
    def __init__(self, layer_name: str, max_retries: int = 3):
        """
        Initialize base layer
        
        Args:
            layer_name: Layer adı (örn: 'RSI_Layer')
            max_retries: Maximum retry attempts
        """
        self.name = layer_name
        self.quality_score = 100.0
        self.last_error = None
        self.error_count = 0
        self.max_retries = max_retries
        self.status = LayerStatus.HEALTHY
        self.last_execution_time = None
        self.consecutive_failures = 0
        self.created_at = datetime.now()
    
    async def execute_with_retry(self, 
                                func: Callable, 
                                *args, 
                                **kwargs) -> Dict:
        """
        Retry logic + REAL data fallback
        
        Akış:
        1. Primary API'dan veri çek
        2. Fail olursa, 2. kez retry (exponential backoff)
        3. 3. kez retry
        4. Hepsi fail = REAL backup API'dan çek
        5. Hepsi fail = NEUTRAL sinyal (hiç mock data DEĞİL!)
        
        Args:
            func: Çalıştırılacak async fonksiyon
            *args: Positional args
            **kwargs: Keyword args
        
        Returns:
            Dict: Sonuç veya fallback (REAL data fallback)
        """
        
        start_time = datetime.now()
        
        for attempt in range(self.max_retries):
            try:
                # Primary kaynaktan veri çek
                result = await func(*args, **kwargs)
                
                # Sonuç gerçek mi, valid mi?
                if self.validate_result(result):
                    self.quality_score = 100.0
                    self.status = LayerStatus.HEALTHY
                    self.consecutive_failures = 0
                    self.last_error = None
                    
                    self.last_execution_time = (datetime.now() - start_time).total_seconds()
                    logger.debug(f"✅ {self.name}: Success (attempt {attempt+1})")
                    
                    return result
                else:
                    # Veri geçersiz
                    self.quality_score = 40.0
                    self.status = LayerStatus.DEGRADED
                    self.last_error = "Invalid result data"
                    logger.warning(f"⚠️ {self.name}: Invalid result data")
                    
            except asyncio.TimeoutError:
                self.last_error = "Timeout"
                self.error_count += 1
                logger.warning(f"⏱️ {self.name}: Timeout (attempt {attempt+1}/{self.max_retries})")
                
            except Exception as e:
                self.last_error = str(e)
                self.error_count += 1
                logger.warning(f"❌ {self.name}: Error - {e} (attempt {attempt+1}/{self.max_retries})")
            
            # Retry öncesi bekle (exponential backoff)
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                logger.debug(f"🔄 {self.name}: Retry in {wait_time}s...")
                await asyncio.sleep(wait_time)
        
        # Tüm retry'lar başarısız = fallback'e geç
        logger.warning(f"⚠️ {self.name}: All retries failed, using REAL backup source...")
        
        return await self.get_real_data_fallback()
    
    async def get_real_data_fallback(self) -> Dict:
    """
    REAL DATA FALLBACK
    ⚠️ ASLA mock data DEĞİL!
    
    Uses:
    1. Binance (Primary)
    2. Coinbase (Secondary)
    3. CMC (Tertiary)
    4. Bybit Futures (if futures)
    5. ERROR if all fail (not fake!)
    """
    
    try:
        from utils.multi_api_orchestrator import MultiAPIOrchestrator
        
        orchestrator = MultiAPIOrchestrator()
        
        # Sistemi futures data istiyorsa
        futures = self.name.lower().find('futures') != -1
        
        # Get real data
        real_data = await orchestrator.get_price('BTC', futures=futures)
        
        if real_data and real_data.get('valid'):
            self.quality_score = 75.0
            self.status = LayerStatus.DEGRADED
            logger.info(f"✅ Real data from {real_data['source']}")
            return real_data
        else:
            # No real data available - return NEUTRAL (not fake!)
            self.quality_score = 0
            self.status = LayerStatus.FAILED
            
            return {
                'available': False,
                'signal': 'NEUTRAL',
                'confidence': 0.0,
                'error': real_data.get('error', 'No real data available'),
                'layer': self.name
            }
    
    except Exception as e:
        logger.critical(f"Fallback error: {e}")
        return {
            'available': False,
            'signal': 'NEUTRAL',
            'error': str(e)
        }
    
    async def _fetch_from_backup_real_source(self) -> Optional[Dict]:
        """
        Second REAL API kaynağından veri çek
        
        Örn: Binance fail → CoinGecko'dan real veri
        
        OVERRIDE et subclass'ta!
        
        Returns:
            Dict: REAL veri veya None
        """
        
        # Her layer'da override etmek gerekli
        logger.debug(f"⚠️ {self.name}: No backup source configured (override in subclass)")
        return None
    
    def validate_result(self, result: Any) -> bool:
        """
        Sonucun gerçek ve valid olduğunu kontrol et
        
        Args:
            result: Validate edilecek sonuç
        
        Returns:
            bool: Valid mi?
        """
        
        if result is None:
            return False
        
        # Dict sonuç kontrolü
        if isinstance(result, dict):
            # Error var mı?
            if 'error' in result and result['error'] is not None:
                return False
            
            # Available false mı?
            if 'available' in result and not result['available']:
                return False
        
        # NaN check
        if isinstance(result, (int, float)):
            if result != result:  # NaN check
                return False
        
        return True
    
    def get_health_status(self) -> Dict:
        """
        Layer sağlık durumu
        
        Returns:
            Dict: Sağlık bilgileri
        """
        
        return {
            'name': self.name,
            'status': self.status.value,
            'quality_score': self.quality_score,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'consecutive_failures': self.consecutive_failures,
            'last_execution_time': self.last_execution_time,
            'uptime_hours': (datetime.now() - self.created_at).total_seconds() / 3600
        }
    
    async def self_recover(self):
        """
        Layer kendini kurtarma çabası
        
        Yapılacaklar:
        - Cache temizle
        - API bağlantısını resetle
        - Veri kaynağını yenile
        
        Override et subclass'ta!
        """
        
        self.status = LayerStatus.RECOVERING
        self.consecutive_failures = 0
        logger.info(f"🔧 {self.name}: Self-recovery initiated")
        
        # Default implementation
        await asyncio.sleep(5)
        self.status = LayerStatus.HEALTHY
        logger.info(f"✅ {self.name}: Self-recovery completed")
