"""
MCP Server Implementation - Quick Start Guide
"""

# MCP Server - Python Model Context Protocol

This is a simple implementation of a Model Context Protocol (MCP) server following
the [Python SDK quickstart](https://github.com/modelcontextprotocol/python-sdk#quickstart).

## Overview

This server exposes three example tools that demonstrate the MCP protocol:

- **echo_string**: Echoes a string message back to the caller
- **add_numbers**: Adds two numbers together
- **get_string_length**: Returns the length of a string

## Project Structure

```
src/
├── __init__.py      # Package initialization and exports
├── __main__.py      # Entry point for running the server
└── server.py        # Main MCPServer implementation
tests/
└── test_server.py   # Unit tests for the server
```

## Installation

1. **Install dependencies**:

```bash
pip install -e .
```

Or for development with test dependencies:

```bash
pip install -e ".[dev]"
```

2. **Verify installation**:

```bash
python -m pip list | grep mcp
```

## Running the Server

### Option 1: Using Python Module

```bash
python -m src
```

### Option 2: Using Python directly

```bash
python -c "from src import MCPServer; import asyncio; asyncio.run(MCPServer().main())"
```

The server will start and listen on stdin/stdout using the stdio transport.

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src --cov-report=html
```

## Development

### Code Quality

The project uses several tools for code quality:

- **ruff**: Linting and formatting (configured in `pyproject.toml`)
- **pyright**: Static type checking
- **pytest**: Testing framework
- **pre-commit**: Git hooks

Run linting:

```bash
ruff check src tests
```

Format code:

```bash
ruff format src tests
```

Run type checking:

```bash
pyright
```

### Adding New Tools

To add a new tool to the server:

1. Create a handler method in `MCPServer` class:

```python
async def _handle_my_tool(self, param1: str) -> ToolResult:
    """Handle the my_tool tool call."""
    # Tool implementation
    return ToolResult(
        content=[TextContent(type="text", text=f"Result: {param1}")],
        isError=False,
    )
```

2. Register the tool in `_setup_tools()`:

```python
self.server.register_tool(
    Tool(
        name="my_tool",
        description="Description of my tool",
        inputSchema={
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Description of param1",
                }
            },
            "required": ["param1"],
        },
    ),
    self._handle_my_tool,
)
```

3. Add tests in `tests/test_server.py`

## Protocol Details

### Supported Transports

Currently, the server uses **stdio transport** for communication, which is the
standard for MCP servers. This allows the server to:

- Read requests from stdin
- Write responses to stdout
- Be easily integrated with other applications

### Tool Schema

Each tool exposes a JSON Schema describing its inputs. This allows clients to:

- Discover available tools
- Validate inputs before calling tools
- Generate appropriate user interfaces

## References

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)

