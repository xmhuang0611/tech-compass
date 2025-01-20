from datetime import datetime
from typing import List, Optional
from bson import ObjectId

from app.models.tag import TagCreate, TagUpdate, TagInDB, TagList, format_tag_name
from app.core.database import get_database

class TagService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.tags

    async def create_tag(self, tag: TagCreate, username: Optional[str] = None) -> TagInDB:
        """Create a new tag"""
        # Name is already formatted by the model validator
        formatted_name = tag.name

        # Check if tag already exists (case-insensitive)
        existing_tag = await self.get_tag_by_name(formatted_name)
        if existing_tag:
            raise ValueError(f"Tag '{formatted_name}' already exists")

        tag_dict = tag.dict()
        tag_dict["created_at"] = datetime.utcnow()
        tag_dict["updated_at"] = datetime.utcnow()
        tag_dict["usage_count"] = 0
        if username:
            tag_dict["created_by"] = username
            tag_dict["updated_by"] = username

        result = await self.collection.insert_one(tag_dict)
        return await self.get_tag_by_id(str(result.inserted_id))

    async def get_tag_by_id(self, tag_id: str) -> Optional[TagInDB]:
        """Get a tag by ID - internal use only"""
        tag = await self.collection.find_one({"_id": ObjectId(tag_id)})
        if tag:
            return TagInDB(**tag)
        return None

    async def get_tag_by_name(self, name: str) -> Optional[TagInDB]:
        """Get a tag by name (case-insensitive)"""
        # Format the name for consistency
        formatted_name = format_tag_name(name)
        tag = await self.collection.find_one({"name": formatted_name})
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
                "$sort": {"name": 1}  # Sort tags alphabetically
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

    async def update_tag_by_name(
        self,
        name: str,
        tag_update: TagUpdate,
        username: Optional[str] = None,
        update_solutions: bool = False
    ) -> Optional[TagInDB]:
        """Update a tag by name. Optionally update all solutions using this tag."""
        # Get the tag first
        tag = await self.get_tag_by_name(name)
        if not tag:
            return None

        update_dict = tag_update.model_dump(exclude_unset=True)
        
        # If name is changing and we need to update solutions
        if update_solutions and "name" in update_dict and update_dict["name"] != name:
            # Update all solutions that use this tag
            await self.db.solutions.update_many(
                {"tags": name},
                {"$set": {
                    "tags.$": update_dict["name"],
                    "updated_at": datetime.utcnow()
                }}
            )
            if username:
                await self.db.solutions.update_many(
                    {"tags": name},
                    {"$set": {"updated_by": username}}
                )

        # Update the tag itself
        update_dict["updated_at"] = datetime.utcnow()
        if username:
            update_dict["updated_by"] = username

        result = await self.collection.update_one(
            {"name": name},
            {"$set": update_dict}
        )
        if result.modified_count:
            return await self.get_tag_by_name(update_dict.get("name", name))
        return None

    async def delete_tag_by_name(self, name: str) -> bool:
        """Delete a tag by name"""
        # Format the name
        formatted_name = format_tag_name(name)
        
        # Get tag first
        tag = await self.get_tag_by_name(formatted_name)
        if not tag:
            return False

        # Check if tag is being used by any solutions
        solutions_using_tag = await self.db.solutions.find_one({"tags": tag.id})
        if solutions_using_tag:
            raise ValueError("Cannot delete tag as it is being used by solutions")

        result = await self.collection.delete_one({"name": formatted_name})
        return result.deleted_count > 0

    async def get_solution_by_slug(self, slug: str) -> Optional[dict]:
        """Get a solution by its slug"""
        return await self.db.solutions.find_one({"slug": slug})

    async def get_solution_tags(self, solution_slug: str) -> TagList:
        """Get all tags for a specific solution using slug"""
        solution = await self.get_solution_by_slug(solution_slug)
        if not solution or not solution.get("tags"):
            return TagList(tags=[])

        tag_ids = [ObjectId(tag_id) for tag_id in solution["tags"]]
        cursor = self.collection.find({"_id": {"$in": tag_ids}})
        tags = await cursor.to_list(length=None)
        return TagList(tags=[TagInDB(**tag) for tag in tags])

    async def add_solution_tag_by_name(self, solution_slug: str, name: str) -> bool:
        """Add a tag to a solution by solution slug and tag name"""
        # Format the name
        formatted_name = format_tag_name(name)
        
        # Get solution by slug
        solution = await self.get_solution_by_slug(solution_slug)
        if not solution:
            return False
        
        # Get tag by name
        tag = await self.get_tag_by_name(formatted_name)
        if not tag:
            return False

        result = await self.db.solutions.update_one(
            {"slug": solution_slug},
            {"$addToSet": {"tags": tag.id}}
        )
        return result.modified_count > 0

    async def remove_solution_tag_by_name(self, solution_slug: str, name: str) -> bool:
        """Remove a tag from a solution by solution slug and tag name"""
        # Format the name
        formatted_name = format_tag_name(name)
        
        # Get solution by slug
        solution = await self.get_solution_by_slug(solution_slug)
        if not solution:
            return False
        
        # Get tag by name
        tag = await self.get_tag_by_name(formatted_name)
        if not tag:
            return False

        result = await self.db.solutions.update_one(
            {"slug": solution_slug},
            {"$pull": {"tags": tag.id}}
        )
        return result.modified_count > 0

    async def count_tags(self) -> int:
        """Get total number of tags"""
        return await self.collection.count_documents({})
