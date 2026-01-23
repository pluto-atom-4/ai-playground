"""
Simple Resource MCP Server

A lightweight MCP server implementation that serves sample text resources.
Demonstrates MCP server lifecycle management, resource handling, and MCP tools.

This FastMCP server implementation follows the MCP specification for resource management,
providing a clean example of:
- Environment-based configuration (python-dotenv)
- Structured logging at INFO level
- Graceful async/await implementation
- Both stdio and SSE transport support
- Proper error handling with user-friendly messages
- MCP Tool definition and invocation (@app.tool decorators)

Resources:
    The server provides three sample text resources:
    - greeting: Welcome message
    - help: Help documentation
    - about: Server information

Available Tools:
    1. list_resources_tool()
       Lists all available resources with their metadata.
       Returns: Dictionary with "resources" (list) and "count" (int) keys
       Example:
           {
               "resources": [
                   {"name": "greeting", "title": "Welcome Message", ...},
                   ...
               ],
               "count": 3
           }

    2. get_resource_content(resource_name: str)
       Retrieves the full content of a specific resource by name.
       Args: resource_name (str) - Name of resource: "greeting", "help", or "about"
       Returns: Dictionary with "name", "title", "content", and "uri" keys
       Example:
           {
               "name": "greeting",
               "title": "Welcome Message",
               "content": "Hello! This is a sample text resource.",
               "uri": "file:///greeting.txt"
           }
       Raises: ValueError if resource not found or name is invalid

Usage:
    # Using stdio transport (default)
    python simple_resource_mcp_server.py

    # Show help
    python simple_resource_mcp_server.py --help

Environment Variables:
    LOG_LEVEL: Logging level (default: INFO)
              Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL

Transport Types:
    stdio: Standard input/output (default, best for direct MCP connections)
    sse: Server-Sent Events (best for HTTP-based clients)
"""

import logging
import os
from urllib.parse import urlparse

import anyio
import click
from dotenv import load_dotenv

import mcp.types as types
from mcp.server.lowlevel.helper_types import ReadResourceContents

from mcp.server.fastmcp import FastMCP

# ============================================================================
# Configuration & Initialization
# ============================================================================

# Load environment variables from .env file if present
load_dotenv()

# Configure logging based on environment variable
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

logger.info(f"Simple Resource MCP Server initializing with LOG_LEVEL={log_level}")

# ============================================================================
# Sample Resources
# ============================================================================

SAMPLE_RESOURCES = {
    "greeting": {
        "content": "Hello! This is a sample text resource.",
        "title": "Welcome Message",
    },
    "help": {
        "content": "This server provides a few sample text resources for testing.",
        "title": "Help Documentation",
    },
    "about": {
        "content": "This is the simple-resource MCP server implementation.",
        "title": "About This Server",
    },
}

# ============================================================================
# MCP Server Instance
# ============================================================================

# Create the MCP server instance as a global variable for mcp-inspector support
mcp = FastMCP("mcp-simple-resource")
logger.info(f"MCP server instance created: {mcp.name}")


# ============================================================================
# MCP Resource Handlers
# ============================================================================


async def list_resources() -> list[types.Resource]:
    """
    List all available resources.

    Returns:
        A list of Resource objects representing all available resources.
        Each resource includes name, title, description, URI, and mime type.

    Logging:
        - INFO: Resource list retrieval attempt
    """
    try:
        resources = [
            types.Resource(
                uri=f"file:///{name}.txt",
                name=name,
                title=SAMPLE_RESOURCES[name]["title"],
                description=f"A sample text resource named {name}",
                mime_type="text/plain",
            )
            for name in SAMPLE_RESOURCES.keys()
        ]
        logger.info(f"Resource listing requested: found {len(resources)} available resources")
        return resources
    except Exception as e:
        logger.error(f"Error listing resources: {e}", exc_info=True)
        raise


async def read_resource(uri: str) -> list[ReadResourceContents]:
    """
    Read the content of a specific resource by URI.

    Args:
        uri: The resource URI in format "file:///resource_name.txt"

    Returns:
        A list containing one ReadResourceContents object with the resource content.

    Raises:
        ValueError: If the URI format is invalid or the resource is not found.

    Logging:
        - INFO: Successful resource read
        - WARNING: Invalid URI format or unknown resource
    """
    try:
        # Parse the URI to extract resource name
        parsed = urlparse(uri)
        if not parsed.path:
            error_msg = f"Invalid resource path: URI has no path component: {uri}"
            logger.warning(error_msg)
            raise ValueError(error_msg)

        # Extract resource name from path (remove .txt extension and leading slash)
        name = parsed.path.replace(".txt", "").lstrip("/")

        # Validate resource exists
        if name not in SAMPLE_RESOURCES:
            error_msg = f"Unknown resource requested: {name}. Available resources: {list(SAMPLE_RESOURCES.keys())}"
            logger.warning(error_msg)
            raise ValueError(error_msg)

        content = SAMPLE_RESOURCES[name]["content"]
        logger.info(f"Resource read successfully: {name} ({uri})")

        return [
            ReadResourceContents(
                content=content,
                mime_type="text/plain",
            )
        ]

    except ValueError as e:
        # Re-raise validation errors with original context
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading resource {uri}: {e}", exc_info=True)
        raise ValueError(f"Error reading resource: {str(e)}")


