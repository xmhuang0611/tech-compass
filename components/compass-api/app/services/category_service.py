from datetime import datetime
from typing import Optional

from bson import ObjectId

from app.core.database import get_database
from app.models.category import CategoryCreate, CategoryUpdate, CategoryInDB


class CategoryService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.categories

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
        category = CategoryCreate(
            name=name,
            description=f"Category for {name}"
        )
        return await self.create_category(category, username)

    async def get_categories(self, skip: int = 0, limit: int = 100) -> list[CategoryInDB]:
        """Get all categories with pagination"""
        cursor = self.collection.find().sort("name", 1).skip(skip).limit(limit)
        categories = await cursor.to_list(length=limit)
        return [CategoryInDB(**category) for category in categories]

    async def update_category_by_name(
        self,
        name: str,
        category_update: CategoryUpdate,
        username: Optional[str] = None
    ) -> Optional[CategoryInDB]:
        """Update a category by name"""
        # Name is already trimmed by the model validator
        
        # Get existing category
        existing_category = await self.get_category_by_name(name)
        if not existing_category:
            return None

        update_dict = category_update.model_dump(exclude_unset=True)
        
        # Check name uniqueness if being updated
        if "name" in update_dict and update_dict["name"] != name:
            other_category = await self.get_category_by_name(update_dict["name"])
            if other_category:
                raise ValueError(f"Category '{update_dict['name']}' is already in use")

            # Update all solutions using this category
            await self.db.solutions.update_many(
                {"category_id": existing_category.id},
                {"$set": {
                    "category": update_dict["name"],
                    "updated_at": datetime.utcnow(),
                    "updated_by": username if username else None
                }}
            )

        update_dict["updated_at"] = datetime.utcnow()
        if username:
            update_dict["updated_by"] = username

        result = await self.collection.update_one(
            {"name": name},
            {"$set": update_dict}
        )
        if result.modified_count:
            return await self.get_category_by_name(update_dict.get("name", name))
        return existing_category

    async def delete_category_by_name(self, name: str) -> bool:
        """Delete a category by name"""
        # Name is already trimmed by the model validator
        
        # Get category first
        category = await self.get_category_by_name(name)
        if not category:
            return False

        # Check if category is being used by any solutions
        solutions_using_category = await self.db.solutions.find_one({"category": name})
        if solutions_using_category:
            raise ValueError(f"Cannot delete category '{name}' as it is being used by solutions")

        result = await self.collection.delete_one({"name": name})
        return result.deleted_count > 0

    async def count_categories(self) -> int:
        """Get total number of categories"""
        return await self.collection.count_documents({})
