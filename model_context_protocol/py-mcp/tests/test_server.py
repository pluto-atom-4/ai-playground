"""
Tests for the MCP Server implementation using FastMCP (decorator API).
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from server import echo_string, add_numbers, get_string_length


class TestMCPServer:
    """Test cases for MCP server tools (FastMCP decorator API)."""

    def test_echo_string(self):
        result = echo_string("test message")
        assert result is not None
        assert not result["isError"]
        assert len(result["content"]) > 0
        assert "test message" in result["content"][0].text

    def test_add_numbers(self):
        result = add_numbers(5, 3)
        assert result is not None
        assert not result["isError"]
        assert len(result["content"]) > 0
        assert result["content"][0].text == "8"

    def test_get_string_length(self):
        result = get_string_length("hello")
        assert result is not None
        assert not result["isError"]
        assert len(result["content"]) > 0
        assert result["content"][0].text == "5"
