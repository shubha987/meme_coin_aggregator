import pytest
from unittest.mock import AsyncMock, patch
import asyncio
from app.utils.retry import retry

@pytest.mark.asyncio
async def test_retry_success_first_attempt():
    """Test retry decorator when function succeeds on first attempt"""
    mock_func = AsyncMock(return_value="success")
    
    # Apply the retry decorator to the mock
    decorated_func = retry(max_retries=3, base_delay=0.1)(mock_func)
    
    # Call the decorated function
    result = await decorated_func("arg1", kwarg1="kwarg1")
    
    # Verify function was called exactly once
    assert mock_func.call_count == 1
    mock_func.assert_called_once_with("arg1", kwarg1="kwarg1")
    assert result == "success"

@pytest.mark.asyncio
async def test_retry_success_after_retries():
    """Test retry decorator when function succeeds after failures"""
    # Mock that fails twice then succeeds
    mock_func = AsyncMock(side_effect=[Exception("Error 1"), Exception("Error 2"), "success"])
    
    # Apply the retry decorator to the mock
    decorated_func = retry(max_retries=3, base_delay=0.01)(mock_func)
    
    # Call the decorated function
    result = await decorated_func("arg1")
    
    # Verify function was called exactly three times
    assert mock_func.call_count == 3
    assert result == "success"

@pytest.mark.asyncio
async def test_retry_all_attempts_fail():
    """Test retry decorator when all attempts fail"""
    # Mock that always fails
    mock_func = AsyncMock(side_effect=Exception("Always fails"))
    
    # Apply the retry decorator to the mock
    decorated_func = retry(max_retries=2, base_delay=0.01)(mock_func)
    
    # Call the decorated function and expect exception
    with pytest.raises(Exception, match="Always fails"):
        await decorated_func()
    
    # Verify function was called exactly three times (initial + 2 retries)
    assert mock_func.call_count == 3