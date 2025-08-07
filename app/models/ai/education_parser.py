"""
Education parsing for resume analysis.
Extracts educational background, degrees, institutions, and academic achievements.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.core.logging import get_logger

logger = get_logger("education_parser")


class EducationParser:
    """Parse education information from resume text."""
    
    def __init__(self):
        """Initialize the education parser."""
        # Common degree patterns
        self.degree_patterns = {
            'bachelor': ['Bachelor', 'B.S.', 'B.A.', 'B.Eng', 'B.Tech', 'B.Sc'],
            'master': ['Master', 'M.S.', 'M.A.', 'M.Eng', 'M.Tech', 'M.Sc', 'M.B.A'],
            'phd': ['Ph.D.', 'PhD', 'Doctorate', 'Doctor of Philosophy'],
            'associate': ['Associate', 'A.S.', 'A.A.'],
            'diploma': ['Diploma', 'Certificate', 'Certification']
        }
        
        # Common field of study patterns
        self.field_patterns = [
            'Computer Science', 'Computer Engineering', 'Software Engineering',
            'Information Technology', 'Data Science', 'Machine Learning',
            'Business Administration', 'Economics', 'Mathematics', 'Statistics'
        ]
    
    def extract_education(self, text: str) -> List[Dict]:
        """Extract education information from resume text."""
        logger.info("Starting education extraction")
        
        # Identify education sections
        education_sections = self._identify_education_sections(text)
        
        education_entries = []
        for section in education_sections:
            education = self._parse_education_section(section)
            if education:
                education_entries.append(education)
        
        logger.info(f"Extracted {len(education_entries)} education entries")
        return education_entries
    
    def _identify_education_sections(self, text: str) -> List[str]:
        """Identify sections that contain education information."""
        sections = []
        
        education_headers = [r'education', r'academic', r'qualifications', r'degrees']
        
        lines = text.split('\n')
        current_section = []
        in_education_section = False
        
        for line in lines:
            line = line.strip()
            
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in education_headers):
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
                in_education_section = True
            elif in_education_section:
                if self._is_major_section_header(line):
                    if current_section:
                        sections.append('\n'.join(current_section))
                    current_section = []
                    in_education_section = False
                else:
                    current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section))
        
        return sections
    
    def _is_major_section_header(self, line: str) -> bool:
        """Check if a line is a major section header."""
        major_sections = [r'experience', r'skills', r'projects', r'work']
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in major_sections)
    
    def _parse_education_section(self, section_text: str) -> Optional[Dict]:
        """Parse a single education section."""
        if not section_text.strip():
            return None
        
        institution_name = self._extract_institution_name(section_text)
        degree, field_of_study = self._extract_degree_info(section_text)
        start_date, end_date = self._extract_education_dates(section_text)
        gpa = self._extract_gpa(section_text)
        honors = self._extract_honors(section_text)
        
        if not institution_name and not degree:
            return None
        
        return {
            'institution_name': institution_name,
            'degree': degree,
            'field_of_study': field_of_study,
            'start_date': start_date,
            'end_date': end_date,
            'gpa': gpa,
            'honors': honors,
            'confidence': self._calculate_education_confidence(section_text)
        }
    
    def _extract_institution_name(self, text: str) -> Optional[str]:
        """Extract educational institution name."""
        patterns = [
            r'([A-Z][a-zA-Z\s&]+)\s+(?:University|College|Institute|School)',
            r'([A-Z][a-zA-Z\s&]+)\s+(?:State|National)\s+(?:University|College)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_degree_info(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract degree and field of study."""
        degree = None
        field_of_study = None
        
        for degree_type, patterns in self.degree_patterns.items():
            for pattern in patterns:
                if re.search(r'\b' + re.escape(pattern) + r'\b', text, re.IGNORECASE):
                    degree = pattern
                    break
            if degree:
                break
        
        for field in self.field_patterns:
            if re.search(r'\b' + re.escape(field) + r'\b', text, re.IGNORECASE):
                field_of_study = field
                break
        
        return degree, field_of_study
    
    def _extract_education_dates(self, text: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Extract start and end dates."""
        start_date = None
        end_date = None
        
        # Look for year patterns
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        if len(years) >= 2:
            start_date = datetime(int(years[0]), 1, 1)
            end_date = datetime(int(years[1]), 12, 31)
        elif len(years) == 1:
            start_date = datetime(int(years[0]), 1, 1)
        
        return start_date, end_date
    
    def _extract_gpa(self, text: str) -> Optional[float]:
        """Extract GPA from text."""
        gpa_match = re.search(r'GPA[:\s]*(\d+\.\d+)', text, re.IGNORECASE)
        if gpa_match:
            try:
                gpa = float(gpa_match.group(1))
                if 0.0 <= gpa <= 4.0:
                    return gpa
            except ValueError:
                pass
        return None
    
    def _extract_honors(self, text: str) -> List[str]:
        """Extract honors and achievements."""
        honors = []
        honor_patterns = [
            r'(Summa Cum Laude)', r'(Magna Cum Laude)', r'(Cum Laude)',
            r'(Dean\'s List)', r'(Honor Roll)', r'(Phi Beta Kappa)'
        ]
        
        for pattern in honor_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                honor = match.group(1)
                if honor not in honors:
                    honors.append(honor)
        
        return honors
    
    def _calculate_education_confidence(self, text: str) -> float:
        """Calculate confidence score."""
        confidence = 0.5
        
        if re.search(r'\b(education|university|college|degree)\b', text, re.IGNORECASE):
            confidence += 0.3
        
        if re.search(r'\d{4}', text):
            confidence += 0.2
        
        return min(1.0, confidence)
    
    def get_education_statistics(self, education_entries: List[Dict]) -> Dict[str, any]:
        """Get statistics about extracted education."""
        if not education_entries:
            return {}
        
        stats = {
            'total_education': len(education_entries),
            'institutions': set(),
            'degrees': set(),
            'fields_of_study': set(),
            'highest_degree': None
        }
        
        for edu in education_entries:
            if edu.get('institution_name'):
                stats['institutions'].add(edu['institution_name'])
            if edu.get('degree'):
                stats['degrees'].add(edu['degree'])
            if edu.get('field_of_study'):
                stats['fields_of_study'].add(edu['field_of_study'])
        
        # Convert sets to lists
        stats['institutions'] = list(stats['institutions'])
        stats['degrees'] = list(stats['degrees'])
        stats['fields_of_study'] = list(stats['fields_of_study'])
        
        return stats
