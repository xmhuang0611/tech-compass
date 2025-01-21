from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import get_current_active_user
from app.models.user import User
from app.services.comment_service import CommentService
from app.models.comment import CommentCreate, CommentInDB

router = APIRouter()

@router.get("/solution/{solution_slug}", response_model=dict, tags=["comments"])
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
    return {
        "status": "success",
        "data": comments,
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total
        }
    }

@router.post("/solution/{solution_slug}", response_model=dict, status_code=status.HTTP_201_CREATED, tags=["comments"])
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
        return {
            "status": "success",
            "data": new_comment
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating comment: {str(e)}"
        )

@router.put("/solution/{solution_slug}/comment/{comment_id}", response_model=dict, tags=["comments"])
async def update_comment(
    solution_slug: str,
    comment_id: str,
    comment: CommentCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a comment's content.
    
    - **solution_slug**: Unique identifier of the solution
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
    return {
        "status": "success",
        "data": updated_comment
    }

@router.delete("/solution/{solution_slug}/comment/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["comments"])
async def delete_comment(
    solution_slug: str,
    comment_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a comment.
    
    - **solution_slug**: Unique identifier of the solution
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