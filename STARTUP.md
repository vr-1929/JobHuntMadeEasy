# Job App OS - Quick Start Guide

## 🚀 Getting Started (5-10 minutes)

### Step 1: Set Up Python Environment

```bash
cd JobAppWebApp
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Install LaTeX (for resume PDF compilation)

Choose ONE of these based on your OS:

**macOS:**
```bash
brew install mactex
# Or lighter weight: brew install basictex
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install texlive-full
# Or just the essentials: sudo apt-get install texlive-latex-base texlive-latex-extra
```

**Windows:**
- Download and install [MiKTeX](https://miktex.org/download)
- OR (cross-platform fallback): `pip install tectonic` (automatic if pdflatex not found)

**Verify installation:**
```bash
pdflatex --version
# Should print version info. If not found, install from above.
```

### Step 3: Get API Keys (3 minutes)

#### 🔑 Gemini API (Recommended - Free)
1. Go to https://ai.google.dev
2. Click "Get API key"
3. Sign in with Google account
4. Copy the key

#### 🔑 Adzuna API (Free - for Phase 2 job search)
1. Go to https://developer.adzuna.com
2. Sign up for free
3. Create an app to get App ID and App Key

#### 🔑 USAJobs API (Free - for Phase 2 job search)
1. Go to https://developer.usajobs.gov
2. Request API access
3. Get your API key and use your email

**All other job board APIs** (RemoteOK, Greenhouse, Lever, Remotive) are public — no key needed!

### Step 4: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

```
LLM_PROVIDER=gemini
GEMINI_API_KEY=<paste-your-key-here>
ADZUNA_APP_ID=<your-app-id>
ADZUNA_APP_KEY=<your-app-key>
USAJOBS_API_KEY=<your-api-key>
USAJOBS_EMAIL=ved.raval.official@gmail.com
```

**⚠️ IMPORTANT**: Never commit `.env` to Git — it's already in `.gitignore`.

### Step 5: Test the Pipeline ✅

Run the end-to-end test:

```bash
python test_pipeline.py
```

**Expected output** (~2-3 minutes):
```
==================================================
JOB APP OS - END-TO-END PIPELINE TEST
==================================================

[Step 1] Initializing database...
✓ Database initialized
[Step 2] Seeding master resume...
✓ Master resume seeded
[Step 3] Compiling master resume...
✓ Master resume PDF: backend/resume/templates/master_resume.pdf
[Step 4] Extracting keywords from job description...
✓ Extracted 12 keywords
[Step 5] Running gap analysis...
✓ Gap analysis complete
[Step 6] Tailoring resume...
✓ Resume tailored
[Step 7] Compiling tailored resume...
✓ Tailored PDF: backend/resume/templates/app_1_AI_ML_Platform_Startup.pdf
[Step 8] Generating cover letter...
✓ Cover letter generated
[Step 9] Saving application to database...
✓ Application saved (ID: 1)

==================================================
✓ PIPELINE TEST COMPLETE
==================================================

Generated Files:
  - Database: data/jobapp.db
  - Master Resume PDF: backend/resume/templates/master_resume.pdf
  - Tailored Resume PDF: backend/resume/templates/app_1_AI_ML_Platform_Startup.pdf
