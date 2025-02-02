from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import get_current_active_user
from app.models.response import StandardResponse
from app.models.user import User
from app.services.comment_service import CommentService
from app.models.comment import CommentCreate, Comment

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

@router.post("/solution/{solution_slug}", response_model=StandardResponse[Comment], status_code=status.HTTP_201_CREATED, tags=["comments"])
async def create_comment(
    solution_slug: str,
    comment: CommentCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new comment for a solution.
    
    - **solution_slug**: Unique identifier of the solution
    - **comment**: Comment details including content
    """
    comment_service = CommentService()
    try:
        new_comment = await comment_service.create_comment(
            solution_slug=solution_slug,
            comment=comment,
            username=current_user.username
        )
        return StandardResponse.of(new_comment)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating comment: {str(e)}"
        )

@router.put("/{comment_id}",
            response_model=StandardResponse[Comment], 
            tags=["comments"])
async def update_comment(
    comment_id: str,
    comment: CommentCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a comment's content.
    - **comment_id**: Unique identifier of the comment
    - **comment**: Updated comment content
    """
    comment_service = CommentService()
    updated_comment = await comment_service.update_comment(
        comment_id=comment_id,
        content=comment.content,
        username=current_user.username
    )
    if not updated_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to update it"
        )
    return StandardResponse.of(updated_comment)

@router.delete("/{comment_id}", 
            status_code=status.HTTP_204_NO_CONTENT, 
            tags=["comments"])
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a comment.
    
    - **comment_id**: Unique identifier of the comment
    """
    comment_service = CommentService()
    success = await comment_service.delete_comment(
        comment_id=comment_id,
        username=current_user.username
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to delete it"
        )
    return StandardResponse.of(None)
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