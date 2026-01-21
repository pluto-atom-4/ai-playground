"""
Simple Tool MCP Server - Website Fetcher

A lightweight MCP server implementation that fetches website content.
Demonstrates FastMCP tool registration and MCP server lifecycle management.

Usage:
    python simple-tool-mcp-server.py

    With options:
    python simple-tool-mcp-server.py --help
"""

import logging
import os
from typing import Any

import click
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("simple-tool.server")

# Create FastMCP server instance
mcp = FastMCP("mcp-website-fetcher")


@mcp.tool(
    name="fetch",
    description="Fetches a website and returns its content",
)
def fetch_website(url: str) -> dict[str, Any]:
    """
    Fetch the content of a website.

    Args:
        url: The URL to fetch

    Returns:
        Dictionary with content and status information

    Raises:
        ValueError: If URL is invalid or fetch fails
    """
    logger.info(f"Fetching website from URL: {url}")

    if not url:
        error_msg = "URL cannot be empty"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if not url.startswith(("http://", "https://")):
        error_msg = f"Invalid URL: {url} (must start with http:// or https://)"
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        import httpx

        headers = {
            "User-Agent": "MCP Simple Tool Server (github.com/modelcontextprotocol)"
        }

        response = httpx.get(url, headers=headers, timeout=30.0)
        response.raise_for_status()

        content = response.text
        logger.info(
            f"Successfully fetched {len(content)} bytes from {url}"
        )

        return {
            "content": [
                TextContent(type="text", text=content)
            ],
            "isError": False,
        }

    except ImportError:
        error_msg = "httpx library not installed"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Failed to fetch {url}: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)


@click.command()
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Set logging level",
)
def main(log_level: str) -> int:
    """
    Main entry point for the Simple Tool MCP Server.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Update logging level if specified
    if log_level:
        logging.getLogger().setLevel(log_level.upper())
        logger.info(f"Set logging level to {log_level.upper()}")

    logger.info(f"Starting Simple Tool MCP Server")

    try:
        mcp.run()
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user (CTRL+C)")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        exit(1)
