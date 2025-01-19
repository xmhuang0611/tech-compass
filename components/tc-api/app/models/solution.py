from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.common import PyObjectId

class SolutionBase(BaseModel):
    """Base solution model with common fields"""
    name: str = Field(..., description="Solution name")
    description: str = Field(..., description="Detailed description")
    category: Optional[str] = Field(None, description="Primary category")
    category_id: Optional[PyObjectId] = Field(None, description="Reference to category")
    status: str = Field(..., description="Current status")
    department: str = Field(..., description="Department name")
    team: str = Field(..., description="Team name")
    team_email: Optional[str] = Field(None, description="Team contact email")
    official_website: Optional[str] = Field(None, description="Official website URL")
    documentation_url: Optional[str] = Field(None, description="Documentation URL")
    demo_url: Optional[str] = Field(None, description="Demo/POC URL")
    version: Optional[str] = Field(None, description="Current version")
    pros: Optional[List[str]] = Field(default_factory=list, description="List of advantages")
    cons: Optional[List[str]] = Field(default_factory=list, description="List of disadvantages")
    development_status: Optional[str] = Field(None, description="Development phase status")
    recommend_status: Optional[str] = Field(None, description="Strategic recommendation")

class SolutionCreate(SolutionBase):
    """Solution creation model"""
    pass

class SolutionUpdate(BaseModel):
    """Solution update model"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    category_id: Optional[PyObjectId] = None
    status: Optional[str] = None
    department: Optional[str] = None
    team: Optional[str] = None
    team_email: Optional[str] = None
    official_website: Optional[str] = None
    documentation_url: Optional[str] = None
    demo_url: Optional[str] = None
    version: Optional[str] = None
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    development_status: Optional[str] = None
    recommend_status: Optional[str] = None

class SolutionInDB(SolutionBase):
    """Solution model as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[PyObjectId] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[PyObjectId] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Solution(SolutionInDB):
    """Solution model for API responses"""
    pass
