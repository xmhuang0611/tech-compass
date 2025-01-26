from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class CommentBase(BaseModel):
    """Base model for comments"""
    content: str = Field(
        ..., 
        min_length=1, 
        max_length=1000, 
        description="Comment content"
    )

    @field_validator('content')
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

class CommentInDB(CommentBase):
    """Model for comment in database"""
    id: str = Field(..., description="Unique identifier for the comment")
    solution_slug: str = Field(..., description="Slug of the solution this comment belongs to")
    username: str = Field(..., description="Username of the comment author")
    created_at: str = Field(..., description="Timestamp when the comment was created")
    updated_at: str = Field(..., description="Timestamp when the comment was last updated")

class CommentList(BaseModel):
    """Model for list of comments with pagination"""
    comments: list[CommentInDB]
    total: int = Field(..., description="Total number of comments")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of comments per page") 