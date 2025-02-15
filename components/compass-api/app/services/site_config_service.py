from datetime import datetime
from typing import Optional

from bson import ObjectId

from app.core.database import get_database
from app.models.site_config import SiteConfigBase, SiteConfigInDB, SiteConfigUpdate


class SiteConfigService:
    def __init__(self):
        self.db = get_database()

    async def get_site_config(self) -> Optional[SiteConfigInDB]:
        """Get the current site configuration"""
        config = await self.db.site_config.find_one({})
        if config:
            return SiteConfigInDB(**config)
        return None

    async def create_site_config(self, config: SiteConfigBase, username: str) -> SiteConfigInDB:
        """Create initial site configuration"""
        # Check if config already exists
        existing = await self.get_site_config()
        if existing:
            raise ValueError("Site configuration already exists. Use update instead.")

        now = datetime.utcnow()
        config_dict = config.model_dump()
        new_config = {
            "id": str(ObjectId()),
            **config_dict,
            "created_at": now,
            "updated_at": now,
            "updated_by": username,
        }

        await self.db.site_config.insert_one(new_config)
        return SiteConfigInDB(**new_config)

    async def update_site_config(self, config_update: SiteConfigUpdate, username: str) -> Optional[SiteConfigInDB]:
        """Update site configuration"""
        now = datetime.utcnow()
        update_dict = config_update.model_dump(exclude_unset=True)

        if not update_dict:
            return await self.get_site_config()

        update_dict["updated_at"] = now
        update_dict["updated_by"] = username

        result = await self.db.site_config.find_one_and_update(
            {},  # Update the first (and only) config document
            {"$set": update_dict},
            return_document=True,
        )

        if result:
            return SiteConfigInDB(**result)
        return None

    async def reset_site_config(self, username: str) -> SiteConfigInDB:
        """Reset site configuration to defaults"""
        # Delete existing config
        await self.db.site_config.delete_many({})

        # Create default config
        default_config = SiteConfigBase(
            site_name="Tech Compass",
            site_description="Navigate your technology landscape",
            welcome_message="Welcome to Tech Compass",
            contact_email="support@techcompass.com",
            features={
                "ratings_enabled": True,
                "comments_enabled": True,
                "tags_enabled": True,
            },
        )

        return await self.create_site_config(default_config, username)
