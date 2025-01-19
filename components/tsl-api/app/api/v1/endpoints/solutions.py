from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_db, get_current_active_user
from app.db.models import Solution
from bson import ObjectId
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[Solution])
async def list_solutions(
    db: AsyncIOMotorDatabase = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    status: Optional[str] = None,
    department: Optional[str] = None,
):
    """
    List technical solutions with optional filtering.
    """
    try:
        query = {}
        if category:
            query["category"] = category
        if status:
            query["status"] = status
        if department:
            query["department"] = department

        logger.info(f"Fetching solutions with query: {query}")
        cursor = db.solutions.find(query).skip(skip).limit(limit)
        solutions = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for solution in solutions:
            solution["_id"] = str(solution["_id"])
            
        return solutions
    except Exception as e:
        logger.error(f"Error listing solutions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing solutions: {str(e)}")

@router.get("/{solution_id}", response_model=Solution)
async def get_solution(
    solution_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get a specific technical solution by ID.
    """
    solution = await db.solutions.find_one({"_id": ObjectId(solution_id)})
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")
    return solution

@router.post("/", response_model=Solution)
async def create_solution(
    solution: Solution,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create a new technical solution.
    """
    try:
        # Convert solution to dict and set audit fields
        solution_dict = solution.model_dump(exclude={"id"})
        now = datetime.utcnow()
        
        # Set audit fields
        solution_dict.update({
            "created_by": current_user["username"],
            "updated_by": current_user["username"],
            "created_at": now,
            "updated_at": now
        })
        
        logger.info(f"Creating solution: {solution_dict}")
        result = await db.solutions.insert_one(solution_dict)
        
        # Fetch and return the created solution
        created_solution = await db.solutions.find_one({"_id": result.inserted_id})
        if created_solution:
            # Convert ObjectId to string
            created_solution["_id"] = str(created_solution["_id"])
            return Solution(**created_solution)
        else:
            raise HTTPException(status_code=404, detail="Created solution not found")
    except Exception as e:
        logger.error(f"Error creating solution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating solution: {str(e)}")

@router.put("/{solution_id}", response_model=Solution)
async def update_solution(
    solution_id: str,
    solution_update: Solution,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update a technical solution.
    """
    try:
        solution_update.updated_by = current_user["username"]
        update_data = solution_update.model_dump(exclude_unset=True)
        
        logger.info(f"Updating solution {solution_id}: {update_data}")
        result = await db.solutions.update_one(
            {"_id": ObjectId(solution_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Solution not found")
        
        updated_solution = await db.solutions.find_one({"_id": ObjectId(solution_id)})
        if updated_solution:
            # Convert ObjectId to string for the _id field
            updated_solution["_id"] = str(updated_solution["_id"])
            return Solution(**updated_solution)
        else:
            raise HTTPException(status_code=404, detail="Updated solution not found")
    except Exception as e:
        logger.error(f"Error updating solution {solution_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating solution {solution_id}: {str(e)}")

@router.delete("/{solution_id}")
async def delete_solution(
    solution_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Delete a technical solution.
    """
    try:
        logger.info(f"Deleting solution {solution_id}")
        result = await db.solutions.delete_one({"_id": ObjectId(solution_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Solution not found")
        return {"status": "success", "message": "Solution deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting solution {solution_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting solution {solution_id}: {str(e)}")
