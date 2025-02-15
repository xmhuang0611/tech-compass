from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import AuditModel


class UserBase(BaseModel):
    """Base user model with common fields"""

    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="Username for login")
    full_name: str = Field(..., description="User's full name")

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    """User creation model"""

    password: str = Field(..., description="User's password (will be hashed)")
    is_active: bool = Field(default=True, description="Whether the user is active")
    is_superuser: bool = Field(default=False, description="Whether the user is a superuser")


class UserPasswordUpdate(BaseModel):
    """User password update model"""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password")


class UserUpdateBase(BaseModel):
    """Base model for user updates with optional fields"""

    email: EmailStr | None = Field(default=None, description="User's email address")
    username: str | None = Field(default=None, description="Username for login")
    full_name: str | None = Field(default=None, description="User's full name")

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(UserUpdateBase):
    """User update model - excludes sensitive fields"""

    pass


class AdminUserUpdate(UserUpdateBase):
    """Admin user update model that includes all fields"""

    is_active: bool | None = Field(default=None, description="Whether the user is active")
    is_superuser: bool | None = Field(default=None, description="Whether the user is a superuser")
    password: str | None = Field(default=None, description="New password (optional)")


class UserInDB(UserBase, AuditModel):
    """User model as stored in database"""

    hashed_password: str = Field(..., description="Hashed password")
    is_active: bool = Field(default=True, description="Whether the user is active")
    is_superuser: bool = Field(default=False, description="Whether the user is a superuser")


class User(UserBase, AuditModel):
    """User model for API responses - excludes password fields"""

    is_active: bool = Field(default=True, description="Whether the user is active")
    is_superuser: bool = Field(default=False, description="Whether the user is a superuser")
