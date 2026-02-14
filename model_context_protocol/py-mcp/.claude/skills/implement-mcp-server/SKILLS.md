---
name: implement-mcp-server
description: Build high-quality MCP (Model Context Protocol) servers using FastMCP with Python. Use when creating MCP servers to integrate external APIs or services, implementing tools, resources, or prompts, setting up logging and error handling, or refactoring existing servers to follow modern best practices. Provides patterns for architecture, Pydantic validation, pagination, and deployment via stdio transport.
---

# MCP Server Implementation Skill

This skill guides the implementation of Model Context Protocol (MCP) servers following modern Python best practices, focusing on code organization, logging, authentication, and transport handling.

## Quick Start

To build an MCP server:

1. Create server directory: `src/servers/my_server/`
2. Set up FastMCP with logging configuration
3. Define tools using `@mcp.tool` decorator
4. Use Pydantic models for input/output validation
5. Create `__main__.py` entry point
6. Test with MCP Inspector

## Core Server Architecture

Use FastMCP for modern, decorator-based server implementation:

```python
import logging
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import click

load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("my-server")

# Create FastMCP server
mcp = FastMCP("my-server")

@click.command()
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Set logging level",
)
def main(log_level: str = "INFO") -> int:
    """Start the MCP server"""
    logging.getLogger().setLevel(log_level.upper())
    logger.info(f"Set logging level to {log_level.upper()}")
    logger.info("Starting My Server")

    try:
        mcp.run()
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user (CTRL+C)")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        return 1
```

## Tool Implementation

All tools use decorator-based registration with Pydantic validation:

```python
from pydantic import BaseModel
from typing import Optional

class MyToolInput(BaseModel):
    """Input parameters"""
    param1: str
    param2: Optional[int] = None

class MyToolOutput(BaseModel):
    """Output structure"""
    result: str
    status: str = "success"

@mcp.tool(name="my_tool", description="Tool description")
async def my_tool(input_data: MyToolInput) -> MyToolOutput:
    logger.debug(f"Tool invoked: {input_data.param1}")
    try:
        result = process(input_data.param1)
        logger.info("Tool execution successful")
        return MyToolOutput(result=result, status="success")
    except Exception as e:
        logger.error(f"Tool failed: {e}", exc_info=True)
        return MyToolOutput(result=str(e), status="error")
```

## Key Design Decisions

### Transport

- **Stdio (Recommended):** Use `mcp.run()` for simple CLI integration
- **HTTP (When Needed):** Use `StreamableHTTPSessionManager` with Starlette

### Pagination

Use cursor-based pagination with string format:

```python
class ListInput(BaseModel):
    cursor: Optional[str] = None
    limit: int = 10

@mcp.tool(name="list_items", description="List items")
async def list_items(input_data: ListInput) -> dict:
    offset = 0
    if input_data.cursor:
        try:
            offset = int(input_data.cursor)
        except (ValueError, TypeError):
            logger.warning(f"Invalid cursor: {input_data.cursor}")
            offset = 0

    items = get_items(offset, input_data.limit)
    next_cursor = str(offset + input_data.limit) if len(items) == input_data.limit else None
    return {"items": items, "nextCursor": next_cursor}
```

### Resources and Prompts

For resource reading:

```python
@mcp.resource(uri_pattern="resource://*")
def read_resource(uri: str) -> str:
    logger.debug(f"Reading: {uri}")
    try:
        return get_resource_content(uri)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return str(e)
```

For prompt templates:

```python
from mcp.types import PromptMessage, TextContent

@mcp.tool(name="get_prompt", description="Get a prompt")
async def get_prompt(name: str) -> dict:
    messages = [
        PromptMessage(
            role="user",
            content=TextContent(type="text", text="Prompt content")
        )
    ]
    return {"messages": messages}
```

## Entry Point

Create `__main__.py` to make your server runnable as a Python module:

```python
"""MCP Server entry point.

This module allows the server to be run as:
  python -m src.servers.my_server

Also enables mcp-inspector discovery via:
  mcp-inspector "python -m src.servers.my_server"
"""

import sys
from src.servers.my_server.my_server_server import main

if __name__ == "__main__":
    sys.exit(main())
```

