"""
Unified CV Generator - Combines CrewAI and rule-based approaches.
"""
from typing import Dict, Optional, Literal
import os
from src.engines.cv_tailor import CVTailoringEngine
from src.engines.crewai_integration import CrewAIIntegration
from src.utils.pdf_handler import extract_pdf_text
from src.utils.docx_handler import extract_docx_text, read_docx
from src.utils.file_converter import pdf_to_docx_text
from src.parsers.jd_parser import JobDescriptionParser


class UnifiedCVGenerator:
    """Unified CV generator supporting multiple modes."""
    
    def __init__(self):
        """Initialize unified generator."""
        self.crewai = None
        try:
            self.crewai = CrewAIIntegration()
        except ImportError:
            pass  # CrewAI not available
    
    def generate_cv(self, 
                    base_cv_path: str,
                    job_description: str,
                    mode: Literal['crewai', 'rule-based', 'both'] = 'rule-based',
                    output_path: Optional[str] = None,
                    output_format: Literal['pdf', 'docx'] = 'docx',
                    **kwargs) -> Dict:
        """
        Generate tailored CV using specified mode.
        
        Args:
            base_cv_path: Path to base CV
            job_description: Job description text
            mode: Generation mode ('crewai', 'rule-based', or 'both')
            output_path: Output file path
            output_format: Output format ('pdf' or 'docx')
            **kwargs: Additional parameters (location_availability, right_to_work, etc.)
            
        Returns:
            Dict with generation results
        """
        # Parse JD
        jd_parser = JobDescriptionParser(job_description)
        jd_analysis = jd_parser.extract_all()
        
        # Determine base CV format
        _, ext = os.path.splitext(base_cv_path.lower())
        is_pdf = ext == '.pdf'
        is_docx = ext == '.docx'
        
        if mode == 'crewai':
            if not self.crewai:
                raise ValueError("CrewAI mode not available. Install required dependencies.")
            
            if not is_pdf:
                # Convert DOCX to text for CrewAI
                doc = read_docx(base_cv_path)
                resume_text = extract_docx_text(doc)
            else:
                resume_text = extract_pdf_text(base_cv_path)
            
            # Run CrewAI optimization
            result = self.crewai.optimize_resume(resume_text, job_description)
            
            # Generate output
            if output_format == 'pdf':
                pdf_bytes = self.crewai.generate_pdf(result['resume_schema'])
                if output_path:
                    with open(output_path, 'wb') as f:
                        f.write(pdf_bytes)
                return {
                    'success': True,
                    'output_path': output_path,
                    'format': 'pdf',
                    'mode': 'crewai',
                    'resume_schema': result['resume_schema']
                }
            else:
                # Convert PDF to DOCX (basic conversion)
                if output_path is None:
                    output_path = base_cv_path.replace(ext, '_tailored.docx')
                pdf_to_docx_text(base_cv_path, output_path)
                return {
                    'success': True,
                    'output_path': output_path,
                    'format': 'docx',
                    'mode': 'crewai'
                }
        
        elif mode == 'rule-based':
            if not is_docx:
                # Convert PDF to DOCX first
                temp_docx = base_cv_path.replace(ext, '_temp.docx')
                pdf_to_docx_text(base_cv_path, temp_docx)
                base_cv_path = temp_docx
            
            # Use rule-based tailor
            tailor = CVTailoringEngine(base_cv_path, jd_analysis)
            
            if output_path is None:
                output_path = base_cv_path.replace('.docx', '_tailored.docx')
            
            result = tailor.generate_tailored_cv(
                output_path,
                location_availability=kwargs.get('location_availability'),
                right_to_work=kwargs.get('right_to_work')
            )
            
            return {
                'success': True,
                'output_path': output_path,
                'format': 'docx',
                'mode': 'rule-based',
                **result
            }
        
        elif mode == 'both':
            # Use rule-based for structure/keywords, then CrewAI for content
            if not self.crewai:
                # Fallback to rule-based only
                return self.generate_cv(base_cv_path, job_description, 'rule-based', 
                                      output_path, output_format, **kwargs)
            
            # Step 1: Rule-based tailoring for structure
            if not is_docx:
                temp_docx = base_cv_path.replace(ext, '_temp.docx')
                pdf_to_docx_text(base_cv_path, temp_docx)
                base_cv_path = temp_docx
            
            intermediate_path = base_cv_path.replace('.docx', '_intermediate.docx')
            tailor = CVTailoringEngine(base_cv_path, jd_analysis)
            tailor.generate_tailored_cv(intermediate_path, **kwargs)
            
            # Step 2: Extract text and run CrewAI
            doc = read_docx(intermediate_path)
            resume_text = extract_docx_text(doc)
            crewai_result = self.crewai.optimize_resume(resume_text, job_description)
            
            # Step 3: Generate final output
            if output_path is None:
                output_path = base_cv_path.replace('.docx', '_final.docx')
            
            if output_format == 'pdf':
                pdf_bytes = self.crewai.generate_pdf(crewai_result['resume_schema'])
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                return {
                    'success': True,
                    'output_path': output_path,
                    'format': 'pdf',
                    'mode': 'both',
                    'resume_schema': crewai_result['resume_schema']
                }
            else:
                # Save as DOCX (would need to convert from schema)
                # For now, use intermediate DOCX
                import shutil
                shutil.copy(intermediate_path, output_path)
                return {
                    'success': True,
                    'output_path': output_path,
                    'format': 'docx',
                    'mode': 'both'
                }
        
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'crewai', 'rule-based', or 'both'")
