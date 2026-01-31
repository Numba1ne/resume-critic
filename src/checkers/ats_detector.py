"""
ATS System Detector - Identifies ATS systems and provides optimization tips.
"""
import yaml
import os
import re
from typing import Dict, Optional, List


class ATSSystemDetector:
    """Detects ATS system and provides specific guidance."""
    
    ATS_SIGNATURES = {
        'greenhouse': {
            'url_patterns': ['greenhouse.io', 'boards.greenhouse.io'],
            'html_signatures': ['data-greenhouse', 'greenhouse'],
            'focus': 'Keyword matching + scorecard alignment',
            'tips': [
                'Role title matches highly weighted',
                'Answer knockout questions carefully',
                'Keywords are heavily weighted'
            ]
        },
        'workable': {
            'url_patterns': ['workable.com', 'apply.workable.com'],
            'html_signatures': ['workable-app', 'workable'],
            'focus': 'Skills matching + disqualification questions',
            'tips': [
                'Watch for disqualification questions',
                'Parses .docx very well',
                'Skills matching is primary scoring'
            ]
        },
        'lever': {
            'url_patterns': ['lever.co', 'jobs.lever.co'],
            'html_signatures': ['lever-form', 'lever'],
            'focus': 'Experience duration + cover letters',
            'tips': [
                'State years of experience clearly',
                'Cover letters surfaced to recruiters',
                'Write detailed cover letter'
            ]
        },
        'ashby': {
            'url_patterns': ['ashbyhq.com', 'jobs.ashbyhq.com'],
            'html_signatures': ['ashby-job', 'ashby'],
            'focus': 'Modern, similar to Greenhouse',
            'tips': [
                'Treat similar to Greenhouse',
                'Strong keyword matching'
            ]
        },
        'taleo': {
            'url_patterns': ['taleo.net', 'taleo.com'],
            'html_signatures': ['taleo'],
            'focus': 'Strict keyword matching',
            'tips': [
                'Older system, very keyword-focused',
                'Use exact terminology',
                'Be thorough with all fields'
            ]
        },
        'workday': {
            'url_patterns': ['myworkday.com', 'workday.com'],
            'html_signatures': ['workday'],
            'focus': 'Enterprise, keyword-focused',
            'tips': [
                'Very keyword-driven',
                'Complete all optional fields',
                'Use exact matches'
            ]
        }
    }
    
    def __init__(self, rules_path: Optional[str] = None):
        """
        Initialize ATS detector.
        
        Args:
            rules_path: Path to ATS rules YAML file
        """
        if rules_path is None:
            rules_path = os.path.join('data', 'ats_rules.yaml')
        
        try:
            with open(rules_path, 'r') as f:
                rules = yaml.safe_load(f)
                if 'ats_systems' in rules:
                    # Merge with default signatures
                    for system, config in rules['ats_systems'].items():
                        if system in self.ATS_SIGNATURES:
                            self.ATS_SIGNATURES[system].update(config)
        except FileNotFoundError:
            pass  # Use default signatures
    
    def detect_ats(self, application_url: Optional[str] = None,
                  html_content: Optional[str] = None) -> Optional[str]:
        """
        Identify ATS system from URL or page content.
        
        Args:
            application_url: Application URL
            html_content: HTML content of application page
            
        Returns:
            Detected ATS system name or None
        """
        # Check URL patterns
        if application_url:
            url_lower = application_url.lower()
            for system_name, config in self.ATS_SIGNATURES.items():
                for pattern in config.get('url_patterns', []):
                    if pattern in url_lower:
                        return system_name
        
        # Check HTML signatures
        if html_content:
            html_lower = html_content.lower()
            for system_name, config in self.ATS_SIGNATURES.items():
                for signature in config.get('html_signatures', []):
                    if signature in html_lower:
                        return system_name
        
        return None
    
    def get_optimization_tips(self, ats_name: str) -> Dict:
        """
        Return system-specific tips.
        
        Args:
            ats_name: ATS system name
            
        Returns:
            Dict with tips and focus areas
        """
        if ats_name not in self.ATS_SIGNATURES:
            return {
                'focus': 'General ATS optimization',
                'tips': [
                    'Use exact keywords from job description',
                    'Ensure .docx format',
                    'Single column layout',
                    'No graphics or tables'
                ]
            }
        
        config = self.ATS_SIGNATURES[ats_name]
        return {
            'focus': config.get('focus', 'General optimization'),
            'tips': config.get('tips', [])
        }
    
    def get_all_systems(self) -> List[str]:
        """
        Get list of all known ATS systems.
        
        Returns:
            List of ATS system names
        """
        return list(self.ATS_SIGNATURES.keys())
