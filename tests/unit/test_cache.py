import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.core.cache import CacheManager

@pytest.fixture
def cache_manager():
    return CacheManager()

@pytest.mark.asyncio
async def test_cache_connect_disconnect(cache_manager):
    """Test connecting and disconnecting from Redis"""
    # Use AsyncMock instead of MagicMock for async functions
    with patch('aioredis.from_url', return_value=AsyncMock()) as mock_from_url:
        await cache_manager.connect()
        mock_from_url.assert_called_once()
        assert cache_manager.redis is not None
        
        await cache_manager.disconnect()
        cache_manager.redis.close.assert_called_once()
        cache_manager.redis.wait_closed.assert_called_once()

@pytest.mark.asyncio
async def test_cache_get_set(cache_manager):
    """Test getting and setting cache values"""
    # Use AsyncMock for redis
    mock_redis = AsyncMock()
    cache_manager.redis = mock_redis
    
    # Test set
    mock_redis.set.return_value = True
    await cache_manager.set("test_key", "test_value", 30)
    mock_redis.set.assert_called_once_with("test_key", '"test_value"', ex=30)
    
    # Test get
    mock_redis.get.return_value = '"test_value"'
    value = await cache_manager.get("test_key")
    mock_redis.get.assert_called_once_with("test_key")
    assert value == "test_value"

@pytest.mark.asyncio
async def test_cache_get_nonexistent(cache_manager):
    """Test getting a nonexistent cache key"""
    mock_redis = MagicMock()
    cache_manager.redis = mock_redis
    
    mock_redis.get.return_value = None
    value = await cache_manager.get("nonexistent_key")
    mock_redis.get.assert_called_with("nonexistent_key")
    assert value is None