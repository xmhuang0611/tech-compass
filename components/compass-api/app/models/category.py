from pydantic import BaseModel, Field, field_validator

from app.models.common import AuditModel


class CategoryBase(BaseModel):
    """Base category model with common fields"""

    name: str = Field(
        ...,
        description="Category name (spaces will be trimmed)",
        min_length=1,
        max_length=100,
        examples=["Development", "Infrastructure"],
    )
    description: str = Field("", description="Category description", max_length=500)
    radar_quadrant: int = Field(
        default=-1,
        description="Radar quadrant number (-1 to 3, -1 means not assigned)",
        ge=-1,
        le=3,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str) -> str:
        """Validate and transform category name"""
        # Trim spaces
        name = name.strip()
        # Check if empty after trimming
        if not name:
            raise ValueError("Category name cannot be empty")
        return name

    @field_validator("description")
    @classmethod
    def validate_description(cls, description: str) -> str:
        """Validate category description"""
        return description.strip() if description else ""

    @field_validator("radar_quadrant")
    @classmethod
    def validate_radar_quadrant(cls, value: int) -> int:
        """Validate radar quadrant value"""
        if not (-1 <= value <= 3):
            raise ValueError("Radar quadrant must be between -1 and 3")
        return value


class CategoryCreate(CategoryBase):
    """Category creation model"""

    pass


class CategoryUpdate(CategoryBase):
    """Category update model"""

    pass


class CategoryInDB(CategoryBase, AuditModel):
    """Category model as stored in database"""

    pass


class Category(CategoryInDB):
    """Category model for API responses"""

    usage_count: int = Field(default=0, description="Number of solutions using this category")
