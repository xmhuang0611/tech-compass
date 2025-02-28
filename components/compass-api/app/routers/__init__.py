from fastapi import APIRouter

from app.routers import (
    auth,
    categories,
    comments,
    history,
    ratings,
    site_config,
    solutions,
    tags,
    tech_radar,
    users,
)

api_router = APIRouter()


api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(solutions.router, prefix="/solutions", tags=["solutions"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(ratings.router, prefix="/ratings", tags=["ratings"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(site_config.router, prefix="/site-config", tags=["site-config"])
api_router.include_router(tech_radar.router, prefix="/tech-radar", tags=["tech-radar"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
