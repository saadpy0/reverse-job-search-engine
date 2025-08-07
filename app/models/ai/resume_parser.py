"""
Main resume parser orchestrator.
Coordinates all AI components for comprehensive resume analysis.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from app.models.ai.text_extractor import TextExtractor
from app.models.ai.skill_extractor import SkillExtractor
from app.models.ai.experience_parser import ExperienceParser
from app.models.ai.education_parser import EducationParser
from app.models.ai.quality_assessor import QualityAssessor
from app.core.logging import get_logger

logger = get_logger("resume_parser")


class ResumeParser:
    """Main resume parser that orchestrates all AI components."""
    
    def __init__(self):
        """Initialize the resume parser with all components."""
        self.text_extractor = TextExtractor()
        self.skill_extractor = SkillExtractor()
        self.experience_parser = ExperienceParser()
        self.education_parser = EducationParser()
        self.quality_assessor = QualityAssessor()
        
        logger.info("ResumeParser initialized with all AI components")
    
    def parse_resume(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a resume file and extract all information.
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Dictionary containing all parsed resume data
        """
        logger.info(f"Starting comprehensive resume parsing for {file_path.name}")
        
        try:
            # Step 1: Extract text from document
            text_data = self.text_extractor.extract_text(file_path)
            logger.info("Text extraction completed")
            
            # Step 2: Identify sections
            sections = self.text_extractor.identify_sections(text_data['cleaned_text'])
            logger.info(f"Identified {len(sections)} sections")
            
            # Step 3: Extract skills
            skills = self.skill_extractor.extract_skills(text_data['cleaned_text'])
            logger.info("Skill extraction completed")
            
            # Step 4: Extract work experience
            experience = self.experience_parser.extract_experience(text_data['cleaned_text'])
            logger.info(f"Extracted {len(experience)} work experiences")
            
            # Step 5: Extract education
            education = self.education_parser.extract_education(text_data['cleaned_text'])
            logger.info(f"Extracted {len(education)} education entries")
            
            # Step 6: Assess quality
            parsed_data = {
                'cleaned_text': text_data['cleaned_text'],
                'sections': sections,
                'skills': skills,
                'experience': experience,
                'education': education
            }
            
            quality_assessment = self.quality_assessor.assess_resume_quality(parsed_data)
            logger.info("Quality assessment completed")
            
            # Step 7: Compile final results
            results = {
                'file_info': text_data['file_info'],
                'extraction_metadata': {
                    'extraction_method': text_data['extraction_method'],
                    'extraction_confidence': text_data['extraction_confidence'],
                    'parsing_timestamp': datetime.now().isoformat(),
                    'total_characters': len(text_data['cleaned_text']),
                    'word_count': len(text_data['cleaned_text'].split())
                },
                'sections': sections,
                'skills': skills,
                'experience': experience,
                'education': education,
                'quality_assessment': quality_assessment,
                'statistics': self._generate_statistics(
                    text_data, sections, skills, experience, education
                )
            }
            
            logger.info("Resume parsing completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Resume parsing failed: {e}")
            raise
    
    def parse_resume_text(self, text: str) -> Dict[str, Any]:
        """
        Parse resume from text (without file).
        
        Args:
            text: Resume text to parse
            
        Returns:
            Dictionary containing all parsed resume data
        """
        logger.info("Starting resume parsing from text")
        
        try:
            # Clean the text
            cleaned_text = self.text_extractor._clean_text(text)
            
            # Identify sections
            sections = self.text_extractor.identify_sections(cleaned_text)
            
            # Extract skills
            skills = self.skill_extractor.extract_skills(cleaned_text)
            
            # Extract work experience
            experience = self.experience_parser.extract_experience(cleaned_text)
            
            # Extract education
            education = self.education_parser.extract_education(cleaned_text)
            
            # Assess quality
            parsed_data = {
                'cleaned_text': cleaned_text,
                'sections': sections,
                'skills': skills,
                'experience': experience,
                'education': education
            }
            
            quality_assessment = self.quality_assessor.assess_resume_quality(parsed_data)
            
            # Compile results
            results = {
                'extraction_metadata': {
                    'extraction_method': 'text_input',
                    'extraction_confidence': 1.0,
                    'parsing_timestamp': datetime.now().isoformat(),
                    'total_characters': len(cleaned_text),
                    'word_count': len(cleaned_text.split())
                },
                'sections': sections,
                'skills': skills,
                'experience': experience,
                'education': education,
                'quality_assessment': quality_assessment,
                'statistics': self._generate_statistics(
                    {'cleaned_text': cleaned_text}, sections, skills, experience, education
                )
            }
            
            logger.info("Text-based resume parsing completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Text-based resume parsing failed: {e}")
            raise
    
    def extract_skills_only(self, text: str) -> Dict[str, Any]:
        """
        Extract only skills from resume text.
        
        Args:
            text: Resume text to analyze
            
        Returns:
            Dictionary containing extracted skills and statistics
        """
        logger.info("Starting skills-only extraction")
        
        try:
            cleaned_text = self.text_extractor._clean_text(text)
            skills = self.skill_extractor.extract_skills(cleaned_text)
            skill_stats = self.skill_extractor.get_skill_statistics(skills)
            
            results = {
                'skills': skills,
                'statistics': skill_stats,
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            logger.info("Skills extraction completed")
            return results
            
        except Exception as e:
            logger.error(f"Skills extraction failed: {e}")
            raise
    
    def assess_quality_only(self, parsed_data: Dict) -> Dict[str, Any]:
        """
        Assess quality of already parsed resume data.
        
        Args:
            parsed_data: Previously parsed resume data
            
        Returns:
            Dictionary containing quality assessment
        """
        logger.info("Starting quality assessment")
        
        try:
            quality_assessment = self.quality_assessor.assess_resume_quality(parsed_data)
            
            results = {
                'quality_assessment': quality_assessment,
                'assessment_timestamp': datetime.now().isoformat()
            }
            
            logger.info("Quality assessment completed")
            return results
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            raise
    
    def _generate_statistics(self, text_data: Dict, sections: Dict, skills: Dict, 
                           experience: List, education: List) -> Dict[str, Any]:
        """Generate comprehensive statistics about the parsed resume."""
        stats = {
            'text_statistics': {
                'total_characters': len(text_data.get('cleaned_text', '')),
                'word_count': len(text_data.get('cleaned_text', '').split()),
                'line_count': len(text_data.get('cleaned_text', '').split('\n')),
                'section_count': len(sections)
            },
            'skills_statistics': self.skill_extractor.get_skill_statistics(skills),
            'experience_statistics': self.experience_parser.get_experience_statistics(experience),
            'education_statistics': self.education_parser.get_education_statistics(education),
            'overall_statistics': {
                'total_skills': sum(len(skill_list) for skill_list in skills.values()),
                'total_experience_entries': len(experience),
                'total_education_entries': len(education),
                'parsing_completeness': self._calculate_parsing_completeness(
                    sections, skills, experience, education
                )
            }
        }
        
        return stats
    
    def _calculate_parsing_completeness(self, sections: Dict, skills: Dict, 
                                      experience: List, education: List) -> float:
        """Calculate how complete the parsing was."""
        completeness_score = 0.0
        total_checks = 0
        
        # Check if we have sections
        total_checks += 1
        if sections and len(sections) > 0:
            completeness_score += 1.0
        
        # Check if we have skills
        total_checks += 1
        if skills and any(len(skill_list) > 0 for skill_list in skills.values()):
            completeness_score += 1.0
        
        # Check if we have experience
        total_checks += 1
        if experience and len(experience) > 0:
            completeness_score += 1.0
        
        # Check if we have education
        total_checks += 1
        if education and len(education) > 0:
            completeness_score += 1.0
        
        return completeness_score / total_checks if total_checks > 0 else 0.0
    
    def get_parser_status(self) -> Dict[str, Any]:
        """Get the status of all parser components."""
        status = {
            'text_extractor': {
                'available': True,
                'supported_formats': self.text_extractor.supported_formats
            },
            'skill_extractor': {
                'available': True,
                'skill_categories': list(self.skill_extractor.skill_categories.keys())
            },
            'experience_parser': {
                'available': True
            },
            'education_parser': {
                'available': True
            },
            'quality_assessor': {
                'available': True,
                'criteria': list(self.quality_assessor.criteria_weights.keys())
            },
            'overall_status': 'ready'
        }
        
        return status
    
    def save_parsing_results(self, results: Dict, output_path: Path) -> bool:
        """
        Save parsing results to a JSON file.
        
        Args:
            results: Parsing results to save
            output_path: Path to save the results
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert datetime objects to strings for JSON serialization
            json_results = self._prepare_for_json(results)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Parsing results saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save parsing results: {e}")
            return False
    
    def _prepare_for_json(self, data: Any) -> Any:
        """Prepare data for JSON serialization by converting datetime objects."""
        if isinstance(data, dict):
            return {key: self._prepare_for_json(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._prepare_for_json(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        else:
            return data
