from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

from app.models.common import AuditModel, PyObjectId

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

class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

    model_config = ConfigDict(
        from_attributes=True
    )

class UserInDB(UserBase):
    """User model as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str = Field(..., description="Hashed password")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Username who created")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = Field(None, description="Username who last updated")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True
    )

class User(BaseModel):
    """User model for API responses - excludes password fields"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="Username for login")
    full_name: str = Field(..., description="User's full name")
    is_active: bool = Field(default=True, description="Whether the user is active")
    is_superuser: bool = Field(default=False, description="Whether the user is a superuser")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Username who created")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = Field(None, description="Username who last updated")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_encoders={PyObjectId: str}
    )

class UserList(BaseModel):
    """API response model for list of users"""
    users: list[User]

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId: str}
    )
