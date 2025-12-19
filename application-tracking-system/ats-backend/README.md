# Application Tracking System Backend

A high-performance FastAPI-based backend for the Application Tracking System with NLP capabilities for resume parsing, candidate matching, and ranking against job descriptions.

## Features

- **Resume Parsing**: Extract text and entities from PDF resumes
- **Candidate Matching**: TF-IDF and cosine similarity-based matching
- **Semantic Search**: Vector embeddings using Transformers and ChromaDB
- **Skill Extraction**: Identify skills from resumes and job descriptions
- **Ranking Engine**: Automatically rank candidates by relevance
- **LLM Integration**: Support for OpenAI and Google Gemini APIs

## Technology Stack

- **Framework**: FastAPI 0.104+
- **Python**: 3.14+
- **Database**: PostgreSQL for structured data
- **Embeddings**: ChromaDB with Sentence Transformers
- **NLP**: spaCy, NLTK, scikit-learn
- **LLMs**: OpenAI, Google Gemini
- **ORM**: SQLAlchemy 2.0+

## Installation

### Prerequisites

- Python 3.14 or higher
- PostgreSQL database
- Git

### Setup

1. **Clone the repository** (or navigate to the project directory)

2. **Create and activate virtual environment**:
   ```bash
   cd ats-backend
   python -m venv .venv
   source .venv/Scripts/activate  # On Windows Git Bash
   ```

3. **Install dependencies**:
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -e ".[dev]"
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Download spaCy model**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Development

### Code Quality

Run all checks before committing:

```bash
# Format code
black . && isort .

# Lint
ruff check . --fix

# Type checking
mypy .

# Tests
pytest --cov=src
```

### Running the Server

```bash
# Development mode (hot-reload)
fastapi dev src/main.py

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src

# Verbose output
pytest -v

# Specific test
pytest tests/test_parser.py::test_extract_text_from_pdf
```

## Project Structure

```
ats-backend/
├── src/
│   ├── main.py                 # FastAPI application entry
│   ├── api/
│   │   ├── routes/             # API route handlers
│   │   └── dependencies.py     # Dependency injection
│   ├── core/
│   │   ├── config.py           # Configuration management
│   │   └── security.py         # Authentication utilities
│   ├── models/
│   │   └── schemas.py          # Pydantic data schemas
│   ├── services/               # Business logic
│   ├── nlp/
│   │   ├── parser.py           # Resume parsing
│   │   ├── matcher.py          # Candidate matching
│   │   └── embeddings.py       # Vector embeddings
│   └── database/
│       ├── session.py          # DB session management
│       └── models.py           # SQLAlchemy ORM models
├── tests/                      # Test suite
├── pyproject.toml              # Project configuration
├── .env.example                # Environment template
└── .env                        # Local environment (not committed)
```

## API Endpoints

### Health Check

- `GET /health` - Application health status

### Candidates

- `POST /api/candidates` - Create a new candidate
- `GET /api/candidates` - List all candidates
- `GET /api/candidates/{id}` - Get candidate details
- `PUT /api/candidates/{id}` - Update candidate
- `DELETE /api/candidates/{id}` - Delete candidate

### Job Descriptions

- `POST /api/jobs` - Create a new job description
- `GET /api/jobs` - List all job descriptions
- `GET /api/jobs/{id}` - Get job details

### Matching

- `POST /api/match` - Calculate match score for candidate-job pair
- `POST /api/match/rank` - Rank candidates for a job

## Environment Variables

See `.env.example` for all available configuration options:

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for LLM integration
- `GOOGLE_API_KEY`: Google API key for Gemini
- `SPACY_MODEL`: spaCy model to use
- `CHROMA_DB_PATH`: Path for vector database storage

## Development Workflow

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes and run tests: `pytest`
3. Format and lint: `black . && isort . && ruff check . --fix`
4. Type check: `mypy .`
5. Commit with descriptive message: `git commit -m "feature: add new feature"`
6. Push to repository: `git push origin feature/my-feature`

## Contributing

Please follow the guidelines in `CONTRIBUTING.md` and ensure all tests pass before submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Import errors for NLP libraries

If you encounter import errors:

1. Ensure virtual environment is activated
2. Run `pip install -e ".[dev]"` to install all dependencies
3. For spaCy models: `python -m spacy download en_core_web_sm`

### Database connection issues

1. Verify PostgreSQL is running
2. Check `DATABASE_URL` in `.env` is correct
3. Ensure database exists and user has permissions

### ModuleNotFoundError

Make sure you're running commands from the `ats-backend` directory with the virtual environment activated.

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/)
- [spaCy Documentation](https://spacy.io/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)

