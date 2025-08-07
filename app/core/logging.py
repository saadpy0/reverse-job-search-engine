"""
Logging configuration for the AI-Driven Reverse Job Search Engine.
Uses loguru for advanced logging features and better formatting.
"""

import sys
import os
from pathlib import Path
from loguru import logger
from config.settings import settings


def setup_logging():
    """Configure logging for the application."""
    
    # Remove default logger
    logger.remove()
    
    # Create logs directory if it doesn't exist
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Console logging
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # File logging
    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # Error logging to separate file
    error_log_file = str(Path(settings.log_file).parent / "errors.log")
    logger.add(
        error_log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="10 MB",
        retention="90 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # AI/ML specific logging
    ml_log_file = str(Path(settings.log_file).parent / "ml.log")
    logger.add(
        ml_log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        filter=lambda record: "ml" in record["name"].lower() or "model" in record["name"].lower(),
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    logger.info("Logging configured successfully")
    return logger


def get_logger(name: str = None):
    """Get a logger instance with the specified name."""
    if name:
        return logger.bind(name=name)
    return logger


# Initialize logging on module import
setup_logging()
