"""
Analytics - Success metrics and analysis.
"""
from typing import Dict, List
from datetime import datetime, timedelta
from src.trackers.application_tracker import ApplicationTracker


class ApplicationAnalytics:
    """Analyze application success metrics."""
    
    def __init__(self, tracker: ApplicationTracker):
        """
        Initialize analytics.
        
        Args:
            tracker: Application tracker instance
        """
        self.tracker = tracker
    
    def calculate_response_rate(self, days: int = 30) -> Dict:
        """
        Calculate response rate for recent applications.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dict with response rate statistics
        """
        cutoff_date = datetime.now().date() - timedelta(days=days)
        all_apps = self.tracker.get_applications()
        
        recent_apps = [app for app in all_apps 
                      if datetime.strptime(app['date_applied'], '%Y-%m-%d').date() >= cutoff_date]
        
        total = len(recent_apps)
        responded = len([app for app in recent_apps if app['status'] != 'Applied'])
        
        response_rate = (responded / total * 100) if total > 0 else 0
        
        return {
            'total_applications': total,
            'responded': responded,
            'response_rate': round(response_rate, 1),
            'period_days': days
        }
    
    def calculate_interview_rate(self) -> Dict:
        """
        Calculate interview conversion rate.
        
        Returns:
            Dict with interview statistics
        """
        all_apps = self.tracker.get_applications()
        total = len(all_apps)
        
        interviews = len([app for app in all_apps 
                         if app['status'] in ['Interview', 'Offer']])
        
        interview_rate = (interviews / total * 100) if total > 0 else 0
        
        return {
            'total_applications': total,
            'interviews': interviews,
            'interview_rate': round(interview_rate, 1)
        }
    
    def get_status_breakdown(self) -> Dict[str, int]:
        """
        Get breakdown by status.
        
        Returns:
            Dict with status counts
        """
        stats = self.tracker.get_applications_summary()
        return stats.get('by_status', {})
    
    def get_weekly_trends(self, weeks: int = 4) -> List[Dict]:
        """
        Get weekly application trends.
        
        Args:
            weeks: Number of weeks to analyze
            
        Returns:
            List of weekly statistics
        """
        all_apps = self.tracker.get_applications()
        trends = []
        
        for i in range(weeks):
            week_start = datetime.now().date() - timedelta(weeks=i+1)
            week_end = datetime.now().date() - timedelta(weeks=i)
            
            week_apps = [app for app in all_apps 
                        if week_start <= datetime.strptime(app['date_applied'], '%Y-%m-%d').date() < week_end]
            
            trends.append({
                'week': f"Week {i+1}",
                'start_date': week_start.isoformat(),
                'end_date': week_end.isoformat(),
                'applications': len(week_apps),
                'interviews': len([app for app in week_apps 
                                 if app['status'] in ['Interview', 'Offer']])
            })
        
        return list(reversed(trends))  # Oldest first
    
    def get_success_metrics(self) -> Dict:
        """
        Get comprehensive success metrics.
        
        Returns:
            Dict with all metrics
        """
        summary = self.tracker.get_applications_summary()
        response_rate = self.calculate_response_rate()
        interview_rate = self.calculate_interview_rate()
        status_breakdown = self.get_status_breakdown()
        
        return {
            'total_applications': summary.get('total', 0),
            'this_week': summary.get('this_week', 0),
            'response_rate': summary.get('response_rate', 0),
            'interview_rate': summary.get('interview_rate', 0),
            'status_breakdown': status_breakdown,
            'recent_response_rate': response_rate.get('response_rate', 0),
            'overall_interview_rate': interview_rate.get('interview_rate', 0)
        }
