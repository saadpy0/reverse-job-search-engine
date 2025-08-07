"""
Resume API router for handling resume upload, parsing, and retrieval.
"""

import asyncio
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.models.ai.resume_parser import ResumeParser
from app.utils.file_utils import (
    validate_file_type, validate_file_size, generate_unique_filename,
    save_uploaded_file, get_file_path
)
from app.models.resume import Resume
from config.settings import settings

logger = get_logger("resume_api")

router = APIRouter(prefix="/resumes", tags=["resumes"])

# Initialize the resume parser
resume_parser = ResumeParser()


@router.post("/upload")
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: int = 1,  # TODO: Get from authentication
    db: Session = Depends(get_db)
):
    """
    Upload and parse a resume file.
    
    Args:
        file: Resume file to upload (PDF, DOCX, or TXT)
        user_id: ID of the user uploading the resume
        db: Database session
        
    Returns:
        Resume parsing results
    """
    try:
        # Validate file
        if not validate_file_type(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported types: {settings.allowed_file_types}"
            )
        
        # Read file content
        file_content = await file.read()
        
        if not validate_file_size(len(file_content)):
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.max_file_size / (1024*1024)}MB"
            )
        
        # Generate unique filename and save file
        unique_filename = generate_unique_filename(file.filename, user_id)
        file_path, file_size = save_uploaded_file(file_content, unique_filename, user_id)
        
        # Create resume record in database
        resume_record = Resume(
            user_id=user_id,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            file_type=Path(file.filename).suffix.lower(),
            parsing_status="processing"
        )
        
        db.add(resume_record)
        db.commit()
        db.refresh(resume_record)
        
        # Start background parsing task
        background_tasks.add_task(
            parse_resume_background,
            resume_record.id,
            file_path,
            db
        )
        
        return {
            "message": "Resume uploaded successfully",
            "resume_id": resume_record.id,
            "filename": file.filename,
            "status": "processing",
            "estimated_time": "30-60 seconds"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload resume")


@router.get("/{resume_id}")
async def get_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Get parsed resume data by ID.
    
    Args:
        resume_id: ID of the resume
        db: Database session
        
    Returns:
        Parsed resume data
    """
    try:
        resume_record = db.query(Resume).filter(Resume.id == resume_id).first()
        
        if not resume_record:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Check if parsing is complete
        if resume_record.parsing_status != "completed":
            return {
                "resume_id": resume_id,
                "status": resume_record.parsing_status,
                "message": "Resume is still being processed"
            }
        
        # Load parsing results
        if resume_record.parsed_content:
            import json
            parsed_data = json.loads(resume_record.parsed_content)
            
            return {
                "resume_id": resume_id,
                "status": "completed",
                "data": parsed_data
            }
        else:
            raise HTTPException(status_code=500, detail="Parsed data not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get resume {resume_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve resume")


@router.get("/{resume_id}/status")
async def get_resume_status(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the processing status of a resume.
    
    Args:
        resume_id: ID of the resume
        db: Database session
        
    Returns:
        Processing status
    """
    try:
        resume_record = db.query(Resume).filter(Resume.id == resume_id).first()
        
        if not resume_record:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        return {
            "resume_id": resume_id,
            "status": resume_record.parsing_status,
            "confidence": resume_record.parsing_confidence,
            "errors": resume_record.parsing_errors,
            "created_at": resume_record.created_at,
            "parsed_at": resume_record.parsed_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get resume status {resume_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get resume status")


@router.post("/{resume_id}/skills")
async def extract_skills_only(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Extract only skills from a resume.
    
    Args:
        resume_id: ID of the resume
        db: Database session
        
    Returns:
        Extracted skills
    """
    try:
        resume_record = db.query(Resume).filter(Resume.id == resume_id).first()
        
        if not resume_record:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Read the file
        file_path = Path(resume_record.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Resume file not found")
        
        # Extract text first
        text_data = resume_parser.text_extractor.extract_text(file_path)
        
        # Extract skills only
        skills_result = resume_parser.extract_skills_only(text_data['cleaned_text'])
        
        return {
            "resume_id": resume_id,
            "skills": skills_result['skills'],
            "statistics": skills_result['statistics']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to extract skills from resume {resume_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract skills")


@router.post("/parse-text")
async def parse_resume_text(
    text: str,
    user_id: int = 1  # TODO: Get from authentication
):
    """
    Parse resume from text input.
    
    Args:
        text: Resume text to parse
        user_id: ID of the user
        
    Returns:
        Parsed resume data
    """
    try:
        if not text or len(text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Resume text must be at least 50 characters long"
            )
        
        # Parse the text
        results = resume_parser.parse_resume_text(text)
        
        return {
            "message": "Resume text parsed successfully",
            "user_id": user_id,
            "data": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text parsing failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse resume text")


@router.get("/parser/status")
async def get_parser_status():
    """
    Get the status of the resume parser components.
    
    Returns:
        Parser component status
    """
    try:
        status = resume_parser.get_parser_status()
        return {
            "message": "Parser status retrieved successfully",
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Failed to get parser status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get parser status")


async def parse_resume_background(resume_id: int, file_path: Path, db: Session):
    """
    Background task to parse a resume file.
    
    Args:
        resume_id: ID of the resume record
        file_path: Path to the resume file
        db: Database session
    """
    try:
        logger.info(f"Starting background parsing for resume {resume_id}")
        
        # Update status to processing
        resume_record = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume_record:
            resume_record.parsing_status = "processing"
            db.commit()
        
        # Parse the resume
        results = resume_parser.parse_resume(file_path)
        
        # Save results to database
        import json
        resume_record.parsed_content = json.dumps(results)
        resume_record.parsing_status = "completed"
        resume_record.parsing_confidence = results.get('extraction_metadata', {}).get('extraction_confidence', 0.0)
        resume_record.parsed_at = datetime.now()
        
        db.commit()
        
        logger.info(f"Background parsing completed for resume {resume_id}")
        
    except Exception as e:
        logger.error(f"Background parsing failed for resume {resume_id}: {e}")
        
        # Update status to failed
        try:
            resume_record = db.query(Resume).filter(Resume.id == resume_id).first()
            if resume_record:
                resume_record.parsing_status = "failed"
                resume_record.parsing_errors = str(e)
                db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update resume status: {db_error}")


# Import datetime for background task
from datetime import datetime
