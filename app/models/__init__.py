"""
Database models package.
Imports all models to ensure they're registered with SQLAlchemy.
"""

from .user import User
from .resume import Resume, ResumeSkill, ResumeExperience, ResumeEducation
from .job import Job, JobSkill, JobCompany
from .matching import JobMatch, MatchScore

__all__ = [
    "User",
    "Resume",
    "ResumeSkill", 
    "ResumeExperience",
    "ResumeEducation",
    "Job",
    "JobSkill",
    "JobCompany",
    "JobMatch",
    "MatchScore"
]
