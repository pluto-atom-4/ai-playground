# Simple Tool MCP Server

A lightweight MCP (Model Context Protocol) server implementation that demonstrates website content fetching.

## Features

- **Website Fetcher Tool**: Fetches and returns the content of websites via HTTP(S)
- **FastMCP Implementation**: Uses the FastMCP decorator-based server framework
- **Comprehensive Error Handling**: Validates URLs and provides user-friendly error messages
- **Logging Support**: Configurable logging levels for debugging
- **Environment Configuration**: Supports `.env` file for configuration

## Installation

Ensure dependencies are installed:

```bash
# Using pip
pip install -e .

# Or using uv
uv pip install -e .
```

## Usage

### Start the Server

```bash
# Run with default INFO log level
python src/servers/simple_tool/simple_tool_mcp_server.py

# Run with DEBUG logging
python src/servers/simple_tool/simple_tool_mcp_server.py --log-level DEBUG

# Show help
python src/servers/simple_tool/simple_tool_mcp_server.py --help
```

### Tools

#### fetch

Fetches a website and returns its content.

**Parameters:**
- `url` (string, required): The URL to fetch (must start with http:// or https://)

**Returns:**
- Content block with the website HTML/text
- Error indication flag

**Example:**

```python
# Using via MCP client
result = await client.call_tool("fetch", {"url": "https://example.com"})
```

## Environment Configuration

Create a `.env` file in the project root:

```bash
# Logging level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO
```

## Architecture

### FastMCP Server Pattern

This server uses the **FastMCP** framework which provides:

1. **Decorator-based tool registration**: Simple `@mcp.tool` decorators
2. **Automatic protocol handling**: Manages MCP protocol details
3. **Built-in stdio transport**: Default stdio-based communication
4. **Structured logging**: INFO-level logging for monitoring

### Tool Implementation

The `fetch_website` tool:
- Validates URL format (must have http/https prefix)
- Imports httpx for HTTP requests
- Includes proper error handling with descriptive messages
- Logs all operations for debugging
- Returns TextContent in MCP-compatible format

## Testing

To test the server with the MCP Inspector:

```bash
# Terminal 1: Start the MCP server
python src/servers/simple_tool/simple_tool_mcp_server.py

# Terminal 2: Run the MCP Inspector
mcp-inspector

# Then use the web UI to test the tools
```

## Error Handling

The server provides descriptive error messages for:

- **Empty URL**: "URL cannot be empty"
- **Invalid URL format**: "Invalid URL: {url} (must start with http:// or https://)"
- **Network errors**: "Failed to fetch {url}: {error details}"
- **Missing httpx**: "httpx library not installed"

## Logging

Logs include:
- Server startup/shutdown events
- Configuration loaded messages
- Tool invocations with URLs
- Success/failure indicators with data sizes
- Error traces for debugging

Example log output:

```
2025-01-21 10:30:45 [INFO] simple-tool.server: Starting Simple Tool MCP Server
2025-01-21 10:30:45 [INFO] simple-tool.server: Fetching website from URL: https://example.com
2025-01-21 10:30:46 [INFO] simple-tool.server: Successfully fetched 1234 bytes from https://example.com
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/servers/simple_tool/

# Run specific test
pytest tests/test_simple_tool_mcp.py -v
```

### Code Structure

```
src/servers/simple_tool/
├── __init__.py                      # Package initialization
├── simple_tool_mcp_server.py        # Main server implementation
└── README.md                        # This file
```

## References

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/modelcontextprotocol/python-sdk)
- [Official Example](https://github.com/modelcontextprotocol/python-sdk/tree/main/examples/servers/simple-tool)

## License

MIT
