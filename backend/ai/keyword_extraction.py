"""
Keyword extraction from job descriptions.
"""
import logging
from typing import Any, Dict, List

from backend.ai.llm_client import get_llm_client

logger = logging.getLogger(__name__)


def _fallback_keywords(job_description: str, role_title: str, company_name: str) -> List[Dict[str, Any]]:
    text = f"{role_title} {company_name} {job_description}".lower()
    preferred = [
        "python", "fastapi", "sql", "postgres", "docker",
        "kubernetes", "aws", "api", "microservices",
        "testing", "ci/cd", "observability"
    ]
    keywords = []
    for term in preferred:
        if term.lower() in text:
            keywords.append({
                "keyword": term.title(),
                "category": "language" if term.lower() in {"python"} else "skill",
                "importance": 8,
                "context": f"Relevant to {role_title}"
            })
    return keywords[:10]


def extract_keywords(job_description: str, role_title: str, company_name: str) -> List[Dict[str, Any]]:
    """
    Extract the 10-15 most important required skills/tools/qualifications from a job description.
    Returns a list of keywords ranked by importance.
    """
    client = get_llm_client()

    system_prompt = """You are an expert recruiter analyzing job descriptions to extract key requirements.
Your task is to identify the most important skills, tools, frameworks, and qualifications.
Never invent or assume requirements not explicitly mentioned.
Return structured JSON only, no other text."""

    prompt = f"""Analyze this job description for {role_title} at {company_name}.
Extract the 10-15 most important required skills, tools, frameworks, and qualifications.
Rank them by importance (10 = most critical, 1 = nice-to-have).

Job Description:
{job_description}

Return a JSON array with objects containing:
- "keyword": the skill/tool/framework/qualification name
- "category": one of "skill", "tool", "framework", "qualification", "language"
- "importance": 1-10 ranking
- "context": brief excerpt (under 15 words) showing why it's required

Example format:
[
  {{"keyword": "Python", "category": "language", "importance": 10, "context": "Strong Python programming experience required"}},
  {{"keyword": "FastAPI", "category": "framework", "importance": 9, "context": "Experience building APIs with FastAPI"}}
]"""

    try:
        # Bumped from 1500 -> 4096. Asking for 10-15 full objects (each with a
        # keyword, category, importance, and context string) is a lot of JSON
        # output — 1500 tokens was truncating this almost every time, which is
        # why only 1 keyword was coming back instead of 10-15.
        keywords_data = client.generate_json(prompt, system_prompt, temperature=0.5, max_tokens=4096)
        if isinstance(keywords_data, dict):
            keywords_data = keywords_data.get("keywords", [])
        if not isinstance(keywords_data, list):
            keywords_data = []
    except Exception as exc:
        logger.warning("LLM keyword extraction failed, using fallback keywords: %s", exc)
        keywords_data = _fallback_keywords(job_description, role_title, company_name)

    logger.info("Extracted %d keywords from %s - %s", len(keywords_data), company_name, role_title)
    return keywords_data