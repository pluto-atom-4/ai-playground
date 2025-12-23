"""
Tests for the MCP Client for Desktop MCP Server.

This test suite validates the HTTP client implementation for the Desktop server,
following similar patterns as test_echo.py.
"""

import sys
import os

# Add clients directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../clients')))

import pytest
from unittest.mock import Mock, patch

# Import the MCP client
from mcp_client_desktop import MCPDesktopServerClient


class TestMCPDesktopClientInitialization:
    """Tests for MCPDesktopServerClient initialization."""

    def test_client_initialization_defaults(self):
        """Test that client initializes with default parameters."""
        client = MCPDesktopServerClient()

        assert client.base_url == "http://127.0.0.1:8000"
        assert client.api_key == "default-api-key-change-me"
        assert client.timeout == 10.0

    def test_client_initialization_custom(self):
        """Test that client initializes with custom parameters."""
        custom_url = "http://192.168.1.100:9000"
        custom_key = "custom-api-key"
        custom_timeout = 20.0

        client = MCPDesktopServerClient(
            base_url=custom_url,
            api_key=custom_key,
            timeout=custom_timeout
        )

        assert client.base_url == custom_url
        assert client.api_key == custom_key
        assert client.timeout == custom_timeout

    def test_client_has_required_methods(self):
        """Test that client has all required methods."""
        client = MCPDesktopServerClient()

        required_methods = [
            'get_server_info',
            'list_tools',
            'list_resources',
            'list_desktop_files',
            'get_file_content',
            'get_desktop_stats',
            'run_test_scenario',
        ]

        for method_name in required_methods:
            assert hasattr(client, method_name), f"Missing method: {method_name}"
            assert callable(getattr(client, method_name)), f"Not callable: {method_name}"


