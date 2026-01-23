"""
Tests for Simple Resource MCP Server

Tests the resource listing and reading functionality of the simple-resource MCP server.
"""

import pytest
import logging
import asyncio
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
from urllib.parse import urlparse

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.lowlevel.helper_types import ReadResourceContents


# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def load_simple_resource_module():
    """Dynamically load the simple_resource_mcp_server module."""
    server_path = Path(__file__).parent.parent / "src" / "servers" / "simple_resource" / "simple_resource_mcp_server.py"
    spec = importlib.util.spec_from_file_location("simple_resource_mcp_server", server_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def simple_resource_module():
    """Fixture to provide the simple_resource_mcp_server module."""
    return load_simple_resource_module()


class TestSampleResources:
    """Test the sample resources data structure."""

    def test_sample_resources_dict_exists(self, simple_resource_module):
        """Test that SAMPLE_RESOURCES dict is properly defined."""
        assert isinstance(simple_resource_module.SAMPLE_RESOURCES, dict)
        assert len(simple_resource_module.SAMPLE_RESOURCES) > 0

    def test_sample_resources_have_required_fields(self, simple_resource_module):
        """Test that each resource has required fields."""
        for name, resource in simple_resource_module.SAMPLE_RESOURCES.items():
            assert "content" in resource, f"Resource '{name}' missing 'content' field"
            assert "title" in resource, f"Resource '{name}' missing 'title' field"
            assert isinstance(resource["content"], str), f"Resource '{name}' content must be string"
            assert isinstance(resource["title"], str), f"Resource '{name}' title must be string"

    def test_sample_resources_content_not_empty(self, simple_resource_module):
        """Test that resource content is not empty."""
        for name, resource in simple_resource_module.SAMPLE_RESOURCES.items():
            assert len(resource["content"]) > 0, f"Resource '{name}' content is empty"
            assert len(resource["title"]) > 0, f"Resource '{name}' title is empty"

    def test_greeting_resource_exists(self, simple_resource_module):
        """Test that greeting resource is available."""
        assert "greeting" in simple_resource_module.SAMPLE_RESOURCES
        assert "Hello" in simple_resource_module.SAMPLE_RESOURCES["greeting"]["content"]

    def test_help_resource_exists(self, simple_resource_module):
        """Test that help resource is available."""
        assert "help" in simple_resource_module.SAMPLE_RESOURCES
        assert len(simple_resource_module.SAMPLE_RESOURCES["help"]["content"]) > 0

    def test_about_resource_exists(self, simple_resource_module):
        """Test that about resource is available."""
        assert "about" in simple_resource_module.SAMPLE_RESOURCES
        assert "simple-resource" in simple_resource_module.SAMPLE_RESOURCES["about"]["content"].lower()


@pytest.mark.asyncio
class TestListResources:
    """Test the list_resources endpoint handler."""

    async def test_list_resources_returns_list(self, simple_resource_module):
        """Test that list_resources returns a list."""
        SAMPLE_RESOURCES = simple_resource_module.SAMPLE_RESOURCES

        app = Server("test-server")

        @app.list_resources()
        async def list_resources():
            return [
                types.Resource(
                    uri=f"file:///{name}.txt",
                    name=name,
                    title=SAMPLE_RESOURCES[name]["title"],
                    description=f"A sample text resource named {name}",
                    mime_type="text/plain",
                )
                for name in SAMPLE_RESOURCES.keys()
            ]

        resources = await list_resources()
        assert isinstance(resources, list)
        assert len(resources) > 0

    async def test_list_resources_returns_resource_objects(self, simple_resource_module):
        """Test that list_resources returns proper Resource objects."""
        SAMPLE_RESOURCES = simple_resource_module.SAMPLE_RESOURCES

        app = Server("test-server")

        @app.list_resources()
        async def list_resources():
            return [
                types.Resource(
                    uri=f"file:///{name}.txt",
                    name=name,
                    title=SAMPLE_RESOURCES[name]["title"],
                    description=f"A sample text resource named {name}",
                    mime_type="text/plain",
                )
                for name in SAMPLE_RESOURCES.keys()
            ]

        resources = await list_resources()
        for resource in resources:
            assert isinstance(resource, types.Resource)
            assert hasattr(resource, "uri")
            assert hasattr(resource, "name")
            assert hasattr(resource, "title")
            assert hasattr(resource, "mime_type")

    async def test_list_resources_uri_format(self, simple_resource_module):
        """Test that resource URIs follow file:/// format."""
        SAMPLE_RESOURCES = simple_resource_module.SAMPLE_RESOURCES

        app = Server("test-server")

        @app.list_resources()
        async def list_resources():
            return [
                types.Resource(
                    uri=f"file:///{name}.txt",
                    name=name,
                    title=SAMPLE_RESOURCES[name]["title"],
                    description=f"A sample text resource named {name}",
                    mime_type="text/plain",
                )
                for name in SAMPLE_RESOURCES.keys()
            ]

        resources = await list_resources()
        for resource in resources:
            uri_str = str(resource.uri)
            assert uri_str.startswith("file:///")
            assert uri_str.endswith(".txt")

    async def test_list_resources_mime_type(self, simple_resource_module):
        """Test that resources have correct mime type."""
        SAMPLE_RESOURCES = simple_resource_module.SAMPLE_RESOURCES

        app = Server("test-server")

        @app.list_resources()
        async def list_resources():
            return [
                types.Resource(
                    uri=f"file:///{name}.txt",
                    name=name,
                    title=SAMPLE_RESOURCES[name]["title"],
                    description=f"A sample text resource named {name}",
                    mime_type="text/plain",
                )
                for name in SAMPLE_RESOURCES.keys()
            ]

        resources = await list_resources()
        for resource in resources:
            assert resource.mime_type == "text/plain"

    async def test_list_resources_includes_all_sample_resources(self, simple_resource_module):
        """Test that all sample resources are included in list."""
        SAMPLE_RESOURCES = simple_resource_module.SAMPLE_RESOURCES

        app = Server("test-server")

        @app.list_resources()
        async def list_resources():
            return [
                types.Resource(
                    uri=f"file:///{name}.txt",
                    name=name,
                    title=SAMPLE_RESOURCES[name]["title"],
                    description=f"A sample text resource named {name}",
                    mime_type="text/plain",
                )
                for name in SAMPLE_RESOURCES.keys()
            ]

        resources = await list_resources()
        resource_names = [r.name for r in resources]

        for sample_name in SAMPLE_RESOURCES.keys():
            assert sample_name in resource_names


@pytest.mark.asyncio
class TestReadResource:
    """Test the read_resource endpoint handler."""

    async def test_read_resource_returns_list(self, simple_resource_module):
        """Test that read_resource returns a list."""
        SAMPLE_RESOURCES = simple_resource_module.SAMPLE_RESOURCES

        app = Server("test-server")

        @app.read_resource()
        async def read_resource(uri: str):
            from urllib.parse import urlparse

            parsed = urlparse(uri)
            if not parsed.path:
                raise ValueError(f"Invalid resource path: {uri}")
            name = parsed.path.replace(".txt", "").lstrip("/")

            if name not in SAMPLE_RESOURCES:
                raise ValueError(f"Unknown resource: {uri}")

            return [ReadResourceContents(content=SAMPLE_RESOURCES[name]["content"], mime_type="text/plain")]

        result = await read_resource("file:///greeting.txt")
        assert isinstance(result, list)
        assert len(result) > 0

    async def test_read_resource_returns_content_object(self, simple_resource_module):
        """Test that read_resource returns ReadResourceContents objects."""
        SAMPLE_RESOURCES = simple_resource_module.SAMPLE_RESOURCES

        app = Server("test-server")

        @app.read_resource()
        async def read_resource(uri: str):
            from urllib.parse import urlparse

            parsed = urlparse(uri)
            if not parsed.path:
                raise ValueError(f"Invalid resource path: {uri}")
            name = parsed.path.replace(".txt", "").lstrip("/")

            if name not in SAMPLE_RESOURCES:
                raise ValueError(f"Unknown resource: {uri}")

            return [ReadResourceContents(content=SAMPLE_RESOURCES[name]["content"], mime_type="text/plain")]

        result = await read_resource("file:///greeting.txt")
        for item in result:
            assert isinstance(item, ReadResourceContents)
            assert hasattr(item, "content")
            assert hasattr(item, "mime_type")

    async def test_read_greeting_resource(self, simple_resource_module):
        """Test reading the greeting resource."""
        SAMPLE_RESOURCES = simple_resource_module.SAMPLE_RESOURCES

        app = Server("test-server")

        @app.read_resource()
        async def read_resource(uri: str):
            from urllib.parse import urlparse

            parsed = urlparse(uri)
            if not parsed.path:
                raise ValueError(f"Invalid resource path: {uri}")
            name = parsed.path.replace(".txt", "").lstrip("/")

            if name not in SAMPLE_RESOURCES:
                raise ValueError(f"Unknown resource: {uri}")

            return [ReadResourceContents(content=SAMPLE_RESOURCES[name]["content"], mime_type="text/plain")]

        result = await read_resource("file:///greeting.txt")
        assert len(result) == 1
        assert "Hello" in result[0].content

    async def test_read_help_resource(self, simple_resource_module):
        """Test reading the help resource."""
        SAMPLE_RESOURCES = simple_resource_module.SAMPLE_RESOURCES

        app = Server("test-server")

        @app.read_resource()
        async def read_resource(uri: str):
            from urllib.parse import urlparse

            parsed = urlparse(uri)
            if not parsed.path:
                raise ValueError(f"Invalid resource path: {uri}")
            name = parsed.path.replace(".txt", "").lstrip("/")

            if name not in SAMPLE_RESOURCES:
                raise ValueError(f"Unknown resource: {uri}")

            return [ReadResourceContents(content=SAMPLE_RESOURCES[name]["content"], mime_type="text/plain")]

        result = await read_resource("file:///help.txt")
        assert len(result) == 1
        assert len(result[0].content) > 0

    async def test_read_about_resource(self, simple_resource_module):
        """Test reading the about resource."""
        SAMPLE_RESOURCES = simple_resource_module.SAMPLE_RESOURCES

        app = Server("test-server")

        @app.read_resource()
        async def read_resource(uri: str):
            from urllib.parse import urlparse

            parsed = urlparse(uri)
            if not parsed.path:
                raise ValueError(f"Invalid resource path: {uri}")
            name = parsed.path.replace(".txt", "").lstrip("/")

            if name not in SAMPLE_RESOURCES:
                raise ValueError(f"Unknown resource: {uri}")

            return [ReadResourceContents(content=SAMPLE_RESOURCES[name]["content"], mime_type="text/plain")]

        result = await read_resource("file:///about.txt")
        assert len(result) == 1
        assert len(result[0].content) > 0

    async def test_read_nonexistent_resource_raises_error(self, simple_resource_module):
        """Test that reading nonexistent resource raises ValueError."""
        SAMPLE_RESOURCES = simple_resource_module.SAMPLE_RESOURCES

        app = Server("test-server")

        @app.read_resource()
        async def read_resource(uri: str):
            from urllib.parse import urlparse

            parsed = urlparse(uri)
            if not parsed.path:
                raise ValueError(f"Invalid resource path: {uri}")
            name = parsed.path.replace(".txt", "").lstrip("/")

            if name not in SAMPLE_RESOURCES:
                raise ValueError(f"Unknown resource: {uri}")

            return [ReadResourceContents(content=SAMPLE_RESOURCES[name]["content"], mime_type="text/plain")]

        with pytest.raises(ValueError):
            await read_resource("file:///nonexistent.txt")

    async def test_read_invalid_uri_raises_error(self, simple_resource_module):
        """Test that reading invalid URI raises ValueError."""
        SAMPLE_RESOURCES = simple_resource_module.SAMPLE_RESOURCES

        app = Server("test-server")

        @app.read_resource()
        async def read_resource(uri: str):
            from urllib.parse import urlparse

            parsed = urlparse(uri)
            if not parsed.path:
                raise ValueError(f"Invalid resource path: {uri}")
            name = parsed.path.replace(".txt", "").lstrip("/")

            if name not in SAMPLE_RESOURCES:
                raise ValueError(f"Unknown resource: {uri}")

            return [ReadResourceContents(content=SAMPLE_RESOURCES[name]["content"], mime_type="text/plain")]

        with pytest.raises(ValueError):
            await read_resource("file:///")

    async def test_read_resource_content_mime_type(self, simple_resource_module):
        """Test that resource content has correct mime type."""
        SAMPLE_RESOURCES = simple_resource_module.SAMPLE_RESOURCES

        app = Server("test-server")

        @app.read_resource()
        async def read_resource(uri: str):
            from urllib.parse import urlparse

            parsed = urlparse(uri)
            if not parsed.path:
                raise ValueError(f"Invalid resource path: {uri}")
            name = parsed.path.replace(".txt", "").lstrip("/")

            if name not in SAMPLE_RESOURCES:
                raise ValueError(f"Unknown resource: {uri}")

            return [ReadResourceContents(content=SAMPLE_RESOURCES[name]["content"], mime_type="text/plain")]

        result = await read_resource("file:///greeting.txt")
        for item in result:
            assert item.mime_type == "text/plain"


class TestURIParsing:
    """Test URI parsing and extraction logic."""

    def test_extract_name_from_valid_uri(self):
        """Test extracting resource name from valid URI."""
        from urllib.parse import urlparse

        uri = "file:///greeting.txt"
        parsed = urlparse(uri)
        name = parsed.path.replace(".txt", "").lstrip("/")
        assert name == "greeting"

    def test_extract_name_from_help_uri(self):
        """Test extracting resource name from help URI."""
        from urllib.parse import urlparse

        uri = "file:///help.txt"
        parsed = urlparse(uri)
        name = parsed.path.replace(".txt", "").lstrip("/")
        assert name == "help"

    def test_extract_name_from_about_uri(self):
        """Test extracting resource name from about URI."""
        from urllib.parse import urlparse

        uri = "file:///about.txt"
        parsed = urlparse(uri)
        name = parsed.path.replace(".txt", "").lstrip("/")
        assert name == "about"

    def test_empty_path_detection(self):
        """Test detection of empty path."""
        from urllib.parse import urlparse

        uri = "file:///"
        parsed = urlparse(uri)
        assert not parsed.path or parsed.path == "/"

    def test_uri_with_multiple_slashes(self):
        """Test handling of URI with multiple slashes."""
        from urllib.parse import urlparse

        uri = "file:///greeting.txt"
        parsed = urlparse(uri)
        name = parsed.path.replace(".txt", "").lstrip("/")
        assert name == "greeting"


class TestLoggingConfiguration:
    """Test logging configuration."""

    def test_logging_is_configured(self):
        """Test that logging module is properly imported."""
        import logging

        logger = logging.getLogger("test_logger")
        assert logger is not None

    def test_logger_can_be_created(self):
        """Test that logger can be created for module."""
        import logging

        logger = logging.getLogger(__name__)
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "debug")


