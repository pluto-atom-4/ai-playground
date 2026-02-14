"""Simple task server demonstrating MCP tasks over streamable HTTP.

This server can be run in several ways:
1. As an MCP server over stdio (for mcp-inspector):
   mcp-inspector "python -m src.servers.simple_task"

2. As a standalone server:
   python -m src.servers.simple_task
"""

import asyncio
import logging
import os

import anyio
import click
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("simple-task-server")

# Create the MCP server instance
# This is the main server object that mcp-inspector will discover and communicate with
server = FastMCP("simple-task-server")


@server.tool()
async def long_running_task() -> str:
    """A task that takes a few seconds to complete with status updates"""
    logger.info("Long running task started")
    try:
        logger.info("Starting work...")
        await anyio.sleep(1)

        logger.info("Processing step 1...")
        await anyio.sleep(1)

        logger.info("Processing step 2...")
        await anyio.sleep(1)

        logger.info("Long running task completed successfully")
        return "Task completed!"
    except Exception as e:
        logger.error(f"Task execution failed: {e}", exc_info=True)
        raise


@click.command()
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Set logging level",
)
def main(log_level: str = "INFO") -> int:
    """Start the simple task MCP server."""
    # Update logging level
    logging.getLogger().setLevel(log_level.upper())
    logger.info(f"Set logging level to {log_level.upper()}")
    logger.info("Starting Simple Task Server")

    try:
        server.run()
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user (CTRL+C)")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        return 1
