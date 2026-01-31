"""
Checklist System - Pre-application and submission checklists.
"""
from typing import Dict, List


class ChecklistSystem:
    """Manages pre-application and submission checklists."""
    
    PRE_APPLICATION_CHECKLIST = [
        {
            'category': 'CV PREPARATION',
            'items': [
                {'id': 'cv_title_match', 'task': 'Match CV title to exact job title', 'priority': 'HIGH'},
                {'id': 'cv_verbatim_keywords', 'task': 'Copy verbatim keywords from JD', 'priority': 'HIGH'},
                {'id': 'cv_mirror_structure', 'task': 'Mirror JD structure in experience section', 'priority': 'HIGH'},
                {'id': 'cv_required_skills', 'task': 'Include all required skills explicitly', 'priority': 'HIGH'},
                {'id': 'cv_quantifiable', 'task': 'Add quantifiable achievements', 'priority': 'HIGH'},
                {'id': 'cv_acronyms_full', 'task': 'Include both acronyms AND full terms', 'priority': 'MEDIUM'},
                {'id': 'cv_values_alignment', 'task': 'Add Values Alignment section (if company lists values)', 'priority': 'MEDIUM'},
                {'id': 'cv_location_logistics', 'task': 'Confirm location/logistics in Additional Info', 'priority': 'MEDIUM'},
                {'id': 'cv_ats_formatting', 'task': 'Check ATS formatting', 'priority': 'HIGH'},
                {'id': 'cv_proofread', 'task': 'Proofread for errors', 'priority': 'HIGH'}
            ]
        },
        {
            'category': 'COVER LETTER PREPARATION',
            'items': [
                {'id': 'cl_hook', 'task': 'Paragraph 1: Hook with company-specific enthusiasm', 'priority': 'HIGH'},
                {'id': 'cl_technical_match', 'task': 'Paragraph 2: List technical skills using their terms', 'priority': 'HIGH'},
                {'id': 'cl_experience_story', 'task': 'Paragraph 3: Give relevant experience example with numbers', 'priority': 'HIGH'},
                {'id': 'cl_why_role', 'task': 'Paragraph 4: Explain why THIS role excites you', 'priority': 'MEDIUM'},
                {'id': 'cl_close', 'task': 'Paragraph 5: Confirm logistics and close', 'priority': 'MEDIUM'},
                {'id': 'cl_word_count', 'task': 'Keep under 400 words', 'priority': 'MEDIUM'},
                {'id': 'cl_tone', 'task': 'Use human tone (contractions, conversational)', 'priority': 'HIGH'},
                {'id': 'cl_proofread', 'task': 'Proofread', 'priority': 'HIGH'}
            ]
        }
    ]
    
    FINAL_SUBMISSION_CHECKLIST = [
        {'id': 'final_cv_title', 'task': 'CV title matches or closely aligns with job title', 'priority': 'HIGH'},
        {'id': 'final_verbatim_keywords', 'task': 'Verbatim keywords from JD included in CV', 'priority': 'HIGH'},
        {'id': 'final_mirror_structure', 'task': 'Experience section mirrors JD requirements structure', 'priority': 'HIGH'},
        {'id': 'final_quantifiable', 'task': 'Quantifiable achievements included (%, £, numbers)', 'priority': 'HIGH'},
        {'id': 'final_ats_format', 'task': 'CV in ATS-friendly format (.docx, single column)', 'priority': 'HIGH'},
        {'id': 'final_location_logistics', 'task': 'Location/logistics addressed in CV', 'priority': 'MEDIUM'},
        {'id': 'final_cl_company_interest', 'task': 'Cover letter shows genuine interest in THIS company', 'priority': 'HIGH'},
        {'id': 'final_cl_terminology', 'task': "Cover letter uses company's exact technical terminology", 'priority': 'HIGH'},
        {'id': 'final_cl_values', 'task': 'Company values aligned with (if mentioned in JD)', 'priority': 'MEDIUM'},
        {'id': 'final_required_fields', 'task': 'All required application fields completed', 'priority': 'HIGH'},
        {'id': 'final_salary_expectations', 'task': 'Salary expectations researched and reasonable', 'priority': 'MEDIUM'},
        {'id': 'final_notice_period', 'task': 'Notice period accurately stated', 'priority': 'MEDIUM'},
        {'id': 'final_right_to_work', 'task': 'Right to work confirmed (if asked)', 'priority': 'MEDIUM'},
        {'id': 'final_file_names', 'task': 'File names are professional', 'priority': 'MEDIUM'},
        {'id': 'final_proofread', 'task': 'Final proofread completed - no errors', 'priority': 'HIGH'}
    ]
    
    def __init__(self):
        """Initialize checklist system."""
        self.progress = {
            'pre_application': {},
            'final_submission': {}
        }
    
    def get_pre_application_checklist(self) -> List[Dict]:
        """
        Get pre-application checklist.
        
        Returns:
            List of checklist categories with items
        """
        return self.PRE_APPLICATION_CHECKLIST
    
    def get_final_submission_checklist(self) -> List[Dict]:
        """
        Get final submission checklist.
        
        Returns:
            List of checklist items
        """
        return self.FINAL_SUBMISSION_CHECKLIST
    
    def mark_complete(self, checklist_type: str, item_id: str):
        """
        Mark checklist item as complete.
        
        Args:
            checklist_type: 'pre_application' or 'final_submission'
            item_id: Item ID
        """
        if checklist_type not in self.progress:
            self.progress[checklist_type] = {}
        
        self.progress[checklist_type][item_id] = True
    
    def mark_incomplete(self, checklist_type: str, item_id: str):
        """
        Mark checklist item as incomplete.
        
        Args:
            checklist_type: 'pre_application' or 'final_submission'
            item_id: Item ID
        """
        if checklist_type in self.progress and item_id in self.progress[checklist_type]:
            del self.progress[checklist_type][item_id]
    
    def get_completion_percentage(self, checklist_type: str) -> float:
        """
        Calculate checklist completion percentage.
        
        Args:
            checklist_type: 'pre_application' or 'final_submission'
            
        Returns:
            Completion percentage (0-100)
        """
        if checklist_type == 'pre_application':
            total_items = sum(len(cat['items']) for cat in self.PRE_APPLICATION_CHECKLIST)
        elif checklist_type == 'final_submission':
            total_items = len(self.FINAL_SUBMISSION_CHECKLIST)
        else:
            return 0.0
        
        completed = len(self.progress.get(checklist_type, {}))
        return (completed / total_items * 100) if total_items > 0 else 0.0
    
    def get_all_completion_status(self) -> Dict[str, float]:
        """
        Get completion status for all checklists.
        
        Returns:
            Dict with completion percentages
        """
        return {
            'pre_application': self.get_completion_percentage('pre_application'),
            'final_submission': self.get_completion_percentage('final_submission')
        }
    
    def reset_checklist(self, checklist_type: str):
        """
        Reset checklist progress.
        
        Args:
            checklist_type: 'pre_application' or 'final_submission'
        """
        if checklist_type in self.progress:
            self.progress[checklist_type] = {}
