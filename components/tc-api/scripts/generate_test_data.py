#!/usr/bin/env python3
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

# Add the app directory to the Python path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.security import get_password_hash

# Test data constants
DEPARTMENTS = ["Engineering", "Product", "Design", "Operations", "Security"]
TEAMS = {
    "Engineering": ["Frontend", "Backend", "DevOps", "Mobile", "Data", "QA"],
    "Product": ["Product Management", "Product Analytics", "User Research"],
    "Design": ["UX Design", "UI Design", "Design Systems"],
    "Operations": ["IT", "Infrastructure", "Support"],
    "Security": ["Security Operations", "Security Engineering", "Compliance"]
}

CATEGORIES = [
    {"name": "Frontend", "description": "Frontend technologies and frameworks"},
    {"name": "Backend", "description": "Backend technologies and frameworks"},
    {"name": "DevOps", "description": "DevOps tools and practices"},
    {"name": "Database", "description": "Database technologies"},
    {"name": "Cloud", "description": "Cloud platforms and services"},
    {"name": "Security", "description": "Security tools and practices"},
    {"name": "Mobile", "description": "Mobile development technologies"},
    {"name": "AI/ML", "description": "Artificial Intelligence and Machine Learning"},
    {"name": "Analytics", "description": "Analytics and monitoring tools"},
    {"name": "Testing", "description": "Testing tools and frameworks"}
]

TAGS = [
    {"name": "JavaScript", "description": "JavaScript programming language"},
    {"name": "Python", "description": "Python programming language"},
    {"name": "React", "description": "React.js framework"},
    {"name": "Vue", "description": "Vue.js framework"},
    {"name": "Node.js", "description": "Node.js runtime"},
    {"name": "FastAPI", "description": "FastAPI framework"},
    {"name": "Django", "description": "Django framework"},
    {"name": "AWS", "description": "Amazon Web Services"},
    {"name": "GCP", "description": "Google Cloud Platform"},
    {"name": "Azure", "description": "Microsoft Azure"},
    {"name": "Docker", "description": "Docker containerization"},
    {"name": "Kubernetes", "description": "Kubernetes orchestration"},
    {"name": "MongoDB", "description": "MongoDB database"},
    {"name": "PostgreSQL", "description": "PostgreSQL database"},
    {"name": "Redis", "description": "Redis in-memory database"}
]

SOLUTIONS = [
    {
        "name": "React Frontend Framework",
        "description": "React is a JavaScript library for building user interfaces",
        "pros": ["Component-based", "Virtual DOM", "Large ecosystem"],
        "cons": ["Learning curve", "JSX syntax", "State management complexity"]
    },
    {
        "name": "FastAPI Backend Framework",
        "description": "FastAPI is a modern Python web framework for building APIs",
        "pros": ["Fast performance", "Automatic docs", "Type hints"],
        "cons": ["New framework", "Small ecosystem", "Python 3.6+ required"]
    },
    {
        "name": "MongoDB Database",
        "description": "MongoDB is a document-oriented NoSQL database",
        "pros": ["Flexible schema", "Horizontal scaling", "JSON-like documents"],
        "cons": ["Complex transactions", "Memory usage", "No joins"]
    }
]

async def create_test_users(db) -> List[Dict]:
    """Create test users"""
    print("Creating test users...")
    users = []
    # Create superuser
    superuser = {
        "_id": ObjectId(),
        "username": "admin",
        "email": "admin@techcompass.com",
        "hashed_password": get_password_hash("admin"),
        "full_name": "Admin User",
        "is_active": True,
        "is_superuser": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await db.users.insert_one(superuser)
    users.append(superuser)

    # Create regular users
    for i in range(5):
        user = {
            "_id": ObjectId(),
            "username": f"user{i}",
            "email": f"user{i}@techcompass.com",
            "hashed_password": get_password_hash("admin"),
            "full_name": f"Test User {i}",
            "is_active": True,
            "is_superuser": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await db.users.insert_one(user)
        users.append(user)
    
    return users

async def create_test_categories(db, users: List[Dict]) -> List[Dict]:
    """Create test categories"""
    print("Creating test categories...")
    categories = []
    for category in CATEGORIES:
        cat = {
            "_id": ObjectId(),
            **category,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": users[0]["_id"],  # Created by admin
            "updated_by": users[0]["_id"]
        }
        await db.categories.insert_one(cat)
        categories.append(cat)
    return categories

async def create_test_tags(db, users: List[Dict]) -> List[Dict]:
    """Create test tags"""
    print("Creating test tags...")
    tags = []
    for tag in TAGS:
        tag_doc = {
            "_id": ObjectId(),
            **tag,
            "usage_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": users[0]["_id"],  # Created by admin
            "updated_by": users[0]["_id"]
        }
        await db.tags.insert_one(tag_doc)
        tags.append(tag_doc)
    return tags

async def create_test_solutions(db, users: List[Dict], categories: List[Dict], tags: List[Dict]) -> None:
    """Create test solutions"""
    print("Creating test solutions...")
    for solution in SOLUTIONS:
        # Pick random user, category, and tags
        user = random.choice(users)
        category = random.choice(categories)
        solution_tags = random.sample(tags, random.randint(2, 5))
        
        department = random.choice(DEPARTMENTS)
        team = random.choice(TEAMS[department])

        solution_doc = {
            "_id": ObjectId(),
            **solution,
            "slug": solution["name"].lower().replace(" ", "-"),
            "category": str(category["_id"]),
            "status": random.choice(["Draft", "Published", "Archived"]),
            "department": department,
            "team": team,
            "team_email": f"{team.lower().replace(' ', '.')}@techcompass.com",
            "author_id": str(user["_id"]),
            "author_name": user["full_name"],
            "author_email": user["email"],
            "tags": [str(tag["_id"]) for tag in solution_tags],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": user["_id"],
            "updated_by": user["_id"]
        }
        await db.solutions.insert_one(solution_doc)

async def main():
    """Main function to generate test data"""
    print(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    # Clear existing data
    print("Clearing existing data...")
    await db.users.delete_many({})
    await db.categories.delete_many({})
    await db.tags.delete_many({})
    await db.solutions.delete_many({})

    # Create test data
    users = await create_test_users(db)
    categories = await create_test_categories(db, users)
    tags = await create_test_tags(db, users)
    await create_test_solutions(db, users, categories, tags)

    print("\nTest data generation completed!")
    print(f"Database: {db.name}")
    print("\nYou can login with the following credentials:")
    print("Superuser:")
    print("  Username: admin")
    print("  Password: admin")
    print("Regular users:")
    for i in range(5):
        print(f"  Username: user{i}")
        print(f"  Password: admin")

    client.close()

if __name__ == "__main__":
    asyncio.run(main())
