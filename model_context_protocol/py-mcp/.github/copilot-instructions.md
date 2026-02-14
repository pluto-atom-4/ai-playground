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

## MCP Server Implementation

When implementing Model Context Protocol (MCP) servers in this project, refer to the comprehensive **MCP Server Implementation Skill** documentation:

📖 **Location:** `.claude/skills/implement-mcp-server/SKILLS.md`

This skill provides:
- Core server architecture patterns using FastMCP
- Tool implementation with Pydantic validation
- Testing strategies and mcp-inspector usage
- Common issues and troubleshooting solutions
- Real-world working examples from this project

**Use this skill when:**
- Creating new MCP servers
- Implementing tools, resources, or prompts
- Setting up logging and error handling
- Testing with mcp-inspector
- Troubleshooting server issues

---

## Troubleshooting Guide

### Common Issues & Solutions

#### Issue: Test Failures with "import not found"
**Cause**: Virtual environment not activated or dependencies not installed  
**Solution**:
```bash
# Ensure dependencies are installed
pip install -e .
# Then run tests
pytest
```

#### Issue: "TypeError: got an unexpected keyword argument 'scope'"
**Cause**: Using fixture with positional argument instead of keyword argument  
**Solution**:
```python
# ❌ Wrong - scope as positional argument
@pytest.fixture(scope="session")
def client():
    return TestClient(app)

# ✅ Correct - scope as keyword argument
@pytest.fixture(scope="session")
def client():
    return TestClient(app)
```

#### Issue: API Key Authentication Failing in Tests
**Cause**: TEST_API_KEY environment variable not set  
**Solution**:
```bash
# Load test environment variables
source .env.test
# Or set directly
export TEST_API_KEY="test-key-12345"
# Then run tests
pytest
```

#### Issue: FastMCP Inspector Shows "Connection refused"
**Cause**: MCP server not running or wrong port  
**Solution**:
1. Start your MCP server: `python src/server.py`
2. In another terminal, run: `mcp-inspector`
3. Open http://localhost:5173 in browser
4. Verify server is responding to protocol messages

#### Issue: Pydantic Validation Errors with Valid Data
**Cause**: Field type mismatch or missing required field  
**Solution**:
```bash
# Check the actual error message
# Run test with verbose output
pytest -v -s

# Check your Pydantic model
# Print the schema to see requirements
python -c "from your_module import YourModel; print(YourModel.schema())"
```

#### Issue: Unicode Characters Breaking in Responses
**Cause**: Encoding mismatch between request/response  
**Solution**:
```python
# Ensure UTF-8 encoding in FastAPI
app = FastAPI(...)
# Response models work with unicode automatically
# Test with parametrized unicode inputs
@pytest.mark.parametrize("text", ["Hello", "中文", "🎉"])
def test_unicode(text):
    # Your test here
    pass
```

#### Issue: Tool Invocation Timeout or Hangs
**Cause**: Tool has infinite loop or blocking I/O without timeout  
**Solution**:
```python
# Add timeout to tool definition
@server.tool(timeout=30)  # 30-second timeout
def my_tool(param: str) -> str:
    # Always include exit condition
    # Use async for I/O operations
    return result

# Test with timeout
def test_tool_timeout(client, auth_headers):
    response = client.post(
        "/api/tools/my-tool",
        headers=auth_headers,
        json={"param": "test"},
        timeout=5  # 5-second test timeout
    )
```

---

## Environment Management

### Environment Files

#### Development Environment (.env)
```
# For local development - use safe defaults
ENVIRONMENT=development
LOG_LEVEL=DEBUG
API_KEY=dev-key-only-for-local-testing
DATABASE_URL=sqlite:///./test.db
DEBUG=true
ALLOW_CORS=true
```

