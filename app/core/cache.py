# app/core/cache.py
import aioredis
import json
from typing import Optional, Any
from app.config import settings

class CacheManager:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self):
        self.redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def get(self, key: str) -> Optional[Any]:
        if not self.redis:
            return None
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 30):
        if not self.redis:
            return
        try:
            await self.redis.setex(key, ttl, json.dumps(value, default=str))
        except Exception:
            pass
    
    async def delete(self, pattern: str):
        if not self.redis:
            return
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

cache_manager = CacheManager()

async def startup_event():
    await cache_manager.connect()
