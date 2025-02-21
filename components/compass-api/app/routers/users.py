from typing import Any, List, Optional

from cachetools import TTLCache
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response

from app.core.auth import get_current_active_user, get_current_superuser
from app.models.response import StandardResponse
from app.models.user import (
    AdminUserUpdate,
    User,
    UserCreate,
    UserPasswordUpdate,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter()

# Create a cache with 1-day TTL (86400 seconds)
avatar_cache = TTLCache(maxsize=1000, ttl=86400)


@router.post("/", response_model=StandardResponse[User], status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(get_current_superuser),
    user_service: UserService = Depends(),
) -> Any:
    """Create a new user (admin only)."""
    try:
        result = await user_service.create_user(user)
        return StandardResponse.of(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=StandardResponse[List[User]])
async def get_users(
    skip: int = 0,
    limit: int = 10,
    username: Optional[str] = Query(None, description="Filter by username (case-insensitive partial match)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_superuser: Optional[bool] = Query(None, description="Filter by superuser status"),
    user_service: UserService = Depends(),
) -> Any:
    """Get all users with pagination and filtering.

    Query Parameters:
    - skip: Number of records to skip
    - limit: Maximum number of records to return
    - username: Filter by username (case-insensitive partial match)
    - is_active: Filter by active status (true/false)
    - is_superuser: Filter by superuser status (true/false)
    """
    users = await user_service.get_users(
        skip=skip,
        limit=limit,
        username=username,
        is_active=is_active,
        is_superuser=is_superuser,
    )
    total = await user_service.count_users(username=username, is_active=is_active, is_superuser=is_superuser)
    return StandardResponse.paginated(data=users, total=total, skip=skip, limit=limit)


@router.get("/me", response_model=StandardResponse[User])
async def read_user_me(current_user: User = Depends(get_current_active_user)) -> Any:
    """Get current user."""
    return StandardResponse.of(current_user)


@router.get("/{username}", response_model=StandardResponse[User])
async def get_user(
    username: str,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(),
) -> Any:
    """Get a specific user by username."""
    user = await user_service.get_user_for_api(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return StandardResponse.of(user)


@router.put("/{username}/password", response_model=StandardResponse[dict])
async def update_user_password(
    username: str,
    password_update: UserPasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(),
) -> Any:
    """Update a user's password."""
    try:
        success = await user_service.update_user_password(
            username=username,
            password_update=password_update,
            current_username=current_user.username,
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return StandardResponse.of({"message": "Password updated successfully"})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{username}", response_model=StandardResponse[User])
async def update_user(
    username: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(),
) -> Any:
    """Update a user by username. Users can only update their own information."""
    try:
        user = await user_service.update_user_by_username(
            username=username,
            user_update=user_update,
            current_username=current_user.username,
        )
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return StandardResponse.of(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{username}", response_model=StandardResponse[dict], status_code=status.HTTP_200_OK)
async def delete_user(
    username: str,
    current_user: User = Depends(get_current_superuser),
    user_service: UserService = Depends(),
) -> Any:
    """Delete a user by username (superuser only)."""
    try:
        success = await user_service.admin_delete_user(username=username, admin_username=current_user.username)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return StandardResponse.of({"message": "User deleted successfully"})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/manage/{username}", response_model=StandardResponse[User])
async def admin_update_user(
    username: str,
    user_update: AdminUserUpdate,
    current_user: User = Depends(get_current_superuser),
    user_service: UserService = Depends(),
) -> Any:
    """Update any user's information (admin only).

    This endpoint allows superusers to:
    * Update all user fields including is_active and is_superuser
    * Change user's password
    * Update external user information
    """
    try:
        user = await user_service.admin_update_user(
            username=username,
            user_update=user_update,
            admin_username=current_user.username,
            new_password=user_update.password,
        )
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return StandardResponse.of(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/manage/{username}", response_model=StandardResponse[dict])
async def admin_delete_user(
    username: str,
    current_user: User = Depends(get_current_superuser),
    user_service: UserService = Depends(),
) -> Any:
    """Delete any user (admin only)."""
    try:
        success = await user_service.admin_delete_user(username=username, admin_username=current_user.username)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return StandardResponse.of({"message": "User deleted successfully"})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{username}/avatar", response_class=Response)
async def get_user_avatar(
    username: str,
    user_service: UserService = Depends(),
) -> Any:
    """Get an avatar for a user.
    If AVATAR_SERVER_ENABLED is true and URL is configured, fetches from the configured avatar server.
    Otherwise, returns a generated SVG avatar.
    Response is cached for 1 day."""

    content, media_type = await user_service.get_user_avatar(username)
    return Response(content=content, media_type=media_type)
