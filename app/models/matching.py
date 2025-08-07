"""
Matching models for storing job-resume matches and scoring data.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class JobMatch(Base):
    """Job-resume matching results."""
    
    __tablename__ = "job_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    # Overall match score
    overall_score = Column(Float, nullable=False, index=True)
    match_rank = Column(Integer, nullable=True)  # Rank among all matches for this user
    
    # Detailed scoring breakdown
    skill_match_score = Column(Float, nullable=True)
    experience_match_score = Column(Float, nullable=True)
    location_match_score = Column(Float, nullable=True)
    salary_match_score = Column(Float, nullable=True)
    culture_match_score = Column(Float, nullable=True)
    
    # Match metadata
    is_hidden_opportunity = Column(Boolean, default=False)
    match_reason = Column(Text, nullable=True)  # Why this job was recommended
    skill_gaps = Column(JSON, nullable=True)  # JSON array of missing skills
    skill_overlaps = Column(JSON, nullable=True)  # JSON array of matching skills
    
    # User interaction
    user_viewed = Column(Boolean, default=False)
    user_applied = Column(Boolean, default=False)
    user_saved = Column(Boolean, default=False)
    user_feedback = Column(String(50), nullable=True)  # like, dislike, neutral
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="job_matches")
    resume = relationship("Resume")
    job = relationship("Job", back_populates="matches")
    scores = relationship("MatchScore", back_populates="job_match", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<JobMatch(id={self.id}, user_id={self.user_id}, job_id={self.job_id}, score={self.overall_score})>"


class MatchScore(Base):
    """Detailed scoring breakdown for job matches."""
    
    __tablename__ = "match_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    job_match_id = Column(Integer, ForeignKey("job_matches.id"), nullable=False)
    
    # Score components
    score_type = Column(String(100), nullable=False)  # skill_match, experience_match, etc.
    score_value = Column(Float, nullable=False)
    score_weight = Column(Float, nullable=True)  # Weight in overall calculation
    confidence = Column(Float, nullable=True)  # Confidence in this score
    
    # Score details
    details = Column(JSON, nullable=True)  # Detailed breakdown of the score
    explanation = Column(Text, nullable=True)  # Human-readable explanation
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    job_match = relationship("JobMatch", back_populates="scores")
    
    def __repr__(self):
        return f"<MatchScore(id={self.id}, type='{self.score_type}', value={self.score_value})>"
