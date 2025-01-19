import pytest
from bson import ObjectId
from datetime import datetime

pytestmark = pytest.mark.asyncio

async def test_create_solution(test_client, test_token, test_db):
    """Test creating a new solution."""
    # Create test category and tags first
    category = {
        "name": "Test Category",
        "description": "Test category description",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    cat_result = await test_db.categories.insert_one(category)
    
    tag = {
        "name": "Test Tag",
        "description": "Test tag description",
        "usage_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    tag_result = await test_db.tags.insert_one(tag)
    
    solution_data = {
        "name": "Test Solution",
        "description": "Test solution description",
        "category": str(cat_result.inserted_id),
        "tags": [str(tag_result.inserted_id)],
        "pros": ["Pro 1", "Pro 2"],
        "cons": ["Con 1", "Con 2"],
        "department": "Engineering",
        "team": "Backend",
        "team_email": "backend@techcompass.com"
    }
    
    response = test_client.post(
        "/api/v1/solutions/",
        json=solution_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == solution_data["name"]
    assert data["description"] == solution_data["description"]
    assert data["category"] == solution_data["category"]
    assert data["tags"] == solution_data["tags"]
    assert "_id" in data
    
    # Verify in database
    db_solution = await test_db.solutions.find_one({"_id": ObjectId(data["_id"])})
    assert db_solution is not None
    assert db_solution["name"] == solution_data["name"]

async def test_get_solutions(test_client, test_token, test_db):
    """Test getting all solutions."""
    # Create test solutions
    solutions = [
        {
            "name": "Solution 1",
            "description": "Description 1",
            "department": "Engineering",
            "team": "Backend",
            "team_email": "backend@techcompass.com"
        },
        {
            "name": "Solution 2",
            "description": "Description 2",
            "department": "Engineering",
            "team": "Frontend",
            "team_email": "frontend@techcompass.com"
        }
    ]
    
    for solution in solutions:
        solution["created_at"] = datetime.utcnow()
        solution["updated_at"] = datetime.utcnow()
        await test_db.solutions.insert_one(solution)
    
    response = test_client.get(
        "/api/v1/solutions/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 2
    assert data["total"] >= 2

async def test_get_solution(test_client, test_token, test_db):
    """Test getting a specific solution."""
    # Create test solution
    solution = {
        "name": "Test Solution",
        "description": "Test Description",
        "department": "Engineering",
        "team": "Backend",
        "team_email": "backend@techcompass.com",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await test_db.solutions.insert_one(solution)
    solution_id = str(result.inserted_id)
    
    response = test_client.get(
        f"/api/v1/solutions/{solution_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == solution["name"]
    assert data["description"] == solution["description"]

async def test_update_solution(test_client, test_token, test_db):
    """Test updating a solution."""
    # Create test solution
    solution = {
        "name": "Old Name",
        "description": "Old Description",
        "department": "Engineering",
        "team": "Backend",
        "team_email": "backend@techcompass.com",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await test_db.solutions.insert_one(solution)
    solution_id = str(result.inserted_id)
    
    update_data = {
        "name": "New Name",
        "description": "New Description",
        "department": "Product",
        "team": "Product Management",
        "team_email": "product@techcompass.com"
    }
    
    response = test_client.put(
        f"/api/v1/solutions/{solution_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    
    # Verify in database
    db_solution = await test_db.solutions.find_one({"_id": ObjectId(solution_id)})
    assert db_solution["name"] == update_data["name"]
    assert db_solution["description"] == update_data["description"]

async def test_delete_solution(test_client, test_token, test_db):
    """Test deleting a solution."""
    # Create test solution
    solution = {
        "name": "To Delete",
        "description": "Will be deleted",
        "department": "Engineering",
        "team": "Backend",
        "team_email": "backend@techcompass.com",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await test_db.solutions.insert_one(solution)
    solution_id = str(result.inserted_id)
    
    response = test_client.delete(
        f"/api/v1/solutions/{solution_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 204
    
    # Verify deletion in database
    db_solution = await test_db.solutions.find_one({"_id": ObjectId(solution_id)})
    assert db_solution is None

async def test_solution_with_tags(test_client, test_token, test_db):
    """Test solution with tags operations."""
    # Create test tags
    tags = [
        {
            "name": "Tag 1",
            "description": "Description 1",
            "usage_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Tag 2",
            "description": "Description 2",
            "usage_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    tag_ids = []
    for tag in tags:
        result = await test_db.tags.insert_one(tag)
        tag_ids.append(str(result.inserted_id))
    
    # Create solution with tags
    solution_data = {
        "name": "Tagged Solution",
        "description": "Solution with tags",
        "department": "Engineering",
        "team": "Backend",
        "team_email": "backend@techcompass.com",
        "tags": tag_ids
    }
    
    response = test_client.post(
        "/api/v1/solutions/",
        json=solution_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert set(data["tags"]) == set(tag_ids)
    
    # Verify tag usage count
    for tag_id in tag_ids:
        tag_response = test_client.get(
            f"/api/v1/tags/{tag_id}",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert tag_response.status_code == 200
        tag_data = tag_response.json()
        assert tag_data["usage_count"] == 1
