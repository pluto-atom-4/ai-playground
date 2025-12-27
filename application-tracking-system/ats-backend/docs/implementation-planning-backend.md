# Backend Implementation Planning for ATS

This document outlines the phased implementation roadmap for the ATS backend, aligned with the high-level specification and frontend integration requirements. It includes current state assessment, required updates, and step-by-step execution plan.

---

## Current Implementation Assessment

### ✅ Existing Components (Status: In Place)

1. **FastAPI Application Foundation** (`src/main.py`)
   - CORS middleware configured
   - Health check endpoint implemented
   - Async lifespan management

2. **Configuration Management** (`src/core/config.py`)
   - Environment-based settings via pydantic-settings
   - Database and ChromaDB URLs configured
   - LLM API keys (OpenAI, Google)

3. **Database Layer** (`src/database/`)
   - SQLAlchemy ORM models for Candidate, JobDescription, MatchResult
   - SQLite-ready schema (needs PostgreSQL migration)
   - Type-mapped columns with proper constraints

4. **NLP Modules** (`src/nlp/`)
   - `parser.py`: ResumeParser class with PDF extraction and entity recognition
   - `matcher.py`: MatchingEngine with TF-IDF and cosine similarity
   - `embeddings.py`: EmbeddingsManager with ChromaDB and sentence-transformers
   - Lazy loading for models (efficient memory usage)

5. **Pydantic Schemas** (`src/models/schemas.py`)
   - CandidateCreate, CandidateResponse, JobDescriptionResponse
   - MatchResult schema with match_score validation

6. **Test Suite** (`tests/`)
   - Unit tests for parser, matcher, security
   - Fixtures in conftest.py for sample data
   - Pytest markers (@pytest.mark.unit, @pytest.mark.integration)

### ❌ Missing / Incomplete Components (Priority Updates)

| Component | Current Status | Priority | Required Updates |
|-----------|---------------|-----------|--------------------|
| **API Routes** | Minimal | **HIGH** | Implement all endpoints (parse-resume, semantic-search, candidates, jobs) |
| **Resume Parser** | Partially complete | **HIGH** | Complete skill extraction, date parsing, entity extraction |
| **Semantic Search** | Framework only | **HIGH** | Implement ChromaDB query logic, ranking combination |
| **Database Migration** | Not configured | **HIGH** | Set up Alembic, create PostgreSQL schema |
| **Error Handling** | Generic exceptions | **MEDIUM** | Custom exception classes, consistent error responses |
| **Authentication** | Not implemented | **MEDIUM** | JWT token generation/validation, API key management |
| **Input Validation** | Basic Pydantic | **MEDIUM** | Enhanced validation rules per API spec |
| **Caching Strategy** | Not implemented | **MEDIUM** | Redis integration or in-memory cache for rankings |
| **Background Tasks** | Not set up | **MEDIUM** | Celery/APScheduler for async resume processing |
| **Logging** | Print statements | **LOW** | Structured JSON logging with request IDs |
| **API Documentation** | Not configured | **LOW** | OpenAPI/Swagger setup and endpoint docs |

---

## Phase 1: Foundation & API Scaffolding (Week 1)

### Goals
- Establish API endpoint structure aligned with frontend requirements
- Complete Pydantic schemas for all request/response payloads
- Set up database migrations with PostgreSQL support

### Tasks

#### 1.1 Create Enhanced Pydantic Schemas (`src/models/schemas.py`)

**Updates needed**:
- Add UUID support to replace integer IDs
- Create detailed request/response schemas for all endpoints
- Add Zod-like validation using Pydantic field validators

**Code locations**:
```
src/models/schemas.py (modify existing)
- Add CandidateStatus enum
- Extend CandidateResponse with all required fields
- Add ParsedResumeResponse with nested structures
- Add SemanticSearchRequest/Response schemas
- Add JobDescriptionRequest/Response schemas
```

