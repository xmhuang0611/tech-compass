from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth import get_current_active_user
from app.models.category import Category, CategoryCreate, CategoryUpdate
from app.models.user import User
from app.services.category_service import CategoryService

router = APIRouter()

@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    category_service: CategoryService = Depends()
) -> Any:
    """Create a new category."""
    try:
        return await category_service.create_category(category, current_user.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=dict)
async def get_categories(
    skip: int = 0,
    limit: int = 10,
    category_service: CategoryService = Depends()
) -> Any:
    """Get all categories with pagination."""
    categories = await category_service.get_categories(skip=skip, limit=limit)
    total = await category_service.count_categories()
    return {
        "items": categories,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{category_id}", response_model=Category)
async def get_category(
    category_id: str,
    category_service: CategoryService = Depends()
) -> Any:
    """Get a specific category."""
    category = await category_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@router.put("/{category_id}", response_model=Category)
async def update_category(
    category_id: str,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    category_service: CategoryService = Depends()
) -> Any:
    """Update a category."""
    try:
        category = await category_service.update_category(category_id, category_update, current_user.username)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        return category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_active_user),
    category_service: CategoryService = Depends()
) -> None:
    """Delete a category."""
    success = await category_service.delete_category(category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

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
