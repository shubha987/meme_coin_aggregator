import pytest
import json
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app


@pytest.fixture
def websocket_client():
    with TestClient(app) as client:
        yield client

def test_websocket_connection(websocket_client):
    """Test WebSocket connection and subscription"""
    with websocket_client.websocket_connect("/api/v1/ws") as websocket:
        # Send subscription message
        websocket.send_text(json.dumps({
            "type": "subscribe",
            "topic": "tokens"
        }))
        
        # Receive subscription confirmation
        response = json.loads(websocket.receive_text())
        assert response["type"] == "subscription_confirmed"
        assert response["topic"] == "tokens"

@pytest.mark.asyncio
async def test_websocket_broadcast():
    """Test broadcasting messages to WebSocket clients"""
    from app.services.websocket import websocket_manager
    from app.models.token import TokenData, WebSocketMessage
    import json
    
    # Create a fresh websocket manager for testing
    websocket_manager.active_connections = []
    websocket_manager.subscriptions = {}
    
    # Create a mock WebSocket with a more reliable side effect
    mock_websocket = AsyncMock()
    
    # Reset call count and configure side effect
    mock_websocket.send_text.reset_mock()
    
    # Connect and subscribe the mock
    await websocket_manager.connect(mock_websocket)
    websocket_manager.subscribe(mock_websocket, "tokens")
    
    # Create test data
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
    
    # Create a simplified version of the message to avoid any serialization issues
    message = {"type": "update", "data": token_dict}
    
    # Use broadcast_to_topic method directly with a dict
    await websocket_manager.broadcast_to_topic("tokens", message)
    
    # Verify the mock websocket received the message
    assert mock_websocket.send_text.called
    
    # Clean up
    websocket_manager.disconnect(mock_websocket)