#### Testing Environment (.env.test)
```
# For pytest runs - NEVER use real credentials
ENVIRONMENT=testing
TEST_API_KEY=test-key-12345
LOG_LEVEL=INFO
TESTING=true
DEBUG=false
DATABASE_URL=sqlite:///:memory:
```

#### Production Environment (.env.production)
```
# For production deployment - use secrets manager
ENVIRONMENT=production
LOG_LEVEL=WARNING
API_KEY=${SECRETS_API_KEY}  # Injected from secrets manager
DATABASE_URL=${SECRETS_DB_URL}
DEBUG=false
ALLOW_CORS=false
```

### Loading Environment Variables

```python
# In your main server file (src/server.py)
import os
from dotenv import load_dotenv
import logging

# Determine environment
env = os.getenv("ENVIRONMENT", "development")

# Load appropriate .env file
if env == "testing":
    load_dotenv(".env.test")
elif env == "production":
    load_dotenv(".env.production", override=False)
else:
    load_dotenv(".env")

# Validate required variables
REQUIRED_VARS = ["API_KEY", "LOG_LEVEL"]
missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
if missing:
    raise RuntimeError(f"Missing required environment variables: {missing}")

logger = logging.getLogger(__name__)
logger.info(f"Environment: {env}, Log Level: {os.getenv('LOG_LEVEL')}")
```

### Environment Variable Guidelines

| Variable | Dev | Test | Prod | Notes |
|----------|-----|------|------|-------|
| `ENVIRONMENT` | development | testing | production | Controls behavior |
| `LOG_LEVEL` | DEBUG | INFO | WARNING | Verbosity control |
| `API_KEY` | test value | test-key-12345 | secrets mgr | Never hardcode |
| `TESTING` | false | true | false | Skip expensive ops |
| `DEBUG` | true | false | false | Debug mode |

### Secrets Management Best Practices

- ❌ **Never** commit `.env` files with real secrets
- ❌ **Never** use production credentials in development
- ❌ **Never** hardcode API keys in code
- ✅ **Always** use environment variables for secrets
- ✅ **Always** add `.env*` to `.gitignore`
- ✅ **Always** use secrets manager (AWS Secrets, HashiCorp Vault) in production
- ✅ **Always** rotate secrets regularly

### Local Development Setup

```bash
# 1. Create .env from template
cp .env.example .env

# 2. Edit .env with your local settings
nano .env

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install dependencies
pip install -e .

# 5. Run development server
python -m src.server
```

---

## Security Guidelines

### API Key Management

#### Secure Key Generation
```bash
# Generate a strong random key (32 bytes = 256 bits)
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Output example: 7X_kQ1pM8-vN2hL4jR6wS9tU3aB5cD7e9F0gH2i

# Store in .env (never in code)
echo "API_KEY=7X_kQ1pM8-vN2hL4jR6wS9tU3aB5cD7e9F0gH2i" >> .env
```

#### API Key Validation in FastAPI
```python
from fastapi import Header, HTTPException, status

async def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from request header"""
    valid_key = os.getenv("API_KEY")
    if not x_api_key or x_api_key != valid_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return x_api_key

@app.post("/api/tools/{tool_name}")
async def invoke_tool(
    tool_name: str,
    _: str = Depends(verify_api_key),
):
    # Protected endpoint
    pass
```

### HTTPS/TLS Requirements

- ✅ **Always** use HTTPS in production (never HTTP)
- ✅ **Always** validate SSL certificates
- ✅ **Always** use strong cipher suites
- ✅ **Consider** HSTS headers (HTTP Strict Transport Security)
- ✅ **Use** TLS 1.2 or higher

### Input Validation & Sanitization

- ✅ **Always** validate input types with Pydantic
- ✅ **Always** check input length/size limits
- ✅ **Always** sanitize string inputs (prevent injection)
- ❌ **Never** use user input in system commands

