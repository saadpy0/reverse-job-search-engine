"""
Resume quality assessment and improvement suggestions.
Analyzes resume completeness, structure, and effectiveness.
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from app.core.logging import get_logger

logger = get_logger("quality_assessor")


class QualityAssessor:
    """Assess resume quality and provide improvement suggestions."""
    
    def __init__(self):
        """Initialize the quality assessor."""
        # Quality criteria weights
        self.criteria_weights = {
            'completeness': 0.25,
            'structure': 0.20,
            'content_quality': 0.25,
            'ats_compatibility': 0.15,
            'professionalism': 0.15
        }
        
        # Required sections
        self.required_sections = [
            'contact', 'summary', 'experience', 'education', 'skills'
        ]
        
        # ATS keywords to check
        self.ats_keywords = [
            'experience', 'skills', 'education', 'work', 'job', 'position',
            'responsibilities', 'achievements', 'leadership', 'management',
            'project', 'team', 'development', 'analysis', 'design'
        ]
    
    def assess_resume_quality(self, parsed_data: Dict) -> Dict:
        """
        Assess the overall quality of a resume.
        
        Args:
            parsed_data: Parsed resume data from the parser
            
        Returns:
            Dictionary with quality scores and suggestions
        """
        logger.info("Starting resume quality assessment")
        
        # Extract components
        text = parsed_data.get('cleaned_text', '')
        sections = parsed_data.get('sections', {})
        skills = parsed_data.get('skills', {})
        experience = parsed_data.get('experience', [])
        education = parsed_data.get('education', [])
        
        # Calculate individual scores
        completeness_score = self._assess_completeness(sections, skills, experience, education)
        structure_score = self._assess_structure(text, sections)
        content_score = self._assess_content_quality(text, experience, education)
        ats_score = self._assess_ats_compatibility(text, sections)
        professionalism_score = self._assess_professionalism(text)
        
        # Calculate weighted overall score
        overall_score = (
            completeness_score * self.criteria_weights['completeness'] +
            structure_score * self.criteria_weights['structure'] +
            content_score * self.criteria_weights['content_quality'] +
            ats_score * self.criteria_weights['ats_compatibility'] +
            professionalism_score * self.criteria_weights['professionalism']
        )
        
        # Generate improvement suggestions
        suggestions = self._generate_suggestions(
            completeness_score, structure_score, content_score, 
            ats_score, professionalism_score, sections, skills, experience, education
        )
        
        assessment = {
            'overall_score': round(overall_score, 2),
            'scores': {
                'completeness': round(completeness_score, 2),
                'structure': round(structure_score, 2),
                'content_quality': round(content_score, 2),
                'ats_compatibility': round(ats_score, 2),
                'professionalism': round(professionalism_score, 2)
            },
            'suggestions': suggestions,
            'strengths': self._identify_strengths(sections, skills, experience, education),
            'weaknesses': self._identify_weaknesses(sections, skills, experience, education),
            'grade': self._calculate_grade(overall_score)
        }
        
        logger.info(f"Resume quality assessment completed. Overall score: {overall_score:.2f}")
        return assessment
    
    def _assess_completeness(self, sections: Dict, skills: Dict, experience: List, education: List) -> float:
        """Assess resume completeness."""
        score = 0.0
        total_checks = 0
        
        # Check required sections
        for section in self.required_sections:
            total_checks += 1
            if section in sections and sections[section].strip():
                score += 1.0
        
        # Check for skills
        total_checks += 1
        if skills and any(len(skill_list) > 0 for skill_list in skills.values()):
            score += 1.0
        
        # Check for experience
        total_checks += 1
        if experience and len(experience) > 0:
            score += 1.0
        
        # Check for education
        total_checks += 1
        if education and len(education) > 0:
            score += 1.0
        
        # Check for contact information
        total_checks += 1
        if 'contact' in sections and self._has_contact_info(sections['contact']):
            score += 1.0
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def _assess_structure(self, text: str, sections: Dict) -> float:
        """Assess resume structure and organization."""
        score = 0.0
        total_checks = 0
        
        # Check for clear section headers
        total_checks += 1
        if len(sections) >= 3:
            score += 1.0
        
        # Check for consistent formatting
        total_checks += 1
        if self._has_consistent_formatting(text):
            score += 1.0
        
        # Check for logical flow
        total_checks += 1
        if self._has_logical_flow(sections):
            score += 1.0
        
        # Check for appropriate length
        total_checks += 1
        word_count = len(text.split())
        if 200 <= word_count <= 800:  # Ideal resume length
            score += 1.0
        elif 100 <= word_count <= 1200:  # Acceptable range
            score += 0.7
        elif word_count > 1200:  # Too long
            score += 0.3
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def _assess_content_quality(self, text: str, experience: List, education: List) -> float:
        """Assess the quality of resume content."""
        score = 0.0
        total_checks = 0
        
        # Check for action verbs
        total_checks += 1
        action_verbs = self._count_action_verbs(text)
        if action_verbs >= 5:
            score += 1.0
        elif action_verbs >= 3:
            score += 0.7
        elif action_verbs >= 1:
            score += 0.4
        
        # Check for quantifiable achievements
        total_checks += 1
        quantifiable = self._count_quantifiable_achievements(text)
        if quantifiable >= 3:
            score += 1.0
        elif quantifiable >= 1:
            score += 0.6
        
        # Check for recent experience
        total_checks += 1
        if experience and self._has_recent_experience(experience):
            score += 1.0
        
        # Check for relevant education
        total_checks += 1
        if education and self._has_relevant_education(education):
            score += 1.0
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def _assess_ats_compatibility(self, text: str, sections: Dict) -> float:
        """Assess ATS (Applicant Tracking System) compatibility."""
        score = 0.0
        total_checks = 0
        
        # Check for ATS keywords
        total_checks += 1
        keyword_matches = sum(1 for keyword in self.ats_keywords if keyword.lower() in text.lower())
        if keyword_matches >= 8:
            score += 1.0
        elif keyword_matches >= 5:
            score += 0.7
        elif keyword_matches >= 3:
            score += 0.4
        
        # Check for simple formatting
        total_checks += 1
        if self._has_simple_formatting(text):
            score += 1.0
        
        # Check for standard section headers
        total_checks += 1
        standard_headers = sum(1 for section in sections.keys() if self._is_standard_header(section))
        if standard_headers >= 3:
            score += 1.0
        elif standard_headers >= 2:
            score += 0.7
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def _assess_professionalism(self, text: str) -> float:
        """Assess professionalism and writing quality."""
        score = 0.0
        total_checks = 0
        
        # Check for spelling and grammar (basic check)
        total_checks += 1
        if not self._has_obvious_errors(text):
            score += 1.0
        
        # Check for professional tone
        total_checks += 1
        if self._has_professional_tone(text):
            score += 1.0
        
        # Check for appropriate language
        total_checks += 1
        if not self._has_inappropriate_language(text):
            score += 1.0
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def _has_contact_info(self, contact_text: str) -> bool:
        """Check if contact section has essential information."""
        has_email = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', contact_text)
        has_phone = re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', contact_text)
        return bool(has_email or has_phone)
    
    def _has_consistent_formatting(self, text: str) -> bool:
        """Check for consistent formatting."""
        lines = text.split('\n')
        bullet_points = sum(1 for line in lines if line.strip().startswith(('•', '-', '*')))
        return bullet_points > 0 and bullet_points < len(lines) * 0.8
    
    def _has_logical_flow(self, sections: Dict) -> bool:
        """Check for logical flow of sections."""
        # Check if experience comes before education (typical flow)
        section_order = list(sections.keys())
        experience_index = -1
        education_index = -1
        
        for i, section in enumerate(section_order):
            if 'experience' in section.lower():
                experience_index = i
            elif 'education' in section.lower():
                education_index = i
        
        return experience_index < education_index or experience_index == -1 or education_index == -1
    
    def _count_action_verbs(self, text: str) -> int:
        """Count action verbs in the text."""
        action_verbs = [
            'developed', 'implemented', 'managed', 'led', 'created', 'designed',
            'built', 'maintained', 'improved', 'increased', 'decreased', 'achieved',
            'coordinated', 'organized', 'planned', 'executed', 'delivered', 'launched',
            'established', 'grew', 'expanded', 'optimized', 'streamlined', 'enhanced'
        ]
        
        text_lower = text.lower()
        return sum(1 for verb in action_verbs if verb in text_lower)
    
    def _count_quantifiable_achievements(self, text: str) -> int:
        """Count quantifiable achievements."""
        patterns = [
            r'\d+%',  # Percentages
            r'\$\d+',  # Dollar amounts
            r'\d+\s+(?:people|employees|users|customers)',  # People counts
            r'\d+\s+(?:years|months|weeks)',  # Time periods
            r'increased\s+by\s+\d+',  # Increase statements
            r'decreased\s+by\s+\d+',  # Decrease statements
        ]
        
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        
        return count
    
    def _has_recent_experience(self, experience: List) -> bool:
        """Check if there's recent work experience."""
        current_year = datetime.now().year
        for exp in experience:
            if exp.get('end_date'):
                if isinstance(exp['end_date'], datetime):
                    if exp['end_date'].year >= current_year - 2:
                        return True
        return False
    
    def _has_relevant_education(self, education: List) -> bool:
        """Check if education is relevant to typical job requirements."""
        relevant_fields = [
            'computer', 'engineering', 'science', 'technology', 'business',
            'management', 'administration', 'mathematics', 'statistics'
        ]
        
        for edu in education:
            field = edu.get('field_of_study', '').lower()
            if any(relevant in field for relevant in relevant_fields):
                return True
        return False
    
    def _has_simple_formatting(self, text: str) -> bool:
        """Check if formatting is simple and ATS-friendly."""
        # Check for excessive formatting characters
        formatting_chars = text.count('*') + text.count('_') + text.count('`')
        return formatting_chars < len(text) * 0.05
    
    def _is_standard_header(self, section_name: str) -> bool:
        """Check if section header is standard."""
        standard_headers = [
            'experience', 'education', 'skills', 'summary', 'contact',
            'work', 'employment', 'qualifications', 'achievements'
        ]
        return any(header in section_name.lower() for header in standard_headers)
    
    def _has_obvious_errors(self, text: str) -> bool:
        """Check for obvious spelling/grammar errors."""
        # Basic checks - in production, use a proper spell checker
        common_errors = ['teh', 'recieve', 'seperate', 'occured', 'definately']
        return any(error in text.lower() for error in common_errors)
    
    def _has_professional_tone(self, text: str) -> bool:
        """Check for professional tone."""
        unprofessional_words = ['awesome', 'cool', 'stuff', 'things', 'guy', 'dude']
        return not any(word in text.lower() for word in unprofessional_words)
    
    def _has_inappropriate_language(self, text: str) -> bool:
        """Check for inappropriate language."""
        inappropriate_words = ['fuck', 'shit', 'damn', 'hell']  # Basic examples
        return any(word in text.lower() for word in inappropriate_words)
    
    def _generate_suggestions(self, completeness: float, structure: float, content: float,
                            ats: float, professionalism: float, sections: Dict, 
                            skills: Dict, experience: List, education: List) -> List[str]:
        """Generate improvement suggestions based on scores."""
        suggestions = []
        
        if completeness < 0.7:
            suggestions.append("Add missing required sections (contact, summary, experience, education, skills)")
        
        if structure < 0.7:
            suggestions.append("Improve resume structure with clear section headers and consistent formatting")
        
        if content < 0.7:
            suggestions.append("Add more action verbs and quantifiable achievements to make your experience stand out")
        
        if ats < 0.7:
            suggestions.append("Include more industry-specific keywords to improve ATS compatibility")
        
        if professionalism < 0.7:
            suggestions.append("Review and improve writing quality and professional tone")
        
        # Specific suggestions
        if not skills or not any(len(skill_list) > 0 for skill_list in skills.values()):
            suggestions.append("Add a comprehensive skills section with technical and soft skills")
        
        if not experience:
            suggestions.append("Include relevant work experience with specific achievements")
        
        if not education:
            suggestions.append("Add your educational background and relevant certifications")
        
        return suggestions
    
    def _identify_strengths(self, sections: Dict, skills: Dict, experience: List, education: List) -> List[str]:
        """Identify resume strengths."""
        strengths = []
        
        if len(sections) >= 4:
            strengths.append("Well-organized with multiple relevant sections")
        
        if skills and any(len(skill_list) > 5 for skill_list in skills.values()):
            strengths.append("Comprehensive skills section")
        
        if experience and len(experience) >= 2:
            strengths.append("Multiple work experiences showing career progression")
        
        if education and len(education) >= 1:
            strengths.append("Strong educational background")
        
        return strengths
    
    def _identify_weaknesses(self, sections: Dict, skills: Dict, experience: List, education: List) -> List[str]:
        """Identify resume weaknesses."""
        weaknesses = []
        
        if len(sections) < 3:
            weaknesses.append("Missing important resume sections")
        
        if not skills or not any(len(skill_list) > 0 for skill_list in skills.values()):
            weaknesses.append("No skills section or insufficient skills listed")
        
        if not experience:
            weaknesses.append("No work experience listed")
        
        if not education:
            weaknesses.append("No educational background provided")
        
        return weaknesses
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade based on score."""
        if score >= 0.9:
            return "A+"
        elif score >= 0.85:
            return "A"
        elif score >= 0.8:
            return "A-"
        elif score >= 0.75:
            return "B+"
        elif score >= 0.7:
            return "B"
        elif score >= 0.65:
            return "B-"
        elif score >= 0.6:
            return "C+"
        elif score >= 0.55:
            return "C"
        elif score >= 0.5:
            return "C-"
        else:
            return "D"