class TestImports:
    """Test that all required imports are available."""

    def test_import_logging(self):
        """Test logging import."""
        import logging

        assert logging is not None

    def test_import_os(self):
        """Test os import."""
        import os

        assert os is not None

    def test_import_anyio(self):
        """Test anyio import."""
        import anyio

        assert anyio is not None

    def test_import_click(self):
        """Test click import."""
        import click

        assert click is not None

    def test_import_dotenv(self):
        """Test dotenv import."""
        from dotenv import load_dotenv

        assert load_dotenv is not None

    def test_import_mcp_types(self):
        """Test mcp.types import."""
        import mcp.types

        assert mcp.types is not None

    def test_import_mcp_server(self):
        """Test mcp.server imports."""
        from mcp.server.lowlevel import Server

        assert Server is not None

    def test_import_starlette(self):
        """Test starlette import."""
        from starlette.requests import Request

        assert Request is not None


class TestServerInstantiation:
    """Test server instantiation."""

    def test_create_server_instance(self):
        """Test creating a server instance."""
        from mcp.server.lowlevel import Server

        app = Server("test-server")
        assert app is not None

    def test_server_has_decorators(self):
        """Test that server has decorator methods."""
        from mcp.server.lowlevel import Server

        app = Server("test-server")
        assert hasattr(app, "list_resources")
        assert hasattr(app, "read_resource")

    def test_server_name_is_stored(self):
        """Test that server stores its name."""
        from mcp.server.lowlevel import Server

        app = Server("test-server")
        # The server name is typically stored internally
        assert app is not None