```python
from pydantic import BaseModel, Field, validator

class ToolInput(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    timeout: int = Field(default=30, ge=1, le=300)
    
    @validator('message')
    def validate_message(cls, v):
        # Prevent script injection
        if '<script>' in v.lower() or '<?php' in v.lower():
            raise ValueError('Scripts not allowed in message')
        return v.strip()
```

### Error Handling & Information Disclosure

- ✅ **Return** generic error messages to clients
- ✅ **Log** detailed errors for debugging
- ❌ **Never** expose stack traces to clients
- ❌ **Never** reveal internal paths or database names

```python
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    # Log detailed error for debugging
    logger.error(f"Internal error: {exc}", exc_info=True)
    # Return generic message to client
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### Logging Best Practices

- ✅ **Log** all authentication attempts (success and failure)
- ✅ **Log** all tool invocations with execution time
- ✅ **Monitor** for unusual patterns (rate limit spikes, repeated failures)
- ❌ **Never** log sensitive data (API keys, passwords, tokens)

```python
# Good: Logs the action but not the secret
logger.info(f"Tool invocation: {tool_name} by client")

# Bad: Logs sensitive data - NEVER do this!
logger.info(f"API Key: {api_key}")  # ❌ Security breach!
```

### Dependency Security

- ✅ **Regularly** update dependencies: `pip list --outdated`
- ✅ **Scan** for vulnerabilities: `pip-audit` or `safety check`
- ✅ **Pin** versions in production: `pip freeze > requirements-lock.txt`
- ✅ **Review** CHANGELOG before major updates

```bash
# Scan for known vulnerabilities
pip install pip-audit
pip-audit

# Generate lock file for reproducible builds
pip freeze > requirements-lock.txt
```

---

## Performance Guidelines

### Response Time Targets

Define acceptable latency for each endpoint:

| Endpoint | Target | Max Acceptable | Notes |
|----------|--------|-----------------|-------|
| GET / | < 10ms | 50ms | Service info |
| GET /health | < 5ms | 20ms | Health check |
| GET /api/tools | < 50ms | 100ms | Tool list (cached) |
| POST /api/tools/{tool} | < 1s | 5s | Tool invocation |

### Measuring Performance

```python
import time
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow requests
    if process_time > 1.0:
        logger.warning(
            f"Slow request: {request.method} {request.url.path} "
            f"took {process_time:.2f}s"
        )
    
    return response
```

### Optimization Techniques

#### 1. Response Caching
```python
from fastapi_cache2 import FastAPICache2

# Cache tool list for 5 minutes
@app.get("/api/tools", response_cache_ttl=300)
async def list_tools():
    return get_tools()
```

#### 2. Connection Pooling
```python
import aiohttp

session = None

@app.on_event("startup")
async def startup():
    global session
    session = aiohttp.ClientSession()

@app.on_event("shutdown")
async def shutdown():
    await session.close()
```

#### 3. Async Operations
```python
import asyncio

@app.post("/api/tools/fetch-data")
async def fetch_data():
    # Concurrent I/O operations
    results = await asyncio.gather(
        fetch_external_api_1(),
        fetch_external_api_2(),
    )
    return results
```

### Load Testing

```bash
# Using Apache Bench (ab)
ab -n 1000 -c 10 http://localhost:8000/api/tools

# Using wrk (recommended)
wrk -t4 -c100 -d30s http://localhost:8000/api/tools

# Using locust (with test file)
pip install locust
locust -f locustfile.py -H http://localhost:8000
```

### Resource Limits

Set reasonable limits to prevent abuse:

```python
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
import json

# Maximum body size: 1MB
MAX_BODY_SIZE = 1024 * 1024

class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.headers.get("content-length"):
            content_length = int(request.headers["content-length"])
            if content_length > MAX_BODY_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request body too large"}
                )
        return await call_next(request)

