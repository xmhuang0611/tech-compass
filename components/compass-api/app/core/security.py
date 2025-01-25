from datetime import datetime, timedelta
from typing import Optional

import httpx
from jose import jwt

from app.core.config import settings
from app.core.password import verify_password
from app.models.user import UserInDB

async def get_user_from_db(username: str) -> Optional[UserInDB]:
    """Get user from database without circular import."""
    from app.services.user_service import UserService
    user_service = UserService()
    return await user_service.get_user_by_username(username)

async def verify_credentials(username: str, password: str) -> bool:
    """Verify user credentials against external auth server or local database."""
    # First check if user exists in our database
    user = await get_user_from_db(username)
    if not user:
        return False
    
    if not settings.AUTH_SERVER_ENABLED:
        # Development mode - verify password against local database
        return verify_password(password, user.hashed_password)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AUTH_SERVER_URL}/verify",
                json={"username": username, "password": password},
                timeout=5.0
            )
            return response.status_code == 200
    except httpx.RequestError:
        # If auth server is unreachable, fail closed for security
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt
