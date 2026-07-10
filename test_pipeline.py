"""
End-to-end test of the AI tailoring pipeline.
Run this after setting up .env to validate the full workflow.

Usage:
    python test_pipeline.py

This will:
1. Initialize the database
2. Seed master resume
3. Process a sample job description
4. Generate keyword extraction, gap analysis, tailored resume, and cover letter
5. Compile resume to PDF
6. Save everything to the database
"""
import logging
import json
from datetime import datetime
from backend.db import init_db, get_session
from backend.models import MasterProfile, Application
from backend.ai.keyword_extraction import extract_keywords
from backend.ai.gap_analysis import analyze_gaps
from backend.ai.resume_tailoring import tailor_resume
from backend.ai.cover_letter import generate_cover_letter
from backend.resume.compile import compile_tailored_resume, compile_master_resume

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Master resume from project brief
MASTER_RESUME_LATEX = r"""
\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\input{glyphtounicode}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\addtolength{\oddsidemargin}{-0.6in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1.19in}
\addtolength{\topmargin}{-.7in}
\addtolength{\textheight}{1.4in}

\urlstyle{same}
\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large\bfseries
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

\pdfgentounicode=1

\newcommand{\resumeItem}[1]{
  \item\small{{#1 \vspace{-2pt}}}
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      #1 & \small #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{1.001\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & \textbf{\small #2}\\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeCoursework}[1]{
  \item\small{
    \emph{Coursework:} #1 \vspace{-2pt}
  }
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemi{$\vcenter{\hbox{\tiny$\bullet$}}$}
\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.0in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}[leftmargin=0.15in]}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}

%----------HEADING----------
\begin{center}
    {\huge \scshape \textbf{Ved Raval}} \\ \vspace{1pt}
    \small Green Card Holder $|$ Allentown, NJ (Open to Relocate) $|$ +1 (331) 291-3082 $|$
    \href{mailto:ved.raval.official@gmail.com}{\underline{ved.raval.official@gmail.com}} $|$
    \href{https://www.linkedin.com/in/ved-raval-1905p/}{\underline{LinkedIn}} $|$
    \href{https://leetcode.com/u/Ved1905/}{\underline{LeetCode}}
    \vspace{-8pt}
\end{center}

%-----------EDUCATION-----------
\section{Education}
\resumeSubHeadingListStart
  \resumeSubheading
    {\textbf{Ahmedabad University} $|$ \emph{B.Tech in Computer Science \& Engineering}}{\textbf{2022 - 2026}}{}{}
    \vspace{-18pt}
    \resumeCoursework{LLMs \& Applications, Deep Learning, ML, NLP, Computer Vision, Distributed Systems, Cloud Computing, DSA, Software Engineering}
    \vspace{-10pt}
    \resumeItemListStart
      \resumeItem{JEE Mains 96th Percentile $|$ JEE Advanced AIR Under 25,000}
    \resumeItemListEnd
\resumeSubHeadingListEnd
\vspace{-18pt}

%-----------EXPERIENCE-----------
\section{Experience}
\resumeSubHeadingListStart

  \resumeSubheading
    {\textbf{Swiftforce.AI} $|$ \emph{AI Python Developer \& Engineer}}{Allentown, NJ $|$ \textbf{Nov 2025 - Present}}{}{}
    \vspace{-18pt}
    \resumeItemListStart
      \resumeItem{Designed and shipped a full-stack HIPAA-compliant AI system integrating \textbf{GPT-4 API} across omnichannel patient touchpoints (web, SMS, voice); built \textbf{Python FastAPI} backend with a \textbf{React} front-end, processing \textbf{1,000+ daily interactions} at sub-200ms p95 latency}
      \resumeItem{Engineered ML-powered \textbf{Python} API data-mapping pipeline: omnichannel intake $\rightarrow$ AI triage engine $\rightarrow$ CRM schema $\rightarrow$ \textbf{Snowflake}/EHR writes; applied chain-of-thought prompt logic achieving \textbf{95\% intent classification accuracy}, reducing operational overhead by \textbf{40\%}}
      \resumeItem{Built production \textbf{AWS Lambda} + \textbf{EC2} backend services; \textbf{Redis} semantic caching cut LLM API costs \textbf{30\%}; enforced HIPAA-aligned security patterns (PHI field encryption, rate limiting, JWT auth) with \textbf{85\% automated test coverage} and \textbf{99.9\% uptime}}
      \resumeItem{Triaged and resolved production ML pipeline issues by tracing root causes across service layers (AWS infra, Python runtime, API integrations); added telemetry and alerting to prevent recurrence}
    \resumeItemListEnd

  \resumeSubheading
    {\textbf{Sensegood Instruments Pvt. Ltd.} $|$ \emph{Machine Learning Intern}}{Ahmedabad, India $|$ \textbf{Apr 2025 - Sept 2025}}{}{}
    \vspace{-18pt}
    \resumeItemListStart
      \resumeItem{Built \textbf{Python} genetic algorithm + \textbf{scikit-learn} optimization system processing millions of spectral data points; reduced raw material costs \textbf{20\%} and improved color accuracy \textbf{15\%}}
      \resumeItem{Engineered scalable \textbf{Python} ML data pipeline with automated validation and real-time monitoring; cut data processing time \textbf{35\%} and accelerated model iteration cycles}
    \resumeItemListEnd

  \resumeSubheading
    {\textbf{Ahmedabad University} $|$ \emph{Software Engineering Teaching Assistant}}{Ahmedabad, India $|$ \textbf{Jan 2026 - May 2026}}{}{}
    \vspace{-18pt}
    \resumeItemListStart
      \resumeItem{Mentored \textbf{150+ students} on clean code, Git, Python testing, and debugging; conducted regular code reviews enforcing best practices around accuracy, testability, and efficiency}
    \resumeItemListEnd

\resumeSubHeadingListEnd
\vspace{-16pt}

%-----------PROJECTS-----------
\section{Projects}
    \vspace{-5pt}
    \resumeSubHeadingListStart

      \resumeProjectHeading
        {\textbf{Multimodal AI for 6G Wireless Networks} $|$ \emph{Python, TensorFlow, LiDAR, AWS}}{MICXN Lab $|$ Dec 2023 - Dec 2024}
        \resumeItemListStart
          \resumeItem{Built multimodal deep learning system fusing LiDAR and visual data via cross-modal attention; achieved \textbf{96\% Top-5 beam prediction accuracy} and cut system overhead \textbf{92\%} via optimized \textbf{AWS} preprocessing for low-latency vehicular inference}
        \resumeItemListEnd

      \vspace{-16pt}
      \resumeProjectHeading
        {\textbf{Secure Multi-Tenant AI Platform} $|$ \emph{Python, Docker, Kubernetes, AWS S3}}{}
        \resumeItemListStart
          \resumeItem{Architected \textbf{Python}-driven platform on \textbf{AWS} (\textbf{Docker} + \textbf{Kubernetes}) for \textbf{15+ concurrent} data scientists with dynamic GPU allocation and JupyterHub; enforced RBAC, network isolation, and audit logging for multi-tenant data governance}
        \resumeItemListEnd

      \vspace{-16pt}
      \resumeProjectHeading
        {\textbf{Computer Vision \& Pose Estimation} $|$ \emph{Python, PyTorch, HRNet-W48}}{Thesis $|$ Aug 2025 - Present}
        \resumeItemListStart
          \resumeItem{Fine-tuning \textbf{HRNet-W48} in \textbf{PyTorch} for cultural heritage Human Pose Estimation (\textbf{0.84 OKS@0.5}); resolved convergence issues via transfer + curriculum learning and Human-in-the-Loop active learning with CVAT}
        \resumeItemListEnd

    \resumeSubHeadingListEnd
\vspace{-16pt}

%-----------TECHNICAL SKILLS-----------
\section{Technical Skills}
\begin{itemize}[leftmargin=0.15in, label={}]
  \small{\item{
    \textbf{Languages}{: Python (Advanced), C++, Java, Go, JavaScript, SQL} \\
    \textbf{AI \& ML}{: PyTorch, TensorFlow, GPT-4/5, LangChain, RAG, Fine-tuning, HuggingFace Transformers, Scikit-learn} \\
    \textbf{Backend \& APIs}{: FastAPI, Flask, REST, WebSockets, Microservices, Async Python, Prompt Engineering} \\
    \textbf{Cloud \& DevOps}{: AWS (Lambda, EC2, S3, SageMaker), Docker, Kubernetes, CI/CD, Serverless, Monitoring} \\
    \textbf{Data \& Security}{: Snowflake, PostgreSQL, MongoDB, Redis, Pinecone, ETL Pipelines, HIPAA/PHI, RBAC, Encryption}
  }}
\end{itemize}
\vspace{-18pt}

%-----------ACHIEVEMENTS-----------
\section{Achievements}
\resumeItemListStart
  \resumeItem{Ranked \textbf{1st} at Optimized Minds ML Competition 2025 (96\% train / 89\% test accuracy), outperforming \textbf{50+ competitors} via ensemble methods and Bayesian hyperparameter search}
  \vspace{-5pt}
  \resumeItem{\textbf{AWS} Cloud Foundations \& Architecture $|$ \textbf{Harvard CS50x} (edX) $|$ \textbf{IEEE} AI/ML Workshop - Data Modeling \& Analytics}
\resumeItemListEnd

\end{document}
"""