app.add_middleware(BodySizeLimitMiddleware)
```

---

## MCP Inspector Tool

### @modelcontextprotocol/inspector

**Purpose**: Inspector is a development tool provided by the Model Context Protocol that enables debugging, testing, and introspection of MCP servers.

**Installation**: Install globally using npm:
```bash
npm install -g @modelcontextprotocol/inspector
```

**Usage**:
- **Start MCP Server**: Launch your MCP server (FastAPI or FastMCP)
- **Run Inspector**: Execute `mcp-inspector` or `mcp <server-path>` to start the inspection UI
- **Debug Tools**: Provides a web-based interface to:
  - List available tools on the server
  - Inspect tool schemas and parameters
  - Execute tools with test inputs
  - View responses and error messages
  - Debug protocol communication

**Key Features**:
- ✅ Web-based UI for tool inspection
- ✅ Interactive tool invocation with live feedback
- ✅ Protocol compliance verification
- ✅ Request/response logging and debugging
- ✅ Schema validation visualization

**Development Workflow**:
1. Start your MCP server
2. Launch inspector pointing to your server
3. Test tools interactively before integration
4. Verify request/response formats
5. Debug protocol issues in real-time

---

## MCP Server Implementation Guidelines

To implement MCP servers with modern Python best practices, follow these requirements. Choose the appropriate server type based on your use case.

---

## Common MCP Server Instructions

These guidelines apply to all MCP server implementations (FastAPI and FastMCP types).

### Core Technologies
- **Python**: Use Python 3.8+
- **dotenv**: For environment variable management
- **logging**: Use Python's logging module

### Logging
- **Level**: Set logging level to `INFO`
- **Coverage**: Log all API errors and important events
- **Format**: Use structured logging with timestamps and log levels
- **Example**: Include request/response details, exception traces, and configuration loaded messages

### Validation
- **Use complex Pydantic models** for request/response validation
- **Validation scope**: Validate all input parameters and API payloads
- **Error responses**: Return validation errors in user-friendly format

### Error Handling
- **Logging**: Log all API errors with context (request details, stack traces)
- **Responses**: Return user-friendly error messages in API responses
- **HTTP Status**: Use appropriate HTTP status codes (400, 401, 403, 404, 500, etc.)
- **Format**: Return errors as JSON objects with descriptive messages

### API Key Authentication
- **Implementation**: Require API key for REST API authentication
- **Validation**: Validate API key on protected endpoints
- **Storage**: Load API key from environment variables via `.env` file
- **Headers**: Expect API key in `X-API-Key` header (or configurable header)
- **Error handling**: Return 401 Unauthorized for missing/invalid keys

---

## FastAPI MCP Server

Use FastAPI when you need a full RESTful API with multiple endpoints, request validation, and web server capabilities integrated with MCP.

### Core Technologies
- **FastAPI**: For RESTful API endpoints and server framework
- **Pydantic**: For complex model validation
- **Uvicorn**: For ASGI server
- **FastApiMCP** (from `fastapi_mcp`): Optional integration for MCP tool support (use if needed for custom MCP tool registration and management)

### MCP Tool Integration
- **Decorator**: Use `@mcp.tool` decorator to define tool name and description
- **Purpose**: Define custom MCP tools that can be invoked via REST API
- **Registration**: Register tools with the MCP server instance

### RESTful API Endpoints
Implement the following endpoints using FastAPI:

- **`GET /`** — Service information
  - Returns: `{"version": "...", "description": "...", "endpoints": [...]}`
  - Purpose: Provides service metadata and available endpoints

- **`GET /health`** — Health check endpoint
  - Returns: `{"status": "healthy"}`
  - Purpose: Verify server is running and responsive

- **`GET /api/tools`** — List available tools
  - Returns: List of available MCP tools with their descriptions and schemas
  - Purpose: Discover available tools that can be invoked

- **`POST /api/tools/{tool_name}`** — Invoke MCP tool
  - Payload: Tool-specific arguments as JSON
  - Returns: Tool execution result
  - Purpose: Execute a defined MCP tool with parameters
  - **Authentication**: Require valid API key

### Uvicorn Server Configuration
- **Server**: Use Uvicorn to start the FastAPI app
- **Configuration**:
  - `host`: Configurable (default: `127.0.0.1`)
  - `port`: Configurable (default: `8000`)
  - `log_level`: Configurable (default: `INFO`)
- **Shutdown**: Handle graceful shutdown on Ctrl+C (SIGINT)
- **Example**: `uvicorn.run(app, host=HOST, port=PORT, log_level=LOG_LEVEL)`

### Testing FastAPI MCP Server

FastAPI MCP servers should be tested using both manual testing with REST clients and automated testing with pytest to ensure API endpoints work correctly, validation passes, and MCP tool integration functions properly.

#### Manual Testing with TestClient

Use `FastAPI.TestClient` to test API endpoints in a controlled environment:

**Setup**:
```python
from fastapi.testclient import TestClient
from your_mcp_server import app

