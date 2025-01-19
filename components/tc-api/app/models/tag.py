from typing import Optional
from pydantic import BaseModel, Field

from app.models.common import AuditModel, PyObjectId

class TagBase(BaseModel):
    """Base tag model with common fields"""
    name: str = Field(..., description="Tag name")
    description: Optional[str] = Field(None, description="Tag description")
    color: Optional[str] = Field(None, description="Color code for UI display")

class TagCreate(TagBase):
    """Tag creation model"""
    pass

class TagUpdate(BaseModel):
    """Tag update model"""
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None

class TagInDB(TagBase, AuditModel):
    """Tag model as stored in database"""
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class Tag(TagInDB):
    """Tag model for API responses"""
    pass
