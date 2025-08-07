#!/usr/bin/env python3
"""
Startup script for the AI-Driven Reverse Job Search Engine.
"""

import uvicorn
from config.settings import settings
from app.core.logging import get_logger

logger = get_logger("startup")


def main():
    """Start the FastAPI application."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Server will run on http://{settings.api_host}:{settings.api_port}")
    logger.info(f"API documentation available at http://{settings.api_host}:{settings.api_port}/docs")
    
    uvicorn.run(
        "app.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()
