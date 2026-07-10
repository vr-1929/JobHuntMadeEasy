# Phase 2 Roadmap: Job Search API Integration

After Phase 1-3 (foundation + AI pipeline), Phase 2 integrates multiple job board APIs to search for roles automatically.

## Overview

**Goal**: Search multiple job boards simultaneously, find roles matching your skills, and store results in the database for Phase 4 (UI) to process.

**Inputs**:
- Target keywords (Python, FastAPI, AWS, etc. — from `config.py`)
- Location filter (USA only)
- Max results desired

**Outputs**:
- List of deduplicated jobs in the `applications` table with status `found`
- Match score calculated (keyword overlap between job description and your resume)

---

## APIs to Integrate (in order of priority)

### 1. **Adzuna** (HIGH PRIORITY - Broad Coverage)

**What**: Job aggregator covering 1000+ job boards
**Docs**: https://developer.adzuna.com/docs
**Authentication**: App ID + App Key (free)
**Rate limit**: 100 requests/day on free tier

**File**: `backend/job_sources/adzuna.py`

**Implementation**:
```python
def search_adzuna(keywords: list, location="USA", max_results=50) -> list:
    # 1. Build query string from keywords (OR together)
    # 2. Call https://api.adzuna.com/v1/search/1
    #    - country=us
    #    - location0=<country_code>
    #    - what=<keyword1> <keyword2> ...
    #    - results_per_page=<max>
    # 3. Parse response, extract:
    #    - title, company, description, redirect_url, location, salary_min, salary_max, posted_date
    # 4. Return list of job dicts
    # 5. Log API call for debugging
```

**Test**:
```bash
python -c "from backend.job_sources.adzuna import search_adzuna; results = search_adzuna(['Python', 'FastAPI'], max_results=5); print(len(results), 'jobs found')"
```

### 2. **Greenhouse** (HIGH PRIORITY - Tech Companies)

**What**: Job board used by 1000+ companies (Stripe, Anthropic, etc.)
**Docs**: https://developers.greenhouse.io/job-board-api.html
**Authentication**: None! Public API
**Rate limit**: Generous

**File**: `backend/job_sources/greenhouse.py`

**Implementation**:
```python
def search_greenhouse(company_names: list, max_results=50) -> list:
    # 1. For each company name:
    #    - Call https://boards-api.greenhouse.io/v1/boards/{company}/jobs
    # 2. Parse response, extract:
    #    - title, department, offices[], updated_at, absolute_url
    #    - Fetch full description from absolute_url or parse from API
    # 3. Return aggregated list
```

**Common tech company boards**:
- stripe, anthropic, openai, databricks, retool, figma, etc.
- Maintain a list in `config.py` for easy expansion

### 3. **Lever** (HIGH PRIORITY - Tech Companies)

**What**: Similar to Greenhouse, used by many startups
**Docs**: https://github.com/lever/postings-api
**Authentication**: None! Public API
**Rate limit**: Generous

**File**: `backend/job_sources/lever.py`

**Implementation**:
```python
def search_lever(company_names: list, max_results=50) -> list:
    # 1. For each company name:
    #    - Call https://api.lever.co/v0/postings/{company}
    # 2. Parse response
    # 3. Filter/search via keywords
```

### 4. **RemoteOK + Remotive** (MEDIUM PRIORITY - Remote-First)

**What**: Aggregators of remote-only jobs
**Docs**: https://remoteok.com/api, https://remotive.com/api
**Authentication**: None! Public APIs
**Rate limit**: Generous

**File**: `backend/job_sources/remotive.py`

**Implementation**:
```python
def search_remoteok(keywords, max_results=50) -> list:
    # Call https://remoteok.io/api
    # Filter for keywords in title/description
    
def search_remotive(keywords, max_results=50) -> list:
    # Call https://remotive.com/api/all-jobs/
    # Filter for keywords
```

### 5. **USAJobs** (MEDIUM PRIORITY - Federal/Government)

**What**: Official US government job postings
**Docs**: https://developer.usajobs.gov
**Authentication**: API Key + email (free signup)
**Rate limit**: 2 requests/second

**File**: `backend/job_sources/usajobs.py`

