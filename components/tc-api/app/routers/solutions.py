from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.core.auth import get_current_active_user
from app.models.solution import Solution, SolutionCreate, SolutionUpdate
from app.models.user import User
from app.services.solution_service import SolutionService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=Solution, status_code=status.HTTP_201_CREATED)
async def create_solution(
    solution: SolutionCreate,
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends()
) -> Any:
    """Create a new solution."""
    try:
        return await solution_service.create_solution(solution, current_user.username)
    except Exception as e:
        logger.error(f"Error creating solution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating solution: {str(e)}")

@router.get("/", response_model=dict)
async def get_solutions(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    department: Optional[str] = None,
    team: Optional[str] = None,
    recommend_status: Optional[str] = Query(None, description="Filter by recommendation status (BUY/HOLD/SELL)"),
    radar_status: Optional[str] = Query(None, description="Filter by radar status (ADOPT/TRIAL/ASSESS/HOLD)"),
    stage: Optional[str] = Query(None, description="Filter by stage (DEVELOPING/UAT/PRODUCTION/DEPRECATED/RETIRED)"),
    solution_service: SolutionService = Depends()
) -> Any:
    """Get all solutions with pagination and filtering.
    
    Query Parameters:
    - category: Filter by category name
    - department: Filter by department name
    - team: Filter by team name
    - recommend_status: Filter by recommendation status (BUY/HOLD/SELL)
    - radar_status: Filter by radar status (ADOPT/TRIAL/ASSESS/HOLD)
    - stage: Filter by stage (DEVELOPING/UAT/PRODUCTION/DEPRECATED/RETIRED)
    """
    try:
        # Validate enum values if provided
        if recommend_status and recommend_status not in ["BUY", "HOLD", "SELL"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid recommend_status. Must be one of: BUY, HOLD, SELL"
            )
        if radar_status and radar_status not in ["ADOPT", "TRIAL", "ASSESS", "HOLD"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid radar_status. Must be one of: ADOPT, TRIAL, ASSESS, HOLD"
            )
        if stage and stage not in ["DEVELOPING", "UAT", "PRODUCTION", "DEPRECATED", "RETIRED"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid stage. Must be one of: DEVELOPING, UAT, PRODUCTION, DEPRECATED, RETIRED"
            )

        solutions = await solution_service.get_solutions(
            skip=skip,
            limit=limit,
            category=category,
            department=department,
            team=team,
            recommend_status=recommend_status,
            radar_status=radar_status,
            stage=stage
        )
        total = await solution_service.count_solutions()
        return {
            "items": solutions,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error listing solutions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing solutions: {str(e)}")

@router.get("/{slug}", response_model=Solution)
async def get_solution(
    slug: str,
    solution_service: SolutionService = Depends()
) -> Any:
    """Get a specific solution by slug."""
    solution = await solution_service.get_solution_by_slug(slug)
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution not found"
        )
    return solution

@router.put("/{slug}", response_model=Solution)
async def update_solution(
    slug: str,
    solution_update: SolutionUpdate,
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends()
) -> Any:
    """Update a solution by slug."""
    try:
        solution = await solution_service.update_solution_by_slug(slug, solution_update, current_user.username)
        if not solution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solution not found"
            )
        return solution
    except Exception as e:
        logger.error(f"Error updating solution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating solution: {str(e)}")

@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_solution(
    slug: str,
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends()
) -> None:
    """Delete a solution by slug."""
    success = await solution_service.delete_solution_by_slug(slug)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution not found"
        )

@router.get("/{slug}/tags", response_model=List[str])
async def get_solution_tags(
    slug: str,
    solution_service: SolutionService = Depends()
) -> Any:
    """Get all tags for a specific solution by slug."""
    solution = await solution_service.get_solution_by_slug(slug)
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution not found"
        )
    return solution.tags if solution.tags else []

@router.post("/{slug}/tags/{tag_name}", status_code=status.HTTP_201_CREATED)
async def add_solution_tag(
    slug: str,
    tag_name: str,
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends()
) -> Any:
    """Add a tag to a solution. Creates the tag if it doesn't exist."""
    try:
        # Validate tag name is not empty
        if not tag_name or tag_name.isspace():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag name cannot be empty"
            )
        
        # Get the solution first
        solution = await solution_service.get_solution_by_slug(slug)
        if not solution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solution not found"
            )
        
        # Check if tag already exists in solution
        existing_tags = solution.tags or []
        if tag_name in existing_tags:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag '{tag_name}' is already added to this solution"
            )

        # Create tag if it doesn't exist and add it to solution
        solution_update = SolutionUpdate(tags=existing_tags + [tag_name])
        updated_solution = await solution_service.update_solution_by_slug(
            slug, 
            solution_update,
            current_user.username
        )
        if not updated_solution:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update solution with new tag"
            )
        
        return {"message": f"Tag '{tag_name}' added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding tag to solution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding tag to solution: {str(e)}"
        )

@router.delete("/{slug}/tags/{tag_name}", status_code=status.HTTP_200_OK)
async def delete_solution_tag(
    slug: str,
    tag_name: str,
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends()
) -> Any:
    """Remove a tag from a solution."""
    try:
        # Validate tag name is not empty
        if not tag_name or tag_name.isspace():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag name cannot be empty"
            )
        
        # Get the solution first
        solution = await solution_service.get_solution_by_slug(slug)
        if not solution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solution not found"
            )
        
        # Check if tag exists in solution
        existing_tags = solution.tags or []
        if tag_name not in existing_tags:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tag '{tag_name}' not found in this solution"
            )

        # Remove tag from solution
        updated_tags = [tag for tag in existing_tags if tag != tag_name]
        solution_update = SolutionUpdate(tags=updated_tags)
        updated_solution = await solution_service.update_solution_by_slug(
            slug, 
            solution_update,
            current_user.username
        )
        if not updated_solution:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update solution after removing tag"
            )
        
        return {"message": f"Tag '{tag_name}' removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing tag from solution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing tag from solution: {str(e)}"
        )
