from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.common import PyObjectId

class TagBase(BaseModel):
    """Base tag model"""
    name: str = Field(..., description="Tag name")
    description: Optional[str] = Field(None, description="Tag description")

class TagCreate(TagBase):
    """Model for creating a new tag"""
    pass

class TagUpdate(TagBase):
    """Model for updating an existing tag"""
    name: Optional[str] = None
    description: Optional[str] = None

class TagInDB(TagBase):
    """Model for tag in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Username who created")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = Field(None, description="Username who last updated")
    usage_count: int = Field(default=0, description="Number of solutions using this tag")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            PyObjectId: str
        }

class Tag(TagInDB):
    """API response model for tag"""
    pass

class TagList(BaseModel):
    """API response model for list of tags"""
    tags: list[TagInDB]

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            PyObjectId: str
        }
