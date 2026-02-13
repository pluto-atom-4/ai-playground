# MCP Server Implementation - Code Examples

## Quick Reference: Tool Implementation Templates

### Basic Tool Template

```python
from pydantic import BaseModel
from typing import Optional

class MyToolInput(BaseModel):
    """Input validation model"""
    param1: str
    param2: Optional[int] = None

class MyToolOutput(BaseModel):
    """Output structure"""
    result: str
    status: str = "success"

@mcp.tool(name="my_tool", description="Does something useful")
async def my_tool(input_data: MyToolInput) -> MyToolOutput:
    """
    Tool implementation.
    
    Args:
        input_data: Input parameters
        
    Returns:
        MyToolOutput with result
    """
    logger.debug(f"Tool invoked with param1={input_data.param1}")
    
    try:
        # Process input
        result = process(input_data.param1, input_data.param2)
        logger.info("Tool execution successful")
        return MyToolOutput(result=result, status="success")
    except Exception as e:
        logger.error(f"Tool execution failed: {e}", exc_info=True)
        return MyToolOutput(result=str(e), status="error")
```

### Paginated List Tool

```python
from typing import List, Optional

class ListItemsInput(BaseModel):
    cursor: Optional[str] = None
    limit: int = 10

class Item(BaseModel):
    id: str
    name: str
    description: str

class ListItemsOutput(BaseModel):
    items: List[Item]
    nextCursor: Optional[str] = None
    totalCount: Optional[int] = None

@mcp.tool(name="list_items", description="List items with pagination")
async def list_items(input_data: ListItemsInput) -> ListItemsOutput:
    logger.debug(f"Listing items with cursor={input_data.cursor}, limit={input_data.limit}")
    
    # Parse cursor
    offset = 0
    if input_data.cursor:
        try:
            offset = int(input_data.cursor)
        except (ValueError, TypeError):
            logger.warning(f"Invalid cursor format: {input_data.cursor}, using offset 0")
            offset = 0
    
    # Fetch items
    all_items = get_all_items()
    items = all_items[offset:offset + input_data.limit]
    
    # Generate next cursor
    next_offset = offset + input_data.limit
    next_cursor = str(next_offset) if next_offset < len(all_items) else None
    
    logger.info(f"Returning {len(items)} items")
    
    return ListItemsOutput(
        items=[Item(**item) for item in items],
        nextCursor=next_cursor,
        totalCount=len(all_items)
    )
```

### Resource Handler

```python
from mcp.types import Resource, TextContent

class ReadResourceInput(BaseModel):
    uri: str

@mcp.resource(uri_pattern="file://*")
def read_resource(uri: str) -> str:
    """Read resource by URI"""
    logger.debug(f"Reading resource: {uri}")
    
    try:
        # Validate URI format
        if not uri.startswith("file://"):
            logger.warning(f"Invalid URI format: {uri}")
            return "Invalid URI format"
        
        # Extract path
        path = uri.replace("file://", "")
        
        # Read file
        with open(path, 'r') as f:
            content = f.read()
        
        logger.info(f"Successfully read resource: {uri}")
        return content
        
    except FileNotFoundError:
        logger.error(f"Resource not found: {uri}")
        return f"Resource not found: {uri}"
    except Exception as e:
        logger.error(f"Error reading resource {uri}: {e}", exc_info=True)
        return f"Error reading resource: {str(e)}"
```

### Prompt Handler

```python
from mcp.types import PromptMessage, TextContent, PromptArgument, Prompt
from typing import Optional, Dict

class GetPromptInput(BaseModel):
    name: str
    arguments: Optional[Dict[str, str]] = None

class GetPromptOutput(BaseModel):
    messages: List[PromptMessage]
    description: str

def create_system_prompt(topic: Optional[str] = None) -> list[PromptMessage]:
    """Create system prompt messages"""
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
                    text=f"Focus on the topic: {topic}"
                )
            )
        )
    
    return messages

@mcp.tool(name="get_prompt", description="Get a prompt template")
async def get_prompt(input_data: GetPromptInput) -> GetPromptOutput:
    logger.debug(f"Getting prompt: {input_data.name}")
    
    if input_data.name == "assistant":
        arguments = input_data.arguments or {}
        messages = create_system_prompt(arguments.get("topic"))
        return GetPromptOutput(
            messages=messages,
            description="General assistant prompt"
        )
    else:
        logger.warning(f"Unknown prompt requested: {input_data.name}")
        return GetPromptOutput(
            messages=[],
            description="Unknown prompt"
        )
```

## Complete Server Template

