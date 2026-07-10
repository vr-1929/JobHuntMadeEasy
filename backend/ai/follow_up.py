"""
Follow-up email generation.
Status: Placeholder for Phase 7
"""
import logging

logger = logging.getLogger(__name__)


def generate_follow_up_email(
    company_name: str,
    role_title: str,
    date_applied: str,
    candidate_name: str,
    resume_highlights: str,
) -> str:
    """
    Generate a professional follow-up email.
    
    Called automatically when 7+ days have passed since applying,
    or on-demand from the dashboard.
    
    Args:
        company_name: Target company
        role_title: Target role
        date_applied: When you applied (for context)
        candidate_name: Your name
        resume_highlights: Key achievements from your resume
        
    Returns:
        Plain text follow-up email draft
    """
    raise NotImplementedError("Phase 7: Implement follow-up email generation")
