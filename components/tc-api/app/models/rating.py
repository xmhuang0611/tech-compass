from pydantic import BaseModel, Field
from typing import Optional

class RatingBase(BaseModel):
    score: int = Field(..., ge=1, le=5, description="Rating score between 1 and 5")
    comment: Optional[str] = Field(None, description="Optional comment for the rating")

class RatingCreate(RatingBase):
    pass

class RatingInDB(RatingBase):
    id: str
    solution_slug: str
    username: str
    created_at: str
    updated_at: str

class RatingDistribution(BaseModel):
    average_score: float
    count: int

class RatingList(BaseModel):
    ratings: list[RatingInDB]
    distribution: RatingDistribution 