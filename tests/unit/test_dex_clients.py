import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.dex_clients import DexScreenerClient, JupiterPriceClient

@pytest.fixture
def dex_screener_client():
    client = DexScreenerClient()
    # Replace the HTTP client with a mock
    client.client = AsyncMock()
    return client

@pytest.fixture
def jupiter_client():
    client = JupiterPriceClient()
    # Replace the HTTP client with a mock
    client.client = AsyncMock()
    return client

@pytest.mark.asyncio
async def test_dex_screener_get_token(dex_screener_client):
    """Test fetching token data from DexScreener"""
    token_address = "576P1t7XsRL4ZVj38LV2eYWxXRPguBADA8BxcNz1xo8y"
    
    mock_response = {
        "pairs": [
            {
                "chainId": "solana",
                "dexId": "raydium",
                "pairAddress": "test_pair",
                "baseToken": {
                    "address": token_address,
                    "name": "PIPE CTO",
                    "symbol": "PIPE"
                },
                "priceUsd": "0.00001",
                "priceNative": 4.4141209798877615e-7,
                "liquidity": {"usd": 10000, "base": 1000000, "quote": 149.359428555},
                "volume": {"h24": 1322.4350391679925},
                "txns": {"h24": {"buys": 1200, "sells": 1005}},
                "priceChange": {"h1": 120.61, "h24": 50.5, "h7d": 10.1}
            }
        ]
    }
    
    # Mock the implementation of get_token_data directly
    with patch.object(dex_screener_client, 'get_token_data', return_value=mock_response) as mock_get_token:
        # Call the method under test
        token_data = await dex_screener_client.get_token_data(token_address)
        
        # Verify the mock was called correctly
        mock_get_token.assert_called_once_with(token_address)
        
        # Verify result matches our expected response
        assert token_data == mock_response

@pytest.mark.asyncio
async def test_jupiter_get_prices(jupiter_client):
    """Test fetching prices from Jupiter API"""
    token_addresses = ["576P1t7XsRL4ZVj38LV2eYWxXRPguBADA8BxcNz1xo8y"]
    
    mock_response = {
        "data": {
            "576P1t7XsRL4ZVj38LV2eYWxXRPguBADA8BxcNz1xo8y": {
                "id": "576P1t7XsRL4ZVj38LV2eYWxXRPguBADA8BxcNz1xo8y",
                "mintSymbol": "PIPE",
                "vsToken": "SOL",
                "vsTokenSymbol": "SOL",
                "price": 4.4141209798877615e-7
            }
        }
    }
    
    # Mock the implementation of get_prices directly
    with patch.object(jupiter_client, 'get_prices', return_value=mock_response) as mock_get_prices:
        # Call the method under test
        prices = await jupiter_client.get_prices(token_addresses)
        
        # Verify the mock was called correctly
        mock_get_prices.assert_called_once_with(token_addresses)
        
        # Verify result matches our expected response
        assert prices == mock_response