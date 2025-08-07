"""
Work experience parsing for resume analysis.
Extracts work history, dates, companies, roles, and achievements using NLP techniques.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

# NLP libraries
try:
    import spacy
    from spacy.matcher import Matcher
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from app.core.logging import get_logger

logger = get_logger("experience_parser")


class ExperienceParser:
    """Parse work experience from resume text."""
    
    def __init__(self):
        """Initialize the experience parser."""
        self.nlp = None
        self.matcher = None
        
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                self.matcher = Matcher(self.nlp.vocab)
                self._setup_experience_patterns()
                logger.info("ExperienceParser initialized with spaCy")
            except OSError:
                logger.warning("spaCy model not found for experience parsing")
        
        # Common job title patterns
        self.job_titles = {
            'software_engineer': [
                'Software Engineer', 'Software Developer', 'Programmer', 'Developer',
                'Full Stack Developer', 'Frontend Developer', 'Backend Developer',
                'Web Developer', 'Mobile Developer', 'iOS Developer', 'Android Developer'
            ],
            'data_scientist': [
                'Data Scientist', 'Machine Learning Engineer', 'ML Engineer',
                'Data Analyst', 'Data Engineer', 'Business Intelligence Analyst'
            ],
            'manager': [
                'Manager', 'Team Lead', 'Project Manager', 'Product Manager',
                'Engineering Manager', 'Technical Lead', 'Senior Manager'
            ],
            'designer': [
                'UX Designer', 'UI Designer', 'Product Designer', 'Graphic Designer',
                'Web Designer', 'Interaction Designer'
            ]
        }
        
        # Date patterns
        self.date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{2,4})',  # MM/DD/YYYY
            r'(\d{1,2})-(\d{1,2})-(\d{2,4})',  # MM-DD-YYYY
            r'(\w+)\s+(\d{4})',  # Month YYYY
            r'(\d{4})\s*-\s*(\d{4}|\bPresent\b|\bCurrent\b)',  # YYYY - YYYY/Present
            r'(\w+)\s+(\d{4})\s*-\s*(\w+)\s+(\d{4})',  # Month YYYY - Month YYYY
        ]
    
    def _setup_experience_patterns(self):
        """Set up spaCy patterns for experience detection."""
        if not self.nlp or not self.matcher:
            return
        
        # Patterns for company names
        company_patterns = [
            [{"ENT_TYPE": "ORG"}],  # Named entity organization
            [{"LOWER": "inc"}, {"LOWER": "."}],
            [{"LOWER": "corp"}, {"LOWER": "."}],
            [{"LOWER": "ltd"}, {"LOWER": "."}],
            [{"LOWER": "llc"}],
        ]
        
        # Patterns for job titles
        title_patterns = [
            [{"LOWER": "senior"}, {"LOWER": "software"}, {"LOWER": "engineer"}],
            [{"LOWER": "software"}, {"LOWER": "engineer"}],
            [{"LOWER": "data"}, {"LOWER": "scientist"}],
            [{"LOWER": "product"}, {"LOWER": "manager"}],
            [{"LOWER": "project"}, {"LOWER": "manager"}],
        ]
        
        self.matcher.add("COMPANY", company_patterns)
        self.matcher.add("JOB_TITLE", title_patterns)
    
    def extract_experience(self, text: str) -> List[Dict]:
        """
        Extract work experience from resume text.
        
        Args:
            text: Resume text to analyze
            
        Returns:
            List of work experience entries
        """
        logger.info("Starting work experience extraction")
        
        # Split text into potential experience sections
        experience_sections = self._identify_experience_sections(text)
        
        experiences = []
        for section in experience_sections:
            experience = self._parse_experience_section(section)
            if experience:
                experiences.append(experience)
        
        # Sort by start date (most recent first)
        experiences.sort(key=lambda x: x.get('start_date', datetime.min), reverse=True)
        
        logger.info(f"Extracted {len(experiences)} work experience entries")
        return experiences
    
    def _identify_experience_sections(self, text: str) -> List[str]:
        """Identify sections that contain work experience."""
        sections = []
        
        # Common experience section headers
        experience_headers = [
            r'work\s+experience',
            r'employment\s+history',
            r'professional\s+experience',
            r'career\s+history',
            r'job\s+history',
            r'experience'
        ]
        
        lines = text.split('\n')
        current_section = []
        in_experience_section = False
        
        for line in lines:
            line = line.strip()
            
            # Check if this line is an experience section header
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in experience_headers):
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
                in_experience_section = True
            elif in_experience_section:
                # Check if we've hit another major section
                if self._is_major_section_header(line):
                    if current_section:
                        sections.append('\n'.join(current_section))
                    current_section = []
                    in_experience_section = False
                else:
                    current_section.append(line)
        
        # Add the last section
        if current_section:
            sections.append('\n'.join(current_section))
        
        return sections
    
    def _is_major_section_header(self, line: str) -> bool:
        """Check if a line is a major section header."""
        major_sections = [
            r'education',
            r'skills',
            r'projects',
            r'certifications',
            r'languages',
            r'interests',
            r'achievements'
        ]
        
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in major_sections)
    
    def _parse_experience_section(self, section_text: str) -> Optional[Dict]:
        """Parse a single experience section."""
        if not section_text.strip():
            return None
        
        # Extract company name
        company_name = self._extract_company_name(section_text)
        
        # Extract job title
        job_title = self._extract_job_title(section_text)
        
        # Extract dates
        start_date, end_date, is_current = self._extract_dates(section_text)
        
        # Extract location
        location = self._extract_location(section_text)
        
        # Extract description and achievements
        description, achievements = self._extract_description_and_achievements(section_text)
        
        # Extract technologies used
        technologies = self._extract_technologies(section_text)
        
        if not company_name and not job_title:
            return None
        
        experience = {
            'company_name': company_name,
            'job_title': job_title,
            'start_date': start_date,
            'end_date': end_date,
            'is_current': is_current,
            'location': location,
            'description': description,
            'achievements': achievements,
            'technologies_used': technologies,
            'duration_months': self._calculate_duration(start_date, end_date),
            'confidence': self._calculate_experience_confidence(section_text)
        }
        
        return experience
    
    def _extract_company_name(self, text: str) -> Optional[str]:
        """Extract company name from text."""
        if self.nlp and self.matcher:
            doc = self.nlp(text)
            matches = self.matcher(doc)
            
            for match_id, start, end in matches:
                if self.nlp.vocab.strings[match_id] == "COMPANY":
                    return doc[start:end].text.strip()
        
        # Fallback: look for common company patterns
        company_patterns = [
            r'([A-Z][a-zA-Z\s&]+)\s+(?:Inc|Corp|LLC|Ltd|Company|Co)\.?',
            r'([A-Z][a-zA-Z\s&]+)\s+(?:Technologies|Systems|Solutions|Group|Partners)',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_job_title(self, text: str) -> Optional[str]:
        """Extract job title from text."""
        if self.nlp and self.matcher:
            doc = self.nlp(text)
            matches = self.matcher(doc)
            
            for match_id, start, end in matches:
                if self.nlp.vocab.strings[match_id] == "JOB_TITLE":
                    return doc[start:end].text.strip()
        
        # Fallback: look for job title patterns
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            
            # Look for lines that might be job titles
            if any(title.lower() in line.lower() for titles in self.job_titles.values() for title in titles):
                return line
        
        return None
    
    def _extract_dates(self, text: str) -> Tuple[Optional[datetime], Optional[datetime], bool]:
        """Extract start and end dates from text."""
        start_date = None
        end_date = None
        is_current = False
        
        # Look for date patterns
        for pattern in self.date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    date_str = match.group(0)
                    
                    # Check if it's a current position
                    if 'present' in date_str.lower() or 'current' in date_str.lower():
                        is_current = True
                        if not end_date:
                            end_date = datetime.now()
                    
                    # Try to parse the date
                    parsed_date = self._parse_date_string(date_str)
                    if parsed_date:
                        if not start_date:
                            start_date = parsed_date
                        elif not end_date and not is_current:
                            end_date = parsed_date
                            
                except Exception as e:
                    logger.debug(f"Failed to parse date: {match.group(0)} - {e}")
        
        return start_date, end_date, is_current
    
    def _parse_date_string(self, date_str: str) -> Optional[datetime]:
        """Parse a date string into a datetime object."""
        try:
            # Handle common date formats
            if re.match(r'\d{4}', date_str):
                # Just year
                return datetime(int(date_str), 1, 1)
            elif re.match(r'\w+\s+\d{4}', date_str):
                # Month Year
                return date_parser.parse(date_str, fuzzy=True)
            elif re.match(r'\d{1,2}/\d{1,2}/\d{2,4}', date_str):
                # MM/DD/YYYY
                return date_parser.parse(date_str)
            else:
                # Try fuzzy parsing
                return date_parser.parse(date_str, fuzzy=True)
        except Exception as e:
            logger.debug(f"Failed to parse date string '{date_str}': {e}")
            return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from text."""
        # Look for location patterns
        location_patterns = [
            r'([A-Z][a-zA-Z\s]+),\s*([A-Z]{2})',  # City, State
            r'([A-Z][a-zA-Z\s]+),\s*([A-Z][a-zA-Z\s]+)',  # City, Country
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()
        
        return None
    
    def _extract_description_and_achievements(self, text: str) -> Tuple[Optional[str], List[str]]:
        """Extract job description and achievements."""
        description = None
        achievements = []
        
        lines = text.split('\n')
        in_description = False
        description_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or self._is_section_header(line):
                continue
            
            # Look for bullet points (achievements)
            if line.startswith(('•', '-', '*', '→', '▶')):
                achievements.append(line[1:].strip())
            elif line.startswith(('o ', '○ ', '▪ ')):
                achievements.append(line[2:].strip())
            else:
                # Regular description text
                description_lines.append(line)
        
        if description_lines:
            description = ' '.join(description_lines)
        
        return description, achievements
    
    def _extract_technologies(self, text: str) -> List[str]:
        """Extract technologies mentioned in the experience."""
        technologies = []
        
        # Common technology patterns
        tech_patterns = [
            r'\b(Python|JavaScript|Java|React|Angular|Django|Flask|AWS|Docker|Kubernetes|MySQL|PostgreSQL|MongoDB)\b',
            r'\b(TensorFlow|PyTorch|Scikit-learn|Pandas|NumPy|Git|Jenkins|Ansible|Terraform)\b',
        ]
        
        for pattern in tech_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                tech = match.group(1)
                if tech not in technologies:
                    technologies.append(tech)
        
        return technologies
    
    def _is_section_header(self, line: str) -> bool:
        """Check if a line is a section header."""
        header_patterns = [
            r'^[A-Z][A-Z\s]+$',  # All caps
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # Title Case
        ]
        
        return any(re.match(pattern, line) for pattern in header_patterns)
    
    def _calculate_duration(self, start_date: Optional[datetime], end_date: Optional[datetime]) -> Optional[int]:
        """Calculate duration in months."""
        if not start_date:
            return None
        
        if not end_date:
            end_date = datetime.now()
        
        delta = relativedelta(end_date, start_date)
        return delta.years * 12 + delta.months
    
    def _calculate_experience_confidence(self, text: str) -> float:
        """Calculate confidence score for experience extraction."""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for having key elements
        if re.search(r'\b(experience|work|employment|career)\b', text, re.IGNORECASE):
            confidence += 0.2
        
        if re.search(r'\d{4}', text):  # Has dates
            confidence += 0.2
        
        if re.search(r'\b(Inc|Corp|LLC|Ltd|Company|Technologies|Systems)\b', text, re.IGNORECASE):
            confidence += 0.1
        
        if re.search(r'[•\-*]', text):  # Has bullet points
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def get_experience_statistics(self, experiences: List[Dict]) -> Dict[str, any]:
        """Get statistics about extracted work experience."""
        if not experiences:
            return {}
        
        stats = {
            'total_experience': len(experiences),
            'total_duration_months': 0,
            'average_duration_months': 0,
            'current_positions': 0,
            'companies': set(),
            'job_titles': set(),
            'locations': set(),
            'technologies': set()
        }
        
        for exp in experiences:
            if exp.get('duration_months'):
                stats['total_duration_months'] += exp['duration_months']
            
            if exp.get('is_current'):
                stats['current_positions'] += 1
            
            if exp.get('company_name'):
                stats['companies'].add(exp['company_name'])
            
            if exp.get('job_title'):
                stats['job_titles'].add(exp['job_title'])
            
            if exp.get('location'):
                stats['locations'].add(exp['location'])
            
            if exp.get('technologies_used'):
                stats['technologies'].update(exp['technologies_used'])
        
        if stats['total_experience'] > 0:
            stats['average_duration_months'] = stats['total_duration_months'] / stats['total_experience']
        
        # Convert sets to lists for JSON serialization
        stats['companies'] = list(stats['companies'])
        stats['job_titles'] = list(stats['job_titles'])
        stats['locations'] = list(stats['locations'])
        stats['technologies'] = list(stats['technologies'])
        
        return stats
