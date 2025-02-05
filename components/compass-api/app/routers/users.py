from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_active_user
from app.models.user import User, UserCreate, UserUpdate
from app.services.user_service import UserService
from app.models.response import StandardResponse

router = APIRouter()

@router.post("/", response_model=StandardResponse[User], status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    user_service: UserService = Depends()
) -> Any:
    """Create a new user."""
    try:
        result = await user_service.create_user(user)
        return StandardResponse.of(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=StandardResponse[List[User]])
async def get_users(
    skip: int = 0,
    limit: int = 10,
    user_service: UserService = Depends()
) -> Any:
    """Get all users with pagination."""
    users = await user_service.get_users(skip=skip, limit=limit)
    total = await user_service.count_users()
    return StandardResponse.paginated(
        data=users,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/me", response_model=StandardResponse[User])
async def read_user_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get current user."""
    return StandardResponse.of(current_user)

@router.get("/{username}", response_model=StandardResponse[User])
async def get_user(
    username: str,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends()
) -> Any:
    """Get a specific user by username."""
    user = await user_service.get_user_for_api(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return StandardResponse.of(user)

@router.put("/{username}", response_model=StandardResponse[User])
async def update_user(
    username: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends()
) -> Any:
    """Update a user by username."""
    try:
        user = await user_service.update_user_by_username(
            username=username,
            user_update=user_update,
            current_username=current_user.username
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return StandardResponse.of(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{username}", response_model=StandardResponse[dict], status_code=status.HTTP_200_OK)
async def delete_user(
    username: str,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends()
) -> Any:
    """Delete a user by username."""
    success = await user_service.delete_user_by_username(username)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return StandardResponse.of({"message": "User deleted successfully"})
