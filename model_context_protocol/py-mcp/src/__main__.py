"""
Entry point for running the MCP Server.

This module sets up and runs the MCP server with stdio transport.
"""

import asyncio
import sys

from mcp.server.stdio import stdio_server

from .server import MCPServer


async def main() -> None:
    """Run the MCP server."""
    # Create the MCP server
    mcp_server = MCPServer()
    server = mcp_server.get_server()

    # Run the server with stdio transport
    async with stdio_server(server) as (read_stream, write_stream):
        await server.run(read_stream, write_stream, sys.exit)


if __name__ == "__main__":
    asyncio.run(main())

