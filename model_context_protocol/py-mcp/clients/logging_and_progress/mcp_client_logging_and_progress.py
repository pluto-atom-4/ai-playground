#!/usr/bin/env python
"""
MCP Client for testing FastMCP Echo Server with Logging and Progress Updates

This script provides an HTTP client interface to interact with the FastMCP Echo Server
and test its echo tool with logging and progress tracking capabilities.
It demonstrates how to handle progress notifications and log messages from the server.

Usage:
    python clients/logging_and_progress/mcp_client_logging_and_progress.py --help
    python clients/logging_and_progress/mcp_client_logging_and_progress.py --echo "Hello World"
    python clients/logging_and_progress/mcp_client_logging_and_progress.py --list-tools
    python clients/logging_and_progress/mcp_client_logging_and_progress.py --scenario basic
"""

import asyncio
import json
import logging
from typing import Any, Dict

import httpx
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class MCPLoggingProgressClient:
    """HTTP Client for interacting with FastMCP Echo Server via REST API"""

    DEFAULT_SERVER_URL = "http://127.0.0.1:8000"
    DEFAULT_TIMEOUT = 30.0

    def __init__(self, server_url: str = DEFAULT_SERVER_URL, timeout: float = DEFAULT_TIMEOUT):
        """
        Initialize the MCP Logging and Progress Client

        Args:
            server_url: Server base URL for HTTP API
            timeout: Request timeout in seconds
        """
        self.server_url = server_url
        self.timeout = timeout
        logger.info(f"Created MCP Logging and Progress Client for {server_url}")

    async def get_server_info(self) -> Dict[str, Any]:
        """
        Get server information

        Returns:
            Dictionary containing server info
        """
        logger.info("Fetching server information...")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.server_url}/")
                response.raise_for_status()
                logger.info("Successfully retrieved server information")
                return {
                    "success": True,
                    "info": response.json()
                }
        except Exception as e:
            logger.error(f"Error fetching server info: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def list_tools(self) -> Dict[str, Any]:
        """
        List available tools from the server

        Returns:
            Dictionary containing tools information
        """
        logger.info("Listing available tools...")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.server_url}/api/tools")
                response.raise_for_status()
                logger.info("Successfully retrieved tools from server")
                return {
                    "success": True,
                    "tools": response.json()
                }
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def call_echo_tool(self, text: str) -> Dict[str, Any]:
        """
        Call the echo tool and track progress and log messages

        Args:
            text: Text to echo back

        Returns:
            Dictionary containing echo result with progress tracking
        """
        logger.info(f"Starting echo operation with text: '{text}'")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Call the echo tool via REST API
                response = await client.post(
                    f"{self.server_url}/api/tools/echo",
                    json={"text": text}
                )
                response.raise_for_status()

                result = response.json()
                logger.info("Echo operation completed successfully")
                return {
                    "success": True,
                    "result": result,
                    "message": "Tool executed with progress tracking"
                }
        except Exception as e:
            logger.error(f"Error during echo operation: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def run_echo_scenario(self, text: str = "Hello from MCP Client") -> None:
        """
        Run a complete echo scenario demonstrating progress tracking

        Args:
            text: Text to echo
        """
        logger.info("=" * 60)
        logger.info("Starting MCP Echo Scenario")
        logger.info("=" * 60)

        # Get server info
        info_result = await self.get_server_info()
        if info_result["success"]:
            logger.info(f"Server Info: {info_result['info']}")
        else:
            logger.error(f"Failed to get server info: {info_result.get('error')}")
            return

        # List available tools
        tools_result = await self.list_tools()
        if tools_result["success"]:
            logger.info("Available Tools:")
            tools = tools_result["tools"]
            if isinstance(tools, dict) and "tools" in tools:
                for tool in tools.get("tools", []):
                    logger.info(f"  - {tool.get('name', 'unknown')}: {tool.get('description', '')}")
            else:
                logger.info(f"  {tools}")
        else:
            logger.error(f"Failed to list tools: {tools_result.get('error')}")

        # Execute echo with progress tracking
        logger.info("-" * 60)
        echo_result = await self.call_echo_tool(text)
        if echo_result["success"]:
            logger.info(f"Echo Result: {echo_result['result']}")
        else:
            logger.error(f"Echo failed: {echo_result.get('error')}")

        logger.info("=" * 60)
        logger.info("Echo Scenario Complete")
        logger.info("=" * 60)


async def main():
    """Main entry point for the MCP client"""
    import argparse

    parser = argparse.ArgumentParser(
        description="MCP Client for FastMCP Echo Server with Logging and Progress"
    )
    parser.add_argument(
        "--server-url",
        default=MCPLoggingProgressClient.DEFAULT_SERVER_URL,
        help="Server base URL"
    )
    parser.add_argument(
        "--echo",
        type=str,
        help="Text to echo"
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List available tools"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Get server information"
    )
    parser.add_argument(
        "--scenario",
        choices=["basic"],
        help="Run a predefined scenario"
    )

    args = parser.parse_args()

    client = MCPLoggingProgressClient(server_url=args.server_url)

    if args.info:
        result = await client.get_server_info()
        print(json.dumps(result, indent=2))
    elif args.echo:
        result = await client.call_echo_tool(args.echo)
        print(json.dumps(result, indent=2))
    elif args.list_tools:
        result = await client.list_tools()
        print(json.dumps(result, indent=2))
    elif args.scenario == "basic":
        await client.run_echo_scenario()
    else:
        # Default: run basic scenario
        await client.run_echo_scenario()


if __name__ == "__main__":
    asyncio.run(main())

