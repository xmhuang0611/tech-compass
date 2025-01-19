#!/usr/bin/env python3
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
from app.core.security import get_password_hash

def generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from a name"""
    return name.lower().replace(" ", "-")

# Test data
ADMIN_USER = {
    "username": "admin@techcompass.com",
    "email": "admin@techcompass.com",
    "full_name": "Admin User",
    "hashed_password": get_password_hash("admin123"),
    "is_active": True,
    "is_superuser": True,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
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
        "slug": "microservices-architecture",
        "category": "Development",
        "status": "Active",
        "department": "Engineering",
        "team": "Backend",
        "team_email": "backend@techcompass.com"
    },
    {
        "name": "Kubernetes Deployment",
        "description": "Standard Kubernetes deployment patterns",
        "slug": "kubernetes-deployment",
        "category": "Infrastructure",
        "status": "Active",
        "department": "DevOps",
        "team": "Infrastructure",
        "team_email": "infrastructure@techcompass.com"
    },
    {
        "name": "Zero Trust Security",
        "description": "Implementing zero trust security model",
        "slug": "zero-trust-security",
        "category": "Security",
        "status": "Draft",
        "department": "Security",
        "team": "Security Engineering",
        "team_email": "security.engineering@techcompass.com"
    },
    {
        "name": "Data Lake Architecture",
        "description": "Building scalable data lakes",
        "slug": "data-lake-architecture",
        "category": "Data",
        "status": "Active",
        "department": "Data",
        "team": "Data Engineering",
        "team_email": "data.engineering@techcompass.com"
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

async def create_admin_user():
    """Create admin user directly in database"""
    print("\nCreating admin user...")
    db = get_database()
    await db.users.delete_many({"email": ADMIN_USER["email"]})
    await db.users.insert_one(ADMIN_USER)
    print("Admin user created.")

async def get_access_token(client: httpx.AsyncClient) -> str:
    """Get access token for authentication"""
    login_data = {
        "username": "admin@techcompass.com",
        "password": "admin123"
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
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Get access token
        access_token = await get_access_token(client)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Create categories
        print("\nCreating categories...")
        categories = []
        for category_data in CATEGORIES:
            try:
                response = await client.post("/api/categories/", json=category_data, headers=headers)
                response.raise_for_status()
                category = response.json()
                categories.append(category)
                print(f"Created category: {category['name']}")
            except httpx.HTTPError as e:
                print(f"Failed to create category: {category_data['name']}")
                print(f"Error: {str(e)}")
                continue

        # Create solutions
        print("\nCreating solutions...")
        for solution_data in SOLUTIONS:
            try:
                response = await client.post("/api/solutions/", json=solution_data, headers=headers)
                response.raise_for_status()
                solution = response.json()
                print(f"Created solution: {solution['name']}")
            except httpx.HTTPError as e:
                print(f"Failed to create solution: {solution_data['name']}")
                print(f"Error: {str(e)}")
                continue

async def main():
    """Main function to generate test data"""
    try:
        # First clear existing data
        await clear_existing_data()
        
        # Create admin user
        await create_admin_user()
        
        # Start the test data creation
        print("\nStarting test data generation...")
        await create_test_data()
        print("\nTest data generation completed!")
    except Exception as e:
        print(f"\nError during test data generation: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
