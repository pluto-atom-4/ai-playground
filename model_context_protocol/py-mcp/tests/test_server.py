"""
Tests for the MCP Server implementation using FastMCP (decorator API).
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from server import echo_string, add_numbers, get_string_length


class TestEchoStringTool:
    """Test cases for the echo_string tool."""

    def test_echo_string_simple(self):
        """Test echoing a simple string."""
        result = echo_string("test message")

        assert result is not None
        assert isinstance(result, dict)
        assert not result["isError"]
        assert len(result["content"]) > 0
        assert result["content"][0].text == "test message"

    def test_echo_string_empty(self):
        """Test echoing an empty string."""
        result = echo_string("")

        assert not result["isError"]
        assert result["content"][0].text == ""

    def test_echo_string_special_chars(self):
        """Test echoing with special characters."""
        test_input = "Hello\nWorld\t123!"
        result = echo_string(test_input)

        assert not result["isError"]
        assert result["content"][0].text == test_input

    def test_echo_string_long_message(self):
        """Test echoing a long string."""
        long_msg = "x" * 5000
        result = echo_string(long_msg)

        assert not result["isError"]
        assert result["content"][0].text == long_msg


class TestAddNumbersTool:
    """Test cases for the add_numbers tool."""

    def test_add_positive_integers(self):
        """Test adding two positive integers."""
        result = add_numbers(5, 3)

        assert result is not None
        assert not result["isError"]
        assert len(result["content"]) > 0
        assert result["content"][0].text == "8"

    def test_add_negative_numbers(self):
        """Test adding negative numbers."""
        result = add_numbers(-5, -3)

        assert not result["isError"]
        assert result["content"][0].text == "-8"

    def test_add_mixed_signs(self):
        """Test adding numbers with different signs."""
        result = add_numbers(10, -5)

        assert not result["isError"]
        assert result["content"][0].text == "5"

    def test_add_floats(self):
        """Test adding floating point numbers."""
        result = add_numbers(3.5, 2.5)

        assert not result["isError"]
        assert result["content"][0].text == "6.0"

    def test_add_zero(self):
        """Test adding zero."""
        result = add_numbers(0, 5)

        assert not result["isError"]
        assert result["content"][0].text == "5"

    def test_add_decimal_precision(self):
        """Test adding numbers with decimal precision."""
        result = add_numbers(0.1, 0.2)

        assert not result["isError"]
        # Result should be approximately 0.3
        result_float = float(result["content"][0].text)
        assert abs(result_float - 0.3) < 0.0001


class TestGetStringLengthTool:
    """Test cases for the get_string_length tool."""

    def test_length_simple_string(self):
        """Test length of a simple string."""
        result = get_string_length("hello")

        assert result is not None
        assert not result["isError"]
        assert len(result["content"]) > 0
        assert result["content"][0].text == "5"

    def test_length_empty_string(self):
        """Test length of an empty string."""
        result = get_string_length("")

        assert not result["isError"]
        assert result["content"][0].text == "0"

    def test_length_unicode_string(self):
        """Test length of unicode string."""
        result = get_string_length("你好世界")

        assert not result["isError"]
        assert result["content"][0].text == "4"

    def test_length_with_emoji(self):
        """Test length of string with emoji."""
        test_str = "Hello🎉"
        result = get_string_length(test_str)

        assert not result["isError"]
        # Emoji counts as 1 character in Python 3
        assert result["content"][0].text == str(len(test_str))

    def test_length_long_string(self):
        """Test length of a very long string."""
        long_str = "a" * 10000
        result = get_string_length(long_str)

        assert not result["isError"]
        assert result["content"][0].text == "10000"

    def test_length_with_newlines_and_tabs(self):
        """Test length counting newlines and tabs."""
        test_str = "line1\nline2\tcolumn"
        result = get_string_length(test_str)

        assert not result["isError"]
        assert result["content"][0].text == str(len(test_str))


class TestMCPServerIntegration:
    """Integration tests for the MCP server tools."""

    def test_response_structure(self):
        """Test that all tools return proper MCP response structure."""
        tools_to_test = [
            (echo_string, ["test"]),
            (add_numbers, [5, 3]),
            (get_string_length, ["test"]),
        ]

        for tool, args in tools_to_test:
            result = tool(*args)

            # Verify response structure
            assert isinstance(result, dict), f"{tool.__name__} should return dict"
            assert "content" in result, f"{tool.__name__} should have 'content' key"
            assert "isError" in result, f"{tool.__name__} should have 'isError' key"
            assert isinstance(result["content"], list), f"{tool.__name__} content should be a list"
            assert len(result["content"]) > 0, f"{tool.__name__} content should not be empty"
            assert hasattr(result["content"][0], "text"), f"{tool.__name__} content should have 'text' attribute"

    def test_no_errors_in_normal_operation(self):
        """Test that no errors are returned in normal operation."""
        results = [
            echo_string("normal operation"),
            add_numbers(1, 1),
            get_string_length("test"),
        ]

        for result in results:
            assert result["isError"] is False, "Tools should not report errors in normal operation"

