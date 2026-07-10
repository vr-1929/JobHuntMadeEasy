"""
Gap analysis: compare job requirements against master resume.
"""
import json
import logging
from typing import List, Dict, Any
from backend.ai.llm_client import get_llm_client

logger = logging.getLogger(__name__)


def analyze_gaps(
    extracted_keywords: List[Dict[str, Any]],
    master_resume_latex: str,
    job_description: str,
) -> Dict[str, Any]:
    """
    Compare extracted keywords against master resume.
    For each keyword, classify as:
    - reword_and_add: I have equivalent/adjacent real experience, just needs rephrasing
    - flag_for_review: I have no clear equivalent experience

    Args:
        extracted_keywords: List from keyword_extraction()
        master_resume_latex: Full LaTeX resume
        job_description: Full job description

    Returns:
        Dict with:
        - matched: keywords present in resume
        - missing_reword: keywords to reword existing experience for
        - missing_flagged: keywords not in resume, needs user input
    """
    client = get_llm_client()

    system_prompt = """You are an expert career coach and resume writer.
Your job is to map job requirements to real candidate experience.
CRITICAL: Never invent or claim skills not clearly present in the resume.
If there's genuine doubt, flag it for manual review instead of guessing.
Return structured JSON only."""

    keywords_json = json.dumps(extracted_keywords, indent=2)

    prompt = f"""Analyze this candidate's master resume and compare it against job requirements.
For each required keyword, classify it as:
1. "matched": The keyword or clear equivalent is in the resume
2. "reword_and_add": The candidate has related/adjacent experience that can be legitimately reworded to match the keyword
3. "flag_for_review": The candidate has no clear equivalent - do NOT claim it, flag it instead

Master Resume (LaTeX):
{master_resume_latex}

Required Keywords from Job Description:
{keywords_json}

Return a JSON object with this structure:
{{
  "matched": [
    {{"keyword": "Python", "context": "Found in technical skills and multiple projects", "resume_sections": ["Technical Skills", "Swiftforce.AI experience"]}}
  ],
  "missing_reword": [
    {{"keyword": "CI/CD", "equivalent_from_resume": "automated test coverage + deployment in Swiftforce experience", "suggested_rewording": "Implemented CI/CD pipelines for automated testing and deployment"}}
  ],
  "missing_flagged": [
    {{"keyword": "Kubernetes", "reason": "Not found in resume, no clear adjacent experience"}}
  ],
  "analysis_notes": "Brief overall assessment of fit"
}}"""

    try:
        gap_analysis = client.generate_json(prompt, system_prompt, temperature=0.5, max_tokens=2000)
        logger.info(f"Gap analysis complete: {len(gap_analysis.get('matched', []))} matched, "
                   f"{len(gap_analysis.get('missing_reword', []))} to reword, "
                   f"{len(gap_analysis.get('missing_flagged', []))} flagged")
        return gap_analysis
    except Exception as e:
        logger.error(f"Gap analysis failed: {e}")
        raise