**Implementation**:
```python
def search_usajobs(keywords, max_results=50) -> list:
    # 1. Call https://data.usajobs.gov/api/search
    #    - Require API key in headers
    #    - Search for keywords
    # 2. Parse response
    # 3. Filter to US locations
```

---

## Common Implementation Pattern

Each job source module should follow this pattern:

```python
import logging
import requests
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

def search_<source>(keywords: List[str], max_results: int = 50) -> List[Dict[str, Any]]:
    """
    Search <source> for jobs matching keywords.
    
    Args:
        keywords: List of skill keywords to search
        max_results: Max results to return
        
    Returns:
        List of job dicts with keys:
        - title: Job title
        - company: Company name
        - description: Job description text (full or summary)
        - url: Link to job posting
        - location: Location (city, state, or "Remote")
        - location_type: "remote", "onsite", or "hybrid"
        - salary: Salary info if available
        - posted_date: When posted (ISO format if possible)
        - source: "adzuna", "greenhouse", etc.
    """
    try:
        # 1. Build API request
        # 2. Make request with try/except for network errors
        # 3. Parse response
        # 4. Return standardized job list
        
        logger.info(f"Found {len(jobs)} jobs from {source}")
        return jobs
        
    except requests.RequestException as e:
        logger.error(f"{source} API error: {e}")
        return []  # Return empty list on error, don't crash
    except Exception as e:
        logger.error(f"Unexpected error in {source}: {e}")
        return []
```

---

## Integration with Existing Codebase

### 1. **Job Aggregator** (`backend/job_aggregator.py` — NEW)

Create a master function that calls all enabled sources in parallel:

```python
import asyncio
from backend.job_sources import adzuna, greenhouse, lever, remotive, usajobs

async def search_all_jobs(keywords: list, max_results: int = 10) -> list:
    """
    Search all enabled job sources in parallel.
    Deduplicates by (company, title).
    Ranks by match score.
    Returns top N.
    """
    tasks = [
        asyncio.create_task(adzuna.search_adzuna(keywords, max_results=20)),
        asyncio.create_task(greenhouse.search_greenhouse(TECH_COMPANIES, max_results=20)),
        asyncio.create_task(lever.search_lever(TECH_COMPANIES, max_results=20)),
        asyncio.create_task(remotive.search_remoteok(keywords, max_results=20)),
        asyncio.create_task(remotive.search_remotive(keywords, max_results=20)),
        asyncio.create_task(usajobs.search_usajobs(keywords, max_results=20)),
    ]
    
    results = await asyncio.gather(*tasks)
    all_jobs = [job for source_jobs in results for job in source_jobs]
    
    # Deduplicate: same company + title = same job
    unique_jobs = {}
    for job in all_jobs:
        key = (job['company'].lower(), job['title'].lower())
        if key not in unique_jobs:
            unique_jobs[key] = job
    
    # Rank by match score
    # (TODO: implement keyword match scoring)
    ranked = sorted(unique_jobs.values(), key=lambda j: j.get('match_score', 0), reverse=True)
    
    return ranked[:max_results]
```

### 2. **CRUD for Applications** (`backend/crud.py` — NEW)

```python
from sqlalchemy.orm import Session
from backend.models import Application

def create_applications_from_jobs(db: Session, jobs: list, master_profile_id: int):
    """
    Bulk insert jobs from search into applications table.
    Check for duplicates first (company + title + source).
    Set status = "found".
    """
    for job in jobs:
        existing = db.query(Application).filter(
            Application.company_name == job['company'],
            Application.role_title == job['title'],
            Application.source == job['source'],
        ).first()
        
        if not existing:
            app = Application(
                master_profile_id=master_profile_id,
                company_name=job['company'],
                role_title=job['title'],
                job_url=job['url'],
                job_description_raw=job['description'],
                source=job['source'],
                location_type=job['location_type'],
                location_text=job['location'],
                status='found',
                match_score=job.get('match_score', 0),
            )
            db.add(app)
    
    db.commit()
```

### 3. **Match Scoring** (`backend/ai/match_scoring.py` — NEW)

Simple keyword matching (more sophisticated version in Phase 6):

