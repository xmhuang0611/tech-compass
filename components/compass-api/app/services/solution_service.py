import re
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from fastapi import logger
from pymongo import ASCENDING, DESCENDING

from app.core.database import get_database
from app.models.history import ChangeType
from app.models.solution import Solution, SolutionCreate, SolutionInDB, SolutionUpdate
from app.services.category_service import CategoryService
from app.services.history_service import HistoryService
from app.services.rating_service import RatingService
from app.services.tag_service import TagService

VALID_SORT_FIELDS = {"name", "category", "created_at", "updated_at"}


def generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from solution name
    Format: {name}
    Example: docker
    """
    # Convert to lowercase and replace spaces/special chars with hyphens
    name_slug = re.sub(r"[^\w\s-]", "", name.lower())
    # Replace spaces and multiple hyphens with single hyphen
    name_slug = re.sub(r"[-\s]+", "-", name_slug).strip("-")
    return name_slug


class SolutionService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.solutions
        self.category_service = CategoryService()
        self.tag_service = TagService()
        self.rating_service = RatingService()
        self.history_service = HistoryService()

    async def _get_user_info(self, username: str) -> Optional[dict]:
        """Get user information from users collection

        Args:
            username: The username to look up

        Returns:
            User document if found, None otherwise
        """
        return await self.db.users.find_one({"username": username})

    async def _process_category(self, category_name: str, username: Optional[str] = None) -> str:
        """Process category creation/update

        Args:
            category_name: The category name to process
            username: The username performing the operation

        Returns:
            The processed category name
        """
        category = await self.category_service.get_or_create_category(category_name, username)
        return category.name

    async def _process_tags(self, tags: List[str], username: Optional[str] = None) -> List[str]:
        """Process tags creation/update

        Args:
            tags: List of tag names to process
            username: The username performing the operation

        Returns:
            List of processed tag names
        """
        formatted_tags = []
        # Get unique tags first
        unique_tags = list(set(tags))
        for tag_name in unique_tags:
            # Create tag if it doesn't exist
            tag = await self.tag_service.get_tag_by_name(tag_name)
            if not tag:
                from app.models.tag import TagCreate

                tag_create = TagCreate(name=tag_name, description=f"Tag for {tag_name}")
                tag = await self.tag_service.create_tag(tag_create, username)
            formatted_tags.append(tag.name)
        return formatted_tags

    async def _process_solution_update(
        self,
        update_dict: dict,
        username: Optional[str] = None,
        existing_solution: Optional[SolutionInDB] = None,
    ) -> None:
        """Process common solution update operations

        Args:
            update_dict: The update dictionary to process
            username: The username performing the operation
            existing_solution: Optional existing solution to check maintainer fields
        """
        # Handle category update
        if "category" in update_dict:
            update_dict["category"] = await self._process_category(update_dict["category"], username)

        # Handle tags update
        if "tags" in update_dict:
            update_dict["tags"] = await self._process_tags(update_dict["tags"], username)

        # Handle maintainer fields update
        maintainer_fields = {"maintainer_id", "maintainer_name", "maintainer_email"}

        # Ensure maintainer_id is lowercase if provided
        if "maintainer_id" in update_dict and update_dict["maintainer_id"]:
            update_dict["maintainer_id"] = update_dict["maintainer_id"].lower()

        if existing_solution:
            # Check if existing solution has any maintainer field
            has_existing_maintainer = any(getattr(existing_solution, field) for field in maintainer_fields)

            has_maintainer_update = any(field in update_dict for field in maintainer_fields)

            if not has_existing_maintainer and not has_maintainer_update and username:
                # If no maintainer info exists and no update provided, use current user
                user = await self.db.users.find_one({"username": username})
                if user:
                    update_dict["maintainer_id"] = username
                    update_dict["maintainer_name"] = user.get("full_name")
                    update_dict["maintainer_email"] = user.get("email")

        # Update timestamp and user fields
        update_dict["updated_at"] = datetime.utcnow()
        if username:
            update_dict["updated_by"] = username

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

    async def delete_solutions_by_name(self, name: str, username: Optional[str] = None) -> int:
        """Delete all solutions with the exact name (case-sensitive)

        Args:
            name: The solution name to delete
            username: The username of the user making the deletion

        Returns:
            Number of solutions deleted
        """
        # Get solutions before deleting for history records
        cursor = self.collection.find({"name": name})
        solutions = [SolutionInDB(**solution) async for solution in cursor]

        if not solutions:
            return 0

        result = await self.collection.delete_many({"name": name})

        # Record history for each deleted solution
        for solution in solutions:
            await self.history_service.record_object_change(
                object_type="solution",
                object_id=str(solution.id),
                object_name=solution.name,
                change_type=ChangeType.DELETE,
                username=username or "system",
                change_summary=f"Deleted solution '{solution.name}' as part of bulk delete by name",
            )

        return result.deleted_count

    async def update_solutions_by_name(
        self, name: str, solution_update: SolutionUpdate, username: Optional[str] = None
    ) -> List[SolutionInDB]:
        """Update all solutions with the exact name (case-sensitive)

        Args:
            name: The solution name to update
            solution_update: The update data
            username: The username of the user making the update

        Returns:
            List of updated solutions
        """
        # Get all solutions with the same name
        solutions = []
        async for solution in self.collection.find({"name": name}):
            solutions.append(SolutionInDB(**solution))

        # Update each solution individually
        updated_solutions = []
        for solution in solutions:
            updated = await self.update_solution(solution, solution_update, username)
            if updated:
                updated_solutions.append(updated)

        return updated_solutions

    async def create_solution(self, solution: SolutionCreate, username: Optional[str] = None) -> SolutionInDB:
        """Create a new solution"""
        solution_dict = solution.model_dump(exclude_unset=True)
        solution_dict["review_status"] = "PENDING"

        # Generate and ensure unique slug
        base_slug = generate_slug(solution_dict["name"])
        solution_dict["slug"] = await self.ensure_unique_slug(base_slug)

        # Process common solution fields
        await self._process_solution_update(solution_dict, username)

        # Set creation timestamp
        solution_dict["created_at"] = solution_dict["updated_at"]
        if username:
            solution_dict["created_by"] = username

        result = await self.collection.insert_one(solution_dict)
        created_solution = await self.get_solution_by_id(str(result.inserted_id))

        # Record history for creation
        if created_solution:
            await self.history_service.record_object_change(
                object_type="solution",
                object_id=str(result.inserted_id),
                object_name=created_solution.name,
                change_type=ChangeType.CREATE,
                username=username or "system",
                changes=solution_dict,
                old_values=None,
            )

        return created_solution

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
        sort: str = "name",
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
        existing_solution: SolutionInDB,
        solution_update: SolutionUpdate,
        username: Optional[str] = None,
    ) -> Optional[SolutionInDB]:
        """Update a solution

        Args:
            existing_solution: The existing solution to update
            solution_update: The update data
            username: The username of the user making the update

        Returns:
            Updated solution if successful, None otherwise
        """
        update_dict = solution_update.model_dump(exclude_unset=True)

        # Store original values for history tracking
        old_values = {field: getattr(existing_solution, field) for field in update_dict.keys()}

        # Handle slug update if name changes
        if "name" in update_dict:
            base_slug = generate_slug(update_dict["name"])
            update_dict["slug"] = await self.ensure_unique_slug(base_slug, str(existing_solution.id))

        # Process common update operations
        await self._process_solution_update(update_dict, username, existing_solution)

        result = await self.collection.update_one({"_id": existing_solution.id}, {"$set": update_dict})
        if result.modified_count:
            updated_solution = await self.get_solution_by_id(str(existing_solution.id))

            # Record history
            if updated_solution:
                # remove field: slug, updated_at, updated_by
                update_dict.pop("slug", None)
                update_dict.pop("updated_at", None)
                update_dict.pop("updated_by", None)

                # record change if update_dict is not empty
                if update_dict:
                    await self.history_service.record_object_change(
                        object_type="solution",
                        object_id=str(existing_solution.id),
                        object_name=updated_solution.name,
                        change_type=ChangeType.UPDATE,
                        username=username or "system",
                        changes=update_dict,
                        old_values=old_values,
                    )

            return updated_solution
        return None

    async def update_solution_by_slug(
        self, slug: str, solution_update: SolutionUpdate, username: Optional[str] = None
    ) -> Optional[SolutionInDB]:
        """Update a solution by slug"""
        solution = await self.get_solution_by_slug(slug)
        if not solution:
            return None
        return await self.update_solution(solution, solution_update, username)

    async def delete_solution(self, solution_id: str, username: Optional[str] = None) -> bool:
        """Delete a solution"""
        # Get solution before deleting for history record
        solution = await self.get_solution_by_id(solution_id)
        if not solution:
            return False

        result = await self.collection.delete_one({"_id": ObjectId(solution_id)})

        if result.deleted_count > 0:
            # Record deletion in history
            await self.history_service.record_object_change(
                object_type="solution",
                object_id=solution_id,
                object_name=solution.name,
                change_type=ChangeType.DELETE,
                username=username or "system",
                change_summary=f"Deleted solution '{solution.name}'",
            )
            return True
        return False

    async def delete_solution_by_slug(self, slug: str, username: Optional[str] = None) -> bool:
        """Delete a solution by slug"""
        # Get solution before deleting for history record
        solution = await self.get_solution_by_slug(slug)
        if not solution:
            return False

        result = await self.collection.delete_one({"slug": slug})

        if result.deleted_count > 0:
            # Record deletion in history
            await self.history_service.record_object_change(
                object_type="solution",
                object_id=str(solution.id),
                object_name=solution.name,
                change_type=ChangeType.DELETE,
                username=username or "system",
                change_summary=f"Deleted solution '{solution.name}'",
            )
            return True
        return False

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
        sort: str = "name",
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
            sort=sort,
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

    async def search_solutions(self, keyword: str) -> List[Solution]:
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
        Returns all approved matches sorted by recommend_status (ADOPT first) and then by text relevance score
        """
        # Create text index with field weights if it doesn't exist
        await self.collection.create_index(
            [
                ("name", "text"),
                ("brief", "text"),
                ("description", "text"),
                ("category", "text"),
                ("department", "text"),
                ("team", "text"),
                ("maintainer_name", "text"),
                ("pros", "text"),
                ("cons", "text"),
            ],
            weights={
                "name": 10,  # Highest priority
                "brief": 8,  # Second priority
                "description": 5,  # Third priority
                "category": 3,
                "department": 3,
                "team": 3,
                "maintainer_name": 2,
                "pros": 1,
                "cons": 1,
            },
        )

        # Create index for recommend_status for faster sorting
        await self.collection.create_index([("recommend_status", 1)])

        # Perform text search with simple match
        pipeline = [{"$match": {"$text": {"$search": keyword}, "review_status": "APPROVED"}}]

        solutions = await self.collection.aggregate(pipeline).to_list(length=None)

        # Group solutions by recommend status and add ratings
        adopt_solutions = []
        trial_solutions = []
        assess_solutions = []
        hold_solutions = []
        other_solutions = []

        # Add ratings and group by status
        for solution in solutions:
            rating_summary = await self.rating_service.get_rating_summary(solution["slug"])
            solution["rating"] = rating_summary["average"]
            solution["rating_count"] = rating_summary["count"]
            solution_obj = Solution(**solution)

            # Group by recommendation status
            if solution["recommend_status"] == "ADOPT":
                adopt_solutions.append(solution_obj)
            elif solution["recommend_status"] == "TRIAL":
                trial_solutions.append(solution_obj)
            elif solution["recommend_status"] == "ASSESS":
                assess_solutions.append(solution_obj)
            elif solution["recommend_status"] == "HOLD":
                hold_solutions.append(solution_obj)
            else:
                other_solutions.append(solution_obj)

        # Sort each group by rating
        for solutions_list in [
            adopt_solutions,
            trial_solutions,
            assess_solutions,
            hold_solutions,
            other_solutions,
        ]:
            solutions_list.sort(key=lambda x: (x.rating or 0), reverse=True)

        # Combine all groups maintaining order by status
        return adopt_solutions + trial_solutions + assess_solutions + hold_solutions + other_solutions

    async def get_user_solutions(
        self, username: str, skip: int = 0, limit: int = 100, sort: str = "name"
    ) -> List[Solution]:
        """Get solutions created by or maintained by the user

        Args:
            username: The username to get solutions for
            skip: Number of solutions to skip
            limit: Maximum number of solutions to return
            sort: Sort field (name, category, created_at, updated_at)

        Returns:
            List of solutions created by or maintained by the user
        """
        # Query for solutions where user is creator or maintainer
        query = {"$or": [{"created_by": username}, {"maintainer_id": username}]}

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

        # Convert to Solution model and add ratings
        result = []
        for solution in solutions:
            # Convert to dict to allow adding rating fields
            solution_dict = solution
            rating_summary = await self.rating_service.get_rating_summary(solution["slug"])
            solution_dict["rating"] = rating_summary["average"]
            solution_dict["rating_count"] = rating_summary["count"]
            result.append(Solution(**solution_dict))

        return result

    async def count_user_solutions(self, username: str) -> int:
        """Get total number of solutions created by or maintained by the user"""
        query = {"$or": [{"created_by": username}, {"maintainer_id": username}]}
        return await self.collection.count_documents(query)

    async def check_user_solution_permission(self, solution: SolutionInDB, username: str, is_superuser: bool) -> bool:
        """Check if user has permission to modify the solution.

        Args:
            solution: The solution to check
            username: The username of the user
            is_superuser: Whether the user is a superuser

        Returns:
            True if user has permission, False otherwise
        """
        if is_superuser:
            return True

        return solution.created_by == username or solution.maintainer_id == username
