"""
FastMCP Echo Server with direct CallToolResult return

Demonstrates using CallToolResult for structured responses with metadata.
Follows FastMCP Server guidelines with proper logging, validation, and error handling.
"""

import asyncio
import logging

from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Create server
mcp = FastMCP("Echo Server with CallToolResult")


class EchoResponse(BaseModel):
    """Response model for echo tool"""
    text: str = Field(..., description="The echoed text")


@mcp.tool(
    name="echo",
    description="Echo the input text with structure and metadata"
)
def echo(text: str = Field(..., description="Text to echo")) -> CallToolResult:
    """
    Echo the input text and return structured response with metadata.

    Args:
        text: The text string to echo back

    Returns:
        CallToolResult: Response containing text content and structured metadata

    Raises:
        ValueError: If text is None or invalid
    """
    logger.info(f"echo tool called with text: {text}")

    if text is None:
        logger.error("echo tool called with None text")
        raise ValueError("Text parameter cannot be None")

    try:
        # Create structured response
        response = EchoResponse(text=text)
        logger.debug(f"EchoResponse created: {response}")

        # Prepare metadata
        metadata = {"echo_length": len(text), "type": "echo_response"}
        logger.info(f"echo tool metadata: {metadata}")

        # Return CallToolResult with content, structured content, and metadata
        result = CallToolResult(
            content=[TextContent(type="text", text=text)],
            structuredContent={
                "original_text": text,
                "status": "success",
                "length": len(text)
            },
            _meta={"some": "metadata"}
        )
        logger.info(f"echo tool returning CallToolResult")
        return result

    except Exception as e:
        logger.error(f"Error in echo tool: {e}", exc_info=True)
        raise RuntimeError(f"Echo tool failed: {str(e)}") from e


async def main():
    """Main entry point for the FastMCP server"""
    logger.info("=" * 80)
    logger.info("ECHO SERVER WITH CALLTOOLRESULT INITIALIZATION")
    logger.info("=" * 80)
    logger.info(f"Server Name: {mcp.name}")
    logger.info(f"Server Version: 1.0.0")
    logger.info(f"Tool: echo (direct CallToolResult return)")
    logger.info("=" * 80)

    async with mcp.run_stdio() as stdio:
        logger.info("=" * 80)
        logger.info("FASTMCP SERVER RUNNING")
        logger.info("=" * 80)
        logger.info("Server is listening for MCP protocol messages via stdio")
        logger.info("Use MCP clients to invoke tools")
        logger.info("=" * 80)
        await stdio


if __name__ == "__main__":
    # Configure detailed logging for CLI execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    logger = logging.getLogger(__name__)

    logger.info("=" * 80)
    logger.info("STARTING FASTMCP ECHO SERVER")
    logger.info("=" * 80)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server startup failed: {e}", exc_info=True)
        raise
