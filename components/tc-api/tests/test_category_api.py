import pytest
from bson import ObjectId
from datetime import datetime

pytestmark = pytest.mark.asyncio

async def test_create_category(test_client, test_token, test_db):
    """Test creating a new category."""
    category_data = {
        "name": "Test Category",
        "description": "Test category description"
    }
    
    response = test_client.post(
        "/api/v1/categories/",
        json=category_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == category_data["name"]
    assert data["description"] == category_data["description"]
    assert "_id" in data
    
    # Verify in database
    db_category = await test_db.categories.find_one({"_id": ObjectId(data["_id"])})
    assert db_category is not None
    assert db_category["name"] == category_data["name"]

async def test_get_categories(test_client, test_token, test_db):
    """Test getting all categories."""
    # Create test categories
    categories = [
        {"name": "Category 1", "description": "Description 1"},
        {"name": "Category 2", "description": "Description 2"}
    ]
    
    for category in categories:
        category["created_at"] = datetime.utcnow()
        category["updated_at"] = datetime.utcnow()
        await test_db.categories.insert_one(category)
    
    response = test_client.get(
        "/api/v1/categories/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 2
    assert data["total"] >= 2

async def test_get_category(test_client, test_token, test_db):
    """Test getting a specific category."""
    # Create test category
    category = {
        "name": "Test Category",
        "description": "Test Description",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await test_db.categories.insert_one(category)
    category_id = str(result.inserted_id)
    
    response = test_client.get(
        f"/api/v1/categories/{category_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == category["name"]
    assert data["description"] == category["description"]

async def test_update_category(test_client, test_token, test_db):
    """Test updating a category."""
    # Create test category
    category = {
        "name": "Old Name",
        "description": "Old Description",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await test_db.categories.insert_one(category)
    category_id = str(result.inserted_id)
    
    update_data = {
        "name": "New Name",
        "description": "New Description"
    }
    
    response = test_client.put(
        f"/api/v1/categories/{category_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    
    # Verify in database
    db_category = await test_db.categories.find_one({"_id": ObjectId(category_id)})
    assert db_category["name"] == update_data["name"]
    assert db_category["description"] == update_data["description"]

async def test_delete_category(test_client, test_token, test_db):
    """Test deleting a category."""
    # Create test category
    category = {
        "name": "To Delete",
        "description": "Will be deleted",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await test_db.categories.insert_one(category)
    category_id = str(result.inserted_id)
    
    response = test_client.delete(
        f"/api/v1/categories/{category_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 204
    
    # Verify deletion in database
    db_category = await test_db.categories.find_one({"_id": ObjectId(category_id)})
    assert db_category is None
