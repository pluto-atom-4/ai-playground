# MCP Echo Server Clients

This directory contains client scripts for interacting with and testing the MCP Echo Server via HTTP.

## Available Clients

### http_client.py

A comprehensive HTTP client for interacting with the MCP Echo Server running on `http://127.0.0.1:8000`.

#### Features

- ✅ **Real HTTP Requests** - Submits actual requests to the server (not mock responses)
- ✅ **Dual HTTP Library Support** - Use `requests` (default) or `httpx`
- ✅ **Full REST API Integration** - Tools, resources, and prompts operations
- ✅ **Server Information** - Get server status and capabilities
- ✅ **Tool Discovery** - List and call available tools
- ✅ **Resource Management** - List and retrieve resources
- ✅ **Prompt Support** - List and call prompts
- ✅ **Test Scenarios** - Basic (3 tests) and comprehensive (12 tests)
- ✅ **Special Character Support** - Unicode, emoji, and special characters
- ✅ **Error Handling** - Graceful connection and timeout error handling
- ✅ **Configuration Options** - Custom server URL, timeout, and HTTP library
- ✅ **Curl Examples** - Reference commands for manual testing

#### Installation

1. Install dependencies:
```bash
pip install -e .
```

2. Verify installation:
```bash
python -c "from clients.http_client import MCPEchoServerClient; print('✅ OK')"
```

#### Quick Start

##### 1. Start the Server (Terminal 1)

```bash
python src/echo.py
# Output: Starting Echo MCP server with HTTP API on http://127.0.0.1:8000
```

##### 2. Test the Client (Terminal 2)

```bash
# Get server info
python clients/http_client.py --info

# List available tools
python clients/http_client.py --list-tools

# Call echo tool
python clients/http_client.py --tool echo --message "Hello World"

# Run comprehensive tests
python clients/http_client.py --scenario comprehensive
```

#### Usage Examples

##### Server Operations

```bash
# Get server information
python clients/http_client.py --info

# Show curl command examples
python clients/http_client.py --curl-examples
```

##### Tool Operations

```bash
# List available tools
python clients/http_client.py --list-tools

# Call echo tool with requests library (default)
python clients/http_client.py --tool echo --message "Hello, World!"

# Call echo tool with httpx library
python clients/http_client.py --client httpx --tool echo --message "Hello, World!"

# Echo with special characters
python clients/http_client.py --tool echo --message "Special: @#$%^&*()"

# Echo with unicode
python clients/http_client.py --tool echo --message "Unicode: 你好🎉"
```

##### Resource Operations

```bash
# List available resources
python clients/http_client.py --list-resources

# Get a specific resource
python clients/http_client.py --resource echo/static

# Get template resource
python clients/http_client.py --resource echo/test_message
```

##### Prompt Operations

```bash
# List available prompts
python clients/http_client.py --list-prompts

# Call a prompt
python clients/http_client.py --prompt Echo --prompt-text "Hello from Prompt"
```

##### Configuration Options

```bash
# Use custom server URL
python clients/http_client.py --server-url http://192.168.1.100:8000 --info

# Use custom timeout (in seconds)
python clients/http_client.py --timeout 30 --tool echo --message "Test"

# Choose HTTP library (requests or httpx)
python clients/http_client.py --client httpx --info
```

##### Test Scenarios

```bash
# Run basic test scenario (3 tests)
python clients/http_client.py --scenario basic

# Run comprehensive test scenario (12 tests)
python clients/http_client.py --scenario comprehensive

# Run comprehensive tests with httpx
python clients/http_client.py --client httpx --scenario comprehensive
```

#### Test Scenarios

##### Basic Scenario (3 tests)

- Test 1: Get server information
- Test 2: List available tools
- Test 3: Call echo tool with simple message

##### Comprehensive Scenario (12 tests)

- Test 1: Get server information
- Test 2: List available tools
- Test 3: Echo simple message
- Test 4: Echo special characters
- Test 5: Echo unicode characters
- Test 6: Echo empty string
- Test 7: Echo long message (500 chars)
- Test 8: List available resources
- Test 9: Get static resource
- Test 10: Get template resource
- Test 11: List available prompts
- Test 12: Call prompt

#### Examples

```bash
# List all tools
python clients/http_client.py --list-tools

# Run basic test scenario
python clients/http_client.py --scenario basic

# Test echo tool
python clients/http_client.py --tool echo --message "Testing HTTP client"

# Test with different HTTP library
python clients/http_client.py --client httpx --tool echo --message "Using httpx"

# Test unicode support
python clients/http_client.py --tool echo --message "你好世界"

# Show curl command examples
python clients/http_client.py --curl-examples
```

## Workflow

### 1. Start the Echo Server (Terminal 1)

```bash
python src/echo.py
# Server starts on http://127.0.0.1:8000
```

### 2. Run Client Tests (Terminal 2)

```bash
# Get server info
python clients/http_client.py --info

# Run basic tests
python clients/http_client.py --scenario basic

# Run comprehensive tests
python clients/http_client.py --scenario comprehensive
```

### 3. Inspect Results

The client will display:
- Request details (tool name, arguments)
- HTTP response in formatted JSON
- Status and result information

## Client Architecture

