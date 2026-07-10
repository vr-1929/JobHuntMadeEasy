"""
SQLAlchemy models for Job App OS database.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import json

Base = declarative_base()


class MasterProfile(Base):
    """Master candidate profile with base resume."""
    __tablename__ = "master_profile"

    id = Column(Integer, primary_key=True, index=True)
    resume_latex = Column(Text, nullable=False)
    name = Column(String, default="Ved Raval")
    email = Column(String, default="ved.raval.official@gmail.com")
    phone = Column(String, default="+1 (331) 291-3082")
    location = Column(String, default="Allentown, NJ")
    work_authorization = Column(String, default="Green Card Holder")
    veteran_status = Column(String, default="Not a veteran")
    disability_status = Column(String, default="No disability")
    gender = Column(String, default="Male")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applications = relationship("Application", back_populates="master_profile")


class Application(Base):
    """Individual job application with tailored materials."""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    master_profile_id = Column(Integer, ForeignKey("master_profile.id"), default=1)
    
    company_name = Column(String, nullable=False)
    role_title = Column(String, nullable=False)
    job_url = Column(String, nullable=False)
    job_description_raw = Column(Text, nullable=False)
    source = Column(String)  # adzuna/usajobs/remotive/greenhouse/lever/manual
    location_type = Column(String)  # remote/onsite/hybrid
    location_text = Column(String)
    
    date_found = Column(DateTime, default=datetime.utcnow)
    status = Column(
        String,
        default="found",
        comment="found, reviewed, approved, applied, interviewing, rejected, offer, ghosted, skipped"
    )
    
    match_score = Column(Float, default=0.0)  # 0-100
    keywords_matched = Column(JSON, default=list)
    keywords_missing_added = Column(JSON, default=list)  # reworded from master resume
    keywords_missing_flagged = Column(JSON, default=list)  # not in master resume, needs review
    
    tailored_resume_latex = Column(Text, nullable=True)
    tailored_resume_pdf_path = Column(String, nullable=True)
    tailored_cover_letter = Column(Text, nullable=True)
    
    date_applied = Column(DateTime, nullable=True)
    last_status_update = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(Text, nullable=True)

    master_profile = relationship("MasterProfile", back_populates="applications")
    follow_ups = relationship("FollowUp", back_populates="application", cascade="all, delete-orphan")
    interview_prep = relationship("InterviewPrep", back_populates="application", cascade="all, delete-orphan")


class FollowUp(Base):
    """Follow-up email drafts for applications."""
    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    
    generated_email_text = Column(Text, nullable=False)
    sent = Column(Boolean, default=False)
    sent_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="follow_ups")


class InterviewPrep(Base):
    """Interview prep questions and talking points per application."""
    __tablename__ = "interview_prep"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    
    questions_and_talking_points = Column(JSON, nullable=False)  # structured Q&A + talking points
    generated_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="interview_prep")
