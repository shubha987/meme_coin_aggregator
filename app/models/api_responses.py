from pydantic import BaseModel
from typing import Optional, Any, List, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = datetime.utcnow()

class DataResponse(BaseResponse, Generic[T]):
    data: T

class ErrorResponse(BaseResponse):
    success: bool = False
    error_code: str
    detail: Optional[str] = None

class PaginatedResponse(BaseResponse, Generic[T]):
    data: List[T]
    total_count: int
    next_cursor: Optional[str] = None
    has_more: bool = False
    
class TokenUpdateResponse(BaseResponse):
    tokens: List[Any]
    updated_at: datetime = datetime.utcnow()