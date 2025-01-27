from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, field_validator

from app.models.common import AuditModel, PyObjectId


class CategoryBase(BaseModel):
    """Base category model with common fields"""
    name: str = Field(
        ...,
        description="Category name (spaces will be trimmed)",
        min_length=1,
        max_length=100,
        examples=["Development", "Infrastructure"]
    )
    description: str = Field(
        "",
        description="Category description",
        max_length=500
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, name: str) -> str:
        """Validate and transform category name"""
        # Trim spaces
        name = name.strip()
        # Check if empty after trimming
        if not name:
            raise ValueError("Category name cannot be empty")
        return name

    @field_validator('description')
    @classmethod
    def validate_description(cls, description: str) -> str:
        """Validate category description"""
        return description.strip() if description else ""


class CategoryCreate(CategoryBase):
    """Category creation model"""
    pass


class CategoryUpdate(CategoryBase):
    """Category update model"""
    pass


class CategoryInDB(CategoryBase, AuditModel):
    """Category model as stored in database"""
    pass


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
