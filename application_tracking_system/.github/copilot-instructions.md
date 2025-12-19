# GitHub Copilot Instructions

**Purpose:** Guide AI-assisted development for a dual-stack project supporting both Python and Next.js applications with consistent workflows and best practices.

---

## Project Overview

This workspace contains multiple applications:
- **Python Backend**: Application Tracking System with NLP capabilities (FastAPI)
- **Next.js Frontend**: React-based dashboard with AI integration
- Both share unified development practices and tooling standards

---

## File & Documentation Generation

### Directory Rules
- **Output directory:** `generated/docs-copilot/` (auto-created)
- All generated files must go to this subdirectory
- **Maximum files per session:** 1 per application
- **Require explicit user request** before generating

### Suppress in Root
❌ Files to avoid in project root:
- `COMPLETION-SUMMARY.*`, `FINAL-.*`, `IMPLEMENTATION.*`
- `*-COMPLETE.*`, `*-STATUS.*`, `*-SUMMARY.*`, `*-REPORT.*`
- `QUICK_REFERENCE.*`, `INDEX.*`, `MANIFEST.*`, `CONFIGURATION.*`, `DELIVERABLES.*`

### Preserve in Root Only
✅ Only these documentation files in root:
- `README.md`, `README-*.md`, `SETUP.md`, `CONTRIBUTING.md`, `LICENSE`

### Correct File Paths
```
✅ generated/docs-copilot/QUICKSTART.md
✅ generated/docs-copilot/API_REFERENCE.md
✅ generated/docs-copilot/SETUP_GUIDE.md
```

---

## Code Generation Rules

- Confirm before creating new files
- Prefer modifying existing files
- Keep changes focused and minimal
- Follow language-specific standards (see below)

---

## Shell & Terminal Configuration

### Default Shell: bash.exe (Git Bash)

**All terminal operations must use Git Bash (bash.exe) with Unix-style commands.**

| Operation | Shell | Notes |
|-----------|-------|-------|
| ✅ Git operations | bash | POSIX paths: `/c/Users/...` |
| ✅ npm/pnpm commands | bash | Auto-convert Windows paths |
| ✅ Python development | bash | Virtual environment support |
| ✅ File/directory operations | bash | Use `find`, `grep`, `sed`, etc. |
| ✅ Script execution | bash | `.sh` scripts and bash operations |
| ❌ cmd.exe | | Avoid for complex pipes and text processing |

### Git Configuration
- **Default branch:** main
- **Commit template:** `fix: {description}`
- **Auto-stage:** disabled

### Bash Environment
```
SHELL=C:\Program Files\Git\bin\bash.exe
MSYSTEM=MINGW64
TERM=xterm-256color
Path conversion: C:\ → /c/ (POSIX style)
```

**Console Prompt Format:**
```
username@hostname MINGW64 ~/path/to/repo (branch)
$ 
```

**Example:**
```
nobu@KUMATA MINGW64 ~/Documents/JetBrains/ai-playground/application_tracking_system (main)
$ 
```

---

## Python Application Guidelines

### Technology Stack
- **Framework**: FastAPI - High-performance async API for NLP tasks
- **Python**: 3.114 or higher with latest security updates
- **Package Manager**: uv or pip with `pyproject.toml`
- **Database**: PostgreSQL for structured data, ChromaDB for embeddings
- **NLP Libraries**: spaCy, NLTK, Hugging Face Transformers, scikit-learn

### Environment Management

#### Virtual Environment Setup for ats-backend
```bash
# 1. Navigate to ats-backend directory (if in monorepo)
cd ats-backend

# 2. Create virtual environment using venv (recommended)
python -m venv .venv

# 3. Activate virtual environment (Windows Git Bash)
source .venv/Scripts/activate

# 4. Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel

# 5. Install dependencies with dev extras
pip install -e ".[dev]"
```

**Alternative: Using uv (faster)**
```bash
# One-command setup with uv
cd ats-backend
uv sync
uv sync --group dev
```

#### Project Configuration
- **Config File**: `pyproject.toml` (primary source of truth for all dependencies)
- **Location**: `ats-backend/pyproject.toml`
- **Lock File**: `uv.lock` (if using uv) or `pip-freeze.txt`
- **Dev Dependencies**: Defined in `pyproject.toml` under `[project.optional-dependencies]` with key `dev`
- **.env File**: `ats-backend/.env` (copy from `.env.example` after setup)

### Development Workflow for ats-backend

**Prerequisites**: Virtual environment activated (see setup above)

```bash
# 1. Ensure dependencies are installed
pip install -e ".[dev]"  # Install with dev dependencies

# 2. Code formatting and linting (run before commits)
black . && isort .      # Format code with black and organize imports
ruff check . --fix      # Lint and auto-fix with ruff

# 3. Type checking
mypy .                  # Strict type checking

# 4. Testing
pytest                  # Run test suite
pytest --cov=src       # Run with coverage report
pytest -v              # Verbose output

# 5. Start development API server (hot-reload)
fastapi dev src/main.py  # Runs on http://localhost:8000

# 6. Full pre-commit check
black . && isort . && ruff check . --fix && mypy . && pytest
```

### Python Code Guidelines

- Write with **PEP 8** compliance
- Use **type hints** for all functions and classes
- Implement **docstrings** using Google or NumPy style
- Leverage **async/await** for I/O operations in FastAPI
- Use **Pydantic v2** for data validation and serialization
- Structure with **Domain-Driven Design** principles
- Keep modules focused on single responsibility

### Python File Structure