```

### Step 6: Check Generated Files

Open these in a PDF viewer to inspect the output:
- `backend/resume/templates/master_resume.pdf` (your unedited resume)
- `backend/resume/templates/app_1_AI_ML_Platform_Startup.pdf` (tailored for the sample job)

Verify:
- ✓ Master resume compiles without errors
- ✓ Tailored resume looks reasonable (same structure, updated bullet points)
- ✓ Both fit on 1 page
- ✓ No hallucinated experience

### Step 7: Check Database

Open the SQLite database to see saved data:

**Option A: Use a GUI (easiest)**
- Download [DB Browser for SQLite](https://sqlitebrowser.org)
- Open `data/jobapp.db`
- Browse the `applications` table

**Option B: Use CLI**
```bash
sqlite3 data/jobapp.db
> SELECT company_name, role_title, match_score, status FROM applications;
```

---

## 📋 What's Working (Phase 1-3)

- ✅ Database setup (SQLAlchemy + SQLite)
- ✅ Master resume seeding
- ✅ LLM client (provider-agnostic: Gemini, Anthropic, Groq, OpenRouter)
- ✅ Keyword extraction from job descriptions
- ✅ Gap analysis (matching resume skills vs job requirements)
- ✅ Resume tailoring (preserves dates/titles, rewords bullets)
- ✅ Cover letter generation
- ✅ LaTeX → PDF compilation
- ✅ Full pipeline test with sample job description

---

## 🔄 What's Next (Phase 2-7)

### Phase 2: Job Search APIs
Integrate job board APIs to search for roles automatically:
- [ ] Adzuna API
- [ ] USAJobs API
- [ ] RemoteOK / Remotive
- [ ] Greenhouse / Lever boards

**Files to edit**: `backend/job_sources/*.py`

### Phase 3: Complete (✅ You're here!)

### Phase 4: Streamlit UI
Build the daily workflow interface:
- [ ] Morning check-in ("Find N applications")
- [ ] Job search trigger
- [ ] Review queue (show JD, resume diff, cover letter)
- [ ] Approve/Edit/Skip buttons

**File to create**: `frontend/app.py`

**Command**: `streamlit run frontend/app.py`

### Phase 5: Semi-Automated Apply
Playwright-based form filling:
- [ ] Detect application form fields
- [ ] Auto-fill name, email, phone, resume, cover letter
- [ ] Pause for user to review/submit
- [ ] Log "applied" status

**File to edit**: `backend/apply/playwright_runner.py`

### Phase 6: Dashboard & Analytics
Track all applications:
- [ ] Status tracking (Applied → Interviewing → Rejected / Offer)
- [ ] Response rate charts
- [ ] Match score distribution
- [ ] Applications per week

### Phase 7: Interview Prep & Follow-Ups
On-demand AI assistance:
- [ ] Generate likely interview questions
- [ ] Talking points from your resume
- [ ] Follow-up email drafts

---

## 🐛 Troubleshooting

### "pdflatex not found"
```
❌ error: pdflatex not found. Install with: pip install tectonic
```
**Fix**: Install a LaTeX distribution (see Step 2 above)

### "GEMINI_API_KEY not set in .env"
```
❌ ValueError: GEMINI_API_KEY not set in .env
```
**Fix**: 
1. Go to https://ai.google.dev
2. Get your API key
3. Paste it in `.env` as `GEMINI_API_KEY=...`

### "Failed to parse JSON response"
```
❌ Failed to parse JSON response: ...
```
**Fix**: Usually means the LLM didn't return valid JSON. Try:
- Use a different provider (Anthropic or Groq may be more stable)
- Shorten the job description input
- Check your API key is correct

### "sqlite3.OperationalError: database is locked"
```
❌ sqlite3.OperationalError: database is locked
```
**Fix**: Another process has the database open. Close DB Browser or other sqlite sessions.

### "ModuleNotFoundError: No module named 'backend'"
```
❌ ModuleNotFoundError: No module named 'backend'
```
**Fix**: Make sure you're in the project root directory when running Python:
```bash
cd JobAppWebApp  # Make sure you're in this directory
python test_pipeline.py
```

---

## 📁 Project Layout After First Run

```
job-app-os/
├── .env                          # Your API keys (DO NOT COMMIT)
├── backend/
│   ├── models.py
│   ├── db.py
│   ├── config.py
│   ├── ai/
│   │   ├── llm_client.py         # LLM provider wrapper
│   │   ├── keyword_extraction.py
│   │   ├── gap_analysis.py
│   │   ├── resume_tailoring.py
│   │   ├── cover_letter.py
│   │   ├── interview_prep.py     # (Phase 7)
│   │   └── follow_up.py          # (Phase 7)
│   ├── job_sources/              # (Phase 2)
│   ├── resume/
│   │   ├── compile.py
│   │   └── templates/
│   │       ├── master_resume.pdf         # ✓ Generated
│   │       └── app_1_*.pdf               # ✓ Generated
│   └── apply/                    # (Phase 5)
├── frontend/
│   └── app.py                    # (Phase 4 - not yet)
├── data/
│   └── jobapp.db                 # ✓ Generated (SQLite database)
├── venv/
│   └── ...                       # Python virtual environment
├── .env                          # ✓ Created (from .env.example)
├── test_pipeline.py              # ✓ Test script
├── requirements.txt
├── README.md
└── STARTUP.md                    # You are here
```

---

## 💡 Tips for Development

### Logging
To see debug info, set `DEBUG=true` in `.env`:
```
DEBUG=true
```

Then check terminal output for detailed logs from LLM calls, database operations, etc.

### Testing with Real Job Descriptions
Instead of using the hardcoded sample in `test_pipeline.py`, you can:
1. Find a real job posting
2. Copy the full job description
3. Replace `SAMPLE_JOB_DESCRIPTION` in `test_pipeline.py` with your text
4. Re-run: `python test_pipeline.py`

### Customizing Your Resume
Your master resume is stored in the database. To change it:

**Option 1: Edit in database**
- Use DB Browser for SQLite
- Find `master_profile` table
- Edit the `resume_latex` field directly

**Option 2: Edit in code**
- Edit `MASTER_RESUME_LATEX` in `test_pipeline.py`
- Delete `data/jobapp.db` to force reseed
- Re-run: `python test_pipeline.py`

### Switching LLM Providers
Just change `LLM_PROVIDER` in `.env` and re-run:
```
# Use Anthropic Claude instead of Gemini
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Then run test again:
python test_pipeline.py
```

No code changes needed — the abstraction handles it!

---

## 📊 Monitoring Database

Check what's stored after running the test:

```bash
sqlite3 data/jobapp.db

# List all applications
sqlite> SELECT id, company_name, role_title, match_score, status FROM applications;

# See the tailored resume for app #1
sqlite> SELECT tailored_resume_latex FROM applications WHERE id=1;

# See the cover letter
sqlite> SELECT tailored_cover_letter FROM applications WHERE id=1;

# Exit
sqlite> .quit
```

---

## ✅ Verification Checklist

After completing the startup, verify:

- [ ] Python virtual environment activated (`venv/bin/activate`)
- [ ] All packages installed (`pip list | grep -E fastapi|streamlit|sqlalchemy`)
- [ ] LaTeX installed and working (`pdflatex --version`)
- [ ] `.env` file exists with Gemini API key
- [ ] `python test_pipeline.py` runs without errors
- [ ] `data/jobapp.db` created
- [ ] PDF files generated in `backend/resume/templates/`
- [ ] Database has 1 application record

If all ✓, you're ready to move to Phase 2 (job search APIs)!

---

## 🎯 Next Step: Build Phase 4 (UI)

Once you've verified everything works, start building the Streamlit UI:

```bash
# Create frontend/app.py with Streamlit
# Then run:
streamlit run frontend/app.py
```

This will build out the daily workflow: morning check-in → job search → review queue → apply.

---

## 📚 Documentation

- **Full project brief**: See the GitHub Copilot Chat message you pasted (all 9 sections)
- **Database schema**: `backend/models.py`
- **LLM setup**: `backend/ai/llm_client.py`
- **Configuration**: `backend/config.py`
- **README**: `README.md` (full feature overview)

---

Questions? Check the README or project brief for more context!
