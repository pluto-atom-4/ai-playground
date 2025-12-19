"""Pydantic models for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Base response model."""

    message: str
    status: str = "success"


class CandidateBase(BaseModel):
    """Base candidate model."""

    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None


class CandidateCreate(CandidateBase):
    """Model for creating a new candidate."""

    pass


class CandidateResponse(CandidateBase):
    """Model for candidate response."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class JobDescriptionBase(BaseModel):
    """Base job description model."""

    title: str
    description: str
    required_skills: list[str] = Field(default_factory=list)


class JobDescriptionCreate(JobDescriptionBase):
    """Model for creating a new job description."""

    pass


class JobDescriptionResponse(JobDescriptionBase):
    """Model for job description response."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class MatchResult(BaseModel):
    """Model for candidate-job match result."""

    candidate_id: int
    job_id: int
    match_score: float = Field(..., ge=0, le=100)
    missing_skills: list[str] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)
    created_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True

