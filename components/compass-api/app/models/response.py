from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    """Standard API response model"""

    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[T] = Field(None, description="Response data")
    detail: Optional[str] = Field(None, description="Error message if success is false")
    total: Optional[int] = Field(None, description="Total number of items (for list endpoints)")
    skip: Optional[int] = Field(None, description="Number of items skipped (for list endpoints)")
    limit: Optional[int] = Field(None, description="Maximum number of items (for list endpoints)")

    @classmethod
    def of(cls, data: T) -> "StandardResponse[T]":
        """Create a successful response with data"""
        return cls(success=True, data=data, detail=None)

    @classmethod
    def error(cls, message: str) -> "StandardResponse[None]":
        """Create an error response"""
        return cls(success=False, detail=message)

    @classmethod
    def paginated(cls, data: T, total: int, skip: int = 0, limit: int = 20) -> "StandardResponse[T]":
        """Create a paginated response with data"""
        return cls(success=True, data=data, total=total, skip=skip, limit=limit, detail=None)