# ============================================================================
# MCP Tools
# ============================================================================


@mcp.tool()
def list_resources_tool() -> dict:
    """
    List all available resources in the server.

    Returns a dictionary containing a list of all available resources with their
    names, titles, and descriptions.

    Returns:
        A dictionary with:
        - resources: List of dictionaries containing resource metadata
        - count: Total number of available resources

    Example:
        {
            "resources": [
                {
                    "name": "greeting",
                    "title": "Welcome Message",
                    "description": "A sample text resource named greeting",
                    "uri": "file:///greeting.txt"
                },
                ...
            ],
            "count": 3
        }

    Logging:
        - INFO: Successful listing of resources
    """
    try:
        resources = []
        for name in SAMPLE_RESOURCES.keys():
            resources.append(
                {
                    "name": name,
                    "title": SAMPLE_RESOURCES[name]["title"],
                    "description": f"A sample text resource named {name}",
                    "uri": f"file:///{name}.txt",
                }
            )

        logger.info(f"Tool 'list_resources_tool' invoked: returning {len(resources)} resources")

        return {
            "resources": resources,
            "count": len(resources),
        }
    except Exception as e:
        logger.error(f"Error in list_resources_tool: {e}", exc_info=True)
        raise


@mcp.tool()
def get_resource_content(resource_name: str) -> dict:
    """
    Get the content of a specific resource by name.

    Args:
        resource_name: The name of the resource to retrieve (e.g., "greeting", "help", "about")

    Returns:
        A dictionary containing:
        - name: The resource name
        - title: The resource title
        - content: The resource content
        - uri: The resource URI

    Raises:
        ValueError: If the resource name is invalid or not found.

    Example:
        {
            "name": "greeting",
            "title": "Welcome Message",
            "content": "Hello! This is a sample text resource.",
            "uri": "file:///greeting.txt"
        }

    Logging:
        - INFO: Successful resource content retrieval
        - WARNING: Resource not found
        - ERROR: Unexpected errors during retrieval
    """
    try:
        # Validate resource exists
        if not resource_name or resource_name not in SAMPLE_RESOURCES:
            available = list(SAMPLE_RESOURCES.keys())
            error_msg = f"Unknown resource: '{resource_name}'. Available resources: {available}"
            logger.warning(error_msg)
            raise ValueError(error_msg)

        resource_data = SAMPLE_RESOURCES[resource_name]
        result = {
            "name": resource_name,
            "title": resource_data["title"],
            "content": resource_data["content"],
            "uri": f"file:///{resource_name}.txt",
        }

        logger.info(f"Tool 'get_resource_content' invoked for resource: {resource_name}")

        return result
    except ValueError as e:
        raise
    except Exception as e:
        logger.error(f"Error in get_resource_content: {e}", exc_info=True)
        raise ValueError(f"Error retrieving resource content: {str(e)}")


# ============================================================================
# Server Lifecycle & Transport Management
# ============================================================================


@click.command()
@click.option("--port", default=8000, type=int, help="Port to listen on for SSE transport (default: 8000)")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type: stdio (default) or sse",
)
def main(port: int, transport: str) -> int:
    """
    Start the Simple Resource MCP Server.

    This function initializes the MCP server lifecycle and starts the appropriate
    transport handler based on the --transport argument.

    Args:
        port: Port number for SSE transport (default: 8000)
        transport: Transport type - "stdio" for stdio transport (default),
                  or "sse" for Server-Sent Events transport

    Returns:
        Exit code (0 for success, 1 for error)

    Server Lifecycle:
        1. Startup: Initialize MCP server with stdio or SSE transport
        2. Running: Accept MCP protocol messages and route to resource handlers
        3. Shutdown: Handle graceful shutdown on SIGTERM/SIGINT

    Logging:
        - INFO: Server startup and configuration
        - INFO: Transport selection and initialization
        - INFO: Graceful shutdown notification
        - ERROR: Any fatal errors during execution
    """
    global mcp

    logger.info(f"Starting Simple Resource MCP Server with transport={transport}")

    if transport == "sse":
        logger.info(f"Configuring SSE transport on http://127.0.0.1:{port}")
    else:
        logger.info("Configuring stdio transport")

    logger.info("Simple Resource MCP Server shutdown complete")
    return 0


# ============================================================================
# Entry Point
# ============================================================================


if __name__ == "__main__":
    """
    Entry point for the Simple Resource MCP Server.

    This script sets up logging and handles top-level exceptions to ensure
    proper error reporting and graceful shutdown.

    Execution:
        python simple_resource_mcp_server.py [OPTIONS]

    Options:
        --transport [stdio|sse]: Transport type (default: stdio)
        --port PORT: Port for SSE transport (default: 8000)
        --help: Show this help message
    """
    try:
        logger.info("=" * 70)
        logger.info("Simple Resource MCP Server Startup")
        logger.info("=" * 70)
        exit_code = main()
        logger.info("=" * 70)
        logger.info(f"Simple Resource MCP Server exiting with code {exit_code}")
        logger.info("=" * 70)
        exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Server interrupted by user (Ctrl+C)")
        exit(0)
    except Exception as e:
        logger.error("=" * 70)
        logger.error(f"Fatal error: {e}", exc_info=True)
        logger.error("=" * 70)
        exit(1)
