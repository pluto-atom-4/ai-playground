"""Pydantic models for request/response validation."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Enums
# ============================================================================


class CandidateStatusEnum(str, Enum):
    """Candidate application status enumeration."""

    APPLIED = "Applied"
    SCREENING = "Screening"
    INTERVIEW = "Interview"
    HIRED = "Hired"
    REJECTED = "Rejected"


# ============================================================================
# Base Response Models
# ============================================================================


class BaseResponse(BaseModel):
    """Base response model for all API responses."""

    message: str
    status: str = "success"


# ============================================================================
# Experience & Education Models
# ============================================================================


class ExperienceEntry(BaseModel):
    """Model representing a work experience entry."""

    role: str = Field(..., description="Job title or position")
    company: str = Field(..., description="Company name")
    start_date: str = Field(..., description="Start date in YYYY-MM format")
    end_date: Optional[str] = Field(
        None, description="End date in YYYY-MM format. Null if current"
    )
    years: Optional[float] = Field(
        None, description="Duration in years (calculated from dates)"
    )
    description: Optional[str] = Field(
        None, description="Job responsibilities and achievements"
    )

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate date is in YYYY-MM format."""
        if v is None:
            return None
        if not isinstance(v, str) or len(v) != 7 or v[4] != "-":
            raise ValueError("Date must be in YYYY-MM format")
        return v


class EducationEntry(BaseModel):
    """Model representing an education entry."""

    degree: str = Field(..., description="Degree type (e.g., B.S., M.S., Ph.D.)")
    institution: str = Field(..., description="School or university name")
    graduation_year: Optional[int] = Field(
        None, description="Graduation year (e.g., 2018)"
    )


# ============================================================================
# Resume Parsing Models
# ============================================================================


class ParsedResumeResponse(BaseModel):
    """Model for parsed resume response from resume parser endpoint."""

    id: UUID = Field(..., description="Unique resume identifier")
    candidate_name: str = Field(..., description="Full name of candidate")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    skills: list[str] = Field(
        default_factory=list, description="Extracted skills from resume"
    )
    experience: list[ExperienceEntry] = Field(
        default_factory=list, description="Work experience entries"
    )
    education: list[EducationEntry] = Field(
        default_factory=list, description="Education entries"
    )
    summary: Optional[str] = Field(
        None, description="Professional summary from resume"
    )
    extracted_text: str = Field(..., description="Full raw text extracted from resume")
    years_experience: Optional[float] = Field(
        None, description="Total years of work experience"
    )
    parsed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Timestamp when resume was parsed"
    )

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# ============================================================================
# Candidate Models
# ============================================================================


class CandidateBase(BaseModel):
    """Base candidate model."""

    first_name: str = Field(..., description="Candidate's first name")
    last_name: str = Field(..., description="Candidate's last name")
    email: str = Field(..., description="Candidate's email address")
    phone: Optional[str] = Field(None, description="Candidate's phone number")


class CandidateCreate(CandidateBase):
    """Model for creating a new candidate."""

    pass


class CandidateResponse(CandidateBase):
    """Model for candidate response."""

    id: UUID = Field(..., description="Unique candidate identifier")
    created_at: datetime = Field(..., description="When candidate was created")
    updated_at: datetime = Field(..., description="When candidate was last updated")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class CandidateDetailResponse(CandidateResponse):
    """Extended candidate response with additional details."""

    current_status: CandidateStatusEnum = Field(
        default=CandidateStatusEnum.APPLIED, description="Current application status"
    )
    extracted_skills: list[str] = Field(
        default_factory=list, description="Skills extracted from resume"
    )
    years_experience: Optional[float] = Field(
        None, description="Total years of work experience"
    )
    resume_url: Optional[str] = Field(None, description="URL to access candidate's resume")
    notes: Optional[str] = Field(
        None, description="Recruiter notes about candidate"
    )


class UpdateCandidateStatusRequest(BaseModel):
    """Model for updating candidate status."""

    status: CandidateStatusEnum = Field(..., description="New candidate status")
    notes: Optional[str] = Field(
        None, description="Optional notes for status change"
    )


class CandidatesListResponse(BaseModel):
    """Model for paginated candidates list response."""

    data: list[CandidateDetailResponse] = Field(
        ..., description="List of candidates"
    )
    pagination: dict = Field(
        ...,
        description="Pagination metadata",
        examples=[{
            "page": 1,
            "limit": 20,
            "total": 342,
            "totalPages": 18,
        }],
    )


# ============================================================================
# Job Description Models
# ============================================================================