# Sample job description for testing
SAMPLE_JOB_DESCRIPTION = """
Senior Backend Engineer - AI/ML Platform

About the Role:
We're looking for an experienced Backend Engineer to join our AI/ML platform team. You'll architect and build robust, scalable APIs that power our machine learning infrastructure serving thousands of concurrent users.

Key Responsibilities:
- Design and implement REST APIs using FastAPI for our ML training platform
- Build data pipelines that process terabytes of data daily
- Implement Redis caching strategies to optimize API response times
- Deploy and maintain services on AWS using Docker and Kubernetes
- Work with our ML team to integrate PyTorch models into production systems
- Ensure HIPAA compliance and implement security best practices
- Write comprehensive unit and integration tests (pytest)

Required Qualifications:
- 5+ years of backend development experience with Python
- Strong proficiency in FastAPI and async Python programming
- Experience with AWS (Lambda, EC2, S3, RDS)
- Knowledge of Docker and Kubernetes
- Experience with relational databases (PostgreSQL) and Redis
- Familiarity with CI/CD pipelines and monitoring
- Understanding of data structures and algorithms

Nice to Have:
- Experience with PyTorch or other ML frameworks
- Knowledge of LLMs and RAG systems
- Experience with microservices architecture
- Contributions to open-source projects

Location: Remote (US)
Salary: $180K - $240K + equity
"""


