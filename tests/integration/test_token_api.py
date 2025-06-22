import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

def test_get_tokens():
    """Test getting token list"""
    with patch('app.api.routes.tokens.aggregation_service.get_filtered_tokens') as mock_get_tokens:
        # Mock response to match actual format
        mock_get_tokens.return_value = {
            "tokens": [
                {
                    "token_address": "576P1t7XsRL4ZVj38LV2eYWxXRPguBADA8BxcNz1xo8y",
                    "token_name": "PIPE CTO",
                    "token_ticker": "PIPE",
                    "price_sol": 4.4141209798877615e-7,
                    "market_cap_sol": 441.41,
                    "volume_sol": 1322.43,
                    "liquidity_sol": 149.35,
                    "transaction_count": 2205,
                    "price_1hr_change": 120.61,
                    "protocol": "Raydium CLMM",
                    "last_updated": "2023-06-21T12:00:00"
                }
            ],
            "total_count": 1,
            "next_cursor": None,
            "has_more": False
        }
        
        response = client.get("/api/v1/tokens")
        
        assert response.status_code == 200
        assert response.json()["tokens"][0]["token_address"] == "576P1t7XsRL4ZVj38LV2eYWxXRPguBADA8BxcNz1xo8y"
        assert response.json()["total_count"] == 1

def test_get_tokens_with_filters():
    """Test getting tokens with filters"""
    with patch('app.api.routes.tokens.aggregation_service.get_filtered_tokens') as mock_get_tokens:
        # Mock response
        mock_get_tokens.return_value = {
            "tokens": [
                {
                    "token_address": "576P1t7XsRL4ZVj38LV2eYWxXRPguBADA8BxcNz1xo8y",
                    "token_name": "PIPE CTO",
                    "token_ticker": "PIPE",
                    "price_sol": 4.4141209798877615e-7,
                    "market_cap_sol": 441.41,
                    "volume_sol": 1322.43,
                    "liquidity_sol": 149.35,
                    "transaction_count": 2205,
                    "price_1hr_change": 120.61,
                    "protocol": "Raydium CLMM",
                    "last_updated": "2023-06-21T12:00:00"
                }
            ],
            "total_count": 1,
            "next_cursor": None,
            "has_more": False
        }
        
        response = client.get("/api/v1/tokens?limit=10&sort_by=volume_sol&time_filter=24h")
        
        assert response.status_code == 200
        mock_get_tokens.assert_called_once()

def test_get_token_by_address():
    """Test getting a specific token by address"""
    token_address = "576P1t7XsRL4ZVj38LV2eYWxXRPguBADA8BxcNz1xo8y"
    
    with patch('app.api.routes.tokens.aggregation_service.get_token_by_address') as mock_get_token:
        # Mock response
        mock_get_token.return_value = {
            "token_address": token_address,
            "token_name": "PIPE CTO",
            "token_ticker": "PIPE",
            "price_sol": 4.4141209798877615e-7,
            "market_cap_sol": 441.41,
            "volume_sol": 1322.43,
            "liquidity_sol": 149.35,
            "transaction_count": 2205,
            "price_1hr_change": 120.61,
            "protocol": "Raydium CLMM",
            "last_updated": "2023-06-21T12:00:00"
        }
        
        response = client.get(f"/api/v1/tokens/{token_address}")
        
        assert response.status_code == 200
        assert response.json()["token_address"] == token_address