# Create test client for testing endpoints without running server
client = TestClient(app)
```

**Testing Workflow**:
- ✅ **Test Service Information**: Verify `GET /` returns service metadata with version, description, and endpoints
- ✅ **Test Health Check**: Verify `GET /health` returns `{"status": "healthy"}`
- ✅ **Test Tool Discovery**: Verify `GET /api/tools` returns list of available MCP tools with complete schemas
- ✅ **Test Tool Invocation**: Verify `POST /api/tools/{tool_name}` executes tools with correct parameters
- ✅ **Test API Key Authentication**: Verify endpoints validate API keys in `X-API-Key` header
- ✅ **Test Parameter Passing**: Verify parameters passed via query strings and JSON bodies are correctly handled
- ✅ **Test Special Characters**: Verify endpoints handle special characters and Unicode in inputs

#### Automated Testing with pytest

Write comprehensive automated tests for FastAPI MCP server endpoints using `pytest`:

**Test Configuration** (`pyproject.toml` or `pytest.ini`):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
log_cli = true
log_cli_level = "INFO"
```

**Test Structure**:
```python
import pytest
import os
from fastapi.testclient import TestClient
from your_mcp_server import app

# Use environment variable for test API key
TEST_API_KEY = os.getenv("TEST_API_KEY", "test-key-12345")

@pytest.fixture(scope="session")
def client():
    """Create FastAPI TestClient for all tests"""
    return TestClient(app)

@pytest.fixture
def valid_api_key():
    """Provide valid API key for authenticated endpoints"""
    return TEST_API_KEY

@pytest.fixture
def auth_headers(valid_api_key):
    """Provide authorization headers for authenticated requests"""
    return {"X-API-Key": valid_api_key}

class TestServiceEndpoints:
    """Test public service information endpoints"""

    def test_service_info(self, client):
        """Test GET / returns service metadata"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "description" in data
        assert "endpoints" in data
        assert isinstance(data["endpoints"], list)

    def test_health_check(self, client):
        """Test GET /health indicates server is running"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"

class TestToolDiscovery:
    """Test tool listing and schema discovery endpoints"""

    def test_tool_list_success(self, client):
        """Test GET /api/tools returns available MCP tools"""
        response = client.get("/api/tools")
        assert response.status_code == 200
        tools = response.json()
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_tool_schema_completeness(self, client):
        """Test each tool has required schema fields"""
        response = client.get("/api/tools")
        tools = response.json()
        
        for tool in tools:
            assert "name" in tool, f"Tool missing 'name' field"
            assert "description" in tool, f"Tool missing 'description' field"
            assert "inputSchema" in tool, f"Tool missing 'inputSchema' field"
            assert isinstance(tool["inputSchema"], dict), f"inputSchema must be a dict"

class TestToolInvocation:
    """Test tool execution via POST endpoints"""

    def test_tool_invocation_with_query_params(self, client, auth_headers):
        """Test POST /api/tools/{tool_name} with query string parameters"""
        response = client.post(
            "/api/tools/echo",
            headers=auth_headers,
            params={"message": "Hello World"}
        )
        assert response.status_code == 200
        result = response.json()
        assert result.get("echo") == "Hello World"

    def test_tool_invocation_with_json_body(self, client, auth_headers):
        """Test tool invocation with JSON request body"""
        response = client.post(
            "/api/tools/echo",
            headers=auth_headers,
            json={"message": "JSON Test"}
        )
        assert response.status_code == 200
        result = response.json()
        assert result.get("echo") == "JSON Test"

    def test_tool_invocation_with_unicode(self, client, auth_headers):
        """Test tool correctly handles Unicode and special characters"""
        test_inputs = [
            "ASCII: abc123!@#",
            "Unicode: 中文 日本語 한국어",
            "Emoji: 🎉 🚀 ✨",
            "Mixed: Hello 世界 !@# 🌟"
        ]
        
        for test_msg in test_inputs:
            response = client.post(
                "/api/tools/echo",
                headers=auth_headers,
                params={"message": test_msg}
            )
            assert response.status_code == 200
            assert response.json().get("echo") == test_msg

    def test_tool_invocation_nonexistent(self, client, auth_headers):
        """Test invoking nonexistent tool returns 404"""
        response = client.post(
            "/api/tools/nonexistent_tool",
            headers=auth_headers,
            params={"message": "test"}
        )
        assert response.status_code == 404

class TestAuthentication:
    """Test API key authentication and authorization"""

    def test_missing_api_key_returns_unauthorized(self, client):
        """Test protected endpoint without API key returns 401"""
        response = client.post(
            "/api/tools/echo",
            params={"message": "test"}
        )
        assert response.status_code == 401
        error_data = response.json()
        assert "detail" in error_data

    def test_invalid_api_key_returns_unauthorized(self, client):
        """Test protected endpoint with invalid API key returns 401"""
        response = client.post(
            "/api/tools/echo",
            headers={"X-API-Key": "invalid-key-xyz"},
            params={"message": "test"}
        )
        assert response.status_code == 401

    def test_valid_api_key_grants_access(self, client, auth_headers):
        """Test protected endpoint with valid API key succeeds"""
        response = client.post(
            "/api/tools/echo",
            headers=auth_headers,
            params={"message": "authorized"}
        )
        assert response.status_code == 200

class TestValidation:
    """Test request validation and error handling"""

    def test_missing_required_parameter(self, client, auth_headers):
        """Test tool invocation without required parameter returns 422"""
        response = client.post(
            "/api/tools/echo",
            headers=auth_headers
        )
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

    def test_invalid_parameter_type_validation(self, client, auth_headers):
        """Test Pydantic validates parameter types"""
        # Assuming message parameter expects string
        response = client.post(
            "/api/tools/echo",
            headers=auth_headers,
            json={"message": 12345}  # Integer instead of string
        )
        # Either coerces to string (200) or returns validation error (422)
        assert response.status_code in [200, 422]

    def test_response_structure_compliance(self, client):
        """Test responses follow declared Pydantic models"""
        response = client.get("/api/tools")
        assert response.status_code == 200
        data = response.json()
        
        # Response should be list of tool objects
        assert isinstance(data, list)
        if len(data) > 0:
            tool = data[0]
            assert isinstance(tool, dict)

class TestErrorHandling:
    """Test error responses include user-friendly messages"""

    def test_auth_error_message_format(self, client):
        """Test authentication error has descriptive message"""
        response = client.post(
            "/api/tools/echo",
            params={"message": "test"}
        )
        assert response.status_code == 401
        error_data = response.json()
        assert "detail" in error_data
        error_msg = error_data["detail"]
        assert len(error_msg) > 0
        assert isinstance(error_msg, str)

    def test_tool_error_user_friendly_message(self, client, auth_headers):
        """Test tool execution errors return descriptive messages"""
        # Invoke tool with edge case that triggers error
        response = client.post(
            "/api/tools/echo",
            headers=auth_headers,
            params={"message": ""}  # Empty string test
        )
        
        if response.status_code >= 400:
            error_data = response.json()
            assert "detail" in error_data or "message" in error_data
            error_text = error_data.get("detail") or error_data.get("message")
            assert len(error_text) > 0
```

