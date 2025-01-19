from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.category import Category, CategoryCreate, CategoryUpdate
from app.services.category_service import CategoryService
from app.core.auth import get_current_user

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=Category)
async def create_category(
    category: CategoryCreate,
    current_user: dict = Depends(get_current_user),
    category_service: CategoryService = Depends()
):
    """Create a new category"""
    return await category_service.create_category(category, current_user.get("id"))

@router.get("/", response_model=List[Category])
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category_service: CategoryService = Depends()
):
    """List all categories with pagination"""
    return await category_service.get_categories(skip=skip, limit=limit)

@router.get("/{category_id}", response_model=Category)
async def get_category(
    category_id: str,
    category_service: CategoryService = Depends()
):
    """Get a specific category by ID"""
    category = await category_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/{category_id}", response_model=Category)
async def update_category(
    category_id: str,
    category_update: CategoryUpdate,
    current_user: dict = Depends(get_current_user),
    category_service: CategoryService = Depends()
):
    """Update a category"""
    category = await category_service.update_category(category_id, category_update, current_user.get("id"))
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    current_user: dict = Depends(get_current_user),
    category_service: CategoryService = Depends()
):
    """Delete a category"""
    success = await category_service.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}

@router.get("/name/{name}", response_model=Category)
async def get_category_by_name(
    name: str,
    category_service: CategoryService = Depends()
):
    """Get a category by name"""
    category = await category_service.get_category_by_name(name)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
