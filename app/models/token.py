# app/models/token.py
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class TokenData(BaseModel):
    token_address: str = Field(..., description="Token contract address")
    token_name: str = Field(..., description="Token name")
    token_ticker: str = Field(..., description="Token symbol/ticker")
    price_sol: float = Field(..., description="Price in SOL")
    market_cap_sol: float = Field(..., description="Market cap in SOL")
    volume_sol: float = Field(..., description="24h volume in SOL")
    liquidity_sol: float = Field(..., description="Liquidity in SOL")
    transaction_count: int = Field(..., description="Transaction count")
    price_1hr_change: float = Field(..., description="1hr price change %")
    protocol: str = Field(..., description="DEX protocol name")
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class TokenListResponse(BaseModel):
    tokens: List[TokenData]
    total_count: int
    next_cursor: Optional[str] = None
    has_more: bool = False

class WebSocketMessage(BaseModel):
    type: str = Field(..., description="Message type")
    data: Any = Field(..., description="Message payload")  # Change from dict to Any
    timestamp: datetime = Field(default_factory=datetime.utcnow)
