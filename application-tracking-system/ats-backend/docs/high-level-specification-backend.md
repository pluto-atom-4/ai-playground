# Backend Specifications for ATS

To implement a high-performance Application Tracking System (ATS) backend in December 2025, follow these backend specifications optimized for FastAPI with NLP capabilities.

## 1. Core Backend Architecture (FastAPI)

**Framework & Performance**:
- **Framework**: FastAPI 0.104+ with async/await for high concurrency
- **Python**: 3.11+ (3.12, 3.13, 3.14 supported via uv dependency management)
- **Server**: Uvicorn with worker multiplexing for production
- **Type Safety**: Full type hints on all functions and classes per PEP 484
- **Database**: PostgreSQL for structured data, ChromaDB for semantic embeddings
- **Validation**: Pydantic v2 for request/response schemas with runtime validation

**Key Requirements**:
- Async database operations using SQLAlchemy 2.0 with async support
- Thread-safe NLP model initialization with lazy loading
- Caching layer for heavy NLP computations (ranking, embeddings)
- Worker queue for long-running tasks (PDF parsing, embedding generation)
- Comprehensive error handling and structured logging

---

## 2. API Endpoints & Specifications

### A. Resume Parser Endpoint

**Endpoint**: `POST /api/parse-resume`

**Request**:
- Content-Type: `multipart/form-data`
- Body: File upload (PDF, DOCX, or plain text)

**Response Schema** (200 OK):
```json
{
  "id": "resume-uuid-123",
  "candidateName": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-0123",
  "skills": ["Python", "React", "PostgreSQL", "FastAPI"],
  "experience": [
    {
      "role": "Senior Software Engineer",
      "company": "Tech Corp",
      "startDate": "2022-01",
      "endDate": "2024-12",
      "years": 2,
      "description": "Led backend architecture redesign"
    }
  ],
  "education": [
    {
      "degree": "B.S. Computer Science",
      "institution": "University of Tech",
      "graduationYear": 2018
    }
  ],
  "summary": "Experienced full-stack engineer with 5+ years in Python and React development",
  "extractedText": "Full resume text...",
  "parsedAt": "2024-12-26T10:30:00Z"
}
```

**Error Responses**:
- `400`: Invalid file format or corrupted PDF
- `413`: File too large (limit: 10MB)
- `500`: Parser error during extraction

**Processing Details**:
- Extract text from PDF using pypdf library
- Named Entity Recognition (NER) for names, emails, phone numbers using spaCy
- Skill extraction using regex patterns and spaCy entity matching
- Experience dates parsed with natural language processing
- Rate limit: 50 resumes/minute per client

---

### B. Semantic Search Endpoint

**Endpoint**: `POST /api/semantic-search`

**Request**:
```json
{
  "query": "React developer with Python experience and PostgreSQL",
  "jobDescriptionId": "job-uuid-456",
  "limit": 50,
  "minMatchScore": 60,
  "filters": {
    "skills": ["Python", "React"],
    "yearsExperience": 3
  }
}
```

**Response Schema** (200 OK):
```json
{
  "query": "React developer with Python experience",
  "jobId": "job-uuid-456",
  "results": [
    {
      "candidateId": "cand-uuid-1",
      "name": "John Doe",
      "email": "john@example.com",
      "matchScore": 92,
      "matchScoreBreakdown": {
        "tfidfScore": 85,
        "semanticScore": 98,
        "skillsMatchPercentage": 95
      },
      "relevantSkills": ["React", "Python", "PostgreSQL"],
      "missingSkills": ["Docker", "Kubernetes"],
      "matchedKeywords": {
        "react": 0.98,
        "python": 0.96,
        "backend": 0.88
      },
      "yearsExperience": 5,
      "topCompanies": ["Tech Corp", "StartupXYZ"],
      "resumeUrl": "/api/resumes/cand-uuid-1/download"
    }
  ],
  "totalResults": 142,
  "queryExecutionTime": "245ms",
  "cacheHit": true,
  "generatedAt": "2024-12-26T10:30:00Z"
}
```

**Ranking Algorithm**:
- **TF-IDF Matching** (40% weight): Token frequency-inverse document frequency on skills
- **Semantic Similarity** (50% weight): Embedding-based similarity using ChromaDB
- **Keyword Matching** (10% weight): Exact skill matches and domain keywords
- **Final Score**: Weighted combination normalized to 0-100 range

