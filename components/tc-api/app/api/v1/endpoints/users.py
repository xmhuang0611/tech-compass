from typing import List
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_db, get_current_active_user
from app.core.security import get_password_hash
from app.db.models import User
from bson import ObjectId

router = APIRouter()

@router.get("/me", response_model=User)
async def read_user_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user.
    """
    return current_user

@router.post("/", response_model=User)
async def create_user(
    user: User,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create new user. Only superusers can create new users.
    """
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=403,
            detail="Only superusers can create new users"
        )
    
    # Check if user with same email exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    user_data = user.dict()
    user_data["hashed_password"] = get_password_hash(user_data["hashed_password"])
    user_data["created_by"] = str(current_user["_id"])
    user_data["updated_by"] = str(current_user["_id"])
    
    result = await db.users.insert_one(user_data)
    created_user = await db.users.find_one({"_id": result.inserted_id})
    return created_user

@router.put("/me", response_model=User)
async def update_user_me(
    user_update: User,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update current user.
    """
    user_data = user_update.dict(exclude_unset=True)
    if "hashed_password" in user_data:
        user_data["hashed_password"] = get_password_hash(user_data["hashed_password"])
    
    user_data["updated_by"] = str(current_user["_id"])
    
    result = await db.users.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": user_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
        
    updated_user = await db.users.find_one({"_id": ObjectId(current_user["_id"])})
    return updated_user
