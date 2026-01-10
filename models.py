"""
Pydantic models for resume data structure.
These models ensure data safety before PDF generation.
"""
from typing import List
from pydantic import BaseModel, Field


class Job(BaseModel):
    """Represents a single work experience entry."""
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    rewritten_bullets: List[str] = Field(..., description="Optimized bullet points for this role")


class ResumeSchema(BaseModel):
    """Root schema for resume data structure."""
    personal_info: dict = Field(..., description="Personal information (name, email, phone, location)")
    summary: str = Field(..., description="Professional summary")
    work_experience: List[Job] = Field(..., description="List of work experience entries")
    skills: List[str] = Field(..., description="List of technical and professional skills")
