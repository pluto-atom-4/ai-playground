# MCP Server Implementation - Python Model Context Protocol

This guide covers implementing and testing MCP (Model Context Protocol) servers in Python using two modern approaches: **FastMCP** (lightweight, pure MCP) and **FastAPI-MCP** (full RESTful API integration).

## Table of Contents

1. [Overview](#overview)
2. [Server Types](#server-types)
3. [Project Structure](#project-structure)
4. [Core Implementation Guidelines](#core-implementation-guidelines)
5. [FastMCP Server Implementation](#fastmcp-server-implementation)
6. [FastAPI MCP Server Implementation](#fastapi-mcp-server-implementation)
7. [Testing with mcp dev Inspector](#testing-with-mcp-dev-inspector)
8. [Development Workflow](#development-workflow)

## Overview

The Model Context Protocol (MCP) enables seamless integration between applications and AI models through standardized tool exposure. This guide covers two implementation approaches:

- **FastMCP**: Lightweight MCP server following the specification with optional REST API
- **FastAPI-MCP**: Full-featured REST API with integrated MCP tools

Example tools demonstrated:
- **echo_string**: Echoes a string message back to the caller
- **add_numbers**: Adds two numbers together
- **get_string_length**: Returns the length of a string

## Server Types

### FastMCP (Recommended for Pure MCP)

**Use when:**
- You need a lightweight MCP-compliant server
- You want to follow the Model Context Protocol specification closely
- You may add optional REST API endpoints later
- You need simple tool registration via decorators

**Technologies:**
- FastMCP: Lightweight MCP server framework
- Python asyncio: Async/await support
- Optional: FastAPI for HTTP API integration

### FastAPI-MCP (Recommended for REST APIs)

**Use when:**
- You need a full-featured REST API with multiple endpoints
- You want comprehensive request/response validation
- You need API key authentication
- You want health checks and service metadata endpoints
- You need production-grade HTTP server capabilities

**Technologies:**
- FastAPI: RESTful API framework
- Uvicorn: ASGI server
- Pydantic: Request/response validation
- FastApiMCP: Optional MCP integration layer

## Project Structure

```
src/
├── __init__.py              # Package initialization
├── __main__.py              # Entry point
├── server.py                # FastMCP server implementation
├── desktop.py               # FastAPI-MCP server example
├── echo.py                  # Echo server with REST API
└── logging_and_progress.py  # Logging/progress example

tests/
├── test_server.py           # FastMCP server tests
├── test_desktop.py          # FastAPI-MCP server tests
└── test_echo.py             # Echo server tests

.env                         # Development environment variables
.env.test                    # Test environment variables
```

## Core Implementation Guidelines

### Common Requirements (Both Server Types)

#### Logging
- **Level**: Set logging to `INFO` by default
- **Coverage**: Log all API errors and important events
- **Format**: Use structured logging with timestamps

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)
```

#### Validation
- **Use Pydantic models** for request/response validation
- **Validate all inputs** - Check parameters and API payloads
- **Error handling** - Return user-friendly validation error messages

#### Error Handling
- **Log errors** with context (request details, stack traces)
- **Return proper HTTP status codes** (400, 401, 403, 404, 500, etc.)
- **Never expose internals** - Don't leak stack traces to clients

#### API Key Authentication (for REST APIs)
- **Implementation**: Require API key for protected endpoints
- **Validation**: Validate API key on each request
- **Storage**: Load from environment variables via `.env` file
- **Headers**: Expect API key in `X-API-Key` header
- **Error handling**: Return 401 Unauthorized for missing/invalid keys

### Tool Definition with Decorators

Both server types use the `@mcp.tool` decorator to define MCP tools:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool(name="echo_string", description="Echo a string back")
def echo_string(message: str) -> str:
    """Tool function with proper docstring"""
    return f"Echo: {message}"

@mcp.tool(name="add_numbers", description="Add two numbers")
def add_numbers(a: float, b: float) -> float:
    """Tool function with parameter types"""
    return a + b
```

## FastMCP Server Implementation

FastMCP provides a lightweight, pure MCP implementation following the protocol specification.

### Basic Setup

```python
from mcp.server.fastmcp import FastMCP
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server instance
mcp = FastMCP("MyServer", json_response=True)

@mcp.tool(name="echo", description="Echo tool")
def echo(message: str) -> str:
    logger.info(f"Echo called with: {message}")
    return message

if __name__ == "__main__":
    logger.info("Starting FastMCP server...")
    mcp.run()
```

### Tool Registration

Register tools using the `@mcp.tool` decorator:

```python
@mcp.tool(name="tool_name", description="Tool description")
def tool_function(param1: str, param2: int = 10) -> dict:
    """
    Tool function with full documentation.
    
    Parameters are automatically converted to MCP schema.
    Return type becomes the tool output schema.
    """
    return {"param1": param1, "param2": param2}
```

### Resource Support (Optional)

Define resources for file/data access:

```python
@mcp.resource("resource://path")
def get_resource() -> str:
    """Get a resource"""
    return "resource content"
```

### Prompt Support (Optional)

Define prompts for common interactions:

```python
@mcp.prompt(name="greet")
def greet_prompt(name: str) -> str:
    """Greeting prompt"""
    return f"Hello, {name}!"
```

### Running FastMCP Server

```bash
# Option 1: Direct Python
python src/server.py

# Option 2: Python module
python -m src

# The server listens on stdio by default
```

### Testing FastMCP Server

Comprehensive testing for FastMCP servers:

```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_tool_execution():
    """Test tool execution with valid inputs"""
    result = echo("test message")
    assert result == "test message"

@pytest.mark.asyncio
async def test_async_tool():
    """Test async tool execution"""
    async def async_tool(text: str) -> str:
        return text.upper()
    
    result = await async_tool("hello")
    assert result == "HELLO"

def test_tool_schema():
    """Verify tool schema is properly defined"""
    # MCP automatically generates schema from type hints
    pass
```

**Key Testing Points:**
- ✅ Verify tools execute with correct inputs
- ✅ Test async and sync tool paths
- ✅ Validate tool schemas match MCP spec
- ✅ Check error handling with user-friendly messages
- ✅ Verify logging output
- ✅ Test edge cases (empty inputs, special characters, Unicode)

## FastAPI MCP Server Implementation

FastAPI-MCP provides a full-featured REST API with optional MCP integration.

### Basic Setup

```python
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP
import uvicorn
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
API_KEY = os.getenv("API_KEY", "default-key")

# Create FastAPI app
app = FastAPI(title="MCP Server", version="1.0.0")

# Create MCP server
mcp = FastMCP("MyServer")

# ... define tools with @mcp.tool ...

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="INFO")
```

### RESTful API Endpoints

Implement standard REST endpoints:

```python
@app.get("/")
async def service_info():
    """Service information"""
    return {
        "version": "1.0.0",
        "description": "MCP Server",
        "endpoints": ["/health", "/api/tools", "/api/tools/{tool_name}"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/api/tools")
async def list_tools():
    """List available MCP tools"""
    # Return list of tools with schemas
    return [...]

@app.post("/api/tools/{tool_name}")
async def invoke_tool(tool_name: str, request: ToolRequest):
    """Invoke an MCP tool"""
    # Execute tool and return result
    return {...}
```

### API Key Authentication

Require API key on protected endpoints:

```python
async def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from request header"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

@app.post("/api/tools/{tool_name}")
async def invoke_tool(
    tool_name: str,
    request: ToolRequest,
    _: str = Depends(verify_api_key)
):
    """Protected tool invocation endpoint"""
    return {...}
```

### Pydantic Models for Validation

```python
class ToolRequest(BaseModel):
    """Request model for tool invocation"""
    arguments: dict

class ToolResponse(BaseModel):
    """Response model for tool results"""
    result: dict
    tool_name: str
```

### Running FastAPI-MCP Server

```bash
# Start server with Uvicorn
uvicorn src.server:app --host 127.0.0.1 --port 8000 --log-level info

# With reload for development
uvicorn src.server:app --reload --log-level debug
```

### Testing FastAPI-MCP Server

```python
import pytest
from fastapi.testclient import TestClient
from src.server import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    return {"X-API-Key": "test-key"}

class TestServiceEndpoints:
    def test_service_info(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "version" in response.json()
    
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

class TestToolInvocation:
    def test_tool_list(self, client):
        response = client.get("/api/tools")
        assert response.status_code == 200
        tools = response.json()
        assert isinstance(tools, list)
    
    def test_invoke_tool_with_auth(self, client, auth_headers):
        response = client.post(
            "/api/tools/echo",
            headers=auth_headers,
            json={"arguments": {"message": "test"}}
        )
        assert response.status_code == 200

class TestAuthentication:
    def test_missing_api_key(self, client):
        response = client.post(
            "/api/tools/echo",
            json={"arguments": {"message": "test"}}
        )
        assert response.status_code == 401
    
    def test_invalid_api_key(self, client):
        response = client.post(
            "/api/tools/echo",
            headers={"X-API-Key": "wrong-key"},
            json={"arguments": {"message": "test"}}
        )
        assert response.status_code == 401
```

**Key Testing Points:**
- ✅ Test all REST endpoints (GET /, /health, /api/tools, POST /api/tools/{tool})
- ✅ Verify API key authentication (missing, invalid, valid)
- ✅ Test Pydantic validation for requests/responses
- ✅ Verify parameter passing via JSON body and query strings
- ✅ Test Unicode and special character handling
- ✅ Verify error responses include user-friendly messages
- ✅ Check appropriate HTTP status codes (200, 401, 404, 422, 500)
- ✅ Verify logging output at INFO level
- ✅ Test edge cases (empty values, invalid types, nonexistent tools)

## Testing with mcp dev Inspector

The MCP dev command provides an interactive web-based inspector for testing and debugging MCP servers. This is the recommended approach for both FastMCP and FastAPI-MCP server types.

### Installation

Install the MCP Inspector globally:

```bash
npm install -g @modelcontextprotocol/inspector
```

Or use with npx without installing:

```bash
npx @modelcontextprotocol/inspector
```

### Starting the Inspector for FastMCP

`mcp dev` automatically starts your server and launches the inspector in one command.

**Launch the inspector (development mode):**

```bash
# Using uv (recommended for MCP projects)
uv run mcp dev src/server.py
```

**With additional dependencies:**

```bash
# Add specific packages
uv run mcp dev src/server.py --with pandas --with numpy

# Mount local code for development
uv run mcp dev src/server.py --with-editable .
```

**Alternative with npx** (if not using uv):

```bash
npx @modelcontextprotocol/inspector src/server.py
```

**Access the web interface:**

- Inspector opens automatically at `http://localhost:5173`
- Shows a web-based UI for testing your MCP server
- No need to separately start the server - `mcp dev` does it for you

### Starting the Inspector for FastAPI-MCP

For FastAPI-MCP servers that support stdio-based MCP protocol, `mcp dev` can launch the inspector directly.

**If your FastAPI-MCP server uses stdio transport:**

```bash
# Launch inspector with development mode
uv run mcp dev src/server.py
```

With dependencies:

```bash
# Add packages if needed
uv run mcp dev src/server.py --with fastapi --with uvicorn
```

**If your FastAPI-MCP server uses HTTP-only transport:**

If your server only exposes REST API endpoints without MCP stdio support, test the API directly:

```bash
# Terminal 1: Start the FastAPI server
uvicorn src.server:app --host 127.0.0.1 --port 8000

# Terminal 2: In another terminal, test API endpoints
# List tools
curl http://localhost:8000/api/tools

# Invoke a tool
curl -X POST http://localhost:8000/api/tools/echo \
  -H "X-API-Key: test-key" \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"message": "test"}}'
```

**Recommended approach:**

For development and testing, ensure your FastAPI-MCP server supports the MCP protocol over stdio, allowing `mcp dev` to work seamlessly with both server types.

### Using the Inspector Web UI

Once the inspector is running at `http://localhost:5173`:

#### 1. **List Tools**
- Left sidebar shows all available MCP tools
- Click to view tool details
- Shows tool name, description, and input schema

#### 2. **Inspect Tool Schema**
- Center panel displays tool schema (parameters, types, requirements)
- Shows JSON Schema for inputs and outputs
- Verify parameter types and descriptions

#### 3. **Invoke Tools**
- Fill in tool parameters in the input form
- Click "Call Tool" to execute
- View results in real-time
- Shows response data and execution time

#### 4. **Test Edge Cases**
- Test with empty strings: `""`
- Test with special characters: `!@#$%^&*()`
- Test with Unicode: `中文 日本語 🎉`
- Test with large inputs
- Test with invalid parameter types

#### 5. **Debug Protocol Messages**
- View request/response JSON
- Check MCP protocol compliance
- Verify schema validation
- Review error messages

#### 6. **Monitor Logs**
- View server logs in real-time
- See execution traces
- Check error details

### Inspector Testing Workflow

Here's a recommended workflow for testing your MCP server:

```
1. Start MCP Server
   └─ python src/server.py

2. Start Inspector
   └─ mcp dev src/server.py

3. List All Tools
   └─ Verify all tools appear in sidebar

4. For Each Tool:
   ├─ Inspect Schema
   │  └─ Verify parameters match implementation
   ├─ Invoke with Valid Inputs
   │  └─ Verify correct output format
   ├─ Invoke with Invalid Inputs
   │  └─ Verify error messages are descriptive
   ├─ Test Edge Cases
   │  └─ Empty strings, Unicode, special characters
   └─ Check Response Time
      └─ Ensure execution is fast

5. Verify Logging
   └─ Check server logs for INFO messages

6. Test Error Handling
   ├─ Missing required parameters
   ├─ Invalid parameter types
   ├─ Tool not found
   └─ Server errors
```

### Example: Testing Echo Tool

```
1. Inspector shows "echo_string" tool
2. Click on tool to view schema:
   ├─ Name: echo_string
   ├─ Description: Echo a string back
   ├─ Input: { "message": string }
3. Enter test input: "Hello World"
4. Click "Call Tool"
5. View result: "Echo: Hello World"
6. Try edge cases:
   ├─ Empty string: ""
   ├─ Unicode: "你好世界"
   ├─ Special chars: "!@#$%^&*()"
```

### Inspector Advantages

- ✅ **Interactive Testing**: Execute tools without coding
- ✅ **Visual Schema**: See parameter requirements clearly
- ✅ **Real-time Feedback**: Immediate execution results
- ✅ **Protocol Compliance**: Verify MCP protocol adherence
- ✅ **Error Debugging**: Clear error messages and traces
- ✅ **Development Speed**: Test changes quickly
- ✅ **Integration Ready**: Test before client integration

### Troubleshooting Inspector

| Issue | Solution |
|-------|----------|
| **Inspector won't start** | Ensure Node.js/npm is installed: `node --version` |
| **Can't connect to server** | Verify server is running on expected stdio/port |
| **Tools not appearing** | Check server logs for initialization errors |
| **Tool invocation fails** | Verify input schema and parameter types in inspector |
| **Unicode not displaying** | Inspector handles UTF-8, check terminal encoding |
| **Timeout errors** | Tool may be hanging - check for infinite loops |

## Development Workflow

### 1. Setup Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Load development environment
cp .env.example .env
```

### 2. Implement Your Server

Choose FastMCP or FastAPI-MCP based on your requirements, then:

```bash
# Create your server file (src/my_server.py)
# Implement tools with @mcp.tool decorators
# Add logging at INFO level
# Include error handling
```

### 3. Test with Inspector

```bash
# Terminal 1: Start your server
python src/my_server.py

# Terminal 2: Start inspector
mcp dev src/my_server.py

# Visit http://localhost:5173 and test interactively
```

### 4. Verify with Automated Tests

```bash
# Run pytest suite
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_my_server.py -v
```

### 5. Code Quality Checks

```bash
# Run linting
ruff check src tests

# Format code
ruff format src tests

# Type checking
pyright
```

### 6. Deploy

```bash
# For FastMCP: Integrate with client application
# For FastAPI-MCP: Deploy with Uvicorn or gunicorn

# Example: Deploy FastAPI
gunicorn src.server:app -w 4 -b 0.0.0.0:8000
```

## References

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)

