from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_active_user
from app.models.site_config import SiteConfigBase, SiteConfigUpdate
from app.models.user import User
from app.services.site_config_service import SiteConfigService

router = APIRouter()


@router.get("", response_model=dict, tags=["site-config"])
async def get_site_config():
    """
    Get the current site configuration.
    This endpoint is public and does not require authentication.
    """
    config_service = SiteConfigService()
    config = await config_service.get_site_config()

    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site configuration not found")

    return {"status": "success", "data": config}


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED, tags=["site-config"])
async def create_site_config(config: SiteConfigBase, current_user: User = Depends(get_current_active_user)):
    """
    Create initial site configuration.
    Requires authentication. Can only be called once when no configuration exists.
    """
    config_service = SiteConfigService()
    try:
        new_config = await config_service.create_site_config(config=config, username=current_user.username)
        return {"status": "success", "data": new_config}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating site configuration: {str(e)}",
        )


@router.put("", response_model=dict, tags=["site-config"])
async def update_site_config(
    config_update: SiteConfigUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Update site configuration.
    Requires authentication. Only updates the fields that are provided.
    """
    config_service = SiteConfigService()
    updated_config = await config_service.update_site_config(
        config_update=config_update, username=current_user.username
    )

    if not updated_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site configuration not found")

    return {"status": "success", "data": updated_config}


@router.post("/reset", response_model=dict, tags=["site-config"])
async def reset_site_config(current_user: User = Depends(get_current_active_user)):
    """
    Reset site configuration to default values.
    Requires authentication. This will delete the existing configuration and create a new one with defaults.
    """
    config_service = SiteConfigService()
    try:
        new_config = await config_service.reset_site_config(username=current_user.username)
        return {"status": "success", "data": new_config}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting site configuration: {str(e)}",
        )
