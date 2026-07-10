"""
Database connection and session management.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from backend.models import Base

load_dotenv()

# Get database URL from environment or use default SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/jobapp.db")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Create engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite needs check_same_thread=False for async support
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )
else:
    engine = create_engine(DATABASE_URL, echo=os.getenv("DEBUG", "false").lower() == "true")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency for FastAPI to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database and create all tables."""
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized")


def get_session() -> Session:
    """Get a database session for standalone scripts."""
    return SessionLocal()
