import pytest
from app.models.token import TokenData, WebSocketMessage

def test_token_data_model():
    """Test creating a valid token data model"""
    token = TokenData(
        token_address="576P1t7XsRL4ZVj38LV2eYWxXRPguBADA8BxcNz1xo8y",
        token_name="PIPE CTO",
        token_ticker="PIPE",
        price_sol=4.4141209798877615e-7,
        market_cap_sol=441.41209798877617,
        volume_sol=1322.4350391679925,
        liquidity_sol=149.359428555,
        transaction_count=2205,
        price_1hr_change=120.61,
        protocol="Raydium CLMM"
    )
    
    assert token.token_address == "576P1t7XsRL4ZVj38LV2eYWxXRPguBADA8BxcNz1xo8y"
    assert token.token_name == "PIPE CTO"
    assert token.price_sol == 4.4141209798877615e-7
    assert token.protocol == "Raydium CLMM"

def test_websocket_message_model():
    """Test creating a valid WebSocket message model"""
    # Create token as a dictionary instead of TokenData object
    token_dict = {
        "token_address": "576P1t7XsRL4ZVj38LV2eYWxXRPguBADA8BxcNz1xo8y",
        "token_name": "PIPE CTO",
        "token_ticker": "PIPE",
        "price_sol": 4.4141209798877615e-7,
        "market_cap_sol": 441.41,
        "volume_sol": 1322.43,
        "liquidity_sol": 149.35,
        "transaction_count": 2205,
        "price_1hr_change": 120.61,
        "protocol": "Raydium CLMM"
    }
    
    message = WebSocketMessage(
        type="update",
        data=token_dict
    )
    
    assert message.type == "update"
    assert message.data["token_address"] == "576P1t7XsRL4ZVj38LV2eYWxXRPguBADA8BxcNz1xo8y"