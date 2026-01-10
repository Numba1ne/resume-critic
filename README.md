# AI Resume Optimizer

A production-grade agentic system that uses CrewAI to intelligently rewrite and optimize resumes to match specific job descriptions. The application leverages two specialized AI agents working in tandem to analyze job requirements and tailor resumes with ATS-optimized, achievement-driven content.

## Overview

The AI Resume Optimizer is an intelligent resume tailoring system built with CrewAI orchestration. It transforms generic resumes into targeted, keyword-optimized documents that pass ATS (Applicant Tracking System) filters while remaining engaging for human recruiters.

**Key Capabilities:**
- **Intelligent Analysis**: Extracts critical keywords, tone, and industry focus from job descriptions
- **Strategic Rewriting**: Uses T-A-R (Task, Action, Result) framework to create impactful bullet points
- **ATS Optimization**: Ensures resumes meet 2025 ATS standards while maintaining authenticity
- **PDF Generation**: Produces professional, formatted PDF resumes ready for download
- **Data Safety**: Pydantic validation ensures data integrity before PDF generation

**Why It's Useful:**
In 2025, you can't use one résumé for every job application. Recruiters can instantly spot generic, copy-paste résumés. This tool helps you quickly adapt your résumé for each role using AI-powered analysis and rewriting, without losing your authentic voice.

## Target Audience

- **Job Seekers**: Professionals looking to optimize their resumes for specific job applications
- **Career Coaches**: Resume writing professionals who need efficient tools for client work
- **Recruiters**: HR professionals who want to help candidates improve their application materials
- **Tech Professionals**: Developers, engineers, and tech workers targeting roles in E-commerce, Fintech, SaaS, and related industries

## Prerequisites

### Required Knowledge
- Basic understanding of Python (for development/contributions)
- Familiarity with resume writing best practices (for optimal usage)
- Knowledge of your target industry and role requirements

### System Requirements
- **Python**: >= 3.13
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM
- **Storage**: ~500MB for dependencies

