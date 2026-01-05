"""
FastMCP Echo Server that sends log messages and progress updates to the client.

This module implements an MCP server that demonstrates logging and progress
tracking capabilities, following modern Python best practices with FastAPI,
Pydantic, and proper error handling.
"""

import asyncio
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mcp.server.fastmcp import Context, FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server
mcp = FastMCP("Echo Server with logging and progress updates")


class MockContext:
    """Mock context for HTTP API calls that safely handles progress and logging"""

    async def report_progress(self, progress: int, total: int) -> None:
        """Mock progress reporting"""
        logger.info(f"Progress: {progress}/{total} ({100*progress//total}%)")

    async def info(self, message: str) -> None:
        """Mock info logging"""
        logger.info(message)


@mcp.tool()
async def echo(text: str, ctx: Context = None) -> str:
    """
    Echo the input text sending log messages and progress updates during processing.

    This tool demonstrates:
    - Progress reporting to the client
    - Logging information messages
    - Asynchronous processing with delays

    Args:
        text: The text to echo back
        ctx: MCP context for sending progress and log messages

    Returns:
        The echoed text
    """
    # Use mock context if not provided (for HTTP API calls)
    if ctx is None:
        ctx = MockContext()

    # Start progress tracking
    await ctx.report_progress(progress=0, total=100)
    await ctx.info("Starting to process echo for input: " + text)

    # First processing phase
    await asyncio.sleep(2)

    # Halfway progress update
    await ctx.info("Halfway through processing echo for input: " + text)
    await ctx.report_progress(progress=50, total=100)

    # Second processing phase
    await asyncio.sleep(2)

    # Completion
    await ctx.info("Finished processing echo for input: " + text)
    await ctx.report_progress(progress=100, total=100)

    # Progress notifications are processed asynchronously by the client.
    # A small delay here helps ensure the last notification is processed by the client.
    await asyncio.sleep(0.1)

    logger.info(f"Echo operation completed successfully for input: {text}")
    return text


# Create FastAPI app for HTTP API
app = FastAPI(title="MCP Echo Server with Logging and Progress", version="1.0.0")


# Request models
class EchoRequest(BaseModel):
    text: str


@app.get("/")
async def get_root():
    """Get server information"""
    return {
        "name": "Echo Server with logging and progress updates",
        "version": "1.0.0",
        "description": "FastMCP server demonstrating logging and progress tracking",
        "status": "running"
    }


@app.get("/api/tools")
async def list_tools():
    """List all available tools"""
    try:
        tools_response = await mcp.list_tools()
        # Handle the response correctly - it may be a list or object with tools
        tools_list = tools_response.tools if hasattr(tools_response, 'tools') else tools_response
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema if hasattr(tool, 'inputSchema') else {}
                }
                for tool in tools_list
            ]
        }
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        return {"tools": [], "error": str(e)}


@app.post("/api/tools/echo")
async def call_echo_tool(request: EchoRequest):
    """Call the echo tool with logging and progress tracking"""
    logger.info(f"Calling echo tool with text: {request.text}")
    try:
        # Call the echo function with MockContext for HTTP API
        result = await echo(request.text, MockContext())
        return {
            "success": True,
            "result": result,
            "message": "Echo completed successfully"
        }
    except Exception as e:
        logger.error(f"Error calling echo tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


