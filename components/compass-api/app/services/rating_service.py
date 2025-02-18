from datetime import datetime
from typing import Dict, List, Optional, Tuple

from bson import ObjectId
from fastapi import HTTPException, status
from pymongo import ASCENDING, DESCENDING

from app.core.database import get_database
from app.models.rating import Rating, RatingCreate, RatingInDB
from app.services.user_service import UserService

VALID_SORT_FIELDS = {"created_at", "updated_at", "score"}


class RatingService:
    def __init__(self):
        self.db = get_database()
        self.user_service = UserService()

    async def _convert_to_rating(self, rating_data: dict) -> Rating:
        """Private helper method to convert rating data to Rating model with full name"""
        # Get user's full name from user service
        user_info = await self.user_service.get_user_info(rating_data["username"])
        if user_info:
            rating_data["full_name"] = user_info["full_name"]
        return Rating(**rating_data)

    async def get_ratings(
        self,
        skip: int = 0,
        limit: int = 20,
        sort: str = "-created_at",  # Default sort by created_at desc
        solution_slug: Optional[str] = None,
        score: Optional[int] = None,
    ) -> Tuple[List[Rating], int]:
        """Get all ratings with pagination and sorting.
        Default sort is by created_at in descending order (newest first)."""

        # Build query
        query = {}
        if solution_slug:
            # Add case-insensitive partial matching for solution_slug
            query["solution_slug"] = {"$regex": solution_slug, "$options": "i"}
        if score is not None:
            query["score"] = score  # Exact match for score

        # Parse sort parameter
        sort_field = "created_at"
        sort_direction = DESCENDING  # Default to descending

        if sort.startswith("-"):
            sort_field = sort[1:]  # Remove the minus sign
            sort_direction = DESCENDING
        else:
            sort_field = sort
            sort_direction = ASCENDING

        # Validate sort field
        if sort_field not in VALID_SORT_FIELDS:
            raise ValueError(f"Invalid sort field: {sort_field}. Valid fields are: {', '.join(VALID_SORT_FIELDS)}")

        # Execute query with sort
        cursor = self.db.ratings.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit)
        ratings = [await self._convert_to_rating(rating) async for rating in cursor]
        total = await self.db.ratings.count_documents(query)

        return ratings, total

    async def get_solution_ratings(
        self, solution_slug: str, skip: int, limit: int, sort_by: str
    ) -> Tuple[List[Rating], int]:
        query = {"solution_slug": solution_slug}
        sort_field = "created_at" if sort_by == "created_at" else "score"
        cursor = self.db.ratings.find(query).sort(sort_field, DESCENDING).skip(skip).limit(limit)
        ratings = [await self._convert_to_rating(rating) async for rating in cursor]
        total = await self.db.ratings.count_documents(query)
        return ratings, total

    async def get_user_rating(self, solution_slug: str, username: str) -> Optional[Rating]:
        rating = await self.db.ratings.find_one({"solution_slug": solution_slug, "username": username})
        if rating:
            return await self._convert_to_rating(rating)
        return None

    async def get_rating_summary(self, solution_slug: str) -> Dict:
        """Get rating summary statistics for a solution"""
        pipeline = [
            {"$match": {"solution_slug": solution_slug}},
            {
                "$group": {
                    "_id": None,
                    "average": {"$avg": "$score"},
                    "count": {"$sum": 1},
                    "scores": {"$push": "$score"},
                }
            },
        ]

        result = await self.db.ratings.aggregate(pipeline).to_list(1)
        if not result:
            return {
                "average": 0,
                "count": 0,
                "distribution": {str(i): 0 for i in range(1, 6)},
            }

        summary = result[0]
        # Calculate distribution
        distribution = {str(i): 0 for i in range(1, 6)}
        for score in summary["scores"]:
            distribution[str(score)] += 1

        return {
            "average": round(summary["average"], 2),
            "count": summary["count"],
            "distribution": distribution,
        }

    async def create_or_update_rating(self, solution_slug: str, rating: RatingCreate, username: str) -> RatingInDB:
        # First check if solution exists
        solution = await self.db.solutions.find_one({"slug": solution_slug})
        if not solution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Solution with slug '{solution_slug}' not found",
            )

        now = datetime.utcnow()
        rating_data = rating.model_dump()

        # Try to update existing rating first
        result = await self.db.ratings.update_one(
            {"solution_slug": solution_slug, "username": username},
            {
                "$set": {
                    "score": rating_data["score"],
                    "comment": rating_data.get("comment"),
                    "is_adopted_user": rating_data.get("is_adopted_user", False),
                    "updated_at": now,
                }
            },
        )

        # If no existing rating was updated, create a new one
        if result.modified_count == 0:
            new_rating = {
                "solution_slug": solution_slug,
                "username": username,
                "score": rating_data["score"],
                "comment": rating_data.get("comment"),
                "is_adopted_user": rating_data.get("is_adopted_user", False),
                "created_at": now,
                "updated_at": now,
            }
            await self.db.ratings.insert_one(new_rating)
            return RatingInDB(**new_rating)

        # Return the updated rating
        return await self.get_user_rating(solution_slug, username)

    async def get_user_ratings(
        self, username: str, skip: int = 0, limit: int = 20, sort: str = "-created_at"
    ) -> Tuple[List[Rating], int]:
        """Get all ratings created by a specific user with pagination and sorting.
        Default sort is by created_at in descending order (newest first)."""

        # Parse sort parameter
        if sort.startswith("-"):
            sort_field = sort[1:]  # Remove the minus sign
            sort_direction = DESCENDING
        else:
            sort_field = sort
            sort_direction = ASCENDING

        # Validate sort field
        if sort_field not in VALID_SORT_FIELDS:
            raise ValueError(f"Invalid sort field: {sort_field}. Valid fields are: {', '.join(VALID_SORT_FIELDS)}")

        # Query for user's ratings
        query = {"username": username}
        cursor = self.db.ratings.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit)

        # Convert to Rating objects with user full names
        ratings = [await self._convert_to_rating(rating) async for rating in cursor]
        total = await self.db.ratings.count_documents(query)

        return ratings, total

    async def _get_rating_or_404(self, rating_id: str) -> RatingInDB:
        """Get a rating by ID or raise 404 if not found."""
        try:
            rating = await self.db.ratings.find_one({"_id": ObjectId(rating_id)})
            if not rating:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
            return RatingInDB(**rating)
        except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid rating ID")

    def check_rating_permission(self, rating: RatingInDB, username: str, is_superuser: bool) -> bool:
        """Check if user has permission to modify the rating.

        Args:
            rating: The rating to check
            username: The username of the user
            is_superuser: Whether the user is a superuser

        Returns:
            True if user has permission, False otherwise
        """
        return is_superuser or rating.username == username

    async def update_rating(
        self,
        rating_id: str,
        rating_update: RatingCreate,
        username: str,
        is_superuser: bool,
    ) -> Optional[RatingInDB]:
        """Update a rating.
        Only the rating creator or superusers can update it."""
        rating = await self._get_rating_or_404(rating_id)

        # Check permission
        if not self.check_rating_permission(rating, username, is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this rating",
            )

        update_dict = rating_update.model_dump()
        update_dict.update({"updated_at": datetime.utcnow(), "updated_by": username})

        result = await self.db.ratings.find_one_and_update(
            {"_id": ObjectId(rating_id)}, {"$set": update_dict}, return_document=True
        )
        return RatingInDB(**result) if result else None

    async def delete_rating(self, rating_id: str, username: str, is_superuser: bool) -> bool:
        """Delete a rating.
        Only the rating creator or superusers can delete it."""
        rating = await self._get_rating_or_404(rating_id)

        # Check permission
        if not self.check_rating_permission(rating, username, is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this rating",
            )

        result = await self.db.ratings.delete_one({"_id": ObjectId(rating_id)})
        return result.deleted_count > 0

    async def get_solution_adopted_usernames(self, solution_slug: str) -> set[str]:
        """Get unique usernames of adopted users who rated a solution.

        Args:
            solution_slug: The slug of the solution

        Returns:
            Set of unique usernames who are marked as adopted users
        """
        pipeline = [
            {"$match": {"solution_slug": solution_slug, "is_adopted_user": True}},
            {"$group": {"_id": None, "usernames": {"$addToSet": "$username"}}},
        ]

        result = await self.db.ratings.aggregate(pipeline).to_list(1)
        if not result:
            return set()

        return set(result[0]["usernames"])
