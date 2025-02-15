from typing import List, Optional

from pydantic import BaseModel, Field

from app.models import AuditModel


class SiteConfigBase(BaseModel):
    """Base model for site configuration"""

    site_name: str = Field(..., description="Name of the site")
    site_description: str = Field(..., description="Description of the site")
    welcome_message: str = Field(..., description="Welcome message shown on homepage")
    contact_email: str = Field(..., description="Contact email for support")
    features: dict = Field(
        default_factory=dict,
        description="Feature flags for enabling/disabling functionality",
    )
    custom_links: List[dict] = Field(default_factory=list, description="Custom navigation links")
    theme: dict = Field(
        default_factory=lambda: {
            "primary_color": "#1890ff",
            "secondary_color": "#52c41a",
            "layout": "default",
        },
        description="Theme configuration including colors and layout",
    )
    meta: dict = Field(
        default_factory=lambda: {"keywords": [], "author": "", "favicon": ""},
        description="Meta information for SEO",
    )


class SiteConfigUpdate(SiteConfigBase):
    """Model for updating site configuration"""

    site_name: Optional[str] = None
    site_description: Optional[str] = None
    welcome_message: Optional[str] = None
    contact_email: Optional[str] = None
    features: Optional[dict] = None
    custom_links: Optional[List[dict]] = None
    theme: Optional[dict] = None
    meta: Optional[dict] = None


class SiteConfigInDB(SiteConfigBase, AuditModel):
    """Model for site configuration in database"""

    pass
