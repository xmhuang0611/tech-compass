import pytest
from unittest.mock import AsyncMock
from bson import ObjectId
from fastapi import HTTPException
from app.models.category import Category, CategoryCreate, CategoryUpdate
from app.services.category_service import CategoryService
from app.models.user import User
from app.core.auth import get_current_active_user
from app.core.security import get_password_hash
from main import app

pytestmark = pytest.mark.asyncio

# Test data
test_user_id = ObjectId()
test_category_id = ObjectId()
test_category_data = {
    "_id": test_category_id,
    "name": "Test Category",
    "description": "Test Description",
    "parent_id": None,
    "created_by": test_user_id,
    "updated_by": test_user_id,
    "created_at": "2024-01-19T00:00:00",
    "updated_at": "2024-01-19T00:00:00"
}

test_category = Category(**test_category_data)

@pytest.fixture
def category_service_mock():
    """Mock the CategoryService."""
    mock = AsyncMock(spec=CategoryService)
    mock.get_categories.return_value = [test_category]
    mock.get_category_by_id.return_value = test_category
    mock.create_category.return_value = test_category
    mock.update_category.return_value = test_category
    mock.delete_category.return_value = True
    mock.count_categories.return_value = 1
    return mock

@pytest.fixture
def mock_current_user():
    """Mock the current user."""
    return User(
        _id=test_user_id,
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
        hashed_password=get_password_hash("testpass123"),
        created_at="2024-01-19T00:00:00",
        updated_at="2024-01-19T00:00:00"
    )

@pytest.fixture
def override_dependencies(category_service_mock, mock_current_user):
    """Override dependencies for testing."""
    app.dependency_overrides[CategoryService] = lambda: category_service_mock
    app.dependency_overrides[get_current_active_user] = lambda: mock_current_user
    yield {"category_service": category_service_mock}
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_get_categories(test_client, override_dependencies, auth_headers):
    response = test_client.get("/api/categories/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == test_category.name

@pytest.mark.asyncio
async def test_get_category(test_client, override_dependencies, auth_headers):
    response = test_client.get(f"/api/categories/{str(test_category_id)}", headers=auth_headers)
    assert response.status_code == 200
    category = response.json()
    assert category["name"] == test_category.name

@pytest.mark.asyncio
async def test_create_category(test_client, override_dependencies, auth_headers):
    new_category = {
        "name": "New Category",
        "description": "New Description"
    }
    response = test_client.post("/api/categories/", json=new_category, headers=auth_headers)
    assert response.status_code == 201
    category = response.json()
    assert category["name"] == test_category.name

@pytest.mark.asyncio
async def test_update_category(test_client, override_dependencies, auth_headers):
    update_data = {
        "name": "Updated Category",
        "description": "Updated Description"
    }
    response = test_client.put(f"/api/categories/{str(test_category_id)}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    category = response.json()
    assert category["name"] == test_category.name

@pytest.mark.asyncio
async def test_delete_category(test_client, override_dependencies, auth_headers):
    response = test_client.delete(f"/api/categories/{str(test_category_id)}", headers=auth_headers)
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_get_category_not_found(test_client, override_dependencies, auth_headers):
    category_service_mock = override_dependencies["category_service"]
    category_service_mock.get_category_by_id.side_effect = HTTPException(status_code=404, detail="Category not found")
    response = test_client.get(f"/api/categories/{str(ObjectId())}", headers=auth_headers)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_category_invalid_data(test_client, override_dependencies, auth_headers):
    response = test_client.post("/api/categories/", json={"name": ""}, headers=auth_headers)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_update_category_not_found(test_client, override_dependencies, auth_headers):
    category_service_mock = override_dependencies["category_service"]
    category_service_mock.update_category.side_effect = HTTPException(status_code=404, detail="Category not found")
    update_data = {
        "name": "Updated Category",
        "description": "Updated Description"
    }
    response = test_client.put(f"/api/categories/{str(ObjectId())}", json=update_data, headers=auth_headers)
    assert response.status_code == 404
