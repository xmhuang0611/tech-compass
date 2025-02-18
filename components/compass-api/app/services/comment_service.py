from datetime import datetime
from typing import List, Optional, Tuple

from bson import ObjectId
from fastapi import HTTPException, status
from pymongo import ASCENDING, DESCENDING

from app.core.database import get_database
from app.models.comment import (
    Comment,
    CommentCreate,
    CommentInDB,
    CommentType,
    CommentUpdate,
)
from app.services.user_service import UserService

VALID_SORT_FIELDS = {"created_at", "updated_at"}


class CommentService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.comments
        self.user_service = UserService()

    async def _convert_to_comment(self, comment_data: dict) -> Comment:
        """Private helper method to convert comment data to Comment model with full name"""
        # Get user's full name from user service
        user_info = await self.user_service.get_user_info(comment_data["username"])
        if user_info:
            comment_data["full_name"] = user_info["full_name"]
        return Comment(**comment_data)

    async def get_comments(
        self,
        skip: int = 0,
        limit: int = 20,
        sort: str = "-created_at",  # Default sort by created_at desc
        type: Optional[CommentType] = None,
        solution_slug: Optional[str] = None,
    ) -> Tuple[List[Comment], int]:
        """Get all comments with pagination, sorting and optional type filtering."""
        query = {}
        if type:
            query["type"] = type
        if solution_slug:
            # Add case-insensitive partial matching for solution_slug
            query["solution_slug"] = {"$regex": solution_slug, "$options": "i"}

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
        cursor = self.collection.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit)

        # Convert to Comment objects with user full names
        comments = []
        async for comment in cursor:
            # If username is missing, use created_by as fallback
            if "username" not in comment:
                comment["username"] = comment["created_by"]
            comments.append(await self._convert_to_comment(comment))

        total = await self.collection.count_documents(query)

        return comments, total

    async def get_solution_comments(
        self,
        solution_slug: str,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        type: Optional[CommentType] = None,
    ) -> Tuple[List[Comment], int]:
        """Get all comments for a solution with pagination and optional type filtering."""
        query = {"solution_slug": solution_slug}
        if type:
            query["type"] = type

        sort_field = sort_by
        cursor = self.collection.find(query).sort(sort_field, DESCENDING).skip(skip).limit(limit)

        # Convert to Comment objects with user full names
        comments = []
        async for comment in cursor:
            # If username is missing, use created_by as fallback
            if "username" not in comment:
                comment["username"] = comment["created_by"]
            comments.append(await self._convert_to_comment(comment))

        total = await self.collection.count_documents(query)
        return comments, total

    async def get_comment_by_id(self, comment_id: str) -> Optional[Comment]:
        """Get a specific comment by ID"""
        comment = await self.collection.find_one({"_id": ObjectId(comment_id)})
        if comment:
            return await self._convert_to_comment(comment)
        return None

    async def _get_comment_or_404(self, comment_id: str) -> CommentInDB:
        """Get a comment by ID or raise 404 if not found."""
        try:
            comment = await self.collection.find_one({"_id": ObjectId(comment_id)})
            if not comment:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
            return CommentInDB(**comment)
        except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid comment ID")

    def check_comment_permission(self, comment: CommentInDB, username: str, is_superuser: bool) -> bool:
        """Check if user has permission to modify the comment.

        Args:
            comment: The comment to check
            username: The username of the user
            is_superuser: Whether the user is a superuser

        Returns:
            True if user has permission, False otherwise
        """
        return is_superuser or comment.created_by == username

    async def create_comment(self, solution_slug: str, comment: CommentCreate, username: str) -> CommentInDB:
        """Create a new comment"""
        # Check if solution exists
        solution = await self.db.solutions.find_one({"slug": solution_slug})
        if not solution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Solution with slug '{solution_slug}' not found",
            )

        now = datetime.utcnow()
        comment_dict = comment.model_dump()
        comment_dict.update(
            {
                "solution_slug": solution_slug,
                "username": username,
                "type": CommentType.USER,  # Always set type to USER for new comments
                "created_at": now,
                "updated_at": now,
                "created_by": username,
                "updated_by": username,
            }
        )
        result = await self.collection.insert_one(comment_dict)
        comment_dict["_id"] = result.inserted_id
        return CommentInDB(**comment_dict)

    async def update_comment(
        self,
        comment_id: str,
        comment_update: CommentUpdate,
        username: str,
        is_superuser: bool,
    ) -> Optional[CommentInDB]:
        """Update a comment.
        Only the comment creator or superusers can update it.
        Only superusers can update the type field, for non-admin users the type field will be ignored."""
        comment = await self._get_comment_or_404(comment_id)

        # Check permission
        if not self.check_comment_permission(comment, username, is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this comment",
            )

        # Get update fields
        update_dict = comment_update.model_dump(exclude_unset=True)

        # Remove type field for non-admin users
        if not is_superuser and "type" in update_dict:
            del update_dict["type"]

        update_dict.update({"updated_at": datetime.utcnow(), "updated_by": username})

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(comment_id)}, {"$set": update_dict}, return_document=True
        )
        return CommentInDB(**result) if result else None

    async def delete_comment(self, comment_id: str, username: str, is_superuser: bool) -> bool:
        """Delete a comment.
        Only the comment creator or superusers can delete it."""
        comment = await self._get_comment_or_404(comment_id)

        # Check permission
        if not self.check_comment_permission(comment, username, is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this comment",
            )

        result = await self.collection.delete_one({"_id": ObjectId(comment_id)})
        return result.deleted_count > 0

    async def count_solution_comments(self, solution_slug: str) -> int:
        """Get total number of comments for a solution."""
        return await self.collection.count_documents({"solution_slug": solution_slug})

    async def get_user_comments(
        self, username: str, skip: int = 0, limit: int = 20, sort: str = "-created_at"
    ) -> Tuple[List[Comment], int]:
        """Get all comments created by a specific user with pagination and sorting.
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

        # Query for user's comments
        query = {"username": username}
        cursor = self.collection.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit)

        # Convert to Comment objects with user full names
        comments = []
        async for comment in cursor:
            comments.append(await self._convert_to_comment(comment))

        total = await self.collection.count_documents(query)
        return comments, total

    async def get_solution_adopted_usernames(self, solution_slug: str) -> set[str]:
        """Get unique usernames of adopted users who commented on a solution.

        Args:
            solution_slug: The slug of the solution

        Returns:
            Set of unique usernames who are marked as adopted users
        """
        pipeline = [
            {"$match": {"solution_slug": solution_slug, "is_adopted_user": True}},
            {"$group": {"_id": None, "usernames": {"$addToSet": "$username"}}},
        ]

        result = await self.collection.aggregate(pipeline).to_list(1)
        if not result:
            return set()

        return set(result[0]["usernames"])
