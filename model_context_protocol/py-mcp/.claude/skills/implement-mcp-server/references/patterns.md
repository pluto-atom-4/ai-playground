# Implementation Patterns - MCP Server Development

This document contains detailed patterns and design approaches for MCP server development.

## Table of Contents

1. [Server Architecture](#server-architecture)
2. [Pydantic Model Design](#pydantic-model-design)
3. [Pagination Implementation](#pagination-implementation)
4. [Resource and Prompt Support](#resource-and-prompt-support)
5. [Transport Configuration](#transport-configuration)
6. [Error Handling](#error-handling)
7. [Testing Patterns](#testing-patterns)

## Server Architecture Pattern

### FastMCP Server with Logging

```python
import logging
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("server-name")

# Create FastMCP server instance
mcp = FastMCP("server-name")
```

### Handler Extraction and Tool Registration

**Original Pattern (Avoid):**
- Handler functions in separate functions with `@app.list_tools()`, `@app.call_tool()` decorators
- Tools defined as async functions with context parameters
- Complex router logic in main()

**New Pattern (Follow):**
- Tools decorated with `@mcp.tool(name="...", description="...")`
- Input/output validated using Pydantic models
- Async-first implementation
- Clean separation of concerns

## Pydantic Model Design

### Input Model Pattern

```python
from pydantic import BaseModel
from typing import List, Optional, Dict

class ToolInput(BaseModel):
    """Input parameters for a tool"""
    param1: str
    param2: Optional[int] = None
    param3: Dict[str, str] = {}

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "param1": "example value",
                "param2": 42,
                "param3": {"key": "value"}
            }
        }
```

### Output Model Pattern

```python
class ToolOutput(BaseModel):
    """Output structure for a tool"""
    result: str
    status: str = "success"
    metadata: Optional[Dict] = None

@mcp.tool(name="my_tool", description="Tool description")
async def my_tool(input_data: ToolInput) -> ToolOutput:
    """Implementation"""
    return ToolOutput(result="...", status="success")
```

### Model Hierarchy for Complex Types

For list operations with items:

```python
class Item(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

class ListOutput(BaseModel):
    items: List[Item]
    nextCursor: Optional[str] = None
    totalCount: Optional[int] = None
```

## Pagination Implementation

### Cursor-Based Pagination Pattern

**Pagination Cursor Format:**
- Use string-based cursor format (not offset-based)
- Include cursor in request parameters
- Log warnings for invalid cursors (DO NOT raise exceptions)
- Return cursor in response for next page

```python
from typing import Optional
from pydantic import BaseModel

class ListInput(BaseModel):
    """List request with pagination"""
    cursor: Optional[str] = None
    limit: int = 10

class ListOutput(BaseModel):
    """List response with pagination"""
    items: List[dict]
    nextCursor: Optional[str] = None

@mcp.tool(name="list_items", description="List items with pagination")
async def list_items(input_data: ListInput) -> ListOutput:
    """List items with pagination support"""

    # Validate cursor
    offset = 0
    if input_data.cursor is not None:
        try:
            # Parse cursor
            offset = int(input_data.cursor)
        except (ValueError, TypeError):
            logger.warning(f"Invalid cursor format: {input_data.cursor}")
            offset = 0

    # Get items
    items = get_paginated_items(offset, input_data.limit)

    # Create next cursor if more items exist
    next_cursor = str(offset + input_data.limit) if has_more_items(offset + input_data.limit) else None

    return ListOutput(items=items, nextCursor=next_cursor)
```

### Pagination Best Practices

1. **Cursor Format:** String-based, opaque to client (implementation detail)
2. **Validation:** Log warnings (not errors) for invalid cursors
3. **Default:** Always fallback to offset 0 if parsing fails
4. **Response:** Include both items and nextCursor (None when no more pages)

## Resource and Prompt Support

### Resource Handler Pattern

```python
from mcp.types import TextContent, Resource

@mcp.resource(uri_pattern="resource://*")
def read_resource(uri: str) -> str:
    """Read a resource by URI"""
    logger.debug(f"Reading resource: {uri}")

    try:
        # Validate URI
        if not uri.startswith("resource://"):
            logger.warning(f"Invalid URI format: {uri}")
            return "Invalid URI format"

        # Extract path and read
        path = uri.replace("resource://", "")
        with open(path, 'r') as f:
            content = f.read()

        logger.info(f"Successfully read: {uri}")
        return content

    except FileNotFoundError:
        logger.error(f"Resource not found: {uri}")
        return f"Resource not found"
    except Exception as e:
        logger.error(f"Error reading {uri}: {e}", exc_info=True)
        return f"Error: {str(e)}"
```

### Prompt Handler Pattern

```python
from mcp.types import PromptMessage, TextContent
from typing import List, Optional

def build_prompt(topic: Optional[str] = None) -> List[PromptMessage]:
    """Build prompt messages"""
    messages = [
        PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text="You are a helpful assistant."
            )
        )
    ]

    if topic:
        messages.append(
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"Focus on: {topic}"
                )
            )
        )

    return messages

@mcp.tool(name="get_prompt", description="Get a prompt template")
async def get_prompt(name: str, topic: Optional[str] = None) -> dict:
    """Get prompt by name"""
    logger.debug(f"Getting prompt: {name}")

    if name == "assistant":
        return {"messages": build_prompt(topic)}
    else:
        logger.warning(f"Unknown prompt: {name}")
        return {"messages": []}
```

## Transport Configuration

### Stdio Transport (Recommended)

```python
# Only configure stdio - omit port configuration
# The server.run() handles stdio transport automatically
mcp.run()
```

**Advantages:**
- Single transport mechanism
- No port configuration needed
- Automatic by `mcp.run()`
- Best for CLI and direct integration

### HTTP Transport (When Needed)

When you need HTTP endpoints, use `StreamableHTTPSessionManager` with Starlette:

```python
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount

app = FastAPI()
mcp = FastMCP("my-server")

# Mount MCP at /mcp path
app.mount("/mcp", Mount(app=mcp.app))

# Configure host and port
if __name__ == "__main__":
    import uvicorn
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
```

## Error Handling

### Pattern: Graceful Error Handling

```python
@mcp.tool(name="process", description="Process data")
async def process(input_data: ToolInput) -> ToolOutput:
    try:
        # Validate input
        if not input_data.value:
            logger.warning(f"Empty input provided")
            return ToolOutput(
                result="No input provided",
                status="error"
            )

        # Process
        result = perform_processing(input_data)
        logger.info(f"Processing completed successfully")
        return ToolOutput(result=result, status="success")

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return ToolOutput(
            result=f"Invalid input: {str(e)}",
            status="error"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return ToolOutput(
            result="Internal server error",
            status="error"
        )
```

### Best Practices

1. **Specific Exceptions First:** Catch specific exceptions before generic `Exception`
2. **User-Friendly Messages:** Return messages clients understand
3. **Never Expose Stacks:** Log full details with `exc_info=True`, return summary
4. **Validate at Boundaries:** Check input at entry point
5. **Don't Raise:** Return error status in output, don't raise exceptions

## Testing Patterns

### Using FastMCP Inspector

```bash
# Install inspector
npm install -g @modelcontextprotocol/inspector

# Terminal 1: Run server
python -m src.servers.my_server

# Terminal 2: Run inspector
mcp-inspector
```

### Unit Testing Pattern

```python
import pytest
from src.servers.my_server.my_server import my_tool, ToolInput, ToolOutput

@pytest.mark.asyncio
async def test_tool_basic():
    """Test tool with valid input"""
    input_data = ToolInput(param1="test", param2=5)
    output = await my_tool(input_data)
    assert isinstance(output, ToolOutput)
    assert output.status == "success"

@pytest.mark.asyncio
async def test_tool_error_handling():
    """Test tool error handling"""
    input_data = ToolInput(param1="", param2=-1)
    output = await my_tool(input_data)
    assert output.status == "error"
```

### Pagination Testing Pattern

```python
@pytest.mark.asyncio
async def test_pagination_valid_cursor():
    """Test pagination with valid cursor"""
    input1 = ListInput(cursor="0", limit=5)
    output1 = await list_items(input1)
    assert len(output1.items) > 0

    if output1.nextCursor:
        input2 = ListInput(cursor=output1.nextCursor, limit=5)
        output2 = await list_items(input2)
        # Verify we got different items
        assert output1.items[0]["id"] != output2.items[0]["id"]

@pytest.mark.asyncio
async def test_pagination_invalid_cursor():
    """Test pagination handles invalid cursor gracefully"""
    input_data = ListInput(cursor="invalid-cursor", limit=5)
    output = await list_items(input_data)
    # Should not raise, should use offset 0
    assert output.items is not None
```

## Common Issues and Solutions

### Issue: "No such option: --port"
**Solution:** Remove `--port` option from click command and use environment variables instead.

### Issue: Multiple handler decorators cause conflicts
**Solution:** Use `@mcp.tool` decorator exclusively, not `@app.call_tool()` + separate handlers.

### Issue: Pagination cursor validation fails
**Solution:** Log warning (not error) for invalid cursors and fallback to offset 0.

### Issue: Logging not appearing
**Solution:** Configure logging before creating FastMCP instance and load environment variables first.

### Issue: Resource handler not found
**Solution:** Ensure URI pattern matches exactly and return proper TextContent objects.

### Issue: Server won't start with mcp.run()
**Solution:** Check stdin/stdout are available, verify no syntax errors, ensure all decorators are applied correctly.
