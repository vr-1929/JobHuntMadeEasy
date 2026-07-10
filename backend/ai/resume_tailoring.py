"""
Resume tailoring: generate customized LaTeX resume per job.
"""
import logging
from typing import Dict, Any, List
from backend.ai.llm_client import get_llm_client
import json

logger = logging.getLogger(__name__)


def tailor_resume(
    master_resume_latex: str,
    job_description: str,
    gap_analysis: Dict[str, Any],
    role_title: str,
    company_name: str,
) -> str:
    """
    Generate a tailored LaTeX resume for a specific job.
    Preserves exact employment dates, company names, job titles.
    Rewords bullet points only where gap analysis permits.
    Keeps to 1 page.
    Avoids AI-written patterns (repetitive --, uniform sentence rhythm).

    Args:
        master_resume_latex: Base LaTeX resume
        job_description: Full job description
        gap_analysis: Output from analyze_gaps()
        role_title: Target job title
        company_name: Target company name

    Returns:
        Full valid LaTeX resume text, ready to compile
    """
    client = get_llm_client()

    system_prompt = """You are an expert resume writer and LaTeX specialist.
Your goal: tailor a resume to match a job description WITHOUT inventing experience.

CRITICAL RULES:
1. PRESERVE EXACTLY: employment dates (month/year), company names, job titles
2. REWORD ONLY bullet points, and only where gap analysis permits ("reword_and_add")
3. Mirror job description language ONLY if truthful per gap analysis
4. Keep 1 page - if necessary, remove least-relevant content, don't add
5. AVOID AI patterns: don't use repetitive "--" or "●", don't start every bullet with same verb
6. Use natural human phrasing: varied sentence structure, different openers
7. For "missing_flagged" keywords: DO NOT add them. Leave them out.
8. Output ONLY valid LaTeX code. No commentary. Must compile with pdflatex.
9. Your output MUST be a complete document: it must start with \\documentclass
   and end with \\end{document}. Never stop partway through.

When rewriting bullets:
- Keep core facts identical
- Change wording to surface relevant keywords
- Example: "deployed ML models" → "deployed ML models using Docker and Kubernetes pipelines"
  (only if gap analysis says Kubernetes is "reword_and_add")
"""

    gap_analysis_json = json.dumps(gap_analysis, indent=2)

    prompt = f"""Tailor this master resume for a candidate applying to:
ROLE: {role_title}
COMPANY: {company_name}

Use this gap analysis to guide which keywords to surface:
{gap_analysis_json}

Master Resume (LaTeX):
{master_resume_latex}

Job Description:
{job_description}

Generate the tailored LaTeX resume. Ensure it compiles and is exactly 1 page.
Preserve all employment dates, company names, and job titles exactly.
Only reword bullet points where gap analysis permits.
Return ONLY valid LaTeX code, no other text. The document must be complete,
starting with \\documentclass and ending with \\end{{document}}."""

    def _is_complete(latex: str) -> bool:
        return "\\documentclass" in latex and "\\end{document}" in latex

    try:
        # Bumped from 3500 -> 9000. The master resume alone is roughly
        # 2,000-2,500 tokens, and the model has to return a comparably-sized
        # full LaTeX document, not just a diff. 3500 was truncating the
        # output before it ever reached \end{document}.
        tailored_latex = client.generate_text(
            prompt,
            system_prompt,
            temperature=0.7,
            max_tokens=9000
        )

        if not _is_complete(tailored_latex):
            logger.warning(
                "Generated LaTeX missing expected document markers "
                "(likely truncated) — retrying once with a stricter prompt."
            )
            retry_prompt = (
                prompt
                + "\n\nIMPORTANT: Your previous attempt was incomplete or cut off. "
                "Be concise in bullet wording so the FULL document fits. "
                "Do not omit \\end{document}."
            )
            tailored_latex = client.generate_text(
                retry_prompt,
                system_prompt,
                temperature=0.5,
                max_tokens=9000,
            )

            if not _is_complete(tailored_latex):
                # Give up gracefully rather than silently handing broken
                # LaTeX to the compiler — fall back to the master resume
                # untouched so the pipeline can still proceed.
                logger.error(
                    "Tailored LaTeX still incomplete after retry; "
                    "falling back to master resume unmodified."
                )
                return master_resume_latex

        logger.info(f"Resume tailored for {company_name} - {role_title}")
        return tailored_latex
    except Exception as e:
        logger.error(f"Resume tailoring failed: {e}")
        raise