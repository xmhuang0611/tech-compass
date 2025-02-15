from datetime import datetime
from typing import Any, Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field
from pydantic.json_schema import JsonSchemaValue


class PyObjectId(ObjectId):
    """Custom type for handling MongoDB ObjectId"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: Any, handler: Any) -> JsonSchemaValue:
        """Customize JSON schema for ObjectId"""
        return {
            "type": "string",
            "description": "MongoDB ObjectId",
            "pattern": "^[0-9a-fA-F]{24}$",
        }


class AuditModel(BaseModel):
    """Base model with audit fields"""

    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Username who created")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = Field(None, description="Username who last updated")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str, datetime: lambda v: v.isoformat()},
    )