**File changes**:
```python
# Add to schemas.py
from enum import Enum
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl

class CandidateStatusEnum(str, Enum):
    APPLIED = "Applied"
    SCREENING = "Screening"
    INTERVIEW = "Interview"
    HIRED = "Hired"
    REJECTED = "Rejected"

class ExperienceEntry(BaseModel):
    role: str
    company: str
    startDate: str  # ISO 8601
    endDate: Optional[str] = None
    years: float
    description: Optional[str] = None

class EducationEntry(BaseModel):
    degree: str
    institution: str
    graduationYear: Optional[int] = None

class ParsedResumeResponse(BaseModel):
    id: UUID
    candidateName: str
    email: str
    phone: Optional[str] = None
    skills: List[str]
    experience: List[ExperienceEntry]
    education: List[EducationEntry]
    summary: Optional[str] = None
    extractedText: str
    parsedAt: datetime

class SemanticSearchRequest(BaseModel):
    query: str
    jobDescriptionId: UUID
    limit: int = Field(50, le=100, ge=1)
    minMatchScore: int = Field(0, le=100, ge=0)

class SearchResultItem(BaseModel):
    candidateId: UUID
    name: str
    email: str
    matchScore: float
    matchScoreBreakdown: dict
    relevantSkills: List[str]
    missingSkills: List[str]
    yearsExperience: Optional[float] = None

class SemanticSearchResponse(BaseModel):
    query: str
    jobId: UUID
    results: List[SearchResultItem]
    totalResults: int
    queryExecutionTime: str
    cacheHit: bool
    generatedAt: datetime
```

#### 1.2 Set Up Database Migrations (Alembic)

**New files**:
```bash
# Create Alembic environment
alembic init alembic
```

**Create migration for PostgreSQL schema**:
```
alembic/versions/001_initial_schema.py
```

**Updates to config.py**:
- Add SQLALCHEMY_DATABASE_URL pointing to PostgreSQL
- Add Alembic configuration

#### 1.3 Update Database Models for UUIDs

**File**: `src/database/models.py`

**Changes**:
```python
from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import sqlalchemy.orm as orm

class Candidate(Base):
    __tablename__ = "candidates"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    # ... rest of columns
    status: Mapped[str] = mapped_column(String(50), default="Applied")
```

#### 1.4 Create API Route Structure

**New files**:
```
src/api/routes/
├── __init__.py           (import and re-export all routers)
├── parse_resume.py       (POST /api/parse-resume)
├── semantic_search.py    (POST /api/semantic-search)
├── candidates.py         (GET/POST/PATCH /api/candidates)
├── job_descriptions.py   (GET/POST /api/job-descriptions)
└── health.py             (health checks)
```

**Endpoint structure** (minimal implementation):
```python
# src/api/routes/parse_resume.py
from fastapi import APIRouter, File, UploadFile, HTTPException
from src.models.schemas import ParsedResumeResponse

router = APIRouter(prefix="/api", tags=["Resume"])

@router.post("/parse-resume", response_model=ParsedResumeResponse)
async def parse_resume(file: UploadFile = File(...)) -> ParsedResumeResponse:
    """Parse uploaded resume file."""
    if not file.filename.endswith(('.pdf', '.docx', '.txt')):
        raise HTTPException(status_code=400, detail="Invalid file format")
    # TODO: Implement parsing logic
    pass
```

#### 1.5 Update Main Application Router

**File**: `src/api/__init__.py` and `src/main.py`

**Changes**:
```python
# src/api/__init__.py
from .routes import parse_resume, semantic_search, candidates, job_descriptions, health

# src/main.py
from src.api.routes import (
    parse_resume, semantic_search, candidates, job_descriptions, health
)

# In create_app():
app.include_router(parse_resume.router)
app.include_router(semantic_search.router)
app.include_router(candidates.router)
app.include_router(job_descriptions.router)
app.include_router(health.router)
```

---

## Phase 2: Core NLP Implementation (Week 2)

### Goals
- Complete resume parser with skill extraction and entity recognition
- Implement matching engine with both TF-IDF and semantic scoring
- Set up ChromaDB for embedding storage and retrieval

### Tasks

#### 2.1 Complete Resume Parser (`src/nlp/parser.py`)

**Current status**: Skeleton with lazy loading

**Methods to implement**:
- `extract_text_from_pdf(file_path)` - Extract text from PDF
- `extract_entities(text)` - Extract name, email, phone using spaCy NER
- `extract_skills(text)` - Match skills from predefined list
- `extract_experience(text)` - Parse work history dates and roles
- `extract_education(text)` - Parse education entries
- `parse_resume_file(file: UploadFile)` - Main orchestration method

