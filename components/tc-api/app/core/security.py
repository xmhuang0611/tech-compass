from datetime import datetime, timedelta
from typing import Optional, Dict
import httpx
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def verify_user_credentials(username: str, password: str) -> Dict:
    """
    Verify user credentials against auth server or use fake validation for development.
    Returns user info if validation successful, None otherwise.
    """
    if not settings.AUTH_SERVER_ENABLED:
        # Fake validation for development - accept any credentials
        return {
            "id": "fake_user_id",
            "username": username,
            "email": f"{username}@example.com",
            "is_active": True,
            "is_superuser": False
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AUTH_SERVER_URL}/validate",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"Auth server error: {str(e)}")
        return None
    
    return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt
