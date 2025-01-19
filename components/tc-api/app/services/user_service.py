from datetime import datetime
from typing import List, Optional
from bson import ObjectId

from app.models.user import UserCreate, UserUpdate, UserInDB
from app.core.security import get_password_hash, verify_password
from app.core.database import get_database

class UserService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.users

    async def create_user(self, user: UserCreate, created_by: Optional[str] = None) -> UserInDB:
        """Create a new user"""
        # Check if user with same email exists
        existing_user = await self.get_user_by_email(user.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Check if username is taken
        existing_user = await self.get_user_by_username(user.username)
        if existing_user:
            raise ValueError("Username is already taken")

        user_dict = user.dict(exclude={"password"})
        user_dict["hashed_password"] = get_password_hash(user.password)
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        if created_by:
            user_dict["created_by"] = ObjectId(created_by)
            user_dict["updated_by"] = ObjectId(created_by)

        result = await self.collection.insert_one(user_dict)
        return await self.get_user_by_id(str(result.inserted_id))

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get a user by ID"""
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return UserInDB(**user)
        return None

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get a user by email"""
        user = await self.collection.find_one({"email": email})
        if user:
            return UserInDB(**user)
        return None

    async def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """Get a user by username"""
        user = await self.collection.find_one({"username": username})
        if user:
            return UserInDB(**user)
        return None

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        """Get all users with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit)
        users = await cursor.to_list(length=limit)
        return [UserInDB(**user) for user in users]

    async def update_user(
        self,
        user_id: str,
        user_update: UserUpdate,
        updated_by: Optional[str] = None
    ) -> Optional[UserInDB]:
        """Update a user"""
        update_dict = user_update.dict(exclude_unset=True)
        
        # Handle password update
        if "password" in update_dict:
            update_dict["hashed_password"] = get_password_hash(update_dict.pop("password"))

        # Check email uniqueness if being updated
        if "email" in update_dict:
            existing_user = await self.get_user_by_email(update_dict["email"])
            if existing_user and str(existing_user.id) != user_id:
                raise ValueError("Email is already in use")

        # Check username uniqueness if being updated
        if "username" in update_dict:
            existing_user = await self.get_user_by_username(update_dict["username"])
            if existing_user and str(existing_user.id) != user_id:
                raise ValueError("Username is already taken")

        update_dict["updated_at"] = datetime.utcnow()
        if updated_by:
            update_dict["updated_by"] = ObjectId(updated_by)

        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_dict}
        )
        if result.modified_count:
            return await self.get_user_by_id(user_id)
        return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    async def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """Authenticate a user by username and password"""
        user = await self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
