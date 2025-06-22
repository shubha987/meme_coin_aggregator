import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.core.cache import CacheManager

@pytest.fixture
def cache_manager():
    return CacheManager()

@pytest.mark.asyncio
async def test_cache_connect_disconnect(cache_manager):
    """Test connecting and disconnecting from Redis"""
    # Create a mock Redis client
    mock_redis = AsyncMock()
    
    # Create a function that returns the mock when awaited
    async def mock_from_url_func(*args, **kwargs):
        return mock_redis
    
    # Patch the function to return our custom async function
    with patch('aioredis.from_url', mock_from_url_func):
        await cache_manager.connect()
        assert cache_manager.redis is mock_redis
        
        await cache_manager.disconnect()
        mock_redis.close.assert_called_once()
        mock_redis.wait_closed.assert_called_once()

@pytest.mark.asyncio
async def test_cache_get_set(cache_manager):
    """Test getting and setting cache values"""
    # Create a mock Redis client
    mock_redis = AsyncMock()
    cache_manager.redis = mock_redis
    
    # Test set
    await cache_manager.set("test_key", "test_value", 30)
    # Use setex if that's what your implementation uses
    mock_redis.setex.assert_called_once_with("test_key", 30, '"test_value"')
    
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