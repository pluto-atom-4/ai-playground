# GitHub Copilot Instructions

**Purpose:** Suppress excessive file generation, maintain clean project structure, and use Git Bash for terminal operations.

---

## File & Documentation Generation

### Directory Rules
- **Output directory:** `generated/docs-copilot/` (auto-created)
- All generated files go to this subdirectory by default
- **Maximum documents per task:** 3 (unless explicit user request specifies otherwise)
- **Require explicit user request** before generating
- **Consolidate content** - Merge related documentation into fewer, comprehensive documents

### Document Suppression Strategy
- ❌ **Suppress excessive generation:** Do NOT create multiple partial documents
- ❌ **Consolidate before creating:** Always combine related content into single comprehensive files
- ❌ **Avoid redundancy:** One complete document > many fragmented ones
- ⚠️ **Review before creating:** Check if content can be added to existing documentation

### Suppress in Root
❌ `COMPLETION-SUMMARY.*`, `FINAL-.*`, `IMPLEMENTATION.*`, `*-COMPLETE.*`, `*-STATUS.*`, `*-SUMMARY.*`, `*-REPORT.*`, `QUICK_REFERENCE.*`, `INDEX.*`, `MANIFEST.*`, `CONFIGURATION.*`, `DELIVERABLES.*`

### Suppress in generated/docs-copilot/
❌ Multiple status/summary files: Keep max 1 per category
❌ Fragmented guides: Consolidate into single comprehensive guide
❌ Redundant task-specific files: Merge into primary documentation

### Preserve in Root Only
✅ `README.md`, `README-*.md`, `SETUP.md`, `CONTRIBUTING.md`, `LICENSE`

### Ideal Documentation Structure
For typical tasks, limit to 3 documents:
```
✅ generated/docs-copilot/IMPLEMENTATION_PLAN.md (comprehensive plan + checklist)
✅ generated/docs-copilot/QUICK_START.md (usage instructions + examples)
✅ generated/docs-copilot/API_REFERENCE.md (technical details + examples)
```

---

## Code Generation Rules

- Confirm before creating new files
- Prefer modifying existing files
- Keep changes focused and minimal

---

## Shell & Terminal Configuration

### Default Shell: bash.exe (Git Bash)

| Operation | Shell | Notes |
|-----------|-------|-------|
| ✅ Git operations | bash | POSIX paths: `/c/Users/...` |
| ✅ npm/node commands | bash | Auto-convert Windows paths |
| ✅ Python development | bash | |
| ✅ File/directory operations | bash | |
| ✅ Script execution | bash | |
| ❌ cmd.exe | | Avoid for grep, sed, awk, complex pipes |

### Git Configuration
- **Default branch:** main
- **Commit template:** `fix: {description}`
- **Auto-stage:** disabled

### Bash Environment
```
SHELL=bash
TERM=cygwin
Path conversion: C:\ → /c/
```

---

## Key Principles

1. **Maximum 3 documents** - Enforce strict document limit per task unless explicitly requested otherwise
2. **Consolidate over creation** - Always merge related content instead of creating new files
3. **Minimal generation** - Create only what's necessary
4. **Single source of truth** - `README.md` is primary documentation
5. **No redundant files** - One comprehensive document > many partial ones
6. **Git Bash always** - Use `bash.exe` for all terminal operations
7. **Keep root clean** - Generated content → `generated/docs-copilot/`

---

## MCP Server Implementation Guidelines

To implement an MCP server with modern Python best practices, follow these requirements:

### Core Technologies
- **Python**: Use Python 3.8+
- **FastAPI**: For RESTful API endpoints
- **Pydantic**: For complex model validation
- **Uvicorn**: For ASGI server
- **dotenv**: For environment variable management
- **logging**: Use Python's logging module
- **FastMCP**: Integrate as needed for MCP tool support

### Logging
- Set logging level to `INFO`
- Log all API errors and important events

### Validation
- Use complex Pydantic models for request/response validation

### MCP Tool Integration
- Use `@mcp.tool` decorator to define tool name and description

### RESTful API Endpoints
- Implement with FastAPI:
  - `GET /` — Returns service version, description, and available endpoints
  - `GET /health` — Health check endpoint
  - `GET /api/tools` — Returns list of available tools with descriptions
  - `POST /api/tools/{tool_name}` — Invokes the defined MCP tool

### Uvicorn Server
- Use Uvicorn to start the FastAPI app
- Allow configuration of host, port, and log level
- Ensure graceful shutdown on Ctrl+C

### Error Handling
- Log all API errors
- Return user-friendly error messages in API responses

### API Key Authentication
- Require API key for REST API authentication
- Validate API key on protected endpoints
