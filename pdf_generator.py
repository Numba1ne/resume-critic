"""
PDF generation using FPDF2.
Takes validated Pydantic ResumeSchema objects and generates professional PDFs.
"""
from fpdf import FPDF
from models import ResumeSchema


class ResumePDF(FPDF):
    """Custom PDF class for resume generation."""
    
    def header(self):
        """Header styling."""
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 0, 0)
    
    def footer(self):
        """Footer styling."""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def section_title(self, title: str):
        """Add a section title."""
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, title, 0, 1, 'L')
        self.set_draw_color(0, 0, 0)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)
    
    def add_bullet_point(self, text: str, indent: int = 15):
        """Add a bullet point."""
        self.set_font('Arial', '', 10)
        self.set_x(indent)
        self.cell(5, 6, '-', 0, 0, 'L')  # Use ASCII dash instead of Unicode bullet
        self.multi_cell(0, 6, text, 0, 'L')
        self.ln(2)


def generate_resume_pdf(data: ResumeSchema) -> bytes:
    """
    Generate a PDF resume from a validated ResumeSchema object.
    
    Args:
        data: Validated ResumeSchema Pydantic model
        
    Returns:
        bytes: PDF file as bytes for download
    """
    pdf = ResumePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Personal Information Section
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(0, 0, 0)
    
    name = data.personal_info.get('name', 'N/A')
    pdf.cell(0, 10, name, 0, 1, 'C')
    pdf.ln(5)
    
    pdf.set_font('Arial', '', 10)
    contact_info = []
    if 'email' in data.personal_info:
        contact_info.append(data.personal_info['email'])
    if 'phone' in data.personal_info:
        contact_info.append(data.personal_info['phone'])
    if 'location' in data.personal_info:
        contact_info.append(data.personal_info['location'])
    
    if contact_info:
        contact_str = ' | '.join(contact_info)
        pdf.cell(0, 6, contact_str, 0, 1, 'C')
    
    pdf.ln(10)
    
    # Professional Summary
    if data.summary:
        pdf.section_title('PROFESSIONAL SUMMARY')
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 6, data.summary, 0, 'L')
        pdf.ln(5)
    
    # Work Experience
    if data.work_experience:
        pdf.section_title('WORK EXPERIENCE')
        
        for job in data.work_experience:
            # Job title and company
            pdf.set_font('Arial', 'B', 11)
            pdf.set_text_color(0, 0, 0)
            job_header = f"{job.title}"
            if job.company:
                job_header += f" | {job.company}"
            pdf.cell(0, 7, job_header, 0, 1, 'L')
            pdf.ln(3)
            
            # Bullet points
            if job.rewritten_bullets:
                for bullet in job.rewritten_bullets:
                    pdf.add_bullet_point(bullet)
                pdf.ln(3)
    
    # Skills Section
    if data.skills:
        pdf.section_title('SKILLS')
        pdf.set_font('Arial', '', 10)
        skills_text = ' | '.join(data.skills)  # Use pipe separator instead of Unicode bullet
        pdf.multi_cell(0, 6, skills_text, 0, 'L')
        pdf.ln(5)
    
    # Return PDF as bytes (output already returns bytes when dest='S')
    pdf_bytes = pdf.output(dest='S')
    if isinstance(pdf_bytes, str):
        return pdf_bytes.encode('latin1')
    elif isinstance(pdf_bytes, bytearray):
        return bytes(pdf_bytes)
    return pdf_bytes
