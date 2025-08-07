"""
Tests for Phase 2: Resume Parser components.
"""

import pytest
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.models.ai.text_extractor import TextExtractor
from app.models.ai.skill_extractor import SkillExtractor
from app.models.ai.experience_parser import ExperienceParser
from app.models.ai.education_parser import EducationParser
from app.models.ai.quality_assessor import QualityAssessor
from app.models.ai.resume_parser import ResumeParser


class TestTextExtractor:
    """Test the text extraction component."""
    
    def test_text_extractor_initialization(self):
        """Test that text extractor initializes correctly."""
        extractor = TextExtractor()
        assert extractor is not None
        assert hasattr(extractor, 'supported_formats')
        assert len(extractor.supported_formats) > 0
    
    def test_text_cleaning(self):
        """Test text cleaning functionality."""
        extractor = TextExtractor()
        
        dirty_text = "This   is   a   test   text   with   extra   spaces."
        cleaned = extractor._clean_text(dirty_text)
        
        assert cleaned == "This is a test text with extra spaces."
    
    def test_section_identification(self):
        """Test section identification."""
        extractor = TextExtractor()
        
        resume_text = """
        CONTACT
        John Doe
        john@example.com
        
        EXPERIENCE
        Software Engineer at Tech Corp
        2020-2023
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology
        """
        
        sections = extractor.identify_sections(resume_text)
        
        assert 'contact' in sections
        assert 'experience' in sections
        assert 'education' in sections


class TestSkillExtractor:
    """Test the skill extraction component."""
    
    def test_skill_extractor_initialization(self):
        """Test that skill extractor initializes correctly."""
        extractor = SkillExtractor()
        assert extractor is not None
        assert hasattr(extractor, 'skill_categories')
        assert len(extractor.skill_categories) > 0
    
    def test_skill_extraction(self):
        """Test skill extraction from text."""
        extractor = SkillExtractor()
        
        resume_text = """
        I have experience with Python, JavaScript, and React.
        I also know Docker and AWS.
        """
        
        skills = extractor.extract_skills(resume_text)
        
        # Should extract some skills
        assert isinstance(skills, dict)
        assert any(len(skill_list) > 0 for skill_list in skills.values())
    
    def test_skill_categorization(self):
        """Test skill categorization."""
        extractor = SkillExtractor()
        
        # Test programming language categorization
        category = extractor._categorize_skill("Python")
        assert category == "programming_languages"
        
        # Test framework categorization
        category = extractor._categorize_skill("React")
        assert category == "frameworks"


class TestExperienceParser:
    """Test the experience parsing component."""
    
    def test_experience_parser_initialization(self):
        """Test that experience parser initializes correctly."""
        parser = ExperienceParser()
        assert parser is not None
        assert hasattr(parser, 'job_titles')
        assert len(parser.job_titles) > 0
    
    def test_experience_extraction(self):
        """Test experience extraction from text."""
        parser = ExperienceParser()
        
        experience_text = """
        WORK EXPERIENCE
        
        Software Engineer
        Tech Company Inc.
        2020-2023
        - Developed web applications
        - Led team of 5 developers
        """
        
        experiences = parser.extract_experience(experience_text)
        
        # Should extract at least one experience
        assert isinstance(experiences, list)
        assert len(experiences) > 0


class TestEducationParser:
    """Test the education parsing component."""
    
    def test_education_parser_initialization(self):
        """Test that education parser initializes correctly."""
        parser = EducationParser()
        assert parser is not None
        assert hasattr(parser, 'degree_patterns')
        assert len(parser.degree_patterns) > 0
    
    def test_education_extraction(self):
        """Test education extraction from text."""
        parser = EducationParser()
        
        education_text = """
        EDUCATION
        
        Bachelor of Science in Computer Science
        University of Technology
        2016-2020
        GPA: 3.8
        """
        
        education = parser.extract_education(education_text)
        
        # Should extract at least one education entry
        assert isinstance(education, list)
        assert len(education) > 0


class TestQualityAssessor:
    """Test the quality assessment component."""
    
    def test_quality_assessor_initialization(self):
        """Test that quality assessor initializes correctly."""
        assessor = QualityAssessor()
        assert assessor is not None
        assert hasattr(assessor, 'criteria_weights')
        assert len(assessor.criteria_weights) > 0
    
    def test_quality_assessment(self):
        """Test quality assessment functionality."""
        assessor = QualityAssessor()
        
        # Mock parsed data
        parsed_data = {
            'cleaned_text': 'This is a test resume with some content.',
            'sections': {
                'contact': 'John Doe, john@example.com',
                'experience': 'Software Engineer at Tech Corp',
                'education': 'Bachelor of Science'
            },
            'skills': {
                'programming_languages': [{'skill_name': 'Python'}],
                'frameworks': [{'skill_name': 'React'}]
            },
            'experience': [{'company_name': 'Tech Corp', 'job_title': 'Software Engineer'}],
            'education': [{'institution_name': 'University', 'degree': 'Bachelor'}]
        }
        
        assessment = assessor.assess_resume_quality(parsed_data)
        
        assert isinstance(assessment, dict)
        assert 'overall_score' in assessment
        assert 'suggestions' in assessment
        assert 'grade' in assessment


class TestResumeParser:
    """Test the main resume parser orchestrator."""
    
    def test_resume_parser_initialization(self):
        """Test that resume parser initializes correctly."""
        parser = ResumeParser()
        assert parser is not None
        assert hasattr(parser, 'text_extractor')
        assert hasattr(parser, 'skill_extractor')
        assert hasattr(parser, 'experience_parser')
        assert hasattr(parser, 'education_parser')
        assert hasattr(parser, 'quality_assessor')
    
    def test_parser_status(self):
        """Test parser status functionality."""
        parser = ResumeParser()
        status = parser.get_parser_status()
        
        assert isinstance(status, dict)
        assert 'overall_status' in status
        assert status['overall_status'] == 'ready'
    
    def test_text_parsing(self):
        """Test text-based resume parsing."""
        parser = ResumeParser()
        
        resume_text = """
        CONTACT
        John Doe
        john@example.com
        
        EXPERIENCE
        Software Engineer at Tech Corp
        2020-2023
        - Developed applications using Python and React
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology
        2016-2020
        
        SKILLS
        Python, JavaScript, React, Docker
        """
        
        results = parser.parse_resume_text(resume_text)
        
        assert isinstance(results, dict)
        assert 'sections' in results
        assert 'skills' in results
        assert 'experience' in results
        assert 'education' in results
        assert 'quality_assessment' in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
