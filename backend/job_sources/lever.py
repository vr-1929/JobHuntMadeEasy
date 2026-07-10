"""
Lever job board API integration.
Status: Placeholder for Phase 2
"""
import logging

logger = logging.getLogger(__name__)


def search_lever(
    company_names: list,
    max_results: int = 50,
) -> list:
    """
    Search Lever job boards for specific companies.
    
    Many companies publish their open positions at:
    https://api.lever.co/v0/postings/{company}
    
    Args:
        company_names: List of company names to search (e.g., ["openai", "anthropic"])
        max_results: Max results to return
        
    Returns:
        List of job dicts with keys: title, company, url, description, location
    """
    raise NotImplementedError("Phase 2: Implement Lever API integration")
