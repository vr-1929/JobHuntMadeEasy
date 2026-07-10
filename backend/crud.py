"""
CRUD operations for database management.
To be expanded in Phase 2+ for job search, application tracking, etc.
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from backend.models import Application, MasterProfile, FollowUp, InterviewPrep


def get_master_profile(db: Session) -> Optional[MasterProfile]:
    """Get the first (and usually only) master profile."""
    return db.query(MasterProfile).first()


def get_application(db: Session, app_id: int) -> Optional[Application]:
    """Get application by ID."""
    return db.query(Application).filter(Application.id == app_id).first()


def get_applications_by_status(db: Session, status: str) -> List[Application]:
    """Get all applications with a specific status."""
    return db.query(Application).filter(Application.status == status).all()


def get_all_applications(db: Session, limit: int = 100) -> List[Application]:
    """Get all applications, optionally limited."""
    return db.query(Application).order_by(Application.date_found.desc()).limit(limit).all()


def update_application_status(db: Session, app_id: int, new_status: str) -> bool:
    """Update application status."""
    app = get_application(db, app_id)
    if app:
        app.status = new_status
        app.last_status_update = datetime.utcnow()
        db.commit()
        return True
    return False


def get_applications_pending_review(db: Session) -> List[Application]:
    """Get all applications waiting for user review (status='found' or 'reviewed')."""
    return db.query(Application).filter(
        Application.status.in_(["found", "reviewed"])
    ).order_by(Application.match_score.desc()).all()


def get_applications_applied(db: Session) -> List[Application]:
    """Get all applications that have been submitted."""
    return db.query(Application).filter(
        Application.status.in_(["applied", "interviewing", "rejected", "offer", "ghosted"])
    ).all()


def create_follow_up(db: Session, app_id: int, email_text: str) -> FollowUp:
    """Create a follow-up email draft."""
    follow_up = FollowUp(
        application_id=app_id,
        generated_email_text=email_text,
        sent=False,
    )
    db.add(follow_up)
    db.commit()
    return follow_up


def mark_follow_up_sent(db: Session, follow_up_id: int) -> bool:
    """Mark a follow-up as sent."""
    follow_up = db.query(FollowUp).filter(FollowUp.id == follow_up_id).first()
    if follow_up:
        follow_up.sent = True
        follow_up.sent_date = datetime.utcnow()
        db.commit()
        return True
    return False


def create_interview_prep(db: Session, app_id: int, questions_and_talking_points: dict) -> InterviewPrep:
    """Create interview prep for an application."""
    prep = InterviewPrep(
        application_id=app_id,
        questions_and_talking_points=questions_and_talking_points,
    )
    db.add(prep)
    db.commit()
    return prep


def get_interview_prep(db: Session, app_id: int) -> Optional[InterviewPrep]:
    """Get interview prep for an application."""
    return db.query(InterviewPrep).filter(InterviewPrep.application_id == app_id).first()