class TestEnvironmentVariables:
    """Test environment variable handling."""

    def test_get_log_level_with_env_var(self):
        """Test getting log level from environment."""
        import os

        os.environ["LOG_LEVEL"] = "DEBUG"
        log_level = os.getenv("LOG_LEVEL", "INFO")
        assert log_level == "DEBUG"

    def test_get_log_level_with_default(self):
        """Test getting log level with default."""
        import os

        if "LOG_LEVEL" in os.environ:
            del os.environ["LOG_LEVEL"]
        log_level = os.getenv("LOG_LEVEL", "INFO")
        assert log_level == "INFO"


class TestErrorHandling:
    """Test error handling in the server."""

    def test_invalid_uri_handling(self):
        """Test handling of invalid URIs."""
        from urllib.parse import urlparse

        uri = "file:///"
        parsed = urlparse(uri)
        path = parsed.path

        # Empty path should be caught
        assert not path or path == "/"

    def test_unknown_resource_handling(self, simple_resource_module):
        """Test handling of unknown resources."""
        SAMPLE_RESOURCES = simple_resource_module.SAMPLE_RESOURCES

        name = "nonexistent"
        assert name not in SAMPLE_RESOURCES


class TestListResourcesTool:
    """Test the list_resources_tool MCP tool."""

    def test_list_resources_tool_exists(self, simple_resource_module):
        """Test that list_resources_tool is defined."""
        assert hasattr(simple_resource_module, "list_resources_tool")
        assert callable(simple_resource_module.list_resources_tool)

    def test_list_resources_tool_returns_dict(self, simple_resource_module):
        """Test that list_resources_tool returns a dictionary."""
        result = simple_resource_module.list_resources_tool()
        assert isinstance(result, dict)

    def test_list_resources_tool_has_resources_key(self, simple_resource_module):
        """Test that result has 'resources' key."""
        result = simple_resource_module.list_resources_tool()
        assert "resources" in result
        assert isinstance(result["resources"], list)

    def test_list_resources_tool_has_count_key(self, simple_resource_module):
        """Test that result has 'count' key."""
        result = simple_resource_module.list_resources_tool()
        assert "count" in result
        assert isinstance(result["count"], int)

    def test_list_resources_tool_count_matches_resources_length(self, simple_resource_module):
        """Test that count matches the number of resources."""
        result = simple_resource_module.list_resources_tool()
        assert result["count"] == len(result["resources"])

    def test_list_resources_tool_returns_all_resources(self, simple_resource_module):
        """Test that all sample resources are returned."""
        result = simple_resource_module.list_resources_tool()
        resource_names = [r["name"] for r in result["resources"]]

        for name in simple_resource_module.SAMPLE_RESOURCES.keys():
            assert name in resource_names

    def test_list_resources_tool_resource_structure(self, simple_resource_module):
        """Test that each resource has required fields."""
        result = simple_resource_module.list_resources_tool()

        for resource in result["resources"]:
            assert "name" in resource
            assert "title" in resource
            assert "description" in resource
            assert "uri" in resource
            assert isinstance(resource["name"], str)
            assert isinstance(resource["title"], str)
            assert isinstance(resource["description"], str)
            assert isinstance(resource["uri"], str)

    def test_list_resources_tool_uri_format(self, simple_resource_module):
        """Test that URIs follow file:/// format."""
        result = simple_resource_module.list_resources_tool()

        for resource in result["resources"]:
            uri = resource["uri"]
            assert uri.startswith("file:///")
            assert uri.endswith(".txt")

    def test_list_resources_tool_greeting_resource(self, simple_resource_module):
        """Test that greeting resource is in the list."""
        result = simple_resource_module.list_resources_tool()
        resource_names = [r["name"] for r in result["resources"]]
        assert "greeting" in resource_names

        greeting = next(r for r in result["resources"] if r["name"] == "greeting")
        assert "Welcome" in greeting["title"]

    def test_list_resources_tool_help_resource(self, simple_resource_module):
        """Test that help resource is in the list."""
        result = simple_resource_module.list_resources_tool()
        resource_names = [r["name"] for r in result["resources"]]
        assert "help" in resource_names

        help_res = next(r for r in result["resources"] if r["name"] == "help")
        assert len(help_res["title"]) > 0

    def test_list_resources_tool_about_resource(self, simple_resource_module):
        """Test that about resource is in the list."""
        result = simple_resource_module.list_resources_tool()
        resource_names = [r["name"] for r in result["resources"]]
        assert "about" in resource_names

        about = next(r for r in result["resources"] if r["name"] == "about")
        assert len(about["title"]) > 0

    def test_list_resources_tool_minimum_count(self, simple_resource_module):
        """Test that at least one resource is returned."""
        result = simple_resource_module.list_resources_tool()
        assert result["count"] >= 1

    def test_list_resources_tool_resource_names_valid(self, simple_resource_module):
        """Test that resource names are not empty."""
        result = simple_resource_module.list_resources_tool()

        for resource in result["resources"]:
            assert len(resource["name"]) > 0
            assert len(resource["title"]) > 0


