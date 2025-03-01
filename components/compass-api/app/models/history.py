from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.common import AuditModel


class ChangeType(str, Enum):
    """Type of change made to an object"""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class ChangeField(BaseModel):
    """Represents a field that was changed"""

    field_name: str = Field(..., description="Name of the field that was changed")
    old_value: Optional[Any] = Field(None, description="Previous value of the field")
    new_value: Optional[Any] = Field(None, description="New value of the field")


class HistoryRecord(AuditModel):
    """Model to track changes to objects"""

    object_type: str = Field(..., description="Type of object that was changed (e.g., 'solution', 'category')")
    object_id: str = Field(..., description="ID of the object that was changed")
    object_name: str = Field(..., description="Name of the object for easy reference")
    change_type: ChangeType = Field(..., description="Type of change (create, update, delete)")
    changed_fields: List[ChangeField] = Field(default_factory=list, description="List of fields that were changed")
    change_summary: str = Field(..., description="Summary of changes made")

    @classmethod
    def create_record(
        cls,
        object_type: str,
        object_id: str,
        object_name: str,
        change_type: ChangeType,
        username: str,
        changes: Dict[str, Any] = None,
        old_values: Dict[str, Any] = None,
        change_summary: Optional[str] = None,
    ) -> "HistoryRecord":
        """
        Create a history record for an object change

        Args:
            object_type: Type of object (solution, category, etc.)
            object_id: ID of the object
            object_name: Name of the object
            change_type: Type of change (create, update, delete)
            username: Username who made the change
            changes: Dictionary of changed fields and their new values
            old_values: Dictionary of old values for the changed fields
            change_summary: Optional summary of changes

        Returns:
            A new HistoryRecord instance
        """
        changed_fields = []

        if changes and change_type != ChangeType.DELETE:
            for field_name, new_value in changes.items():
                old_value = old_values.get(field_name) if old_values else None
                # Only record if the value actually changed
                if old_value != new_value:
                    changed_fields.append(ChangeField(field_name=field_name, old_value=old_value, new_value=new_value))

        # Generate a default change summary if none provided
        if not change_summary:
            if change_type == ChangeType.CREATE:
                change_summary = f"Created {object_type} '{object_name}'"
            elif change_type == ChangeType.UPDATE:
                field_names = [field.field_name for field in changed_fields]
                change_summary = f"Updated {object_type} '{object_name}': {', '.join(field_names)}"
            elif change_type == ChangeType.DELETE:
                change_summary = f"Deleted {object_type} '{object_name}'"

        return cls(
            object_type=object_type,
            object_id=object_id,
            object_name=object_name,
            change_type=change_type,
            changed_fields=changed_fields,
            change_summary=change_summary,
            created_by=username,
            updated_by=username,
        )


class HistoryQuery(BaseModel):
    """Query parameters for history records"""

    object_type: Optional[str] = Field(None, description="Filter by object type")
    object_id: Optional[str] = Field(None, description="Filter by object ID")
    object_name: Optional[str] = Field(None, description="Filter by object name")
    change_type: Optional[ChangeType] = Field(None, description="Filter by change type")
    username: Optional[str] = Field(None, description="Filter by username who made the change")
    start_date: Optional[datetime] = Field(None, description="Filter changes after this date")
    end_date: Optional[datetime] = Field(None, description="Filter changes before this date")
    skip: int = Field(0, description="Number of records to skip (for pagination)")
    limit: int = Field(20, description="Maximum number of records to return (for pagination)")
