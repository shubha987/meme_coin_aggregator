# API Reference

## Base URL

All API endpoints are prefixed with `/api/v1`.

## Authentication

Currently, the API does not require authentication.

## Rate Limiting

API requests are rate-limited to 100 requests per minute per IP address. Exceeding this limit will result in a 429 Too Many Requests response.

## Endpoints

### List Tokens
#### `GET /tokens`

Retrieves a list of all tokens tracked by the aggregator.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sort_by` | string | No | Field to sort results by. Options: `name`, `price`, `market_cap`, `volume_24h`, `change_24h`. Default: `market_cap` |
| `order` | string | No | Sort order. Options: `asc`, `desc`. Default: `desc` |
| `limit` | integer | No | Maximum number of results to return. Default: 100, Max: 500 |
| `offset` | integer | No | Number of results to skip for pagination. Default: 0 |
| `min_market_cap` | number | No | Filter tokens with market cap >= this value (in USD) |

**Response:**

```json
{
    "success": true,
    "count": 100,
    "total": 1245,
    "data": [
        {
            "id": "dogecoin",
            "symbol": "DOGE",
            "name": "Dogecoin",
            "logo_url": "https://example.com/logos/dogecoin.png",
            "current_price": 0.12345,
            "market_cap": 16234567890,
            "volume_24h": 1234567890,
            "change_24h": 5.67
        }
        // More tokens...
    ]
}
```

**Example Request:**

```
GET /api/v1/tokens?sort_by=volume_24h&order=desc&limit=10
```

### Get Token Details

#### `GET /tokens/{token_id}`

Retrieves detailed information for a specific token.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `token_id` | string | Yes | Token identifier (e.g., `dogecoin`, `shiba-inu`) |

**Example Response:**

```json
{
    "success": true,
    "data": {
        "id": "dogecoin",
        "symbol": "DOGE",
        "name": "Dogecoin",
        "logo_url": "https://example.com/logos/dogecoin.png",
        "current_price": 0.12345,
        "market_cap": 16234567890,
        "volume_24h": 1234567890,
        "change_24h": 5.67,
        "all_time_high": 0.7376,
        "website": "https://dogecoin.com"
    }
}
```