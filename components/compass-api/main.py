import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.core.mongodb import connect_to_mongo, close_mongo_connection
from app.routers import api_router
from app.services.user_service import UserService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    
    # Ensure default admin exists
    user_service = UserService()
    try:
        await user_service.ensure_default_admin()
        logger.info("Default admin user check completed")
    except Exception as e:
        logger.error(f"Error ensuring default admin user: {e}")
    
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Tech Compass API",
    description="API for Tech Compass",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def root():
    """Redirect root path to API documentation"""
    return RedirectResponse(url="/docs")

# Include routers
app.include_router(api_router, prefix="/api")

def run_debug_server():
    """Run the debug server with hot reload"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="debug"
    )

if __name__ == "__main__":
    run_debug_server()