```python
def calculate_match_score(job_description: str, keywords: list) -> float:
    """
    Simple match score: % of keywords found in job description.
    Range: 0-100
    """
    description_lower = job_description.lower()
    matches = sum(1 for kw in keywords if kw.lower() in description_lower)
    return (matches / len(keywords) * 100) if keywords else 0
```

---

## Testing Phase 2

### Unit Tests

Create `test_job_sources.py`:

```python
def test_adzuna_search():
    jobs = adzuna.search_adzuna(['Python'], max_results=5)
    assert len(jobs) > 0
    assert 'title' in jobs[0]
    assert 'company' in jobs[0]
    
def test_greenhouse_search():
    jobs = greenhouse.search_greenhouse(['stripe', 'anthropic'], max_results=5)
    assert len(jobs) > 0
    
def test_deduplication():
    # Ensure same job from multiple sources doesn't create duplicates
    pass
```

### Integration Test

```bash
python -c "
from backend.job_aggregator import search_all_jobs
import asyncio

jobs = asyncio.run(search_all_jobs(['Python', 'FastAPI'], max_results=20))
print(f'Found {len(jobs)} unique jobs')
for job in jobs[:5]:
    print(f'  - {job[\"company\"]}: {job[\"title\"]} ({job[\"source\"]})')
"
```

---

## Configuration

Add to `backend/config.py`:

```python
# Job Search
TECH_COMPANIES = [
    'stripe', 'anthropic', 'openai', 'databricks', 'retool',
    'figma', 'notion', 'linear', 'zepeto', 'together',
]

ENABLED_JOB_SOURCES = [
    'adzuna',
    'greenhouse',
    'lever',
    'remoteok',
    'remotive',
    'usajobs',
]

MIN_MATCH_SCORE = int(os.getenv("MIN_MATCH_SCORE", "50"))
```

---

## Implementation Checklist

- [ ] Adzuna integration + test
- [ ] Greenhouse integration + test
- [ ] Lever integration + test
- [ ] RemoteOK + Remotive integration + test
- [ ] USAJobs integration + test
- [ ] Job aggregator (parallel search, deduplication)
- [ ] CRUD functions for bulk insert
- [ ] Match scoring
- [ ] Error handling + retry logic
- [ ] Logging and debugging
- [ ] Integration test (search_all_jobs works)
- [ ] Update config with tech companies list
- [ ] Rate limiting / backoff strategy

---

## Known Challenges

1. **Rate limits**: Some APIs have strict limits. Use caching or backoff.
2. **Duplicate job descriptions**: Different boards post the same job. Use company+title as key.
3. **Parsing variability**: Each API returns different fields. Normalize to standard schema.
4. **Location filtering**: Some APIs don't filter well. Do client-side filtering.
5. **Salary info**: Not always available. Mark as null when missing.
6. **Async errors**: Network failures mid-request. Use try/except + return empty list.

---

## Next Steps After Phase 2

Once job search is working:

1. **Phase 4 (UI)**: Build Streamlit interface to trigger job search and review
2. **Phase 3.5 (Match Scoring)**: Improve scoring with LLM-based relevance ranking
3. **Phase 5 (Auto-Apply)**: Semi-automated application submission

---

## Files to Create/Edit

```
backend/
├── job_sources/
│   ├── adzuna.py          (implement)
│   ├── greenhouse.py      (implement)
│   ├── lever.py           (implement)
│   ├── remotive.py        (implement)
│   ├── usajobs.py         (implement)
│   └── __init__.py        (add exports)
├── job_aggregator.py      (NEW - parallel search)
├── crud.py                (NEW - database CRUD)
└── ai/
    └── match_scoring.py   (NEW - keyword matching)
```

---

## Resources

- **Adzuna**: https://developer.adzuna.com/overview
- **Greenhouse**: https://developers.greenhouse.io/job-board-api.html
- **Lever**: https://github.com/lever/postings-api
- **RemoteOK**: https://remoteok.io/api
- **Remotive**: https://remotive.com/api
- **USAJobs**: https://developer.usajobs.gov
- **Async patterns in Python**: https://docs.python.org/3/library/asyncio.html

---

Ready to implement? Start with Adzuna (easiest) and Greenhouse (most relevant), then expand to others.
