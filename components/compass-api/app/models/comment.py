from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

from app.models import AuditModel


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

class CommentInDB(CommentBase, AuditModel):
    """Model for comment in database"""
    pass