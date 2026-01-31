"""
Job Description Parser - Rule-based extraction of keywords and structure.
"""
import re
from collections import Counter
from typing import Dict, List, Optional, Set
import spacy


class JobDescriptionParser:
    """Parse job descriptions and extract structured information."""
    
    # Common skill patterns
    SKILL_PATTERNS = {
        'programming': r'\b(Python|Java|JavaScript|R|SQL|C\+\+|Scala|Ruby|Go|TypeScript)\b',
        'tools': r'\b(Tableau|Power BI|Excel|JIRA|Git|Docker|AWS|Azure|GCP|Kubernetes|Jenkins)\b',
        'frameworks': r'\b(React|Angular|Django|Flask|Pandas|NumPy|TensorFlow|PyTorch|Spark)\b',
        'databases': r'\b(PostgreSQL|MySQL|MongoDB|Redis|Cassandra|Oracle|Snowflake|Redshift)\b',
        'methodologies': r'\b(Agile|Scrum|Kanban|Waterfall|DevOps|CI/CD)\b',
    }
    
    # Experience patterns
    EXPERIENCE_PATTERN = r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)?'
    
    # Required vs preferred markers
    REQUIRED_MARKERS = ['required', 'must have', 'essential', 'mandatory', 'must', 'need']
    PREFERRED_MARKERS = ['preferred', 'nice to have', 'desirable', 'bonus', 'plus', 'advantage']
    
    def __init__(self, jd_text: str):
        """
        Initialize parser with job description text.
        
        Args:
            jd_text: Job description text
        """
        self.jd_text = jd_text
        self.jd_text_lower = jd_text.lower()
        
        # Try to load spaCy model, fallback to basic parsing if not available
        try:
            self.nlp = spacy.load('en_core_web_sm')
            self.doc = self.nlp(jd_text)
        except OSError:
            self.nlp = None
            self.doc = None
        
        self.keywords = {
            'required_skills': [],
            'preferred_skills': [],
            'tools_technologies': [],
            'soft_skills': [],
            'experience_requirements': [],
            'industry_domain': [],
            'company_values': [],
            'exact_phrases': []
        }
        self.structure = {
            'sections': [],
            'responsibilities': [],
            'requirements': []
        }
        
    def extract_job_title(self) -> str:
        """
        Extract job title - usually in first few sentences.
        
        Returns:
            Extracted job title
        """
        # Look for patterns like "We're hiring a [TITLE]" or "[TITLE] - [Company]"
        patterns = [
            r'hiring\s+(?:a|an)\s+([A-Z][a-zA-Z\s]+?)(?:\s+at|\s+to|\.|,)',
            r'^([A-Z][a-zA-Z\s]+?)\s*[-–]\s*[A-Z]',
            r'Position:\s*([A-Z][a-zA-Z\s]+)',
            r'Role:\s*([A-Z][a-zA-Z\s]+)',
            r'Job Title:\s*([A-Z][a-zA-Z\s]+)',
            r'Title:\s*([A-Z][a-zA-Z\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.jd_text, re.MULTILINE | re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Clean up title
                title = re.sub(r'\s+', ' ', title)
                if len(title.split()) <= 6:  # Reasonable title length
                    return title
        
        # Fallback: Look for capitalized phrases in first paragraph
        first_para = self.jd_text[:500]
        for sent in first_para.split('.'):
            words = sent.strip().split()
            if 2 <= len(words) <= 5 and all(w[0].isupper() for w in words if w and w[0].isalpha()):
                return ' '.join(words)
        
        return "Unknown Title"
    
    def extract_technical_skills(self) -> List[str]:
        """
        Extract technical skills using patterns.
        
        Returns:
            List of technical skills found
        """
        skills = set()
        
        for category, pattern in self.SKILL_PATTERNS.items():
            matches = re.finditer(pattern, self.jd_text, re.IGNORECASE)
            for match in matches:
                skills.add(match.group(0))
        
        return sorted(list(skills))
    
    def extract_required_vs_preferred(self) -> Dict[str, List[str]]:
        """
        Separate required from preferred skills.
        
        Returns:
            Dict with 'required' and 'preferred' lists
        """
        required_section = ""
        preferred_section = ""
        
        # Split JD into sections
        text_lower = self.jd_text_lower
        
        # Find required skills section
        for marker in self.REQUIRED_MARKERS:
            if marker in text_lower:
                start = text_lower.index(marker)
                # Get next 500 chars or until next major section
                end = min(start + 500, len(text_lower))
                required_section += self.jd_text[start:end]
        
        # Find preferred skills section
        for marker in self.PREFERRED_MARKERS:
            if marker in text_lower:
                start = text_lower.index(marker)
                end = min(start + 500, len(text_lower))
                preferred_section += self.jd_text[start:end]
        
        return {
            'required': self._extract_bullets(required_section),
            'preferred': self._extract_bullets(preferred_section)
        }
    
    def _extract_bullets(self, text: str) -> List[str]:
        """
        Extract bullet points from text.
        
        Args:
            text: Text to extract bullets from
            
        Returns:
            List of bullet point texts
        """
        bullets = []
        # Common bullet patterns
        patterns = [
            r'[•\-\*]\s*(.+?)(?=\n|$)',
            r'\d+\.\s*(.+?)(?=\n|$)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            bullets.extend([m.group(1).strip() for m in matches])
        
        return bullets
    
    def extract_verbatim_phrases(self, min_length: int = 10, max_length: int = 30) -> List[str]:
        """
        Extract important phrases for exact matching.
        Target: Complete, meaningful phrases of 10-30 words.
        
        Args:
            min_length: Minimum words in phrase
            max_length: Maximum words in phrase
            
        Returns:
            List of verbatim phrases
        """
        phrases = []
        
        # Look for sentences containing key skill indicators
        skill_indicators = [
            'ability to', 'experience with', 'proficient in', 
            'knowledge of', 'skilled in', 'expertise in',
            'strong skills', 'demonstrated experience', 'proven ability'
        ]
        
        # Split into sentences
        sentences = re.split(r'[.!?]\s+', self.jd_text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
                
            word_count = len(sent.split())
            
            # Keep sentences that are the right length and contain skills
            if min_length <= word_count <= max_length:
                sent_lower = sent.lower()
                if any(indicator in sent_lower for indicator in skill_indicators):
                    phrases.append(sent)
        
        return phrases[:10]  # Limit to top 10 phrases
    
    def extract_company_values(self) -> List[str]:
        """
        Extract stated company values.
        
        Returns:
            List of company values
        """
        values = []
        
        # Common value section markers
        value_markers = [
            'our values', 'company values', 'core values',
            'we believe', 'our culture', 'values we'
        ]
        
        text_lower = self.jd_text_lower
        
        for marker in value_markers:
            if marker in text_lower:
                start = text_lower.index(marker)
                section = self.jd_text[start:start+500]
                
                # Extract capitalized words (often values)
                value_words = re.findall(r'\b([A-Z][a-z]+)\b', section)
                values.extend(value_words[:5])  # Limit to first 5
        
        return list(set(values))  # Remove duplicates
    
    def analyze_structure(self) -> Dict[str, List[str]]:
        """
        Analyze JD structure to identify sections.
        Returns section headers for CV mirroring.
        
        Returns:
            Dict with sections, responsibilities, requirements
        """
        structure = {
            'sections': [],
            'responsibilities': [],
            'requirements': []
        }
        
        # Find section headers (usually bold, capitalized, or followed by bullets)
        header_patterns = [
            r'^([A-Z][A-Z\s]+):?$',  # ALL CAPS headers
            r'^([A-Z][a-z\s]+):$',   # Title Case headers
            r'^\*\*([^*]+)\*\*',     # Markdown bold
        ]
        
        lines = self.jd_text.split('\n')
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            for pattern in header_patterns:
                match = re.match(pattern, line_stripped)
                if match:
                    header = match.group(1).strip()
                    structure['sections'].append(header)
                    
                    # Check if it's a responsibilities or requirements section
                    header_lower = header.lower()
                    if 'responsibilit' in header_lower or 'what you' in header_lower:
                        # Get bullets under this section
                        bullets = []
                        for j in range(i+1, min(i+20, len(lines))):
                            bullet_match = re.match(r'[•\-\*]\s*(.+)', lines[j].strip())
                            if bullet_match:
                                bullets.append(bullet_match.group(1).strip())
                            elif lines[j].strip() and not re.match(r'^[A-Z]', lines[j].strip()):
                                break
                        structure['responsibilities'].extend(bullets)
                    elif 'requirement' in header_lower or 'about you' in header_lower or 'qualification' in header_lower:
                        bullets = []
                        for j in range(i+1, min(i+20, len(lines))):
                            bullet_match = re.match(r'[•\-\*]\s*(.+)', lines[j].strip())
                            if bullet_match:
                                bullets.append(bullet_match.group(1).strip())
                            elif lines[j].strip() and not re.match(r'^[A-Z]', lines[j].strip()):
                                break
                        structure['requirements'].extend(bullets)
        
        return structure
    
    def calculate_keyword_density(self) -> List[tuple]:
        """
        Calculate frequency of important terms.
        
        Returns:
            List of (word, frequency) tuples, sorted by frequency
        """
        if self.doc:
            # Use spaCy if available
            words = [token.text.lower() for token in self.doc 
                    if not token.is_stop and token.is_alpha and len(token.text) > 3]
        else:
            # Fallback to basic word extraction
            words = re.findall(r'\b[a-z]{4,}\b', self.jd_text_lower)
            # Remove common stop words
            stop_words = {'that', 'this', 'with', 'from', 'have', 'will', 'would', 'could', 'should'}
            words = [w for w in words if w not in stop_words]
        
        return Counter(words).most_common(20)
    
    def extract_experience_requirements(self) -> List[str]:
        """
        Extract experience requirements (years, domains).
        
        Returns:
            List of experience requirement strings
        """
        requirements = []
        
        # Find years of experience
        exp_matches = re.finditer(self.EXPERIENCE_PATTERN, self.jd_text, re.IGNORECASE)
        for match in exp_matches:
            requirements.append(match.group(0))
        
        # Find domain-specific experience
        domain_patterns = [
            r'experience\s+in\s+([A-Z][a-z\s]+)',
            r'background\s+in\s+([A-Z][a-z\s]+)',
        ]
        
        for pattern in domain_patterns:
            matches = re.finditer(pattern, self.jd_text, re.IGNORECASE)
            for match in matches:
                requirements.append(match.group(0))
        
        return list(set(requirements))
    
    def extract_all(self) -> Dict:
        """
        Run all extraction methods and return complete analysis.
        
        Returns:
            Dict with all extracted information
        """
        required_preferred = self.extract_required_vs_preferred()
        
        return {
            'job_title': self.extract_job_title(),
            'technical_skills': self.extract_technical_skills(),
            'required_skills': required_preferred['required'],
            'preferred_skills': required_preferred['preferred'],
            'tools_technologies': self.extract_technical_skills(),  # Can be refined
            'verbatim_phrases': self.extract_verbatim_phrases(),
            'company_values': self.extract_company_values(),
            'structure': self.analyze_structure(),
            'keyword_density': self.calculate_keyword_density(),
            'experience_requirements': self.extract_experience_requirements()
        }
    
    def export_keyword_checklist(self) -> Dict[str, List[str]]:
        """
        Export keywords organized by category for checklist.
        
        Returns:
            Dict with categories and keywords
        """
        analysis = self.extract_all()
        
        return {
            'Required Skills': analysis['required_skills'],
            'Preferred Skills': analysis['preferred_skills'],
            'Technical Skills': analysis['technical_skills'],
            'Tools & Technologies': analysis['tools_technologies'],
            'Company Values': analysis['company_values'],
            'Key Phrases': analysis['verbatim_phrases'][:5]  # Top 5
        }
