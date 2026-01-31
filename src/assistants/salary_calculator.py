"""
Salary Calculator - Provides salary guidance based on role and location.
"""
import yaml
import os
from typing import Dict, Optional


class SalaryCalculator:
    """Calculate salary ranges based on role and location."""
    
    def __init__(self):
        """Initialize salary calculator."""
        self._load_salary_data()
    
    def _load_salary_data(self):
        """Load salary reference data."""
        salary_path = os.path.join('data', 'salary_reference.yaml')
        try:
            with open(salary_path, 'r') as f:
                self.salary_data = yaml.safe_load(f)
        except FileNotFoundError:
            self.salary_data = {}
    
    def get_salary_range(self, role_level: str, location: str, 
                        country: str = 'uk') -> Dict:
        """
        Get salary range for role level and location.
        
        Args:
            role_level: Role level (junior_graduate, mid_level, senior, etc.)
            location: Location (london, other_uk, major_cities, etc.)
            country: Country ('uk' or 'us')
            
        Returns:
            Dict with salary information
        """
        country_key = f'{country}_data_analytics_2026'
        
        if country_key not in self.salary_data:
            return {'error': 'Salary data not available for this country'}
        
        country_data = self.salary_data[country_key]
        
        if role_level not in country_data:
            return {'error': f'Role level "{role_level}" not found'}
        
        role_data = country_data[role_level]
        
        # Get salary for location
        if location in role_data:
            salary_range = role_data[location]
        elif country == 'uk' and 'london' in role_data:
            # Default to London for UK
            salary_range = role_data['london']
        elif country == 'us' and 'major_cities' in role_data:
            # Default to major cities for US
            salary_range = role_data['major_cities']
        else:
            # Use first available
            salary_range = list(role_data.values())[0] if role_data else 'Not available'
        
        return {
            'range': salary_range,
            'level': role_level,
            'location': location,
            'country': country,
            'years_experience': role_data.get('years_experience', 'N/A')
        }
    
    def suggest_salary_expectation(self, role_level: str, location: str,
                                   country: str = 'uk') -> str:
        """
        Suggest salary expectation text for application forms.
        
        Args:
            role_level: Role level
            location: Location
            country: Country
            
        Returns:
            Suggested salary expectation text
        """
        salary_info = self.get_salary_range(role_level, location, country)
        
        if 'error' in salary_info:
            return "Competitive, based on experience"
        
        range_str = salary_info['range']
        # Extract numbers from range
        import re
        numbers = re.findall(r'[\d,]+', range_str)
        
        if len(numbers) >= 2:
            # Use midpoint or upper range
            return f"£{numbers[1]}" if country == 'uk' else f"${numbers[1]}"
        elif len(numbers) == 1:
            return f"£{numbers[0]}" if country == 'uk' else f"${numbers[0]}"
        else:
            return "Competitive, based on experience"
