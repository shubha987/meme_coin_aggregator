# app/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 30
    
    # API settings
    DEXSCREENER_RATE_LIMIT: int = 300
    JUPITER_RATE_LIMIT: int = 100
    
    # WebSocket settings
    WEBSOCKET_PING_INTERVAL: int = 20
    WEBSOCKET_PING_TIMEOUT: int = 10
    
    # Database settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:Shubha%4018022004@localhost:5432/meme_coin_db"

    class Config:
        env_file = ".env"

settings = Settings()
