"""
Tests for JD Parser.
"""
import pytest
from src.parsers.jd_parser import JobDescriptionParser


def test_extract_job_title():
    """Test job title extraction."""
    jd_text = "We're hiring a Senior Data Analyst to join our team."
    parser = JobDescriptionParser(jd_text)
    title = parser.extract_job_title()
    assert "Data Analyst" in title or "Senior" in title


def test_extract_technical_skills():
    """Test technical skills extraction."""
    jd_text = """
    Required skills:
    - SQL expertise
    - Python programming
    - Data visualization with Tableau
    """
    parser = JobDescriptionParser(jd_text)
    skills = parser.extract_technical_skills()
    assert len(skills) > 0


def test_extract_verbatim_phrases():
    """Test verbatim phrase extraction."""
    jd_text = """
    Strong SQL skills, with the ability to query, 
    join, and manipulate large and complex datasets.
    """
    parser = JobDescriptionParser(jd_text)
    phrases = parser.extract_verbatim_phrases()
    assert len(phrases) > 0


def test_extract_all():
    """Test complete extraction."""
    jd_text = """
    Senior Data Analyst Position
    
    We're looking for a Senior Data Analyst with:
    - 5+ years of experience
    - Strong SQL and Python skills
    - Experience with Tableau
    
    Required:
    - SQL expertise
    - Python programming
    
    Preferred:
    - AWS experience
    """
    parser = JobDescriptionParser(jd_text)
    analysis = parser.extract_all()
    
    assert 'job_title' in analysis
    assert 'technical_skills' in analysis
    assert 'required_skills' in analysis
    assert 'preferred_skills' in analysis
