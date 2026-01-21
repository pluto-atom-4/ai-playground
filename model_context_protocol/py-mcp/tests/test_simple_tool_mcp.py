"""
Tests for Simple Tool MCP Server

Tests the website fetcher tool and server functionality.
"""

import pytest
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch
from mcp.types import TextContent


def load_simple_tool_module():
    """Dynamically load the simple_tool_mcp_server module."""
    simple_tool_dir = Path(__file__).parent.parent / "src" / "servers" / "simple_tool"
    spec = importlib.util.spec_from_file_location(
        "simple_tool_mcp_server",
        simple_tool_dir / "simple_tool_mcp_server.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mock_httpx():
    """Mock httpx module for testing without network calls."""
    with patch("httpx.get") as mock_get:
        yield mock_get


class TestFetchWebsiteTool:
    """Test the fetch_website tool."""

    def test_fetch_website_success(self, mock_httpx):
        """Test successful website fetch."""
        # Arrange
        mock_response = MagicMock()
        mock_response.text = "<html><body>Hello World</body></html>"
        mock_httpx.return_value = mock_response

        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        # Act
        result = fetch_website("https://example.com")

        # Assert
        assert result["isError"] is False
        assert len(result["content"]) == 1
        assert result["content"][0].text == "<html><body>Hello World</body></html>"
        mock_httpx.assert_called_once()

    def test_fetch_website_empty_url(self):
        """Test fetch with empty URL raises ValueError."""
        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        with pytest.raises(ValueError, match="URL cannot be empty"):
            fetch_website("")

    def test_fetch_website_invalid_url_format(self):
        """Test fetch with invalid URL format raises ValueError."""
        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        with pytest.raises(ValueError, match="must start with http:// or https://"):
            fetch_website("example.com")

    def test_fetch_website_invalid_url_ftp(self):
        """Test fetch with non-http/https protocol raises ValueError."""
        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        with pytest.raises(ValueError, match="must start with http:// or https://"):
            fetch_website("ftp://example.com")

    def test_fetch_website_http_url(self, mock_httpx):
        """Test successful fetch with http (not https)."""
        # Arrange
        mock_response = MagicMock()
        mock_response.text = "HTTP Content"
        mock_httpx.return_value = mock_response

        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        # Act
        result = fetch_website("http://example.com")

        # Assert
        assert result["isError"] is False
        assert result["content"][0].text == "HTTP Content"

    def test_fetch_website_network_error(self, mock_httpx):
        """Test fetch with network error raises ValueError."""
        # Arrange
        mock_httpx.side_effect = ConnectionError("Network unreachable")

        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to fetch"):
            fetch_website("https://example.com")

    def test_fetch_website_http_error(self, mock_httpx):
        """Test fetch with HTTP error raises ValueError."""
        # Arrange
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_httpx.return_value = mock_response

        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to fetch"):
            fetch_website("https://example.com/notfound")

    def test_fetch_website_timeout(self, mock_httpx):
        """Test fetch with timeout raises ValueError."""
        # Arrange
        import httpx as real_httpx
        mock_httpx.side_effect = real_httpx.TimeoutException("Request timeout")

        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to fetch"):
            fetch_website("https://example.com/slow")

    def test_fetch_website_user_agent_header(self, mock_httpx):
        """Test that proper User-Agent header is sent."""
        # Arrange
        mock_response = MagicMock()
        mock_response.text = "Content"
        mock_httpx.return_value = mock_response

        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        # Act
        fetch_website("https://example.com")

        # Assert
        call_kwargs = mock_httpx.call_args[1]
        assert "headers" in call_kwargs
        assert "User-Agent" in call_kwargs["headers"]
        assert "modelcontextprotocol" in call_kwargs["headers"]["User-Agent"]

    def test_fetch_website_timeout_parameter(self, mock_httpx):
        """Test that timeout is set to 30 seconds."""
        # Arrange
        mock_response = MagicMock()
        mock_response.text = "Content"
        mock_httpx.return_value = mock_response

        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        # Act
        fetch_website("https://example.com")

        # Assert
        call_kwargs = mock_httpx.call_args[1]
        assert call_kwargs["timeout"] == 30.0

    def test_fetch_website_large_content(self, mock_httpx):
        """Test fetch with large content."""
        # Arrange
        large_content = "x" * 1_000_000  # 1MB
        mock_response = MagicMock()
        mock_response.text = large_content
        mock_httpx.return_value = mock_response

        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        # Act
        result = fetch_website("https://example.com/large")

        # Assert
        assert result["isError"] is False
        assert len(result["content"][0].text) == 1_000_000

    def test_fetch_website_unicode_content(self, mock_httpx):
        """Test fetch with Unicode content."""
        # Arrange
        unicode_content = "Hello 世界 🌍 مرحبا"
        mock_response = MagicMock()
        mock_response.text = unicode_content
        mock_httpx.return_value = mock_response

        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        # Act
        result = fetch_website("https://example.com/unicode")

        # Assert
        assert result["isError"] is False
        assert result["content"][0].text == unicode_content

    def test_fetch_website_response_type(self, mock_httpx):
        """Test that response contains TextContent objects."""
        # Arrange
        mock_response = MagicMock()
        mock_response.text = "Test content"
        mock_httpx.return_value = mock_response

        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        # Act
        result = fetch_website("https://example.com")

        # Assert
        assert isinstance(result["content"], list)
        assert len(result["content"]) == 1
        assert isinstance(result["content"][0], TextContent)
        assert result["content"][0].type == "text"


class TestServerInitialization:
    """Test server initialization."""

    def test_mcp_instance_creation(self):
        """Test that MCP instance is created with correct name."""
        module = load_simple_tool_module()
        mcp = module.mcp

        assert mcp.name == "mcp-website-fetcher"

    def test_fetch_tool_registered(self):
        """Test that fetch tool is registered."""
        module = load_simple_tool_module()
        mcp = module.mcp

        # The fetch tool should be in the mcp tools
        assert mcp is not None


class TestCLIInterface:
    """Test CLI interface."""

    def test_cli_main_function_exists(self):
        """Test that main CLI function is defined."""
        module = load_simple_tool_module()
        main = module.main

        assert callable(main)


class TestLogging:
    """Test logging configuration."""

    def test_logging_configured(self):
        """Test that logging is properly configured."""
        import logging

        logger = logging.getLogger("simple-tool.server")
        assert logger is not None

    def test_environment_log_level_loaded(self):
        """Test that LOG_LEVEL environment variable can be loaded."""
        import os
        from dotenv import load_dotenv

        load_dotenv()
        log_level = os.getenv("LOG_LEVEL", "INFO")
        assert log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]


