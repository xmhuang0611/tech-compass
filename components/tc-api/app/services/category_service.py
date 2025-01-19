from datetime import datetime
from typing import List, Optional
from bson import ObjectId

from app.models.category import CategoryCreate, CategoryUpdate, CategoryInDB
from app.core.database import get_database

class CategoryService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.categories

    async def create_category(self, category: CategoryCreate, user_id: Optional[str] = None) -> CategoryInDB:
        """Create a new category"""
        category_dict = category.dict()
        category_dict["created_at"] = datetime.utcnow()
        category_dict["updated_at"] = datetime.utcnow()
        if user_id:
            category_dict["created_by"] = ObjectId(user_id)
            category_dict["updated_by"] = ObjectId(user_id)

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

    async def update_category(self, category_id: str, category_update: CategoryUpdate, user_id: Optional[str] = None) -> Optional[CategoryInDB]:
        """Update a category"""
        category_dict = category_update.dict(exclude_unset=True)
        category_dict["updated_at"] = datetime.utcnow()
        if user_id:
            category_dict["updated_by"] = ObjectId(user_id)

        result = await self.collection.update_one(
            {"_id": ObjectId(category_id)},
            {"$set": category_dict}
        )
        if result.modified_count:
            return await self.get_category_by_id(category_id)
        return None

    async def delete_category(self, category_id: str) -> bool:
        """Delete a category"""
        result = await self.collection.delete_one({"_id": ObjectId(category_id)})
        return result.deleted_count > 0

    async def get_or_create_category(self, name: str, user_id: Optional[str] = None) -> CategoryInDB:
        """Get a category by name or create it if it doesn't exist"""
        category = await self.get_category_by_name(name)
        if category:
            return category
            
        # Create new category if it doesn't exist
        new_category = CategoryCreate(
            name=name,
            description=f"Auto-generated category for {name}"
        )
        return await self.create_category(new_category, user_id)