**Implementation details**:
```python
# src/nlp/parser.py additions

SKILLS_DATABASE = {
    "languages": ["python", "javascript", "java", "c++", ...],
    "frontend": ["react", "angular", "vue", "svelte", ...],
    "backend": ["fastapi", "django", "flask", "node.js", ...],
    "databases": ["postgresql", "mongodb", "mysql", ...],
    # ... more categories
}

def extract_skills(self, text: str) -> List[str]:
    """Extract technical skills from resume text."""
    text_lower = text.lower()
    found_skills = []
    for skill in self._get_all_skills():
        if skill.lower() in text_lower:
            found_skills.append(skill)
    return list(set(found_skills))  # Remove duplicates

def extract_experience(self, text: str) -> List[ExperienceEntry]:
    """Parse work experience sections."""
    # Use regex and spaCy for date/company/role extraction
    pass
```

#### 2.2 Complete Matching Engine (`src/nlp/matcher.py`)

**Current status**: TF-IDF implementation only

**Methods to enhance**:
- `calculate_match_score()` - Combine TF-IDF + semantic scoring
- `extract_missing_skills()` - Already exists, verify it works
- `rank_candidates()` - Already exists, verify ranking order
- `combine_scores()` - Weight TF-IDF (40%) + semantic (50%) + keyword (10%)

**Implementation details**:
```python
# src/nlp/matcher.py additions

def calculate_match_score(
    self, 
    resume_text: str, 
    job_description: str,
    semantic_boost: float = 0.5,
    max_score: float = 100.0
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate combined match score.
    
    Returns:
        (final_score, breakdown)
    """
    tfidf_score = self._calculate_tfidf_score(resume_text, job_description)
    semantic_score = self._calculate_semantic_score(resume_text, job_description)
    keyword_score = self._calculate_keyword_score(resume_text, job_description)
    
    # Weighted combination
    final = (
        tfidf_score * 0.40 +
        semantic_score * 0.50 +
        keyword_score * 0.10
    )
    
    return min(final, max_score), {
        "tfidfScore": tfidf_score,
        "semanticScore": semantic_score,
        "keywordScore": keyword_score
    }
```

#### 2.3 Set Up Embeddings Manager (`src/nlp/embeddings.py`)

**Current status**: ChromaDB client exists, search method incomplete

**Methods to complete**:
- `generate_embeddings()` - Vectorize text using sentence-transformers
- `store_embeddings()` - Store in ChromaDB with metadata
- `search_similar()` - Query ChromaDB for similar resumes
- `update_embedding()` - Re-embed when resume is updated
- `delete_embedding()` - Remove embedding when candidate deleted

**Implementation details**:
```python
# src/nlp/embeddings.py additions

def search_similar(
    self, 
    query_text: str, 
    collection_name: str = "candidates_resumes",
    n_results: int = 50
) -> List[Dict]:
    """Search for similar resumes using embeddings."""
    collection = self.client.get_collection(name=collection_name)
    query_embedding = self.embedder.encode([query_text])
    
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    return self._format_results(results)
```

#### 2.4 Create Service Layer (`src/services/`)

**New file**: `src/services/resume_service.py`

```python
"""Service layer for resume operations."""
from src.nlp.parser import ResumeParser
from src.models.schemas import ParsedResumeResponse

class ResumeService:
    def __init__(self):
        self.parser = ResumeParser()
    
    async def parse_resume_file(self, file) -> ParsedResumeResponse:
        """Orchestrate resume parsing."""
        # Extract text
        text = await self.parser.extract_text_from_pdf(file)
        
        # Extract entities and skills
        name = self.parser.extract_entities(text).get('name')
        skills = self.parser.extract_skills(text)
        experience = self.parser.extract_experience(text)
        education = self.parser.extract_education(text)
        
        return ParsedResumeResponse(
            id=uuid4(),
            candidateName=name,
            skills=skills,
            # ...
        )
```

---

## Phase 3: API Implementation & Integration (Week 3)

### Goals
- Implement all API endpoints with database integration
- Wire up services to endpoints
- Add comprehensive error handling

### Tasks

#### 3.1 Implement Resume Parser Endpoint (`src/api/routes/parse_resume.py`)

