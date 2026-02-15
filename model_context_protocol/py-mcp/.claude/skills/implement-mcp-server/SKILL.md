---
name: implement-mcp-server
description: Build high-quality MCP (Model Context Protocol) servers using FastMCP with Python. Use when creating MCP servers to integrate external APIs or services, implementing tools, resources, or prompts, setting up logging and error handling, or refactoring existing servers to follow modern best practices. Provides patterns for architecture, Pydantic validation, pagination, deployment via stdio transport, and comprehensive linting compliance.
---

# MCP Server Implementation Skill

This skill guides the implementation of Model Context Protocol (MCP) servers following modern Python best practices using FastMCP, focusing on code organization, logging, authentication, transport handling, and production-ready code quality (linting, type hints, error handling).

## Quick Start

To build an MCP server:

1. Create server directory: `src/servers/my_server/`
2. Set up FastMCP with logging configuration
3. Define tools using `@mcp.tool` decorator
4. Use Pydantic models for input/output validation
5. Create `__main__.py` entry point
6. Test with MCP Inspector: `mcp-inspector "python -m src.servers.my_server"`

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

# Create FastMCP server (module-level - CRITICAL for discovery)
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

## Entry Point Configuration

Create `__main__.py` to enable module execution:

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
- FastMCP instance must be created at module level (not inside functions)
- Include docstring explaining invocation methods
- This enables `mcp-inspector` to discover and test your server

## Testing Your Server

**Recommended Method: mcp-inspector** (Only reliable cross-platform method)

```bash
# Navigate to project root
cd /path/to/project

# Run with mcp-inspector
mcp-inspector "python -m src.servers.my_server"

# With custom log level
mcp-inspector "python -m src.servers.my_server --log-level DEBUG"
```

**⚠️ Important:** Do NOT use `mcp dev` - it has critical Windows path parsing bugs. Always use `mcp-inspector` with module invocation pattern.

## Guidelines

### Do's
- ✅ Use `@mcp.tool()` decorator for tools
- ✅ Define Pydantic models for inputs/outputs
- ✅ Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- ✅ Handle errors gracefully (return error status in output models)
- ✅ Create `__main__.py` entry point for module runnable
- ✅ Use cursor-based pagination for list operations
- ✅ **Create `FastMCP` instance at module level** (for discovery - CRITICAL)
- ✅ Use `sys.exit()` instead of `exit()` in entry points
- ✅ Make all imports at the top of the file
- ✅ Run mcp-inspector from the project root directory
- ✅ **Pass ruff linting checks** before deployment
- ✅ **Prefix unused function parameters with `_`** (e.g., `_ctx`, `_params`)
- ✅ **Remove all trailing whitespace** from code and docstrings
- ✅ **Use proper exception handling** with `exc_info=True` in error logs
- ✅ **Include docstrings** for module, functions, and classes

### Don'ts
- ❌ **Don't create `FastMCP` instance inside `main()`** (won't be discoverable)
- ❌ **Don't use `mcp dev` for testing** (has Windows path parsing bugs)
- ❌ Don't use the low-level `Server` class for simple tools (use FastMCP instead)
- ❌ Don't use `if __name__ == "__main__": main()` in server module (use `__main__.py`)
- ❌ Don't add `--port` option to server (unless running HTTP separately)
- ❌ Don't raise exceptions for invalid cursors (handle gracefully)
- ❌ Don't expose stack traces in responses
- ❌ Don't use raw dicts (use Pydantic models)
- ❌ Don't try to invoke with `#file:` syntax or file paths
- ❌ Don't forget to include `__init__.py` in server directory
- ❌ Don't run mcp-inspector from subdirectories (run from project root)
- ❌ **Don't leave unused function parameters uncommented** (fails ARG001 check)
- ❌ **Don't add whitespace to blank lines in docstrings** (fails W293 check)
- ❌ **Don't use print() for logging** (use `logger` instead)
- ❌ **Don't pass handler functions in `Server.__init__()`** - use property assignment instead
- ❌ **Don't import `ServerRequestContext`** - use `Any` type hint instead

## Code Quality & Linting Compliance

### Production-Ready Standards

All MCP servers in this project must pass **ruff linting checks** before being considered complete. This ensures consistency, maintainability, and adherence to Python standards.

### Common Linting Issues & Fixes

#### ARG001 - Unused Function Arguments
**Issue:** Functions have parameters that aren't used in the function body.

**Examples that fail:**
```python
# ❌ FAIL - ctx is not used
async def handle_list_tools(ctx: ServerRequestContext, params: Any) -> Any:
    return types.ListToolsResult(tools=[])
```

**Solution:** Prefix unused parameters with underscore:
```python
# ✅ PASS - Mark unused parameters with _
async def handle_list_tools(_ctx: ServerRequestContext, _params: Any) -> Any:
    return types.ListToolsResult(tools=[])
```