```python
"""
MCP Server Template - Copy and adapt for new servers.
"""

import logging
import os
from typing import List, Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, PromptMessage
from pydantic import BaseModel

# Load environment variables
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


# ============================================================================
# Input/Output Models
# ============================================================================

class MyToolInput(BaseModel):
    """Input for my_tool"""
    query: str
    max_results: Optional[int] = 10


class MyToolOutput(BaseModel):
    """Output from my_tool"""
    results: List[dict]
    total: int


# ============================================================================
# Tool Implementations
# ============================================================================

@mcp.tool(name="search", description="Search for items")
async def search(input_data: MyToolInput) -> MyToolOutput:
    """Search implementation"""
    logger.debug(f"Search invoked with query: {input_data.query}")
    
    try:
        # Implementation
        results = []
        
        logger.info(f"Search completed with {len(results)} results")
        return MyToolOutput(results=results, total=len(results))
        
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        return MyToolOutput(results=[], total=0)


# ============================================================================
# Resource Handlers
# ============================================================================

@mcp.resource(uri_pattern="resource://*")
def read_resource(uri: str) -> str:
    """Read a resource"""
    logger.debug(f"Reading resource: {uri}")
    try:
        # Implementation
        return "resource content"
    except Exception as e:
        logger.error(f"Error reading resource: {e}", exc_info=True)
        return str(e)


# ============================================================================
# Prompt Handlers
# ============================================================================

@mcp.tool(name="get_prompt", description="Get a prompt")
async def get_prompt(name: str) -> dict:
    """Get prompt by name"""
    logger.debug(f"Getting prompt: {name}")
    
    prompts = {
        "default": [
            PromptMessage(
                role="user",
                content=TextContent(type="text", text="Help me with...")
            )
        ]
    }
    
    if name in prompts:
        logger.info(f"Retrieved prompt: {name}")
        return {"messages": prompts[name]}
    else:
        logger.warning(f"Unknown prompt: {name}")
        return {"messages": []}


# ============================================================================
# CLI Entry Point
# ============================================================================

import click


@click.command()
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Set logging level",
)
def main(log_level: str = "INFO") -> int:
    """Start the MCP server"""
    # Update logging level
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

## __main__.py Template

```python
"""Server entry point"""
from src.servers.my_server.my_server import main

if __name__ == "__main__":
    exit(main())
```

## Environment File (.env)

```
# Logging configuration
LOG_LEVEL=INFO

# Server configuration (if needed)
MCP_HOST=127.0.0.1
MCP_PORT=8000

# Application-specific settings
API_KEY=your-api-key
DATABASE_URL=sqlite:///./test.db
```

## Refactoring Workflow

### Step 1: Extract Imports and Setup
```python
# Before
from mcp.server import Server
app = Server("name")

# After
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("name")
```

### Step 2: Extract Tool Handlers
```python
# Before
@app.call_tool()
async def handle_call(name: str, arguments: dict):
    if name == "search":
        # Complex logic mixed here
        return result

# After
@mcp.tool(name="search", description="Search items")
async def search(input_data: SearchInput) -> SearchOutput:
    # Clean, focused implementation
    return output
```

### Step 3: Add Pydantic Models
```python
# Before
arguments = {"query": "...", "limit": "10"}

# After
class SearchInput(BaseModel):
    query: str
    limit: int = 10

async def search(input_data: SearchInput) -> SearchOutput:
    # Validation happens automatically
    pass
```

### Step 4: Implement Logging
```python
# Before
print("Starting server")

# After
logger = logging.getLogger("my-server")
logger.info("Starting server")
```

### Step 5: Update CLI Entry Point
```python
# Remove
if __name__ == "__main__":
    main()

# Add --log-level option
@click.option("--log-level", ...)
def main(log_level: str = "INFO") -> int:
    logging.getLogger().setLevel(log_level.upper())
    logger.info(f"Set logging level to {log_level.upper()}")
    mcp.run()
    return 0
```

### Step 6: Create __main__.py
```python
from src.servers.my_server.my_server import main
if __name__ == "__main__":
    exit(main())
```

## Testing Examples

### Basic Tool Test
```python
import pytest
from src.servers.my_server.my_server import search, MyToolInput, MyToolOutput

@pytest.mark.asyncio
async def test_search_basic():
    input_data = MyToolInput(query="test", max_results=5)
    output = await search(input_data)
    assert isinstance(output, MyToolOutput)
    assert output.total >= 0
```

### Pagination Test
```python
@pytest.mark.asyncio
async def test_pagination_cursor():
    # Test with valid cursor
    input1 = ListItemsInput(cursor="0", limit=5)
    output1 = await list_items(input1)
    assert len(output1.items) > 0
    
    # Test with next cursor
    if output1.nextCursor:
        input2 = ListItemsInput(cursor=output1.nextCursor, limit=5)
        output2 = await list_items(input2)
        assert output1.items[0].id != output2.items[0].id

@pytest.mark.asyncio
async def test_invalid_cursor():
    # Should not raise, should log warning and use offset 0
    input_data = ListItemsInput(cursor="invalid-cursor", limit=5)
    output = await list_items(input_data)
    assert output.items is not None
```

### Integration Test
```python
@pytest.mark.asyncio
async def test_server_startup():
    """Test server can start without errors"""
    try:
        # mcp.run() starts the server
        # In tests, we validate tool registration instead
        assert len(mcp.tools) > 0
        logger.info("Server validation passed")
    except Exception as e:
        pytest.fail(f"Server failed to validate: {e}")
```