```python
@router.post("/parse-resume", response_model=ParsedResumeResponse)
async def parse_resume(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session)
) -> ParsedResumeResponse:
    """Parse uploaded resume and extract candidate information."""
    try:
        # Validate file
        if not file.filename.endswith(('.pdf', '.docx', '.txt')):
            raise HTTPException(400, "Invalid file format")
        
        if file.size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(413, "File too large")
        
        # Parse resume
        resume_service = ResumeService()
        parsed = await resume_service.parse_resume_file(file)
        
        # Store candidate in database
        candidate = Candidate(
            id=parsed.id,
            first_name=parsed.candidateName.split()[0],
            last_name=" ".join(parsed.candidateName.split()[1:]),
            email=parsed.email,
            phone=parsed.phone,
            resume_text=parsed.extractedText,
            extracted_skills=json.dumps(parsed.skills),
        )
        session.add(candidate)
        await session.commit()
        
        return parsed
    except Exception as e:
        raise HTTPException(500, str(e))
```

#### 3.2 Implement Semantic Search Endpoint (`src/api/routes/semantic_search.py`)

```python
@router.post("/semantic-search", response_model=SemanticSearchResponse)
async def semantic_search(
    request: SemanticSearchRequest,
    session: AsyncSession = Depends(get_db_session)
) -> SemanticSearchResponse:
    """Search for candidates matching job description using semantic similarity."""
    try:
        # Get job description
        job = await session.get(JobDescription, request.jobDescriptionId)
        if not job:
            raise HTTPException(404, "Job not found")
        
        # Get all candidates
        stmt = select(Candidate)
        result = await session.execute(stmt)
        candidates = result.scalars().all()
        
        # Calculate scores
        matcher = MatchingEngine()
        embeddings = EmbeddingsManager()
        
        results = []
        for candidate in candidates:
            score, breakdown = matcher.calculate_match_score(
                candidate.resume_text,
                job.description
            )
            
            if score >= request.minMatchScore:
                results.append(SearchResultItem(
                    candidateId=candidate.id,
                    name=f"{candidate.first_name} {candidate.last_name}",
                    matchScore=score,
                    matchScoreBreakdown=breakdown,
                    # ...
                ))
        
        # Sort by score
        results.sort(key=lambda x: x.matchScore, reverse=True)
        
        return SemanticSearchResponse(
            query=request.query,
            jobId=request.jobDescriptionId,
            results=results[:request.limit],
            totalResults=len(results),
            # ...
        )
    except Exception as e:
        raise HTTPException(500, str(e))
```

#### 3.3 Implement Candidates Endpoints (`src/api/routes/candidates.py`)

```python
@router.get("/candidates", response_model=CandidatesListResponse)
async def list_candidates(
    status: Optional[CandidateStatusEnum] = None,
    jobId: Optional[UUID] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=10, le=100),
    sortBy: str = Query("createdAt"),
    session: AsyncSession = Depends(get_db_session)
) -> CandidatesListResponse:
    """List candidates with filters and pagination."""
    # Build query
    stmt = select(Candidate)
    
    if status:
        stmt = stmt.where(Candidate.status == status)
    
    # Apply sorting
    stmt = stmt.order_by(getattr(Candidate, sortBy).desc())
    
    # Pagination
    total = await session.scalar(select(func.count()).select_from(Candidate))
    stmt = stmt.offset((page - 1) * limit).limit(limit)
    
    result = await session.execute(stmt)
    candidates = result.scalars().all()
    
    return CandidatesListResponse(
        data=[CandidateResponse.from_orm(c) for c in candidates],
        pagination=PaginationInfo(
            page=page,
            limit=limit,
            total=total,
            totalPages=(total + limit - 1) // limit
        )
    )

@router.patch("/candidates/{id}/status", response_model=CandidateResponse)
async def update_candidate_status(
    id: UUID,
    request: UpdateCandidateStatusRequest,
    session: AsyncSession = Depends(get_db_session)
) -> CandidateResponse:
    """Update candidate status and notes."""
    candidate = await session.get(Candidate, id)
    if not candidate:
        raise HTTPException(404, "Candidate not found")
    
    candidate.status = request.status
    candidate.notes = request.notes
    candidate.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(candidate)
    
    return CandidateResponse.from_orm(candidate)
```

#### 3.4 Implement Job Descriptions Endpoints (`src/api/routes/job_descriptions.py`)

