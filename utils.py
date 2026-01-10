"""
Utility functions for PDF extraction and resume parsing.
"""
import PyPDF2
import json
import re
from typing import Optional
from models import ResumeSchema, Job


def extract_pdf_text(file) -> str:
    """
    Extract text from uploaded PDF file.
    
    Args:
        file: Uploaded file object (Streamlit UploadedFile)
        
    Returns:
        str: Extracted text from PDF
    """
    if file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif file.type == "text/plain":
        return str(file.read(), "utf-8")
    return ""


def parse_resume_to_schema(text: str) -> ResumeSchema:
    """
    Parse rewritten resume text into ResumeSchema.
    
    This function attempts to extract structured data from the AI-generated text.
    It handles JSON format if the agent outputs JSON, otherwise uses regex parsing.
    
    Args:
        text: Rewritten resume text from Writer agent
        
    Returns:
        ResumeSchema: Validated Pydantic model
        
    Raises:
        ValueError: If text cannot be parsed into valid schema
    """
    # Try to parse as JSON first (if agent outputs JSON)
    try:
        # Look for JSON in the text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return ResumeSchema.model_validate(data)
    except (json.JSONDecodeError, ValueError):
        pass
    
    # Fallback: Try to parse structured text format
    # This is a basic parser - in production, you might want more sophisticated parsing
    try:
        # Extract personal info (basic pattern matching)
        personal_info = {}
        name_match = re.search(r'(?:Name|Full Name):\s*(.+)', text, re.IGNORECASE)
        email_match = re.search(r'Email:\s*([^\s]+)', text, re.IGNORECASE)
        phone_match = re.search(r'Phone:\s*([^\n]+)', text, re.IGNORECASE)
        
        if name_match:
            personal_info['name'] = name_match.group(1).strip()
        if email_match:
            personal_info['email'] = email_match.group(1).strip()
        if phone_match:
            personal_info['phone'] = phone_match.group(1).strip()
        
        # Extract summary
        summary_match = re.search(r'(?:Summary|Professional Summary):\s*(.+?)(?=\n\n|\n[A-Z])', text, re.DOTALL | re.IGNORECASE)
        summary = summary_match.group(1).strip() if summary_match else "Professional summary"
        
        # Extract work experience
        work_experience = []
        work_section = re.search(r'(?:Work Experience|Experience|Employment):\s*(.+?)(?=\n(?:Skills|Education|$))', text, re.DOTALL | re.IGNORECASE)
        if work_section:
            work_text = work_section.group(1)
            # Try to find job entries
            job_pattern = r'(?:Title|Position):\s*(.+?)\n(?:Company|Employer):\s*(.+?)\n(?:Bullets|Responsibilities):\s*(.+?)(?=\n(?:Title|Position|$))'
            jobs = re.finditer(job_pattern, work_text, re.DOTALL | re.IGNORECASE)
            for job_match in jobs:
                title = job_match.group(1).strip()
                company = job_match.group(2).strip()
                bullets_text = job_match.group(3).strip()
                bullets = [b.strip() for b in bullets_text.split('\n') if b.strip() and b.strip().startswith(('-', '•', '*'))]
                if not bullets:
                    bullets = [bullets_text]  # Fallback to single bullet
                work_experience.append(Job(title=title, company=company, rewritten_bullets=bullets))
        
        # Extract skills
        skills_section = re.search(r'(?:Skills|Technical Skills):\s*(.+?)(?=\n\n|$)', text, re.DOTALL | re.IGNORECASE)
        skills = []
        if skills_section:
            skills_text = skills_section.group(1)
            skills = [s.strip() for s in re.split(r'[,;•\-\n]', skills_text) if s.strip()]
        
        # Ensure we have minimum required data
        if not personal_info:
            personal_info = {'name': 'N/A'}
        if not work_experience:
            work_experience = [Job(title="N/A", company="N/A", rewritten_bullets=["No experience listed"])]
        if not skills:
            skills = ["No skills listed"]
        
        return ResumeSchema(
            personal_info=personal_info,
            summary=summary,
            work_experience=work_experience,
            skills=skills
        )
    except Exception as e:
        raise ValueError(f"Failed to parse resume text: {str(e)}")
