from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.common import PyObjectId

class CategoryBase(BaseModel):
    """Base category model with common fields"""
    name: str = Field(..., description="Category name")
    description: str = Field(..., description="Category description")
    parent_id: Optional[PyObjectId] = Field(default=None, description="Parent category reference")

class CategoryCreate(CategoryBase):
    """Category creation model"""
    pass

class CategoryUpdate(BaseModel):
    """Category update model"""
    name: Optional[str] = Field(None, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    parent_id: Optional[PyObjectId] = Field(None, description="Parent category reference")

class CategoryInDB(CategoryBase):
    """Category model as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[PyObjectId] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[PyObjectId] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Category(CategoryInDB):
    """Category model for API responses"""
    pass