### API Access
- **OpenAI API Key**: Required for CrewAI agent operations
  - Sign up at [OpenAI Platform](https://platform.openai.com/api-keys)
  - Ensure you have API credits available

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/Numba1ne/resume-critic.git
cd resume-critic
```

### Step 2: Install Dependencies

This project uses `uv` for dependency management (recommended), but you can also use `pip`.

**Using uv (Recommended):**
```bash
uv sync
```

**Using pip:**
```bash
pip install -e .
# OR
pip install -r requirements.txt  # if requirements.txt exists
```

### Step 3: Verify Installation

```bash
python -c "import streamlit, crewai, pydantic, fpdf; print('All dependencies installed successfully!')"
```

## Environment Setup

### Create Environment File

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key for CrewAI agents | Yes |

**Security Note**: Never commit your `.env` file to version control. It's already included in `.gitignore`.

## Usage

### Starting the Application

```bash
streamlit run app.py
```

The application will start and open in your default web browser at `http://localhost:8501`.

### Step-by-Step Usage Guide

1. **Upload Your Resume**
   - Click "Upload your Resume (PDF)"
   - Select your current resume PDF file
   - The system will extract text automatically

2. **Provide Job Description**
   - Paste the complete job description in the text area
   - Include requirements, responsibilities, and qualifications
   - The more detailed, the better the optimization

3. **Optimize with CrewAI**
   - Click the "Optimize with CrewAI" button
   - Wait for the AI agents to process (typically 30-60 seconds)

4. **Review Strategist's Analysis**
   - Expand the "📊 Strategist's Analysis" section
   - Review the extracted keywords and tone recommendations
   - Understand what the system identified as important

5. **Preview Optimized Resume**
   - Review the optimized resume preview
   - Check that personal information is correct
   - Verify that experience bullets follow T-A-R format
   - Ensure skills are enhanced appropriately

6. **Download PDF**
   - Click "📥 Download Optimized Resume (PDF)"
   - Save the optimized resume for your application

### Example Workflow

```python
# The system processes your resume through this pipeline:

PDF Upload → Text Extraction → CrewAI Orchestration
    ↓
Strategist Agent (Analyzes Job Description)
    ↓
Writer Agent (Rewrites Resume Sections)
    ↓
Pydantic Validation → PDF Generation → Download
```

## Data Requirements

### Input Format

**Resume PDF:**
- Must be a readable PDF (not scanned images)
- Should contain extractable text
- Recommended: Standard resume format with sections for:
  - Personal Information (name, email, phone, location)
  - Professional Summary
  - Work Experience
  - Skills

**Job Description:**
- Plain text format
- Should include:
  - Job title and company
  - Key responsibilities
  - Required qualifications
  - Preferred skills
  - Industry context

### Output Format

The system generates a validated `ResumeSchema` object containing:
- `personal_info`: Dictionary with contact details
- `summary`: Professional summary (4-6 sentences)
- `work_experience`: List of Job objects with:
  - `title`: Job title
  - `company`: Company name
  - `rewritten_bullets`: T-A-R formatted bullet points
- `skills`: List of optimized skills

## Testing

### Manual Testing

1. **Test PDF Extraction:**
   ```bash
   python -c "from utils import extract_pdf_text; print('PDF extraction works')"
   ```

2. **Test Schema Validation:**
   ```bash
   python -c "from models import ResumeSchema; print('Models imported successfully')"
   ```

3. **Test PDF Generation:**
   ```bash
   python -c "from pdf_generator import generate_resume_pdf; print('PDF generator ready')"
   ```

### Running the Application

```bash
# Start Streamlit app
streamlit run app.py

# Test with sample resume and job description
# Upload a test PDF and provide a job description
```

## Configuration

### Agent Configuration

Edit `agents.py` to customize agent behavior:

```python
# Change LLM model
llm = ChatOpenAI(
    model="gpt-4",  # Options: "gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"
    temperature=0.7,  # Adjust creativity (0.0-1.0)
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
```

### PDF Generation Settings

Edit `pdf_generator.py` to customize PDF layout:

```python
# Font settings
pdf.set_font('Arial', 'B', 18)  # Font, Style, Size

# Page margins
pdf.set_auto_page_break(auto=True, margin=15)
```

### Task Prompts

Customize agent prompts in `tasks.py`:
- `create_analysis_task()`: Modify Strategist agent instructions
- `create_rewrite_task()`: Modify Writer agent instructions

## Methodology

### Architecture

The application follows an **agentic architecture** using CrewAI:

```
User Input (PDF + Job Description)
    ↓
PDF Text Extraction (PyPDF2)
    ↓
CrewAI Orchestration
    ├─→ Strategist Agent
    │   └─ Analyzes job description
    │       • Extracts top 5 keywords
    │       • Identifies tone & style
    │       • Determines industry focus
    │
    └─→ Writer Agent
        └─ Rewrites resume sections
            • Professional Summary (4-6 sentences)
            • Experience bullets (T-A-R format)
            • Skills enhancement
    ↓
Pydantic Validation (ResumeSchema)
    ↓
PDF Generation (FPDF2)
    ↓
Streamlit UI Display & Download
```

### Key Algorithms & Approaches

1. **T-A-R Framework**: Task-Action-Result structure for bullet points
   - **Task**: What was the challenge or objective?
   - **Action**: What did you do? (Strong action verbs)
   - **Result**: What was the measurable outcome?

2. **Keyword Extraction**: Identifies frequently mentioned terms across:
   - Job responsibilities
   - Required qualifications
   - Preferred skills
   - Industry-specific terminology

3. **Tone Analysis**: Determines writing style requirements:
   - Achievement-driven
   - Technical vs. Creative
   - Formal vs. Conversational

4. **Data Validation**: Pydantic models ensure:
   - Type safety
   - Required fields present
   - Data structure integrity
   - Error prevention before PDF generation

### Best Practices Implemented

- **Authenticity**: Never fabricates experience or metrics
- **Quantification**: Encourages measurable achievements
- **ATS Optimization**: Uses 2025 ATS-friendly formatting
- **Industry Tailoring**: Adapts to specific niches (E-commerce, Fintech, SaaS)

## Performance

### Expected Performance Metrics

- **Processing Time**: 30-60 seconds per resume optimization
- **PDF Generation**: < 2 seconds
- **Text Extraction**: < 1 second for standard PDFs
- **API Calls**: 2-3 OpenAI API calls per optimization

### Optimization Tips

1. **Job Description Quality**: More detailed descriptions yield better results
2. **Resume Length**: Optimal for 1-2 page resumes
3. **API Rate Limits**: Be mindful of OpenAI API rate limits
4. **PDF Quality**: Ensure PDFs have extractable text (not scanned images)

### Limitations

- Requires internet connection for OpenAI API calls
- Processing time depends on API response times
- PDF extraction quality depends on source PDF format
- Best results with tech industry roles (can be adapted for others)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please follow these guidelines:

### How to Contribute

1. **Fork the Repository**
   ```bash
   git fork https://github.com/Numba1ne/resume-critic.git
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow PEP 8 style guidelines
   - Add docstrings to new functions
   - Update tests if applicable

4. **Commit Your Changes**
   ```bash
   git commit -m "Add: Description of your feature"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Contribution Areas

- **Agent Prompts**: Improve optimization quality
- **PDF Layout**: Enhance visual design
- **Error Handling**: Better user experience
- **Testing**: Add unit and integration tests
- **Documentation**: Improve guides and examples

### Code Style

- Use type hints for function parameters
- Follow Pydantic models for data structures
- Add docstrings to all functions
- Keep functions focused and single-purpose

## Changelog

### Version 0.1.0 (Current)

**Initial Release** - January 2025

**Features:**
- ✅ CrewAI agent orchestration (Strategist + Writer)
- ✅ PDF text extraction
- ✅ Job description analysis
- ✅ Resume rewriting with T-A-R framework
- ✅ Pydantic data validation
- ✅ PDF generation with FPDF2
- ✅ Streamlit web interface
- ✅ Resume preview and download

**Improvements:**
- Fixed Unicode character handling in PDF generation
- Enhanced agent prompts with 2025 resume best practices
- Added comprehensive error handling
- Improved data validation and parsing

**Known Issues:**
- PDF extraction may fail on scanned/image-based PDFs
- Processing time varies with API response times

## Citation

If you use this project in academic work or research, please cite:

```bibtex
@software{resume_optimizer_2025,
  author = {Anthony, Emmanuel},
  title = {AI Resume Optimizer: Agentic System for Resume Tailoring},
  year = {2025},
  url = {https://github.com/Numba1ne/resume-critic},
  version = {0.1.0}
}
```

## Contact

**Maintainer:** Emmanuel Anthony

- **Email**: emmanuelanthony357@gmail.com
- **GitHub**: [www.github.com/Numba1ne](https://www.github.com/Numba1ne)

### Support

For issues, questions, or feature requests:
1. Open an issue on [GitHub Issues](https://github.com/Numba1ne/resume-critic/issues)
2. Email: emmanuelanthony357@gmail.com

### Acknowledgments

- Built with [CrewAI](https://github.com/joaomdmoura/crewAI) for agent orchestration
- Uses [Streamlit](https://streamlit.io/) for the web interface
- Powered by [OpenAI](https://openai.com/) GPT models
- PDF generation with [FPDF2](https://pyfpdf.github.io/fpdf2/)

---

**Made with ❤️ for job seekers who want to stand out in 2025**
