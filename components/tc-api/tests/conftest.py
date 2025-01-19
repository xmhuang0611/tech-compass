import asyncio
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.testclient import TestClient
from main import app
from app.core.config import settings
from app.core.security import get_password_hash, create_access_token
from datetime import datetime, timedelta
from bson import ObjectId
from app.models.user import User

# Set JWT settings for testing
settings.JWT_SECRET_KEY = "test_secret_key"
settings.JWT_ALGORITHM = "HS256"
settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="session")
async def test_db():
    """Create a test database and handle cleanup."""
    test_settings = settings.model_copy()
    test_settings.DATABASE_NAME = "tc_test"
    
    client = AsyncIOMotorClient(test_settings.MONGODB_URL)
    db = client[test_settings.DATABASE_NAME]
    
    # Clear test database before tests
    await db.users.delete_many({})
    await db.categories.delete_many({})
    await db.tags.delete_many({})
    await db.solutions.delete_many({})
    
    yield db
    
    # Clear test database after tests
    await db.users.delete_many({})
    await db.categories.delete_many({})
    await db.tags.delete_many({})
    await db.solutions.delete_many({})
    
    client.close()

@pytest.fixture(scope="session")
async def test_user(test_db):
    """Create a test user."""
    user_data = {
        "_id": ObjectId(),
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "hashed_password": get_password_hash("testpass123"),
        "is_active": True,
        "is_superuser": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await test_db.users.insert_one(user_data)
    user = User(**user_data)
    return user

@pytest.fixture(scope="session")
def auth_headers(test_user):
    """Create authentication headers with JWT token."""
    access_token = create_access_token(
        data={"sub": test_user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"Authorization": f"Bearer {access_token}"}
