from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import get_current_active_user
from app.models.comment import (
    Comment,
    CommentCreate,
    CommentInDB,
    CommentType,
    CommentUpdate,
)
from app.models.response import StandardResponse
from app.models.user import User
from app.services.comment_service import CommentService
from app.services.solution_service import SolutionService

router = APIRouter()


async def verify_solution_exists(solution_slug: str, solution_service: SolutionService = Depends()) -> None:
    """Verify that a solution exists or raise 404."""
    solution = await solution_service.get_solution_by_slug(solution_slug)
    if not solution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found")


@router.get("/", response_model=StandardResponse[list[Comment]], tags=["comments"])
async def get_all_comments(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of items to return"),
    sort: str = Query("-created_at", description="Sort field (prefix with - for descending order)"),
    type: Optional[CommentType] = Query(None, description="Filter comments by type (OFFICIAL or USER)"),
    solution_slug: Optional[str] = Query(
        None, description="Filter comments by solution slug (supports partial matching)"
    ),
    comment_service: CommentService = Depends(),
) -> StandardResponse[list[Comment]]:
    """
    Get all comments with pagination, sorting and optional filtering.
    Default sort is by created_at in descending order (newest first).

    Query Parameters:
    - skip: Number of items to skip
    - limit: Maximum number of items to return (1-100)
    - sort: Sort field (created_at, updated_at). Prefix with - for descending order
    - type: Filter comments by type (OFFICIAL or USER)
    - solution_slug: Filter comments by solution slug (supports partial matching)
    """
    try:
        comments, total = await comment_service.get_comments(
            skip=skip, limit=limit, sort=sort, type=type, solution_slug=solution_slug
        )
        return StandardResponse.paginated(comments, total, skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting comments: {str(e)}")


@router.get(
    "/solution/{solution_slug}",
    response_model=StandardResponse[list[Comment]],
    tags=["comments"],
)
async def get_solution_comments(
    solution_slug: str,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of items to return"),
    sort_by: str = Query("created_at", regex="^(created_at)$", description="Field to sort by"),
    type: Optional[CommentType] = Query(None, description="Filter comments by type (OFFICIAL or USER)"),
    comment_service: CommentService = Depends(),
    _: None = Depends(verify_solution_exists),
) -> StandardResponse[list[Comment]]:
    """
    Get all comments for a solution with pagination, sorting and optional type filtering.
    Comments are sorted by created_at in descending order (newest first).
    """
    try:
        comments, total = await comment_service.get_solution_comments(
            solution_slug=solution_slug,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            type=type,
        )
        return StandardResponse.paginated(comments, total, skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting comments: {str(e)}")


@router.post(
    "/solution/{solution_slug}",
    response_model=StandardResponse[CommentInDB],
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    solution_slug: str,
    comment: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    comment_service: CommentService = Depends(),
    _: None = Depends(verify_solution_exists),
) -> StandardResponse[CommentInDB]:
    """Create a new comment on a solution."""
    try:
        result = await comment_service.create_comment(
            solution_slug=solution_slug, comment=comment, username=current_user.username
        )
        return StandardResponse.of(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating comment: {str(e)}")


@router.put("/{comment_id}", response_model=StandardResponse[CommentInDB])
async def update_comment(
    comment_id: str,
    comment_update: CommentUpdate,
    current_user: User = Depends(get_current_active_user),
    comment_service: CommentService = Depends(),
) -> StandardResponse[CommentInDB]:
    """
    Update a comment.

    Permissions:
    - Regular users can only update their own comments' content
    - Regular users cannot update the type field
    - Administrators can update any comment and all fields including type
    - Attempting to update type field as a non-admin will result in a 403 error

    The type field can be:
    - OFFICIAL: Official comments from administrators
    - USER: Regular user comments (default)
    """
    try:
        result = await comment_service.update_comment(
            comment_id=comment_id,
            comment_update=comment_update,
            username=current_user.username,
            is_superuser=current_user.is_superuser,
        )
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        return StandardResponse.of(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating comment: {str(e)}")


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_active_user),
    comment_service: CommentService = Depends(),
) -> None:
    """
    Delete a comment.
    Only the comment creator or superusers can delete it.
    """
    try:
        success = await comment_service.delete_comment(
            comment_id=comment_id,
            username=current_user.username,
            is_superuser=current_user.is_superuser,
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting comment: {str(e)}")


@router.get("/my/", response_model=StandardResponse[list[Comment]], tags=["comments"])
async def get_my_comments(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of items to return"),
    sort: str = Query("-created_at", description="Sort field (prefix with - for descending order)"),
    current_user: User = Depends(get_current_active_user),
    comment_service: CommentService = Depends(),
) -> StandardResponse[list[Comment]]:
    """
    Get all comments created by the current user with pagination and sorting.
    Default sort is by created_at in descending order (newest first).

    Query Parameters:
    - skip: Number of items to skip
    - limit: Maximum number of items to return (1-100)
    - sort: Sort field (created_at, updated_at). Prefix with - for descending order
    """
    try:
        comments, total = await comment_service.get_user_comments(
            username=current_user.username, skip=skip, limit=limit, sort=sort
        )
        return StandardResponse.paginated(comments, total, skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user comments: {str(e)}")
