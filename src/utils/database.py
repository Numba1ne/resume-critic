"""
Database operations for application tracking.
"""
import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path


class Database:
    """SQLite database manager for application tracking."""
    
    def __init__(self, db_path: str = 'data/applications.db'):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def init_database(self):
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Applications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    job_title TEXT NOT NULL,
                    date_applied DATE NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Applied',
                    cv_version_path TEXT,
                    cover_letter_included BOOLEAN DEFAULT FALSE,
                    followup_date DATE,
                    interview_date DATE,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Job descriptions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_descriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application_id INTEGER,
                    jd_text TEXT,
                    jd_url TEXT,
                    job_location TEXT,
                    salary_range TEXT,
                    ats_system TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
                )
            ''')
            
            # Extracted keywords table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS extracted_keywords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jd_id INTEGER,
                    category TEXT NOT NULL,
                    keyword TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    priority TEXT DEFAULT 'MEDIUM',
                    included_in_cv BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (jd_id) REFERENCES job_descriptions(id) ON DELETE CASCADE
                )
            ''')
            
            # CV versions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cv_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application_id INTEGER,
                    file_path TEXT NOT NULL,
                    ats_score INTEGER,
                    keyword_match_percentage DECIMAL(5,2),
                    generation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    generation_mode TEXT,
                    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
                )
            ''')
            
            # Cover letters table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cover_letters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application_id INTEGER,
                    file_path TEXT,
                    word_count INTEGER,
                    generation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_applications_status 
                ON applications(status)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_applications_date 
                ON applications(date_applied)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_keywords_jd_id 
                ON extracted_keywords(jd_id)
            ''')
            
            conn.commit()
    
    def add_application(self, company_name: str, job_title: str, 
                       status: str = 'Applied', **kwargs) -> int:
        """
        Add new application.
        
        Args:
            company_name: Company name
            job_title: Job title
            status: Application status
            **kwargs: Additional fields (date_applied, notes, etc.)
            
        Returns:
            Application ID
        """
        date_applied = kwargs.get('date_applied', datetime.now().date())
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO applications 
                (company_name, job_title, date_applied, status, notes, 
                 followup_date, interview_date, cover_letter_included)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_name,
                job_title,
                date_applied,
                status,
                kwargs.get('notes'),
                kwargs.get('followup_date'),
                kwargs.get('interview_date'),
                kwargs.get('cover_letter_included', False)
            ))
            return cursor.lastrowid
    
    def update_application(self, application_id: int, **kwargs):
        """
        Update application fields.
        
        Args:
            application_id: Application ID
            **kwargs: Fields to update
        """
        if not kwargs:
            return
        
        set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        set_clause += ", updated_at = CURRENT_TIMESTAMP"
        values = list(kwargs.values()) + [application_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE applications 
                SET {set_clause}
                WHERE id = ?
            ''', values)
    
    def get_applications(self, status: Optional[str] = None, 
                        limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get applications, optionally filtered by status.
        
        Args:
            status: Filter by status
            limit: Limit number of results
            
        Returns:
            List of application dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM applications'
            params = []
            
            if status:
                query += ' WHERE status = ?'
                params.append(status)
            
            query += ' ORDER BY date_applied DESC'
            
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_application(self, application_id: int) -> Optional[Dict[str, Any]]:
        """Get single application by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM applications WHERE id = ?', (application_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def add_job_description(self, application_id: int, jd_text: str, 
                            jd_url: Optional[str] = None, **kwargs) -> int:
        """
        Add job description for an application.
        
        Args:
            application_id: Application ID
            jd_text: Job description text
            jd_url: Job description URL
            **kwargs: Additional fields
            
        Returns:
            JD ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO job_descriptions 
                (application_id, jd_text, jd_url, job_location, salary_range, ats_system)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                application_id,
                jd_text,
                jd_url,
                kwargs.get('job_location'),
                kwargs.get('salary_range'),
                kwargs.get('ats_system')
            ))
            return cursor.lastrowid
    
    def add_keywords(self, jd_id: int, keywords: List[Dict[str, Any]]):
        """
        Add extracted keywords for a job description.
        
        Args:
            jd_id: Job description ID
            keywords: List of keyword dicts with category, keyword, frequency, priority
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for kw in keywords:
                cursor.execute('''
                    INSERT INTO extracted_keywords 
                    (jd_id, category, keyword, frequency, priority)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    jd_id,
                    kw.get('category', 'general'),
                    kw.get('keyword'),
                    kw.get('frequency', 1),
                    kw.get('priority', 'MEDIUM')
                ))
    
    def get_keywords(self, jd_id: int) -> List[Dict[str, Any]]:
        """Get keywords for a job description."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM extracted_keywords 
                WHERE jd_id = ?
                ORDER BY frequency DESC, priority DESC
            ''', (jd_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def add_cv_version(self, application_id: int, file_path: str, 
                      ats_score: Optional[int] = None,
                      keyword_match_percentage: Optional[float] = None,
                      generation_mode: Optional[str] = None) -> int:
        """Add CV version for an application."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO cv_versions 
                (application_id, file_path, ats_score, keyword_match_percentage, generation_mode)
                VALUES (?, ?, ?, ?, ?)
            ''', (application_id, file_path, ats_score, keyword_match_percentage, generation_mode))
            return cursor.lastrowid
    
    def add_cover_letter(self, application_id: int, file_path: Optional[str] = None,
                         word_count: Optional[int] = None) -> int:
        """Add cover letter for an application."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO cover_letters (application_id, file_path, word_count)
                VALUES (?, ?, ?)
            ''', (application_id, file_path, word_count))
            return cursor.lastrowid
    
    def get_application_statistics(self) -> Dict[str, Any]:
        """Get application statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total applications
            cursor.execute('SELECT COUNT(*) as total FROM applications')
            total = cursor.fetchone()['total']
            
            # By status
            cursor.execute('''
                SELECT status, COUNT(*) as count 
                FROM applications 
                GROUP BY status
            ''')
            by_status = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Response rate (any status other than 'Applied')
            cursor.execute('''
                SELECT COUNT(*) as responded 
                FROM applications 
                WHERE status != 'Applied'
            ''')
            responded = cursor.fetchone()['responded']
            response_rate = (responded / total * 100) if total > 0 else 0
            
            # Interview rate
            cursor.execute('''
                SELECT COUNT(*) as interviews 
                FROM applications 
                WHERE status IN ('Interview', 'Offer')
            ''')
            interviews = cursor.fetchone()['interviews']
            interview_rate = (interviews / total * 100) if total > 0 else 0
            
            # This week
            cursor.execute('''
                SELECT COUNT(*) as this_week 
                FROM applications 
                WHERE date_applied >= date('now', '-7 days')
            ''')
            this_week = cursor.fetchone()['this_week']
            
            return {
                'total': total,
                'by_status': by_status,
                'response_rate': round(response_rate, 1),
                'interview_rate': round(interview_rate, 1),
                'this_week': this_week
            }
    
    def export_to_excel(self, output_path: str):
        """
        Export applications to Excel file.
        
        Args:
            output_path: Path to output Excel file
        """
        try:
            import openpyxl
            from openpyxl import Workbook
            
            wb = Workbook()
            ws = wb.active
            ws.title = "Applications"
            
            # Headers
            headers = ['ID', 'Company', 'Job Title', 'Date Applied', 'Status', 
                      'Follow-up Date', 'Interview Date', 'Notes']
            ws.append(headers)
            
            # Data
            applications = self.get_applications()
            for app in applications:
                ws.append([
                    app['id'],
                    app['company_name'],
                    app['job_title'],
                    app['date_applied'],
                    app['status'],
                    app['followup_date'] or '',
                    app['interview_date'] or '',
                    app['notes'] or ''
                ])
            
            wb.save(output_path)
            return True
        except ImportError:
            raise ImportError("openpyxl is required for Excel export. Install with: pip install openpyxl")
        except Exception as e:
            raise Exception(f"Error exporting to Excel: {str(e)}")
