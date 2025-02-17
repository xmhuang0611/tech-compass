from datetime import datetime
from typing import Optional

from bson import ObjectId
from cachetools import TTLCache, keys

from app.core.database import get_database
from app.models.category import Category, CategoryCreate, CategoryInDB, CategoryUpdate


class CategoryService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.categories
        # Create a cache with 1-hour TTL
        self.categories_cache = TTLCache(maxsize=1, ttl=3600)

    async def create_category(self, category: CategoryCreate, username: Optional[str] = None) -> CategoryInDB:
        """Create a new category"""
        # Name is already trimmed by the model validator
        name = category.name

        # Check if category already exists (exact match)
        existing_category = await self.get_category_by_name(name)
        if existing_category:
            raise ValueError(f"Category '{name}' already exists")

        category_dict = category.model_dump()
        category_dict["created_at"] = datetime.utcnow()
        category_dict["updated_at"] = datetime.utcnow()
        if username:
            category_dict["created_by"] = username
            category_dict["updated_by"] = username

        result = await self.collection.insert_one(category_dict)
        # Clear cache since data has been updated
        self.categories_cache.clear()
        return await self.get_category_by_id(str(result.inserted_id))

    async def get_category_by_id(self, category_id: str) -> Optional[CategoryInDB]:
        """Get a category by ID - internal use only"""
        category = await self.collection.find_one({"_id": ObjectId(category_id)})
        if category:
            return CategoryInDB(**category)
        return None

    async def get_category_by_name(self, name: str) -> Optional[CategoryInDB]:
        """Get a category by name (exact match)"""
        # Name is already trimmed by the model validator
        category = await self.collection.find_one({"name": name})
        if category:
            return CategoryInDB(**category)
        return None

    async def get_or_create_category(self, name: str, username: Optional[str] = None) -> CategoryInDB:
        """Get a category by name or create it if it doesn't exist"""
        # Try to get existing category
        existing = await self.get_category_by_name(name)
        if existing:
            return existing

        # Create new category with minimal info
        category = CategoryCreate(name=name, description=f"Category for {name}")
        return await self.create_category(category, username)

    async def get_categories(self, skip: int = 0, limit: int = 100, sort: str = "radar_quadrant") -> list[CategoryInDB]:
        """Get all categories with pagination and sorting

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            sort: Sort field (prefix with - for descending order)
        """
        # Generate cache key
        cache_key = keys.hashkey(skip, limit, sort)

        # Try to get data from cache
        if cache_key in self.categories_cache:
            return self.categories_cache[cache_key]

        # Parse sort parameter
        sort_field = sort.lstrip("-")
        sort_direction = -1 if sort.startswith("-") else 1

        # Build sort query
        sort_query = [(sort_field, sort_direction)]

        # Add name as secondary sort if not already sorting by name
        if sort_field != "name":
            sort_query.append(("name", 1))

        cursor = self.collection.find().sort(sort_query).skip(skip).limit(limit)
        categories = await cursor.to_list(length=limit)
        result = [CategoryInDB(**category) for category in categories]

        # Store result in cache
        self.categories_cache[cache_key] = result
        return result

    async def update_category_by_id(
        self,
        category_id: str,
        category_update: CategoryUpdate,
        username: Optional[str] = None,
    ) -> Optional[CategoryInDB]:
        """Update a category by ID"""
        # Get existing category
        existing_category = await self.get_category_by_id(category_id)
        if not existing_category:
            return None

        update_dict = category_update.model_dump(exclude_unset=True)

        # Check name uniqueness if being updated
        if "name" in update_dict and update_dict["name"] != existing_category.name:
            other_category = await self.get_category_by_name(update_dict["name"])
            if other_category:
                raise ValueError(f"Category '{update_dict['name']}' is already in use")

            # Update all solutions using this category
            await self.db.solutions.update_many(
                {"category": existing_category.name},
                {
                    "$set": {
                        "category": update_dict["name"],
                        "updated_at": datetime.utcnow(),
                        "updated_by": username if username else None,
                    }
                },
            )

        update_dict["updated_at"] = datetime.utcnow()
        if username:
            update_dict["updated_by"] = username

        result = await self.collection.update_one({"_id": ObjectId(category_id)}, {"$set": update_dict})
        # Clear cache since data has been updated
        self.categories_cache.clear()
        if result.modified_count:
            return await self.get_category_by_id(category_id)
        return existing_category

    async def delete_category_by_id(self, category_id: str) -> bool:
        """Delete a category by ID"""
        # Get category first
        category = await self.get_category_by_id(category_id)
        if not category:
            return False

        # Check if category is being used by any solutions
        solutions_using_category = await self.db.solutions.find_one({"category": category.name})
        if solutions_using_category:
            raise ValueError(f"Cannot delete category '{category.name}' as it is being used by solutions")

        result = await self.collection.delete_one({"_id": ObjectId(category_id)})
        # Clear cache since data has been updated
        self.categories_cache.clear()
        return result.deleted_count > 0

    async def count_categories(self) -> int:
        """Get total number of categories"""
        return await self.collection.count_documents({})

    async def get_category_usage_count(self, name: str) -> int:
        """Get the number of approved solutions using this category"""
        return await self.db.solutions.count_documents({"category": name})

    async def get_category_with_usage(self, category: CategoryInDB) -> Category:
        """Convert CategoryInDB to Category with usage count"""
        category_dict = category.model_dump()
        usage_count = await self.get_category_usage_count(category.name)
        return Category(**category_dict, usage_count=usage_count)
