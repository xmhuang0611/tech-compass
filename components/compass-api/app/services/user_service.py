from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status

from app.core.mongodb import get_database
from app.core.password import get_password_hash, verify_password
from app.models.user import User, UserCreate, UserUpdate, UserInDB, UserList
from app.core.config import settings


class UserService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.users

    async def ensure_default_admin(self) -> None:
        """Ensure default admin user exists in the database."""
        admin_username = getattr(settings, "DEFAULT_ADMIN_USERNAME", "admin")
        admin = await self.get_user_by_username(admin_username)
        
        if not admin:
            admin_user = UserCreate(
                username=admin_username,
                email=getattr(settings, "DEFAULT_ADMIN_EMAIL", "admin@techcompass.com"),
                password=getattr(settings, "DEFAULT_ADMIN_PASSWORD", "admin123"),
                full_name="Default Admin",
                is_active=True,
                is_superuser=True
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
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return User.model_validate(user)

    async def get_users(self, skip: int = 0, limit: int = 10) -> UserList:
        """Get all users with pagination."""
        cursor = self.collection.find().sort("username", 1).skip(skip).limit(limit)
        users = []
        async for user_dict in cursor:
            users.append(User(**user_dict))
        return UserList(users=users)

    async def get_user_for_api(self, username: str) -> Optional[User]:
        """Get a user by username for API response."""
        user = await self.get_user_by_username(username)
        if user:
            return User.model_validate(user)
        return None

    async def create_user(self, user: UserCreate) -> User:
        """Create a new user."""
        if await self.get_user_by_username(user.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        user_dict = user.model_dump()
        user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = user_dict["created_at"]

        result = await self.collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        return User(**user_dict)

    async def update_user_by_username(
        self,
        username: str,
        user_update: UserUpdate,
        current_username: str
    ) -> Optional[User]:
        """Update a user by username."""
        # Get existing user
        existing_user = await self.get_user_by_username(username)
        if not existing_user:
            return None

        user_dict = user_update.model_dump(exclude_unset=True)
        
        # Check username uniqueness if being updated
        if "username" in user_dict and user_dict["username"] != username:
            other_user = await self.get_user_by_username(user_dict["username"])
            if other_user:
                raise ValueError(f"Username '{user_dict['username']}' is already in use")

        # Handle password update
        if "password" in user_dict:
            user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))

        user_dict["updated_at"] = datetime.utcnow()
        user_dict["updated_by"] = current_username

        result = await self.collection.find_one_and_update(
            {"username": username},
            {"$set": user_dict},
            return_document=True
        )
        if result:
            return User(**result)
        return None

    async def delete_user_by_username(self, username: str) -> bool:
        """Delete a user by username."""
        # Check if user exists first
        user = await self.get_user_by_username(username)
        if not user:
            return False

        result = await self.collection.delete_one({"username": username})
        return result.deleted_count > 0

    async def count_users(self) -> int:
        """Get total number of users"""
        return await self.collection.count_documents({})
