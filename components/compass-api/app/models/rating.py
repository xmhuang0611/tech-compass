from typing import Optional

from pydantic import BaseModel, Field

from app.models import AuditModel


class RatingBase(BaseModel):
    score: int = Field(..., ge=1, le=5, description="Rating score between 1 and 5")
    comment: Optional[str] = Field(None, description="Optional comment for the rating")
    is_adopted_user: bool = Field(
        default=False, description="Whether the rating author is an adopted user for the solution"
    )


class RatingCreate(RatingBase):
    pass


class RatingInDB(RatingBase, AuditModel):
    solution_slug: str
    username: str


class Rating(RatingInDB):
    """Rating model for API responses with user's full name"""

    full_name: Optional[str] = Field(None, description="Full name of the rating author")
