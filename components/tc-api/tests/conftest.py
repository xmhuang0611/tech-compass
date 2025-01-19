import asyncio
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.testclient import TestClient
from main import app
from app.core.config import settings
from app.core.security import get_password_hash
from datetime import datetime
from bson import ObjectId

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
    return user_data

@pytest.fixture(scope="session")
async def test_token(test_client, test_user):
    """Get a test token."""
    response = test_client.post(
        "/api/auth/login",
        data={
            "grant_type": "password",
            "username": test_user["username"],
            "password": "testpass123",
            "scope": "",
            "client_id": "",
            "client_secret": ""
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]
