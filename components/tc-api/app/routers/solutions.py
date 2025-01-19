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
        return await solution_service.create_solution(solution, current_user)
    except Exception as e:
        logger.error(f"Error creating solution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating solution: {str(e)}")

@router.get("/", response_model=dict)
async def get_solutions(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends()
) -> Any:
    """Get all solutions with pagination."""
    try:
        solutions = await solution_service.get_solutions(skip=skip, limit=limit)
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

@router.get("/{solution_id}", response_model=Solution)
async def get_solution(
    solution_id: str,
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends()
) -> Any:
    """Get a specific solution."""
    solution = await solution_service.get_solution(solution_id)
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution not found"
        )
    return solution

@router.put("/{solution_id}", response_model=Solution)
async def update_solution(
    solution_id: str,
    solution_update: SolutionUpdate,
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends()
) -> Any:
    """Update a solution."""
    try:
        solution = await solution_service.update_solution(solution_id, solution_update)
        if not solution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solution not found"
            )
        return solution
    except Exception as e:
        logger.error(f"Error updating solution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating solution: {str(e)}")

@router.delete("/{solution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_solution(
    solution_id: str,
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends()
) -> None:
    """Delete a solution."""
    success = await solution_service.delete_solution(solution_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution not found"
        )
