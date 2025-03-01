import logging
from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.history import ChangeType, HistoryQuery, HistoryRecord
from app.models.response import StandardResponse
from app.services.history_service import HistoryService

logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/", response_model=StandardResponse[List[HistoryRecord]])
async def get_history(
    object_type: Optional[str] = Query(None, description="Filter by object type (e.g., 'solution', 'category')"),
    object_id: Optional[str] = Query(None, description="Filter by object ID"),
    object_name: Optional[str] = Query(None, description="Filter by object name (case-insensitive, partial match)"),
    change_type: Optional[ChangeType] = Query(None, description="Filter by change type (create/update/delete)"),
    username: Optional[str] = Query(None, description="Filter by username who made the change"),
    start_date: Optional[datetime] = Query(None, description="Filter changes after this date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="Filter changes before this date (ISO format)"),
    skip: int = Query(0, description="Number of records to skip (for pagination)"),
    limit: int = Query(20, description="Maximum number of records to return (for pagination)"),
    history_service: HistoryService = Depends(),
) -> Any:
    """
    Get history records based on query parameters.

    Returns a list of history records matching the specified filters,
    sorted by change date in descending order (newest first).
    """
    query = HistoryQuery(
        object_type=object_type,
        object_id=object_id,
        object_name=object_name,
        change_type=change_type,
        username=username,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )

    try:
        history_records, total = await history_service.get_history_records(query)
        return StandardResponse.paginated(history_records, total, skip, limit)
    except Exception as e:
        logger.error(f"Error getting history records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting history records: {str(e)}",
        )
