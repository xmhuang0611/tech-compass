from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.solution import Solution, SolutionCreate, SolutionUpdate
from app.services.solution_service import SolutionService
from app.core.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=Solution)
async def create_solution(
    solution: SolutionCreate,
    current_user: dict = Depends(get_current_user),
    solution_service: SolutionService = Depends()
):
    """Create a new technical solution"""
    try:
        return await solution_service.create_solution(solution, current_user.get("id"))
    except Exception as e:
        logger.error(f"Error creating solution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating solution: {str(e)}")

@router.get("/", response_model=List[Solution])
async def list_solutions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    status: Optional[str] = None,
    department: Optional[str] = None,
    solution_service: SolutionService = Depends()
):
    """List technical solutions with optional filtering"""
    try:
        return await solution_service.get_solutions(
            skip=skip,
            limit=limit,
            category=category,
            status=status,
            department=department
        )
    except Exception as e:
        logger.error(f"Error listing solutions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing solutions: {str(e)}")

@router.get("/{solution_id}", response_model=Solution)
async def get_solution(
    solution_id: str,
    solution_service: SolutionService = Depends()
):
    """Get a specific technical solution by ID"""
    solution = await solution_service.get_solution_by_id(solution_id)
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")
    return solution

@router.put("/{solution_id}", response_model=Solution)
async def update_solution(
    solution_id: str,
    solution_update: SolutionUpdate,
    current_user: dict = Depends(get_current_user),
    solution_service: SolutionService = Depends()
):
    """Update a technical solution"""
    try:
        solution = await solution_service.update_solution(
            solution_id,
            solution_update,
            current_user.get("id")
        )
        if not solution:
            raise HTTPException(status_code=404, detail="Solution not found")
        return solution
    except Exception as e:
        logger.error(f"Error updating solution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating solution: {str(e)}")

@router.delete("/{solution_id}")
async def delete_solution(
    solution_id: str,
    current_user: dict = Depends(get_current_user),
    solution_service: SolutionService = Depends()
):
    """Delete a technical solution"""
    success = await solution_service.delete_solution(solution_id)
    if not success:
        raise HTTPException(status_code=404, detail="Solution not found")
    return {"message": "Solution deleted successfully"}
