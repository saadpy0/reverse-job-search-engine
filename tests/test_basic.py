"""
Basic tests for the AI-Driven Reverse Job Search Engine.
"""

import pytest
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from app.core.database import get_db, init_db
from app.core.logging import get_logger


def test_settings_loaded():
    """Test that settings are loaded correctly."""
    assert settings.app_name == "AI-Driven Reverse Job Search Engine"
    assert settings.app_version == "1.0.0"
    assert isinstance(settings.debug, bool)


def test_logging_configured():
    """Test that logging is configured."""
    logger = get_logger("test")
    assert logger is not None


def test_database_connection():
    """Test database connection and initialization."""
    try:
        init_db()
        assert True  # If we get here, database initialization succeeded
    except Exception as e:
        pytest.fail(f"Database initialization failed: {e}")


def test_file_structure():
    """Test that required directories exist."""
    required_dirs = [
        "app",
        "app/api",
        "app/core", 
        "app/models",
        "app/services",
        "app/utils",
        "data",
        "data/raw",
        "data/processed",
        "data/models",
        "config",
        "tests"
    ]
    
    for dir_path in required_dirs:
        assert Path(dir_path).exists(), f"Required directory {dir_path} does not exist"


def test_imports():
    """Test that all modules can be imported."""
    try:
        from app.models import User, Resume, Job, JobMatch
        from app.core.database import Base
        from app.core.logging import setup_logging
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
