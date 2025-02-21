from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from cachetools import TTLCache, keys
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.mongodb import get_database
from app.core.password import get_password_hash, verify_password
from app.models.user import User, UserCreate, UserInDB, UserPasswordUpdate, UserUpdate


class UserService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.users
        # Create a cache with 1-day TTL (86400 seconds)
        self.avatar_cache = TTLCache(maxsize=1000, ttl=86400)

    async def _get_user_or_404(self, username: str) -> UserInDB:
        """Get a user by username or raise 404 if not found."""
        user = await self.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def _is_external_user(self, user: UserInDB) -> bool:
        """Check if a user is an external user (empty hashed_password)."""
        return not user.hashed_password

    def _prepare_update_data(self, update_dict: Dict[str, Any], username: str) -> Dict[str, Any]:
        """Prepare update data with audit fields."""
        update_data = update_dict.copy()
        update_data["updated_at"] = datetime.utcnow()
        update_data["updated_by"] = username
        return update_data

    async def _check_username_uniqueness(self, new_username: str, current_username: str) -> None:
        """Check if a username is unique, excluding the current user."""
        if new_username != current_username:
            existing_user = await self.get_user_by_username(new_username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Username '{new_username}' is already in use",
                )

    async def _validate_external_user_update(
        self,
        user: UserInDB,
        update_dict: Dict[str, Any],
        new_password: Optional[str] = None,
    ) -> None:
        """Validate update data for external users."""
        if self._is_external_user(user):
            allowed_fields = {"is_active", "is_superuser"}
            provided_fields = set(update_dict.keys())
            invalid_fields = provided_fields - allowed_fields
            if invalid_fields or new_password is not None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"External users can only update is_active and is_superuser fields. Invalid fields provided: {', '.join(invalid_fields)}",
                )

    async def ensure_default_admin(self) -> None:
        """Ensure default admin user exists in the database."""
        if not all(
            [
                settings.DEFAULT_ADMIN_USERNAME,
                settings.DEFAULT_ADMIN_PASSWORD,
                settings.DEFAULT_ADMIN_EMAIL,
                settings.DEFAULT_ADMIN_FULLNAME,
            ]
        ):
            raise ValueError("Missing required default admin settings")

        admin = await self.get_user_by_username(settings.DEFAULT_ADMIN_USERNAME)
        if not admin:
            admin_user = UserCreate(
                username=settings.DEFAULT_ADMIN_USERNAME,
                email=settings.DEFAULT_ADMIN_EMAIL,
                password=settings.DEFAULT_ADMIN_PASSWORD,
                full_name=settings.DEFAULT_ADMIN_FULLNAME,
                is_active=True,
                is_superuser=True,
            )
            await self.create_user(admin_user)

    async def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """Get a user by username - internal use only."""
        user_dict = await self.collection.find_one({"username": username})
        if user_dict:
            return UserInDB(**user_dict)
        return None

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user."""
        user = await self.get_user_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return User.model_validate(user)

    async def get_users(
        self,
        skip: int = 0,
        limit: int = 10,
        username: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
    ) -> list[User]:
        """Get all users with pagination and filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            username: Optional filter by username (case-insensitive partial match)
            is_active: Optional filter by active status
            is_superuser: Optional filter by superuser status

        Returns:
            List of matching users
        """
        # Build query
        query = {}
        if username:
            query["username"] = {"$regex": username, "$options": "i"}
        if is_active is not None:
            query["is_active"] = is_active
        if is_superuser is not None:
            query["is_superuser"] = is_superuser

        cursor = self.collection.find(query).sort("username", 1).skip(skip).limit(limit)
        users = []
        async for user_dict in cursor:
            users.append(User(**user_dict))
        return users

    async def get_user_for_api(self, username: str) -> Optional[User]:
        """Get a user by username for API response."""
        user = await self.get_user_by_username(username)
        if user:
            return User.model_validate(user)
        return None

    async def create_user(self, user: UserCreate) -> User:
        """Create a new user."""
        user.username = user.username.lower()
        await self._check_username_uniqueness(user.username, "")

        user_dict = user.model_dump(exclude={"password"})
        user_dict.update(
            {
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "hashed_password": get_password_hash(user.password) if user.password else "",
            }
        )

        result = await self.collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        return User(**user_dict)

    async def update_user_password(
        self, username: str, password_update: UserPasswordUpdate, current_username: str
    ) -> bool:
        """Update a user's password."""
        username = username.lower()
        if username != current_username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own password",
            )

        user = await self._get_user_or_404(username)

        if self._is_external_user(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="External users cannot change their password",
            )

        if not verify_password(password_update.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        update_data = self._prepare_update_data(
            {"hashed_password": get_password_hash(password_update.new_password)},
            current_username,
        )

        result = await self.collection.update_one({"username": username}, {"$set": update_data})
        return result.modified_count > 0

    async def update_user_by_username(
        self, username: str, user_update: UserUpdate, current_username: str
    ) -> Optional[User]:
        """Update a user by username."""
        if username != current_username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own information",
            )

        user = await self._get_user_or_404(username)

        if self._is_external_user(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="External users cannot update their information",
            )

        update_dict = user_update.model_dump(exclude_unset=True)
        if "username" in update_dict:
            update_dict["username"] = update_dict["username"].lower()
            await self._check_username_uniqueness(update_dict["username"], username)

        update_data = self._prepare_update_data(update_dict, current_username)

        result = await self.collection.find_one_and_update(
            {"username": username}, {"$set": update_data}, return_document=True
        )
        return User(**result) if result else None

    async def update_external_user(self, username: str, full_name: str, email: str) -> Optional[User]:
        """System level update for external user information during authentication."""
        update_data = self._prepare_update_data({"full_name": full_name, "email": email}, "system")

        result = await self.collection.find_one_and_update(
            {"username": username}, {"$set": update_data}, return_document=True
        )
        return User(**result) if result else None

    async def admin_update_user(
        self,
        username: str,
        user_update: UserUpdate,
        admin_username: str,
        new_password: Optional[str] = None,
    ) -> Optional[User]:
        """Admin level update for user information.
        For external users, ONLY is_active and is_superuser fields can be updated."""
        user = await self._get_user_or_404(username)
        update_dict = user_update.model_dump(exclude_unset=True)

        # Validate external user updates
        await self._validate_external_user_update(user, update_dict, new_password)

        # Prepare update data based on user type
        if self._is_external_user(user):
            allowed_fields = {"is_active", "is_superuser"}
            update_dict = {k: v for k, v in update_dict.items() if k in allowed_fields}
        else:
            if new_password is not None:
                update_dict["hashed_password"] = get_password_hash(new_password)
            if "username" in update_dict:
                update_dict["username"] = update_dict["username"].lower()
                await self._check_username_uniqueness(update_dict["username"], username)

        update_data = self._prepare_update_data(update_dict, admin_username)

        result = await self.collection.find_one_and_update(
            {"username": username}, {"$set": update_data}, return_document=True
        )
        return User(**result) if result else None

    async def admin_delete_user(self, username: str, admin_username: str) -> bool:
        """Admin level delete for users.
        Cannot delete admin's own account or external users."""
        if username == admin_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Administrators cannot delete their own account",
            )

        user = await self._get_user_or_404(username)

        if self._is_external_user(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="External users cannot be deleted, they are managed by the external auth system",
            )

        result = await self.collection.delete_one({"username": username})
        return result.deleted_count > 0

    async def count_users(
        self,
        username: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
    ) -> int:
        """Get total number of users matching the filter criteria.

        Args:
            username: Optional filter by username (case-insensitive partial match)
            is_active: Optional filter by active status
            is_superuser: Optional filter by superuser status

        Returns:
            Total number of matching users
        """
        query = {}
        if username:
            query["username"] = {"$regex": username, "$options": "i"}
        if is_active is not None:
            query["is_active"] = is_active
        if is_superuser is not None:
            query["is_superuser"] = is_superuser

        return await self.collection.count_documents(query)

    async def get_user_info(self, username: str) -> Optional[dict]:
        """Get basic user info (username and full_name) for display purposes."""
        user = await self.collection.find_one({"username": username}, {"full_name": 1})
        if user:
            return {"username": username, "full_name": user["full_name"]}
        return None

    async def get_users_by_usernames(self, usernames: List[str]) -> List[User]:
        """Get multiple users by their usernames.

        Args:
            usernames: List of usernames to fetch

        Returns:
            List of User objects for the given usernames
        """
        if not usernames:
            return []

        cursor = self.collection.find({"username": {"$in": usernames}})
        users = []
        async for user_dict in cursor:
            users.append(User(**user_dict))
        return users

    async def get_user_avatar(self, username: str) -> tuple[bytes | str, str]:
        """Get an avatar for a user.
        If AVATAR_SERVER_ENABLED is true and URL is configured, fetches from the configured avatar server.
        Otherwise, returns a generated SVG avatar.
        Response is cached for 1 day.

        Args:
            username: The username to get avatar for

        Returns:
            Tuple of (content, media_type) where:
                content: The avatar content (bytes for images, str for SVG)
                media_type: The content type of the avatar
        """
        # Generate cache key based on username and avatar server settings
        cache_key = keys.hashkey(username, settings.AVATAR_SERVER_ENABLED, settings.AVATAR_SERVER_URL)

        # Try to get from cache
        if cache_key in self.avatar_cache:
            return (self.avatar_cache[cache_key]["content"], self.avatar_cache[cache_key]["media_type"])

        # Generate or fetch avatar
        if settings.AVATAR_SERVER_ENABLED and settings.AVATAR_SERVER_URL:
            content, media_type = await self._fetch_external_avatar(username)
        else:
            content, media_type = self._generate_svg_avatar(username)

        # Cache the response
        self.avatar_cache[cache_key] = {"content": content, "media_type": media_type}

        return content, media_type

    async def _fetch_external_avatar(self, username: str) -> tuple[bytes, str]:
        """Fetch avatar from external avatar server.
        If the fetch fails for any reason (network error, non-200 status, etc.),
        falls back to generated SVG avatar.

        Args:
            username: The username to fetch avatar for

        Returns:
            Tuple of (content, media_type)
        """
        try:
            avatar_url = settings.AVATAR_SERVER_URL.format(username=username)
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(avatar_url)
                if response.status_code == 200:
                    return response.content, response.headers.get("content-type", "image/png")
        except Exception:
            # Log error if needed
            pass

        # If we get here, either the request failed or returned non-200 status
        # Fallback to generated avatar
        return self._generate_svg_avatar(username)

    def _generate_svg_avatar(self, username: str) -> tuple[str, str]:
        """Generate an SVG avatar for a user.

        Args:
            username: The username to generate avatar for

        Returns:
            Tuple of (svg_content, media_type)
        """
        # Get the first two letters of the username (uppercase)
        first_letters = username[:2].upper() if len(username) >= 2 else (username[0].upper() if username else "?")

        # Generate a consistent color based on the username
        color = f"#{hash(username) % 0xFFFFFF:06x}"

        # Create SVG template
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
    <svg width="100" height="100" version="1.1" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="50" fill="{color}"/>
        <text x="50" y="50" font-family="Arial" font-size="35" fill="white" text-anchor="middle" dominant-baseline="central">
            {first_letters}
        </text>
    </svg>'''

        return svg, "image/svg+xml"
