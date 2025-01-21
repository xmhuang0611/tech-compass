from typing import List, Tuple, Optional
from datetime import datetime
from bson import ObjectId
from pymongo import DESCENDING

from app.core.database import get_database
from app.models.comment import CommentCreate, CommentInDB

class CommentService:
    def __init__(self):
        self.db = get_database()

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
        now = datetime.utcnow().isoformat()
        result = await self.db.comments.update_one(
            {"id": comment_id, "username": username},  # Only allow update by comment author
            {
                "$set": {
                    "content": content,
                    "updated_at": now
                }
            }
        )
        if result.modified_count == 0:
            return None
        return await self.get_comment_by_id(comment_id)

    async def delete_comment(self, comment_id: str, username: str) -> bool:
        """Delete a comment"""
        result = await self.db.comments.delete_one({
            "id": comment_id,
            "username": username  # Only allow deletion by comment author
        })
        return result.deleted_count > 0 