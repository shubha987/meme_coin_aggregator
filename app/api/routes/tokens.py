# app/api/routes/tokens.py
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from app.models.token import TokenData, TokenListResponse
from app.services.aggregation import aggregation_service

router = APIRouter()

@router.get("/tokens", response_model=TokenListResponse)
async def get_tokens(
    limit: int = Query(20, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    sort_by: str = Query("volume_sol", regex="^(volume_sol|market_cap_sol|price_1hr_change)$"),
    time_filter: str = Query("24h", regex="^(1h|24h|7d)$"),
    search: Optional[str] = Query(None)
):
    try:
        tokens = await aggregation_service.get_filtered_tokens(
            limit=limit,
            cursor=cursor,
            sort_by=sort_by,
            time_filter=time_filter,
            search=search
        )
        return tokens
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tokens/{token_address}", response_model=TokenData)
async def get_token(token_address: str):
    try:
        token = await aggregation_service.get_token_by_address(token_address)
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")
        return token
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
