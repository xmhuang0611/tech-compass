from typing import Literal, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "compass"
    MONGODB_TLS_CERT_PATH: Optional[str] = None
    MONGODB_TLS_CA_PATH: Optional[str] = None
    MONGODB_TLS_KEY_PATH: Optional[str] = None

    # JWT settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5256000

    # Auth Server settings
    AUTH_SERVER_URL: str = "http://localhost:8000"
    AUTH_SERVER_ENABLED: bool = False
    AUTH_SERVER_USERNAME_FIELD: str = "username"
    AUTH_SERVER_PASSWORD_FIELD: str = "password"
    AUTH_SERVER_CONTENT_TYPE: Literal["json", "form"] = "json"
    AUTH_SERVER_FULLNAME_FIELD: str = "full_name"
    AUTH_SERVER_EMAIL_FIELD: str = "email"

    # Avatar Server settings
    AVATAR_SERVER_URL: str = ""
    AVATAR_SERVER_ENABLED: bool = False

    # Default Admin settings
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str
    DEFAULT_ADMIN_EMAIL: str = "admin@techcompass.com"
    DEFAULT_ADMIN_FULLNAME: str = "System Admin"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    AUTH_RATE_LIMIT_PER_MINUTE: int = 1000
    WRITE_RATE_LIMIT_PER_MINUTE: int = 50

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
