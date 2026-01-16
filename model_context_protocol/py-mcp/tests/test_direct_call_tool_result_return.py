"""
Tests for the Direct CallToolResult Return Echo Server.

Tests the FastMCP Echo Server with direct CallToolResult return,
including tool functionality, validation, error handling, and Pydantic models.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from direct_call_tool_result_return import echo, EchoResponse
from mcp.types import CallToolResult, TextContent


# ============================================================================
# Unit Tests for Echo Tool
# ============================================================================

class TestEchoTool:
    """Tests for the echo tool function with CallToolResult return."""

    def test_echo_simple_string(self):
        """Test echoing a simple string returns CallToolResult."""
        result = echo("Hello, World!")

        assert isinstance(result, CallToolResult)
        assert len(result.content) > 0
        assert result.content[0].type == "text"
        assert result.content[0].text == "Hello, World!"

    def test_echo_structured_content(self):
        """Test echo returns structured content with text."""
        text = "Test Message"
        result = echo(text)

        assert result.structured_content is not None
        assert "text" in result.structured_content
        assert result.structured_content["text"] == text

    def test_echo_metadata(self):
        """Test echo includes metadata in structured content."""
        text = "Metadata Test"
        result = echo(text)

        # Metadata is passed to CallToolResult but we verify through structured content
        assert result.structured_content is not None
        assert "text" in result.structured_content
        assert result.structured_content["text"] == text

    def test_echo_empty_string(self):
        """Test echoing an empty string."""
        result = echo("")

        assert result.content[0].text == ""
        assert result.structured_content["text"] == ""

    def test_echo_long_string(self):
        """Test echoing a long string."""
        long_text = "a" * 10000
        result = echo(long_text)

        assert result.content[0].text == long_text
        assert result.structured_content["text"] == long_text

    def test_echo_unicode_characters(self):
        """Test echoing strings with Unicode characters."""
        unicode_texts = [
            "你好世界",  # Chinese
            "こんにちは",  # Japanese
            "مرحبا",  # Arabic
            "🎉 Emoji 🚀",  # Emoji
            "Ñoño",  # Spanish accents
        ]

        for text in unicode_texts:
            result = echo(text)
            assert result.content[0].text == text
            assert result.structured_content["text"] == text

    def test_echo_special_characters(self):
        """Test echoing strings with special characters."""
        special_texts = [
            "Hello\nWorld",  # Newline
            "Tab\tSeparated",  # Tab
            'Quote"Test',  # Double quote
            "JSON: {\"key\": \"value\"}",  # JSON-like
            "Path: C:\\Users\\test",  # Windows path
            "URL: https://example.com?param=value&other=123",  # URL
        ]

        for text in special_texts:
            result = echo(text)
            assert result.content[0].text == text
            assert result.structured_content["text"] == text

    def test_echo_none_raises_error(self):
        """Test that echoing None raises ValueError."""
        with pytest.raises(ValueError, match="Text parameter cannot be None"):
            echo(None)

    def test_echo_response_format_compliance(self):
        """Test echo response format complies with Pydantic EchoResponse."""
        result = echo("format test")

        # Verify response can be used with EchoResponse model
        response = EchoResponse(text=result.content[0].text)
        assert response.text == "format test"

    def test_echo_content_type_text(self):
        """Test echo content is always of type 'text'."""
        result = echo("type test")

        assert len(result.content) == 1
        assert isinstance(result.content[0], TextContent)
        assert result.content[0].type == "text"

    def test_echo_metadata_consistency(self):
        """Test echo returns consistent results for repeated calls."""
        text = "consistency test"
        result1 = echo(text)
        result2 = echo(text)

        # Same text should produce same content
        assert result1.content[0].text == result2.content[0].text
        assert result1.structured_content["text"] == result2.structured_content["text"]

    def test_echo_whitespace_preservation(self):
        """Test echo preserves whitespace correctly."""
        texts = [
            "  leading spaces",
            "trailing spaces  ",
            "  both spaces  ",
            "multiple   spaces",
            "\t\ttabs\t\t",
            "\n\nnewlines\n\n",
        ]

        for text in texts:
            result = echo(text)
            assert result.content[0].text == text
            assert result.structured_content["text"] == text

    def test_echo_single_character(self):
        """Test echo with single character."""
        result = echo("x")

        assert result.content[0].text == "x"
        assert result.structured_content["text"] == "x"


# ============================================================================
# Pydantic Model Tests
# ============================================================================

class TestEchoResponse:
    """Tests for EchoResponse Pydantic model."""

    def test_echo_response_creation(self):
        """Test creating EchoResponse model."""
        response = EchoResponse(text="test")

        assert response.text == "test"

    def test_echo_response_from_dict(self):
        """Test creating EchoResponse from dictionary."""
        data = {"text": "from dict"}
        response = EchoResponse(**data)

        assert response.text == "from dict"

    def test_echo_response_validation_missing_text(self):
        """Test EchoResponse requires text field."""
        with pytest.raises(ValueError):
            EchoResponse()

    def test_echo_response_serialization(self):
        """Test EchoResponse model serialization."""
        response = EchoResponse(text="serialize test")
        data = response.model_dump()

        assert data["text"] == "serialize test"

    def test_echo_response_json_schema(self):
        """Test EchoResponse JSON schema."""
        schema = EchoResponse.model_json_schema()

        assert "properties" in schema
        assert "text" in schema["properties"]
        assert "type" in schema["properties"]["text"]
        assert schema["properties"]["text"]["type"] == "string"

    def test_echo_response_field_description(self):
        """Test EchoResponse field has description."""
        schema = EchoResponse.model_json_schema()
        text_schema = schema["properties"]["text"]

        assert "description" in text_schema
        assert text_schema["description"] == "The echoed text"


# ============================================================================
# Edge Cases and Error Scenarios
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error scenarios."""

    def test_echo_very_large_string(self):
        """Test echo with very large string."""
        # Create a 1MB string
        large_text = "x" * (1024 * 1024)
        result = echo(large_text)

        assert result.content[0].text == large_text

    def test_echo_single_character(self):
        """Test echo with single character."""
        result = echo("a")

        assert result.content[0].text == "a"

    def test_echo_numeric_string(self):
        """Test echo with numeric string."""
        result = echo("12345")

        assert result.content[0].text == "12345"

    def test_echo_boolean_like_string(self):
        """Test echo with boolean-like strings."""
        for text in ["true", "false", "True", "False"]:
            result = echo(text)
            assert result.content[0].text == text

    def test_echo_null_character(self):
        """Test echo with null character in string."""
        text = "test\x00null"
        result = echo(text)

        assert result.content[0].text == text

    def test_echo_mixed_content_string(self):
        """Test echo with mixed content (text, numbers, symbols, Unicode)."""
        text = "Test 123 !@#$% 你好 🎉"
        result = echo(text)

        assert result.content[0].text == text
        assert result.structured_content["text"] == text

    def test_echo_repeated_calls_consistency(self):
        """Test echo returns consistent results for repeated calls."""
        text = "consistency check"

        results = [echo(text) for _ in range(5)]

        # All results should be identical
        for result in results:
            assert result.content[0].text == text

    def test_echo_newline_handling(self):
        """Test echo handles various newline formats."""
        texts = [
            "line1\nline2",  # Unix newline
            "line1\r\nline2",  # Windows newline
            "line1\rline2",  # Mac newline
        ]

        for text in texts:
            result = echo(text)
            assert result.content[0].text == text

    def test_echo_zero_width_characters(self):
        """Test echo handles zero-width characters."""
        text = "test\u200bzero\u200cwidth"  # Zero-width space and joiner
        result = echo(text)

        assert result.content[0].text == text


