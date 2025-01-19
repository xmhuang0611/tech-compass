from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth import get_current_active_user
from app.models.user import User, UserCreate, UserUpdate
from app.services.user_service import UserService

router = APIRouter()

@router.get("/me", response_model=User)
async def read_user_me(
    current_user: dict = Depends(get_current_active_user)
):
    """Get current user"""
    return current_user

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends()
) -> Any:
    """Create a new user."""
    return await user_service.create_user(user)

@router.get("/", response_model=dict)
async def get_users(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends()
) -> Any:
    """Get all users with pagination."""
    users = await user_service.get_users(skip=skip, limit=limit)
    total = await user_service.count_users()
    return {
        "items": users,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends()
) -> Any:
    """Get a specific user."""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends()
) -> Any:
    """Update a user."""
    user = await user_service.update_user(user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends()
) -> None:
    """Delete a user."""
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