**Error Responses**:
- `400`: Invalid query or filter parameters
- `404`: Job description not found
- `503`: Embeddings service unavailable

**Performance SLAs**:
- Response time: <500ms (cached), <3s (uncached)
- Throughput: 100+ concurrent queries
- Cache TTL: 1 hour for job-specific rankings

---

### C. Candidates Management Endpoint

**Endpoint**: `GET /api/candidates`

**Query Parameters**:
```
status: 'Applied' | 'Screening' | 'Interview' | 'Hired' | 'Rejected'
jobId: string (uuid, optional)
page: integer (1-based, default: 1)
limit: integer (10-100, default: 20)
sortBy: 'matchScore' | 'createdAt' | 'name' (default: 'createdAt')
sortOrder: 'asc' | 'desc'
```

**Response Schema** (200 OK):
```json
{
  "data": [
    {
      "id": "cand-uuid-1",
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0123",
      "currentStatus": "Interview",
      "matchScore": 92,
      "resumeUrl": "/api/resumes/cand-uuid-1",
      "extractedSkills": ["Python", "React", "PostgreSQL"],
      "yearsExperience": 5,
      "createdAt": "2024-12-24T08:00:00Z",
      "updatedAt": "2024-12-26T10:30:00Z",
      "notes": "Strong technical background, excellent communication"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 342,
    "totalPages": 18
  }
}
```

**Endpoint**: `PATCH /api/candidates/{id}/status`

**Request**:
```json
{
  "status": "Interview",
  "notes": "Scheduled for technical interview on Dec 27"
}
```

**Response Schema** (200 OK):
- Updated candidate object with new status and timestamp

**Error Responses**:
- `404`: Candidate not found
- `409`: Invalid status transition
- `422`: Invalid request body

---

### D. Job Descriptions Endpoint

**Endpoint**: `POST /api/job-descriptions`

**Request**:
```json
{
  "title": "Senior React Developer",
  "description": "We are looking for...",
  "requiredSkills": ["React", "TypeScript", "Node.js"],
  "niceToHaveSkills": ["GraphQL", "Docker"],
  "yearsExperienceRequired": 4
}
```

**Response Schema** (201 Created):
```json
{
  "id": "job-uuid-456",
  "title": "Senior React Developer",
  "description": "Full job description...",
  "requiredSkills": ["React", "TypeScript", "Node.js"],
  "niceToHaveSkills": ["GraphQL", "Docker"],
  "yearsExperienceRequired": 4,
  "createdAt": "2024-12-26T10:00:00Z",
  "updatedAt": "2024-12-26T10:00:00Z",
  "embeddingStored": true
}
```

**Endpoint**: `GET /api/job-descriptions/{id}`

- Retrieve job description with cached embedding status

---

## 3. Database Schema

### Candidates Table
```sql
CREATE TABLE candidates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  phone VARCHAR(20),
  resume_text TEXT,
  resume_url VARCHAR(500),
  extracted_skills JSONB DEFAULT '[]',
  years_experience INTEGER,
  current_status VARCHAR(50) DEFAULT 'Applied',
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by UUID REFERENCES users(id),
  INDEX idx_email (email),
  INDEX idx_status (current_status),
  INDEX idx_created_at (created_at)
);
```

### Job Descriptions Table
```sql
CREATE TABLE job_descriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  required_skills JSONB DEFAULT '[]',
  nice_to_have_skills JSONB DEFAULT '[]',
  years_experience_required INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by UUID REFERENCES users(id),
  INDEX idx_title (title),
  INDEX idx_created_at (created_at)
);
```

### Match Results Table
```sql
CREATE TABLE match_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
  job_id UUID NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
  match_score NUMERIC(5,2) CHECK (match_score >= 0 AND match_score <= 100),
  tfidf_score NUMERIC(5,2),
  semantic_score NUMERIC(5,2),
  matched_skills JSONB DEFAULT '[]',
  missing_skills JSONB DEFAULT '[]',
  matched_keywords JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(candidate_id, job_id),
  INDEX idx_candidate_id (candidate_id),
  INDEX idx_job_id (job_id),
  INDEX idx_match_score (match_score DESC)
);
```

### Embeddings Collection (ChromaDB)
- **Collection Name**: `candidates_resumes`
- **Documents**: Resume text for each candidate
- **Embeddings**: Generated using sentence-transformers/all-MiniLM-L6-v2
- **Metadata**: `{ candidate_id, created_at, skills }`