```
clients/
├── http_client.py          # Main HTTP client (514 lines, real HTTP requests)
└── README.md               # This file
```

The HTTP client uses a REST API to communicate with the server:
- **Base URL**: `http://127.0.0.1:8000` (configurable via `--server-url`)
- **Default Timeout**: 10 seconds (configurable via `--timeout`)
- **HTTP Libraries**: requests (default) or httpx (alternative, via `--client`)

## REST API Reference

### Endpoints

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| GET | `/api/info` | Get server information | ✅ |
| GET | `/api/tools` | List available tools | ✅ |
| POST | `/api/tools/{name}` | Call a tool | ✅ |
| GET | `/api/resources` | List resources | ✅ |
| GET | `/api/resources/{path}` | Get a resource | ✅ |
| GET | `/api/prompts` | List prompts | ✅ |
| POST | `/api/prompts/{name}` | Call a prompt | ✅ |

### Request Format

#### Tool Call

```json
{
  "arguments": {
    "message": "Hello, World!"
  }
}
```

#### Prompt Call

```json
{
  "arguments": {
    "text": "Hello from Prompt"
  }
}
```

### Response Format

#### Success Response (Tool)

```json
{
  "content": [
    {
      "type": "text",
      "text": "Hello, World!"
    }
  ],
  "isError": false
}
```

#### Error Response

```json
{
  "error": "Connection refused",
  "message": "Failed to connect to server at http://127.0.0.1:8000",
  "isError": true
}
```

## Available Tools

### echo

- **Description**: Echo a string back to the caller
- **Arguments**: `message` (str)
- **Endpoint**: `POST /api/tools/echo`
- **Example**: 
  ```bash
  python clients/http_client.py --tool echo --message "Hello, Echo Server!"
  ```
- **Expected Response**: 
  ```json
  {
    "content": [{"type": "text", "text": "Hello, Echo Server!"}],
    "isError": false
  }
  ```

## Testing Edge Cases

The client supports testing various edge cases:

| Case | Example | Usage |
|------|---------|-------|
| Empty string | "" | `--message ""` |
| Special characters | "Hello\nWorld\t!" | `--message "Hello\nWorld\t!"` |
| Unicode | "你好世界" | `--message "你好世界"` |
| Emoji | "Hello 🎉" | `--message "Hello 🎉"` |
| Long string | "a" * 500 | `--message "$(python -c 'print(\"a\" * 500)')"` |

## Command-Line Options

### Server Configuration

```
--server-url URL        Base URL of the MCP server (default: http://127.0.0.1:8000)
--timeout SECONDS       Request timeout in seconds (default: 10.0)
--client {requests,httpx}  HTTP client library to use (default: requests)
```

### Operations

```
--info                  Get server information and health status
--list-tools           List all available tools on the server
--list-resources       List all available resources on the server
--list-prompts         List all available prompts on the server
--tool NAME            Specific tool to call
--message TEXT         Message for echo tool
--resource PATH        Resource path to retrieve
--prompt NAME          Prompt name to call
--prompt-text TEXT     Text argument for prompt
--scenario {basic,comprehensive}  Run predefined test scenario (default: basic)
--curl-examples        Show curl command examples
```

## Troubleshooting

### "Connection refused" error

**Problem**: `Failed to connect to server at http://127.0.0.1:8000`

**Solution**: Ensure the server is running:
```bash
python src/echo.py
```

### "Module not found" error

**Problem**: `ModuleNotFoundError: No module named 'requests'`

**Solution**: Install dependencies:
```bash
pip install -e .
```

### "Missing argument" error

**Problem**: `Error: --message is required for echo tool`

**Solution**: Provide required arguments:
```bash
python clients/http_client.py --tool echo --message "Hello"
```

### Timeout error

**Problem**: Request times out after 10 seconds

**Solution**: Increase timeout:
```bash
python clients/http_client.py --timeout 30 --tool echo --message "Test"
```

## Best Practices

1. **Server First**: Always start the server before running client tests
2. **Check Tools**: Use `--list-tools` to see available tools
3. **Test Scenarios**: Start with `--scenario basic` for quick validation
4. **Edge Cases**: Use `--scenario comprehensive` for thorough testing
5. **Debugging**: Use `--curl-examples` to understand the request format
6. **Performance**: Use `--client httpx` for async capabilities
7. **Configuration**: Use `--server-url` and `--timeout` for custom environments

## Development

To extend the client:

1. Add new API methods to `MCPEchoServerClient` class
2. Use `_make_request()` for HTTP communication
3. Add test cases to `_test_basic()` or `_test_comprehensive()` methods
4. Update documentation in this README

### Adding a New Operation

```python
def my_operation(self) -> Dict[str, Any]:
    """Description of operation"""
    print(f"📤 Performing operation")
    return self._make_request("GET", "/api/my-endpoint")
```

## See Also

- `../src/echo.py` - Echo server implementation (FastAPI + FastMCP)
- `../tests/` - Pytest test suite
- `../generated/docs-copilot/` - Additional documentation guides
  - `HTTP_CLIENT_GUIDE.md` - Complete usage guide
  - `HTTP_CLIENT_QUICK_START.md` - Quick start reference
  - `HTTP_CLIENT_EXAMPLE_OUTPUTS.md` - Example outputs from commands
