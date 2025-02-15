from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class TechRadarEntry(BaseModel):
    """Tech Radar entry model"""

    quadrant: int = Field(ge=0, le=3, description="Radar quadrant (0-3)")
    ring: int = Field(
        ge=0,
        le=3,
        description="Ring position (0-3, representing adopt/trial/assess/hold)",
    )
    label: str = Field(..., description="Solution name")
    link: str = Field(..., description="Link to solution detail page")
    active: bool = Field(True, description="Whether the solution is approved")
    moved: int = Field(default=0, description="Movement indicator (always 0)")


class TechRadarData(BaseModel):
    """Tech Radar data model"""

    date: str = Field(..., description="Current date in YYYY-MM format")
    entries: List[TechRadarEntry] = Field(default_factory=list, description="List of tech radar entries")

    @classmethod
    def create_current(cls, entries: List[TechRadarEntry]) -> "TechRadarData":
        """Create a TechRadarData instance with current date"""
        current_date = datetime.now().strftime("%Y-%m")
        return cls(date=current_date, entries=entries)
