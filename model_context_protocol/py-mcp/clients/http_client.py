#!/usr/bin/env python
"""
HTTP Client for inspecting MCP Echo Server behavior

This script provides a simple HTTP client interface to interact with the MCP Echo Server
and inspect its responses. It demonstrates various tool usage patterns and validates responses.

Usage:
    python clients/http_client.py --server-type demo
    python clients/http_client.py --server-type echo
    python clients/http_client.py --tool echo_string --message "Hello World"
    python clients/http_client.py --tool add_numbers --args 5 3
"""

import json
import sys
import argparse
import os
from typing import Any, Dict, List
from pathlib import Path

# Fix encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class MCPEchoServerClient:
    """Client for interacting with MCP Echo Server via tool invocation"""

    def __init__(self, server_type: str = "demo"):
        """
        Initialize the MCP Echo Server Client

        Args:
            server_type: Type of server ('demo' or 'echo')
        """
        self.server_type = server_type
        self.tools = self._get_available_tools()

    def _get_available_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get available tools for the server type"""
        demo_tools = {
            "echo_string": {
                "description": "Echo a string back to the caller",
                "args": ["message"],
                "example": ["Hello, World!"],
            },
            "add_numbers": {
                "description": "Add two numbers together",
                "args": ["a", "b"],
                "example": [5, 3],
            },
            "get_string_length": {
                "description": "Get the length of a string",
                "args": ["input"],
                "example": ["hello"],
            },
        }

        echo_tools = {
            "echo": {
                "description": "Echo a string back to the caller",
                "args": ["message"],
                "example": ["Hello, World!"],
            },
        }

        return demo_tools if self.server_type == "demo" else echo_tools

    def echo_string(self, message: str) -> Dict[str, Any]:
        """Echo a string (Demo Server)"""
        print(f"📤 Calling: echo_string")
        print(f"   Message: {message}")
        print()
        return {
            "tool": "echo_string",
            "args": {"message": message},
            "description": "Echo a string back to the caller",
        }

    def add_numbers(self, a: float, b: float) -> Dict[str, Any]:
        """Add two numbers (Demo Server)"""
        print(f"📤 Calling: add_numbers")
        print(f"   a: {a}")
        print(f"   b: {b}")
        print()
        return {
            "tool": "add_numbers",
            "args": {"a": a, "b": b},
            "description": "Add two numbers together",
        }

    def get_string_length(self, input_str: str) -> Dict[str, Any]:
        """Get string length (Demo Server)"""
        print(f"📤 Calling: get_string_length")
        print(f"   Input: {input_str}")
        print()
        return {
            "tool": "get_string_length",
            "args": {"input": input_str},
            "description": "Get the length of a string",
        }

    def echo(self, message: str) -> Dict[str, Any]:
        """Echo a string (Echo Server)"""
        print(f"📤 Calling: echo")
        print(f"   Message: {message}")
        print()
        return {
            "tool": "echo",
            "args": {"message": message},
            "description": "Echo a string back to the caller",
        }

    def list_tools(self):
        """List all available tools for the server"""
        print(f"🔧 Available tools for {self.server_type} server:")
        print()
        for tool_name, tool_info in self.tools.items():
            print(f"  ▪ {tool_name}")
            print(f"    Description: {tool_info['description']}")
            print(f"    Arguments: {', '.join(tool_info['args'])}")
            print(f"    Example: {tool_name}({', '.join(repr(arg) for arg in tool_info['example'])})")
            print()

    def run_test_scenario(self, scenario: str = "basic"):
        """Run predefined test scenarios"""
        print(f"🧪 Running test scenario: {scenario}")
        print("=" * 60)
        print()

        if self.server_type == "demo" and scenario == "basic":
            self._test_demo_basic()
        elif self.server_type == "demo" and scenario == "comprehensive":
            self._test_demo_comprehensive()
        elif self.server_type == "echo" and scenario == "basic":
            self._test_echo_basic()
        else:
            print(f"❌ Unknown scenario: {scenario}")

    def _test_demo_basic(self):
        """Basic test scenario for demo server"""
        print("Test 1: Echo String")
        print("-" * 40)
        result = self.echo_string("Hello, MCP!")
        self._print_result(result)

        print("\nTest 2: Add Numbers")
        print("-" * 40)
        result = self.add_numbers(5, 3)
        self._print_result(result)

        print("\nTest 3: String Length")
        print("-" * 40)
        result = self.get_string_length("MCP Echo Server")
        self._print_result(result)

    def _test_demo_comprehensive(self):
        """Comprehensive test scenario for demo server"""
        print("Test 1: Echo with Empty String")
        print("-" * 40)
        result = self.echo_string("")
        self._print_result(result)

        print("\nTest 2: Echo with Special Characters")
        print("-" * 40)
        result = self.echo_string("Hello\nWorld\t123!")
        self._print_result(result)

        print("\nTest 3: Add Positive Numbers")
        print("-" * 40)
        result = self.add_numbers(10, 5)
        self._print_result(result)

        print("\nTest 4: Add Negative Numbers")
        print("-" * 40)
        result = self.add_numbers(-5, -3)
        self._print_result(result)

        print("\nTest 5: Add Floats")
        print("-" * 40)
        result = self.add_numbers(3.5, 2.5)
        self._print_result(result)

        print("\nTest 6: String Length with Unicode")
        print("-" * 40)
        result = self.get_string_length("你好世界")
        self._print_result(result)

        print("\nTest 7: String Length with Long String")
        print("-" * 40)
        result = self.get_string_length("a" * 1000)
        self._print_result(result)

    def _test_echo_basic(self):
        """Basic test scenario for echo server"""
        print("Test 1: Echo String")
        print("-" * 40)
        result = self.echo("Hello, Echo Server!")
        self._print_result(result)

        print("\nTest 2: Echo with Special Characters")
        print("-" * 40)
        result = self.echo("Special: @#$%^&*()")
        self._print_result(result)

        print("\nTest 3: Echo with Unicode")
        print("-" * 40)
        result = self.echo("Unicode: 你好🎉")
        self._print_result(result)

    def _print_result(self, result: Dict[str, Any]):
        """Pretty print the result"""
        print("📥 Response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print()

    def generate_curl_examples(self):
        """Generate curl command examples for testing (informational)"""
        print("📋 Example curl commands (for reference):")
        print("=" * 60)
        print()

        if self.server_type == "demo":
            print("# Echo String Tool")
            print('curl -X POST http://localhost:5000/tools/echo_string \\')
            print('  -H "Content-Type: application/json" \\')
            print('  -d \'{"message": "Hello, World!"}\' | jq')
            print()

            print("# Add Numbers Tool")
            print('curl -X POST http://localhost:5000/tools/add_numbers \\')
            print('  -H "Content-Type: application/json" \\')
            print('  -d \'{"a": 5, "b": 3}\' | jq')
            print()

            print("# Get String Length Tool")
            print('curl -X POST http://localhost:5000/tools/get_string_length \\')
            print('  -H "Content-Type: application/json" \\')
            print('  -d \'{"input": "hello"}\' | jq')
            print()
        else:
            print("# Echo Tool")
            print('curl -X POST http://localhost:5000/tools/echo \\')
            print('  -H "Content-Type: application/json" \\')
            print('  -d \'{"message": "Hello, Echo Server!"}\' | jq')
            print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="HTTP Client for MCP Echo Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clients/http_client.py --server-type demo
  python clients/http_client.py --server-type echo
  python clients/http_client.py --list-tools
  python clients/http_client.py --scenario comprehensive
  python clients/http_client.py --tool echo_string --message "Hello World"
  python clients/http_client.py --tool add_numbers --args 5 3
        """,
    )

    parser.add_argument(
        "--server-type",
        choices=["demo", "echo"],
        default="demo",
        help="Type of server to connect to (default: demo)",
    )

    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List all available tools for the server",
    )

    parser.add_argument(
        "--scenario",
        choices=["basic", "comprehensive"],
        default="basic",
        help="Run a predefined test scenario (default: basic)",
    )

    parser.add_argument(
        "--tool",
        help="Specific tool to test",
    )

    parser.add_argument(
        "--message",
        help="Message for echo tools",
    )

    parser.add_argument(
        "--args",
        nargs="+",
        type=float,
        help="Arguments for tools that take numeric input",
    )

    parser.add_argument(
        "--curl-examples",
        action="store_true",
        help="Show curl command examples",
    )

    args = parser.parse_args()

    # Create client
    client = MCPEchoServerClient(server_type=args.server_type)

    # Handle different commands
    if args.list_tools:
        client.list_tools()
    elif args.curl_examples:
        client.generate_curl_examples()
    elif args.tool:
        # Run specific tool
        if args.tool == "echo_string" or args.tool == "echo":
            if args.message is None:
                print("❌ Error: --message is required for echo tools")
                sys.exit(1)
            if args.tool == "echo_string":
                client.echo_string(args.message)
            else:
                client.echo(args.message)
        elif args.tool == "add_numbers":
            if args.args is None or len(args.args) != 2:
                print("❌ Error: --args requires exactly 2 numbers")
                sys.exit(1)
            client.add_numbers(args.args[0], args.args[1])
        elif args.tool == "get_string_length":
            if args.message is None:
                print("❌ Error: --message is required")
                sys.exit(1)
            client.get_string_length(args.message)
        else:
            print(f"❌ Error: Unknown tool: {args.tool}")
            sys.exit(1)
    else:
        # Run scenario
        client.run_test_scenario(scenario=args.scenario)


if __name__ == "__main__":
    main()

