from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status

from app.core.mongodb import get_database
from app.core.password import get_password_hash, verify_password
from app.models.user import User, UserCreate, UserUpdate, UserInDB, UserPasswordUpdate
from app.core.config import settings


class UserService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.users

    async def ensure_default_admin(self) -> None:
        """Ensure default admin user exists in the database."""
        if not settings.DEFAULT_ADMIN_USERNAME:
            raise ValueError("DEFAULT_ADMIN_USERNAME is not set")
        if not settings.DEFAULT_ADMIN_PASSWORD:
            raise ValueError("DEFAULT_ADMIN_PASSWORD is not set")
        if not settings.DEFAULT_ADMIN_EMAIL:
            raise ValueError("DEFAULT_ADMIN_EMAIL is not set")
        if not settings.DEFAULT_ADMIN_FULLNAME:
            raise ValueError("DEFAULT_ADMIN_FULLNAME is not set")

        admin_username = settings.DEFAULT_ADMIN_USERNAME
        admin = await self.get_user_by_username(admin_username)
        
        if not admin:
            admin_user = UserCreate(
                username=admin_username,
                email=settings.DEFAULT_ADMIN_EMAIL,
                password=settings.DEFAULT_ADMIN_PASSWORD,
                full_name=settings.DEFAULT_ADMIN_FULLNAME,
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

    async def get_users(self, skip: int = 0, limit: int = 10) -> list[User]:
        """Get all users with pagination."""
        cursor = self.collection.find().sort("username", 1).skip(skip).limit(limit)
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
        if await self.get_user_by_username(user.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Create user dict without password field
        user_dict = {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Handle password hashing
        if user.password:
            user_dict["hashed_password"] = get_password_hash(user.password)
        else:
            user_dict["hashed_password"] = ""  # Empty hash for external auth users

        result = await self.collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        return User(**user_dict)

    async def update_user_password(
        self,
        username: str,
        password_update: UserPasswordUpdate,
        current_username: str
    ) -> bool:
        """Update a user's password."""
        # Only allow users to update their own password
        if username != current_username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own password"
            )

        # Get existing user
        existing_user = await self.get_user_by_username(username)
        if not existing_user:
            return False

        # Check if user is an external user (empty hashed_password)
        if not existing_user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="External users cannot change their password"
            )

        # Verify current password
        if not verify_password(password_update.current_password, existing_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Update password
        new_hashed_password = get_password_hash(password_update.new_password)
        result = await self.collection.update_one(
            {"username": username},
            {
                "$set": {
                    "hashed_password": new_hashed_password,
                    "updated_at": datetime.utcnow(),
                    "updated_by": current_username
                }
            }
        )
        return result.modified_count > 0

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

        # Only allow users to update their own information
        if username != current_username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own information"
            )

        # Check if user is an external user (empty hashed_password)
        if not existing_user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="External users cannot update their information"
            )

        # Only include non-None fields in the update
        update_data = {}
        user_dict = user_update.model_dump(exclude_unset=True)
        
        # Check username uniqueness if being updated
        if "username" in user_dict and user_dict["username"] != username:
            other_user = await self.get_user_by_username(user_dict["username"])
            if other_user:
                raise ValueError(f"Username '{user_dict['username']}' is already in use")

        # Add all non-None fields to update_data
        for field, value in user_dict.items():
            if value is not None:
                update_data[field] = value

        if not update_data:
            # If no fields to update, return existing user
            return User.model_validate(existing_user)

        update_data["updated_at"] = datetime.utcnow()
        update_data["updated_by"] = current_username

        result = await self.collection.find_one_and_update(
            {"username": username},
            {"$set": update_data},
            return_document=True
        )
        if result:
            return User(**result)
        return None

    async def update_external_user(
        self,
        username: str,
        full_name: str,
        email: str
    ) -> Optional[User]:
        """System level update for external user information.
        This method is used to update external user information during authentication."""
        user_dict = {
            "full_name": full_name,
            "email": email,
            "updated_at": datetime.utcnow(),
            "updated_by": "system"
        }

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

    async def admin_update_user(
        self,
        username: str,
        user_update: UserUpdate,
        admin_username: str,
        new_password: Optional[str] = None
    ) -> Optional[User]:
        """Admin level update for user information.
        This method allows superusers to update all user fields including password.
        For external users, only is_active and is_superuser fields can be updated."""
        # Get existing user
        existing_user = await self.get_user_by_username(username)
        if not existing_user:
            return None

        # Only include non-None fields in the update
        update_data = {}
        user_dict = user_update.model_dump(exclude_unset=True)
        
        # Check username uniqueness if being updated
        if "username" in user_dict and user_dict["username"] != username:
            other_user = await self.get_user_by_username(user_dict["username"])
            if other_user:
                raise ValueError(f"Username '{user_dict['username']}' is already in use")

        # Check if user is an external user (empty hashed_password)
        is_external = not existing_user.hashed_password

        if is_external:
            # For external users, only allow updating is_active and is_superuser
            allowed_fields = {"is_active", "is_superuser"}
            for field in user_dict:
                if field in allowed_fields:
                    update_data[field] = user_dict[field]
            if new_password is not None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot set password for external users"
                )
        else:
            # For local users, allow updating all fields
            update_data = user_dict
            # Handle password update if provided
            if new_password is not None:
                update_data["hashed_password"] = get_password_hash(new_password)

        if not update_data:
            # If no fields to update, return existing user
            return User.model_validate(existing_user)

        update_data["updated_at"] = datetime.utcnow()
        update_data["updated_by"] = admin_username

        result = await self.collection.find_one_and_update(
            {"username": username},
            {"$set": update_data},
            return_document=True
        )
        if result:
            return User(**result)
        return None

    async def admin_delete_user(
        self,
        username: str,
        admin_username: str
    ) -> bool:
        """Admin level delete for users.
        This method allows superusers to delete any user except themselves and external users."""
        # Prevent admin from deleting themselves
        if username == admin_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Administrators cannot delete their own account"
            )

        # Check if user exists
        user = await self.get_user_by_username(username)
        if not user:
            return False

        # Check if user is an external user (empty hashed_password)
        if not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="External users cannot be deleted, they are managed by the external auth system"
            )

        result = await self.collection.delete_one({"username": username})
        return result.deleted_count > 0
