from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.security import create_access_token, verify_credentials, get_user_from_db
from app.models.token import Token

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests.
    Uses external auth server if enabled, otherwise allows any credentials for development.
    """
    # First check if user exists and is inactive
    user = await get_user_from_db(form_data.username)
    if user and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive. Please contact an administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    is_valid = await verify_credentials(form_data.username, form_data.password)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}
