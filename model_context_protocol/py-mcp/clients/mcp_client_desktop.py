#!/usr/bin/env python
"""
MCP Client for testing Desktop MCP Server

This script provides an HTTP client interface to interact with the Desktop MCP Server
and test its tools and resources. It communicates with the FastMCP server via
HTTP REST API to test file browsing and reading capabilities.

Usage:
    python clients/mcp_client_desktop.py --list-tools
    python clients/mcp_client_desktop.py --list-resources
    python clients/mcp_client_desktop.py --tool list_desktop_files
    python clients/mcp_client_desktop.py --tool get_file_content --filename "README.md"
    python clients/mcp_client_desktop.py --tool get_desktop_stats
    python clients/mcp_client_desktop.py --resource "desktop://files"
    python clients/mcp_client_desktop.py --resource "desktop://stats"
    python clients/mcp_client_desktop.py --resource "desktop://file/README.md"
    python clients/mcp_client_desktop.py --scenario basic
    python clients/mcp_client_desktop.py --scenario comprehensive
"""

import json
import sys
import argparse
from typing import Any, Dict, List, Optional
from pathlib import Path
import logging

# HTTP libraries
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("mcp.desktop.client")


class MCPDesktopServerClient:
    """HTTP Client for interacting with MCP Desktop Server via REST API"""

    DEFAULT_BASE_URL = "http://127.0.0.1:8000"
    DEFAULT_API_KEY = "default-api-key-change-me"
    DEFAULT_TIMEOUT = 10.0

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str = DEFAULT_API_KEY,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the Desktop MCP Server Client

        Args:
            base_url: Base URL of the Desktop MCP Server
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        logger.info(f"Created Desktop MCP Client for {base_url}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the server

        Args:
            method: HTTP method ('GET' or 'POST')
            endpoint: API endpoint path
            data: Request data (for POST requests)

        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

        try:
            logger.info(f"{method} {url}")
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=self.timeout)
            else:
                response = requests.post(url, json=data, headers=headers, timeout=self.timeout)

            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Request error: {e}")
            return {
                "error": str(e),
                "message": f"Failed to connect to server at {self.base_url}",
                "isError": True,
            }

    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        logger.info("Fetching server info...")
        return self._make_request("GET", "/api/info")

    def list_tools(self) -> Dict[str, Any]:
        """List all available tools on the server"""
        logger.info("Fetching available tools...")
        return self._make_request("GET", "/api/tools")

    def list_resources(self) -> Dict[str, Any]:
        """List all available resources on the server"""
        logger.info("Fetching available resources...")
        return self._make_request("GET", "/api/resources")

    def list_desktop_files(self) -> Dict[str, Any]:
        """List files on the desktop"""
        logger.info("Listing desktop files...")
        return self._make_request("GET", "/api/desktop/files")

    def get_file_content(self, filename: str) -> Dict[str, Any]:
        """Get content of a file"""
        logger.info(f"Getting file content: {filename}")
        data = {"filename": filename}
        return self._make_request("POST", "/api/desktop/file", data)

    def get_desktop_stats(self) -> Dict[str, Any]:
        """Get desktop statistics"""
        logger.info("Fetching desktop statistics...")
        return self._make_request("GET", "/api/desktop/stats")

    def run_test_scenario(self, scenario: str = "basic"):
        """Run predefined test scenarios"""
        print(f"\n🧪 Running test scenario: {scenario}")
        print("=" * 70)
        print()

        if scenario == "basic":
            self._test_basic()
        elif scenario == "comprehensive":
            self._test_comprehensive()
        else:
            print(f"❌ Unknown scenario: {scenario}")

    def _test_basic(self):
        """Basic test scenario"""
        print("Test 1: Get Server Info")
        print("-" * 70)
        result = self.get_server_info()
        self._print_result(result)

        print("Test 2: List Available Tools")
        print("-" * 70)
        result = self.list_tools()
        self._print_result(result)

        print("Test 3: List Available Resources")
        print("-" * 70)
        result = self.list_resources()
        self._print_result(result)

        print("Test 4: List Desktop Files")
        print("-" * 70)
        result = self.list_desktop_files()
        self._print_result(result)

        print("Test 5: Get Desktop Statistics")
        print("-" * 70)
        result = self.get_desktop_stats()
        self._print_result(result)

    def _test_comprehensive(self):
        """Comprehensive test scenario"""
        print("Test 1: Get Server Info")
        print("-" * 70)
        result = self.get_server_info()
        self._print_result(result)

        print("Test 2: List Available Tools")
        print("-" * 70)
        result = self.list_tools()
        self._print_result(result)

        print("Test 3: List Available Resources")
        print("-" * 70)
        result = self.list_resources()
        self._print_result(result)

        print("Test 4: List Desktop Files")
        print("-" * 70)
        result = self.list_desktop_files()
        self._print_result(result)

        print("Test 5: Get Desktop Statistics")
        print("-" * 70)
        result = self.get_desktop_stats()
        self._print_result(result)

        print("Test 6: Try to Get File Content (README.md)")
        print("-" * 70)
        result = self.get_file_content("README.md")
        self._print_result(result)

        print("Test 7: Try to Get File Content (Makefile)")
        print("-" * 70)
        result = self.get_file_content("Makefile")
        self._print_result(result)

        print("Test 8: List Files Again (for consistency)")
        print("-" * 70)
        result = self.list_desktop_files()
        self._print_result(result)

    def _print_result(self, result: Dict[str, Any]):
        """Pretty print the result"""
        if isinstance(result, dict):
            if result.get("isError"):
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
            elif "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print("📥 Response:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"📥 Response:\n{result}")
        print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="HTTP Client for Desktop MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clients/mcp_client_desktop.py --list-tools
  python clients/mcp_client_desktop.py --info
  python clients/mcp_client_desktop.py --tool list_desktop_files
  python clients/mcp_client_desktop.py --tool get_file_content --filename "README.md"
  python clients/mcp_client_desktop.py --tool get_desktop_stats
  python clients/mcp_client_desktop.py --scenario basic
  python clients/mcp_client_desktop.py --scenario comprehensive
        """,
    )

    parser.add_argument(
        "--url",
        default=MCPDesktopServerClient.DEFAULT_BASE_URL,
        help=f"Server URL (default: {MCPDesktopServerClient.DEFAULT_BASE_URL})",
    )

    parser.add_argument(
        "--api-key",
        default=MCPDesktopServerClient.DEFAULT_API_KEY,
        help="API key for authentication",
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="Get server information",
    )

    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List all available tools on the server",
    )

    parser.add_argument(
        "--list-resources",
        action="store_true",
        help="List all available resources on the server",
    )

    parser.add_argument(
        "--tool",
        help="Specific tool to call (list_desktop_files, get_file_content, get_desktop_stats)",
    )

    parser.add_argument(
        "--filename",
        help="Filename argument for get_file_content tool",
    )

    parser.add_argument(
        "--scenario",
        choices=["basic", "comprehensive"],
        default="basic",
        help="Run a predefined test scenario (default: basic)",
    )

    args = parser.parse_args()

    # Create client
    client = MCPDesktopServerClient(base_url=args.url, api_key=args.api_key)

    try:
        # Handle different commands
        if args.info:
            print("📡 Fetching server info...")
            print()
            result = client.get_server_info()
            client._print_result(result)

        elif args.list_tools:
            print("📡 Fetching available tools...")
            print()
            result = client.list_tools()
            client._print_result(result)

        elif args.list_resources:
            print("📡 Fetching available resources...")
            print()
            result = client.list_resources()
            client._print_result(result)

        elif args.tool:
            # Call specific tool
            if args.tool == "list_desktop_files":
                result = client.list_desktop_files()
                client._print_result(result)

            elif args.tool == "get_file_content":
                if args.filename is None:
                    print("❌ Error: --filename is required for get_file_content tool")
                    sys.exit(1)
                result = client.get_file_content(args.filename)
                client._print_result(result)

            elif args.tool == "get_desktop_stats":
                result = client.get_desktop_stats()
                client._print_result(result)

            else:
                print(f"❌ Error: Unknown tool: {args.tool}")
                sys.exit(1)

        else:
            # Run scenario
            client.run_test_scenario(scenario=args.scenario)

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