**When to use:**
- MCP handlers that receive parameters required by the protocol but don't use all of them
- Callback functions with fixed signatures
- Compatibility with existing interfaces

#### W293 - Trailing Whitespace in Blank Lines
**Issue:** Blank lines in docstrings or code contain whitespace characters.

**Examples that fail:**
```python
def main() -> int:
    """Start the server.
    
    Line with trailing spaces: ␣␣␣
    """
```

**Solution:** Remove all whitespace from blank lines:
```python
def main() -> int:
    """Start the server.

    No trailing spaces on blank line above.
    """
```

### Required Verification Steps

Before finalizing any MCP server implementation:

```bash
# 1. Run ruff linting check
python -m ruff check src/servers/my_server/

# 2. Run Python compilation check
python -m py_compile src/servers/my_server/*.py

# 3. Test with mcp-inspector
mcp-inspector "python -m src.servers.my_server"
```

**All three checks must pass.**

### Ruff Configuration

The project uses ruff with the following rules enabled:
- **E/W** - Error/Warning (PEP 8 violations)
- **F** - Pyflakes (undefined names, unused imports)
- **I** - isort (import sorting)
- **C** - McCabe complexity
- **B** - flake8-bugbear (likely bugs)
- **UP** - pyupgrade (modernize syntax)
- **ARG** - flake8-unused-arguments (unused parameters)
- **SIM** - flake8-simplify (code simplification)
- **LOG** - flake8-logging (logging best practices)

**Exception handling:**
- `E501` (line too long) - Ignored (handled by formatter)
- `E741` (ambiguous names like `l`, `O`) - Ignored

See `pyproject.toml` for full configuration.

## Reference Documentation

Detailed guidance is available in:

- **[patterns.md](references/patterns.md)** - Tool implementation, Pydantic models, pagination, resources/prompts, transport, error handling, testing patterns
- **[checklist.md](references/checklist.md)** - Decision tree, implementation phases, configuration checklists, migration patterns
- **[examples.md](references/examples.md)** - Tool templates, pagination, resources, prompts, complete server example, testing examples, refactoring patterns

Start with the reference that matches your task:
- **Building a new server?** → Start with [patterns.md](references/patterns.md)
- **Need an implementation checklist?** → Use [checklist.md](references/checklist.md)
- **Looking for code examples?** → See [examples.md](references/examples.md)

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

## Configuration Files

For teams or deployment, use MCP configuration files to centralize server definitions:

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

## Real-World Examples

### Example 1: FastMCP-based Server (Recommended)

The `src/servers/simple_task/` in the reference project demonstrates correct FastMCP implementation:

**Verification Results:**
- ✅ FastMCP instance at module level and discoverable
- ✅ Server name: `simple-task-server`
- ✅ Entry point configured correctly with `__main__.py`
- ✅ Tools registered with async decorator
- ✅ Module runnable with `python -m src.servers.simple_task`
- ✅ Works with `mcp-inspector "python -m src.servers.simple_task"`
- ✅ Passes all ruff linting checks
- ✅ Comprehensive logging at all levels

### Example 2: Low-Level Server API (Experimental Features)

For servers that require experimental features (like task elicitation/sampling), the low-level `Server` API can be used:

**Reference:** `src/servers/simple_task_interactive/` (Updated to work with current MCP)

**When to use low-level API:**
- Experimental task support (`server.experimental.enable_tasks()`)
- HTTP streaming requirements  
- Custom request/response handling

**Key points for low-level servers:**
- ✅ Use `Any` type hint for context parameters (not `ServerRequestContext`)
- ✅ Register handlers using property assignment: `server.on_list_tools = handler` (not constructor parameters)
- ✅ Still use structured logging with `logger`
- ✅ Prefix unused handler parameters with `_`
- ✅ Include proper docstrings and type hints
- ✅ Implement error handling in nested task functions
- ✅ Support dual-mode transport (stdio + HTTP) when appropriate
- ✅ Pass all ruff linting checks
- ✅ Create proper `__main__.py` entry point

**Example pattern (Updated for current MCP):**
```python
from mcp.server import Server
from typing import Any

async def handle_list_tools(_ctx: Any, _params: Any) -> types.ListToolsResult:
    """List tools - Handler signature receives context and params."""
    logger.debug("Listing tools")
    return types.ListToolsResult(tools=[...])

# Create server without handler parameters
server = Server("my-server")

# Register handlers using property assignment
server.on_list_tools = handle_list_tools
server.on_call_tool = handle_call_tool

# Enable experimental features
server.experimental.enable_tasks()
```

## References

- [Model Context Protocol](https://modelcontextprotocol.io)
- [FastMCP Documentation](https://github.com/jlopp/fastmcp)
- [Click Documentation](https://click.palletsprojects.com)
- [Pydantic Documentation](https://docs.pydantic.dev)
