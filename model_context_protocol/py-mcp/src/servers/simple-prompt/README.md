# Simple Prompt MCP Server

A lightweight MCP (Model Context Protocol) server implementation that demonstrates prompt listing and retrieval tools.

## Features

- **Prompt Listing Tool**: Lists available prompts with metadata and argument schemas
- **Prompt Retrieval Tool**: Returns prompt messages and descriptions by name and arguments
- **FastMCP Implementation**: Uses the FastMCP decorator-based server framework
- **Comprehensive Error Handling**: Validates prompt names and provides user-friendly error messages
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
python src/servers/simple-prompt/simple_prompt_server.py

# Run with DEBUG logging
python src/servers/simple-prompt/simple_prompt_server.py --log-level DEBUG

# Show help
python src/servers/simple-prompt/simple_prompt_server.py --help
```

### Tools

#### list_prompts

Lists available prompts with their metadata and argument schemas.

**Returns:**
- List of prompt objects (name, title, description, arguments)

**Example:**

```python
# Using via MCP client
result = await client.call_tool("list_prompts")
```

#### get_prompt

Retrieves a prompt by name and optional arguments (context, topic).

**Parameters:**
- `name` (string, required): The prompt name (e.g., "simple")
- `arguments` (dict, optional): Arguments for the prompt (e.g., context, topic)

**Returns:**
- List of prompt messages
- Description of the prompt

**Example:**

```python
# Using via MCP client
result = await client.call_tool("get_prompt", {"name": "simple", "arguments": {"context": "project info", "topic": "usage"}})
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

- The `list_prompts` tool returns a list of available prompts, each with metadata and argument schemas.
- The `get_prompt` tool validates the prompt name and returns prompt messages and a description, supporting optional arguments (context, topic).
- Both tools use Pydantic models for input/output validation and error handling.

## Testing

To test the server with the MCP Inspector:

```bash
# Terminal 1: Start the MCP server
python src/servers/simple-prompt/simple_prompt_server.py

# Terminal 2: Run the MCP Inspector
mcp-inspector

# Then use the web UI to test the tools
```

## Error Handling

The server provides descriptive error messages for:

- **Unknown prompt name**: "Unknown prompt: {name}"
- **Missing required arguments**: Validation errors from Pydantic

## Logging

Logs include:
- Server startup/shutdown events
- Configuration loaded messages
- Tool invocations with arguments
- Success/failure indicators
- Error traces for debugging

Example log output:

```
2026-02-01 10:30:45 [INFO] simple-prompt.server: Starting Simple Prompt MCP Server
2026-02-01 10:30:45 [INFO] simple-prompt.server: Listing prompts
2026-02-01 10:30:46 [INFO] simple-prompt.server: Returning prompt 'simple' with arguments: {"context": "project info", "topic": "usage"}
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/servers/simple-prompt/

# Run specific test
pytest tests/test_simple_prompt_mcp.py -v
```

### Code Structure

```
src/servers/simple-prompt/
├── __init__.py                      # Package initialization
├── simple_prompt_server.py           # Main server implementation
└── README.md                         # This file
```

## References

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/modelcontextprotocol/python-sdk)
- [Official Example](https://github.com/modelcontextprotocol/python-sdk/tree/main/examples/servers/simple-prompt)

## License

MIT
