from typing import Dict, List, Optional

from pymongo import DESCENDING

from app.core.database import get_database
from app.models.history import ChangeType, HistoryQuery, HistoryRecord


class HistoryService:
    """Service for managing history records"""

    def __init__(self):
        self.db = get_database()
        self.collection = self.db.history

    async def create_history_record(self, record: HistoryRecord) -> str:
        """
        Create a new history record

        Args:
            record: The history record to create

        Returns:
            The ID of the created record
        """
        result = await self.collection.insert_one(record.model_dump(by_alias=True))
        return str(result.inserted_id)

    async def get_history_records(self, query: HistoryQuery) -> tuple[List[HistoryRecord], int]:
        """
        Get history records based on query parameters

        Args:
            query: Query parameters

        Returns:
            A tuple of (records, total_count)
        """
        # Build filter criteria
        filter_criteria = {}

        if query.object_type:
            filter_criteria["object_type"] = query.object_type

        if query.object_id:
            filter_criteria["object_id"] = query.object_id

        if query.object_name:
            filter_criteria["object_name"] = {"$regex": query.object_name, "$options": "i"}

        if query.change_type:
            filter_criteria["change_type"] = query.change_type

        if query.username:
            filter_criteria["$or"] = [{"created_by": query.username}, {"updated_by": query.username}]

        date_criteria = {}
        if query.start_date:
            date_criteria["$gte"] = query.start_date

        if query.end_date:
            date_criteria["$lte"] = query.end_date

        if date_criteria:
            filter_criteria["created_at"] = date_criteria

        # Get total count
        total = await self.collection.count_documents(filter_criteria)

        # Get paginated records
        cursor = self.collection.find(filter_criteria)

        # Sort by created_at in descending order (newest first)
        cursor = cursor.sort("created_at", DESCENDING)

        # Apply pagination
        cursor = cursor.skip(query.skip).limit(query.limit)

        # Convert to HistoryRecord objects
        records = [HistoryRecord(**record) async for record in cursor]

        return records, total

    async def get_object_history(
        self, object_type: str, object_id: str, skip: int = 0, limit: int = 20
    ) -> tuple[List[HistoryRecord], int]:
        """
        Get history records for a specific object

        Args:
            object_type: Type of object
            object_id: ID of the object
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            A tuple of (records, total_count)
        """
        query = HistoryQuery(object_type=object_type, object_id=object_id, skip=skip, limit=limit)
        return await self.get_history_records(query)

    async def record_object_change(
        self,
        object_type: str,
        object_id: str,
        object_name: str,
        change_type: ChangeType,
        username: str,
        changes: Optional[Dict] = None,
        old_values: Optional[Dict] = None,
        change_summary: Optional[str] = None,
    ) -> str:
        """
        Record a change to an object

        Args:
            object_type: Type of object
            object_id: ID of the object
            object_name: Name of the object
            change_type: Type of change
            username: Username who made the change
            changes: Dictionary of changed fields and their new values
            old_values: Dictionary of old values for the changed fields
            change_summary: Optional summary of changes

        Returns:
            The ID of the created history record
        """
        record = HistoryRecord.create_record(
            object_type=object_type,
            object_id=object_id,
            object_name=object_name,
            change_type=change_type,
            username=username,
            changes=changes,
            old_values=old_values,
            change_summary=change_summary,
        )

        return await self.create_history_record(record)
