from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models import AuditModel
from app.models.common import PyObjectId


class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="Username for login")
    full_name: str = Field(..., description="User's full name")
    is_active: bool = Field(default=True, description="Whether the user is active")
    is_superuser: bool = Field(default=False, description="Whether the user is a superuser")

    model_config = ConfigDict(
        from_attributes=True
    )

class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., description="User's password (will be hashed)")

class UserUpdate(UserBase):
    """User update model"""
    pass

class UserInDB(UserBase,AuditModel):
    """User model as stored in database"""
    hashed_password: str = Field(..., description="Hashed password")

class User(UserInDB):
    """User model for API responses - excludes password fields"""
    pass

class UserList(BaseModel):
    """API response model for list of users"""
    users: list[User]

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId: str}
    )
