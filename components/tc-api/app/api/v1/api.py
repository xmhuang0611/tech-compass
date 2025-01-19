from fastapi import APIRouter
from app.api.v1.endpoints import auth, solutions, tags, users, categories

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(solutions.router, prefix="/solutions", tags=["solutions"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
