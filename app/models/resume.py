"""
Resume models for storing parsed resume data and extracted information.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Resume(Base):
    """Main resume model storing parsed resume data."""
    
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf, docx, txt
    
    # Parsed content
    raw_text = Column(Text, nullable=True)
    parsed_content = Column(Text, nullable=True)  # JSON string of structured data
    
    # Extracted information
    full_name = Column(String(200), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    location = Column(String(200), nullable=True)
    summary = Column(Text, nullable=True)
    
    # Parsing metadata
    parsing_confidence = Column(Float, nullable=True)
    parsing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    parsing_errors = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    parsed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    skills = relationship("ResumeSkill", back_populates="resume", cascade="all, delete-orphan")
    experiences = relationship("ResumeExperience", back_populates="resume", cascade="all, delete-orphan")
    education = relationship("ResumeEducation", back_populates="resume", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Resume(id={self.id}, user_id={self.user_id}, filename='{self.original_filename}')>"


class ResumeSkill(Base):
    """Skills extracted from resume."""
    
    __tablename__ = "resume_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    skill_name = Column(String(200), nullable=False)
    skill_category = Column(String(100), nullable=True)  # programming, soft_skills, tools, etc.
    confidence_score = Column(Float, nullable=True)
    years_of_experience = Column(Float, nullable=True)
    proficiency_level = Column(String(50), nullable=True)  # beginner, intermediate, advanced, expert
    
    # Relationships
    resume = relationship("Resume", back_populates="skills")
    
    def __repr__(self):
        return f"<ResumeSkill(id={self.id}, skill='{self.skill_name}', category='{self.skill_category}')>"


class ResumeExperience(Base):
    """Work experience extracted from resume."""
    
    __tablename__ = "resume_experiences"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    company_name = Column(String(200), nullable=False)
    job_title = Column(String(200), nullable=False)
    location = Column(String(200), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_current = Column(Boolean, default=False)
    
    description = Column(Text, nullable=True)
    achievements = Column(Text, nullable=True)  # JSON string of achievements
    technologies_used = Column(Text, nullable=True)  # JSON string of technologies
    
    # Relationships
    resume = relationship("Resume", back_populates="experiences")
    
    def __repr__(self):
        return f"<ResumeExperience(id={self.id}, title='{self.job_title}', company='{self.company_name}')>"


class ResumeEducation(Base):
    """Education information extracted from resume."""
    
    __tablename__ = "resume_education"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    institution_name = Column(String(200), nullable=False)
    degree = Column(String(200), nullable=False)
    field_of_study = Column(String(200), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    gpa = Column(Float, nullable=True)
    honors = Column(Text, nullable=True)
    
    # Relationships
    resume = relationship("Resume", back_populates="education")
    
    def __repr__(self):
        return f"<ResumeEducation(id={self.id}, degree='{self.degree}', institution='{self.institution_name}')>"
