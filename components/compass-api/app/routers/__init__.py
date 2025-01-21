from fastapi import APIRouter

from app.routers import auth, solutions, tags, users, categories, ratings, comments, site_config
from app.routers.auth import router as auth_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(solutions.router, prefix="/solutions", tags=["solutions"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(ratings.router, prefix="/ratings", tags=["ratings"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(site_config.router, prefix="/site-config", tags=["site-config"]) 