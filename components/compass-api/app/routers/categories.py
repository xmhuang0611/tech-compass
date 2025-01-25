from typing import Any

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
    limit: int = 100,
    category_service: CategoryService = Depends()
) -> Any:
    """Get all categories with pagination. Default limit is 100 items."""
    categories = await category_service.get_categories(skip=skip, limit=limit)
    total = await category_service.count_categories()
    return {
        "items": categories,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{name}", response_model=Category)
async def get_category(
    name: str,
    category_service: CategoryService = Depends()
) -> Any:
    """Get a specific category by name."""
    category = await category_service.get_category_by_name(name)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@router.put("/{name}", response_model=Category)
async def update_category(
    name: str,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    category_service: CategoryService = Depends()
) -> Any:
    """Update a category by name."""
    try:
        category = await category_service.update_category_by_name(name, category_update, current_user.username)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        return category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    name: str,
    current_user: User = Depends(get_current_active_user),
    category_service: CategoryService = Depends()
) -> None:
    """Delete a category by name. Will return 400 error if category is being used by any solutions."""
    try:
        success = await category_service.delete_category_by_name(name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
