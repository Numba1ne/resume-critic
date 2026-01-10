"""
Streamlit UI for AI Resume Optimizer.
"""
import streamlit as st
import json
from dotenv import load_dotenv
from utils import extract_pdf_text, parse_resume_to_schema
from tasks import run_resume_optimization_crew
from pdf_generator import generate_resume_pdf

load_dotenv()

st.set_page_config(
    page_title="AI Resume Optimizer",
    page_icon="📝",
    layout="centered"
)

st.title("AI Resume Optimizer")
st.markdown("""
Upload your resume and provide a job description. Our AI agents will optimize your resume 
to match the job requirements using CrewAI orchestration.
""")

# File uploader
uploaded_file = st.file_uploader(
    "Upload your Resume (PDF)",
    type=["pdf"],
    help="Upload your resume in PDF format"
)

# Job description input
job_description = st.text_area(
    "Job Description",
    height=200,
    help="Paste the full job description here",
    placeholder="Paste the job description including requirements, responsibilities, and qualifications..."
)

# Optimize button
if uploaded_file is not None and job_description:
    if st.button("Optimize with CrewAI", type="primary"):
        with st.spinner("Extracting resume text..."):
            try:
                # Extract text from PDF
                resume_text = extract_pdf_text(uploaded_file)
                
                if not resume_text.strip():
                    st.error("Could not extract text from PDF. Please ensure the PDF contains readable text.")
                    st.stop()
                
                st.success("Resume text extracted successfully!")
                
            except Exception as e:
                st.error(f"Error extracting text from PDF: {str(e)}")
                st.stop()
        
        with st.spinner("Running AI agents to optimize your resume..."):
            try:
                # Run CrewAI optimization
                result = run_resume_optimization_crew(resume_text, job_description)
                
                # Display Strategist's analysis in expander
                with st.expander("📊 Strategist's Analysis", expanded=True):
                    analysis = result.get('analysis', {})
                    
                    if isinstance(analysis, dict):
                        keywords = analysis.get('keywords', [])
                        tone = analysis.get('tone', 'Not specified')
                        
                        st.subheader("Top 5 Keywords")
                        if keywords:
                            for i, keyword in enumerate(keywords[:5], 1):
                                st.write(f"{i}. **{keyword}**")
                        else:
                            st.write("Keywords not extracted")
                        
                        st.subheader("Tone & Style")
                        st.write(tone)
                    else:
                        st.write("Analysis:", str(analysis))
                
                # Parse rewritten resume into schema
                with st.spinner("Validating and parsing optimized resume..."):
                    try:
                        rewritten_text = result.get('rewritten_resume', '')
                        resume_schema = parse_resume_to_schema(rewritten_text)
                        
                        st.success("Resume optimized and validated successfully!")
                        
                        # Display preview
                        st.subheader("Optimized Resume Preview")
                        
                        # Personal Info
                        st.write("**Personal Information**")
                        personal_info = resume_schema.personal_info
                        info_display = []
                        if 'name' in personal_info:
                            info_display.append(f"**Name:** {personal_info['name']}")
                        if 'email' in personal_info:
                            info_display.append(f"**Email:** {personal_info['email']}")
                        if 'phone' in personal_info:
                            info_display.append(f"**Phone:** {personal_info['phone']}")
                        if 'location' in personal_info:
                            info_display.append(f"**Location:** {personal_info['location']}")
                        st.write(" | ".join(info_display))
                        st.write("")
                        
                        # Summary
                        st.write("**Professional Summary**")
                        st.write(resume_schema.summary)
                        st.write("")
                        
                        # Work Experience
                        st.write("**Work Experience**")
                        for job in resume_schema.work_experience:
                            st.write(f"**{job.title}** at {job.company}")
                            for bullet in job.rewritten_bullets:
                                st.write(f"- {bullet}")
                            st.write("")
                        
                        # Skills
                        st.write("**Skills**")
                        st.write(" • ".join(resume_schema.skills))
                        
                        # Generate PDF
                        try:
                            pdf_bytes = generate_resume_pdf(resume_schema)
                            
                            # Download button
                            st.download_button(
                                label="📥 Download Optimized Resume (PDF)",
                                data=pdf_bytes,
                                file_name="optimized_resume.pdf",
                                mime="application/pdf",
                                type="primary"
                            )
                        except Exception as pdf_error:
                            st.error(f"Error generating PDF: {str(pdf_error)}")
                            st.info("The resume preview above is still available. Please check the error details.")
                        
                    except Exception as e:
                        st.error(f"Error parsing optimized resume: {str(e)}")
                        st.write("**Raw Output:**")
                        st.text_area("Writer Agent Output", rewritten_text, height=300)
                
            except Exception as e:
                st.error(f"An error occurred during optimization: {str(e)}")
                st.exception(e)

elif uploaded_file is None:
    st.info("👆 Please upload your resume PDF to get started.")

elif not job_description:
    st.info("👆 Please provide a job description to optimize your resume.")

# Sidebar with instructions
with st.sidebar:
    st.header("How It Works")
    st.markdown("""
    1. **Upload Resume**: Upload your current resume in PDF format
    2. **Provide Job Description**: Paste the complete job description
    3. **AI Analysis**: The Strategist agent analyzes keywords and tone
    4. **Resume Rewriting**: The Writer agent optimizes your resume
    5. **Download**: Get your optimized resume as a PDF
    
    **Note**: Make sure you have set your `OPENAI_API_KEY` in the `.env` file.
    """)
