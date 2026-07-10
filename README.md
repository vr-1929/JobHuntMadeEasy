# Job App OS - Personal AI Job Application Automation

A sophisticated, single-user web application that automates your daily job search workflow using AI to tailor resumes and cover letters.

## 📋 Table of Contents

- [What It Does](#what-it-does)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Project Code Overview](#project-code-overview)
- [Troubleshooting](#troubleshooting)

## What It Does

1. **Morning check-in**: Tell it "Find N applications today"
2. **Smart job search**: Searches multiple legitimate job APIs matching your resume skills (US-wide, all location types)
3. **AI tailoring**: For each job, extracts key requirements and generates:
   - A **tailored resume** (LaTeX → PDF) that mirrors the job description language without inventing experience
   - A **tailored cover letter** (200-300 words, company-specific)
4. **Review queue**: You see the JD, resume diff, cover letter, and decide: Approve & Apply, Edit, or Skip
5. **Semi-automated application**: Either submits directly (if API available) or opens a pre-filled browser session for your final click
6. **Tracking dashboard**: Logs all applications with status (Applied, Interviewing, Rejected, Offer, Ghosted)
7. **Interview prep** (on-demand): Generates likely questions + talking points
8. **Follow-ups** (on-demand): Generates professional follow-up emails
9. **Analytics**: Response rates by role type, keyword match %, resume version, weekly application volume

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Streamlit
- **Database**: SQLite (designed for Postgres migration later)
- **LLM**: Provider-agnostic wrapper (default: Google Gemini API - free tier)
- **Job Sources**: Adzuna, USAJobs, RemoteOK, Greenhouse, Lever, Remotive APIs (all free/public)
- **Resume compilation**: LaTeX (pdflatex or tectonic)
- **Browser automation**: Playwright (for review + semi-automated apply)

## Prerequisites

Before starting, ensure you have:

- **Python 3.11 or higher** - [Download](https://www.python.org/downloads/)
- **Git** (optional, for cloning the repo) - [Download](https://git-scm.com/)
- **LaTeX compiler** - One of:
  - **Windows**: [MiKTeX](https://miktex.org/download) or [Tectonic](https://tectonic-typesetting.github.io/)
  - **macOS**: `brew install mactex` (or [MacTeX](https://www.tug.org/mactex/))
  - **Linux**: `sudo apt-get install texlive-full` or equivalent
- **API Keys** (free tier available for all):
  - Google Gemini API (recommended) - https://ai.google.dev
  - Optional: Anthropic, Groq, OpenRouter

## Installation & Setup

### Step 1: Clone and Navigate to Project

```bash
# If cloning from repository
git clone <repo-url>
cd JobAppWebApp

# OR if already in the project directory
cd c:\Users\vedra\OneDrive\Desktop\JobAppWebApp  # Windows
# or
cd ~/Desktop/JobAppWebApp  # macOS/Linux
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# Install Playwright browsers (for future automation features)
playwright install chromium
```

### Step 4: Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env          # macOS/Linux
# or on Windows:
copy .env.example .env

# Edit .env with your API keys (see Environment Configuration below)
```

### Step 5: Initialize Database

```bash
# Run the test pipeline which initializes everything
python test_pipeline.py
```

## Environment Configuration

### Step 1: Get Your API Keys

#### Google Gemini API (Recommended - Free)
1. Go to https://ai.google.dev
2. Click **"Get API key"** button
3. Sign in with your Google account (instant, no payment method required)
4. Copy the API key

#### Alternative LLM Providers

**Anthropic Claude:**
- https://console.anthropic.com
- Free trial ($5 credits)
- Good for production quality text

**Groq (Fast & Free):**
- https://console.groq.com
- Free tier with generous limits
- Excellent for rapid prototyping

**OpenRouter (Multi-model):**
- https://openrouter.ai
- Pay-as-you-go pricing
- Access to multiple AI models

### Step 2: Configure `.env` File

Edit `c:\Users\vedra\OneDrive\Desktop\JobAppWebApp\.env` (Windows) or `~/JobAppWebApp/.env`:

```env
# LLM Configuration (choose one provider)
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
ANTHROPIC_API_KEY=  # Leave blank if not using
GROQ_API_KEY=       # Leave blank if not using
OPENROUTER_API_KEY= # Leave blank if not using

# Job Search API Keys (optional for Phase 2+)
ADZUNA_APP_ID=your_adzuna_id
ADZUNA_APP_KEY=your_adzuna_key
USAJOBS_API_KEY=your_usajobs_key
USAJOBS_EMAIL=your_email@example.com

# Application Settings
DATABASE_URL=sqlite:///./data/jobapp.db
MAX_APPLICATIONS_PER_DAY=10
MIN_MATCH_SCORE=50
DEBUG=false
```

### Step 3: Verify Installation

Test that everything is working:

```bash
# Run the complete pipeline test
python test_pipeline.py

# Expected output shows all steps passing:
# ✓ Database initialized
# ✓ Master resume seeded
# ✓ Master resume compiled to PDF
# ... (more steps)
# ✓ PIPELINE TEST COMPLETE
```

Check that the following files were created:
- `data/jobapp.db` - SQLite database
- `backend/resume/templates/master_resume.pdf`
- `backend/resume/templates/app_1_*.pdf` - Tailored resume

## Project Structure

```
JobAppWebApp/
├── backend/
│   ├── models.py                 # SQLAlchemy models
│   ├── db.py                     # Database setup
│   ├── config.py                 # Configuration
│   ├── crud.py                   # Database operations
│   ├── ai/
│   │   ├── llm_client.py         # Provider-agnostic LLM wrapper
│   │   ├── keyword_extraction.py # Extract skills from JD
│   │   ├── gap_analysis.py       # Compare JD vs resume
│   │   ├── resume_tailoring.py   # Generate tailored resume
│   │   ├── cover_letter.py       # Generate cover letter
│   │   ├── follow_up.py          # Generate follow-up emails
│   │   └── interview_prep.py     # Interview preparation
│   ├── job_sources/
│   │   ├── adzuna.py             # Adzuna job board integration
│   │   ├── usajobs.py            # USAJobs integration
│   │   ├── remotive.py           # Remotive API
│   │   ├── greenhouse.py         # Greenhouse API
│   │   └── lever.py              # Lever API
│   ├── resume/
│   │   ├── compile.py            # LaTeX to PDF compiler
│   │   ├── master_resume.tex     # Master resume template
│   │   └── templates/            # Generated PDFs
│   └── apply/
│       └── playwright_runner.py   # Semi-automated form filling
├── frontend/
│   └── app.py                    # Streamlit web UI
├── data/
│   └── jobapp.db                 # SQLite database (generated)
├── test_pipeline.py              # End-to-end integration test
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (create from .env.example)
├── .env.example                  # Template for environment variables
├── .gitignore                    # Git ignore patterns
└── README.md                     # This file
```

## Running the Application

### Option 1: Run the Complete Pipeline Test (Recommended First Step)

This validates everything is working end-to-end:

```bash
# Activate virtual environment first
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Run the test
python test_pipeline.py
```

**What this does:**
1. Initializes SQLite database
2. Seeds your master resume
3. Compiles it to PDF (validates LaTeX)
4. Extracts keywords from sample job description
5. Runs gap analysis
6. Generates tailored resume
7. Compiles tailored resume to PDF
8. Generates cover letter
9. Saves everything to database

**Expected output:**
```
==================================================
JOB APP OS - END-TO-END PIPELINE TEST
==================================================

[Step 1] Initializing database...
✓ Database initialized
[Step 2] Seeding master resume...
✓ Master resume seeded
[Step 3] Compiling master resume to PDF...
✓ Master resume compiled: backend/resume/templates/master_resume.pdf
[Step 4] Processing sample job description...
  Job Title: AI/ML Platform Engineer
  Company: TechCorp AI
[Step 5] Extracting keywords from job description...
✓ Keywords extracted (12 found)
[Step 6] Analyzing gaps between master resume and job...
✓ Gap analysis complete
[Step 7] Generating tailored resume...
✓ Tailored resume generated
[Step 8] Compiling tailored resume to PDF...
✓ Tailored resume compiled: backend/resume/templates/app_1_AI_ML_Platform_Startup.pdf
[Step 9] Generating cover letter...
✓ Cover letter generated
[Step 10] Saving application to database...
✓ Application saved (ID: 1)

==================================================
✓ PIPELINE TEST COMPLETE
==================================================

Generated Files:
  📄 Master Resume: backend/resume/templates/master_resume.pdf
  📄 Tailored Resume: backend/resume/templates/app_1_AI_ML_Platform_Startup.pdf
  📊 Database: data/jobapp.db
```

### Option 2: Run Interactive Streamlit App (UI)

For a web-based interface:

```bash
streamlit run frontend/app.py
```

Then open http://localhost:8501 in your browser.

*(Note: Frontend is under development in Phase 4)*

### Option 3: Run FastAPI Backend Server

For REST API access:

```bash
uvicorn backend.main:app --reload --port 8000
```

Then access:
- API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

*(Note: Backend API routes are under development)*

## Project Code Overview

### 1. Database Models (`backend/models.py`)

SQLAlchemy models for data persistence:

```python
from sqlalchemy import Column, String, Text, DateTime, Integer, Enum
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class MasterProfile(Base):
    """Your base resume and candidate information"""
    __tablename__ = "master_profiles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    email = Column(String)
    phone = Column(String)
    location = Column(String)
    resume_latex = Column(Text)  # Your master resume in LaTeX
    created_at = Column(DateTime, default=datetime.utcnow)

class Application(Base):
    """Each job application record"""
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("master_profiles.id"))
    job_title = Column(String)
    company = Column(String)
    job_description = Column(Text)
    status = Column(Enum(...))  # Applied, Interviewing, Rejected, etc.
    tailored_resume_latex = Column(Text)
    cover_letter = Column(Text)
    match_score = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 2. LLM Client Wrapper (`backend/ai/llm_client.py`)

Provider-agnostic interface to multiple LLM providers:

```python
import os
from abc import ABC, abstractmethod
import json
from dotenv import load_dotenv

load_dotenv()

class LLMClient(ABC):
    """Abstract base for all LLM providers"""
    
    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: str = "", 
                     temperature: float = 0.7, max_tokens: int = 2048) -> str:
        pass
    
    @abstractmethod
    def generate_json(self, prompt: str, system_prompt: str = "", 
                     temperature: float = 0.5, max_tokens: int = 2048) -> dict:
        pass

class GeminiClient(LLMClient):
    """Google Gemini API implementation"""
    
    def __init__(self):
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
    
    def generate_text(self, prompt: str, system_prompt: str = "", 
                     temperature: float = 0.7, max_tokens: int = 2048) -> str:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = self.model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        return response.text
    
    def generate_json(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.5,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """Generate and parse JSON using Gemini."""
        json_prompt = f"{prompt}\n\nRespond ONLY with valid JSON, no markdown or other text."
        text = self.generate_text(json_prompt, system_prompt, temperature, max_tokens)
        try:
            return _parse_json_response(text)
        except Exception as e:
            logger.error(f"Failed to parse JSON response: {text}")
            raise

class AnthropicClient(LLMClient):
    """Anthropic Claude implementation"""
    
    def __init__(self):
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate_text(self, prompt: str, system_prompt: str = "", 
                     temperature: float = 0.7, max_tokens: int = 2048) -> str:
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt if system_prompt else None,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    
    def generate_json(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.5,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """Generate and parse JSON using Gemini."""
        json_prompt = f"{prompt}\n\nRespond ONLY with valid JSON, no markdown or other text."
        text = self.generate_text(json_prompt, system_prompt, temperature, max_tokens)
        try:
            return _parse_json_response(text)
        except Exception as e:
            logger.error(f"Failed to parse JSON response: {text}")
            raise

# Factory function to get the right client
def get_llm_client() -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider == "gemini":
        return GeminiClient()
    elif provider == "anthropic":
        return AnthropicClient()
    elif provider == "groq":
        from groq import Groq
        return GroqClient()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
```

### 3. Keyword Extraction (`backend/ai/keyword_extraction.py`)

```python
from backend.ai.llm_client import get_llm_client
import json

def extract_keywords(job_description: str, max_keywords: int = 15) -> list:
    """Extract and rank keywords from job description"""
    
    client = get_llm_client()
    
    prompt = f"""
    Analyze this job description and extract 10-15 key skills, technologies, 
    and qualifications. Rank them by importance (1-10).
    
    Job Description:
    {job_description}
    
    Return ONLY valid JSON with this structure:
    [
        {{"keyword": "Python", "category": "language", "importance": 9}},
        {{"keyword": "FastAPI", "category": "framework", "importance": 8}},
        ...
    ]
    """
    
    keywords = client.generate_json(prompt)
    return sorted(keywords, key=lambda x: x['importance'], reverse=True)

# Example usage:
if __name__ == "__main__":
    job_desc = """
    We're hiring a Senior Python Backend Engineer. Requirements:
    - 5+ years Python experience
    - FastAPI or Django
    - SQL databases (PostgreSQL preferred)
    - AWS or Google Cloud
    - REST API design
    """
    
    keywords = extract_keywords(job_desc)
    for kw in keywords:
        print(f"{kw['keyword']} ({kw['importance']}/10) - {kw['category']}")
```

### 4. Gap Analysis (`backend/ai/gap_analysis.py`)

```python
from backend.ai.llm_client import get_llm_client

def analyze_gaps(resume_text: str, job_keywords: list) -> dict:
    """Compare resume against job keywords"""
    
    client = get_llm_client()
    
    keywords_str = "\n".join([kw['keyword'] for kw in job_keywords])
    
    prompt = f"""
    Given this resume and these job requirements, classify each keyword:
    
    Resume:
    {resume_text}
    
    Job Keywords:
    {keywords_str}
    
    For each keyword, respond with:
    - "matched": Already clearly in resume
    - "missing_reword": You have equivalent experience, just needs rephrasing
    - "missing_flagged": Not present (do NOT add to resume)
    
    Return JSON:
    {{
        "matched": ["Python", "FastAPI"],
        "missing_reword": [
            {{"keyword": "CI/CD", "equivalent_text": "automated deployment pipeline"}}
        ],
        "missing_flagged": ["Kubernetes"]
    }}
    """
    
    analysis = client.generate_json(prompt)
    return analysis

# Example usage:
if __name__ == "__main__":
    resume = "5 years Python, built REST APIs with FastAPI, deployed on AWS..."
    keywords = [
        {"keyword": "Python", "importance": 9},
        {"keyword": "FastAPI", "importance": 8},
        {"keyword": "Kubernetes", "importance": 6},
    ]
    
    gaps = analyze_gaps(resume, keywords)
    print("Matched:", gaps['matched'])
    print("Can Reword:", gaps['missing_reword'])
    print("Missing (flagged):", gaps['missing_flagged'])
```

### 5. Resume Tailoring (`backend/ai/resume_tailoring.py`)

```python
from backend.ai.llm_client import get_llm_client
from backend.ai.gap_analysis import analyze_gaps

def tailor_resume(master_resume_latex: str, job_description: str, 
                 job_keywords: list) -> str:
    """Generate a tailored resume for this job"""
    
    # First, understand what needs to change
    gaps = analyze_gaps(master_resume_latex, job_keywords)
    
    client = get_llm_client()
    
    prompt = f"""
    Tailor this LaTeX resume to better match this job, without adding false skills.
    
    Master Resume (LaTeX):
    {master_resume_latex}
    
    Job Description:
    {job_description}
    
    Keywords That Should Be Highlighted:
    {', '.join(gaps['matched'])}
    
    Keywords to Reword Existing Bullets:
    {str(gaps['missing_reword'])}
    
    DO NOT mention: {', '.join(gaps['missing_flagged'])}
    
    Return ONLY the modified LaTeX resume. Keep formatting identical. Only reword bullets.
    """
    
    tailored = client.generate_text(prompt)
    return tailored
```

### 6. Database Connection (`backend/db.py`)

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from backend.models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/jobapp.db")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database and create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized")

def get_session() -> Session:
    """Get a new database session"""
    return SessionLocal()

# Example usage:
if __name__ == "__main__":
    init_db()
    session = get_session()
    # ... perform database operations ...
    session.close()
```

## Troubleshooting

### Common Issues & Solutions

#### 1. "ModuleNotFoundError: No module named 'sqlalchemy'"

**Problem**: Virtual environment dependencies not installed

**Solution**:
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

# Install requirements
pip install -r requirements.txt

# Verify installation
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
```

#### 2. "pdflatex not found" or "xlatex not found"

**Problem**: LaTeX compiler not installed

**Solution** (choose one):

**Option A - MiKTeX (Windows recommended)**
1. Download from https://miktex.org/download
2. Install with default settings
3. Test: `pdflatex --version`

**Option B - Homebrew (macOS)**
```bash
brew install mactex
# May take 10+ minutes
pdflatex --version
```

**Option C - Linux**
```bash
sudo apt-get update
sudo apt-get install texlive-full
pdflatex --version
```

**Option D - Tectonic (Cross-platform, Python)**
```bash
pip install tectonic
tectonic --version
```

#### 3. "GEMINI_API_KEY not set in .env"

**Problem**: Missing or incorrect API key

**Solution**:
1. Go to https://ai.google.dev
2. Click **"Get API key"** button
3. Verify you're signed in to Google account
4. Click **"Create API key in new project"**
5. Copy the long key (starts with `AIzaSy...`)
6. Paste into `.env`:
   ```env
   GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXX
   ```
7. Save file and retry

**Verify**:
```bash
python -c "from backend.ai.llm_client import GeminiClient; GeminiClient()"
```

#### 4. "Failed to parse JSON response" or Invalid JSON

**Problem**: LLM returned malformed JSON

**Solution**:
```bash
# Check your API key is correct
echo %GEMINI_API_KEY%  # Windows
echo $GEMINI_API_KEY   # macOS/Linux

# Try with a different provider
# Edit .env:
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key

# Or try Groq (very reliable for JSON):
LLM_PROVIDER=groq
GROQ_API_KEY=your_key
```

#### 5. "Database is locked" or SQLite errors

**Problem**: Database file is locked or corrupted

**Solution**:
```bash
# Delete and reinitialize
rm data/jobapp.db
python test_pipeline.py

# Or if Windows:
del data\jobapp.db
python test_pipeline.py
```

#### 6. LaTeX compilation errors (PDF not generated)

**Problem**: Resume has invalid LaTeX syntax

**Solution**:
1. Check for non-ASCII characters (use UTF-8 encoding)
2. Look at error log:
   ```bash
   cat backend/resume/templates/*.log  # Find error details
   ```
3. Common issues:
   - Missing `\documentclass`
   - Unmatched `{` or `}`
   - Invalid command syntax
   - Special characters without escaping

#### 7. "Playwright not found" or browser errors

**Problem**: Playwright browsers not installed

**Solution**:
```bash
# Install Playwright browsers
playwright install chromium

# Verify
python -c "from playwright.sync_api import sync_playwright; print('OK')"
```

#### 8. Port already in use (Port 8000 or 8501)

**Problem**: Another process is using the port

**Solution - Option A: Kill existing process**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

**Solution - Option B: Use different port**
```bash
# FastAPI on different port
uvicorn backend.main:app --port 8001

# Streamlit on different port
streamlit run frontend/app.py --server.port 8502
```

#### 9. Virtual environment issues

**Problem**: `venv` is broken or has conflicting packages

**Solution - Complete reset**:
```bash
# Remove old venv
rm -rf venv  # macOS/Linux
# or on Windows:
rmdir /s venv

# Create fresh venv
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall
pip install --upgrade pip
pip install -r requirements.txt
```

#### 10. Still having issues?

**Debug steps**:
```bash
# Check Python version (should be 3.11+)
python --version

# Check installed packages
pip list | grep -E "sqlalchemy|fastapi|streamlit|pydantic"

# Enable debug mode in .env
DEBUG=true

# Run test with verbose output
python -u test_pipeline.py 2>&1 | tee debug.log

# Check environment variables are loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('GEMINI_API_KEY')[:10])"
```

---

## How It Works: The AI Pipeline

### 1. Keyword Extraction (from job description)

**Input**: Job description text
**Output**: 10-15 ranked keywords (skills, tools, frameworks, qualifications)

Example:
```json
[
  {"keyword": "Python", "category": "language", "importance": 10},
  {"keyword": "FastAPI", "category": "framework", "importance": 9},
  {"keyword": "AWS", "category": "tool", "importance": 8}
]
```

### 2. Gap Analysis (master resume vs job keywords)

**Input**: Extracted keywords + master resume
**Output**: Keywords classified as:
- `matched`: Already in resume
- `missing_reword`: You have equivalent experience, just needs rephrasing
- `missing_flagged`: Not in resume — will NOT be added to avoid false claims

Example:
```json
{
  "matched": ["Python", "FastAPI"],
  "missing_reword": [{"keyword": "CI/CD", "equivalent": "automated deployment"}],
  "missing_flagged": ["Kubernetes"]
}
```

### 3. Resume Tailoring (LaTeX customization)

**Input**: Master LaTeX resume + gap analysis
**Output**: Tailored LaTeX resume

**What it does:**
- Preserves exact: employment dates, company names, job titles
- Rewords bullet points to surface matched keywords
- Never adds missing_flagged keywords
- Keeps to 1 page
- Avoids repetitive AI patterns (varied sentence structure, natural phrasing)

Example diff:
```
BEFORE:
  - Deployed ML models using distributed systems

AFTER:
  - Built and deployed ML models using Docker containers and Kubernetes orchestration
  (because gap analysis said Kubernetes is "missing_reword")
```

### 4. Cover Letter Generation

**Input**: Company name, role, job description, master resume
**Output**: 200-300 word professional cover letter

Includes:
- Company-specific opening
- 2-3 references to specific job requirements
- 1-2 relevant project/experience callouts
- Clear call to action

---

## LLM Provider Setup

The app is designed to work with any LLM provider. Switch via `LLM_PROVIDER` in `.env`:

### Gemini (Default - Recommended for Phase 1-3)
- **Provider**: Google Gemini API
- **Model**: `gemini-2.5-flash`
- **Cost**: Free (1,500+ requests/day on free tier)
- **Sign-up**: https://ai.google.dev
- **Setup**: `LLM_PROVIDER=gemini` + `GEMINI_API_KEY=...`

### Anthropic Claude
- **Cost**: Free credit (~$5), then paid
- **Sign-up**: https://console.anthropic.com
- **Setup**: `LLM_PROVIDER=anthropic` + `ANTHROPIC_API_KEY=...`

### Groq (Fast alternative)
- **Cost**: Free tier available
- **Sign-up**: https://console.groq.com
- **Setup**: `LLM_PROVIDER=groq` + `GROQ_API_KEY=...`

### OpenRouter (Multi-model)
- **Cost**: Pay-as-you-go
- **Sign-up**: https://openrouter.ai
- **Setup**: `LLM_PROVIDER=openrouter` + `OPENROUTER_API_KEY=...`

**To switch providers**, only edit `.env` — no code changes needed.

---

## Development Roadmap

- **Phase 1** ✓ Foundation (models, DB, config)
- **Phase 2** ⏳ Job search APIs (Adzuna, Greenhouse, etc.)
- **Phase 3** ✓ AI pipeline (extraction, gap analysis, tailoring, cover letter)
- **Phase 4** 🔄 Streamlit UI (daily check-in, review queue)
- **Phase 5** 📋 Apply flow (Playwright semi-auto fill)
- **Phase 6** 📊 Dashboard & analytics
- **Phase 7** 🎯 Interview prep & follow-ups
- **Phase 8+** Optional: job search APIs, scheduled jobs, advanced analytics

---

## Database Schema

See [backend/models.py](backend/models.py) for full schema. Key tables:

- **MasterProfile**: Your base resume + candidate info
- **Application**: Each job application (status, tailored materials, scores)
- **FollowUp**: Generated follow-up emails per application
- **InterviewPrep**: Interview questions & talking points per role

---

## Notes on Design Decisions

1. **Why "Review Queue" instead of fully unattended auto-apply?**
   - **ToS risk**: LinkedIn, Indeed, Workday explicitly prohibit automated scraping and bot submission. Violating ToS can get your account suspended — which hurts your job search more than it helps.
   - **Resume accuracy**: An unreviewed pipeline that silently "adds missing keywords" drifts into claiming skills you don't have. That becomes a legal/professional liability in an interview.
   - **Solution**: Manual review gate at apply step keeps you in control and every submission is something you'd stand behind.

2. **Why LaTeX instead of Word/Google Docs?**
   - Precise formatting control
   - Easy version control (git-friendly text format)
   - Programmatic generation (edit bullet points via code)
   - Professional typesetting

3. **Why SQLite instead of Postgres immediately?**
   - Single-user, local-first: no networking overhead
   - Zero setup, zero ops
   - Models designed for easy Postgres migration later (just change `DATABASE_URL`)

4. **Why provider-agnostic LLM wrapper?**
   - Gemini is free but rate-limited
   - Anthropic is more capable but costly
   - Groq is fast
   - OpenRouter aggregates many models
   - Easy to switch based on daily budget/needs without rewriting prompts

---

## Contributing / Customization

- **Prompts**: Edit [backend/ai/*.py](backend/ai/) to tune extraction, gap analysis, resume rewording
- **Job sources**: Add new job board APIs to [backend/job_sources/](backend/job_sources/)
- **Resume template**: Replace `master_resume.tex` in [backend/models.py](backend/models.py) with your own LaTeX
- **UI**: Streamlit code in [frontend/app.py](frontend/app.py) (Phase 4)

---

## License

Personal project for your own use. Feel free to modify and extend.

---

## Support / Next Steps

1. **Get API keys** (see [Environment Configuration](#environment-configuration))
2. **Run `test_pipeline.py`** to validate everything works
3. **Review generated PDFs** in `backend/resume/templates/`
4. **Check database** with SQLite browser: `data/jobapp.db`
5. **Start Phase 4**: Build the Streamlit UI for daily workflow

---

Questions? Check the project briefs in the repo root for full context on design decisions.
#   J o b H u n t M a d e E a s y  
 