```
ats-backend/
├── src/
│   ├── main.py                 # FastAPI application entry
│   ├── api/
│   │   ├── routes/
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── models/                 # Pydantic models
│   ├── schemas/                # Data schemas
│   ├── services/               # Business logic
│   ├── nlp/                    # NLP modules
│   │   ├── parser.py
│   │   ├── matcher.py
│   │   └── embeddings.py
│   └── database/
├── tests/
├── pyproject.toml
├── .env
└── .env.example
```

---

## Next.js Application Guidelines

### Technology Stack
- **Framework**: Next.js (App Router)
- **Language**: TypeScript with strict mode
- **Package Manager**: pnpm (not npm or yarn)
- **React**: Version 19.2 with latest features
- **Styling**: Tailwind CSS v4
- **AI Integration**: @ai-sdk, @ai-sdk/react, @ai-sdk/openai
- **Validation**: Zod for runtime schema validation

### Package Manager: pnpm for ats-frontend

**Always use pnpm - never npm or yarn**

```bash
# 1. Navigate to ats-frontend directory (if in monorepo)
cd ats-frontend

# 2. Install dependencies (creates pnpm-lock.yaml)
pnpm install

# 3. Add new package
pnpm add package-name

# 4. Add dev dependency
pnpm add --save-dev package-name

# 5. Remove package
pnpm remove package-name
```

### Development Workflow for ats-frontend

**Prerequisites**: pnpm installed and dependencies installed (see setup above)

```bash
# 1. Ensure dependencies are installed
pnpm install  # Creates pnpm-lock.yaml

# 2. Start development server (hot-reload)
pnpm dev      # Runs on http://localhost:3000

# 3. Check code quality (run before commits)
pnpm lint    # Run ESLint
pnpm type-check  # TypeScript type checking

# 4. Build for production
pnpm build

# 5. Run tests (if configured)
pnpm test

# 6. Full pre-commit check
pnpm type-check && pnpm lint && pnpm build
```

### TypeScript & Code Guidelines

- **Strict Mode**: Always enabled in `tsconfig.json`
- **Type Safety**: Explicit types for all function parameters and returns
- **Functional Components**: Use React functional components with hooks
- **Error Boundaries**: Wrap component trees for error handling
- **Zod Schemas**: Use for API request/response validation
- **Performance**: Implement React.memo and useMemo where appropriate

### Next.js File Structure

```
ats-frontend/
├── src/
│   ├── app/                    # App Router directory
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── api/                # Route handlers
│   │   └── (routes)/
│   ├── components/
│   │   ├── ui/                 # Reusable UI components
│   │   ├── features/           # Feature-specific components
│   │   └── layouts/
│   ├── hooks/                  # Custom React hooks
│   ├── lib/                    # Utility functions
│   ├── services/               # API client services
│   ├── types/                  # TypeScript type definitions
│   └── styles/
├── public/                     # Static assets
├── tests/                      # Test files
├── package.json
├── pnpm-lock.yaml
├── tsconfig.json
├── next.config.ts
├── tailwind.config.ts
└── .eslintrc.json
```

### Tailwind CSS & Styling

- Use **Tailwind utilities** instead of custom CSS
- Leverage **Tailwind plugins** for custom components
- Create **component classes** in `globals.css` or component files
- Use **@apply** directive sparingly for grouped utilities
- Follow **dark mode** conventions if enabled

---

## Key Principles

1. **Minimal Generation** - Create only what's necessary
2. **Single Source of Truth** - `README.md` and `project_planning.md` are primary references
3. **No Redundant Files** - One comprehensive document > many partial ones
4. **Consistent Shell** - Always use `bash.exe` for terminal operations
5. **Keep Root Clean** - Generated content goes to `generated/docs-copilot/`
6. **Language-Specific Tools** - Use pyproject.toml for Python, pnpm for Next.js
7. **Type Safety** - TypeScript strict mode and Python type hints mandatory
8. **API First** - Design endpoints and schemas before implementation
9. **Testing** - Write tests alongside code for both Python and TypeScript
10. **Documentation** - Update docs when making breaking changes

---

## General Development Practices

### Git Workflow
- Commit frequently with descriptive messages
- Use feature branches for new work
- Keep commits atomic and focused
- Reference issues in commit messages

### Code Quality
- **Python**: Black, isort, Ruff, mypy
- **TypeScript**: ESLint, Prettier (if configured)
- Run linters before committing
- Fix all linting warnings, not just errors

### Testing Standards
- **Python**: pytest with >80% coverage
- **TypeScript**: Jest or Vitest (if configured)
- Write unit tests for business logic
- Integration tests for API endpoints

### Documentation
- Inline comments for complex logic only (code should be self-documenting)
- Keep README.md updated with setup and usage
- Document breaking changes immediately
- Use type hints and docstrings as documentation

---

## Project-Specific Notes

This project implements an **Application Tracking System** with NLP capabilities:
- Parse and extract data from resumes (PDF/text)
- Match candidates against job descriptions
- Rank applicants by relevance using TF-IDF and semantic similarity
- Provide visual dashboard for recruiters
- Integrate with LLMs (OpenAI, Google Gemini) for semantic matching

See `project_planning.md` for architecture details and tech stack rationale.

---

## Summary

✅ **Do**
- Use bash.exe for all terminal operations
- Manage Python via pyproject.toml and uv/pip
- Manage Node.js dependencies via pnpm only
- Write type-safe code (Python hints, TypeScript strict)
- Generate docs only to `generated/docs-copilot/`
- Keep changes minimal and focused

❌ **Don't**
- Create files in project root (except README.md variants)
- Use cmd.exe for terminal operations
- Use npm or yarn (pnpm only)
- Generate excessive documentation
- Mix code styles between Python and TypeScript
- Commit without running linters and tests

