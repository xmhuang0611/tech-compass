from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "tsl"
    
    # JWT settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Auth Server settings
    AUTH_SERVER_URL: str = "http://localhost:8000/auth"  # Default value for development
    AUTH_SERVER_ENABLED: bool = False  # For development, set to False to use fake auth
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    AUTH_RATE_LIMIT_PER_MINUTE: int = 1000
    WRITE_RATE_LIMIT_PER_MINUTE: int = 50
    
    class Config:
        env_file = ".env"

settings = Settings()
