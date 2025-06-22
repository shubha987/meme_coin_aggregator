import pytest
from unittest.mock import patch, MagicMock
from app.services.dex_clients import DexScreenerClient, JupiterPriceClient

@pytest.fixture
def dex_screener_client():
    return DexScreenerClient()

@pytest.fixture
def jupiter_client():
    return JupiterPriceClient()

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
    
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response_obj = MagicMock()
        mock_response_obj.status = 200
        mock_response_obj.json.return_value = mock_response
        mock_get.return_value.__aenter__.return_value = mock_response_obj
        
        token_data = await dex_screener_client.get_token_data(token_address)
        
        assert "pairs" in token_data
        assert len(token_data["pairs"]) > 0

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
    
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response_obj = MagicMock()
        mock_response_obj.status = 200
        mock_response_obj.json.return_value = mock_response
        mock_get.return_value.__aenter__.return_value = mock_response_obj
        
        prices = await jupiter_client.get_prices(token_addresses)
        
        assert len(prices) == 1
        assert "576P1t7XsRL4ZVj38LV2eYWxXRPguBADA8BxcNz1xo8y" in prices
        assert prices["576P1t7XsRL4ZVj38LV2eYWxXRPguBADA8BxcNz1xo8y"] == 4.4141209798877615e-7