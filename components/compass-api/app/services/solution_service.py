import re
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from fastapi import logger
from pymongo import ASCENDING, DESCENDING

from app.core.database import get_database
from app.models.solution import SolutionCreate, SolutionUpdate, SolutionInDB, Solution
from app.services.category_service import CategoryService
from app.services.tag_service import TagService
from app.services.rating_service import RatingService

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
        self.rating_service = RatingService()

    async def create_solution(self, solution: SolutionCreate, username: Optional[str] = None) -> SolutionInDB:
        """Create a new solution"""
        solution_dict = solution.model_dump(exclude_unset=True)
        solution_dict["review_status"] = "PENDING"
        
        # Handle category creation if provided
        if solution_dict.get("category"):
            category = await self.category_service.get_or_create_category(solution_dict["category"], username)
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
        stage: Optional[str] = None,
        review_status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        sort: str = "name"
    ) -> List[SolutionInDB]:
        """Get all solutions with filtering and pagination"""
        query = {}
        
        # Add filters if provided
        if category:
            query["category"] = category
        if department:
            query["department"] = department
        if team:
            query["team"] = team
        if recommend_status:
            query["recommend_status"] = recommend_status
        if stage:
            query["stage"] = stage
        if review_status:
            query["review_status"] = review_status
        if tags:
            # Match solutions that have all the specified tags
            query["tags"] = {"$all": tags}

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
        return [SolutionInDB(**solution) for solution in solutions]

    async def get_solution_by_slug(self, slug: str) -> Optional[SolutionInDB]:
        """Get a solution by slug"""
        solution = await self.collection.find_one({"slug": slug})
        if solution:
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

    async def get_solutions_with_ratings(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        department: Optional[str] = None,
        team: Optional[str] = None,
        recommend_status: Optional[str] = None,
        stage: Optional[str] = None,
        review_status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        sort: str = "name"
    ) -> List[Solution]:
        """Get solutions with ratings"""
        solutions = await self.get_solutions(
            skip=skip,
            limit=limit,
            category=category,
            department=department,
            team=team,
            recommend_status=recommend_status,
            stage=stage,
            review_status=review_status,
            tags=tags,
            sort=sort
        )
        
        # Convert to Solution model and add ratings
        result = []
        for solution_in_db in solutions:
            # Convert to dict to allow adding rating fields
            solution_dict = solution_in_db.model_dump()
            rating_summary = await self.rating_service.get_rating_summary(solution_in_db.slug)
            solution_dict["rating"] = rating_summary["average"]
            solution_dict["rating_count"] = rating_summary["count"]
            result.append(Solution(**solution_dict))
            
        return result

    async def get_solution_by_id_with_rating(self, solution_id: str) -> Optional[Solution]:
        """Get a solution by ID with rating"""
        solution = await self.get_solution_by_id(solution_id)
        if solution:
            # Convert to dict to allow adding rating fields
            solution_dict = solution.model_dump()
            rating_summary = await self.rating_service.get_rating_summary(solution.slug)
            solution_dict["rating"] = rating_summary["average"]
            solution_dict["rating_count"] = rating_summary["count"]
            return Solution(**solution_dict)
        return None

    async def get_solution_by_slug_with_rating(self, slug: str) -> Optional[Solution]:
        """Get a solution by slug with rating"""
        solution = await self.get_solution_by_slug(slug)
        if solution:
            # Convert to dict to allow adding rating fields
            solution_dict = solution.model_dump()
            rating_summary = await self.rating_service.get_rating_summary(solution.slug)
            solution_dict["rating"] = rating_summary["average"]
            solution_dict["rating_count"] = rating_summary["count"]
            return Solution(**solution_dict)
        return None

    async def search_solutions(self, keyword: str, limit: int = 6) -> List[Solution]:
        """Search solutions by keyword using text similarity
        Searches across:
        - name (highest weight)
        - brief
        - description
        - category
        - department
        - team
        - maintainer_name
        - pros and cons
        Returns top matches sorted by text relevance score
        """
        # Create text index with field weights if it doesn't exist
        await self.collection.create_index([
            ("name", "text"),
            ("brief", "text"),
            ("description", "text"),
            ("category", "text"),
            ("department", "text"),
            ("team", "text"),
            ("maintainer_name", "text"),
            ("pros", "text"),
            ("cons", "text")
        ], weights={
            "name": 10,        # Highest priority
            "brief": 8,        # Second priority
            "description": 5,  # Third priority
            "category": 3,
            "department": 3,
            "team": 3,
            "maintainer_name": 2,
            "pros": 1,
            "cons": 1
        })

        # Perform text search with score
        cursor = self.collection.find(
            {"$text": {"$search": keyword}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit)

        solutions = await cursor.to_list(length=limit)
        
        # Convert to Solution model with ratings
        result = []
        for solution in solutions:            
            # Add rating information
            solution_model = SolutionInDB(**solution)
            rating_summary = await self.rating_service.get_rating_summary(solution_model.slug)
            solution["rating"] = rating_summary["average"]
            solution["rating_count"] = rating_summary["count"]
            result.append(Solution(**solution))
            
        return result

    async def check_name_exists(self, name: str) -> tuple[bool, int]:
        """Check if a solution name exists and count how many solutions have similar names
        
        Args:
            name: The solution name to check
            
        Returns:
            A tuple of (exists: bool, count: int) where:
            - exists: True if the exact name exists
            - count: Number of solutions with similar names (case-insensitive)
        """
        # Check for exact match
        exact_match = await self.collection.find_one({"name": name})
        exists = exact_match is not None
        
        # Count similar names (case-insensitive)
        similar_count = await self.collection.count_documents(
            {"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}}
        )
        
        return exists, similar_count

    async def delete_solutions_by_name(self, name: str) -> int:
        """Delete all solutions with the exact name (case-sensitive)
        
        Args:
            name: The solution name to delete
            
        Returns:
            Number of solutions deleted
        """
        result = await self.collection.delete_many({"name": name})
        return result.deleted_count

    async def update_solutions_by_name(
        self,
        name: str,
        solution_update: SolutionUpdate,
        username: Optional[str] = None
    ) -> List[SolutionInDB]:
        """Update all solutions with the exact name (case-sensitive)
        
        Args:
            name: The solution name to update
            solution_update: The update data
            username: The username of the user making the update
            
        Returns:
            List of updated solutions
        """
        update_dict = solution_update.model_dump(exclude_unset=True)
        
        # Handle category update if provided
        if "category" in update_dict:
            category = await self.category_service.get_or_create_category(update_dict["category"], username)
            update_dict["category"] = category.name

        # Handle slug update if name changes
        if "name" in update_dict:
            # For each solution being updated, we need to generate a unique slug
            solutions = await self.collection.find({"name": name}).to_list(None)
            for solution in solutions:
                base_slug = generate_slug(update_dict["name"])
                unique_slug = await self.ensure_unique_slug(base_slug, str(solution["_id"]))
                # Update each solution with its unique slug
                await self.collection.update_one(
                    {"_id": solution["_id"]},
                    {"$set": {"slug": unique_slug}}
                )

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

        # Update all matching solutions
        await self.collection.update_many(
            {"name": name},
            {"$set": update_dict}
        )

        # Return all updated solutions
        updated_solutions = await self.collection.find({"name": name if "name" not in update_dict else update_dict["name"]}).to_list(None)
        return [SolutionInDB(**solution) for solution in updated_solutions]
