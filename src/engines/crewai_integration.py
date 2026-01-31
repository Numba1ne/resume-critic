"""
CrewAI Integration - Wrapper for existing CrewAI workflow.
"""
from typing import Dict, Optional
import sys
import os

# Add parent directory to path to import existing modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from tasks import run_resume_optimization_crew
    from utils import parse_resume_to_schema
    from pdf_generator import generate_resume_pdf
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False


class CrewAIIntegration:
    """Integration wrapper for CrewAI resume optimization."""
    
    def __init__(self):
        """Initialize CrewAI integration."""
        if not CREWAI_AVAILABLE:
            raise ImportError("CrewAI modules not available. Ensure agents.py, tasks.py, and utils.py are in the project root.")
    
    def optimize_resume(self, resume_text: str, job_description: str) -> Dict:
        """
        Run CrewAI optimization on resume.
        
        Args:
            resume_text: Resume text content
            job_description: Job description text
            
        Returns:
            Dict with optimized resume data
        """
        # Run CrewAI crew
        result = run_resume_optimization_crew(resume_text, job_description)
        
        # Parse result
        rewritten_text = result.get('rewritten_resume', '')
        analysis = result.get('analysis', {})
        
        # Parse to schema
        try:
            resume_schema = parse_resume_to_schema(rewritten_text)
        except Exception as e:
            raise ValueError(f"Failed to parse CrewAI output: {str(e)}")
        
        return {
            'resume_schema': resume_schema,
            'analysis': analysis,
            'rewritten_text': rewritten_text
        }
    
    def generate_pdf(self, resume_schema) -> bytes:
        """
        Generate PDF from CrewAI-optimized resume.
        
        Args:
            resume_schema: ResumeSchema object
            
        Returns:
            PDF bytes
        """
        return generate_resume_pdf(resume_schema)
