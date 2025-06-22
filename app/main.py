# app/main.py
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import tokens, websocket
from app.core.cache import cache_manager
from app.services.aggregation import aggregation_service
from app.middleware.middleware import RateLimitMiddleware  # Import the middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    await cache_manager.connect()
    await aggregation_service.start()
    
    yield  # This is where the application runs
    
    # Shutdown code
    await aggregation_service.stop()

app = FastAPI(
    title="Meme Coin Aggregator API",
    description="Real-time meme coin data aggregation service",
    version="1.0.0",
    lifespan=lifespan
)

# Add the rate limit middleware
app.add_middleware(RateLimitMiddleware, calls=100, period=60)

# Include routers
app.include_router(tokens.router, prefix="/api/v1", tags=["tokens"])
app.include_router(websocket.router, prefix="/api/v1", tags=["websocket"])

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1  # Single worker for WebSocket state management
    )
