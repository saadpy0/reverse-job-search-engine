"""
Skill extraction and categorization for resume parsing.
Uses BERT and NLP techniques to identify technical skills with confidence scores.
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path
import numpy as np

# NLP libraries
try:
    import spacy
    from spacy.matcher import Matcher, PhraseMatcher
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

# BERT/Transformers
try:
    from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
    from transformers import AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from app.core.logging import get_logger
from config.settings import settings

logger = get_logger("skill_extractor")


class SkillExtractor:
    """Extract and categorize technical skills from resume text."""
    
    def __init__(self):
        """Initialize the skill extractor with models and skill databases."""
        self.skill_categories = {
            'programming_languages': set(),
            'frameworks': set(),
            'databases': set(),
            'cloud_platforms': set(),
            'tools': set(),
            'soft_skills': set(),
            'languages': set(),
            'certifications': set()
        }
        
        # Load skill databases
        self._load_skill_databases()
        
        # Initialize NLP models
        self._initialize_models()
        
        logger.info("SkillExtractor initialized successfully")
    
    def _load_skill_databases(self):
        """Load skill databases from JSON files."""
        skill_db_path = Path(__file__).parent / "data" / "skills"
        
        if not skill_db_path.exists():
            logger.warning(f"Skill database path not found: {skill_db_path}")
            self._load_default_skills()
            return
        
        try:
            for category in self.skill_categories.keys():
                db_file = skill_db_path / f"{category}.json"
                if db_file.exists():
                    with open(db_file, 'r') as f:
                        skills = json.load(f)
                        self.skill_categories[category] = set(skills)
                        logger.info(f"Loaded {len(skills)} skills for category: {category}")
                else:
                    logger.warning(f"Skill database file not found: {db_file}")
        except Exception as e:
            logger.error(f"Failed to load skill databases: {e}")
            self._load_default_skills()
    
    def _load_default_skills(self):
        """Load default skill sets if databases are not available."""
        default_skills = {
            'programming_languages': {
                'Python', 'JavaScript', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust',
                'Swift', 'Kotlin', 'TypeScript', 'Scala', 'R', 'MATLAB', 'Perl', 'Shell',
                'Bash', 'PowerShell', 'SQL', 'HTML', 'CSS', 'Dart', 'Elixir', 'Clojure'
            },
            'frameworks': {
                'React', 'Angular', 'Vue.js', 'Django', 'Flask', 'Spring', 'Express.js',
                'Laravel', 'Ruby on Rails', 'ASP.NET', 'FastAPI', 'Node.js', 'jQuery',
                'Bootstrap', 'Tailwind CSS', 'TensorFlow', 'PyTorch', 'Scikit-learn',
                'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Keras', 'Hadoop', 'Spark'
            },
            'databases': {
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle', 'SQL Server',
                'Cassandra', 'DynamoDB', 'Elasticsearch', 'Neo4j', 'InfluxDB', 'CouchDB',
                'MariaDB', 'Firebase', 'Supabase'
            },
            'cloud_platforms': {
                'AWS', 'Azure', 'Google Cloud', 'Heroku', 'DigitalOcean', 'Vercel',
                'Netlify', 'Firebase', 'Docker', 'Kubernetes', 'Terraform', 'Ansible',
                'Jenkins', 'GitHub Actions', 'GitLab CI', 'CircleCI'
            },
            'tools': {
                'Git', 'GitHub', 'GitLab', 'Bitbucket', 'Jira', 'Confluence', 'Slack',
                'Trello', 'Asana', 'Notion', 'Figma', 'Adobe Creative Suite', 'VS Code',
                'IntelliJ IDEA', 'Eclipse', 'Postman', 'Insomnia', 'Tableau', 'Power BI'
            },
            'soft_skills': {
                'Leadership', 'Communication', 'Teamwork', 'Problem Solving', 'Critical Thinking',
                'Time Management', 'Project Management', 'Agile', 'Scrum', 'Kanban',
                'Customer Service', 'Sales', 'Marketing', 'Research', 'Analysis',
                'Creativity', 'Adaptability', 'Collaboration', 'Presentation', 'Negotiation'
            }
        }
        
        for category, skills in default_skills.items():
            self.skill_categories[category] = skills
    
    def _initialize_models(self):
        """Initialize NLP models for skill extraction."""
        self.nlp = None
        self.matcher = None
        self.bert_ner = None
        
        if SPACY_AVAILABLE:
            try:
                # Load spaCy model
                self.nlp = spacy.load("en_core_web_sm")
                self.matcher = Matcher(self.nlp.vocab)
                self._setup_spacy_matchers()
                logger.info("spaCy models loaded successfully")
            except OSError:
                logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
        
        if TRANSFORMERS_AVAILABLE:
            try:
                # Initialize BERT NER pipeline for skill extraction
                model_name = "dslim/bert-base-NER"  # Named Entity Recognition model
                self.bert_ner = pipeline("ner", model=model_name, aggregation_strategy="simple")
                logger.info("BERT NER model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load BERT model: {e}")
    
    def _setup_spacy_matchers(self):
        """Set up spaCy matchers for skill detection."""
        if not self.nlp or not self.matcher:
            return
        
        # Create patterns for different skill categories
        for category, skills in self.skill_categories.items():
            if skills:
                patterns = []
                for skill in skills:
                    # Create pattern for exact match
                    patterns.append([{"LOWER": skill.lower()}])
                    # Create pattern for skill with common variations
                    patterns.append([{"LOWER": {"IN": [skill.lower(), skill.lower().replace(" ", "")]}}])
                
                self.matcher.add(category, patterns)
    
    def extract_skills(self, text: str) -> Dict[str, List[Dict]]:
        """
        Extract skills from resume text using multiple methods.
        
        Args:
            text: Resume text to analyze
            
        Returns:
            Dictionary with extracted skills by category
        """
        logger.info("Starting skill extraction")
        
        results = {
            'programming_languages': [],
            'frameworks': [],
            'databases': [],
            'cloud_platforms': [],
            'tools': [],
            'soft_skills': [],
            'languages': [],
            'certifications': []
        }
        
        # Method 1: Rule-based extraction with spaCy
        if self.nlp and self.matcher:
            spacy_skills = self._extract_skills_spacy(text)
            for category, skills in spacy_skills.items():
                results[category].extend(skills)
        
        # Method 2: BERT-based NER extraction
        if self.bert_ner:
            bert_skills = self._extract_skills_bert(text)
            for category, skills in bert_skills.items():
                results[category].extend(skills)
        
        # Method 3: Pattern-based extraction
        pattern_skills = self._extract_skills_patterns(text)
        for category, skills in pattern_skills.items():
            results[category].extend(skills)
        
        # Deduplicate and merge results
        final_results = {}
        for category, skills in results.items():
            final_results[category] = self._deduplicate_skills(skills)
        
        # Calculate overall statistics
        total_skills = sum(len(skills) for skills in final_results.values())
        logger.info(f"Extracted {total_skills} unique skills across all categories")
        
        return final_results
    
    def _extract_skills_spacy(self, text: str) -> Dict[str, List[Dict]]:
        """Extract skills using spaCy NLP."""
        if not self.nlp or not self.matcher:
            return {}
        
        doc = self.nlp(text)
        matches = self.matcher(doc)
        
        results = {category: [] for category in self.skill_categories.keys()}
        
        for match_id, start, end in matches:
            category = self.nlp.vocab.strings[match_id]
            skill_text = doc[start:end].text
            
            # Calculate confidence based on context
            confidence = self._calculate_skill_confidence(doc, start, end, skill_text)
            
            skill_info = {
                'skill_name': skill_text,
                'category': category,
                'confidence': confidence,
                'extraction_method': 'spacy',
                'context': self._get_skill_context(doc, start, end)
            }
            
            results[category].append(skill_info)
        
        return results
    
    def _extract_skills_bert(self, text: str) -> Dict[str, List[Dict]]:
        """Extract skills using BERT NER."""
        if not self.bert_ner:
            return {}
        
        try:
            # Split text into chunks if too long
            max_length = 512
            chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            
            results = {category: [] for category in self.skill_categories.keys()}
            
            for chunk in chunks:
                entities = self.bert_ner(chunk)
                
                for entity in entities:
                    if entity['score'] > 0.7:  # Confidence threshold
                        skill_text = entity['word']
                        category = self._categorize_skill(skill_text)
                        
                        if category:
                            skill_info = {
                                'skill_name': skill_text,
                                'category': category,
                                'confidence': entity['score'],
                                'extraction_method': 'bert',
                                'context': chunk[max(0, entity['start']-50):entity['end']+50]
                            }
                            
                            results[category].append(skill_info)
            
            return results
            
        except Exception as e:
            logger.error(f"BERT skill extraction failed: {e}")
            return {}
    
    def _extract_skills_patterns(self, text: str) -> Dict[str, List[Dict]]:
        """Extract skills using regex patterns."""
        results = {category: [] for category in self.skill_categories.keys()}
        
        # Common patterns for skill mentions
        patterns = {
            'programming_languages': [
                r'\b(Python|JavaScript|Java|C\+\+|C#|PHP|Ruby|Go|Rust|Swift|Kotlin|TypeScript|Scala|R|MATLAB|Perl|SQL|HTML|CSS)\b',
                r'\b(HTML5|CSS3|ES6|ES7|ES8|ES9|ES10|ES11|ES12)\b'
            ],
            'frameworks': [
                r'\b(React|Angular|Vue\.js|Django|Flask|Spring|Express\.js|Laravel|Ruby on Rails|ASP\.NET|FastAPI|Node\.js)\b',
                r'\b(TensorFlow|PyTorch|Scikit-learn|Pandas|NumPy|Matplotlib|Seaborn|Keras|Hadoop|Spark)\b'
            ],
            'databases': [
                r'\b(MySQL|PostgreSQL|MongoDB|Redis|SQLite|Oracle|SQL Server|Cassandra|DynamoDB|Elasticsearch|Neo4j)\b'
            ],
            'cloud_platforms': [
                r'\b(AWS|Azure|Google Cloud|Heroku|DigitalOcean|Docker|Kubernetes|Terraform|Ansible|Jenkins)\b'
            ]
        }
        
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    skill_text = match.group()
                    confidence = 0.8  # High confidence for pattern matches
                    
                    skill_info = {
                        'skill_name': skill_text,
                        'category': category,
                        'confidence': confidence,
                        'extraction_method': 'pattern',
                        'context': text[max(0, match.start()-50):match.end()+50]
                    }
                    
                    results[category].append(skill_info)
        
        return results
    
    def _categorize_skill(self, skill_name: str) -> Optional[str]:
        """Categorize a skill based on the skill databases."""
        skill_lower = skill_name.lower()
        
        for category, skills in self.skill_categories.items():
            if any(skill.lower() in skill_lower or skill_lower in skill.lower() for skill in skills):
                return category
        
        return None
    
    def _calculate_skill_confidence(self, doc, start: int, end: int, skill_text: str) -> float:
        """Calculate confidence score for a detected skill."""
        confidence = 0.5  # Base confidence
        
        # Check if skill is in our database
        if self._categorize_skill(skill_text):
            confidence += 0.3
        
        # Check context (nearby words)
        context_start = max(0, start - 5)
        context_end = min(len(doc), end + 5)
        context = doc[context_start:context_end].text.lower()
        
        # Boost confidence for certain context words
        positive_words = ['experience', 'proficient', 'expert', 'skilled', 'knowledge', 'familiar']
        negative_words = ['learning', 'beginner', 'basic', 'introductory']
        
        for word in positive_words:
            if word in context:
                confidence += 0.1
        
        for word in negative_words:
            if word in context:
                confidence -= 0.1
        
        return min(1.0, max(0.0, confidence))
    
    def _get_skill_context(self, doc, start: int, end: int) -> str:
        """Get context around a detected skill."""
        context_start = max(0, start - 10)
        context_end = min(len(doc), end + 10)
        return doc[context_start:context_end].text
    
    def _deduplicate_skills(self, skills: List[Dict]) -> List[Dict]:
        """Remove duplicate skills and merge confidence scores."""
        skill_map = {}
        
        for skill in skills:
            skill_name = skill['skill_name'].lower()
            
            if skill_name in skill_map:
                # Merge with existing skill
                existing = skill_map[skill_name]
                existing['confidence'] = max(existing['confidence'], skill['confidence'])
                if skill['confidence'] > existing['confidence']:
                    existing['extraction_method'] = skill['extraction_method']
                    existing['context'] = skill['context']
            else:
                skill_map[skill_name] = skill.copy()
        
        return list(skill_map.values())
    
    def get_skill_statistics(self, extracted_skills: Dict[str, List[Dict]]) -> Dict[str, any]:
        """Get statistics about extracted skills."""
        stats = {
            'total_skills': 0,
            'skills_by_category': {},
            'average_confidence': 0.0,
            'extraction_methods': {},
            'top_skills': []
        }
        
        all_skills = []
        total_confidence = 0.0
        
        for category, skills in extracted_skills.items():
            stats['skills_by_category'][category] = len(skills)
            stats['total_skills'] += len(skills)
            
            for skill in skills:
                all_skills.append(skill)
                total_confidence += skill['confidence']
                
                method = skill['extraction_method']
                stats['extraction_methods'][method] = stats['extraction_methods'].get(method, 0) + 1
        
        if all_skills:
            stats['average_confidence'] = total_confidence / len(all_skills)
            
            # Get top skills by confidence
            sorted_skills = sorted(all_skills, key=lambda x: x['confidence'], reverse=True)
            stats['top_skills'] = sorted_skills[:10]
        
        return stats
