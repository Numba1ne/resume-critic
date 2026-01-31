"""
CrewAI agent definitions for resume optimization.
"""
import os
from crewai import Agent
from langchain_openai import ChatOpenAI


# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)


def create_strategist_agent() -> Agent:
    """
    Creates the Strategist agent responsible for analyzing job descriptions.
    
    Returns:
        Agent: Configured Strategist agent
    """
    return Agent(
        role="Resume Strategist & ATS Expert",
        goal="Analyze job descriptions to extract critical keywords, tone, industry focus, and key phrases for 2025 ATS-optimized resume tailoring",
        backstory="""You are a professional resume writer and ATS expert specializing in tech industry roles. 
        You excel at identifying the most critical keywords, industry-specific terminology, and language patterns 
        that help resumes pass through modern ATS systems while appealing to human recruiters. Your expertise 
        includes understanding industry niches (E-commerce, Fintech, SaaS), recognizing in-demand skills for 2025, 
        and identifying the tone and style that resonates with hiring managers in the tech sector.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )


def create_writer_agent() -> Agent:
    """
    Creates the Writer agent responsible for rewriting resume sections.
    
    Returns:
        Agent: Configured Writer agent
    """
    return Agent(
        role="World-Class Resume & LinkedIn Profile Writer",
        goal="Create highly impactful, achievement-driven, and keyword-optimized resumes using T-A-R framework while maintaining authenticity",
        backstory="""You are a world-class resume and LinkedIn profile writer with deep expertise in tech industry roles. 
        You specialize in crafting resumes that are both ATS-friendly and human-engaging. Your approach follows the T-A-R 
        (Task, Action, Result) framework, ensuring every bullet point tells a compelling story with quantifiable achievements. 
        You excel at writing powerful professional summaries, transforming generic descriptions into achievement-driven narratives, 
        and naturally incorporating keywords without losing the candidate's authentic voice. You understand that in 2025, resumes 
        must be tailored to specific industries and roles while remaining truthful and verifiable.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
