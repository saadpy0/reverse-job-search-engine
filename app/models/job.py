"""
Job models for storing job posting data and company information.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class JobCompany(Base):
    """Company information for job postings."""
    
    __tablename__ = "job_companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    # Company details
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)  # startup, small, medium, large
    founded_year = Column(Integer, nullable=True)
    headquarters = Column(String(200), nullable=True)
    
    # Company culture and benefits
    culture_tags = Column(JSON, nullable=True)  # JSON array of culture tags
    benefits = Column(JSON, nullable=True)  # JSON array of benefits
    
    # External IDs
    linkedin_id = Column(String(100), nullable=True)
    glassdoor_id = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    jobs = relationship("Job", back_populates="company")
    
    def __repr__(self):
        return f"<JobCompany(id={self.id}, name='{self.name}', industry='{self.industry}')>"


class Job(Base):
    """Main job posting model."""
    
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("job_companies.id"), nullable=False)
    
    # Job details
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    
    # Location and type
    location = Column(String(200), nullable=True)
    remote_type = Column(String(50), nullable=True)  # remote, hybrid, onsite
    job_type = Column(String(50), nullable=True)  # full-time, part-time, contract, internship
    
    # Salary and benefits
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(3), default="USD")
    salary_period = Column(String(20), default="yearly")  # yearly, monthly, hourly
    benefits = Column(JSON, nullable=True)  # JSON array of benefits
    
    # Job metadata
    experience_level = Column(String(50), nullable=True)  # entry, mid, senior, executive
    education_level = Column(String(50), nullable=True)  # high_school, bachelors, masters, phd
    
    # External information
    source = Column(String(50), nullable=False)  # indeed, linkedin, glassdoor, etc.
    external_id = Column(String(100), nullable=True)
    external_url = Column(String(500), nullable=True)
    
    # Status and visibility
    is_active = Column(Boolean, default=True)
    is_hidden = Column(Boolean, default=False)  # For hidden opportunities
    posting_date = Column(DateTime, nullable=True)
    closing_date = Column(DateTime, nullable=True)
    
    # AI processing metadata
    ai_processed = Column(Boolean, default=False)
    skill_extracted = Column(Boolean, default=False)
    embedding_generated = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("JobCompany", back_populates="jobs")
    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title}', company='{self.company.name if self.company else 'Unknown'}')>"


class JobSkill(Base):
    """Skills required for job positions."""
    
    __tablename__ = "job_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    skill_name = Column(String(200), nullable=False, index=True)
    skill_category = Column(String(100), nullable=True)  # programming, soft_skills, tools, etc.
    importance_level = Column(String(50), nullable=True)  # required, preferred, nice_to_have
    years_required = Column(Float, nullable=True)
    
    # AI extraction metadata
    confidence_score = Column(Float, nullable=True)
    extraction_method = Column(String(50), nullable=True)  # keyword, nlp, manual
    
    # Relationships
    job = relationship("Job", back_populates="skills")
    
    def __repr__(self):
        return f"<JobSkill(id={self.id}, skill='{self.skill_name}', importance='{self.importance_level}')>"
