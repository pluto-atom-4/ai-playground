"""
MCP Server Implementation - Quick Start Guide (Decorator API)
"""

# MCP Server - Python Model Context Protocol

This is a simple implementation of a Model Context Protocol (MCP) server using the annotation-based API from the [Python SDK quickstart](https://github.com/modelcontextprotocol/python-sdk#quickstart).

## Overview

This server exposes three example tools using decorators:

- **echo_string**: Echoes a string message back to the caller
- **add_numbers**: Adds two numbers together
- **get_string_length**: Returns the length of a string

## Project Structure

```
src/
├── __init__.py      # Package initialization and exports
├── __main__.py      # Entry point for running the server
└── server.py        # Simple MCP server implementation (decorator API)
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
python src/server.py
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

## Outline for Implementing an MCP Server with Decorators
Implementing an MCP server using decorators involves organizing your code to define tools, resources, and prompts that interact seamlessly within the Model Context Protocol. Below is a structured outline to guide you through the implementation.

1. Create the MCP Server
   * Import Necessary Modules
     - Start by importing the necessary classes and decorators from the MCP SDK.
       ```python
       from modelcontextprotocol import MCP  # Main server class
       ```
     - Initialize the MCP Server
       ```python
       mcp = MCP()
       ```

2. Define Tools with `@mcp.tool`
   * Create Tool Functions
     - Use the` @mcp.tool` decorator to define functions that serve specific functionalities (tools).
       ```python
       @mcp.tool
       def add_numbers(a: int, b: int) -> int:
          return a + b
       ```

3. Define Resources with `@mcp.resource`
   * Create Resource Classes
     - Use the` @mcp.resource` decorator to define classes that represent resources. Resources can manage model states or configurations.
        ```python 
        @mcp.resource
        class ModelResource:
            def __init__(self):
                self.result = 0
            
            @mcp.tool
            def multiply(self, x: int, y: int) -> int:
                self.result = x * y
                return self.result
        ```
    * Create Resource Functions
      - Use the `@mcp.resource` decorator to define functions that provide resource-related functionalities.
        ```python
        @mcp.resource
        def get_string_length(s: str) -> int:
            return len(s)
        ```

4. Define Prompts with `@mcp.prompt`
   * Create Prompt Functions 
     - Use the `@mcp.prompt` decorator to facilitate natural language prompts, making it easier for users to interact with your server.
       ```python  
       @mcp.prompt
       def greet(name: str) -> str:
           return f"Hello, {name}!"
       ```

5. Define Additional Decorators
   * Include any other necessary MCP decorators such as @mcp.event, @mcp.error_handler, and others, depending on your application requirements. 

6. Run the MCP Server
   * Define Entry Point
     - Include a main block to run the server. This will enable the server to process requests.
        ```python
        if __name__ == "__main__":
            mcp.run(host='0.0.0.0', port=8000)
        ```
       
8. Test the Server
    * Write Unit Tests
      - Create unit tests for each tool, resource, and prompt to ensure they function as expected.
        ```python
        def test_add_numbers():
            assert add_numbers(2, 3) == 5
        ```
    * Use Testing Frameworks
      - Utilize frameworks like pytest to run your tests and validate the server's functionality.

9. Implement Logging and Error Handling
   * Add Logging 
     - Implement logging to capture server behavior and user interactions for debugging and analytics.
       ```python
       import logging
    
       logging.basicConfig(level=logging.INFO)
       ``` 
   * Handle Errors Gracefully
     - Use custom error handling to provide meaningful messages during failures.

10. Document and Refactor
    * Code Documentation
      - Add docstrings and comments to enhance code readability and maintainability.
    * Refactor Code
      - Organize the code into separate modules if necessary for better management and scalability.

## References

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
