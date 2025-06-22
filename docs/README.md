# Meme Coin Aggregator

A real-time data aggregation service for meme coins across multiple DEXs.

## Architecture

This service aggregates token data from multiple DEX sources (DexScreener, Jupiter) with efficient caching and real-time updates via WebSockets.

### Key Components

- **Data Aggregation**: Fetches and merges token data from multiple DEX APIs
- **Real-time Updates**: WebSocket support for live price and volume updates
- **Caching**: Redis-based caching with configurable TTL
- **Filtering & Sorting**: Support for time-based filtering and various sorting criteria
- **Pagination**: Cursor-based pagination for large token lists

## API Endpoints

- GET `/api/v1/tokens` - Get list of tokens with filtering and sorting
- GET `/api/v1/tokens/{token_address}` - Get details for a specific token
- WebSocket `/api/v1/ws` - Real-time token updates

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis
- **WebSockets**: Native FastAPI WebSockets
- **Task Scheduling**: APScheduler

## Design Decisions

1. **Async All the Way**: Used Python's async/await throughout for better performance
2. **Smart Caching**: Implemented caching at multiple levels to reduce API calls
3. **Exponential Backoff**: Used retry mechanism with exponential backoff for API rate limits
4. **Topic-based WebSockets**: Implemented topic subscription for targeted updates