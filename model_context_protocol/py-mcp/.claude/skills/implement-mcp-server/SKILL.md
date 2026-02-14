---
name: implement-mcp-server
description: Build high-quality MCP (Model Context Protocol) servers using FastMCP with Python. Use when creating MCP servers to integrate external APIs or services, implementing tools, resources, or prompts, setting up logging and error handling, or refactoring existing servers to follow modern best practices. Provides patterns for architecture, Pydantic validation, pagination, and deployment via stdio transport.
---

# MCP Server Implementation Skill

This skill guides the implementation of Model Context Protocol (MCP) servers following modern Python best practices using FastMCP, focusing on code organization, logging, authentication, and transport handling.

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

### Don'ts
- ❌ **Don't create `FastMCP` instance inside `main()`** (won't be discoverable)
- ❌ **Don't use `mcp dev` for testing** (has Windows path parsing bugs)
- ❌ Don't use the low-level `Server` class (use FastMCP only)
- ❌ Don't use `if __name__ == "__main__": main()` in server module (use `__main__.py`)
- ❌ Don't add `--port` option to server (unless running HTTP separately)
- ❌ Don't raise exceptions for invalid cursors (handle gracefully)
- ❌ Don't expose stack traces in responses
- ❌ Don't use raw dicts (use Pydantic models)
- ❌ Don't try to invoke with `#file:` syntax or file paths
- ❌ Don't forget to include `__init__.py` in server directory
- ❌ Don't run mcp-inspector from subdirectories (run from project root)

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

## Real-World Example

The `src/servers/simple_task/` in the reference project demonstrates correct implementation:

**Verification Results:**
- ✅ FastMCP instance at module level and discoverable
- ✅ Server name: `simple-task-server`
- ✅ Entry point configured correctly with `__main__.py`
- ✅ Tools registered with async decorator
- ✅ Module runnable with `python -m src.servers.simple_task`
- ✅ Works with `mcp-inspector "python -m src.servers.simple_task"`

## References

- [Model Context Protocol](https://modelcontextprotocol.io)
- [FastMCP Documentation](https://github.com/jlopp/fastmcp)
- [Click Documentation](https://click.palletsprojects.com)
- [Pydantic Documentation](https://docs.pydantic.dev)
