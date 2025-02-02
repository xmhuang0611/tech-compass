from datetime import datetime
from typing import List, Optional, Literal

from bson import ObjectId
from pydantic import BaseModel, Field

from app.models import AuditModel
from app.models.common import PyObjectId

# Stage values as defined in db-design.md
StageEnum = Literal[
    "DEVELOPING",   # Solution is under active development
    "UAT",          # Release Candidate
    "PRODUCTION",      # Actively used in production
    "DEPRECATED",  # No longer recommended for new projects
    "RETIRED"      # Completely phased out
]

# Recommend status values as defined in db-design.md
RecommendStatusEnum = Literal[
    "BUY",    # Recommended for new projects and expansion
    "HOLD",   # Maintain existing usage, but don't expand
    "SELL"    # Plan for replacement/retirement
]

# Tech Radar status values
RadarStatusEnum = Literal[
    "ADOPT",   # Proven technology, safe to use
    "TRIAL",   # Worth pursuing, understand how it fits
    "ASSESS",  # Worth exploring with the goal of understanding how it will affect your enterprise
    "HOLD"     # Proceed with caution
]

# Review status values
ReviewStatusEnum = Literal[
    "PENDING",   # Awaiting review
    "APPROVED",  # Approved by admin
    "REJECTED"   # Rejected by admin
]

class SolutionBase(BaseModel):
    """Base solution model with common fields"""
    name: str = Field(..., min_length=1, description="Solution name")
    description: str = Field(..., description="Detailed description")
    category: Optional[str] = Field(None, description="Primary category")
    radar_status: RadarStatusEnum = Field(..., description="Tech Radar status (ADOPT/TRIAL/ASSESS/HOLD)")
    department: str = Field(..., description="Department name")
    team: str = Field(..., description="Team name")
    team_email: Optional[str] = Field(None, description="Team contact email")
    maintainer_id: Optional[str] = Field(None, description="ID of the maintainer")
    maintainer_name: Optional[str] = Field(None, description="Name of the maintainer")
    maintainer_email: Optional[str] = Field(None, description="Email of the maintainer")
    official_website: Optional[str] = Field(None, description="Official website URL")
    documentation_url: Optional[str] = Field(None, description="Documentation URL")
    demo_url: Optional[str] = Field(None, description="Demo/POC URL")
    version: Optional[str] = Field(None, description="Current version")
    tags: List[str] = Field(default_factory=list, description="List of tag names")
    pros: Optional[List[str]] = Field(default_factory=list, description="List of advantages")
    cons: Optional[List[str]] = Field(default_factory=list, description="List of disadvantages")
    stage: Optional[StageEnum] = Field(None, description="Development stage status")
    recommend_status: Optional[RecommendStatusEnum] = Field(None, description="Strategic recommendation (BUY/HOLD/SELL)")

class SolutionCreate(SolutionBase):
    """Solution creation model - excludes review_status field"""
    pass

class SolutionInDBBase(SolutionBase):
    """Base model for database solutions with review status"""
    review_status: ReviewStatusEnum = Field(default="PENDING", description="Review status (PENDING/APPROVED/REJECTED)")

class SolutionUpdate(BaseModel):
    """Solution update model - all fields are optional"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    radar_status: Optional[RadarStatusEnum] = None
    department: Optional[str] = None
    team: Optional[str] = None
    team_email: Optional[str] = None
    maintainer_id: Optional[str] = None
    maintainer_name: Optional[str] = None
    maintainer_email: Optional[str] = None
    official_website: Optional[str] = None
    documentation_url: Optional[str] = None
    demo_url: Optional[str] = None
    version: Optional[str] = None
    tags: Optional[List[str]] = None
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    stage: Optional[StageEnum] = None
    recommend_status: Optional[RecommendStatusEnum] = None
    review_status: Optional[ReviewStatusEnum] = None

class SolutionInDB(SolutionInDBBase, AuditModel):
    """Solution model as stored in database"""
    slug: str = Field(..., description="URL-friendly identifier (auto-generated)")
    category_id: Optional[PyObjectId] = Field(None, description="Reference to category")

class Solution(SolutionInDB):
    """Solution model for API responses, including rating information"""
    rating: float = Field(default=0.0, description="Average rating score")
    rating_count: int = Field(default=0, description="Total number of ratings")
