"""
PDF handling utilities (moved from utils.py).
"""
import PyPDF2
from typing import Optional


def extract_pdf_text(file) -> str:
    """
    Extract text from uploaded PDF file.
    
    Args:
        file: Uploaded file object (Streamlit UploadedFile or file path)
        
    Returns:
        str: Extracted text from PDF
    """
    if hasattr(file, 'type') and file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif isinstance(file, str):
        # File path
        with open(file, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    elif hasattr(file, 'read'):
        # File-like object
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    return ""
