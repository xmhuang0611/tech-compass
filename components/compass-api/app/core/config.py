from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "tc"
    MONGODB_TLS_CERT_PATH: Optional[str] = None
    MONGODB_TLS_CA_PATH: Optional[str] = None
    MONGODB_TLS_KEY_PATH: Optional[str] = None
    
    # JWT settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5256000
    
    # Auth Server settings
    AUTH_SERVER_URL: str = "http://localhost:8000/auth"
    AUTH_SERVER_ENABLED: bool = False
    
    # Default Admin settings
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"
    DEFAULT_ADMIN_EMAIL: str = "admin@techcompass.com"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    AUTH_RATE_LIMIT_PER_MINUTE: int = 1000
    WRITE_RATE_LIMIT_PER_MINUTE: int = 50
    
    class Config:
        env_file = ".env"

settings = Settings()