**Key Testing Points**:
- ✅ Verify all RESTful endpoints (GET /, /health, /api/tools, POST /api/tools/{tool_name})
- ✅ Test API key authentication on protected endpoints (missing, invalid, valid)
- ✅ Validate Pydantic model validation for request/response data
- ✅ Test parameter passing via query strings and JSON bodies
- ✅ Test handling of Unicode, special characters, and emoji in inputs
- ✅ Verify error responses include user-friendly, descriptive messages
- ✅ Test appropriate HTTP status codes (200, 401, 404, 422)
- ✅ Check logging output at INFO level via pytest logging capture
- ✅ Test edge cases (missing parameters, invalid types, nonexistent tools, empty values)
- ✅ Organize tests into logical classes by functionality (service, tools, auth, validation)

**Test Environment Setup**:

Create `.env.test` for test-specific configuration:
```
TEST_API_KEY=test-key-12345
LOG_LEVEL=DEBUG
```

Configure pytest to load test environment:
```python
# In conftest.py
import os
from dotenv import load_dotenv

def pytest_configure(config):
    """Load test environment variables before running tests"""
    load_dotenv(".env.test")
```

**Running Tests**:
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/ --cov-report=html

# Run specific test class
pytest tests/test_mcp_server.py::TestToolInvocation

