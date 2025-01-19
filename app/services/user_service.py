from typing import Optional
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.mongodb import get_database
from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserCreate, UserUpdate

class UserService:
    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_database)):
        self.db = db

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        if user_doc := await self.db.users.find_one({"_id": user_id}):
            return User(**user_doc)
        return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        if user_doc := await self.db.users.find_one({"email": email}):
            return User(**user_doc)
        return None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        if user_doc := await self.db.users.find_one({"username": username}):
            return User(**user_doc)
        return None

    async def create_user(self, user: UserCreate) -> User:
        """Create a new user."""
        user_doc = user.model_dump()
        user_doc["hashed_password"] = get_password_hash(user.password)
        del user_doc["password"]
        
        result = await self.db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        return User(**user_doc)

    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """Update a user."""
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        if update_data:
            result = await self.db.users.update_one(
                {"_id": user_id},
                {"$set": update_data}
            )
            if result.modified_count:
                return await self.get_user(user_id)
        return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        result = await self.db.users.delete_one({"_id": user_id})
        return bool(result.deleted_count)

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user."""
        user = await self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_users(self, skip: int = 0, limit: int = 10) -> list[User]:
        """Get all users with pagination."""
        cursor = self.db.users.find().skip(skip).limit(limit)
        users = []
        async for user_doc in cursor:
            users.append(User(**user_doc))
        return users

    async def count_users(self) -> int:
        """Get total number of users."""
        return await self.db.users.count_documents({}) 