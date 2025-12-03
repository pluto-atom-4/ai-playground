# MCP Server - Quick Reference

## Installation & Setup

```bash
# Clone/navigate to project
cd py-mcp

# Install with dependencies
pip install -e .

# Install with dev tools (for testing & linting)
pip install -e ".[dev]"
```

## Running the Server

```bash
# Simple run
python -m src

# The server will listen on stdin/stdout using the MCP stdio protocol
```

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html
```

## Code Quality

```bash
# Format code
ruff format src tests

# Lint code
ruff check src tests

# Type check
pyright
```

## Project Files

| File | Purpose |
|------|---------|
| `src/server.py` | Main MCPServer implementation |
| `src/__main__.py` | Server entry point |
| `src/__init__.py` | Package exports |
| `tests/test_server.py` | Test suite |
| `pyproject.toml` | Project configuration & dependencies |

## Available Tools

The server exposes these tools:

### 1. echo_string
- **Input**: `message` (string)
- **Output**: Echo message
- **Usage**: Echo any string value

### 2. add_numbers
- **Input**: `a` (number), `b` (number)
- **Output**: Sum of a + b
- **Usage**: Add two numbers

### 3. get_string_length
- **Input**: `text` (string)
- **Output**: Length of the string
- **Usage**: Count characters in a string

## Adding New Tools

### Step 1: Create Handler
```python
# In src/server.py, add to MCPServer class:
async def _handle_my_tool(self, param: str) -> ToolResult:
    """Handle the my_tool tool call."""
    result = f"Processing: {param}"
    return ToolResult(
        content=[TextContent(type="text", text=result)],
        isError=False,
    )
```

### Step 2: Register Tool
```python
# In _setup_tools() method:
self.server.register_tool(
    Tool(
        name="my_tool",
        description="Description of what this tool does",
        inputSchema={
            "type": "object",
            "properties": {
                "param": {
                    "type": "string",
                    "description": "Parameter description"
                }
            },
            "required": ["param"],
        },
    ),
    self._handle_my_tool,
)
```

### Step 3: Add Tests
```python
# In tests/test_server.py:
@pytest.mark.asyncio
async def test_my_tool_handler(self, server: MCPServer) -> None:
    """Test the my_tool tool handler."""
    result = await server._handle_my_tool("test")
    assert not result.isError
    assert "Processing: test" in result.content[0].text
```

## Debugging

### Enable verbose logging
```python
# In src/server.py:
logging.basicConfig(level=logging.DEBUG)  # Change from INFO to DEBUG
```

### Check tool registration
```python
# After creating MCPServer instance:
server = MCPServer()
mcp_server = server.get_server()
# Tools are registered and ready to use
```

## Architecture Overview

```
Client (e.g., Claude) 
    ↓ (stdin/stdout)
MCP Protocol (stdio transport)
    ↓
src/__main__.py (entry point)
    ↓
MCPServer class (src/server.py)
    ├─ Tool: echo_string
    ├─ Tool: add_numbers
    └─ Tool: get_string_length
```

## Key Classes & Methods

### MCPServer
- `__init__()` - Initialize server and tools
- `_setup_tools()` - Register all tools
- `_handle_echo_string()` - Echo tool handler
- `_handle_add_numbers()` - Add numbers handler
- `_handle_get_string_length()` - Get length handler
- `get_server()` - Return MCP server instance

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError: mcp" | Run `pip install -e ".[dev]"` |
| Tests fail with asyncio error | Make sure pytest-asyncio is installed |
| Type checking fails | Run `pyright` - check python version compatibility |
| Tools not appearing | Verify `_setup_tools()` is called in `__init__` |

## References

- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **MCP Website**: https://modelcontextprotocol.io/

---

For detailed information, see:
- `MCP_SERVER_GUIDE.md` - Comprehensive guide
- `IMPLEMENTATION_SUMMARY.md` - Feature overview
- `IMPLEMENTATION_CHECKLIST.md` - Verification list

