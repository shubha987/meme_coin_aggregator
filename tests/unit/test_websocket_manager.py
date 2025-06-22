import pytest
import json
from unittest.mock import AsyncMock, patch
from app.services.websocket import WebSocketManager
from app.models.token import TokenData, WebSocketMessage

@pytest.fixture
def websocket_manager():
    return WebSocketManager()

@pytest.mark.asyncio
async def test_websocket_connection(websocket_manager):
    """Test connecting and disconnecting WebSockets"""
    # Use AsyncMock instead of MagicMock
    websocket = AsyncMock()
    
    # Test connect
    await websocket_manager.connect(websocket)
    websocket.accept.assert_called_once()
    assert websocket in websocket_manager.active_connections
    
    # Test disconnect
    websocket_manager.disconnect(websocket)
    assert websocket not in websocket_manager.active_connections

@pytest.mark.asyncio
async def test_websocket_subscription(websocket_manager):
    """Test WebSocket topic subscription"""
    # Use AsyncMock
    websocket = AsyncMock()
    await websocket_manager.connect(websocket)
    
    # Test subscribe
    websocket_manager.subscribe(websocket, "tokens")
    assert websocket in websocket_manager.subscriptions["tokens"]
    
    # Test unsubscribe
    websocket_manager.unsubscribe(websocket, "tokens")
    assert websocket not in websocket_manager.subscriptions["tokens"]

@pytest.mark.asyncio
async def test_broadcast_message(websocket_manager):
    """Test broadcasting messages to WebSocket subscribers"""
    # Use AsyncMock
    websocket1 = AsyncMock()
    websocket2 = AsyncMock()
    
    # Reset call counts
    websocket1.send_text.reset_mock()
    websocket2.send_text.reset_mock()
    
    # Connect and subscribe
    await websocket_manager.connect(websocket1)
    await websocket_manager.connect(websocket2)
    websocket_manager.subscribe(websocket1, "tokens")
    websocket_manager.subscribe(websocket2, "tokens")
    
    # Create test data as dictionary
    token_dict = {
        "token_address": "test_address",
        "token_name": "Test Token",
        "token_ticker": "TEST",
        "price_sol": 0.1,
        "market_cap_sol": 100,
        "volume_sol": 1000,
        "liquidity_sol": 500,
        "transaction_count": 100,
        "price_1hr_change": 5.0,
        "protocol": "Test Protocol"
    }
    
    # Create a simplified message
    message = {"type": "update", "data": token_dict}
    
    # Use broadcast_to_topic with dict
    await websocket_manager.broadcast_to_topic("tokens", message)
    
    # Verify both websockets received the message
    assert websocket1.send_text.called
    assert websocket2.send_text.called