**Key points:**
- Always use `sys.exit()` instead of `exit()`
- Include docstring explaining invocation methods
- This enables `mcp-inspector` to discover and test your server
- Directory structure must be a proper Python package with `__init__.py`

## Module Discovery & Invocation

For `mcp-inspector` and other MCP clients to discover your server, it must be:

1. **Runnable as a Python module** with `python -m package.module`
2. **Create a `FastMCP` instance at module level** (not inside functions)
3. **Properly structured** with `__init__.py` in all directories
4. **Invoked correctly** with the proper command pattern

### Correct Directory Structure

```
src/servers/my_server/
├── __init__.py                    # Makes it a Python package
├── __main__.py                    # Entry point for python -m
└── my_server_server.py           # Main implementation
```

### Invocation Patterns

**Pattern 1: Python Module (Recommended)**
```bash
mcp-inspector "python -m src.servers.my_server"
```

**Pattern 2: Direct Python File**
```bash
mcp-inspector "python /full/path/to/my_server_server.py"
```

**Pattern 3: With Environment Variables**
```bash
mcp-inspector "python -m src.servers.my_server --log-level DEBUG"
```

### What NOT to Do

❌ `mcp-inspector #file:my_server.py`
❌ `mcp-inspector src/servers/my_server/my_server_server.py`
❌ `mcp-inspector relative/path/to/server.py`
❌ Creating `FastMCP` instance inside `main()` (won't be discoverable)

## Logging

Configure at startup with appropriate levels:

- **DEBUG:** Tool invocation details, parameters, server startup
- **INFO:** Server startup, successful operations, tool executions
- **WARNING:** Invalid input, recoverable issues, cursor parsing
- **ERROR:** Exceptions (always use `exc_info=True`)

## Error Handling

Return errors gracefully in output models:

```python
try:
    result = perform_operation(input_data)
    return ToolOutput(result=result, status="success")
except ValueError as e:
    logger.warning(f"Invalid input: {e}")
    return ToolOutput(result=str(e), status="error")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return ToolOutput(result="Internal error", status="error")
```

## Reference Files

See detailed guidance in:

- **patterns.md** - Server architecture, Pydantic models, pagination, resources/prompts, transport, error handling, testing
- **checklist.md** - Decision tree, implementation phases, configuration checklists, migration patterns, troubleshooting
- **examples.md** - Tool templates, pagination, resources, prompts, complete server, testing, refactoring

## Guidelines

### Do's
- ✅ Use `@server.tool()` decorator for tools
- ✅ Define Pydantic models for inputs/outputs
- ✅ Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- ✅ Handle errors gracefully (raise exceptions or return error status)
- ✅ Create `__main__.py` entry point for module runnable
- ✅ Use cursor-based pagination for list operations
- ✅ **Create `FastMCP` instance at module level** (for discovery - CRITICAL)
- ✅ Use `sys.exit()` instead of `exit()` in entry points
- ✅ Include docstring explaining how to run the server
- ✅ Make all imports at the top of the file
- ✅ Use simple async functions as tools (parameter inference)
- ✅ **Test ONLY with `mcp-inspector "python -m package.module"`** (verified method)
- ✅ Run mcp-inspector from the project root directory

### Don'ts
- ❌ **Don't create `FastMCP` instance inside `main()`** (won't be discoverable by mcp-inspector)
- ❌ **Don't use `mcp dev` for testing** (has Windows path parsing bugs - use mcp-inspector instead)
- ❌ Don't use the low-level `Server` class (use FastMCP only)
- ❌ Don't use `if __name__ == "__main__": main()` in server module (use `__main__.py`)
- ❌ Don't add `--port` option to server (unless running HTTP separately)
- ❌ Don't raise exceptions for invalid cursors (handle gracefully)
- ❌ Don't expose stack traces in responses
- ❌ Don't use raw dicts (use Pydantic models)
- ❌ Don't try to invoke with `#file:` syntax or file paths
- ❌ Don't forget to include `__init__.py` in server directory
- ❌ Don't run mcp-inspector from subdirectories (run from project root)

## Dependencies

```
fastmcp
pydantic
python-dotenv
click
mcp
```

Optional for HTTP:
```
uvicorn
starlette
```

## Testing

### Method 1: Using mcp-inspector (ONLY Recommended Method)

**This is the only reliable, cross-platform way to test MCP servers.**