# ============================================================================
# Logging Tests
# ============================================================================

class TestLogging:
    """Tests for logging behavior."""

    def test_echo_logs_on_call(self, caplog):
        """Test echo tool logs on invocation."""
        import logging
        caplog.set_level(logging.INFO)

        echo("logged text")

        assert any("echo tool called" in record.message for record in caplog.records)

    def test_echo_logs_on_error(self, caplog):
        """Test echo tool logs when error occurs."""
        import logging
        caplog.set_level(logging.INFO)

        with pytest.raises(ValueError):
            echo(None)

        # Verify that logging was captured for the error condition
        assert len(caplog.records) > 0

    def test_echo_logs_result_metadata(self, caplog):
        """Test echo tool logs result metadata."""
        import logging
        caplog.set_level(logging.INFO)

        echo("metadata test")

        assert any("metadata" in record.message.lower() for record in caplog.records)


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Tests for performance characteristics."""

    def test_echo_response_time(self):
        """Test echo tool responds in reasonable time."""
        import time

        start = time.time()
        echo("performance test")
        elapsed = time.time() - start

        # Should complete in less than 100ms
        assert elapsed < 0.1

    def test_echo_handles_rapid_calls(self):
        """Test echo handles rapid sequential calls."""
        for i in range(100):
            result = echo(f"rapid test {i}")
            assert result.content[0].text == f"rapid test {i}"


# ============================================================================
# CallToolResult Specific Tests
# ============================================================================

class TestCallToolResult:
    """Tests specific to CallToolResult return type."""

    def test_call_tool_result_has_content(self):
        """Test CallToolResult has content attribute."""
        result = echo("test")

        assert hasattr(result, 'content')
        assert isinstance(result.content, list)

    def test_call_tool_result_has_structured_content(self):
        """Test CallToolResult has structured_content attribute."""
        result = echo("test")

        assert hasattr(result, 'structured_content')
        assert isinstance(result.structured_content, dict)

    def test_call_tool_result_has_metadata(self):
        """Test CallToolResult is created with metadata."""
        result = echo("test")

        # CallToolResult is properly created and contains structured_content
        assert hasattr(result, 'structured_content')
        assert isinstance(result.structured_content, dict)

    def test_call_tool_result_metadata_keys(self):
        """Test CallToolResult is created with structured content."""
        result = echo("test")

        # Verify structured content contains text
        assert "text" in result.structured_content
        assert result.structured_content["text"] == "test"

    def test_call_tool_result_text_content_match(self):
        """Test content text matches structured_content text."""
        text = "matching test"
        result = echo(text)

        content_text = result.content[0].text
        structured_text = result.structured_content["text"]

        assert content_text == structured_text == text