---

## 4. NLP Pipeline Components

### A. Resume Parser
- **Inputs**: PDF/DOCX file or text
- **Processing**:
  - Text extraction via pypdf
  - Named Entity Recognition (NER) using spaCy
  - Skill extraction via regex patterns and entity matching
  - Date parsing for work experience
- **Outputs**: Structured candidate profile with skills, experience, education

### B. Matching Engine
- **Inputs**: Resume text, job description
- **Processing**:
  - TF-IDF vectorization on text
  - Cosine similarity calculation
  - Skill extraction and matching
  - Semantic similarity via ChromaDB embeddings
- **Outputs**: Match score (0-100), matched/missing skills, keyword matches

### C. Embeddings Manager
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Storage**: ChromaDB (persistent)
- **Use Cases**:
  - Semantic search (natural language queries)
  - Similarity ranking between candidates
  - Semantic duplicate detection
- **Batch Processing**: Generate embeddings for resumes asynchronously

### D. Semantic Search
- **Algorithm**: Vector similarity search via ChromaDB
- **Query Processing**:
  - Parse natural language query to skill keywords
  - Generate query embedding
  - Search similar resumes in ChromaDB
  - Combine with TF-IDF results for ranking
- **Caching**: Cache popular queries (1-hour TTL)

---

## 5. Performance & Caching Strategy

### Caching Layers

**1. Application Cache (Redis)**:
- Cache parsed resumes (24-hour TTL)
- Cache ranking results per job (1-hour TTL)
- Cache semantic search queries (30-minute TTL)

**2. Database Query Cache**:
- SQLAlchemy query result caching
- Materialized views for frequently accessed reports

**3. Embedding Cache**:
- Pre-computed embeddings in ChromaDB
- Background regeneration for updated resumes

### Performance Targets

| Operation | Target | Strategy |
|-----------|--------|----------|
| Resume parsing | <5s | Async queue with 4 workers |
| Semantic search | <500ms | ChromaDB + embedding cache |
| Candidate ranking | <3s | TF-IDF + cached results |
| API response | <100ms | Query optimization + indices |

### Monitoring Metrics

- API response time distribution (p50, p95, p99)
- Cache hit rates by endpoint
- Parser success rate and error distribution
- Embedding generation throughput
- Database query performance (slow query log)

---

## 6. Security & Input Validation

### Request Validation

- **Zod/Pydantic Schemas**: All API inputs validated with strict types
- **File Upload**: Whitelist file types (PDF, DOCX, TXT), max 10MB
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **Rate Limiting**: 100 requests/minute per API key (10/minute for file uploads)
- **CORS**: Restrict to `http://localhost:3000` (frontend) and `http://localhost:8000` (internal)

### Authentication & Authorization

- **JWT Tokens**: Signed with HS256, 1-hour expiry
- **API Keys**: For service-to-service communication
- **Role-Based Access**: Admin (full), Recruiter (read/write), Guest (read-only)

### Data Protection

- **Resume Text**: Encrypted at rest (optional)
- **Email/Phone**: Hashed for GDPR compliance
- **Audit Trail**: Log all candidate status changes and searches
- **Data Retention**: Configurable retention policy (default 2 years)

---

## 7. Error Handling & Logging

### Error Response Format

```json
{
  "status": "error",
  "code": "VALIDATION_ERROR",
  "message": "Invalid file format",
  "details": [
    {
      "field": "file",
      "message": "Only PDF and DOCX files are supported"
    }
  ],
  "timestamp": "2024-12-26T10:30:00Z",
  "requestId": "req-uuid-789"
}
```

### Logging Strategy

- **Level**: DEBUG (dev), INFO (staging), ERROR (prod)
- **Format**: Structured JSON logs with request ID tracing
- **Outputs**: Console (dev), File + Datadog (prod)
- **Sensitive Data**: Mask emails, phone numbers, API keys in logs

### Exception Handling

- **HTTP Exceptions**: Map domain errors to HTTP status codes
- **Graceful Degradation**: Fall back to TF-IDF if embeddings unavailable
- **Circuit Breaker**: Timeout after 30s for external API calls (OpenAI, Google)

---

## 8. Deployment & Infrastructure

### Environment Configuration

