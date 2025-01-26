from typing import List, Tuple, Optional
from datetime import datetime
from bson import ObjectId
from pymongo import DESCENDING, ASCENDING
from fastapi import HTTPException, status

from app.core.database import get_database
from app.models.comment import CommentCreate, CommentInDB

VALID_SORT_FIELDS = {'created_at', 'updated_at'}

class CommentService:
    def __init__(self):
        self.db = get_database()

    async def get_comments(
        self,
        skip: int = 0,
        limit: int = 20,
        sort: str = "-created_at"  # Default sort by created_at desc
    ) -> Tuple[List[CommentInDB], int]:
        """Get all comments with pagination and sorting.
        Default sort is by created_at in descending order (newest first)."""
        
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
        cursor = self.db.comments.find().sort(sort_field, sort_direction).skip(skip).limit(limit)
        comments = [CommentInDB(**comment) async for comment in cursor]
        total = await self.db.comments.count_documents({})
        
        return comments, total

    async def get_solution_comments(
        self,
        solution_slug: str,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "created_at"
    ) -> Tuple[List[CommentInDB], int]:
        """Get all comments for a solution with pagination.
        Comments are sorted by created_at in descending order (newest first)."""
        query = {"solution_slug": solution_slug}
        sort_field = sort_by
        cursor = self.db.comments.find(query).sort(sort_field, DESCENDING).skip(skip).limit(limit)
        comments = [CommentInDB(**comment) async for comment in cursor]
        total = await self.db.comments.count_documents(query)
        return comments, total

    async def get_comment_by_id(self, comment_id: str) -> Optional[CommentInDB]:
        """Get a specific comment by ID"""
        comment = await self.db.comments.find_one({"id": comment_id})
        if comment:
            return CommentInDB(**comment)
        return None

    async def create_comment(
        self,
        solution_slug: str,
        comment: CommentCreate,
        username: str
    ) -> CommentInDB:
        """Create a new comment"""
        # Check if solution exists
        solution = await self.db.solutions.find_one({"slug": solution_slug})
        if not solution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Solution with slug '{solution_slug}' not found"
            )

        now = datetime.utcnow().isoformat()
        comment_dict = comment.model_dump()
        new_comment = {
            "id": str(ObjectId()),
            "solution_slug": solution_slug,
            "username": username,
            "content": comment_dict["content"],
            "created_at": now,
            "updated_at": now
        }
        await self.db.comments.insert_one(new_comment)
        return CommentInDB(**new_comment)

    async def update_comment(
        self,
        comment_id: str,
        content: str,
        username: str
    ) -> Optional[CommentInDB]:
        """Update a comment's content"""
        # First check if comment exists and verify ownership
        existing_comment = await self.db.comments.find_one({"id": comment_id})
        if not existing_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        if existing_comment["username"] != username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this comment"
            )

        now = datetime.utcnow().isoformat()
        result = await self.db.comments.update_one(
            {"id": comment_id, "username": username},  # Double-check ownership
            {
                "$set": {
                    "content": content,
                    "updated_at": now
                }
            }
        )
        return await self.get_comment_by_id(comment_id)

    async def delete_comment(self, comment_id: str, username: str) -> bool:
        """Delete a comment"""
        result = await self.db.comments.delete_one({
            "id": comment_id,
            "username": username  # Only allow deletion by comment author
        })
        return result.deleted_count > 0 