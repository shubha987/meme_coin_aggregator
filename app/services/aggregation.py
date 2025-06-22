# app/services/aggregation.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.dex_clients import DexScreenerClient, JupiterPriceClient
from app.services.websocket import websocket_manager
from app.models.token import TokenData, WebSocketMessage
import asyncio
from typing import List, Dict, Optional, Any
from app.core.cache import cache_manager
from datetime import datetime

class DataAggregationService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.dexscreener = DexScreenerClient()
        self.jupiter = JupiterPriceClient()
        self.is_running = False
    
    async def start(self):
        if not self.is_running:
            self.scheduler.add_job(
                self.update_token_data,
                'interval',
                seconds=30,
                id='token_update'
            )
            self.scheduler.start()
            self.is_running = True
    
    async def stop(self):
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
    
    async def update_token_data(self):
        try:
            # Fetch data from multiple sources
            tasks = [
                self.fetch_trending_tokens(),
                self.update_price_data()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and broadcast updates
            if results[0] and not isinstance(results[0], Exception):
                await self.broadcast_token_updates(results[0])
                
        except Exception as e:
            # Log error but don't stop the scheduler
            print(f"Error in data update: {e}")
    
    async def update_price_data(self):
        """Update token prices in real-time"""
        try:
            # Get cached token addresses
            cached_data = await cache_manager.get("trending_tokens")
            if not cached_data:
                return
            
            token_addresses = [token.get("token_address") for token in cached_data if "token_address" in token]
            
            if not token_addresses:
                return
                
            # Get latest price data for these tokens
            jupiter_data = await self.jupiter.get_prices(token_addresses)
            
            # Update prices and broadcast if there are significant changes
            updated_tokens = []
            
            for token_data in cached_data:
                token_address = token_data.get("token_address")
                if not token_address:
                    continue
                    
                # Get new price from Jupiter if available
                new_price = jupiter_data.get("data", {}).get(token_address, {}).get("price")
                if not new_price:
                    continue
                    
                old_price = token_data.get("price_sol", 0)
                
                # Calculate price change percentage
                if old_price > 0:
                    price_change_pct = ((new_price - old_price) / old_price) * 100
                    
                    # Only update tokens with significant price changes (>0.5%)
                    if abs(price_change_pct) > 0.5:
                        token_data["price_sol"] = new_price
                        token_data["price_1hr_change"] = price_change_pct
                        token_data["last_updated"] = datetime.utcnow().isoformat()
                        updated_tokens.append(TokenData(**token_data))
            
            # Broadcast price updates if any
            if updated_tokens:
                message = WebSocketMessage(
                    type="price_update",
                    data={"tokens": [token.dict() for token in updated_tokens]}
                )
                await websocket_manager.broadcast_to_topic("prices", message.dict())
                
            return updated_tokens
        except Exception as e:
            print(f"Error updating price data: {e}")
            return []
    
    async def fetch_trending_tokens(self) -> List[TokenData]:
        """Fetch trending tokens from multiple sources and merge them"""
        try:
            # Fetch tokens from DexScreener
            dex_data = await self.dexscreener.search_tokens("solana trending")
            
            # Fetch tokens from Jupiter
            # Get top token addresses from DexScreener
            token_addresses = []
            if "pairs" in dex_data:
                token_addresses = [pair.get("baseToken", {}).get("address") 
                                for pair in dex_data.get("pairs", [])[:50] 
                                if "baseToken" in pair]
            
            # Get price data from Jupiter
            jupiter_data = {}
            if token_addresses:
                jupiter_data = await self.jupiter.get_prices(token_addresses)
            
            # Merge data from multiple sources
            merged_tokens = self._merge_token_data(dex_data, jupiter_data)
            
            # Cache the merged data
            await cache_manager.set("trending_tokens", [t.dict() for t in merged_tokens], ttl=60)
            
            return merged_tokens
        except Exception as e:
            print(f"Error fetching trending tokens: {e}")
            # Try to return cached data if available
            cached_data = await cache_manager.get("trending_tokens")
            if cached_data:
                return [TokenData(**token) for token in cached_data]
            return []
    
    def _merge_token_data(self, dex_data: Dict, jupiter_data: Dict) -> List[TokenData]:
        """Merge token data from multiple sources"""
        result = []
        
        # Process DexScreener data
        if "pairs" in dex_data:
            for pair in dex_data.get("pairs", []):
                base_token = pair.get("baseToken", {})
                token_address = base_token.get("address")
                
                if not token_address:
                    continue
                
                # Check if token already in result (avoid duplicates)
                existing_token = next((t for t in result if t.token_address == token_address), None)
                
                if existing_token:
                    # Update existing token with additional data
                    txns = pair.get("txns", {}).get("h24", {})
                    # Make sure we're handling the different possible formats of txns
                    if isinstance(txns, dict):
                        txn_count = txns.get("buys", 0) + txns.get("sells", 0)
                    else:
                        txn_count = int(txns) if txns else 0
                        
                    existing_token.transaction_count += txn_count
                    
                    # Use the protocol with higher liquidity
                    liquidity_usd = pair.get("liquidity", {}).get("usd", 0)
                    if isinstance(liquidity_usd, (int, float)) and liquidity_usd > existing_token.liquidity_sol:
                        existing_token.protocol = pair.get("dexId", "Unknown")
                        existing_token.liquidity_sol = float(liquidity_usd)
                else:
                    # Create new token entry
                    try:
                        # Get price
                        price_usd = pair.get("priceUsd", 0)
                        price_sol = float(price_usd) if price_usd else 0
                        
                        # Get liquidity
                        liquidity = pair.get("liquidity", {}).get("usd", 0)
                        liquidity_sol = float(liquidity) if liquidity else 0
                        
                        # Get volume
                        volume = pair.get("volume", {}).get("h24", 0)
                        volume_sol = float(volume) if volume else 0
                        
                        # Get transaction count
                        txns = pair.get("txns", {}).get("h24", {})
                        if isinstance(txns, dict):
                            txn_count = txns.get("buys", 0) + txns.get("sells", 0)
                        else:
                            txn_count = int(txns) if txns else 0
                        
                        # Get price change
                        price_change = pair.get("priceChange", {}).get("h1", 0)
                        price_1hr_change = float(price_change) if price_change else 0
                        
                        # Get market cap (fdv)
                        market_cap = pair.get("fdv", 0)
                        market_cap_sol = float(market_cap) if market_cap else 0
                        
                        token = TokenData(
                            token_address=token_address,
                            token_name=base_token.get("name", "Unknown"),
                            token_ticker=base_token.get("symbol", "UNKNOWN"),
                            price_sol=price_sol,
                            market_cap_sol=market_cap_sol,
                            volume_sol=volume_sol,
                            liquidity_sol=liquidity_sol,
                            transaction_count=txn_count,
                            price_1hr_change=price_1hr_change,
                            protocol=pair.get("dexId", "Unknown")
                        )
                        result.append(token)
                    except Exception as e:
                        print(f"Error creating token data: {e}")
        
        return result
    
    async def broadcast_token_updates(self, tokens: List[TokenData]):
        message = WebSocketMessage(
            type="token_update",
            data={"tokens": [token.dict() for token in tokens]}
        )
        await websocket_manager.broadcast_to_topic("tokens", message.dict())
    
    async def get_filtered_tokens(
        self, 
        limit: int = 20, 
        cursor: Optional[str] = None, 
        sort_by: str = "volume_sol", 
        time_filter: str = "24h",
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get filtered and sorted tokens with pagination"""
        # Fetch tokens (or use cache)
        tokens = await self.fetch_trending_tokens()
        
        # Apply search filter if provided
        if search:
            search = search.lower()
            tokens = [t for t in tokens if search in t.token_name.lower() or 
                    search in t.token_ticker.lower() or 
                    search in t.token_address.lower()]
        
        # Apply time filter
        # The time_filter parameter is already used when fetching data from the APIs
        
        # Sort tokens based on criteria
        if sort_by == "volume_sol":
            tokens.sort(key=lambda x: x.volume_sol, reverse=True)
        elif sort_by == "market_cap_sol":
            tokens.sort(key=lambda x: x.market_cap_sol, reverse=True)
        elif sort_by == "price_1hr_change":
            tokens.sort(key=lambda x: x.price_1hr_change, reverse=True)
        
        # Apply cursor-based pagination
        total_count = len(tokens)
        start_idx = 0
        
        if cursor:
            try:
                # Cursor is the index of the last item from previous page
                start_idx = int(cursor) + 1
            except ValueError:
                start_idx = 0
        
        end_idx = min(start_idx + limit, total_count)
        has_more = end_idx < total_count
        
        # Create the pagination response
        return {
            "tokens": tokens[start_idx:end_idx],
            "total_count": total_count,
            "next_cursor": str(end_idx - 1) if has_more else None,
            "has_more": has_more
        }
    
    async def get_token_by_address(self, token_address: str) -> Optional[TokenData]:
        """Get detailed information for a specific token"""
        try:
            # Try to get from cache first
            cache_key = f"token_detail:{token_address}"
            cached_data = await cache_manager.get(cache_key)
            
            if cached_data:
                return TokenData(**cached_data)
            
            # Fetch fresh data
            dex_data = await self.dexscreener.get_token_data(token_address)
            
            # Get Jupiter price data
            jupiter_data = await self.jupiter.get_prices([token_address])
            
            # Process and merge data
            token = None
            if "pairs" in dex_data and dex_data["pairs"]:
                # Use the pair with highest liquidity
                pair = max(dex_data["pairs"], key=lambda x: float(x.get("liquidity", {}).get("usd", 0)))
                base_token = pair.get("baseToken", {})
                
                token = TokenData(
                    token_address=token_address,
                    token_name=base_token.get("name", "Unknown"),
                    token_ticker=base_token.get("symbol", "UNKNOWN"),
                    price_sol=float(pair.get("priceUsd", 0)),
                    market_cap_sol=float(pair.get("fdv", 0)),
                    volume_sol=float(pair.get("volume", {}).get("h24", 0)),
                    liquidity_sol=float(pair.get("liquidity", {}).get("usd", 0)),
                    transaction_count=int(pair.get("txns", {}).get("h24", 0)),
                    price_1hr_change=float(pair.get("priceChange", {}).get("h1", 0)),
                    protocol=pair.get("dexId", "Unknown")
                )
                
                # Cache the token data
                await cache_manager.set(cache_key, token.dict(), ttl=30)
            
            return token
        except Exception as e:
            print(f"Error fetching token details: {e}")
            return None

aggregation_service = DataAggregationService()