```python
@router.post("/job-descriptions", response_model=JobDescriptionResponse, status_code=201)
async def create_job_description(
    request: JobDescriptionCreate,
    session: AsyncSession = Depends(get_db_session)
) -> JobDescriptionResponse:
    """Create a new job description."""
    job = JobDescription(
        id=uuid4(),
        title=request.title,
        description=request.description,
        required_skills=json.dumps(request.requiredSkills),
        # ...
    )
    
    session.add(job)
    await session.commit()
    await session.refresh(job)
    
    return JobDescriptionResponse.from_orm(job)

@router.get("/job-descriptions/{id}", response_model=JobDescriptionResponse)
async def get_job_description(
    id: UUID,
    session: AsyncSession = Depends(get_db_session)
) -> JobDescriptionResponse:
    """Get job description by ID."""
    job = await session.get(JobDescription, id)
    if not job:
        raise HTTPException(404, "Job not found")
    
    return JobDescriptionResponse.from_orm(job)
```

---

## Phase 4: Error Handling, Validation & Logging (Week 4)

### Goals
- Implement custom exception handling
- Add request validation and sanitization
- Set up structured logging

### Tasks

#### 4.1 Create Custom Exception Classes (`src/core/exceptions.py`)

```python
"""Custom exception classes for ATS."""

class ATSException(Exception):
    """Base exception for ATS."""
    def __init__(self, message: str, code: str = None, status_code: int = 500):
        self.message = message
        self.code = code or self.__class__.__name__
        self.status_code = status_code
        super().__init__(message)

class ValidationError(ATSException):
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR", 400)

class NotFoundError(ATSException):
    def __init__(self, resource: str, id: str):
        super().__init__(
            f"{resource} with id {id} not found",
            "NOT_FOUND",
            404
        )

class ParsingError(ATSException):
    def __init__(self, message: str):
        super().__init__(message, "PARSING_ERROR", 500)

class FileTooLargeError(ATSException):
    def __init__(self, size: int, max_size: int):
        super().__init__(
            f"File size {size} exceeds maximum {max_size}",
            "FILE_TOO_LARGE",
            413
        )
```

#### 4.2 Add Exception Handler Middleware (`src/core/exceptions.py`)

```python
# In main.py
from src.core.exceptions import ATSException

@app.exception_handler(ATSException)
async def ats_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": exc.code,
            "message": exc.message,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

#### 4.3 Set Up Structured Logging (`src/core/logging.py`)

```python
"""Structured logging configuration."""
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

def setup_logging(debug: bool = False):
    """Configure structured logging."""
    level = logging.DEBUG if debug else logging.INFO
    
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
```

#### 4.4 Add Request ID Middleware (`src/core/middleware.py`)

```python
"""Middleware for request tracking and logging."""
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar

request_id_context: ContextVar[str] = ContextVar('request_id')

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        request_id_context.set(request_id)
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response

# In main.py: app.add_middleware(RequestIDMiddleware)
```

---

## Phase 5: Database Migrations & Setup (Week 4)

### Goals
- Complete Alembic setup for PostgreSQL
- Create migration scripts
- Document database setup

### Tasks

#### 5.1 Initialize Alembic

```bash
cd ats-backend
alembic init alembic
```

#### 5.2 Configure Alembic (`alembic/env.py`)

```python
# Update alembic/env.py to use SQLAlchemy models
from src.database.models import Base

target_metadata = Base.metadata

# In offline mode, use:
# context.execute(script.upgrade())
```

#### 5.3 Create Initial Migration

```bash
alembic revision --autogenerate -m "Initial schema: candidates, jobs, matches"
```

#### 5.4 Update Database Session (`src/database/session.py`)

```python
"""Database session management."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

# Create async engine for PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True
)

# Session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db_session() -> AsyncSession:
    """Dependency for FastAPI routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

---

## Phase 6: Testing & Quality Assurance (Week 5)

### Goals
- Implement comprehensive unit and integration tests
- Achieve >80% code coverage
- Set up performance testing

### Tasks

#### 6.1 Expand Unit Tests

**Resume Parser Tests** (`tests/unit/test_parser.py`):
```python
@pytest.mark.unit
async def test_extract_skills_from_resume(sample_resume_text: str):
    parser = ResumeParser()
    skills = parser.extract_skills(sample_resume_text)
    assert "Python" in skills or "python" in [s.lower() for s in skills]
    assert len(skills) > 0

@pytest.mark.unit
async def test_extract_entities_from_text(sample_resume_text: str):
    parser = ResumeParser()
    entities = parser.extract_entities(sample_resume_text)
    assert "name" in entities or entities.get("email") is not None

@pytest.mark.unit
async def test_parse_experience_dates():
    parser = ResumeParser()
    experience = parser.extract_experience("Jan 2020 - Dec 2022 at Tech Corp")
    assert experience[0].startDate == "2020-01"
    assert experience[0].endDate == "2022-12"
```

