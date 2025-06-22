# Meme Coin Aggregator Overview

## Introduction

The Meme Coin Aggregator is a high-performance real-time data aggregation service that collects, processes, and distributes information about meme coins across multiple Solana-based decentralized exchanges (DEXs). The system provides both REST API endpoints for data retrieval and WebSocket connections for real-time updates.

## Purpose

Meme coins represent a fast-moving and volatile segment of the cryptocurrency market with rapidly changing prices, market caps, and liquidity. This aggregator service solves several key challenges:

1. **Data Fragmentation**: Meme coin data is scattered across multiple DEXs and protocols
2. **Real-time Requirements**: Trading decisions require up-to-date price and volume information
3. **Data Reliability**: Single source data can be unreliable or unavailable
4. **Performance**: High-volume data processing requires efficient handling

## Key Features

- **Multi-source Data Aggregation**: Collects and merges data from DexScreener and Jupiter
- **Real-time Updates**: WebSocket support for live price and volume updates
- **Efficient Caching**: Redis-based caching with configurable TTL
- **Flexible Querying**: Support for time-based filtering and various sorting criteria
- **Pagination**: Cursor-based pagination for large token lists
- **Resilient API Calls**: Retry mechanism with exponential backoff

## Target Users

- **DeFi Developers**: Building applications that require meme coin data
- **Trading Platforms**: Integrating meme coin information into trading interfaces
- **Data Analytics Services**: Tracking and analyzing meme coin market trends
- **Individual Traders**: Accessing real-time information for trading decisions

## System Requirements

- Python 3.12+
- PostgreSQL
- Redis
- Network access to DexScreener and Jupiter APIs