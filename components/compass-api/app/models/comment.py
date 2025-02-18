from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models import AuditModel


class CommentType(str, Enum):
    """Enum for comment types"""

    OFFICIAL = "OFFICIAL"
    USER = "USER"


class CommentBase(BaseModel):
    """Base model for comments"""

    content: str = Field(..., min_length=1, max_length=2000, description="Comment content")
    is_adopted_user: bool = Field(
        default=False, description="Whether the comment author is an adopted user for the solution"
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, content: str) -> str:
        """Validate and transform comment content"""
        # Trim spaces
        content = content.strip()
        # Check if empty after trimming
        if not content:
            raise ValueError("Comment content cannot be empty")
        return content


class CommentCreate(CommentBase):
    """Model for creating a comment"""

    pass


class CommentUpdate(CommentBase):
    """Model for updating a comment"""

    content: Optional[str] = Field(None, min_length=1, max_length=2000, description="Updated comment content")
    type: Optional[CommentType] = Field(
        None,
        description="Type of the comment (OFFICIAL or USER), only admins can update this field",
    )


class CommentInDB(CommentBase, AuditModel):
    """Model for comment in database"""

    solution_slug: str = Field(..., description="Slug of the solution this comment belongs to")
    username: str = Field(..., description="Username of the comment author")
    type: CommentType = Field(default=CommentType.USER, description="Type of the comment (OFFICIAL or USER)")


class Comment(CommentInDB):
    """Comment model for API responses with user's full name"""

    full_name: Optional[str] = Field(None, description="Full name of the comment author")
