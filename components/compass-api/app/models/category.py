from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, field_validator

from app.models.common import PyObjectId


class CategoryBase(BaseModel):
    """Base category model with common fields"""
    name: str = Field(..., description="Category name (spaces will be trimmed)")
    description: str = Field(..., description="Category description")

    @field_validator('name')
    @classmethod
    def trim_name(cls, name: str) -> str:
        """Trim spaces from category name"""
        return name.strip()

class CategoryCreate(CategoryBase):
    """Category creation model"""
    pass

class CategoryUpdate(BaseModel):
    """Category update model"""
    name: Optional[str] = Field(None, description="Category name (spaces will be trimmed)")
    description: Optional[str] = Field(None, description="Category description")

    @field_validator('name')
    @classmethod
    def trim_name(cls, name: Optional[str]) -> Optional[str]:
        """Trim spaces from category name if provided"""
        if name is None:
            return None
        return name.strip()

class CategoryInDB(CategoryBase):
    """Category model as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Username who created")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = Field(None, description="Username who last updated")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Category(CategoryInDB):
    """Category model for API responses"""
    pass

class CategoryList(BaseModel):
    """API response model for list of categories"""
    categories: list[CategoryInDB]

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
