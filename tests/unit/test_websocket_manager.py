import pytest
import json
from unittest.mock import MagicMock, patch
from app.services.websocket import WebSocketManager
from app.models.token import TokenData, WebSocketMessage

@pytest.fixture
def websocket_manager():
    return WebSocketManager()

@pytest.mark.asyncio  # Add asyncio mark
async def test_websocket_connection(websocket_manager):
    """Test connecting and disconnecting WebSockets"""
    # Mock websocket
    websocket = MagicMock()
    
    # Test connect (properly await)
    await websocket_manager.connect(websocket)
    assert websocket in websocket_manager.active_connections
    
    # Test disconnect
    websocket_manager.disconnect(websocket)
    assert websocket not in websocket_manager.active_connections

@pytest.mark.asyncio  # Add asyncio mark
async def test_websocket_subscription(websocket_manager):
    """Test WebSocket topic subscription"""
    # Mock websocket
    websocket = MagicMock()
    await websocket_manager.connect(websocket)
    
    # Test subscribe (use subscriptions instead of topics)
    websocket_manager.subscribe(websocket, "tokens")
    assert websocket in websocket_manager.subscriptions["tokens"]
    
    # Test unsubscribe
    websocket_manager.unsubscribe(websocket, "tokens")
    assert websocket not in websocket_manager.subscriptions["tokens"]

@pytest.mark.asyncio
async def test_broadcast_message(websocket_manager):
    """Test broadcasting messages to WebSocket subscribers"""
    # Create mock websockets
    websocket1 = MagicMock()
    websocket2 = MagicMock()
    
    # Connect and subscribe
    websocket_manager.connect(websocket1)
    websocket_manager.connect(websocket2)
    websocket_manager.subscribe(websocket1, "tokens")
    websocket_manager.subscribe(websocket2, "tokens")
    
    # Create test message
    token = TokenData(
        token_address="test_address",
        token_name="Test Token",
        token_ticker="TEST",
        price_sol=0.1,
        market_cap_sol=100,
        volume_sol=1000,
        liquidity_sol=500,
        transaction_count=100,
        price_1hr_change=5.0,
        protocol="Test Protocol"
    )
    
    message = WebSocketMessage(type="update", data=token)
    
    # Broadcast message
    await websocket_manager.broadcast(message, "tokens")
    
    # Verify both websockets received the message
    expected_json = json.dumps(message.model_dump())
    websocket1.send_text.assert_called_once_with(expected_json)
    websocket2.send_text.assert_called_once_with(expected_json)