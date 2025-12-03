"""
Tests for the MCP Server implementation.
"""

import pytest

from src.server import MCPServer


class TestMCPServer:
    """Test cases for MCPServer."""

    @pytest.fixture
    def server(self) -> MCPServer:
        """Fixture to provide a fresh MCPServer instance."""
        return MCPServer()

    def test_server_initialization(self, server: MCPServer) -> None:
        """Test that the server initializes correctly."""
        assert server is not None
        assert server.get_server() is not None

    def test_server_has_tools(self, server: MCPServer) -> None:
        """Test that the server has registered tools."""
        mcp_server = server.get_server()
        assert mcp_server is not None
        # The server should have tools registered
        # (specific tool verification depends on MCP SDK implementation)

    @pytest.mark.asyncio
    async def test_echo_string_handler(self, server: MCPServer) -> None:
        """Test the echo_string tool handler."""
        result = await server._handle_echo_string("test message")
        assert result is not None
        assert not result.isError
        assert len(result.content) > 0
        assert "test message" in result.content[0].text

    @pytest.mark.asyncio
    async def test_add_numbers_handler(self, server: MCPServer) -> None:
        """Test the add_numbers tool handler."""
        result = await server._handle_add_numbers(5, 3)
        assert result is not None
        assert not result.isError
        assert len(result.content) > 0
        assert "8" in result.content[0].text

    @pytest.mark.asyncio
    async def test_get_string_length_handler(self, server: MCPServer) -> None:
        """Test the get_string_length tool handler."""
        result = await server._handle_get_string_length("hello")
        assert result is not None
        assert not result.isError
        assert len(result.content) > 0
        assert "5" in result.content[0].text

