from fastapi import FastAPI
import logging
import uvicorn
from app.core.mongodb import connect_to_mongo, close_mongo_connection
from app.routers import api_router
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import RedirectResponse

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
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Tech Solutions API",
    description="API for managing technical solutions and documentation",
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
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="debug"
    )

if __name__ == "__main__":
    run_debug_server()
