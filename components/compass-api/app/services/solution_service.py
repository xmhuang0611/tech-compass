import re
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from app.core.database import get_database
from app.models.solution import SolutionCreate, SolutionUpdate, SolutionInDB
from app.services.category_service import CategoryService
from app.services.tag_service import TagService

VALID_SORT_FIELDS = {'name', 'category', 'created_at', 'updated_at'}

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
        self.tag_service = TagService()

    async def create_solution(self, solution: SolutionCreate, username: Optional[str] = None) -> SolutionInDB:
        """Create a new solution"""
        solution_dict = solution.model_dump(exclude_unset=True)
        
        # Handle category creation if provided
        if solution_dict.get("category"):
            category = await self.category_service.get_or_create_category(solution_dict["category"], username)
            solution_dict["category_id"] = category.id
            # Keep category name in the response
            solution_dict["category"] = category.name
        
        # Generate and ensure unique slug
        base_slug = generate_slug(solution_dict["name"])
        solution_dict["slug"] = await self.ensure_unique_slug(base_slug)
            
        # Set maintainer fields if not provided
        if not solution_dict.get("maintainer_id") and username:
            solution_dict["maintainer_id"] = username
        if not solution_dict.get("maintainer_name") and username:
            # Try to get user's full name from users collection
            user = await self.db.users.find_one({"username": username})
            if user and user.get("full_name"):
                solution_dict["maintainer_name"] = user["full_name"]
        if not solution_dict.get("maintainer_email") and username:
            # Try to get user's email from users collection
            user = await self.db.users.find_one({"username": username})
            if user and user.get("email"):
                solution_dict["maintainer_email"] = user["email"]

        # Handle tags
        if "tags" in solution_dict:
            formatted_tags = []
            # Get unique tags first
            unique_tags = list(set(solution_dict["tags"]))
            for tag_name in unique_tags:
                # Create tag if it doesn't exist
                tag = await self.tag_service.get_tag_by_name(tag_name)
                if not tag:
                    from app.models.tag import TagCreate
                    tag_create = TagCreate(
                        name=tag_name,
                        description=f"Tag for {tag_name}"
                    )
                    tag = await self.tag_service.create_tag(tag_create, username)
                formatted_tags.append(tag.name)
            solution_dict["tags"] = formatted_tags

        solution_dict["created_at"] = datetime.utcnow()
        solution_dict["updated_at"] = datetime.utcnow()
        if username:
            solution_dict["created_by"] = username
            solution_dict["updated_by"] = username

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
        department: Optional[str] = None,
        team: Optional[str] = None,
        recommend_status: Optional[str] = None,
        radar_status: Optional[str] = None,
        stage: Optional[str] = None,
        sort: str = "name"
    ) -> List[SolutionInDB]:
        """Get all solutions with filtering and pagination"""
        query = {}
        
        # Add filters if provided
        if category:
            # Get category by name
            category_obj = await self.category_service.get_category_by_name(category)
            if category_obj:
                query["category_id"] = category_obj.id
        if department:
            query["department"] = department
        if team:
            query["team"] = team
        if recommend_status:
            query["recommend_status"] = recommend_status
        if radar_status:
            query["radar_status"] = radar_status
        if stage:
            query["stage"] = stage

        # Parse sort parameter
        sort_field = "name"
        sort_direction = ASCENDING

        if sort.startswith("-"):
            sort_field = sort[1:]  # Remove the minus sign
            sort_direction = DESCENDING
        else:
            sort_field = sort

        # Validate sort field
        if sort_field not in VALID_SORT_FIELDS:
            raise ValueError(f"Invalid sort field: {sort_field}. Valid fields are: {', '.join(VALID_SORT_FIELDS)}")

        cursor = self.collection.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit)
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
        username: Optional[str] = None
    ) -> Optional[SolutionInDB]:
        """Update a solution"""
        update_dict = solution_update.model_dump(exclude_unset=True)
        
        # Handle category update
        if "category" in update_dict:
            category = await self.category_service.get_or_create_category(update_dict["category"], username)
            update_dict["category_id"] = category.id
            # Keep category name in the response
            update_dict["category"] = update_dict["category"]

        # Handle slug update if name changes
        if "name" in update_dict:
            base_slug = generate_slug(update_dict["name"])
            update_dict["slug"] = await self.ensure_unique_slug(base_slug, solution_id)

        # Handle tags update
        if "tags" in update_dict:
            # Get distinct tags first
            distinct_tags = list(set(update_dict["tags"]))
            formatted_tags = []
            for tag_name in distinct_tags:
                # Create tag if it doesn't exist
                tag = await self.tag_service.get_tag_by_name(tag_name)
                if not tag:
                    from app.models.tag import TagCreate
                    tag_create = TagCreate(
                        name=tag_name,
                        description=f"Tag for {tag_name}"
                    )
                    tag = await self.tag_service.create_tag(tag_create, username)
                formatted_tags.append(tag.name)
            update_dict["tags"] = formatted_tags

        # Update maintainer fields if provided
        if "maintainer_id" in update_dict and username:
            # Try to get user's info from users collection
            user = await self.db.users.find_one({"username": update_dict["maintainer_id"]})
            if user:
                if not update_dict.get("maintainer_name"):
                    update_dict["maintainer_name"] = user.get("full_name")
                if not update_dict.get("maintainer_email"):
                    update_dict["maintainer_email"] = user.get("email")

        update_dict["updated_at"] = datetime.utcnow()
        if username:
            update_dict["updated_by"] = username

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
        username: Optional[str] = None
    ) -> Optional[SolutionInDB]:
        """Update a solution by slug"""
        solution = await self.get_solution_by_slug(slug)
        if not solution:
            return None
        return await self.update_solution(str(solution.id), solution_update, username)

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

    async def get_departments(self) -> List[str]:
        """Get all unique department names from solutions"""
        try:
            # Use MongoDB distinct to get unique department values
            departments = await self.collection.distinct("department")
            # Filter out None/empty values and sort alphabetically
            return sorted([dept for dept in departments if dept])
        except Exception as e:
            logger.error(f"Error getting departments: {str(e)}")
            raise
