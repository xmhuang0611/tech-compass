import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.core.database import get_database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_db() -> AsyncIOMotorDatabase:
    return get_database()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        if user_id is None or username is None:
            raise credentials_exception

        return {
            "id": user_id,
            "username": username,
            "is_active": True,  # For development, assume all users are active
        }
    except InvalidTokenError:
        raise credentials_exception


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
