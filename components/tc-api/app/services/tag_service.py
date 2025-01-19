from datetime import datetime
from typing import List, Optional
from bson import ObjectId

from app.models.tag import TagCreate, TagUpdate, TagInDB, TagList
from app.core.database import get_database

class TagService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.tags

    async def create_tag(self, tag: TagCreate, user_id: Optional[str] = None) -> TagInDB:
        """Create a new tag"""
        # Check if tag already exists
        existing_tag = await self.get_tag_by_name(tag.name)
        if existing_tag:
            raise ValueError("Tag already exists")

        tag_dict = tag.dict()
        tag_dict["created_at"] = datetime.utcnow()
        tag_dict["updated_at"] = datetime.utcnow()
        tag_dict["usage_count"] = 0
        if user_id:
            tag_dict["created_by"] = ObjectId(user_id)
            tag_dict["updated_by"] = ObjectId(user_id)

        result = await self.collection.insert_one(tag_dict)
        return await self.get_tag_by_id(str(result.inserted_id))

    async def get_tag_by_id(self, tag_id: str) -> Optional[TagInDB]:
        """Get a tag by ID"""
        tag = await self.collection.find_one({"_id": ObjectId(tag_id)})
        if tag:
            return TagInDB(**tag)
        return None

    async def get_tag_by_name(self, name: str) -> Optional[TagInDB]:
        """Get a tag by name"""
        tag = await self.collection.find_one({"name": name})
        if tag:
            return TagInDB(**tag)
        return None

    async def get_tags(self, skip: int = 0, limit: int = 100) -> TagList:
        """Get all tags with pagination"""
        # Get tags with usage count
        pipeline = [
            {
                "$lookup": {
                    "from": "solutions",
                    "localField": "_id",
                    "foreignField": "tags",
                    "as": "solutions"
                }
            },
            {
                "$addFields": {
                    "usage_count": {"$size": "$solutions"}
                }
            },
            {
                "$project": {
                    "solutions": 0
                }
            },
            {
                "$skip": skip
            },
            {
                "$limit": limit
            }
        ]
        cursor = self.collection.aggregate(pipeline)
        tags = await cursor.to_list(length=limit)
        return TagList(tags=[TagInDB(**tag) for tag in tags])

    async def update_tag(
        self,
        tag_id: str,
        tag_update: TagUpdate,
        user_id: Optional[str] = None
    ) -> Optional[TagInDB]:
        """Update a tag"""
        update_dict = tag_update.dict(exclude_unset=True)
        
        # Check name uniqueness if being updated
        if "name" in update_dict:
            existing_tag = await self.get_tag_by_name(update_dict["name"])
            if existing_tag and str(existing_tag.id) != tag_id:
                raise ValueError("Tag name is already in use")

        update_dict["updated_at"] = datetime.utcnow()
        if user_id:
            update_dict["updated_by"] = ObjectId(user_id)

        result = await self.collection.update_one(
            {"_id": ObjectId(tag_id)},
            {"$set": update_dict}
        )
        if result.modified_count:
            return await self.get_tag_by_id(tag_id)
        return None

    async def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag"""
        # Check if tag is being used by any solutions
        solutions_using_tag = await self.db.solutions.find_one({"tags": ObjectId(tag_id)})
        if solutions_using_tag:
            raise ValueError("Cannot delete tag as it is being used by solutions")

        result = await self.collection.delete_one({"_id": ObjectId(tag_id)})
        return result.deleted_count > 0

    async def get_solution_tags(self, solution_id: str) -> TagList:
        """Get all tags for a specific solution"""
        solution = await self.db.solutions.find_one({"_id": ObjectId(solution_id)})
        if not solution or not solution.get("tags"):
            return TagList(tags=[])

        tag_ids = [ObjectId(tag_id) for tag_id in solution["tags"]]
        cursor = self.collection.find({"_id": {"$in": tag_ids}})
        tags = await cursor.to_list(length=None)
        return TagList(tags=[TagInDB(**tag) for tag in tags])

    async def add_solution_tag(self, solution_id: str, tag_id: str) -> bool:
        """Add a tag to a solution"""
        # Verify tag exists
        tag = await self.get_tag_by_id(tag_id)
        if not tag:
            raise ValueError("Tag not found")

        result = await self.db.solutions.update_one(
            {"_id": ObjectId(solution_id)},
            {"$addToSet": {"tags": ObjectId(tag_id)}}
        )
        return result.modified_count > 0

    async def remove_solution_tag(self, solution_id: str, tag_id: str) -> bool:
        """Remove a tag from a solution"""
        result = await self.db.solutions.update_one(
            {"_id": ObjectId(solution_id)},
            {"$pull": {"tags": ObjectId(tag_id)}}
        )
        return result.modified_count > 0
