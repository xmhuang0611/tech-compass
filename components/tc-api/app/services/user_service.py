from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException, status
from app.core.security import get_password_hash, verify_password
from app.db.mongodb import get_database
from app.models.user import User, UserCreate, UserUpdate

class UserService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.users

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        user_dict = await self.collection.find_one({"username": username})
        if user_dict:
            return User(**user_dict)
        return None

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user."""
        user = await self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        """Get all users with pagination."""
        cursor = self.collection.find().skip(skip).limit(limit)
        users = []
        async for user_dict in cursor:
            users.append(User(**user_dict))
        return users

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        user_dict = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user_dict:
            return User(**user_dict)
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

    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """Update a user."""
        user_dict = user_update.model_dump(exclude_unset=True)
        if "password" in user_dict:
            user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
        user_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": user_dict},
            return_document=True
        )
        if result:
            return User(**result)
        return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