- **Development**: Local PostgreSQL, ChromaDB in-memory, debug=true
- **Staging**: Cloud PostgreSQL, Docker ChromaDB, debug=false
- **Production**: RDS PostgreSQL, Kubernetes ChromaDB, monitoring enabled

### Container & Orchestration

- **Docker**: Multi-stage build with Python 3.12 slim
- **Kubernetes**: Horizontal Pod Autoscaling (HPA) on CPU > 70%
- **Environment Variables**: Managed via .env files (dev) and secrets (prod)

### Database Migrations

- **Tool**: Alembic with SQLAlchemy
- **Strategy**: Automated migrations on startup, versioned in git
- **Rollback**: Support for downgrade scripts

---

## 9. Testing Strategy

### Unit Testing (Pytest)

**Framework**: Pytest with async support (pytest-asyncio)

**Test Coverage Targets**:
1. **Resume Parser** (`tests/unit/test_parser.py`)
   - PDF text extraction
   - Skill extraction accuracy
   - Date parsing edge cases
   - Error handling for corrupted files

2. **Matching Engine** (`tests/unit/test_matcher.py`)
   - TF-IDF score calculation
   - Cosine similarity results
   - Score normalization (0-100 range)
   - Missing/matched skills extraction

3. **Embeddings Manager** (`tests/unit/test_embeddings.py`)
   - Embedding generation consistency
   - ChromaDB storage and retrieval
   - Semantic search accuracy

4. **Database Models** (`tests/unit/test_models.py`)
   - Schema validation
   - Relationship integrity
   - Cascade delete behavior

5. **API Schemas** (`tests/unit/test_schemas.py`)
   - Pydantic validation
   - Required field enforcement
   - Type coercion

**Coverage Target**: >80% for business logic

### Integration Testing (Pytest)

**Test Scenarios**:
1. **End-to-End Resume Processing** (`tests/integration/test_resume_e2e.py`)
   - Upload → Parse → Store → Retrieve workflow

2. **Semantic Search Integration** (`tests/integration/test_search_integration.py`)
   - Index resumes → Query → Verify results

3. **Candidate Ranking** (`tests/integration/test_ranking_integration.py`)
   - Create job → Rank candidates → Verify ordering

4. **Database Transactions** (`tests/integration/test_transactions.py`)
   - Atomic operations
   - Rollback scenarios

### API Testing (Pytest + httpx)

**Endpoints Covered**:
- `POST /api/parse-resume` (file upload)
- `POST /api/semantic-search` (query)
- `GET /api/candidates` (list with filters)
- `PATCH /api/candidates/{id}/status` (update)
- `POST /api/job-descriptions` (create)

**Test Data**: Fixtures with sample resumes, job descriptions

### Performance Testing (Locust)

**Scenarios**:
- Concurrent resume uploads (50 users)
- Concurrent semantic searches (100 users)
- Candidate listing with pagination (200 users)

**SLAs**:
- P95 response time: <1s for reads, <3s for uploads
- Error rate: <1%
- Throughput: >1000 req/s on 4-core server

---

## 10. Technology Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | FastAPI 0.104+ | Web API server |
| **Python** | 3.11-3.14 | Language runtime |
| **Database** | PostgreSQL + SQLAlchemy | Structured data storage |
| **Embeddings** | ChromaDB + sentence-transformers | Semantic search |
| **NLP** | spaCy + NLTK + scikit-learn | Text processing |
| **PDF Parsing** | pypdf | Resume extraction |
| **Async** | asyncio + uvicorn | High-concurrency I/O |
| **Validation** | Pydantic v2 | Request/response schemas |
| **Testing** | Pytest + pytest-asyncio | Unit & integration tests |
| **Monitoring** | Structured logging | Observability |
| **Caching** | Redis (optional) + in-memory | Performance optimization |

---

## Summary

✅ **Requirements Met**:
- High-performance async API for NLP tasks
- Dual-algorithm matching (TF-IDF + semantic)
- Robust resume parsing and skill extraction
- Semantic search with natural language queries
- Production-ready error handling and logging
- >80% test coverage for critical paths
- Type-safe Pydantic schemas
- Comprehensive API documentation

❌ **Future Enhancements**:
- LLM-powered skill extraction (GPT-4, Gemini)
- Real-time pipeline status notifications (WebSockets)
- Candidate communication templates
- Interview scheduling integration
- Automated rejection emails


