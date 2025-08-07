"""
File utility functions for handling resume uploads and processing.
"""

import os
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

from config.settings import settings
from app.core.logging import get_logger

logger = get_logger("file_utils")


def validate_file_type(filename: str) -> bool:
    """
    Validate if the file type is allowed.
    
    Args:
        filename: Name of the file to validate
        
    Returns:
        True if file type is allowed, False otherwise
    """
    file_ext = Path(filename).suffix.lower()
    return file_ext in settings.allowed_file_types


def validate_file_size(file_size: int) -> bool:
    """
    Validate if the file size is within limits.
    
    Args:
        file_size: Size of the file in bytes
        
    Returns:
        True if file size is acceptable, False otherwise
    """
    return file_size <= settings.max_file_size


def generate_unique_filename(original_filename: str, user_id: int) -> str:
    """
    Generate a unique filename for uploaded files.
    
    Args:
        original_filename: Original filename
        user_id: ID of the user uploading the file
        
    Returns:
        Unique filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = Path(original_filename).suffix.lower()
    unique_id = hashlib.md5(f"{user_id}_{timestamp}_{original_filename}".encode()).hexdigest()[:8]
    
    return f"user_{user_id}_{timestamp}_{unique_id}{file_ext}"


def get_file_path(filename: str, user_id: int) -> Path:
    """
    Get the full file path for a given filename and user.
    
    Args:
        filename: Filename
        user_id: ID of the user
        
    Returns:
        Full file path
    """
    upload_dir = Path(settings.upload_dir)
    user_dir = upload_dir / f"user_{user_id}"
    user_dir.mkdir(parents=True, exist_ok=True)
    
    return user_dir / filename


def save_uploaded_file(file_content: bytes, filename: str, user_id: int) -> Tuple[Path, int]:
    """
    Save an uploaded file to the filesystem.
    
    Args:
        file_content: File content as bytes
        filename: Filename to save as
        user_id: ID of the user uploading the file
        
    Returns:
        Tuple of (file_path, file_size)
    """
    file_path = get_file_path(filename, user_id)
    
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        file_size = len(file_content)
        logger.info(f"File saved successfully: {file_path} ({file_size} bytes)")
        
        return file_path, file_size
        
    except Exception as e:
        logger.error(f"Failed to save file {filename}: {e}")
        raise


def delete_file(file_path: Path) -> bool:
    """
    Delete a file from the filesystem.
    
    Args:
        file_path: Path to the file to delete
        
    Returns:
        True if file was deleted successfully, False otherwise
    """
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"File deleted successfully: {file_path}")
            return True
        else:
            logger.warning(f"File not found: {file_path}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to delete file {file_path}: {e}")
        return False


def get_file_info(file_path: Path) -> dict:
    """
    Get information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary containing file information
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    stat = file_path.stat()
    
    return {
        "filename": file_path.name,
        "size": stat.st_size,
        "created": datetime.fromtimestamp(stat.st_ctime),
        "modified": datetime.fromtimestamp(stat.st_mtime),
        "mime_type": mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    }


def cleanup_old_files(directory: Path, max_age_days: int = 30) -> int:
    """
    Clean up old files from a directory.
    
    Args:
        directory: Directory to clean up
        max_age_days: Maximum age of files in days
        
    Returns:
        Number of files deleted
    """
    if not directory.exists():
        return 0
    
    cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
    deleted_count = 0
    
    for file_path in directory.rglob("*"):
        if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
            try:
                file_path.unlink()
                deleted_count += 1
                logger.info(f"Cleaned up old file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete old file {file_path}: {e}")
    
    return deleted_count