**Matching Engine Tests** (`tests/unit/test_matcher.py`):
```python
@pytest.mark.unit
async def test_combined_score_calculation(
    sample_resume_text: str, 
    sample_job_description: str
):
    engine = MatchingEngine()
    score, breakdown = engine.calculate_match_score(
        sample_resume_text,
        sample_job_description
    )
    
    assert 0 <= score <= 100
    assert "tfidfScore" in breakdown
    assert "semanticScore" in breakdown
    assert breakdown["tfidfScore"] + breakdown["semanticScore"] > 0
```

**Embeddings Tests** (`tests/unit/test_embeddings.py`):
```python
@pytest.mark.unit
async def test_generate_embeddings():
    manager = EmbeddingsManager()
    texts = ["Python developer", "React engineer"]
    embeddings = manager.generate_embeddings(texts)
    
    assert len(embeddings) == 2
    assert len(embeddings[0]) > 0  # Not empty

@pytest.mark.unit
async def test_search_similar():
    manager = EmbeddingsManager()
    manager.store_embeddings(
        "test_collection",
        ["Python developer with 5 years experience"],
        ["doc1"]
    )
    
    results = manager.search_similar("Python engineer")
    assert len(results) > 0
```

#### 6.2 Add Integration Tests

**End-to-End Resume Processing** (`tests/integration/test_resume_e2e.py`):
```python
@pytest.mark.integration
async def test_resume_upload_to_search_flow(
    client: TestClient,
    sample_pdf_file,
    session: AsyncSession
):
    """Test complete flow: upload → parse → store → search"""
    # 1. Upload resume
    response = client.post(
        "/api/parse-resume",
        files={"file": sample_pdf_file}
    )
    assert response.status_code == 200
    parsed = response.json()
    candidate_id = parsed["id"]
    
    # 2. Create job
    job_response = client.post(
        "/api/job-descriptions",
        json={
            "title": "Python Developer",
            "description": "Senior Python engineer with FastAPI experience",
            "requiredSkills": ["Python", "FastAPI"]
        }
    )
    job_id = job_response.json()["id"]
    
    # 3. Semantic search
    search_response = client.post(
        "/api/semantic-search",
        json={
            "query": "Python FastAPI developer",
            "jobDescriptionId": job_id
        }
    )
    assert search_response.status_code == 200
    results = search_response.json()
    
    # Verify candidate in results
    candidate_ids = [r["candidateId"] for r in results["results"]]
    assert candidate_id in candidate_ids
```

#### 6.3 Set Up Coverage Reporting

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html tests/

# Target: >80% coverage
# Exclude from coverage: __init__.py, main.py (mostly setup)
```

#### 6.4 Add API Integration Tests

**Test endpoints** (`tests/integration/test_api.py`):
```python
@pytest.mark.integration
async def test_list_candidates_endpoint(client: TestClient, session: AsyncSession):
    """Test GET /api/candidates"""
    response = client.get("/api/candidates?page=1&limit=20")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data

@pytest.mark.integration
async def test_update_candidate_status(client: TestClient, candidate_id: UUID):
    """Test PATCH /api/candidates/{id}/status"""
    response = client.patch(
        f"/api/candidates/{candidate_id}/status",
        json={
            "status": "Interview",
            "notes": "Scheduled for technical round"
        }
    )
    assert response.status_code == 200
    assert response.json()["currentStatus"] == "Interview"
```

---

## Phase 7: Optimization & Documentation (Week 5)

### Goals
- Implement caching for performance
- Complete API documentation
- Optimize database queries

### Tasks

#### 7.1 Add Caching Layer (`src/core/cache.py`)

```python
"""In-memory caching for rankings and searches."""
from functools import lru_cache
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class CacheEntry:
    def __init__(self, data: Any, ttl_seconds: int = 3600):
        self.data = data
        self.created_at = datetime.utcnow()
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.created_at + timedelta(seconds=self.ttl_seconds)

