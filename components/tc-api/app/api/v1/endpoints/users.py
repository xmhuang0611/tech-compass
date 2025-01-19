from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User, UserCreate, UserUpdate
from app.services.user_service import UserService
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/me", response_model=User)
async def read_user_me(
    current_user: dict = Depends(get_current_user)
):
    """Get current user"""
    return current_user

@router.post("/", response_model=User)
async def create_user(
    user: UserCreate,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Create new user. Only superusers can create new users."""
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=403,
            detail="Only superusers can create new users"
        )
    
    try:
        return await user_service.create_user(user, current_user.get("id"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Get a specific user by ID"""
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Update a user"""
    if not current_user.get("is_superuser") and current_user.get("id") != user_id:
        raise HTTPException(
            status_code=403,
            detail="Only superusers can update other users"
        )
    
    try:
        user = await user_service.update_user(user_id, user_update, current_user.get("id"))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Delete a user"""
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=403,
            detail="Only superusers can delete users"
        )
    
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