# Run specific test function
pytest tests/test_mcp_server.py::TestToolInvocation::test_tool_invocation_with_query_params

# Run with verbose output (shows all test names)
pytest -v

# Run with print statements visible
pytest -s

# Run with logging output
pytest --log-cli-level=INFO

# Run with coverage and stop on first failure
pytest --cov=src/ -x
```

---

## FastMCP Server

Use FastMCP when you need a lightweight MCP server implementation following the Model Context Protocol specification, with optional REST API capabilities.

### Core Technologies
- **FastMCP**: For MCP server implementation and tool support
- **Python asyncio**: For async/await support
- **dotenv**: For environment configuration
- **logging**: For server logging

### MCP Tool Integration
- **Decorator**: Use `@mcp.tool` decorator to define tool name and description
- **Purpose**: Define MCP tools that conform to the MCP specification
- **Implementation**: Tools should support both synchronous and asynchronous execution
- **Schema**: Tools must define proper input/output schemas

### Server Lifecycle
- **Initialization**: Load configuration from environment variables
- **Startup**: Set up logging, validate configuration, initialize tools
- **Running**: Accept MCP protocol messages and route to appropriate tools
- **Shutdown**: Graceful cleanup on termination (SIGTERM, SIGINT)

### Configuration
- **Environment variables**: Load from `.env` file using python-dotenv
- **Logging**: Configure logging level and format
- **Timeout**: Set appropriate timeouts for tool execution

### Testing FastMCP Server

FastMCP servers must be tested using both manual inspection and automated testing approaches to ensure protocol compliance, tool functionality, and robustness.

#### Manual Testing with Inspector

Use `@modelcontextprotocol/inspector` to test and validate FastMCP server implementations interactively:

**Setup Steps**:
1. Install the inspector globally:
   ```bash
   npm install -g @modelcontextprotocol/inspector
   ```

2. Start your FastMCP server:
   ```bash
   python your_mcp_server.py
   ```

3. Run the inspector with your server:
   ```bash
   mcp-inspector <path-to-your-server>
   ```

**Testing Workflow**:
- ✅ **List Tools**: View all registered MCP tools in the web UI
- ✅ **Inspect Schemas**: Verify tool parameters and return types
- ✅ **Execute Tools**: Invoke tools interactively with test inputs
- ✅ **Validate Protocol**: Ensure proper MCP protocol compliance
- ✅ **Debug Messages**: Review request/response logs and error traces

#### Automated Testing with pytest

Write comprehensive automated tests for all MCP tools using `pytest`:

**Test Structure**:
```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
# Import your FastMCP server and tools

