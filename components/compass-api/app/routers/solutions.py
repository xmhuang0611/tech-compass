import logging
from typing import Any, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response

from app.core.auth import get_current_active_user, get_current_superuser
from app.models.history import HistoryRecord
from app.models.response import StandardResponse
from app.models.solution import Solution, SolutionCreate, SolutionInDB, SolutionUpdate
from app.models.user import User
from app.services.comment_service import CommentService
from app.services.history_service import HistoryService
from app.services.rating_service import RatingService
from app.services.solution_service import SolutionService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=StandardResponse[SolutionInDB],
    status_code=status.HTTP_201_CREATED,
)
async def create_solution(
    solution: SolutionCreate,
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends(),
) -> Any:
    """Create a new solution."""
    try:
        solution_in_db = await solution_service.create_solution(solution, current_user.username)
        return StandardResponse.of(solution_in_db)
    except Exception as e:
        logger.error(f"Error creating solution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating solution: {str(e)}")


@router.get("/", response_model=StandardResponse[List[Solution]])
async def get_solutions(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    department: Optional[str] = None,
    team: Optional[str] = None,
    recommend_status: Optional[str] = Query(
        None, description="Filter by recommendation status (ADOPT/TRIAL/ASSESS/HOLD)"
    ),
    stage: Optional[str] = Query(
        None,
        description="Filter by stage (DEVELOPING/UAT/PRODUCTION/DEPRECATED/RETIRED)",
    ),
    review_status: Optional[str] = Query(None, description="Filter by review status (PENDING/APPROVED/REJECTED)"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated list of tag names)"),
    sort: str = Query("name", description="Sort field (prefix with - for descending order)"),
    solution_service: SolutionService = Depends(),
) -> Any:
    """Get all solutions with pagination, filtering and sorting.

    Query Parameters:
    - category: Filter by category name
    - department: Filter by department name
    - team: Filter by team name
    - recommend_status: Filter by recommendation status (ADOPT/TRIAL/ASSESS/HOLD)
    - stage: Filter by stage (DEVELOPING/UAT/PRODUCTION/DEPRECATED/RETIRED)
    - review_status: Filter by review status (PENDING/APPROVED/REJECTED)
    - tags: Filter by tags (comma-separated list of tag names)
    - sort: Sort field (name, category, created_at, updated_at). Prefix with - for descending order
    """
    try:
        # Validate enum values if provided
        if recommend_status and recommend_status not in [
            "ADOPT",
            "TRIAL",
            "ASSESS",
            "HOLD",
        ]:
            raise HTTPException(
                status_code=400,
                detail="Invalid recommend_status. Must be one of: ADOPT, TRIAL, ASSESS, HOLD",
            )
        if stage and stage not in [
            "DEVELOPING",
            "UAT",
            "PRODUCTION",
            "DEPRECATED",
            "RETIRED",
        ]:
            raise HTTPException(
                status_code=400,
                detail="Invalid stage. Must be one of: DEVELOPING, UAT, PRODUCTION, DEPRECATED, RETIRED",
            )
        if review_status and review_status not in ["PENDING", "APPROVED", "REJECTED"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid review_status. Must be one of: PENDING, APPROVED, REJECTED",
            )

        # Process tags if provided
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]

        solutions = await solution_service.get_solutions_with_ratings(
            skip=skip,
            limit=limit,
            category=category,
            department=department,
            team=team,
            recommend_status=recommend_status,
            stage=stage,
            review_status=review_status,
            tags=tag_list,
            sort=sort,
        )
        total = await solution_service.count_solutions()
        return StandardResponse.paginated(data=solutions, total=total, skip=skip, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing solutions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing solutions: {str(e)}")


@router.get("/departments", response_model=StandardResponse[List[str]], tags=["solutions"])
async def get_departments(solution_service: SolutionService = Depends()):
    """
    Get all unique department names from solutions.

    Returns:
    - items: List of unique department names
    - total: Total number of unique departments
    """
    try:
        departments = await solution_service.get_departments()
        return StandardResponse.paginated(departments, len(departments), 0, 0)
    except Exception as e:
        logger.error(f"Error getting departments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting departments: {str(e)}")


@router.get("/search/", response_model=StandardResponse[List[Solution]])
async def search_solutions(
    keyword: str = Query(..., description="Search keyword to match against solution fields"),
    solution_service: SolutionService = Depends(),
) -> Any:
    """Search solutions by keyword using text similarity.
    Searches across name, category, description, team, maintainer name, pros and cons.
    Returns all matches sorted by relevance score.
    """
    try:
        solutions = await solution_service.search_solutions(keyword)
        return StandardResponse.of(solutions)
    except Exception as e:
        logger.error(f"Error searching solutions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching solutions: {str(e)}")


@router.get("/my/", response_model=StandardResponse[List[Solution]])
async def get_my_solutions(
    skip: int = 0,
    limit: int = 10,
    sort: str = Query(
        "name",
        description="Sort field (name, category, created_at, updated_at). Prefix with - for descending order",
    ),
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends(),
) -> Any:
    """Get all solutions created by or maintained by the current user with pagination and sorting.

    Query Parameters:
    - sort: Sort field (name, category, created_at, updated_at). Prefix with - for descending order
    """
    try:
        solutions = await solution_service.get_user_solutions(
            username=current_user.username, skip=skip, limit=limit, sort=sort
        )
        total = await solution_service.count_user_solutions(current_user.username)
        return StandardResponse.paginated(data=solutions, total=total, skip=skip, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing user solutions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing user solutions: {str(e)}")


@router.get("/{slug}", response_model=StandardResponse[Solution])
async def get_solution(slug: str, solution_service: SolutionService = Depends()) -> Any:
    """Get a specific solution by slug."""
    solution = await solution_service.get_solution_by_slug_with_rating(slug)
    if not solution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found")
    return StandardResponse.of(solution)


@router.put("/{slug}", response_model=StandardResponse[SolutionInDB])
async def update_solution(
    slug: str,
    solution_update: SolutionUpdate,
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends(),
) -> Any:
    """Update a solution by slug.

    Only superusers or the solution's creator/maintainer can update it.
    """
    try:
        # Get existing solution first
        existing_solution = await solution_service.get_solution_by_slug(slug)
        if not existing_solution:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found")

        # Check user permission
        has_permission = await solution_service.check_user_solution_permission(
            solution=existing_solution,
            username=current_user.username,
            is_superuser=current_user.is_superuser,
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this solution",
            )

        # Check if review_status is being updated and user is not a superuser
        if solution_update.review_status is not None and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only superusers can modify the review status",
            )

        solution_in_db = await solution_service.update_solution_by_slug(slug, solution_update, current_user.username)
        return StandardResponse.of(solution_in_db)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating solution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating solution: {str(e)}")


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_solution(
    slug: str,
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends(),
) -> None:
    """Delete a solution by slug.

    Only superusers or the solution's creator/maintainer can delete it.
    """
    # Get existing solution first
    existing_solution = await solution_service.get_solution_by_slug(slug)
    if not existing_solution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found")

    # Check user permission
    has_permission = await solution_service.check_user_solution_permission(
        solution=existing_solution,
        username=current_user.username,
        is_superuser=current_user.is_superuser,
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this solution",
        )

    success = await solution_service.delete_solution_by_slug(slug, current_user.username)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found")


@router.get("/check-name/{name}", response_model=StandardResponse[Tuple[bool, int]])
async def check_solution_name(name: str, solution_service: SolutionService = Depends()) -> Any:
    """Check if a solution name exists and get count of similar names.

    Returns:
    - exists: True if the exact name exists
    - count: Number of solutions with similar names (case-insensitive)
    """
    try:
        exists, count = await solution_service.check_name_exists(name)
        return StandardResponse.of((exists, count))
    except Exception as e:
        logger.error(f"Error checking solution name: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking solution name: {str(e)}")


@router.delete("/by-name/{name}", status_code=status.HTTP_200_OK)
async def delete_solutions_by_name(
    name: str,
    current_user: User = Depends(get_current_superuser),
    solution_service: SolutionService = Depends(),
) -> Any:
    """Delete all solutions with the exact name (case-sensitive).

    This endpoint is restricted to superusers only.
    """
    try:
        deleted_count = await solution_service.delete_solutions_by_name(name, current_user.username)
        return StandardResponse.of(deleted_count)
    except Exception as e:
        logger.error(f"Error deleting solutions by name: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting solutions by name: {str(e)}")


@router.put("/by-name/{name}", response_model=StandardResponse[List[SolutionInDB]])
async def update_solutions_by_name(
    name: str,
    solution_update: SolutionUpdate,
    current_user: User = Depends(get_current_superuser),
    solution_service: SolutionService = Depends(),
) -> Any:
    """Update all solutions with the exact name (case-sensitive).

    This endpoint is restricted to superusers only.
    """
    try:
        # Check if any solutions exist with this name
        exists, _ = await solution_service.check_name_exists(name)
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No solutions found with this name",
            )

        updated_solutions = await solution_service.update_solutions_by_name(
            name, solution_update, current_user.username
        )
        return StandardResponse.of(updated_solutions)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating solutions by name: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating solutions by name: {str(e)}")


