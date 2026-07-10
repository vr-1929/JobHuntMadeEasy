"""
Greenhouse job board API integration.
Status: Placeholder for Phase 2
"""
import logging

logger = logging.getLogger(__name__)


def search_greenhouse(
    company_names: list,
    max_results: int = 50,
) -> list:
    """
    Search Greenhouse job boards for specific companies.
    
    Many tech companies publish their open positions at:
    https://boards-api.greenhouse.io/v1/boards/{company}/jobs
    
    Args:
        company_names: List of company names to search (e.g., ["stripe", "anthropic"])
        max_results: Max results to return
        
    Returns:
        List of job dicts with keys: title, company, url, description, location
    """
    raise NotImplementedError("Phase 2: Implement Greenhouse API integration")
