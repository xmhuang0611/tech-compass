import pytest
from bson import ObjectId
from datetime import datetime

pytestmark = pytest.mark.asyncio

async def test_create_tag(test_client, test_token, test_db):
    """Test creating a new tag."""
    tag_data = {
        "name": "Test Tag",
        "description": "Test tag description"
    }
    
    response = test_client.post(
        "/api/tags/",
        json=tag_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == tag_data["name"]
    assert data["description"] == tag_data["description"]
    assert "_id" in data
    
    # Verify in database
    db_tag = await test_db.tags.find_one({"_id": ObjectId(data["_id"])})
    assert db_tag is not None
    assert db_tag["name"] == tag_data["name"]

async def test_get_tags(test_client, test_token, test_db):
    """Test getting all tags."""
    # Create test tags
    tags = [
        {"name": "Tag 1", "description": "Description 1", "usage_count": 0},
        {"name": "Tag 2", "description": "Description 2", "usage_count": 0}
    ]
    
    for tag in tags:
        tag["created_at"] = datetime.utcnow()
        tag["updated_at"] = datetime.utcnow()
        await test_db.tags.insert_one(tag)
    
    response = test_client.get(
        "/api/tags/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 2
    assert data["total"] >= 2

async def test_get_tag(test_client, test_token, test_db):
    """Test getting a specific tag."""
    # Create test tag
    tag = {
        "name": "Test Tag",
        "description": "Test Description",
        "usage_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await test_db.tags.insert_one(tag)
    tag_id = str(result.inserted_id)
    
    response = test_client.get(
        f"/api/tags/{tag_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == tag["name"]
    assert data["description"] == tag["description"]

async def test_update_tag(test_client, test_token, test_db):
    """Test updating a tag."""
    # Create test tag
    tag = {
        "name": "Old Name",
        "description": "Old Description",
        "usage_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await test_db.tags.insert_one(tag)
    tag_id = str(result.inserted_id)
    
    update_data = {
        "name": "New Name",
        "description": "New Description"
    }
    
    response = test_client.put(
        f"/api/tags/{tag_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    
    # Verify in database
    db_tag = await test_db.tags.find_one({"_id": ObjectId(tag_id)})
    assert db_tag["name"] == update_data["name"]
    assert db_tag["description"] == update_data["description"]

async def test_delete_tag(test_client, test_token, test_db):
    """Test deleting a tag."""
    # Create test tag
    tag = {
        "name": "To Delete",
        "description": "Will be deleted",
        "usage_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await test_db.tags.insert_one(tag)
    tag_id = str(result.inserted_id)
    
    response = test_client.delete(
        f"/api/tags/{tag_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 204
    
    # Verify deletion in database
    db_tag = await test_db.tags.find_one({"_id": ObjectId(tag_id)})
    assert db_tag is None

async def test_tag_usage_count(test_client, test_token, test_db):
    """Test tag usage count is updated when used in solutions."""
    # Create test tag
    tag = {
        "name": "Usage Test",
        "description": "Testing usage count",
        "usage_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await test_db.tags.insert_one(tag)
    tag_id = str(result.inserted_id)
    
    # Create solution with tag
    solution = {
        "name": "Test Solution",
        "description": "Test Description",
        "tags": [tag_id],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await test_db.solutions.insert_one(solution)
    
    # Get tag and verify usage count
    response = test_client.get(
        f"/api/tags/{tag_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["usage_count"] == 1
