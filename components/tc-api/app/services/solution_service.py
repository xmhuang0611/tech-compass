from datetime import datetime
from typing import List, Optional
from bson import ObjectId

from app.models.solution import SolutionCreate, SolutionUpdate, SolutionInDB
from app.services.category_service import CategoryService
from app.core.database import get_database

def generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from a name"""
    return name.lower().replace(" ", "-")

class SolutionService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.solutions
        self.category_service = CategoryService()

    async def create_solution(self, solution: SolutionCreate, user_id: Optional[str] = None) -> SolutionInDB:
        """Create a new solution"""
        # First ensure category exists
        if solution.category:
            category = await self.category_service.get_or_create_category(solution.category, user_id)
            solution.category_id = category.id

        solution_dict = solution.dict(exclude_unset=True)
        
        # Generate slug if not provided
        if "slug" not in solution_dict:
            solution_dict["slug"] = generate_slug(solution_dict["name"])
            
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

    async def delete_solution(self, solution_id: str) -> bool:
        """Delete a solution"""
        result = await self.collection.delete_one({"_id": ObjectId(solution_id)})
        return result.deleted_count > 0
