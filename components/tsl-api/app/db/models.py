from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, HttpUrl, Field

class AuditFields(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Solution(AuditFields):
    name: str
    description: str
    category: str
    status: str
    department: str
    team: str
    team_email: EmailStr
    author_id: str
    author_name: str
    author_email: EmailStr
    official_website: Optional[HttpUrl] = None
    documentation_url: Optional[HttpUrl] = None
    demo_url: Optional[HttpUrl] = None
    version: str
    pros: List[str] = []
    cons: List[str] = []
    development_status: str
    recommend_status: str

class Tag(AuditFields):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None

class User(AuditFields):
    email: EmailStr
    username: str
    full_name: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