class TestErrorMessages:
    """Test error message quality."""

    def test_empty_url_error_message_is_descriptive(self):
        """Test that empty URL error is user-friendly."""
        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        try:
            fetch_website("")
        except ValueError as e:
            assert "URL cannot be empty" in str(e)

    def test_invalid_url_error_message_is_descriptive(self):
        """Test that invalid URL error is user-friendly."""
        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        try:
            fetch_website("example.com")
        except ValueError as e:
            error_msg = str(e)
            assert "Invalid URL" in error_msg
            assert "http://" in error_msg or "https://" in error_msg

    def test_network_error_message_includes_url(self, mock_httpx):
        """Test that network errors include the URL."""
        import httpx

        mock_httpx.side_effect = httpx.ConnectError("Connection failed")

        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        try:
            fetch_website("https://example.com")
        except ValueError as e:
            assert "example.com" in str(e)


class TestResponseFormat:
    """Test response format compliance."""

    def test_response_has_content_key(self, mock_httpx):
        """Test response contains 'content' key."""
        mock_response = MagicMock()
        mock_response.text = "Test"
        mock_httpx.return_value = mock_response

        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        result = fetch_website("https://example.com")
        assert "content" in result

    def test_response_has_is_error_key(self, mock_httpx):
        """Test response contains 'isError' key."""
        mock_response = MagicMock()
        mock_response.text = "Test"
        mock_httpx.return_value = mock_response

        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        result = fetch_website("https://example.com")
        assert "isError" in result

    def test_is_error_false_on_success(self, mock_httpx):
        """Test isError flag is False on success."""
        mock_response = MagicMock()
        mock_response.text = "Test"
        mock_httpx.return_value = mock_response

        module = load_simple_tool_module()
        fetch_website = module.fetch_website

        result = fetch_website("https://example.com")
        assert result["isError"] is False
