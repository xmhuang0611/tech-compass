from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from cachetools import TTLCache, keys

from app.core.database import get_database
from app.models.tag import Tag, TagCreate, TagInDB, TagUpdate, format_tag_name


class TagService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.tags
        # Create a cache with 1-hour TTL
        self.tags_cache = TTLCache(maxsize=100, ttl=3600)

    async def create_tag(self, tag: TagCreate, username: Optional[str] = None) -> TagInDB:
        """Create a new tag"""
        # Name is already formatted by the model validator
        formatted_name = tag.name

        # Check if tag already exists (case-insensitive)
        existing_tag = await self.get_tag_by_name(formatted_name)
        if existing_tag:
            raise ValueError(f"Tag '{formatted_name}' already exists")

        tag_dict = tag.model_dump()
        tag_dict["created_at"] = datetime.utcnow()
        tag_dict["updated_at"] = datetime.utcnow()
        tag_dict["usage_count"] = 0
        if username:
            tag_dict["created_by"] = username
            tag_dict["updated_by"] = username

        result = await self.collection.insert_one(tag_dict)
        # Clear cache since data has been updated
        self.tags_cache.clear()
        return await self.get_tag_by_id(str(result.inserted_id))

    async def get_tag_by_id(self, tag_id: str) -> Optional[TagInDB]:
        """Get a tag by ID"""
        try:
            tag = await self.collection.find_one({"_id": ObjectId(tag_id)})
            if tag:
                return TagInDB(**tag)
            return None
        except Exception:
            return None

    async def get_tag_by_name(self, name: str) -> Optional[TagInDB]:
        """Get a tag by name (case-insensitive) - internal use only"""
        # Format the name for consistency
        formatted_name = format_tag_name(name)
        tag = await self.collection.find_one({"name": formatted_name})
        if tag:
            return TagInDB(**tag)
        return None

    async def get_tag_usage_counts(self, tag_names: List[str] = None) -> dict:
        """Get usage counts for multiple tags in a single query

        Args:
            tag_names: Optional list of tag names to get counts for. If None, gets counts for all tags.

        Returns:
            Dictionary mapping tag names to their usage counts
        """
        pipeline = [
            # Match stage (optional)
            *([{"$match": {"tags": {"$in": tag_names}}}] if tag_names else []),
            # Only count approved solutions
            {"$match": {"review_status": "APPROVED"}},
            # Unwind tags array to count each tag separately
            {"$unwind": "$tags"},
            # Group by tag and count occurrences
            {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        ]

        # Execute aggregation
        results = await self.db.solutions.aggregate(pipeline).to_list(length=None)

        # Convert to dictionary
        return {doc["_id"]: doc["count"] for doc in results}

    async def get_tags(self, skip: int = 0, limit: int = 100, show_all: bool = False) -> List[Tag]:
        """Get all tags with pagination
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            show_all: If True, return all tags; if False, only return tags with usage_count > 0
        """
        # Generate cache key
        cache_key = keys.hashkey(skip, limit, show_all)

        # Try to get data from cache
        if cache_key in self.tags_cache:
            return self.tags_cache[cache_key]

        # Get all tags first
        cursor = self.collection.find().sort("name", 1).skip(skip).limit(limit)
        tags = await cursor.to_list(length=limit)

        if not tags:
            return []

        # Get usage counts for all tags in a single query
        tag_names = [tag["name"] for tag in tags]
        usage_counts = await self.get_tag_usage_counts(tag_names)

        # Convert to Tag models with usage counts
        result = []
        for tag in tags:
            tag_model = TagInDB(**tag)
            usage_count = usage_counts.get(tag_model.name, 0)

            # Only include tags with usage_count > 0 if show_all is False
            if show_all or usage_count > 0:
                tag_dict = tag_model.model_dump()
                tag_dict["usage_count"] = usage_count
                result.append(Tag(**tag_dict))

        # Store result in cache
        self.tags_cache[cache_key] = result
        return result

    async def get_tag_with_usage(self, tag: TagInDB) -> Tag:
        """Convert TagInDB to Tag with usage count"""
        tag_dict = tag.model_dump()
        usage_counts = await self.get_tag_usage_counts([tag.name])
        tag_dict["usage_count"] = usage_counts.get(tag.name, 0)
        return Tag(**tag_dict)

    async def get_tag_usage_count(self, name: str) -> int:
        """Get the number of solutions using this tag"""
        return await self.db.solutions.count_documents({"tags": name, "review_status": "APPROVED"})

    async def merge_tags(
        self, source_tag_id: str, target_tag_name: str, username: Optional[str] = None
    ) -> Optional[TagInDB]:
        """Merge source tag into target tag.

        This will:
        1. Find all solutions using the source tag
        2. Add the target tag to these solutions
        3. Remove the source tag from these solutions
        4. Delete the source tag

        Args:
            source_tag_id: ID of the tag to be merged and deleted
            target_tag_name: Name of the tag to merge into
            username: Username performing the merge operation

        Returns:
            The target tag if successful, None if either tag not found
        """
        try:
            # Get source tag
            source_tag = await self.get_tag_by_id(source_tag_id)
            if not source_tag:
                return None

            # Get target tag
            target_tag = await self.get_tag_by_name(target_tag_name)
            if not target_tag:
                return None

            # Update all solutions that use the source tag
            # First add the target tag to all solutions using source tag
            await self.db.solutions.update_many(
                {"tags": source_tag.name},
                {
                    "$addToSet": {"tags": target_tag.name},
                    "$set": {
                        "updated_at": datetime.utcnow(),
                        "updated_by": username if username else "system",
                    },
                },
            )

            # Then remove the source tag
            await self.db.solutions.update_many({"tags": source_tag.name}, {"$pull": {"tags": source_tag.name}})

            # Delete the source tag
            await self.collection.delete_one({"_id": ObjectId(source_tag_id)})

            # Clear cache since data has been updated
            self.tags_cache.clear()

            # Return the target tag
            return target_tag
        except Exception as e:
            raise ValueError(f"Error merging tags: {str(e)}")

    async def update_tag(
        self,
        tag_id: str,
        tag_update: TagUpdate,
        username: Optional[str] = None,
        update_solutions: bool = False,
    ) -> Optional[TagInDB]:
        """Update a tag by ID. Optionally update all solutions using this tag."""
        try:
            # Get the tag first
            tag = await self.get_tag_by_id(tag_id)
            if not tag:
                return None

            update_dict = tag_update.model_dump(exclude_unset=True)

            # If name is changing
            if "name" in update_dict and update_dict["name"] != tag.name:
                # Check if target name already exists
                existing_tag = await self.get_tag_by_name(update_dict["name"])
                if existing_tag:
                    # If target tag exists, merge this tag into it
                    return await self.merge_tags(tag_id, existing_tag.name, username)
                elif update_solutions:
                    # If target tag doesn't exist and we need to update solutions
                    await self.db.solutions.update_many(
                        {"tags": tag.name},
                        {
                            "$set": {
                                "tags.$": update_dict["name"],
                                "updated_at": datetime.utcnow(),
                                "updated_by": username if username else "system",
                            }
                        },
                    )

            # Update the tag itself
            update_dict["updated_at"] = datetime.utcnow()
            if username:
                update_dict["updated_by"] = username

            result = await self.collection.update_one({"_id": ObjectId(tag_id)}, {"$set": update_dict})
            # Clear cache since data has been updated
            self.tags_cache.clear()
            if result.modified_count:
                return await self.get_tag_by_id(tag_id)
            return None
        except Exception as e:
            raise ValueError(f"Error updating tag: {str(e)}")

    async def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag by ID and remove it from all solutions using it."""
        try:
            # Validate tag_id format
            try:
                object_id = ObjectId(tag_id)
            except Exception:
                raise ValueError(f"Invalid tag ID format: {tag_id}")

            # Get tag first
            tag = await self.get_tag_by_id(tag_id)
            if not tag:
                return False

            # Remove tag from all solutions that use it
            await self.db.solutions.update_many(
                {"tags": tag.name},
                {
                    "$pull": {"tags": tag.name},
                    "$set": {"updated_at": datetime.utcnow(), "updated_by": "system"},
                },
            )

            # Delete the tag
            result = await self.collection.delete_one({"_id": object_id})
            # Clear cache since data has been updated
            self.tags_cache.clear()
            return result.deleted_count > 0
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Error deleting tag: {str(e)}")

    async def get_solution_by_slug(self, slug: str) -> Optional[dict]:
        """Get a solution by its slug"""
        return await self.db.solutions.find_one({"slug": slug})

    async def get_solution_tags(self, solution_slug: str) -> List[Tag]:
        """Get all tags for a specific solution using slug"""
        solution = await self.get_solution_by_slug(solution_slug)
        if not solution or not solution.get("tags"):
            return []

        # Get all tags in a single query
        tags = await self.collection.find({"name": {"$in": solution["tags"]}}).to_list(length=None)
        if not tags:
            return []

        # Get usage counts for these tags in a single query
        tag_names = [tag["name"] for tag in tags]
        usage_counts = await self.get_tag_usage_counts(tag_names)

        # Convert to Tag models with usage counts
        result = []
        for tag in tags:
            tag_model = TagInDB(**tag)
            tag_dict = tag_model.model_dump()
            tag_dict["usage_count"] = usage_counts.get(tag_model.name, 0)
            result.append(Tag(**tag_dict))

        return result

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

        result = await self.db.solutions.update_one({"slug": solution_slug}, {"$addToSet": {"tags": formatted_name}})
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

        result = await self.db.solutions.update_one({"slug": solution_slug}, {"$pull": {"tags": formatted_name}})
        return result.modified_count > 0

    async def count_tags(self, show_all: bool = False) -> int:
        """Get total number of tags
        Args:
            show_all: If True, count all tags; if False, only count tags with usage_count > 0
        """
        if show_all:
            return await self.collection.count_documents({})

        # Get all tag names
        cursor = self.collection.find({}, {"name": 1})
        tag_names = [doc["name"] async for doc in cursor]

        if not tag_names:
            return 0

        # Get usage counts in a single query
        usage_counts = await self.get_tag_usage_counts(tag_names)

        # Count tags with usage > 0
        return len([count for count in usage_counts.values() if count > 0])
