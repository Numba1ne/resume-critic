"""
Application Tracker - Tracks job applications.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from src.utils.database import Database


class ApplicationTracker:
    """Tracks all job applications."""
    
    def __init__(self, database_path: str = 'data/applications.db'):
        """
        Initialize application tracker.
        
        Args:
            database_path: Path to database file
        """
        self.db = Database(database_path)
    
    def add_application(self, company_name: str, job_title: str,
                      status: str = 'Applied',
                      cv_version_path: Optional[str] = None,
                      cover_letter_included: bool = False,
                      notes: Optional[str] = None,
                      **kwargs) -> int:
        """
        Add new application.
        
        Args:
            company_name: Company name
            job_title: Job title
            status: Application status
            cv_version_path: Path to CV version used
            cover_letter_included: Whether cover letter was included
            notes: Additional notes
            **kwargs: Additional fields
            
        Returns:
            Application ID
        """
        app_id = self.db.add_application(
            company_name,
            job_title,
            status=status,
            notes=notes,
            cover_letter_included=cover_letter_included,
            **kwargs
        )
        
        # Update CV version path if provided
        if cv_version_path:
            self.db.update_application(app_id, cv_version_path=cv_version_path)
        
        return app_id
    
    def update_status(self, application_id: int, new_status: str):
        """
        Update application status.
        
        Args:
            application_id: Application ID
            new_status: New status
        """
        self.db.update_application(application_id, status=new_status)
    
    def schedule_followup(self, application_id: int, followup_date: datetime.date):
        """
        Set reminder for follow-up.
        
        Args:
            application_id: Application ID
            followup_date: Follow-up date
        """
        self.db.update_application(application_id, followup_date=followup_date)
    
    def get_applications_summary(self) -> Dict:
        """
        Get application statistics.
        
        Returns:
            Dict with statistics
        """
        return self.db.get_application_statistics()
    
    def get_applications(self, status: Optional[str] = None,
                        limit: Optional[int] = None) -> List[Dict]:
        """
        Get applications.
        
        Args:
            status: Filter by status
            limit: Limit results
            
        Returns:
            List of application dicts
        """
        return self.db.get_applications(status=status, limit=limit)
    
    def get_application(self, application_id: int) -> Optional[Dict]:
        """
        Get single application.
        
        Args:
            application_id: Application ID
            
        Returns:
            Application dict or None
        """
        return self.db.get_application(application_id)
    
    def export_to_excel(self, output_path: str):
        """
        Export applications to Excel.
        
        Args:
            output_path: Path to save Excel file
        """
        self.db.export_to_excel(output_path)
    
    def get_due_followups(self) -> List[Dict]:
        """
        Get applications with follow-ups due.
        
        Returns:
            List of applications needing follow-up
        """
        today = datetime.now().date()
        all_apps = self.db.get_applications()
        
        due_followups = []
        for app in all_apps:
            if app.get('followup_date'):
                followup_date = datetime.strptime(app['followup_date'], '%Y-%m-%d').date()
                if followup_date <= today:
                    due_followups.append(app)
        
        return due_followups