def main():
    logger.info("=" * 80)
    logger.info("JOB APP OS - END-TO-END PIPELINE TEST")
    logger.info("=" * 80)

    # Step 1: Initialize database
    logger.info("\n[Step 1] Initializing database...")
    init_db()

    # Step 2: Seed master resume
    logger.info("[Step 2] Seeding master resume...")
    db = get_session()

    existing_profile = db.query(MasterProfile).first()
    if not existing_profile:
        profile = MasterProfile(resume_latex=MASTER_RESUME_LATEX)
        db.add(profile)
        db.commit()
        logger.info("✓ Master resume seeded")
    else:
        logger.info("✓ Master resume already exists")
        profile = existing_profile

    # Step 3: Compile master resume as sanity check
    logger.info("\n[Step 3] Compiling master resume...")
    pdf_path = compile_master_resume(MASTER_RESUME_LATEX)
    if pdf_path:
        logger.info(f"✓ Master resume PDF: {pdf_path}")
    else:
        logger.warning("⚠ Master resume PDF compilation failed (but continuing)")

    # Step 4: Extract keywords from job description
    logger.info("\n[Step 4] Extracting keywords from job description...")
    try:
        keywords = extract_keywords(
            SAMPLE_JOB_DESCRIPTION,
            "Senior Backend Engineer",
            "AI/ML Platform Startup"
        )
        logger.info(f"✓ Extracted {len(keywords)} keywords")
        logger.info(f"  Top 3: {json.dumps(keywords[:3], indent=2)}")
    except Exception as e:
        logger.error(f"✗ Keyword extraction failed: {e}")
        return

    # Step 5: Gap analysis
    logger.info("\n[Step 5] Running gap analysis...")
    try:
        gap_analysis = analyze_gaps(keywords, MASTER_RESUME_LATEX, SAMPLE_JOB_DESCRIPTION)
        logger.info(f"✓ Gap analysis complete")
        logger.info(f"  Matched: {len(gap_analysis.get('matched', []))}")
        logger.info(f"  To reword: {len(gap_analysis.get('missing_reword', []))}")
        logger.info(f"  Flagged: {len(gap_analysis.get('missing_flagged', []))}")
    except Exception as e:
        logger.error(f"✗ Gap analysis failed: {e}")
        return

    # Step 6: Tailor resume
    logger.info("\n[Step 6] Tailoring resume...")
    try:
        tailored_latex = tailor_resume(
            MASTER_RESUME_LATEX,
            SAMPLE_JOB_DESCRIPTION,
            gap_analysis,
            "Senior Backend Engineer",
            "AI/ML Platform Startup"
        )
        logger.info(f"✓ Resume tailored ({len(tailored_latex)} chars)")
    except Exception as e:
        logger.error(f"✗ Resume tailoring failed: {e}")
        return

    # Step 7: Compile tailored resume
    logger.info("\n[Step 7] Compiling tailored resume...")
    try:
        tailored_pdf = compile_tailored_resume(
            tailored_latex,
            1,  # temp application_id
            "AI/ML Platform Startup"
        )
        if tailored_pdf:
            logger.info(f"✓ Tailored PDF: {tailored_pdf}")
        else:
            logger.warning("⚠ Tailored PDF compilation failed")
    except Exception as e:
        logger.error(f"⚠ Tailored PDF compilation error: {e}")

    # Step 8: Generate cover letter
    logger.info("\n[Step 8] Generating cover letter...")
    try:
        cover_letter = generate_cover_letter(
            "AI/ML Platform Startup",
            "Senior Backend Engineer",
            SAMPLE_JOB_DESCRIPTION,
            MASTER_RESUME_LATEX,
        )
        logger.info(f"✓ Cover letter generated")
        logger.info(f"\n--- COVER LETTER PREVIEW ---")
        logger.info(cover_letter[:500] + "..." if len(cover_letter) > 500 else cover_letter)
    except Exception as e:
        logger.error(f"✗ Cover letter generation failed: {e}")
        return

    # Step 9: Save to database
    logger.info("\n[Step 9] Saving application to database...")
    try:
        app = Application(
            master_profile_id=profile.id,
            company_name="AI/ML Platform Startup",
            role_title="Senior Backend Engineer",
            job_url="https://example.com/jobs/123",
            job_description_raw=SAMPLE_JOB_DESCRIPTION,
            source="manual",
            location_type="remote",
            location_text="Remote (US)",
            status="reviewed",
            match_score=85.0,
            keywords_matched=[k.get("keyword") for k in gap_analysis.get("matched", [])],
            keywords_missing_added=[k.get("keyword") for k in gap_analysis.get("missing_reword", [])],
            keywords_missing_flagged=[k.get("keyword") for k in gap_analysis.get("missing_flagged", [])],
            tailored_resume_latex=tailored_latex,
            tailored_resume_pdf_path=tailored_pdf if tailored_pdf else None,
            tailored_cover_letter=cover_letter,
        )
        db.add(app)
        db.commit()
        logger.info(f"✓ Application saved (ID: {app.id})")
    except Exception as e:
        logger.error(f"✗ Database save failed: {e}")
        db.rollback()
        return

    logger.info("\n" + "=" * 80)
    logger.info("✓ PIPELINE TEST COMPLETE")
    logger.info("=" * 80)
    logger.info(f"\nGenerated Files:")
    logger.info(f"  - Database: data/jobapp.db")
    logger.info(f"  - Master Resume PDF: backend/resume/templates/master_resume.pdf")
    logger.info(f"  - Tailored Resume PDF: {tailored_pdf if tailored_pdf else 'NOT COMPILED'}")
    logger.info(f"\nNext Steps:")
    logger.info(f"  1. Review the generated PDFs")
    logger.info(f"  2. Check cover letter content in database")
    logger.info(f"  3. Set your API keys in .env and test with real job descriptions")
    logger.info(f"  4. Start building the Streamlit UI (Phase 4)")

    db.close()


if __name__ == "__main__":
    main()
