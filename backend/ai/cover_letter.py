"""
Cover letter generation.
"""
import logging
from typing import Dict, Any
from backend.ai.llm_client import get_llm_client

logger = logging.getLogger(__name__)


def generate_cover_letter(
    company_name: str,
    role_title: str,
    job_description: str,
    master_resume_latex: str,
    candidate_name: str = "Ved Raval",
    candidate_email: str = "ved.raval.official@gmail.com",
    candidate_phone: str = "+1 (331) 291-3082",
) -> str:
    """
    Generate a tailored cover letter (200-300 words).
    References the company by name and 2-3 specific things from the JD.
    Tailored to the role based on real resume experience.

    Args:
        company_name: Company name
        role_title: Job title
        job_description: Full job description
        master_resume_latex: Master resume (for context)
        candidate_name: Your name
        candidate_email: Your email
        candidate_phone: Your phone

    Returns:
        Plain text cover letter
    """
    client = get_llm_client()

    system_prompt = """You are an expert cover letter writer.
Write compelling, authentic cover letters that:
1. Address the hiring manager professionally
2. Reference 2-3 specific things from the job description
3. Highlight relevant experience from the resume
4. Show genuine interest in the company and role
5. Are 200-300 words
6. Use professional but natural language
7. Never invent experience or skills
Return only the cover letter text, no formatting or metadata."""

    prompt = f"""Write a cover letter for {candidate_name} applying for {role_title} at {company_name}.

Candidate:
Name: {candidate_name}
Email: {candidate_email}
Phone: {candidate_phone}

Resume Summary (key experience):
{master_resume_latex}

Job Description:
{job_description}

Generate a professional cover letter (200-300 words) that:
- Opens with interest in the specific role at {company_name}
- References 2-3 specific job requirements or company details
- Highlights 1-2 relevant projects or experiences from the resume
- Shows cultural/mission alignment with the company
- Closes with a clear call to action
- Includes a proper professional greeting and closing

Return only the letter text, no "Dear Hiring Manager:" prefix or subject line."""

    try:
        # Bumped from 1200 -> 2048. A 300-word letter is only ~400-500 tokens,
        # but the previous ceiling was still getting hit (likely Gemini's
        # thinking tokens eating the budget before thinking was disabled in
        # llm_client.py). Extra headroom here is cheap insurance.
        cover_letter = client.generate_text(
            prompt,
            system_prompt,
            temperature=0.7,
            max_tokens=2048
        )
        logger.info(f"Cover letter generated for {company_name} - {role_title}")
        return cover_letter
    except Exception as e:
        logger.error(f"Cover letter generation failed: {e}")
        raise