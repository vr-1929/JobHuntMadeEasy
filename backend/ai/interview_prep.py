"""
Interview prep and questions generation.
Status: Placeholder for Phase 7
"""
import logging

logger = logging.getLogger(__name__)


def generate_interview_prep(
    company_name: str,
    role_title: str,
    job_description: str,
    candidate_resume: str,
) -> dict:
    """
    Generate likely interview questions and talking points.
    
    Combines:
    1. Public info about the company (if available)
    2. Job description requirements
    3. Candidate's resume projects/experience
    
    Args:
        company_name: Target company
        role_title: Target role
        job_description: Job description text
        candidate_resume: Master resume text (for talking points)
        
    Returns:
        Dict with:
        - questions: List of likely interview questions
        - talking_points: List of talking points from your resume
        - company_research: Public info about company
    """
    raise NotImplementedError("Phase 7: Implement interview prep generation")
