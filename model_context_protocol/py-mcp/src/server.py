"""
Simple MCP Server implementation.

This module implements a basic Model Context Protocol server with example tools.
"""

import logging
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPServer:
    """Simple MCP Server with example tools."""

    def __init__(self) -> None:
        """Initialize the MCP Server."""
        self.server = Server("py-mcp")
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Register tools with the server."""
        # Register echo_string tool
        self.server.register_tool(
            Tool(
                name="echo_string",
                description="Echo a string back to the caller",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The message to echo",
                        }
                    },
                    "required": ["message"],
                },
            ),
            self._handle_echo_string,
        )

        # Register add_numbers tool
        self.server.register_tool(
            Tool(
                name="add_numbers",
                description="Add two numbers together",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"},
                    },
                    "required": ["a", "b"],
                },
            ),
            self._handle_add_numbers,
        )

        # Register get_string_length tool
        self.server.register_tool(
            Tool(
                name="get_string_length",
                description="Get the length of a string",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text to measure",
                        }
                    },
                    "required": ["text"],
                },
            ),
            self._handle_get_string_length,
        )

    async def _handle_echo_string(self, message: str) -> ToolResult:
        """Handle the echo_string tool call."""
        logger.info(f"Echoing message: {message}")
        return ToolResult(
            content=[TextContent(type="text", text=f"Echo: {message}")],
            isError=False,
        )

    async def _handle_add_numbers(self, a: float, b: float) -> ToolResult:
        """Handle the add_numbers tool call."""
        result = a + b
        logger.info(f"Adding {a} + {b} = {result}")
        return ToolResult(
            content=[TextContent(type="text", text=f"Result: {a} + {b} = {result}")],
            isError=False,
        )

    async def _handle_get_string_length(self, text: str) -> ToolResult:
        """Handle the get_string_length tool call."""
        length = len(text)
        logger.info(f"String '{text}' has length {length}")
        return ToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"The string '{text}' has {length} characters",
                )
            ],
            isError=False,
        )

    def get_server(self) -> Server:
        """Get the underlying MCP Server instance."""
        return self.server

