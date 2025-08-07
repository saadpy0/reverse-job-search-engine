"""
Main FastAPI application for the AI-Driven Reverse Job Search Engine.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config.settings import settings
from app.core.database import init_db
from app.core.logging import get_logger

# Initialize logger
logger = get_logger("main")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="An intelligent job search platform that analyzes resumes and suggests hidden job opportunities",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting AI-Driven Reverse Job Search Engine...")
    
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")
        
        # Initialize other components here (ML models, etc.)
        logger.info("Application startup completed")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down AI-Driven Reverse Job Search Engine...")


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "Welcome to AI-Driven Reverse Job Search Engine",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "database": "connected"  # Add actual database health check
    }


@app.get("/api/v1/health")
async def api_health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "service": "reverse-job-search-api",
        "version": settings.app_version
    }


# Include API routers here (will be added in future phases)
# from app.api.routers import users, resumes, jobs, matching
# app.include_router(users.router, prefix=settings.api_prefix)
# app.include_router(resumes.router, prefix=settings.api_prefix)
# app.include_router(jobs.router, prefix=settings.api_prefix)
# app.include_router(matching.router, prefix=settings.api_prefix)


if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
