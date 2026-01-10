"""
CrewAI task definitions and crew orchestration.
"""
import json
from crewai import Task, Crew, Process
from agents import create_strategist_agent, create_writer_agent


def create_analysis_task(job_description: str, strategist_agent) -> Task:
    """
    Creates the task for analyzing the job description.
    
    Args:
        job_description: The job description text
        strategist_agent: The Strategist agent instance
        
    Returns:
        Task: Configured analysis task
    """
    return Task(
        description=f"""You are a professional resume writer and ATS expert specializing in tech industry roles. Analyze the following job description to extract critical optimization insights.

Job Description:
{job_description}

Your task is to:
1. Identify the top 5 keywords that are critical for ATS systems and recruiter scanning
2. Determine the tone and style requirements (e.g., formal, technical, creative, achievement-driven)
3. Identify the industry focus (e.g., E-commerce, Fintech, SaaS, etc.)
4. Note any specific tools, technologies, or methodologies mentioned

Focus on:
- Skills and tools that appear multiple times
- Industry-specific terminology
- Action verbs and achievement language
- Quantifiable metrics mentioned in the job description

Output your analysis as a JSON object with the following structure:
{{
    "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
    "tone": "description of the tone and style (e.g., 'achievement-driven, technical, results-oriented')",
    "industry": "primary industry focus",
    "key_phrases": ["phrase1", "phrase2", "phrase3"]
}}""",
        agent=strategist_agent,
        expected_output="JSON object with keywords array, tone string, industry, and key phrases"
    )


def create_rewrite_task(resume_text: str, analysis_result: str, writer_agent) -> Task:
    """
    Creates the task for rewriting the resume.
    
    Args:
        resume_text: Original resume text
        analysis_result: Output from the Strategist agent
        writer_agent: The Writer agent instance
        
    Returns:
        Task: Configured rewrite task
    """
    return Task(
        description=f"""You are a world-class resume and LinkedIn profile writer with expertise in tech industry roles. Your task is to rewrite the resume to be highly impactful, achievement-driven, and keyword-optimized while maintaining authenticity.

Strategist's Analysis:
{analysis_result}

Original Resume Text:
{resume_text}

CRITICAL INSTRUCTIONS:

1. **Professional Summary (4-6 sentences)**:
   - Start with a powerful opening sentence
   - Highlight unique strengths and measurable achievements
   - Use recruiter-friendly keywords from the Strategist's analysis
   - Show industry versatility while maintaining clear specialization
   - Feel authentic and human (avoid generic filler)
   - Subtly connect past experience to future goals

2. **Experience Section - Follow T-A-R (Task, Action, Result)**:
   - Rewrite each bullet point using the T-A-R framework
   - Make achievements quantifiable (use numbers, percentages, metrics)
   - Start bullets with strong action verbs (Led, Designed, Implemented, etc.)
   - Naturally incorporate keywords and key phrases from the job description
   - Keep it concise yet human (avoid robotic language)
   - Ensure it meets 2025 ATS standards while remaining engaging
   - Maintain accuracy - DO NOT fabricate experience or metrics

3. **Skills Section**:
   - Enhance with relevant keywords from the Strategist's analysis
   - Prioritize skills that match the job description
   - Include both core technical skills and transferable skills
   - Make it modern and tailored to 2025 industry standards

4. **Maintain Authenticity**:
   - Keep all personal information exactly as provided
   - Only enhance and optimize existing experience, don't create new roles
   - Ensure all achievements are believable and verifiable

Format your output as JSON with this structure:
{{
    "personal_info": {{
        "name": "...",
        "email": "...",
        "phone": "...",
        "location": "..."
    }},
    "summary": "4-6 sentence achievement-driven professional summary",
    "work_experience": [
        {{
            "title": "...",
            "company": "...",
            "rewritten_bullets": [
                "T-A-R formatted bullet with quantifiable results",
                "Another T-A-R bullet starting with strong action verb",
                "..."
            ]
        }}
    ],
    "skills": ["skill1", "skill2", "skill3", ...]
}}

Remember: The goal is to create a tailored resume that speaks to the specific industry and role while emphasizing skills and measurable results.""",
        agent=writer_agent,
        expected_output="JSON object matching the ResumeSchema structure with optimized, achievement-driven content"
    )


def run_resume_optimization_crew(resume_text: str, job_description: str) -> dict:
    """
    Orchestrates the CrewAI crew to optimize a resume.
    
    Args:
        resume_text: Original resume text extracted from PDF
        job_description: Job description text
        
    Returns:
        dict: Dictionary containing:
            - 'analysis': Strategist's analysis (keywords and tone)
            - 'rewritten_resume': Writer's rewritten resume text
    """
    # Create agents
    strategist = create_strategist_agent()
    writer = create_writer_agent()
    
    # Create tasks
    analysis_task = create_analysis_task(job_description, strategist)
    # Create rewrite task - analysis will be injected via context
    rewrite_task = create_rewrite_task(resume_text, "See context from Strategist agent", writer)
    
    # Set up task dependencies - CrewAI will inject analysis_task output into rewrite_task
    rewrite_task.context = [analysis_task]
    
    # Create crew
    crew = Crew(
        agents=[strategist, writer],
        tasks=[analysis_task, rewrite_task],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute crew
    result = crew.kickoff()
    
    # Extract results
    analysis_output = analysis_task.output.raw if hasattr(analysis_task.output, 'raw') else str(analysis_task.output)
    rewrite_output = rewrite_task.output.raw if hasattr(rewrite_task.output, 'raw') else str(rewrite_task.output)
    
    # Try to parse analysis as JSON
    try:
        # Look for JSON in the analysis output
        analysis_json_match = None
        if isinstance(analysis_output, str):
            import re
            json_match = re.search(r'\{.*\}', analysis_output, re.DOTALL)
            if json_match:
                analysis_json_match = json.loads(json_match.group())
    except Exception:
        pass
    
    analysis_result = analysis_json_match if analysis_json_match else {
        "keywords": [],
        "tone": analysis_output
    }
    
    return {
        'analysis': analysis_result,
        'rewritten_resume': rewrite_output
    }
