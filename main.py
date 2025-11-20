import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Resume Critic", page_icon="📝", layout="centered")

st.title("AI Resume Critic")

st.markdown("""Upload your resume and let the AI analyze it for you!""")

def extract_text(file):
    if file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif file.type == "text/plain":
        return str(file.read(), "utf-8")
    return ""

def get_ai_response(prompt):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    
    completion = client.chat.completions.create(
        model="meta-llama/llama-3-8b-instruct",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return completion.choices[0].message.content

uploaded_file = st.file_uploader("Upload your Resume (PDF or TXT)", type=["pdf", "txt"])
job_role = st.text_input("Enter the job role you are applying for")

if uploaded_file is not None:
    if st.button("Analyze Resume"):
        with st.spinner("Analyzing..."):
            try:
                resume_text = extract_text(uploaded_file)
                prompt = f"""
                You are an expert resume critic. 
                The candidate is applying for the role of: {job_role if job_role else "General Role"}
                
                Please review the following resume and provide:
                1. A summary of the candidate's profile.
                2. Top 3 strengths.
                3. Top 3 areas for improvement.
                4. Specific actionable advice to make the resume stand out for the {job_role if job_role else "target"} role.
                5. Skills
                5. Skills 

                Resume Text:
                {resume_text}
                """
                response = get_ai_response(prompt)
                st.subheader("Analysis Result")
                st.write(response)
            except Exception as e:
                st.error(f"An error occurred: {e}")
