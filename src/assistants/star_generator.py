"""
STAR Answer Generator - Generates STAR format answers for competency questions.
"""
from typing import Dict, List, Optional
from src.parsers.jd_parser import JobDescriptionParser


class STARGenerator:
    """Generate STAR format answers."""
    
    def __init__(self, jd_parser: Optional[JobDescriptionParser] = None):
        """
        Initialize STAR generator.
        
        Args:
            jd_parser: Optional JD parser for context
        """
        self.jd_parser = jd_parser
    
    def generate_star_answer(self, question: str, 
                           situation: str,
                           task: str,
                           action: str,
                           result: str) -> str:
        """
        Generate STAR answer from components.
        
        Args:
            question: The competency question
            situation: Situation description
            task: Task description
            action: Action taken
            result: Result achieved
            
        Returns:
            STAR-formatted answer
        """
        # Extract keywords from JD if available
        keywords = []
        if self.jd_parser:
            jd_analysis = self.jd_parser.extract_all()
            keywords = jd_analysis.get('technical_skills', [])[:2]
        
        # Build answer
        answer = f"Situation: {situation}\n\n"
        answer += f"Task: {task}\n\n"
        answer += f"Action: {action}"
        if keywords:
            answer += f" This involved using {keywords[0]}"
            if len(keywords) > 1:
                answer += f" and {keywords[1]}"
        answer += ".\n\n"
        answer += f"Result: {result}"
        
        return answer
    
    def generate_from_template(self, question: str, 
                              experience_type: str = 'project') -> str:
        """
        Generate STAR answer from template.
        
        Args:
            question: Competency question
            experience_type: Type of experience (project, leadership, problem-solving)
            
        Returns:
            STAR-formatted answer
        """
        templates = {
            'project': {
                'situation': 'I was working on a critical project that required',
                'task': 'My task was to',
                'action': 'I took the following actions',
                'result': 'This resulted in'
            },
            'leadership': {
                'situation': 'I was leading a team when',
                'task': 'I needed to',
                'action': 'I implemented',
                'result': 'The outcome was'
            },
            'problem-solving': {
                'situation': 'I encountered a challenging problem where',
                'task': 'I had to',
                'action': 'I solved this by',
                'result': 'The solution led to'
            }
        }
        
        template = templates.get(experience_type, templates['project'])
        
        return self.generate_star_answer(
            question,
            template['situation'],
            template['task'],
            template['action'],
            template['result']
        )
