"""Database models for ORM."""

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class Candidate(Base):
    """Candidate model for storing candidate information."""

    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    resume_text: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class JobDescription(Base):
    """JobDescription model for storing job postings."""

    __tablename__ = "job_descriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str]
    required_skills: Mapped[str] = mapped_column(nullable=True)  # JSON serialized
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class MatchResult(Base):
    """MatchResult model for storing candidate-job matching results."""

    __tablename__ = "match_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int]
    job_id: Mapped[int]
    match_score: Mapped[float]
    missing_skills: Mapped[str] = mapped_column(nullable=True)  # JSON serialized
    matched_skills: Mapped[str] = mapped_column(nullable=True)  # JSON serialized
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