@router.get("/{slug}/adopted-users", response_model=StandardResponse[List[User]])
async def get_solution_adopted_users(
    slug: str,
    solution_service: SolutionService = Depends(),
    comment_service: CommentService = Depends(),
    rating_service: RatingService = Depends(),
    user_service: UserService = Depends(),
) -> Any:
    """Get all adopted users for a solution.

    This endpoint returns a list of users who have marked themselves as adopted users
    either through comments or ratings on the solution.

    Args:
        slug: The slug of the solution to get adopted users for

    Returns:
        List of User objects for all adopted users with total count
    """
    try:
        # First check if solution exists
        solution = await solution_service.get_solution_by_slug(slug)
        if not solution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Solution with slug '{slug}' not found",
            )

        # Get adopted usernames from both comments and ratings
        comment_usernames = await comment_service.get_solution_adopted_usernames(slug)
        rating_usernames = await rating_service.get_solution_adopted_usernames(slug)

        # Combine unique usernames
        all_usernames = comment_usernames.union(rating_usernames)

        if not all_usernames:
            return StandardResponse.paginated(data=[], total=0, skip=0, limit=0)

        # Get full user information for all usernames
        users = await user_service.get_users_by_usernames(list(all_usernames))
        return StandardResponse.paginated(data=users, total=len(users), skip=0, limit=len(users))

    except Exception as e:
        logger.error(f"Error getting adopted users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting adopted users: {str(e)}",
        )


@router.get("/{slug}/history", response_model=StandardResponse[List[HistoryRecord]])
async def get_solution_history(
    slug: str,
    skip: int = 0,
    limit: int = 20,
    solution_service: SolutionService = Depends(),
    history_service: HistoryService = Depends(),
) -> Any:
    """
    Get change history for a specific solution.

    Returns a list of history records for the solution, sorted by change date in descending order.
    """
    solution = await solution_service.get_solution_by_slug(slug)
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solution with slug '{slug}' not found",
        )

    history_records, total = await history_service.get_object_history(
        object_type="solution", object_id=str(solution.id), skip=skip, limit=limit
    )

    return StandardResponse.paginated(history_records, total, skip, limit)
