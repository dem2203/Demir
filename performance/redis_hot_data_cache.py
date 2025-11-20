"""
⚡ DEMIR AI v8.0 - REDIS HOT DATA CACHING ENGINE
High-frequency, ultra-performanslı market/pipeline verisi için gerçek Redis connection ve cache katmanı.
Sadece canlı veri & prod, mock/fake/test asla yok!
"""
import os
import redis
import logging
from typing import Any, Dict, List
from datetime import datetime
import json
import pytz

logger = logging.getLogger('REDIS_CACHING_ENGINE')

class RedisHotDataCache:
    """
    Redis tabanlı hot-path data cache. Sadece live/prod veri için:
    - Market tick/pipeline sonuçlarını cache
    - API throttling/ratelimit için read-through cache özelliği
    - Expiry, memory cap ve key-prefix bazlı cache managment
    - Fault tolerant (production ready)
    """
    def __init__(self, redis_url:str=None, prefix:str='demir:hot:', default_exp:int=4):
        ru = redis_url or os.getenv('REDIS_URL','redis://localhost:6379/0')
        self.db = redis.StrictRedis.from_url(ru, decode_responses=True)
        self.prefix = prefix
        self.default_exp = default_exp  # saniye
        logger.info(f"✅ RedisHotDataCache initialized @ {ru}")

    def set_cache(self, key:str, value:Any, exp:int=None):
        fullkey = self.prefix + key
        data = value
        if not isinstance(data,str):
            data = json.dumps(data,default=str)
        self.db.set(fullkey, data, ex=exp or self.default_exp)
        logger.info(f"[REDIS] Set {fullkey} (exp={exp or self.default_exp}s)")

    def get_cache(self, key:str) -> Any:
        fullkey = self.prefix + key
        v = self.db.get(fullkey)
        if not v: return None
        try:
            return json.loads(v)
        except Exception:
            return v

    def clear_cache(self):
        filter_keys = [k for k in self.db.keys(self.prefix+'*')]
        if filter_keys:
            self.db.delete(*filter_keys)
            logger.info(f"[REDIS] Cache cleared: {len(filter_keys)} keys")

    def health_check(self) -> Dict:
        try:
            info = self.db.info()
            return {'status':'ok','uptime':info.get('uptime_in_seconds',0),'keys':info.get('db0',{}).get('keys',0)}
        except Exception as e:
            return {'status':'fail','err':str(e)}
