"""
Configuration management for Job App OS.
Loads settings from environment variables and defaults.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central configuration for the application."""

    # LLM Settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

    # Job Search API Keys
    ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
    ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
    USAJOBS_API_KEY = os.getenv("USAJOBS_API_KEY")
    USAJOBS_EMAIL = os.getenv("USAJOBS_EMAIL")

    # Application Settings
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/jobapp.db")
    MAX_APPLICATIONS_PER_DAY = int(os.getenv("MAX_APPLICATIONS_PER_DAY", "10"))
    MIN_MATCH_SCORE = int(os.getenv("MIN_MATCH_SCORE", "50"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Target Keywords for Job Search (configurable list)
    # Edit this to customize which roles you're looking for
    TARGET_KEYWORDS = [
        "Python",
        "FastAPI",
        "Backend",
        "Machine Learning",
        "LLM",
        "RAG",
        "AWS",
        "API",
        "Data Pipeline",
        "Docker",
        "Kubernetes",
    ]

    # Candidate Profile (used for form auto-fill)
    CANDIDATE_NAME = "Ved Raval"
    CANDIDATE_EMAIL = "ved.raval.official@gmail.com"
    CANDIDATE_PHONE = "+1 (331) 291-3082"
    CANDIDATE_LOCATION = "Allentown, NJ"
    CANDIDATE_WORK_AUTH = "Green Card Holder"
    CANDIDATE_VETERAN = False
    CANDIDATE_DISABILITY = False
    CANDIDATE_GENDER = "Male"

    @classmethod
    def validate(cls):
        """Validate that required API keys are set."""
        if not cls.GEMINI_API_KEY and cls.LLM_PROVIDER == "gemini":
            raise ValueError(
                "GEMINI_API_KEY not set in .env. "
                "Get it from: https://ai.google.dev"
            )

        missing_keys = []
        if cls.LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
            missing_keys.append("ANTHROPIC_API_KEY")
        if cls.LLM_PROVIDER == "groq" and not cls.GROQ_API_KEY:
            missing_keys.append("GROQ_API_KEY")

        if missing_keys:
            raise ValueError(f"Missing API keys: {', '.join(missing_keys)}")

        return True