class SimpleCache:
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            entry = self._cache[key]
            if not entry.is_expired():
                return entry.data
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        self._cache[key] = CacheEntry(value, ttl_seconds)
    
    def clear(self):
        self._cache.clear()

# Global cache instance
ranking_cache = SimpleCache()
search_cache = SimpleCache()
```

#### 7.2 Use Caching in Endpoints

```python
# In semantic_search endpoint
@router.post("/semantic-search", response_model=SemanticSearchResponse)
async def semantic_search(request: SemanticSearchRequest, ...):
    # Check cache
    cache_key = f"search_{request.jobDescriptionId}_{request.query}"
    cached_result = search_cache.get(cache_key)
    
    if cached_result:
        cached_result["cacheHit"] = True
        return cached_result
    
    # ... perform search ...
    
    # Store in cache
    search_cache.set(cache_key, result, ttl_seconds=1800)
    result["cacheHit"] = False
    
    return result
```

#### 7.3 Add Database Query Optimization

```python
# Use select() with eager loading
from sqlalchemy import select
from sqlalchemy.orm import selectinload

stmt = select(Candidate).options(selectinload(Candidate.matches))
```

#### 7.4 Generate OpenAPI Documentation

```python
# In main.py - FastAPI auto-generates docs
# Access at: http://localhost:8000/docs (Swagger)
# Or: http://localhost:8000/redoc (ReDoc)

