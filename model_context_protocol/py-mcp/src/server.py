"""
Simple MCP Server implementation using FastMCP (annotation-based API) with logging.
"""

import logging
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("mcp.server")

# Create an MCP server instance
mcp = FastMCP("Demo", json_response=True)


@mcp.tool(
    name="echo_string",
    description="Echo a string back to the caller"
)
def echo_string(message: str):
    logger.info(f"echo_string called with message: {message}")
    return {
        "content": [TextContent(type="text", text=message)],
        "isError": False,
    }


@mcp.tool(
    name="add_numbers",
    description="Add two numbers together"
)
def add_numbers(a: float, b: float):
    logger.info(f"add_numbers called with a={a}, b={b}")
    result = a + b
    logger.info(f"add_numbers result: {result}")
    return {
        "content": [TextContent(type="text", text=str(result))],
        "isError": False,
    }


@mcp.tool(
    name="get_string_length",
    description="Get the length of a string"
)
def get_string_length(input: str):
    logger.info(f"get_string_length called with input: {input}")
    length = len(input)
    logger.info(f"get_string_length result: {length}")
    return {
        "content": [TextContent(type="text", text=str(length))],
        "isError": False,
    }


if __name__ == "__main__":
    logger.info("Starting MCP server...")
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user (CTRL+C)")
        exit(0)