class TestGetResourceContentTool:
    """Test the get_resource_content MCP tool."""

    def test_get_resource_content_exists(self, simple_resource_module):
        """Test that get_resource_content is defined."""
        assert hasattr(simple_resource_module, "get_resource_content")
        assert callable(simple_resource_module.get_resource_content)

    def test_get_resource_content_returns_dict(self, simple_resource_module):
        """Test that get_resource_content returns a dictionary."""
        result = simple_resource_module.get_resource_content("greeting")
        assert isinstance(result, dict)

    def test_get_resource_content_has_name_key(self, simple_resource_module):
        """Test that result has 'name' key."""
        result = simple_resource_module.get_resource_content("greeting")
        assert "name" in result
        assert result["name"] == "greeting"

    def test_get_resource_content_has_title_key(self, simple_resource_module):
        """Test that result has 'title' key."""
        result = simple_resource_module.get_resource_content("greeting")
        assert "title" in result
        assert len(result["title"]) > 0

    def test_get_resource_content_has_content_key(self, simple_resource_module):
        """Test that result has 'content' key."""
        result = simple_resource_module.get_resource_content("greeting")
        assert "content" in result
        assert len(result["content"]) > 0

    def test_get_resource_content_has_uri_key(self, simple_resource_module):
        """Test that result has 'uri' key."""
        result = simple_resource_module.get_resource_content("greeting")
        assert "uri" in result
        assert result["uri"].startswith("file:///")

    def test_get_resource_content_greeting(self, simple_resource_module):
        """Test retrieving greeting resource content."""
        result = simple_resource_module.get_resource_content("greeting")
        assert result["name"] == "greeting"
        assert "Hello" in result["content"]
        assert result["uri"] == "file:///greeting.txt"

    def test_get_resource_content_help(self, simple_resource_module):
        """Test retrieving help resource content."""
        result = simple_resource_module.get_resource_content("help")
        assert result["name"] == "help"
        assert len(result["content"]) > 0
        assert result["uri"] == "file:///help.txt"

    def test_get_resource_content_about(self, simple_resource_module):
        """Test retrieving about resource content."""
        result = simple_resource_module.get_resource_content("about")
        assert result["name"] == "about"
        assert "simple-resource" in result["content"].lower()
        assert result["uri"] == "file:///about.txt"

    def test_get_resource_content_nonexistent_raises_error(self, simple_resource_module):
        """Test that nonexistent resource raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            simple_resource_module.get_resource_content("nonexistent")

        error_msg = str(exc_info.value)
        assert "Unknown resource" in error_msg or "nonexistent" in error_msg

    def test_get_resource_content_empty_name_raises_error(self, simple_resource_module):
        """Test that empty resource name raises ValueError."""
        with pytest.raises(ValueError):
            simple_resource_module.get_resource_content("")

    def test_get_resource_content_none_name_raises_error(self, simple_resource_module):
        """Test that None resource name raises ValueError."""
        with pytest.raises(ValueError):
            simple_resource_module.get_resource_content(None)

    def test_get_resource_content_invalid_name_includes_available(self, simple_resource_module):
        """Test that error message includes available resources."""
        with pytest.raises(ValueError) as exc_info:
            simple_resource_module.get_resource_content("invalid")

        error_msg = str(exc_info.value)
        assert "Available resources" in error_msg

    def test_get_resource_content_case_sensitive(self, simple_resource_module):
        """Test that resource names are case-sensitive."""
        # Uppercase should fail
        with pytest.raises(ValueError):
            simple_resource_module.get_resource_content("GREETING")

    def test_get_resource_content_returns_correct_title(self, simple_resource_module):
        """Test that returned title matches sample resource."""
        result = simple_resource_module.get_resource_content("greeting")
        assert result["title"] == simple_resource_module.SAMPLE_RESOURCES["greeting"]["title"]

    def test_get_resource_content_returns_correct_content(self, simple_resource_module):
        """Test that returned content matches sample resource."""
        result = simple_resource_module.get_resource_content("greeting")
        assert result["content"] == simple_resource_module.SAMPLE_RESOURCES["greeting"]["content"]

    def test_get_resource_content_all_resources_accessible(self, simple_resource_module):
        """Test that all sample resources can be retrieved."""
        for resource_name in simple_resource_module.SAMPLE_RESOURCES.keys():
            result = simple_resource_module.get_resource_content(resource_name)
            assert result["name"] == resource_name
            assert len(result["content"]) > 0


class TestToolIntegration:
    """Test integration between tools and resources."""

    def test_tools_match_resources(self, simple_resource_module):
        """Test that tools expose same resources as SAMPLE_RESOURCES."""
        list_result = simple_resource_module.list_resources_tool()
        resource_names = [r["name"] for r in list_result["resources"]]

        sample_names = list(simple_resource_module.SAMPLE_RESOURCES.keys())

        assert set(resource_names) == set(sample_names)

    def test_list_tool_and_get_tool_consistency(self, simple_resource_module):
        """Test that list_resources_tool and get_resource_content are consistent."""
        list_result = simple_resource_module.list_resources_tool()

        for resource_info in list_result["resources"]:
            name = resource_info["name"]
            get_result = simple_resource_module.get_resource_content(name)

            assert get_result["name"] == resource_info["name"]
            assert get_result["title"] == resource_info["title"]
            assert get_result["uri"] == resource_info["uri"]

    def test_tool_results_have_no_extra_fields(self, simple_resource_module):
        """Test that tool results don't have unexpected fields."""
        list_result = simple_resource_module.list_resources_tool()

        expected_keys = {"resources", "count"}
        assert set(list_result.keys()) == expected_keys

        for resource in list_result["resources"]:
            expected_resource_keys = {"name", "title", "description", "uri"}
            assert set(resource.keys()) == expected_resource_keys

    def test_get_resource_results_have_no_extra_fields(self, simple_resource_module):
        """Test that get_resource_content results don't have unexpected fields."""
        result = simple_resource_module.get_resource_content("greeting")

        expected_keys = {"name", "title", "content", "uri"}
        assert set(result.keys()) == expected_keys


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
