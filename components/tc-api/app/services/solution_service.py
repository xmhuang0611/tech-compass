from datetime import datetime
from typing import List, Optional
from bson import ObjectId
import re

from app.models.solution import SolutionCreate, SolutionUpdate, SolutionInDB
from app.services.category_service import CategoryService
from app.core.database import get_database

def generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from solution name
    Format: {name}
    Example: docker
    """
    # Convert to lowercase and replace spaces/special chars with hyphens
    name_slug = re.sub(r'[^\w\s-]', '', name.lower())
    # Replace spaces and multiple hyphens with single hyphen
    name_slug = re.sub(r'[-\s]+', '-', name_slug).strip('-')
    return name_slug

class SolutionService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.solutions
        self.category_service = CategoryService()

    async def create_solution(self, solution: SolutionCreate, user_id: Optional[str] = None) -> SolutionInDB:
        """Create a new solution"""
        solution_dict = solution.dict(exclude_unset=True)
        
        # Handle category creation if provided
        if solution.category:
            category = await self.category_service.get_or_create_category(solution.category, user_id)
            solution_dict["category_id"] = category.id
            # Keep category name in the response
            solution_dict["category"] = solution.category
        
        # Generate and ensure unique slug
        base_slug = generate_slug(solution_dict["name"])
        solution_dict["slug"] = await self.ensure_unique_slug(base_slug)
            
        solution_dict["created_at"] = datetime.utcnow()
        solution_dict["updated_at"] = datetime.utcnow()
        if user_id:
            solution_dict["created_by"] = ObjectId(user_id)
            solution_dict["updated_by"] = ObjectId(user_id)

        result = await self.collection.insert_one(solution_dict)
        return await self.get_solution_by_id(str(result.inserted_id))

    async def get_solution_by_id(self, solution_id: str) -> Optional[SolutionInDB]:
        """Get a solution by ID"""
        solution = await self.collection.find_one({"_id": ObjectId(solution_id)})
        if solution:
            # Get category details if category_id exists
            if solution.get("category_id"):
                category = await self.category_service.get_category_by_id(str(solution["category_id"]))
                if category:
                    solution["category"] = category.name
            return SolutionInDB(**solution)
        return None

    async def get_solutions(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        status: Optional[str] = None,
        department: Optional[str] = None
    ) -> List[SolutionInDB]:
        """Get all solutions with filtering and pagination"""
        query = {}
        if category:
            # Get category by name
            category_obj = await self.category_service.get_category_by_name(category)
            if category_obj:
                query["category_id"] = category_obj.id
        if status:
            query["status"] = status
        if department:
            query["department"] = department

        cursor = self.collection.find(query).skip(skip).limit(limit)
        solutions = await cursor.to_list(length=limit)
        
        # Populate category names
        for solution in solutions:
            if solution.get("category_id"):
                category = await self.category_service.get_category_by_id(str(solution["category_id"]))
                if category:
                    solution["category"] = category.name

        return [SolutionInDB(**solution) for solution in solutions]

    async def get_solution_by_slug(self, slug: str) -> Optional[SolutionInDB]:
        """Get a solution by slug"""
        solution = await self.collection.find_one({"slug": slug})
        if solution:
            # Get category details if category_id exists
            if solution.get("category_id"):
                category = await self.category_service.get_category_by_id(str(solution["category_id"]))
                if category:
                    solution["category"] = category.name
            return SolutionInDB(**solution)
        return None

    async def ensure_unique_slug(self, slug: str, exclude_id: Optional[str] = None) -> str:
        """Ensure the slug is unique by appending a number if necessary"""
        base_slug = slug
        counter = 1
        while True:
            # Check if slug exists
            query = {"slug": slug}
            if exclude_id:
                query["_id"] = {"$ne": ObjectId(exclude_id)}
            existing = await self.collection.find_one(query)
            if not existing:
                return slug
            # If exists, append counter and try again
            slug = f"{base_slug}-{counter}"
            counter += 1

    async def update_solution(
        self,
        solution_id: str,
        solution_update: SolutionUpdate,
        user_id: Optional[str] = None
    ) -> Optional[SolutionInDB]:
        """Update a solution"""
        update_dict = solution_update.dict(exclude_unset=True)
        
        # Handle category update
        if "category" in update_dict:
            category = await self.category_service.get_or_create_category(update_dict["category"], user_id)
            update_dict["category_id"] = category.id
            # Keep category name in the response
            update_dict["category"] = update_dict["category"]

        # Handle slug update if name changes
        if "name" in update_dict:
            base_slug = generate_slug(update_dict["name"])
            update_dict["slug"] = await self.ensure_unique_slug(base_slug, solution_id)

        update_dict["updated_at"] = datetime.utcnow()
        if user_id:
            update_dict["updated_by"] = ObjectId(user_id)

        result = await self.collection.update_one(
            {"_id": ObjectId(solution_id)},
            {"$set": update_dict}
        )
        if result.modified_count:
            return await self.get_solution_by_id(solution_id)
        return None

    async def update_solution_by_slug(
        self,
        slug: str,
        solution_update: SolutionUpdate,
        user_id: Optional[str] = None
    ) -> Optional[SolutionInDB]:
        """Update a solution by slug"""
        solution = await self.get_solution_by_slug(slug)
        if not solution:
            return None
        return await self.update_solution(str(solution.id), solution_update, user_id)

    async def delete_solution(self, solution_id: str) -> bool:
        """Delete a solution"""
        result = await self.collection.delete_one({"_id": ObjectId(solution_id)})
        return result.deleted_count > 0

    async def delete_solution_by_slug(self, slug: str) -> bool:
        """Delete a solution by slug"""
        result = await self.collection.delete_one({"slug": slug})
        return result.deleted_count > 0

    async def count_solutions(self) -> int:
        """Get total number of solutions"""
        return await self.collection.count_documents({})
