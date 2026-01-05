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

