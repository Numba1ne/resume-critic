"""
JD structure analysis for CV mirroring.
"""
import re
from typing import Dict, List


class StructureAnalyzer:
    """Analyze job description structure for CV mirroring."""
    
    def __init__(self, jd_text: str):
        """
        Initialize structure analyzer.
        
        Args:
            jd_text: Job description text
        """
        self.jd_text = jd_text
        self.lines = jd_text.split('\n')
    
    def identify_sections(self) -> List[Dict[str, any]]:
        """
        Identify major sections in JD.
        
        Returns:
            List of section dicts with name, start_line, end_line
        """
        sections = []
        current_section = None
        
        header_patterns = [
            r'^([A-Z][A-Z\s]+):?$',  # ALL CAPS
            r'^([A-Z][a-z\s]+):$',   # Title Case
            r'^\*\*([^*]+)\*\*',     # Markdown
        ]
        
        for i, line in enumerate(self.lines):
            line_stripped = line.strip()
            
            for pattern in header_patterns:
                match = re.match(pattern, line_stripped)
                if match:
                    if current_section:
                        current_section['end_line'] = i - 1
                        sections.append(current_section)
                    
                    current_section = {
                        'name': match.group(1).strip(),
                        'start_line': i,
                        'end_line': len(self.lines) - 1,
                        'content': []
                    }
                    break
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def extract_responsibilities(self) -> List[str]:
        """
        Extract responsibility bullets.
        
        Returns:
            List of responsibility descriptions
        """
        responsibilities = []
        in_responsibilities_section = False
        
        responsibility_markers = [
            'responsibilities', 'what you', 'key responsibilities',
            'you will', 'duties', 'role includes'
        ]
        
        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            
            # Check if we're entering responsibilities section
            if any(marker in line_lower for marker in responsibility_markers):
                in_responsibilities_section = True
                continue
            
            # Check if we're leaving responsibilities section
            if in_responsibilities_section:
                if re.match(r'^[A-Z][A-Z\s]+:', line.strip()):
                    # New section header
                    if 'responsibilit' not in line_lower:
                        in_responsibilities_section = False
                        continue
                
                # Extract bullets
                bullet_match = re.match(r'[•\-\*]\s*(.+)', line.strip())
                if bullet_match:
                    responsibilities.append(bullet_match.group(1).strip())
        
        return responsibilities
    
    def extract_requirements(self) -> List[str]:
        """
        Extract requirement bullets.
        
        Returns:
            List of requirement descriptions
        """
        requirements = []
        in_requirements_section = False
        
        requirement_markers = [
            'requirements', 'about you', 'qualifications',
            'must have', 'essential', 'required'
        ]
        
        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            
            # Check if we're entering requirements section
            if any(marker in line_lower for marker in requirement_markers):
                in_requirements_section = True
                continue
            
            # Check if we're leaving requirements section
            if in_requirements_section:
                if re.match(r'^[A-Z][A-Z\s]+:', line.strip()):
                    # New section header
                    if not any(marker in line_lower for marker in requirement_markers):
                        in_requirements_section = False
                        continue
                
                # Extract bullets
                bullet_match = re.match(r'[•\-\*]\s*(.+)', line.strip())
                if bullet_match:
                    requirements.append(bullet_match.group(1).strip())
        
        return requirements
    
    def get_structure_for_mirroring(self) -> Dict[str, List[str]]:
        """
        Get structure organized for CV mirroring.
        
        Returns:
            Dict with sections organized by type
        """
        sections = self.identify_sections()
        
        structure = {
            'main_sections': [s['name'] for s in sections],
            'responsibilities': self.extract_responsibilities(),
            'requirements': self.extract_requirements()
        }
        
        return structure
