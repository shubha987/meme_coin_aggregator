import pytest
import json
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from unittest.mock import patch, MagicMock
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
    
    # Create a mock WebSocket
    mock_websocket = MagicMock()
    
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
    
    # Create WebSocketMessage with a dict
    message = WebSocketMessage(type="update", data=token_dict)
    
    # Use the method name that matches your implementation
    await websocket_manager.broadcast_to_topic("tokens", message.model_dump())
    
    # Verify the mock websocket received the message
    mock_websocket.send_text.assert_called_once()
    
    # Clean up
    websocket_manager.disconnect(mock_websocket)