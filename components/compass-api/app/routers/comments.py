from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import get_current_active_user
from app.models.response import StandardResponse
from app.models.user import User
from app.services.comment_service import CommentService
from app.models.comment import CommentCreate, Comment, CommentUpdate, CommentInDB
from app.services.solution_service import SolutionService

router = APIRouter()

@router.get("/solution/{solution_slug}", response_model=StandardResponse[list[Comment]], tags=["comments"])
async def get_solution_comments(
    solution_slug: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at)$"),
):
    """
    Get all comments for a solution with pagination and sorting.
    Comments are sorted by created_at in descending order (newest first).
    
    - **solution_slug**: Unique identifier of the solution
    - **page**: Page number for pagination
    - **page_size**: Number of comments per page
    - **sort_by**: Field to sort by (currently only supports created_at)
    """
    comment_service = CommentService()
    skip = (page - 1) * page_size
    comments, total = await comment_service.get_solution_comments(
        solution_slug=solution_slug,
        skip=skip,
        limit=page_size,
        sort_by=sort_by
    )
    return StandardResponse.paginated(comments, total, skip, page_size)

@router.post("/solution/{solution_slug}/comment", response_model=StandardResponse[CommentInDB])
async def create_comment(
    solution_slug: str,
    comment: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    comment_service: CommentService = Depends(),
    solution_service: SolutionService = Depends()
) -> StandardResponse[CommentInDB]:
    """Create a new comment on a solution."""
    # Verify solution exists
    solution = await solution_service.get_solution_by_slug(solution_slug)
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution not found"
        )

    result = await comment_service.create_comment(
        solution_slug=solution_slug,
        comment=comment,
        username=current_user.username
    )
    return StandardResponse.of(result)

@router.get("/solution/{solution_slug}/comments", response_model=StandardResponse[List[CommentInDB]])
async def get_solution_comments(
    solution_slug: str,
    skip: int = 0,
    limit: int = 100,
    comment_service: CommentService = Depends(),
    solution_service: SolutionService = Depends()
) -> StandardResponse[List[CommentInDB]]:
    """Get all comments for a solution."""
    # Verify solution exists
    solution = await solution_service.get_solution_by_slug(solution_slug)
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution not found"
        )

    comments = await comment_service.get_solution_comments(
        solution_slug=solution_slug,
        skip=skip,
        limit=limit
    )
    total = await comment_service.count_solution_comments(solution_slug)
    return StandardResponse.paginated(
        data=comments,
        total=total,
        skip=skip,
        limit=limit
    )

@router.put("/{comment_id}", response_model=StandardResponse[CommentInDB])
async def update_comment(
    comment_id: str,
    comment_update: CommentUpdate,
    current_user: User = Depends(get_current_active_user),
    comment_service: CommentService = Depends()
) -> StandardResponse[CommentInDB]:
    """Update a comment.
    
    Only the comment creator or superusers can update it.
    """
    result = await comment_service.update_comment(
        comment_id=comment_id,
        comment_update=comment_update,
        username=current_user.username,
        is_superuser=current_user.is_superuser
    )
    return StandardResponse.of(result)

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_active_user),
    comment_service: CommentService = Depends()
) -> None:
    """Delete a comment.
    
    Only the comment creator or superusers can delete it.
    """
    success = await comment_service.delete_comment(
        comment_id=comment_id,
        username=current_user.username,
        is_superuser=current_user.is_superuser
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

@router.get("/", response_model=StandardResponse[list[Comment]], tags=["comments"])
async def get_all_comments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: str = Query("-created_at", description="Sort field (prefix with - for descending order)"),
    comment_service: CommentService = Depends()
):
    """
    Get all comments with pagination and sorting.
    Default sort is by created_at in descending order (newest first).
    
    - **page**: Page number for pagination
    - **page_size**: Number of comments per page
    - **sort**: Field to sort by (created_at). Prefix with - for descending order
    """
    try:
        skip = (page - 1) * page_size
        comments, total = await comment_service.get_comments(
            skip=skip,
            limit=page_size,
            sort=sort
        )
        return StandardResponse.paginated(comments, total, skip, page_size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting comments: {str(e)}")