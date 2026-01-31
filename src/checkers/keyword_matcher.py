"""
Keyword Matching Scorer - Calculates CV-JD alignment percentage.
"""
from typing import Dict, List, Set
import re


class KeywordMatcher:
    """Calculate keyword match percentage between CV and JD."""
    
    def __init__(self, cv_text: str, jd_keywords: Dict[str, List[str]]):
        """
        Initialize keyword matcher.
        
        Args:
            cv_text: CV text content
            jd_keywords: Dict with keyword categories and lists
        """
        self.cv_text = cv_text.lower()
        self.jd_keywords = jd_keywords
        
    def calculate_match_percentage(self) -> Dict[str, any]:
        """
        Calculate keyword match percentage.
        
        Returns:
            Dict with match statistics
        """
        all_keywords = set()
        matched_keywords = set()
        missing_keywords = []
        
        # Collect all keywords from JD
        for category, keywords in self.jd_keywords.items():
            for keyword in keywords:
                if keyword:
                    keyword_lower = keyword.lower().strip()
                    all_keywords.add(keyword_lower)
        
        # Check which keywords are in CV
        for keyword in all_keywords:
            # Use word boundary matching for better accuracy
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, self.cv_text, re.IGNORECASE):
                matched_keywords.add(keyword)
            else:
                missing_keywords.append(keyword)
        
        # Calculate percentages by category
        category_matches = {}
        for category, keywords in self.jd_keywords.items():
            category_keywords = [k.lower().strip() for k in keywords if k]
            category_matched = sum(1 for kw in category_keywords 
                                  if re.search(r'\b' + re.escape(kw) + r'\b', 
                                              self.cv_text, re.IGNORECASE))
            total = len(category_keywords)
            category_matches[category] = {
                'matched': category_matched,
                'total': total,
                'percentage': (category_matched / total * 100) if total > 0 else 0
            }
        
        total_keywords = len(all_keywords)
        matched_count = len(matched_keywords)
        match_percentage = (matched_count / total_keywords * 100) if total_keywords > 0 else 0
        
        return {
            'total_keywords': total_keywords,
            'matched_keywords': matched_count,
            'missing_keywords': len(missing_keywords),
            'match_percentage': round(match_percentage, 1),
            'missing_keywords_list': missing_keywords[:20],  # Top 20 missing
            'category_breakdown': category_matches
        }
    
    def suggest_keyword_placements(self) -> List[Dict[str, str]]:
        """
        Suggest where to add missing keywords.
        
        Returns:
            List of suggestions with keyword and suggested section
        """
        suggestions = []
        analysis = self.calculate_match_percentage()
        
        # Identify CV sections
        cv_sections = {
            'summary': self._find_section('summary|professional summary|profile'),
            'experience': self._find_section('experience|work experience|employment'),
            'skills': self._find_section('skills|technical skills|competencies'),
            'education': self._find_section('education|qualifications')
        }
        
        for missing_kw in analysis['missing_keywords_list'][:10]:  # Top 10
            # Determine best section
            suggested_section = self._determine_best_section(missing_kw, cv_sections)
            suggestions.append({
                'keyword': missing_kw,
                'suggested_section': suggested_section,
                'priority': 'HIGH' if missing_kw in analysis.get('required_keywords', []) else 'MEDIUM'
            })
        
        return suggestions
    
    def _find_section(self, pattern: str) -> str:
        """Find section text matching pattern."""
        match = re.search(pattern, self.cv_text, re.IGNORECASE)
        if match:
            # Get text after section header
            start = match.end()
            # Find next section or end
            next_section = re.search(r'\n[A-Z][A-Z\s]+:', self.cv_text[start:], re.IGNORECASE)
            end = start + next_section.start() if next_section else len(self.cv_text)
            return self.cv_text[start:end]
        return ""
    
    def _determine_best_section(self, keyword: str, sections: Dict[str, str]) -> str:
        """Determine best section to add keyword."""
        # Check if it's a skill (technical term)
        technical_indicators = ['sql', 'python', 'java', 'tableau', 'aws', 'docker']
        if any(indicator in keyword.lower() for indicator in technical_indicators):
            return 'skills'
        
        # Check if it's an action/experience term
        action_indicators = ['led', 'managed', 'developed', 'implemented', 'designed']
        if any(indicator in keyword.lower() for indicator in action_indicators):
            return 'experience'
        
        # Default to skills
        return 'skills'
    
    def get_match_report(self) -> Dict:
        """
        Get comprehensive match report.
        
        Returns:
            Dict with full analysis
        """
        match_stats = self.calculate_match_percentage()
        suggestions = self.suggest_keyword_placements()
        
        return {
            **match_stats,
            'suggestions': suggestions,
            'grade': self._get_match_grade(match_stats['match_percentage'])
        }
    
    def _get_match_grade(self, percentage: float) -> str:
        """Get grade based on match percentage."""
        if percentage >= 90:
            return 'Excellent'
        elif percentage >= 80:
            return 'Good'
        elif percentage >= 70:
            return 'Acceptable'
        elif percentage >= 60:
            return 'Needs Improvement'
        else:
            return 'Poor'
