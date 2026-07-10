"""
Adzuna job search API integration.
Status: Placeholder for Phase 2
"""
import logging

logger = logging.getLogger(__name__)


def search_adzuna(
    keywords: list,
    location: str = "USA",
    max_results: int = 50,
) -> list:
    """
    Search Adzuna for jobs matching keywords.
    
    Args:
        keywords: List of search keywords (e.g., ["Python", "FastAPI"])
        location: Location filter (default: USA)
        max_results: Max results to return
        
    Returns:
        List of job dicts with keys: title, company, url, description, location, salary
    """
    raise NotImplementedError("Phase 2: Implement Adzuna API integration")
