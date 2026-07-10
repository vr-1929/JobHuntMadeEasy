"""
RemoteOK and Remotive API integration for remote jobs.
Status: Placeholder for Phase 2
"""
import logging

logger = logging.getLogger(__name__)


def search_remoteok(
    keywords: list,
    max_results: int = 50,
) -> list:
    """
    Search RemoteOK for remote jobs matching keywords.
    """
    raise NotImplementedError("Phase 2: Implement RemoteOK API integration")


def search_remotive(
    keywords: list,
    max_results: int = 50,
) -> list:
    """
    Search Remotive for remote jobs matching keywords.
    """
    raise NotImplementedError("Phase 2: Implement Remotive API integration")
