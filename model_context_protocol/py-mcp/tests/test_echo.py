"""
Tests for the Echo functionality of the MCP Server.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from echo import echo_tool, echo_resource, echo_template, echo_prompt


class TestEchoTool:
    """Tests for the echo_tool function."""

    def test_echo_simple_string(self):
        """Test echoing a simple string."""
        result = echo_tool("Hello, World!")

        assert "content" in result
        assert "isError" in result
        assert result["isError"] is False
        assert len(result["content"]) == 1
        assert result["content"][0]["type"] == "text"
        assert result["content"][0]["text"] == "Hello, World!"

    def test_echo_empty_string(self):
        """Test echoing an empty string."""
        result = echo_tool("")

        assert result["isError"] is False
        assert result["content"][0]["text"] == ""

    def test_echo_long_string(self):
        """Test echoing a long string."""
        long_message = "a" * 1000
        result = echo_tool(long_message)

        assert result["isError"] is False
        assert result["content"][0]["text"] == long_message

    def test_echo_special_characters(self):
        """Test echoing strings with special characters."""
        test_cases = [
            "Hello\nWorld",
            "Tab\tSeparated",
            'Quote"Test',
            "Unicode: 你好世界",
            "Emoji: 🎉🚀",
            "JSON: {\"key\": \"value\"}",
        ]

        for test_input in test_cases:
            result = echo_tool(test_input)
            assert result["isError"] is False
            assert result["content"][0]["text"] == test_input

    def test_echo_response_format(self):
        """Test that echo response has correct format."""
        result = echo_tool("test")

        # Verify response structure
        assert isinstance(result, dict)
        assert isinstance(result["content"], list)
        assert isinstance(result["isError"], bool)
        assert isinstance(result["content"][0], dict)
        assert "type" in result["content"][0]
        assert "text" in result["content"][0]


class TestEchoResource:
    """Tests for the echo_resource function."""

    def test_static_resource(self):
        """Test the static resource endpoint."""
        result = echo_resource()

        assert isinstance(result, str)
        assert result == "Echo Resource Content"


class TestEchoTemplate:
    """Tests for the echo_template function with template resources."""

    def test_echo_template_simple(self):
        """Test template resource with simple text."""
        result = echo_template("test")

        assert isinstance(result, str)
        assert result == "Echoed: test"

    def test_echo_template_with_special_chars(self):
        """Test template resource with special characters."""
        test_input = "Hello/World?param=value"
        result = echo_template(test_input)

        assert result == f"Echoed: {test_input}"

    def test_echo_template_unicode(self):
        """Test template resource with unicode characters."""
        test_input = "你好"
        result = echo_template(test_input)

        assert result == f"Echoed: {test_input}"


class TestEchoPrompt:
    """Tests for the echo_prompt function."""

    def test_prompt_simple(self):
        """Test prompt with simple text."""
        result = echo_prompt("test")

        assert isinstance(result, str)
        assert result == "Echo Prompt: test"

    def test_prompt_with_special_chars(self):
        """Test prompt with special characters."""
        test_input = "Create a test for {placeholder}"
        result = echo_prompt(test_input)

        assert result == f"Echo Prompt: {test_input}"


class TestEchoIntegration:
    """Integration tests for the Echo server components."""

    def test_echo_consistency(self):
        """Test that echoing returns consistent results."""
        test_message = "Consistency Test"

        result1 = echo_tool(test_message)
        result2 = echo_tool(test_message)

        assert result1["content"][0]["text"] == result2["content"][0]["text"]

    def test_multiple_echo_calls(self):
        """Test multiple echo calls with different inputs."""
        inputs = ["first", "second", "third"]

        for test_input in inputs:
            result = echo_tool(test_input)
            assert result["isError"] is False
            assert result["content"][0]["text"] == test_input

