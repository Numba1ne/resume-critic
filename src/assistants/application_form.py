"""
Application Form Assistant - Helps with application form fields.
"""
import yaml
import os
from typing import Dict, Optional
from src.parsers.jd_parser import JobDescriptionParser


class ApplicationFormAssistant:
    """Assists with application form fields."""
    
    def __init__(self, jd_parser: Optional[JobDescriptionParser] = None):
        """
        Initialize form assistant.
        
        Args:
            jd_parser: Optional JD parser for context
        """
        self.jd_parser = jd_parser
        self._load_salary_data()
    
    def _load_salary_data(self):
        """Load salary reference data."""
        salary_path = os.path.join('data', 'salary_reference.yaml')
        try:
            with open(salary_path, 'r') as f:
                self.salary_data = yaml.safe_load(f)
        except FileNotFoundError:
            self.salary_data = {}
    
    def generate_star_answer(self, question: str, user_experience: Dict) -> str:
        """
        Format answer using STAR method.
        
        Args:
            question: Competency question
            user_experience: User's experience dict with situation, task, action, result
            
        Returns:
            STAR-formatted answer
        """
        situation = user_experience.get('situation', 'In my previous role')
        task = user_experience.get('task', 'I was tasked with')
        action = user_experience.get('action', 'I took action to')
        result = user_experience.get('result', 'This resulted in positive outcomes')
        
        # Include JD keywords if parser available
        keywords = []
        if self.jd_parser:
            jd_analysis = self.jd_parser.extract_all()
            keywords = jd_analysis.get('technical_skills', [])[:3]
        
        # Build STAR answer
        answer = f"Situation: {situation}.\n\n"
        answer += f"Task: {task}.\n\n"
        answer += f"Action: {action}"
        if keywords:
            answer += f", utilizing {', '.join(keywords[:2])}"
        answer += f".\n\n"
        answer += f"Result: {result}."
        
        return answer
    
    def calculate_salary_range(self, role_level: str, location: str, 
                              country: str = 'uk') -> Dict[str, str]:
        """
        Calculate salary range recommendation.
        
        Args:
            role_level: Role level (junior_graduate, mid_level, senior, etc.)
            location: Location (london, other_uk, major_cities, etc.)
            country: Country ('uk' or 'us')
            
        Returns:
            Dict with salary range
        """
        country_key = f'{country}_data_analytics_2026'
        
        if country_key not in self.salary_data:
            return {'range': 'Not available', 'note': 'Salary data not found'}
        
        country_data = self.salary_data[country_key]
        
        if role_level not in country_data:
            return {'range': 'Not available', 'note': 'Role level not found'}
        
        role_data = country_data[role_level]
        
        if location in role_data:
            salary_range = role_data[location]
        elif 'london' in role_data or 'major_cities' in role_data:
            # Use first available location
            salary_range = list(role_data.values())[0]
        else:
            return {'range': 'Not available', 'note': 'Location not found'}
        
        return {
            'range': salary_range,
            'level': role_level,
            'location': location,
            'years_experience': role_data.get('years_experience', 'N/A')
        }
    
    def generate_hiring_message(self, company_name: str, 
                               key_skills: list,
                               jd_detail: Optional[str] = None) -> str:
        """
        Generate 200-300 word message for optional fields.
        
        Args:
            company_name: Company name
            key_skills: List of key skills to mention
            jd_detail: Specific JD detail to reference
            
        Returns:
            Generated message
        """
        message = f"I'm genuinely interested in {company_name}"
        
        if jd_detail:
            message += f" and {jd_detail.lower()}"
        message += ". "
        
        # Mention key skills
        if key_skills:
            skills_text = ', '.join(key_skills[:3])
            message += f"I bring strong expertise in {skills_text}, "
        
        # Reference specific JD detail
        if jd_detail:
            message += f"and I'm particularly excited about {jd_detail.lower()}. "
        
        # Confirm availability
        message += "I'm available to discuss how I can contribute to your team and would welcome the opportunity to speak further."
        
        # Ensure word count is reasonable
        words = message.split()
        if len(words) > 300:
            message = ' '.join(words[:300]) + "..."
        elif len(words) < 200:
            # Expand message
            message += " My experience aligns well with your requirements, and I'm confident I can make a meaningful contribution to your organization."
        
        return message
