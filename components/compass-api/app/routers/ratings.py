from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import get_current_active_user
from app.models.rating import Rating, RatingCreate
from app.models.response import StandardResponse
from app.models.user import User
from app.services.rating_service import RatingService

router = APIRouter()


@router.get(
    "/solution/{solution_slug}",
    response_model=StandardResponse[List[Rating]],
    tags=["ratings"],
)
async def get_solution_ratings(
    solution_slug: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at|score)$"),
):
    """
    Get all ratings for a solution with pagination and sorting.

    - **solution_slug**: Unique identifier of the solution
    - **page**: Page number for pagination
    - **page_size**: Number of ratings per page
    - **sort_by**: Field to sort by (created_at or score)
    """
    rating_service = RatingService()
    skip = (page - 1) * page_size
    ratings, total = await rating_service.get_solution_ratings(
        solution_slug=solution_slug, skip=skip, limit=page_size, sort_by=sort_by
    )
    return StandardResponse.paginated(data=ratings, total=total, skip=skip, limit=page_size)


@router.get(
    "/solution/{solution_slug}/me",
    response_model=StandardResponse[Rating],
    tags=["ratings"],
)
async def get_user_rating(solution_slug: str, current_user: User = Depends(get_current_active_user)):
    """
    Get the current user's rating for a solution.

    - **solution_slug**: Unique identifier of the solution
    """
    rating_service = RatingService()
    rating = await rating_service.get_user_rating(solution_slug, current_user.username)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    return StandardResponse.of(rating)


@router.post(
    "/solution/{solution_slug}",
    response_model=StandardResponse[Rating],
    status_code=status.HTTP_201_CREATED,
    tags=["ratings"],
)
async def create_or_update_rating(
    solution_slug: str,
    rating: RatingCreate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Create or update a rating for a solution.

    - **solution_slug**: Unique identifier of the solution
    - **rating**: Rating details including score and optional comment
    """
    rating_service = RatingService()
    try:
        updated_rating = await rating_service.create_or_update_rating(
            solution_slug=solution_slug, rating=rating, username=current_user.username
        )
        return StandardResponse.of(updated_rating)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating/updating rating: {str(e)}",
        )


@router.get(
    "/solution/{solution_slug}/summary",
    response_model=StandardResponse[dict],
    tags=["ratings"],
)
async def get_solution_rating_summary(
    solution_slug: str,
):
    """
    Get rating summary statistics for a solution.

    Returns:
    - average: Average rating score
    - count: Total number of ratings
    - distribution: Count of ratings for each score (1-5)
    """
    rating_service = RatingService()
    summary = await rating_service.get_rating_summary(solution_slug)
    return StandardResponse.of(summary)


@router.get("/", response_model=StandardResponse[List[Rating]], tags=["ratings"])
async def get_all_ratings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: str = Query("-created_at", description="Sort field (prefix with - for descending order)"),
    solution_slug: Optional[str] = Query(
        None, description="Filter ratings by solution slug (supports partial matching)"
    ),
    score: Optional[int] = Query(None, ge=1, le=5, description="Filter ratings by exact score (1-5)"),
    rating_service: RatingService = Depends(),
):
    """
    Get all ratings with pagination and sorting.
    Default sort is by created_at in descending order (newest first).

    - **page**: Page number for pagination
    - **page_size**: Number of ratings per page
    - **sort**: Field to sort by (created_at, updated_at, score). Prefix with - for descending order
    - **solution_slug**: Filter ratings by solution slug (supports partial matching)
    - **score**: Filter ratings by exact score (1-5)
    """
    try:
        skip = (page - 1) * page_size
        ratings, total = await rating_service.get_ratings(
            skip=skip,
            limit=page_size,
            sort=sort,
            solution_slug=solution_slug,
            score=score,
        )
        return StandardResponse.paginated(data=ratings, total=total, skip=skip, limit=page_size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ratings: {str(e)}")


@router.get("/my/", response_model=StandardResponse[list[Rating]], tags=["ratings"])
async def get_my_ratings(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of items to return"),
    sort: str = Query("-created_at", description="Sort field (prefix with - for descending order)"),
    current_user: User = Depends(get_current_active_user),
    rating_service: RatingService = Depends(),
) -> StandardResponse[list[Rating]]:
    """
    Get all ratings created by the current user with pagination and sorting.
    Default sort is by created_at in descending order (newest first).

    Query Parameters:
    - skip: Number of items to skip
    - limit: Maximum number of items to return (1-100)
    - sort: Sort field (created_at, updated_at, score). Prefix with - for descending order
    """
    try:
        ratings, total = await rating_service.get_user_ratings(
            username=current_user.username, skip=skip, limit=limit, sort=sort
        )
        return StandardResponse.paginated(ratings, total, skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user ratings: {str(e)}")


@router.put("/{rating_id}", response_model=StandardResponse[Rating], tags=["ratings"])
async def update_rating(
    rating_id: str,
    rating_update: RatingCreate,
    current_user: User = Depends(get_current_active_user),
    rating_service: RatingService = Depends(),
) -> StandardResponse[Rating]:
    """
    Update a rating by ID.
    Only the rating creator or superusers can update it.

    Path Parameters:
    - rating_id: ID of the rating to update

    Request Body:
    - score: New rating score (1-5)
    - comment: Optional new comment
    - is_adopted_user: Whether you are an adopted user for this solution (default: false)
    """
    try:
        updated_rating = await rating_service.update_rating(
            rating_id=rating_id,
            rating_update=rating_update,
            username=current_user.username,
            is_superuser=current_user.is_superuser,
        )
        if not updated_rating:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
        return StandardResponse.of(updated_rating)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating rating: {str(e)}",
        )


@router.delete("/{rating_id}", response_model=StandardResponse[bool], tags=["ratings"])
async def delete_rating(
    rating_id: str,
    current_user: User = Depends(get_current_active_user),
    rating_service: RatingService = Depends(),
) -> StandardResponse[bool]:
    """
    Delete a rating by ID.
    Only the rating creator or superusers can delete it.

    Path Parameters:
    - rating_id: ID of the rating to delete
    """
    try:
        success = await rating_service.delete_rating(
            rating_id=rating_id,
            username=current_user.username,
            is_superuser=current_user.is_superuser,
        )
        return StandardResponse.of(success)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting rating: {str(e)}",
        )
