#!/usr/bin/env python
"""
HTTP Client for inspecting MCP Echo Server behavior

This script provides an HTTP client interface to interact with the MCP Echo Server
running on http://127.0.0.1:8000 and inspect its responses. It supports both
requests and httpx libraries for making HTTP calls.

Usage:
    python clients/http_client.py --server-type echo
    python clients/http_client.py --tool echo --message "Hello World"
    python clients/http_client.py --list-tools
    python clients/http_client.py --info
    python clients/http_client.py --client httpx --tool echo --message "Test"
"""

import json
import sys
import argparse
import os
from typing import Any, Dict, List, Optional
from pathlib import Path
import time

# Third-party HTTP libraries
import requests
import httpx

# Fix encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class MCPEchoServerClient:
    """Client for interacting with MCP Echo Server via HTTP API"""

    # Default server configuration
    DEFAULT_BASE_URL = "http://127.0.0.1:8000"
    DEFAULT_TIMEOUT = 10.0

    def __init__(
        self,
        server_type: str = "echo",
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        client_type: str = "requests",
    ):
        """
        Initialize the MCP Echo Server Client

        Args:
            server_type: Type of server ('echo' or 'demo')
            base_url: Base URL of the server
            timeout: Request timeout in seconds
            client_type: HTTP client library to use ('requests' or 'httpx')
        """
        self.server_type = server_type
        self.base_url = base_url
        self.timeout = timeout
        self.client_type = client_type
        self._validate_client_type()

    def _validate_client_type(self):
        """Validate that client_type is supported"""
        if self.client_type not in ["requests", "httpx"]:
            raise ValueError(f"Unsupported client_type: {self.client_type}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the server

        Args:
            method: HTTP method ('GET' or 'POST')
            endpoint: API endpoint path
            data: Request data (for POST requests)
            timeout: Request timeout

        Returns:
            Response data as dictionary
        """
        if timeout is None:
            timeout = self.timeout

        url = f"{self.base_url}{endpoint}"

        try:
            if self.client_type == "requests":
                return self._make_request_with_requests(method, url, data, timeout)
            else:
                return self._make_request_with_httpx(method, url, data, timeout)
        except Exception as e:
            return {
                "error": str(e),
                "message": f"Failed to connect to server at {self.base_url}",
                "isError": True,
            }

    def _make_request_with_requests(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]],
        timeout: float,
    ) -> Dict[str, Any]:
        """Make request using requests library"""
        print(f"  🔌 Using: requests library")
        headers = {"Content-Type": "application/json"}

        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        else:
            response = requests.post(url, json=data, headers=headers, timeout=timeout)

        response.raise_for_status()
        return response.json()

    def _make_request_with_httpx(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]],
        timeout: float,
    ) -> Dict[str, Any]:
        """Make request using httpx library"""
        print(f"  🔌 Using: httpx library")
        headers = {"Content-Type": "application/json"}

        with httpx.Client(timeout=timeout) as client:
            if method.upper() == "GET":
                response = client.get(url, headers=headers)
            else:
                response = client.post(url, json=data, headers=headers)

            response.raise_for_status()
            return response.json()

    def get_server_info(self) -> Dict[str, Any]:
        """Get server information and health status"""
        print(f"📡 Fetching server info from {self.base_url}/api/info")
        print()
        return self._make_request("GET", "/api/info")

    def list_tools(self) -> Dict[str, Any]:
        """List all available tools on the server"""
        print(f"📡 Fetching available tools from {self.base_url}/api/tools")
        print()
        return self._make_request("GET", "/api/tools")

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the server

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            Tool response
        """
        print(f"📤 Calling tool: {tool_name}")
        print(f"   Arguments: {json.dumps(arguments, ensure_ascii=False)}")
        print()

        payload = {"arguments": arguments}
        return self._make_request("POST", f"/api/tools/{tool_name}", payload)

    def echo(self, message: str) -> Dict[str, Any]:
        """Call the echo tool"""
        return self.call_tool("echo", {"message": message})

    def list_resources(self) -> Dict[str, Any]:
        """List all available resources on the server"""
        print(f"📡 Fetching available resources from {self.base_url}/api/resources")
        print()
        return self._make_request("GET", "/api/resources")

    def get_resource(self, resource_path: str) -> Dict[str, Any]:
        """
        Get a resource from the server

        Args:
            resource_path: Path to the resource

        Returns:
            Resource data
        """
        print(f"📤 Getting resource: {resource_path}")
        print()
        return self._make_request("GET", f"/api/resources/{resource_path}")

    def list_prompts(self) -> Dict[str, Any]:
        """List all available prompts on the server"""
        print(f"📡 Fetching available prompts from {self.base_url}/api/prompts")
        print()
        return self._make_request("GET", "/api/prompts")

    def call_prompt(self, prompt_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a prompt on the server

        Args:
            prompt_name: Name of the prompt to call
            arguments: Arguments to pass to the prompt

        Returns:
            Prompt response
        """
        print(f"📤 Calling prompt: {prompt_name}")
        print(f"   Arguments: {json.dumps(arguments, ensure_ascii=False)}")
        print()

        payload = {"arguments": arguments}
        return self._make_request("POST", f"/api/prompts/{prompt_name}", payload)

    def run_test_scenario(self, scenario: str = "basic"):
        """Run predefined test scenarios"""
        print(f"🧪 Running test scenario: {scenario}")
        print(f"📍 Server: {self.base_url}")
        print(f"🔌 Client: {self.client_type}")
        print("=" * 60)
        print()

        if scenario == "basic":
            self._test_basic()
        elif scenario == "comprehensive":
            self._test_comprehensive()
        else:
            print(f"❌ Unknown scenario: {scenario}")

    def _test_basic(self):
        """Basic test scenario"""
        print("Test 1: Server Info")
        print("-" * 40)
        result = self.get_server_info()
        self._print_result(result)

        print("\nTest 2: List Tools")
        print("-" * 40)
        result = self.list_tools()
        self._print_result(result)

        print("\nTest 3: Call Echo Tool")
        print("-" * 40)
        result = self.echo("Hello from HTTP Client!")
        self._print_result(result)

    def _test_comprehensive(self):
        """Comprehensive test scenario"""
        print("Test 1: Server Info")
        print("-" * 40)
        result = self.get_server_info()
        self._print_result(result)

        print("\nTest 2: List Tools")
        print("-" * 40)
        result = self.list_tools()
        self._print_result(result)

        print("\nTest 3: Echo - Simple Message")
        print("-" * 40)
        result = self.echo("Hello, Echo Server!")
        self._print_result(result)

        print("\nTest 4: Echo - Special Characters")
        print("-" * 40)
        result = self.echo("Special: @#$%^&*()")
        self._print_result(result)

        print("\nTest 5: Echo - Unicode")
        print("-" * 40)
        result = self.echo("Unicode: 你好🎉")
        self._print_result(result)

        print("\nTest 6: Echo - Empty String")
        print("-" * 40)
        result = self.echo("")
        self._print_result(result)

        print("\nTest 7: Echo - Long Message")
        print("-" * 40)
        result = self.echo("x" * 500)
        self._print_result(result)

        print("\nTest 8: List Resources")
        print("-" * 40)
        result = self.list_resources()
        self._print_result(result)

        print("\nTest 9: Get Static Resource")
        print("-" * 40)
        result = self.get_resource("echo/static")
        self._print_result(result)

        print("\nTest 10: Get Template Resource")
        print("-" * 40)
        result = self.get_resource("echo/test_message")
        self._print_result(result)

        print("\nTest 11: List Prompts")
        print("-" * 40)
        result = self.list_prompts()
        self._print_result(result)

        print("\nTest 12: Call Prompt")
        print("-" * 40)
        result = self.call_prompt("Echo", {"text": "Hello from Prompt!"})
        self._print_result(result)

    def _print_result(self, result: Dict[str, Any]):
        """Pretty print the result"""
        print("📥 Response:")
        if isinstance(result, dict) and "error" in result:
            print(f"❌ {result.get('message', result.get('error'))}")
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        print()

    def generate_curl_examples(self):
        """Generate curl command examples for testing (informational)"""
        print("📋 Example curl commands (for reference):")
        print("=" * 60)
        print()

        print("# Server Info")
        print(f"curl -X GET {self.base_url}/api/info | jq")
        print()

        print("# List Tools")
        print(f"curl -X GET {self.base_url}/api/tools | jq")
        print()

        print("# Call Echo Tool")
        print(f'curl -X POST {self.base_url}/api/tools/echo \\')
        print('  -H "Content-Type: application/json" \\')
        print('  -d \'{"arguments": {"message": "Hello, World!"}}\'')
        print()

        print("# List Resources")
        print(f"curl -X GET {self.base_url}/api/resources | jq")
        print()

        print("# Get Static Resource")
        print(f"curl -X GET {self.base_url}/api/resources/echo/static | jq")
        print()

        print("# List Prompts")
        print(f"curl -X GET {self.base_url}/api/prompts | jq")
        print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="HTTP Client for MCP Echo Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clients/http_client.py --info
  python clients/http_client.py --list-tools
  python clients/http_client.py --list-resources
  python clients/http_client.py --list-prompts
  python clients/http_client.py --tool echo --message "Hello World"
  python clients/http_client.py --client httpx --tool echo --message "Test"
  python clients/http_client.py --scenario comprehensive
  python clients/http_client.py --scenario comprehensive --client httpx
  python clients/http_client.py --curl-examples
        """,
    )

    parser.add_argument(
        "--server-url",
        default=MCPEchoServerClient.DEFAULT_BASE_URL,
        help=f"Base URL of the MCP server (default: {MCPEchoServerClient.DEFAULT_BASE_URL})",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=MCPEchoServerClient.DEFAULT_TIMEOUT,
        help=f"Request timeout in seconds (default: {MCPEchoServerClient.DEFAULT_TIMEOUT})",
    )

    parser.add_argument(
        "--client",
        choices=["requests", "httpx"],
        default="requests",
        help="HTTP client library to use (default: requests)",
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="Get server information and health status",
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
        "--list-prompts",
        action="store_true",
        help="List all available prompts on the server",
    )

    parser.add_argument(
        "--scenario",
        choices=["basic", "comprehensive"],
        default="basic",
        help="Run a predefined test scenario (default: basic)",
    )

    parser.add_argument(
        "--tool",
        help="Specific tool to call",
    )

    parser.add_argument(
        "--message",
        help="Message for echo tool",
    )

    parser.add_argument(
        "--resource",
        help="Resource path to retrieve",
    )

    parser.add_argument(
        "--prompt",
        help="Prompt name to call",
    )

    parser.add_argument(
        "--prompt-text",
        help="Text argument for prompt",
    )

    parser.add_argument(
        "--curl-examples",
        action="store_true",
        help="Show curl command examples",
    )

    args = parser.parse_args()

    # Create client
    client = MCPEchoServerClient(
        server_type="echo",
        base_url=args.server_url,
        timeout=args.timeout,
        client_type=args.client,
    )

    # Handle different commands
    if args.curl_examples:
        client.generate_curl_examples()
    elif args.info:
        result = client.get_server_info()
        client._print_result(result)
    elif args.list_tools:
        result = client.list_tools()
        client._print_result(result)
    elif args.list_resources:
        result = client.list_resources()
        client._print_result(result)
    elif args.list_prompts:
        result = client.list_prompts()
        client._print_result(result)
    elif args.tool:
        # Call specific tool
        if args.tool == "echo":
            if args.message is None:
                print("❌ Error: --message is required for echo tool")
                sys.exit(1)
            result = client.echo(args.message)
            client._print_result(result)
        else:
            print(f"❌ Error: Unknown tool: {args.tool}")
            sys.exit(1)
    elif args.resource:
        # Get specific resource
        result = client.get_resource(args.resource)
        client._print_result(result)
    elif args.prompt:
        # Call specific prompt
        prompt_args = {}
        if args.prompt_text:
            prompt_args["text"] = args.prompt_text
        result = client.call_prompt(args.prompt, prompt_args)
        client._print_result(result)
    else:
        # Run scenario
        client.run_test_scenario(scenario=args.scenario)


if __name__ == "__main__":
    main()

