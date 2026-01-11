from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar, List
from datetime import datetime

DataT = TypeVar("DataT")


class ErrorResponse(BaseModel):
    """Standard error response format"""

    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class SuccessResponse(BaseModel, Generic[DataT]):
    """Standard success response format"""

    success: bool = Field(True, description="Operation success indicator")
    data: DataT = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Optional success message")


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Paginated response format"""

    items: List[DataT] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class TimestampSchema(BaseModel):
    """Mixin for schemas with timestamps"""

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
