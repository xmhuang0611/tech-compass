from datetime import datetime
from typing import List, Optional
from bson import ObjectId

from app.models.category import CategoryCreate, CategoryUpdate, CategoryInDB
from app.core.database import get_database

class CategoryService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.categories

    async def create_category(self, category: CategoryCreate, username: Optional[str] = None) -> CategoryInDB:
        """Create a new category"""
        # Check if category already exists
        existing = await self.get_category_by_name(category.name)
        if existing:
            raise ValueError("Category already exists")

        category_dict = category.dict()
        category_dict["created_at"] = datetime.utcnow()
        category_dict["updated_at"] = datetime.utcnow()
        if username:
            category_dict["created_by"] = username
            category_dict["updated_by"] = username

        result = await self.collection.insert_one(category_dict)
        return await self.get_category_by_id(str(result.inserted_id))

    async def get_category_by_id(self, category_id: str) -> Optional[CategoryInDB]:
        """Get a category by ID"""
        category = await self.collection.find_one({"_id": ObjectId(category_id)})
        if category:
            return CategoryInDB(**category)
        return None

    async def get_category_by_name(self, name: str) -> Optional[CategoryInDB]:
        """Get a category by name"""
        category = await self.collection.find_one({"name": name})
        if category:
            return CategoryInDB(**category)
        return None

    async def get_categories(self, skip: int = 0, limit: int = 100) -> List[CategoryInDB]:
        """Get all categories with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit)
        categories = await cursor.to_list(length=limit)
        return [CategoryInDB(**category) for category in categories]

    async def count_categories(self) -> int:
        """Get total number of categories"""
        return await self.collection.count_documents({})

    async def update_category(
        self,
        category_id: str,
        category_update: CategoryUpdate,
        username: Optional[str] = None
    ) -> Optional[CategoryInDB]:
        """Update a category"""
        update_dict = category_update.dict(exclude_unset=True)
        
        # Check name uniqueness if being updated
        if "name" in update_dict:
            existing = await self.get_category_by_name(update_dict["name"])
            if existing and str(existing.id) != category_id:
                raise ValueError("Category name is already in use")

        update_dict["updated_at"] = datetime.utcnow()
        if username:
            update_dict["updated_by"] = username

        result = await self.collection.update_one(
            {"_id": ObjectId(category_id)},
            {"$set": update_dict}
        )
        if result.modified_count:
            return await self.get_category_by_id(category_id)
        return None

    async def delete_category(self, category_id: str) -> bool:
        """Delete a category"""
        result = await self.collection.delete_one({"_id": ObjectId(category_id)})
        return result.deleted_count > 0

    async def get_or_create_category(self, name: str, username: Optional[str] = None) -> CategoryInDB:
        """Get a category by name or create it if it doesn't exist"""
        existing = await self.get_category_by_name(name)
        if existing:
            return existing
        
        # Create new category with minimal info
        category = CategoryCreate(
            name=name,
            description=f"Category for {name}"
        )
        return await self.create_category(category, username)
