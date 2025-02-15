from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response

from app.core.auth import get_current_superuser
from app.models.category import Category, CategoryCreate, CategoryUpdate
from app.models.response import StandardResponse
from app.models.user import User
from app.services.category_service import CategoryService

router = APIRouter()


@router.post("/", response_model=StandardResponse[Category], status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_superuser),
    category_service: CategoryService = Depends(),
) -> StandardResponse[Category]:
    """Create a new category (superuser only)."""
    try:
        result = await category_service.create_category(category, current_user.username)
        category_with_usage = await category_service.get_category_with_usage(result)
        return StandardResponse.of(category_with_usage)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=StandardResponse[List[Category]])
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    sort: str = Query("radar_quadrant", description="Sort field (prefix with - for descending order)"),
    category_service: CategoryService = Depends(),
) -> StandardResponse[List[Category]]:
    """Get all categories with pagination and sorting. Default sorting is by radar_quadrant ascending."""
    categories = await category_service.get_categories(skip=skip, limit=limit, sort=sort)
    total = await category_service.count_categories()

    # Convert to Category model with usage count
    categories_with_usage = []
    for category in categories:
        category_with_usage = await category_service.get_category_with_usage(category)
        categories_with_usage.append(category_with_usage)

    return StandardResponse.paginated(data=categories_with_usage, total=total, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=StandardResponse[Category])
async def get_category(category_id: str, category_service: CategoryService = Depends()) -> StandardResponse[Category]:
    """Get a specific category by ID."""
    category = await category_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    category_with_usage = await category_service.get_category_with_usage(category)
    return StandardResponse.of(category_with_usage)


@router.put("/{category_id}", response_model=StandardResponse[Category])
async def update_category(
    category_id: str,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_superuser),
    category_service: CategoryService = Depends(),
) -> StandardResponse[Category]:
    """Update a category by ID (superuser only)."""
    try:
        category = await category_service.update_category_by_id(category_id, category_update, current_user.username)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        category_with_usage = await category_service.get_category_with_usage(category)
        return StandardResponse.of(category_with_usage)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_superuser),
    category_service: CategoryService = Depends(),
) -> None:
    """Delete a category by ID (superuser only). Will return 400 error if category is being used by any solutions."""
    try:
        success = await category_service.delete_category_by_id(category_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
