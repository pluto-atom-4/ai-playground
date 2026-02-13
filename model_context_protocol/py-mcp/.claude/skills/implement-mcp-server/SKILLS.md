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

Create `__main__.py`:

```python
"""MCP Server entry point"""
from src.servers.my_server.my_server import main

if __name__ == "__main__":
    exit(main())
```

## Logging

Configure at startup with appropriate levels:

- **DEBUG:** Tool invocation details, parameters
- **INFO:** Server startup, successful operations
- **WARNING:** Invalid input, recoverable issues
- **ERROR:** Exceptions (with `exc_info=True`)

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
- Use `@mcp.tool` decorator for tools
- Define Pydantic models for inputs/outputs
- Log at appropriate levels
- Handle errors gracefully
- Use `__main__.py` entry point
- Use cursor-based pagination

### Don'ts
- Don't use `if __name__ == "__main__": main()` in server
- Don't add `--port` option (unless HTTP needed)
- Don't raise exceptions for invalid cursors
- Don't expose stack traces in responses
- Don't use raw dicts (use Pydantic models)

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

```bash
# Terminal 1: Run server
python -m src.servers.my_server --log-level DEBUG

# Terminal 2: Run inspector
mcp-inspector
```

## References

- [Model Context Protocol](https://modelcontextprotocol.io)
- [FastMCP](https://github.com/jlopp/fastmcp)
- [Click](https://click.palletsprojects.com)
- [Pydantic](https://docs.pydantic.dev)
