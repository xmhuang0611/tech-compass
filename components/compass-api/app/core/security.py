from datetime import datetime, timedelta
from typing import Optional

import httpx
import jwt

from app.core.config import settings
from app.core.password import verify_password
from app.models.user import UserCreate, UserInDB


async def get_user_from_db(username: str) -> Optional[UserInDB]:
    """Get user from database without circular import."""
    from app.services.user_service import UserService

    user_service = UserService()
    return await user_service.get_user_by_username(username)


async def verify_credentials(username: str, password: str) -> bool:
    """Verify user credentials against external auth server or local database."""
    # First check if user exists in our database
    user = await get_user_from_db(username)

    # Check if user exists and is active
    if user and not user.is_active:
        return False

    # Always verify admin user with password
    if username == "admin":
        if not user:
            return False
        return verify_password(password, user.hashed_password)

    if not settings.AUTH_SERVER_ENABLED:
        # Development mode - verify password against local database
        if not user:
            return False
        return verify_password(password, user.hashed_password)

    try:
        # Create a transport that skips SSL verification
        transport = httpx.AsyncHTTPTransport(verify=False)
        async with httpx.AsyncClient(transport=transport) as client:
            data = {
                settings.AUTH_SERVER_USERNAME_FIELD: username,
                settings.AUTH_SERVER_PASSWORD_FIELD: password,
            }
            headers = {
                "Content-Type": "application/json"
                if settings.AUTH_SERVER_CONTENT_TYPE == "json"
                else "application/x-www-form-urlencoded"
            }

            if settings.AUTH_SERVER_CONTENT_TYPE == "form":
                response = await client.post(settings.AUTH_SERVER_URL, data=data, headers=headers, timeout=5.0)
            else:
                response = await client.post(settings.AUTH_SERVER_URL, json=data, headers=headers, timeout=5.0)

            if response.status_code != 200:
                return False

            # Parse response JSON
            try:
                auth_data = response.json()
                # Get full_name from configured field or fallback to username
                full_name = auth_data.get(settings.AUTH_SERVER_FULLNAME_FIELD, username)
                # Get email from configured field or use fallback
                email = auth_data.get(settings.AUTH_SERVER_EMAIL_FIELD, f"{username}@external.auth")

                # Create or update local user
                from app.services.user_service import UserService

                user_service = UserService()
                if not user:
                    # Create new user
                    user_create = UserCreate(
                        username=username,
                        password="",  # Empty password for external auth users
                        email=email,
                        full_name=full_name,
                        is_active=True,
                        is_superuser=False,
                    )
                    await user_service.create_user(user_create)
                else:
                    # If user exists but is not active, deny login
                    if not user.is_active:
                        return False

                    # Update existing user's info if changed
                    if user.full_name != full_name or user.email != email:
                        await user_service.update_external_user(username=username, full_name=full_name, email=email)

                return True
            except (ValueError, KeyError):
                # If response is not valid JSON or missing required fields
                return False

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