```bash
# Navigate to project root
cd C:\path\to\your\project

# Run with mcp-inspector
mcp-inspector "python -m src.servers.my_server"
```

**What happens:**
1. Server starts and logs: `Starting My Server`
2. Inspector connects via stdio protocol
3. Discovers all `@server.tool()` decorated functions
4. Shows list of available tools
5. Allows tool invocation and testing
6. Displays results and logs

**Example output:**
```
Tool: long_running_task
Description: A task that takes a few seconds to complete with status updates
Status: Ready to invoke
```

### Method 2: Manual server execution (debugging only)

For debugging or standalone testing:

```bash
# Run server directly
python -m src.servers.my_server --log-level DEBUG

# In separate terminal, use your MCP client to connect via stdio
# (The server writes protocol messages to stdout)
```

### Verification Checklist

Before running with `mcp-inspector`, verify your server setup:

```python
# Run this Python code in your project root:
from src.servers.my_server.my_server_server import server

print(f"Server type: {type(server).__name__}")  # Should be: FastMCP
print(f"Server location: module-level")          # Should be discoverable
print(f"Has __main__.py: Yes")                   # Required
```

### Troubleshooting Tests

| Issue | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError` | Python path not set | Run from project root; check `__init__.py` in all directories |
| Port 6277 already in use | Inspector already running | Kill existing process: `lsof -i :6277 \| kill` |
| `No tools found` | Tools not registered | Verify `@server.tool()` decorators; FastMCP instance at module level |
| Server hangs on startup | Blocking I/O in tool | Move blocking operations to async tasks |
| `KeyboardInterrupt` doesn't work | Poor exception handling | Ensure `try/except KeyboardInterrupt` in main |

### ⚠️ Why NOT to Use `mcp dev`

`mcp dev` is **NOT recommended** for testing MCP servers:

**Problem on Windows:**
```bash
# This FAILS with path parsing errors:
mcp dev .\src\servers\my_server\my_server_server.py

# Results in malformed path:
File not found: C:\...\.srcserverssimple_tasksimple_task_server.py
```

**Why it fails:**
- Windows path separators (backslashes) not handled correctly
- Relative path resolution issues
- Forward slashes in paths get lost

**Use `mcp-inspector` instead** - it's designed for MCP server testing and works reliably across all platforms.

## Common Issues & Troubleshooting

### Error: "File not found" when using `mcp dev` (CRITICAL - Windows Users)

**Problem:** When you run:
```bash
mcp dev src/servers/my_server/my_server_server.py
```

You get:
```
File not found: C:\...\.srcserverssimple_tasksimple_task_server.py
```

**Root Cause:** `mcp dev` has a critical bug with path parsing on Windows. It:
- Drops forward slashes from paths
- Concatenates path components without separators
- Results in malformed file paths

**Solution (REQUIRED):** **NEVER use `mcp dev` for testing.** Use `mcp-inspector` instead:

```bash
# Correct - use module invocation
mcp-inspector "python -m src.servers.my_server"
```

This approach:
- ✅ Avoids all path parsing issues
- ✅ Works on Windows, macOS, and Linux
- ✅ Properly discovers FastMCP instances
- ✅ Is the MCP protocol standard for testing

### Error: "expecting <class 'mcp.server.fastmcp.server.FastMCP'>"

**Problem:** You're using the low-level `Server` class instead of `FastMCP`:

```python
# ❌ Wrong - causes mcp dev error
from mcp.server import Server
from mcp.server.lowlevel.server import RequestContext

server = Server("my-server")

@server.call_tool()
async def handle_call_tool(ctx: RequestContext, params: types.CallToolRequestParams):
    # Low-level API - NOT compatible with mcp dev
```

**Solution:** Refactor to use FastMCP:

```python
# ✅ Correct
from mcp.server.fastmcp import FastMCP

server = FastMCP("my-server")

@server.tool()
async def my_tool(param: str) -> str:
    # Simple, declarative API - works with mcp dev
    return f"Result: {param}"
```

**Key differences:**
- **Low-level Server:** Uses `RequestContext`, `call_tool()`, `list_tools()` handlers with manual response construction
- **FastMCP:** Uses simple decorated async functions, automatic schema generation from function signatures
- **Transport:** Low-level supports Starlette/HTTP; FastMCP works directly with stdio/mcp dev

### Error: "File not found" with mcp-inspector

**Problem:** Trying to run mcp-inspector with a file path or `#file:` syntax:

```bash
# ❌ These don't work
mcp-inspector #file:simple_task_server.py
mcp-inspector src/servers/simple_task/simple_task_server.py
mcp-inspector /path/to/simple_task_server.py
```

**Solution:** Use proper module path with `python -m`:

```bash
# ✅ Correct
mcp-inspector "python -m src.servers.simple_task"
```

**Why:** MCP inspector needs a command that starts a server process. It can't directly load Python files. The `-m` flag tells Python to run a module, which executes `__main__.py`.

### Error: "No tools found" with mcp-inspector

**Problem:** Tools aren't discovered by mcp-inspector.

**Causes:**
1. `FastMCP` instance created inside `main()` (not discoverable)
2. Missing `__main__.py` file
3. Wrong invocation pattern

**Solution:**
- Move server instance to module level
- Create proper `__main__.py` entry point
- Use correct invocation: `mcp-inspector "python -m package.module"`


### Removing HTTP/Starlette Setup

If migrating from low-level Server with HTTP support, remove:

```python
# ❌ Remove these imports
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
import uvicorn

# ❌ Remove HTTP setup from main()
session_manager = StreamableHTTPSessionManager(app=server)
starlette_app = Starlette(routes=[Mount("/mcp", app=session_manager.handle_request)])
uvicorn.run(starlette_app, host="127.0.0.1", port=port)

# ✅ Replace with simple stdio
server.run()
```

## Configuration Files

For teams or deployment, use MCP configuration files to centralize server definitions:

### `.mcp/servers.json` or `cline_mcp_config.json`

```json
{
  "my-server": {
    "command": "python",
    "args": ["-m", "src.servers.my_server"],
    "type": "stdio",
    "description": "My MCP server"
  }
}
```

Then run with:
```bash
mcp-inspector my-server
```

**Benefits:**
- Centralized server configuration
- Easy to share across team
- Consistent invocation patterns
- Works with multiple MCP clients

## Real-World Example: simple_task_server

The `src/servers/simple_task/` in this project demonstrates the correct implementation:

**Files:**
- `simple_task_server.py` - FastMCP server with `long_running_task` tool
- `__main__.py` - Entry point for module discovery

**Verification Results (Confirmed Working):**

| Check | Result | Details |
|-------|--------|---------|
| FastMCP Instance | ✅ PASS | Found at module level, discoverable |
| Server Name | ✅ PASS | `simple-task-server` |
| Entry Point | ✅ PASS | `__main__.py` configured correctly |
| Tools Registered | ✅ PASS | `long_running_task` (async, decorated) |
| Module Runnable | ✅ PASS | Works with `python -m src.servers.simple_task` |
| mcp-inspector Test | ✅ PASS | Discovers all tools, invocation works |

**How to test it:**
```bash
cd C:\Users\nobu\Documents\JetBrains\ai-playground\model_context_protocol\py-mcp
mcp-inspector "python -m src.servers.simple_task"
```

**Also see generated documentation:**
- `generated/docs-copilot/SIMPLE_TASK_SERVER_RESOLUTION.md` - How the server was fixed
- `generated/docs-copilot/MCP_INSPECTOR_FILE_NOT_FOUND_FIX.md` - Detailed troubleshooting
- `generated/docs-copilot/MCP_INSPECTOR_QUICK_REFERENCE.md` - Quick start guide

## Key Findings

Based on testing with `simple_task_server`:

1. **`mcp dev` is unreliable on Windows** - Don't use it for testing
2. **`mcp-inspector` is the standard method** - Use module invocation: `python -m package.module`
3. **Module-level FastMCP instance is critical** - Must be discoverable by tools
4. **Proper entry point is required** - `__main__.py` is needed for `python -m` to work
5. **Run from project root** - Ensures relative imports and module paths work correctly

## References

- [Model Context Protocol](https://modelcontextprotocol.io)
- [FastMCP Documentation](https://github.com/jlopp/fastmcp)
- [Click Documentation](https://click.palletsprojects.com)
- [Pydantic Documentation](https://docs.pydantic.dev)
