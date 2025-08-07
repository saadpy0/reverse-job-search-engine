#!/usr/bin/env python3
"""
Database setup script for the AI-Driven Reverse Job Search Engine.
Initializes the database and creates all necessary tables.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import init_db, drop_db
from app.core.logging import get_logger
from config.settings import settings

logger = get_logger("database_setup")


def setup_database():
    """Initialize the database and create all tables."""
    try:
        logger.info("Starting database setup...")
        
        # Initialize database
        init_db()
        
        logger.info("Database setup completed successfully!")
        logger.info(f"Database URL: {settings.database_url}")
        
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False


def reset_database():
    """Drop all tables and recreate them (DANGEROUS - deletes all data)."""
    try:
        logger.warning("Dropping all database tables...")
        
        # Drop all tables
        drop_db()
        
        logger.info("All tables dropped successfully!")
        
        # Recreate tables
        init_db()
        
        logger.info("Database reset completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database setup for Reverse Job Search Engine")
    parser.add_argument(
        "--reset", 
        action="store_true", 
        help="Drop all tables and recreate them (DANGEROUS - deletes all data)"
    )
    
    args = parser.parse_args()
    
    if args.reset:
        # Ask for confirmation
        response = input("Are you sure you want to reset the database? This will delete ALL data! (yes/no): ")
        if response.lower() == "yes":
            success = reset_database()
        else:
            logger.info("Database reset cancelled.")
            success = True
    else:
        success = setup_database()
    
    sys.exit(0 if success else 1)