class JobDescriptionBase(BaseModel):
    """Base job description model."""

    title: str = Field(..., description="Job title")
    description: str = Field(..., description="Full job description")
    required_skills: list[str] = Field(
        default_factory=list, description="List of required skills"
    )
    nice_to_have_skills: list[str] = Field(
        default_factory=list, description="List of nice-to-have skills"
    )
    years_experience_required: Optional[int] = Field(
        None, description="Minimum years of experience required"
    )


class JobDescriptionCreate(JobDescriptionBase):
    """Model for creating a new job description."""

    pass


class JobDescriptionResponse(JobDescriptionBase):
    """Model for job description response."""

    id: UUID = Field(..., description="Unique job description identifier")
    created_at: datetime = Field(..., description="When job was created")
    updated_at: datetime = Field(..., description="When job was last updated")
    embedding_stored: bool = Field(
        default=False, description="Whether embedding has been generated and stored"
    )

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# ============================================================================
# Semantic Search Models
# ============================================================================


class SemanticSearchFilters(BaseModel):
    """Filters for semantic search."""

    skills: Optional[list[str]] = Field(
        None, description="Filter by specific skills"
    )
    years_experience: Optional[int] = Field(
        None, description="Minimum years of experience"
    )


class SemanticSearchRequest(BaseModel):
    """Model for semantic search request."""

    query: str = Field(
        ..., description="Natural language search query"
    )
    job_description_id: Optional[UUID] = Field(
        None, description="Job description ID for ranking context"
    )
    limit: int = Field(
        default=50, ge=1, le=500, description="Maximum number of results"
    )
    min_match_score: float = Field(
        default=60, ge=0, le=100, description="Minimum match score threshold"
    )
    filters: Optional[SemanticSearchFilters] = Field(
        None, description="Additional search filters"
    )


class SearchResultItem(BaseModel):
    """Single result item from semantic search."""

    candidate_id: UUID = Field(..., description="Candidate's unique identifier")
    name: str = Field(..., description="Candidate's full name")
    email: str = Field(..., description="Candidate's email")
    match_score: float = Field(
        ..., ge=0, le=100, description="Overall match score (0-100)"
    )
    match_score_breakdown: dict = Field(
        ...,
        description="Breakdown of match score components",
        examples=[{
            "tfidfScore": 85,
            "semanticScore": 98,
            "skillsMatchPercentage": 95,
        }],
    )
    relevant_skills: list[str] = Field(
        ..., description="Skills that matched the job requirements"
    )
    missing_skills: list[str] = Field(
        ..., description="Required skills that are missing"
    )
    matched_keywords: dict = Field(
        ...,
        description="Keywords matched with confidence scores",
        examples=[{"react": 0.98, "python": 0.96, "backend": 0.88}],
    )
    years_experience: Optional[float] = Field(
        None, description="Candidate's years of experience"
    )
    resume_url: Optional[str] = Field(
        None, description="URL to access candidate's resume"
    )


class SemanticSearchResponse(BaseModel):
    """Model for semantic search response."""

    query: str = Field(..., description="Original search query")
    job_id: Optional[UUID] = Field(..., description="Job ID used for ranking")
    results: list[SearchResultItem] = Field(
        ..., description="Array of search results ranked by match score"
    )
    total_results: int = Field(..., description="Total number of matching results")
    query_execution_time: str = Field(
        ..., description="Query execution time (e.g., '245ms')"
    )
    cache_hit: bool = Field(
        default=False, description="Whether result was served from cache"
    )
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of response generation"
    )


# ============================================================================
# Match Result Models
# ============================================================================


class MatchResult(BaseModel):
    """Model for candidate-job match result."""

    candidate_id: UUID = Field(..., description="Candidate's unique identifier")
    job_id: UUID = Field(..., description="Job description's unique identifier")
    match_score: float = Field(
        ..., ge=0, le=100, description="Overall match score (0-100)"
    )
    tfidf_score: Optional[float] = Field(
        None, ge=0, le=100, description="TF-IDF based match score"
    )
    semantic_score: Optional[float] = Field(
        None, ge=0, le=100, description="Semantic similarity score"
    )
    missing_skills: list[str] = Field(
        default_factory=list, description="Required skills not found in resume"
    )
    matched_skills: list[str] = Field(
        default_factory=list, description="Required skills found in resume"
    )
    matched_keywords: dict = Field(
        default_factory=dict,
        description="Keywords matched with confidence scores",
    )
    created_at: datetime = Field(..., description="When match result was created")

    @field_validator("match_score", "tfidf_score", "semantic_score", mode="before")
    @classmethod
    def validate_score_range(cls, v: Optional[float]) -> Optional[float]:
        """Validate that scores are between 0 and 100."""
        if v is None:
            return None
        if not (0 <= v <= 100):
            raise ValueError("Score must be between 0 and 100")
        return v

    class Config:
        """Pydantic configuration."""

        from_attributes = True

