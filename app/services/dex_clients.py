# app/services/dex_clients.py
import httpx
import asyncio
from typing import List, Dict, Any
from app.utils.retry import retry_with_backoff
from app.core.cache import cache_manager

class DexScreenerClient:
    def __init__(self):
        self.base_url = "https://api.dexscreener.com"
        self.rate_limit = 300  # requests per minute
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    async def get_token_data(self, token_address: str) -> Dict[str, Any]:
        cache_key = f"dexscreener:token:{token_address}"
        cached_data = await cache_manager.get(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.base_url}/latest/dex/tokens/{token_address}"
        response = await self.client.get(url)
        response.raise_for_status()
        
        data = response.json()
        await cache_manager.set(cache_key, data, ttl=30)
        return data
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    async def search_tokens(self, query: str) -> Dict[str, Any]:
        cache_key = f"dexscreener:search:{query}"
        cached_data = await cache_manager.get(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.base_url}/latest/dex/search"
        params = {"q": query}
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        await cache_manager.set(cache_key, data, ttl=30)
        return data

class JupiterPriceClient:
    def __init__(self):
        self.base_url = "https://price.jup.ag"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    async def get_prices(self, token_ids: List[str]) -> Dict[str, Any]:
        cache_key = f"jupiter:prices:{':'.join(sorted(token_ids))}"
        cached_data = await cache_manager.get(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.base_url}/v4/price"
        params = {"ids": ",".join(token_ids)}
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        await cache_manager.set(cache_key, data, ttl=30)
        return data