# Custom documentation can be added via docstrings
@router.post("/api/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """
    Parse a resume file and extract candidate information.
    
    ## Parameters
    - **file**: PDF, DOCX, or TXT file (max 10MB)
    
    ## Response
    Returns parsed resume with candidate details including:
    - Extracted skills
    - Work experience
    - Education history
    
    ## Example
    Upload a resume PDF and receive structured candidate data
    """
    pass
```

---

## Implementation Checklist

### Phase 1: Foundation & API Scaffolding ✓
- [ ] Create comprehensive Pydantic schemas with UUID support
- [ ] Set up Alembic for database migrations
- [ ] Update database models for PostgreSQL (UUID primary keys)
- [ ] Create API route structure (parse_resume, semantic_search, candidates, jobs)
- [ ] Update main application router to include all routes
- [ ] Verify FastAPI app starts without errors
- [ ] Test health check endpoint

### Phase 2: Core NLP Implementation ✓
- [ ] Complete resume parser (PDF extraction, skill parsing, entity recognition)
- [ ] Test parser with sample resumes
- [ ] Complete matching engine (TF-IDF + semantic scoring)
- [ ] Set up ChromaDB for embeddings storage
- [ ] Implement embeddings manager (generate, store, search)
- [ ] Create service layer for orchestration
- [ ] Unit tests for all NLP modules (>80% coverage)

### Phase 3: API Implementation & Integration ✓
- [ ] Implement POST /api/parse-resume endpoint
- [ ] Implement POST /api/semantic-search endpoint
- [ ] Implement GET /api/candidates endpoint
- [ ] Implement PATCH /api/candidates/{id}/status endpoint
- [ ] Implement POST /api/job-descriptions endpoint
- [ ] Implement GET /api/job-descriptions/{id} endpoint
- [ ] Database integration for all endpoints
- [ ] Test endpoints with sample data

### Phase 4: Error Handling, Validation & Logging ✓
- [ ] Create custom exception classes
- [ ] Add exception handler middleware
- [ ] Set up structured JSON logging
- [ ] Implement request ID tracking middleware
- [ ] Add input validation and sanitization
- [ ] Document error response format

### Phase 5: Database Migrations & Setup ✓
- [ ] Initialize Alembic
- [ ] Configure Alembic for PostgreSQL
- [ ] Create initial migration script
- [ ] Document database setup instructions
- [ ] Test migrations on fresh database

### Phase 6: Testing & Quality Assurance ✓
- [ ] Expand unit tests for parser, matcher, embeddings
- [ ] Add integration tests for E2E flows
- [ ] Add API endpoint tests
- [ ] Achieve >80% code coverage
- [ ] Set up coverage reporting
- [ ] Performance testing (load, response times)
- [ ] Visual regression testing (if applicable)

### Phase 7: Optimization & Documentation ✓
- [ ] Implement caching layer for rankings
- [ ] Optimize database queries (indexing, eager loading)
- [ ] Generate OpenAPI/Swagger documentation
- [ ] Create README with setup and usage instructions
- [ ] Document API endpoints and schemas
- [ ] Create deployment guide

---

## File Structure After Implementation

```
ats-backend/
├── src/
│   ├── __init__.py
│   ├── main.py                          (updated)
│   ├── api/
│   │   ├── __init__.py                  (updated)
│   │   ├── dependencies.py              (database session, auth)
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── parse_resume.py          (new)
│   │       ├── semantic_search.py       (new)
│   │       ├── candidates.py            (new)
│   │       ├── job_descriptions.py      (new)
│   │       └── health.py                (new)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                    (updated)
│   │   ├── security.py
│   │   ├── exceptions.py                (new)
│   │   ├── logging.py                   (new)
│   │   ├── middleware.py                (new)
│   │   └── cache.py                     (new)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── session.py                   (updated for async)
│   │   └── models.py                    (updated)
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py                   (expanded)
│   ├── nlp/
│   │   ├── __init__.py
│   │   ├── parser.py                    (completed)
│   │   ├── matcher.py                   (enhanced)
│   │   └── embeddings.py                (completed)
│   └── services/
│       ├── __init__.py
│       ├── resume_service.py            (new)
│       ├── matching_service.py          (new)
│       └── search_service.py            (new)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      (updated)
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_parser.py               (expanded)
│   │   ├── test_matcher.py              (expanded)
│   │   ├── test_embeddings.py           (new)
│   │   ├── test_schemas.py              (new)
│   │   └── test_security.py
│   └── integration/
│       ├── __init__.py
│       ├── test_resume_e2e.py           (new)
│       ├── test_search_integration.py   (new)
│       ├── test_api.py                  (new)
│       └── test_transactions.py         (new)
├── alembic/                             (new)
│   ├── versions/
│   │   └── 001_initial_schema.py
│   ├── env.py
│   └── script.py.mako
├── pyproject.toml                       (updated with new deps)
├── uv.lock                              (updated)
├── .env                                 (updated)
├── .env.example                         (updated)
└── alembic.ini                          (new)
```

---

## Technology Stack Verification

| Component | Current | Status | Target |
|-----------|---------|--------|--------|
| FastAPI | 0.104+ | ✅ | 0.104+ |
| Python | 3.11+ | ✅ | 3.11-3.14 |
| PostgreSQL | Not set | ❌ | Latest |
| SQLAlchemy | 2.0.0 | ✅ | 2.0+ |
| Pydantic | 2.5.0 | ✅ | 2.5+ |
| spaCy | 3.7.0 | ✅ | 3.7+ |
| ChromaDB | Optional | ⚠️ | 0.5+ |
| sentence-transformers | Not listed | ❌ | Latest |
| pytest | 7.4.0 | ✅ | 7.4+ |
| Alembic | Not listed | ❌ | Latest |
| async support | Partial | ⚠️ | Full |

---

## Critical Updates Required

1. **Add async database support** - Update session.py for async SQLAlchemy
2. **Add sentence-transformers** - For embedding generation
3. **Configure PostgreSQL** - Switch from SQLite to PostgreSQL
4. **Implement all API routes** - Currently missing endpoints
5. **Add comprehensive error handling** - Use custom exceptions
6. **Set up testing infrastructure** - Expand test suite
7. **Configure Alembic** - For database migrations
8. **Add structured logging** - Replace print statements

---

## Success Criteria

✅ All phases completed successfully when:

1. **API Endpoints**: All 6+ endpoints implemented and tested
2. **NLP Pipeline**: Parser, matcher, embeddings fully functional
3. **Database**: PostgreSQL with proper schema and migrations
4. **Testing**: >80% code coverage, all critical paths E2E tested
5. **Performance**: All endpoints meet SLA targets (<500ms cached, <3s uncached)
6. **Error Handling**: Consistent error responses with proper HTTP status codes
7. **Documentation**: Complete API docs, setup guide, and deployment instructions
8. **Frontend Integration**: Backend endpoints respond with exact schemas expected by frontend

---

## Next Steps

1. **Review this plan** with team for alignment
2. **Execute Phase 1** - Create schemas, routes, database setup
3. **Begin Phase 2** - Implement NLP modules
4. **Parallel execution** - Start Phase 3 while Phase 2 is in testing
5. **Continuous testing** - Run tests at end of each phase
6. **Regular checkpoints** - Review progress weekly


