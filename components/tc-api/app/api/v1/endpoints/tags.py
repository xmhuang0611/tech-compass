from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.tag import Tag, TagCreate, TagUpdate, TagList
from app.services.tag_service import TagService
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=TagList)
async def list_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    tag_service: TagService = Depends()
):
    """List all tags with pagination"""
    return await tag_service.get_tags(skip=skip, limit=limit)

@router.post("/", response_model=Tag)
async def create_tag(
    tag: TagCreate,
    current_user: dict = Depends(get_current_user),
    tag_service: TagService = Depends()
):
    """Create a new tag"""
    try:
        return await tag_service.create_tag(tag, current_user.get("id"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{tag_id}", response_model=Tag)
async def get_tag(
    tag_id: str,
    tag_service: TagService = Depends()
):
    """Get a specific tag by ID"""
    tag = await tag_service.get_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

@router.put("/{tag_id}", response_model=Tag)
async def update_tag(
    tag_id: str,
    tag_update: TagUpdate,
    current_user: dict = Depends(get_current_user),
    tag_service: TagService = Depends()
):
    """Update a tag"""
    try:
        tag = await tag_service.update_tag(tag_id, tag_update, current_user.get("id"))
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        return tag
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: str,
    current_user: dict = Depends(get_current_user),
    tag_service: TagService = Depends()
):
    """Delete a tag"""
    try:
        success = await tag_service.delete_tag(tag_id)
        if not success:
            raise HTTPException(status_code=404, detail="Tag not found")
        return {"status": "success", "message": "Tag deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/solution/{solution_id}", response_model=TagList)
async def get_solution_tags(
    solution_id: str,
    tag_service: TagService = Depends()
):
    """Get all tags for a specific solution"""
    return await tag_service.get_solution_tags(solution_id)

@router.post("/solution/{solution_id}/tags/{tag_id}")
async def add_solution_tag(
    solution_id: str,
    tag_id: str,
    current_user: dict = Depends(get_current_user),
    tag_service: TagService = Depends()
):
    """Add a tag to a solution"""
    try:
        success = await tag_service.add_solution_tag(solution_id, tag_id)
        if not success:
            raise HTTPException(status_code=404, detail="Solution or tag not found")
        return {"status": "success", "message": "Tag added to solution successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/solution/{solution_id}/tags/{tag_id}")
async def remove_solution_tag(
    solution_id: str,
    tag_id: str,
    current_user: dict = Depends(get_current_user),
    tag_service: TagService = Depends()
):
    """Remove a tag from a solution"""
    success = await tag_service.remove_solution_tag(solution_id, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Solution or tag not found")
    return {"status": "success", "message": "Tag removed from solution successfully"}
