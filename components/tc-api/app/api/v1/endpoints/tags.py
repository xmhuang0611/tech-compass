from typing import List
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_db, get_current_active_user
from app.db.models import Tag
from bson import ObjectId

router = APIRouter()

@router.get("/", response_model=List[Tag])
async def list_tags(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    List all tags.
    """
    cursor = db.tags.find()
    tags = await cursor.to_list(length=100)
    return tags

@router.post("/", response_model=Tag)
async def create_tag(
    tag: Tag,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create a new tag.
    """
    tag.created_by = str(current_user["_id"])
    tag.updated_by = str(current_user["_id"])
    
    # Check if tag already exists
    existing_tag = await db.tags.find_one({"name": tag.name})
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag already exists")
    
    result = await db.tags.insert_one(tag.dict())
    created_tag = await db.tags.find_one({"_id": result.inserted_id})
    return created_tag

@router.put("/{tag_id}", response_model=Tag)
async def update_tag(
    tag_id: str,
    tag_update: Tag,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update a tag.
    """
    tag_update.updated_by = str(current_user["_id"])
    update_data = tag_update.dict(exclude_unset=True)
    
    result = await db.tags.update_one(
        {"_id": ObjectId(tag_id)},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Tag not found")
        
    updated_tag = await db.tags.find_one({"_id": ObjectId(tag_id)})
    return updated_tag

@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Delete a tag.
    """
    # Check if tag is being used by any solutions
    solutions_using_tag = await db.solutions.find_one({"tags": tag_id})
    if solutions_using_tag:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete tag as it is being used by solutions"
        )
    
    result = await db.tags.delete_one({"_id": ObjectId(tag_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"status": "success", "message": "Tag deleted successfully"}
