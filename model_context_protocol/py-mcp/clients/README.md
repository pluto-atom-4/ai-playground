# MCP Echo Server Clients

This directory contains client scripts for interacting with and testing the MCP Echo Server.

## Available Clients

### http_client.py

A comprehensive Python client for inspecting and testing the MCP Echo Server behavior.

#### Features

- ✅ Support for both `demo` and `echo` server types
- ✅ Tool listing and discovery
- ✅ Predefined test scenarios (basic, comprehensive)
- ✅ Individual tool testing
- ✅ Special character and unicode support
- ✅ Response inspection and pretty-printing
- ✅ Curl command examples

#### Usage

##### List available tools

```bash
python clients/http_client.py --list-tools
python clients/http_client.py --server-type echo --list-tools
```

##### Run test scenarios

```bash
# Run basic tests for demo server
python clients/http_client.py --scenario basic

# Run comprehensive tests for demo server
python clients/http_client.py --scenario comprehensive

# Run tests for echo server
python clients/http_client.py --server-type echo --scenario basic
```

##### Test specific tools

```bash
# Test echo_string with demo server
python clients/http_client.py --tool echo_string --message "Hello, World!"

# Test add_numbers
python clients/http_client.py --tool add_numbers --args 5 3

# Test get_string_length
python clients/http_client.py --tool get_string_length --message "hello"

# Test echo tool with echo server
python clients/http_client.py --server-type echo --tool echo --message "Hello, Echo!"
```

##### Show curl examples

```bash
python clients/http_client.py --curl-examples
python clients/http_client.py --server-type echo --curl-examples
```

#### Test Scenarios

##### Demo Server - Basic

- Echo string: "Hello, MCP!"
- Add numbers: 5 + 3
- String length: "MCP Echo Server"

##### Demo Server - Comprehensive

- Echo with empty string
- Echo with special characters (newlines, tabs)
- Add positive numbers
- Add negative numbers
- Add floating-point numbers
- String length with unicode characters
- String length with long string (1000 chars)

##### Echo Server - Basic

- Echo string: "Hello, Echo Server!"
- Echo with special characters: "@#$%^&*()"
- Echo with unicode and emoji: "你好🎉"

#### Examples

```bash
# List all tools for demo server
python clients/http_client.py --list-tools

# Run basic test scenario
python clients/http_client.py --scenario basic

# Test echo_string tool
python clients/http_client.py --tool echo_string --message "Testing echo"

# Test add_numbers tool
python clients/http_client.py --tool add_numbers --args 10 20

# Test string length with unicode
python clients/http_client.py --tool get_string_length --message "你好世界"

# Show curl examples
python clients/http_client.py --curl-examples
```

## Workflow

### 1. Start the Echo Server

```bash
# Terminal 1: Start echo server
./scripts/start-mpc-server.sh echo

# Or start demo server
./scripts/start-mpc-server.sh demo
```

### 2. Run Client Tests

```bash
# Terminal 2: Run tests
python clients/http_client.py --server-type echo --scenario basic
```

### 3. Inspect Results

The client will display:
- Tool call details (arguments passed)
- Response structure (formatted JSON)
- Expected vs actual behavior

## Client Architecture

```
clients/
├── http_client.py          # Main HTTP client for server inspection
├── README.md               # This file
```

## Response Structure

The MCP Echo Server returns responses in the following format:

### Success Response

```json
{
  "tool": "echo_string",
  "args": {
    "message": "Hello, World!"
  },
  "description": "Echo a string back to the caller"
}
```

### Error Response

```json
{
  "isError": true,
  "content": [
    {
      "type": "text",
      "text": "Error message"
    }
  ]
}
```

## Tool Reference

### Demo Server Tools

#### echo_string

- **Description**: Echo a string back to the caller
- **Arguments**: `message` (str)
- **Example**: `echo_string("Hello, World!")`

#### add_numbers

- **Description**: Add two numbers together
- **Arguments**: `a` (float), `b` (float)
- **Example**: `add_numbers(5, 3)`
- **Expected Result**: 8

#### get_string_length

- **Description**: Get the length of a string
- **Arguments**: `input` (str)
- **Example**: `get_string_length("hello")`
- **Expected Result**: 5

### Echo Server Tools

#### echo

- **Description**: Echo a string back to the caller
- **Arguments**: `message` (str)
- **Example**: `echo("Hello, Echo Server!")`

## Testing Edge Cases

The client supports testing various edge cases:

| Case | Example | Usage |
|------|---------|-------|
| Empty string | "" | `--message ""` |
| Special characters | "Hello\nWorld\t!" | `--message "Hello\nWorld\t!"` |
| Unicode | "你好世界" | `--message "你好世界"` |
| Emoji | "Hello 🎉" | `--message "Hello 🎉"` |
| Long string | "a" * 1000 | `--message "$( python -c 'print("a" * 1000)' )"` |
| Negative numbers | -5 | `--args -5 -3` |
| Floats | 3.5 | `--args 3.5 2.5` |

## Troubleshooting

### "Connection refused" error

**Problem**: `Error: Connection refused`

**Solution**: Ensure the server is running:
```bash
./scripts/start-mpc-server.sh echo
```

### "Unknown tool" error

**Problem**: `Error: Unknown tool: my_tool`

**Solution**: Check available tools:
```bash
python clients/http_client.py --list-tools
```

### "Missing argument" error

**Problem**: `Error: --message is required`

**Solution**: Provide required arguments:
```bash
python clients/http_client.py --tool echo_string --message "Hello"
```

## Best Practices

1. **Server First**: Always start the server before running client tests
2. **Check Tools**: Use `--list-tools` to see available tools for your server type
3. **Test Scenarios**: Start with `--scenario basic` for quick validation
4. **Edge Cases**: Use comprehensive tests for thorough validation
5. **Debugging**: Use `--curl-examples` to understand the request format

## Development

To extend the client:

1. Add new test scenarios to `MCPEchoServerClient._test_*` methods
2. Add new tools as methods following the pattern: `def tool_name(self, *args)`
3. Update `_get_available_tools()` for new tool discovery

## See Also

- `../scripts/start-mpc-server.sh` - Server startup script
- `../src/echo.py` - Echo server implementation
- `../src/server.py` - Demo server implementation
- `../tests/` - Pytest test suite

