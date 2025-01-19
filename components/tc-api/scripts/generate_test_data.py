"""
generate test data by using solution api post methods
1. clear existing data from db: user, solution, category, tag (use same .env config)
2. create admin user by post /api/users (auth server enable = false, allow any user to login)
3. post fake solutions one by one (category should be auto created, slug should be auto generated in backend)
"""
import asyncio
import httpx
import os
import sys
from datetime import datetime
from typing import List, Dict
from bson import ObjectId

# Add the parent directory to Python path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_database

# Constants
API_BASE_URL = "http://localhost:8000"
MAX_RETRIES = 5
RETRY_DELAY = 2  # seconds

async def verify_server_running() -> bool:
    """Verify that the local development server is running"""
    print("\nVerifying local server is running...")
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=5.0) as client:
        for attempt in range(MAX_RETRIES):
            try:
                # Try to hit the health check endpoint or any public endpoint
                response = await client.get("/api/health")
                if response.status_code == 200:
                    print("Local server is up and running!")
                    return True
                print(f"Server returned status code {response.status_code}, retrying...")
            except httpx.RequestError as e:
                if attempt < MAX_RETRIES - 1:
                    print(f"Server not ready (attempt {attempt + 1}/{MAX_RETRIES}), retrying in {RETRY_DELAY} seconds...")
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    print(f"Failed to connect to local server at {API_BASE_URL}")
                    print("Please ensure the development server is running (uvicorn main:app --reload)")
                    return False
    return False

# Test data
ADMIN_USER = {
    "username": "admin@techcompass.com",
    "email": "admin@techcompass.com",
    "full_name": "Admin User",
    "password": "admin123",  # Plain password for API
    "is_active": True,
    "is_superuser": True
}

CATEGORIES = [
    {
        "name": "Development",
        "description": "Software development solutions"
    },
    {
        "name": "Infrastructure",
        "description": "Infrastructure and DevOps solutions"
    },
    {
        "name": "Security",
        "description": "Security and compliance solutions"
    },
    {
        "name": "Data",
        "description": "Data and analytics solutions"
    }
]

SOLUTIONS = [
    {
        "name": "Microservices Architecture",
        "description": "Best practices for microservices implementation",
        "_category": "Development",  # Temporary field to map to category_id
        "status": "Active",
        "department": "Engineering",
        "team": "Backend",
        "team_email": "backend@techcompass.com",
        "pros": ["Scalability", "Independent deployments", "Technology flexibility"],
        "cons": ["Distributed complexity", "Service coordination", "Data consistency challenges"]
    },
    {
        "name": "Kubernetes Deployment",
        "description": "Standard Kubernetes deployment patterns",
        "_category": "Infrastructure",  # Temporary field to map to category_id
        "status": "Active",
        "department": "DevOps",
        "team": "Infrastructure",
        "team_email": "infrastructure@techcompass.com",
        "pros": ["Container orchestration", "Auto-scaling", "Self-healing"],
        "cons": ["Learning curve", "Resource overhead", "Complex networking"]
    },
    {
        "name": "Zero Trust Security",
        "description": "Implementing zero trust security model",
        "_category": "Security",  # Temporary field to map to category_id
        "status": "Draft",
        "department": "Security",
        "team": "Security Engineering",
        "team_email": "security.engineering@techcompass.com",
        "pros": ["Enhanced security", "Reduced attack surface", "Identity-based access"],
        "cons": ["Implementation complexity", "Performance impact", "User friction"]
    },
    {
        "name": "Data Lake Architecture",
        "description": "Building scalable data lakes",
        "_category": "Data",  # Temporary field to map to category_id
        "status": "Active",
        "department": "Data",
        "team": "Data Engineering",
        "team_email": "data.engineering@techcompass.com",
        "pros": ["Data consolidation", "Schema flexibility", "Cost-effective storage"],
        "cons": ["Data governance challenges", "Query performance", "Data quality management"]
    }
]

async def clear_existing_data():
    """Clear existing data directly using database connection"""
    print("Clearing existing data...")
    db = get_database()
    await db.solutions.delete_many({})
    await db.categories.delete_many({})
    await db.users.delete_many({})
    print("Existing data cleared.")

async def create_admin_user(client: httpx.AsyncClient) -> dict:
    """Create admin user using API"""
    print("\nCreating admin user...")
    try:
        response = await client.post("/api/users/", json=ADMIN_USER)
        response.raise_for_status()
        user = response.json()
        print(f"Admin user created: {user['email']}")
        return user
    except httpx.HTTPError as e:
        print(f"Failed to create admin user: {str(e)}")
        print(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
        raise

async def get_access_token(client: httpx.AsyncClient) -> str:
    """Get access token for authentication"""
    login_data = {
        "username": ADMIN_USER["email"],
        "password": ADMIN_USER["password"]
    }
    try:
        response = await client.post(
            "/api/auth/login", 
            data=login_data,  # Use form data instead of JSON
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        token_data = response.json()
        return token_data["access_token"]
    except httpx.HTTPError as e:
        print(f"Failed to get access token: {str(e)}")
        raise

async def create_test_data():
    """Create test data using API endpoints"""
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
        # Create admin user first
        admin_user = await create_admin_user(client)
        
        # Get access token
        access_token = await get_access_token(client)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Create categories
        print("\nCreating categories...")
        categories_map = {}  # Store category IDs by name
        for category_data in CATEGORIES:
            try:
                response = await client.post("/api/categories/", json=category_data, headers=headers)
                response.raise_for_status()
                category = response.json()
                categories_map[category["name"]] = category["_id"]
                print(f"Created category: {category['name']}")
            except httpx.HTTPError as e:
                print(f"Failed to create category: {category_data['name']}")
                print(f"Error: {str(e)}")
                continue

        # Create solutions
        print("\nCreating solutions...")
        for solution_data in SOLUTIONS:
            try:
                # Prepare solution data
                solution_payload = solution_data.copy()
                category_name = solution_payload.pop("_category")  # Remove temporary field
                if category_name in categories_map:
                    solution_payload["category_id"] = categories_map[category_name]
                
                # Create solution
                response = await client.post("/api/solutions/", json=solution_payload, headers=headers)
                response.raise_for_status()
                solution = response.json()
                print(f"Created solution: {solution['name']}")
            except httpx.HTTPError as e:
                print(f"Failed to create solution: {solution_data['name']}")
                print(f"Error: {str(e)}")
                print(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
                continue

async def main():
    """Main function to generate test data"""
    try:
        # First verify server is running
        if not await verify_server_running():
            sys.exit(1)
            
        # Clear existing data
        await clear_existing_data()
        
        # Start the test data creation
        print("\nStarting test data generation...")
        await create_test_data()
        print("\nTest data generation completed!")
    except Exception as e:
        print(f"\nError during test data generation: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())