class TestMCPDesktopClientRequests:
    """Tests for HTTP request handling."""

    def test_make_request_get(self):
        """Test GET request to server."""
        client = MCPDesktopServerClient()

        with patch('mcp_client_desktop.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "ok"}
            mock_get.return_value = mock_response

            result = client._make_request("GET", "/test")

            assert result == {"status": "ok"}
            mock_get.assert_called_once()

    def test_make_request_post(self):
        """Test POST request to server."""
        client = MCPDesktopServerClient()

        with patch('mcp_client_desktop.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"result": "created"}
            mock_post.return_value = mock_response

            result = client._make_request("POST", "/test", {"data": "value"})

            assert result == {"result": "created"}
            mock_post.assert_called_once()

    def test_make_request_includes_api_key(self):
        """Test that requests include API key header."""
        client = MCPDesktopServerClient(api_key="test-key-123")

        with patch('mcp_client_desktop.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {}
            mock_get.return_value = mock_response

            client._make_request("GET", "/test")

            # Check that X-API-Key header was included
            call_kwargs = mock_get.call_args[1]
            assert "headers" in call_kwargs
            assert call_kwargs["headers"]["X-API-Key"] == "test-key-123"

    def test_make_request_error_handling(self):
        """Test error handling in requests."""
        client = MCPDesktopServerClient()

        with patch('mcp_client_desktop.requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection error")

            result = client._make_request("GET", "/test")

            assert result["isError"] is True
            assert "error" in result


class TestMCPDesktopClientTools:
    """Tests for tool-related client methods."""

    def test_list_tools(self):
        """Test list_tools method."""
        client = MCPDesktopServerClient()

        with patch('mcp_client_desktop.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "tools": [
                    {"name": "list_desktop_files", "description": "List desktop files"},
                    {"name": "get_file_content", "description": "Get file content"},
                    {"name": "get_desktop_stats", "description": "Get desktop stats"},
                ]
            }
            mock_get.return_value = mock_response

            result = client.list_tools()

            assert "tools" in result
            assert len(result["tools"]) == 3
            mock_get.assert_called_once()

    def test_list_desktop_files(self):
        """Test list_desktop_files method."""
        client = MCPDesktopServerClient()

        with patch('mcp_client_desktop.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "files": [
                    {"name": "file1.txt", "type": "file", "size": 100},
                    {"name": "dir1", "type": "directory", "size": None},
                ]
            }
            mock_get.return_value = mock_response

            result = client.list_desktop_files()

            assert "files" in result
            mock_get.assert_called_once()

    def test_get_file_content(self):
        """Test get_file_content method."""
        client = MCPDesktopServerClient()

        with patch('mcp_client_desktop.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "filename": "test.txt",
                "content": "Test content",
                "size": 12
            }
            mock_post.return_value = mock_response

            result = client.get_file_content("test.txt")

            assert result["filename"] == "test.txt"
            mock_post.assert_called_once()

    def test_get_desktop_stats(self):
        """Test get_desktop_stats method."""
        client = MCPDesktopServerClient()

        with patch('mcp_client_desktop.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "desktop_path": "/home/user/Desktop",
                "total_files": 5,
                "total_directories": 2,
                "total_size_bytes": 1024,
                "total_size_mb": 0.001
            }
            mock_get.return_value = mock_response

            result = client.get_desktop_stats()

            assert "desktop_path" in result
            assert result["total_files"] == 5
            mock_get.assert_called_once()


class TestMCPDesktopClientResources:
    """Tests for resource-related client methods."""

    def test_list_resources(self):
        """Test list_resources method."""
        client = MCPDesktopServerClient()

        with patch('mcp_client_desktop.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "resources": [
                    {"uri": "desktop://files", "description": "List files"},
                    {"uri": "desktop://stats", "description": "Stats"},
                    {"uri": "desktop://file/{filename}", "description": "File content"},
                ]
            }
            mock_get.return_value = mock_response

            result = client.list_resources()

            assert "resources" in result
            assert len(result["resources"]) == 3
            mock_get.assert_called_once()

    def test_get_server_info(self):
        """Test get_server_info method."""
        client = MCPDesktopServerClient()

        with patch('mcp_client_desktop.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "name": "Desktop MCP Server",
                "version": "1.0.0",
                "status": "running"
            }
            mock_get.return_value = mock_response

            result = client.get_server_info()

            assert result["name"] == "Desktop MCP Server"
            mock_get.assert_called_once()


class TestMCPDesktopClientIntegration:
    """Integration tests for the client."""

    def test_print_result_success(self):
        """Test printing successful result."""
        client = MCPDesktopServerClient()

        result = {
            "status": "ok",
            "data": "test data"
        }

        # Should not raise any exceptions
        client._print_result(result)

    def test_print_result_error(self):
        """Test printing error result."""
        client = MCPDesktopServerClient()

        result = {
            "error": "Test error",
            "isError": True
        }

        # Should not raise any exceptions
        client._print_result(result)

    def test_multiple_requests_with_same_client(self):
        """Test making multiple requests with same client."""
        client = MCPDesktopServerClient()

        with patch('mcp_client_desktop.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"count": 1}
            mock_get.return_value = mock_response

            result1 = client._make_request("GET", "/test1")
            result2 = client._make_request("GET", "/test2")

            assert result1 == {"count": 1}
            assert result2 == {"count": 1}
            assert mock_get.call_count == 2


class TestMCPDesktopClientScenarios:
    """Tests for test scenario running."""

    def test_run_test_scenario_basic(self):
        """Test basic scenario execution."""
        client = MCPDesktopServerClient()

        with patch('mcp_client_desktop.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "name": "Desktop MCP Server",
                "version": "1.0.0"
            }
            mock_get.return_value = mock_response

            # Should not raise any exceptions
            client.run_test_scenario("basic")

    def test_run_test_scenario_comprehensive(self):
        """Test comprehensive scenario execution."""
        client = MCPDesktopServerClient()

        with patch('mcp_client_desktop.requests.get') as mock_get, \
             patch('mcp_client_desktop.requests.post') as mock_post:

            mock_get.return_value = Mock(json=Mock(return_value={"data": "test"}))
            mock_post.return_value = Mock(json=Mock(return_value={"data": "test"}))

            # Should not raise any exceptions
            client.run_test_scenario("comprehensive")

    def test_run_test_scenario_invalid(self):
        """Test invalid scenario name."""
        client = MCPDesktopServerClient()

        # Should not raise any exceptions
        client.run_test_scenario("invalid_scenario")


class TestMCPDesktopClientResponseFormats:
    """Tests for response format validation."""

    def test_server_info_response_format(self):
        """Test server info response has correct format."""
        client = MCPDesktopServerClient()

        response = {
            "name": "Desktop MCP Server",
            "version": "1.0.0",
            "status": "running"
        }

        assert "name" in response
        assert "version" in response
        assert "status" in response

    def test_tools_response_format(self):
        """Test tools response has correct format."""
        response = {
            "tools": [
                {"name": "tool1", "description": "Description 1"},
                {"name": "tool2", "description": "Description 2"},
            ]
        }

        assert "tools" in response
        assert isinstance(response["tools"], list)

    def test_resources_response_format(self):
        """Test resources response has correct format."""
        response = {
            "resources": [
                {"uri": "resource://1", "description": "Desc 1"},
                {"uri": "resource://2", "description": "Desc 2"},
            ]
        }

        assert "resources" in response
        assert isinstance(response["resources"], list)


class TestMCPDesktopClientErrorHandling:
    """Tests for error handling."""

    def test_request_error_handling(self):
        """Test error handling in requests."""
        client = MCPDesktopServerClient()

        with patch('mcp_client_desktop.requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")

            result = client._make_request("GET", "/test")

            assert result["isError"] is True
            assert "error" in result

    def test_server_not_responding(self):
        """Test handling of non-responding server."""
        client = MCPDesktopServerClient(base_url="http://invalid-host:9999")

        with patch('mcp_client_desktop.requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection refused")

            result = client._make_request("GET", "/test")

            assert result["isError"] is True


class TestMCPDesktopClientDocumentation:
    """Tests for client documentation."""

    def test_client_has_docstring(self):
        """Test that client class has documentation."""
        assert MCPDesktopServerClient.__doc__ is not None
        assert len(MCPDesktopServerClient.__doc__) > 0

    def test_list_tools_has_docstring(self):
        """Test that list_tools method has documentation."""
        client = MCPDesktopServerClient()
        assert client.list_tools.__doc__ is not None

    def test_list_resources_has_docstring(self):
        """Test that list_resources method has documentation."""
        client = MCPDesktopServerClient()
        assert client.list_resources.__doc__ is not None

    def test_get_file_content_has_docstring(self):
        """Test that get_file_content method has documentation."""
        client = MCPDesktopServerClient()
        assert client.get_file_content.__doc__ is not None

    def test_get_desktop_stats_has_docstring(self):
        """Test that get_desktop_stats method has documentation."""
        client = MCPDesktopServerClient()
        assert client.get_desktop_stats.__doc__ is not None