@pytest.mark.asyncio
async def test_tool_basic_functionality():
    """Test basic tool execution with valid inputs"""
    # Arrange: Set up test inputs and expected outputs
    # Act: Execute the tool
    # Assert: Verify the result matches expectations

@pytest.mark.asyncio
async def test_tool_schema_validation():
    """Test tool schema compliance with MCP specification"""
    # Verify tool has proper name and description
    # Validate input parameters match schema
    # Confirm return type matches schema

@pytest.mark.asyncio
async def test_tool_error_handling():
    """Test error handling and user-friendly error messages"""
    # Test with invalid inputs
    # Verify error messages are descriptive
    # Confirm errors don't crash the server

@pytest.mark.asyncio
async def test_async_tool_execution():
    """Test asynchronous tool execution"""
    # Execute async tools
    # Verify proper async/await handling
    # Check concurrent execution works correctly

@pytest.mark.asyncio
async def test_sync_tool_execution():
    """Test synchronous tool execution"""
    # Execute sync tools
    # Verify execution completes without blocking
    # Check return values match expectations
```

**Protocol Message Mocking**:

Mock MCP protocol messages to simulate client interactions:

```python
@pytest.mark.asyncio
async def test_protocol_message_handling():
    """Test server handles MCP protocol messages correctly"""
    # Mock CallToolRequest message
    mock_call_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "tool_name",
            "arguments": {"param1": "value1"}
        }
    }
    
    # Simulate protocol message exchange
    # Verify server response follows MCP spec
    # Check response includes proper metadata

@pytest.mark.asyncio
async def test_tool_list_request():
    """Test ListToolsRequest protocol message handling"""
    # Mock ListToolsRequest
    # Verify server returns complete tool list
    # Validate each tool has required fields (name, description, inputSchema)

@pytest.mark.asyncio
async def test_error_response_format():
    """Test error response follows MCP protocol format"""
    # Mock invalid request
    # Verify error response has correct structure
    # Check error includes proper error code and message
```

**Schema Validation Testing**:

Validate tool schemas and ensure compliance:

```python
def test_tool_schema_completeness():
    """Verify all tools have complete schemas"""
    # Iterate through all registered tools
    # Check each tool has: name, description, inputSchema
    # Validate inputSchema has required structure

def test_input_parameter_validation():
    """Test input parameter validation against schema"""
    # Test with valid parameters (should pass)
    # Test with missing required parameters (should fail)
    # Test with invalid parameter types (should fail)
    # Verify descriptive validation error messages

def test_return_type_compliance():
    """Test tool return types match schema"""
    # Execute tools
    # Verify return values match declared schema
    # Check no unexpected fields are returned
```

**Key Testing Points**:
- ✅ Verify `@mcp.tool` decorators are properly registered with names and descriptions
- ✅ Confirm tool input schemas match the MCP specification format
- ✅ Test asynchronous and synchronous tool execution paths
- ✅ Validate error handling with user-friendly error messages
- ✅ Check logging output at INFO level (use pytest logging capture)
- ✅ Mock protocol messages to test server behavior without real clients
- ✅ Test schema validation for inputs and outputs
- ✅ Verify graceful shutdown behavior
- ✅ Use `pytest-asyncio` for async test support
- ✅ Use `unittest.mock` for mocking protocol interactions

**Running Tests**:
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/

# Run specific test file
pytest tests/test_mcp_server.py

# Run with verbose output
pytest -v

# Run tests and show print statements
pytest -s
```

