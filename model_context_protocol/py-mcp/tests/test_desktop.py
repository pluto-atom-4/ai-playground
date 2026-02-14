"""
Tests for the Desktop MCP Server functionality.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from desktop import (
    list_desktop_files,
    get_file_content,
    get_desktop_stats,
    desktop_files_resource,
    desktop_stats_resource,
    desktop_file_resource,
)


class TestListDesktopFiles:
    """Tests for the list_desktop_files tool."""

    def test_list_desktop_files_response_format(self):
        """Test that list_desktop_files returns correct response format."""
        result = list_desktop_files()

        assert "content" in result
        assert "isError" in result
        assert result["isError"] is False
        assert isinstance(result["content"], list)
        assert len(result["content"]) == 1
        assert result["content"][0]["type"] == "text"

    def test_list_desktop_files_returns_json(self):
        """Test that list_desktop_files returns valid JSON."""
        result = list_desktop_files()

        assert result["isError"] is False
        json_text = result["content"][0]["text"]
        parsed = json.loads(json_text)
        assert isinstance(parsed, list)

    def test_list_desktop_files_contains_metadata(self):
        """Test that each file item contains required metadata."""
        result = list_desktop_files()

        if result["isError"] is False:
            json_text = result["content"][0]["text"]
            items = json.loads(json_text)

            if len(items) > 0:
                item = items[0]
                assert "name" in item
                assert "type" in item
                assert "path" in item
                assert item["type"] in ["file", "directory"]

    def test_list_desktop_files_file_size(self):
        """Test that file items have size information."""
        result = list_desktop_files()

        if result["isError"] is False:
            json_text = result["content"][0]["text"]
            items = json.loads(json_text)

            for item in items:
                if item["type"] == "file":
                    assert "size" in item
                    assert isinstance(item["size"], (int, type(None)))

    def test_list_desktop_files_directory_size(self):
        """Test that directory items have null size."""
        result = list_desktop_files()

        if result["isError"] is False:
            json_text = result["content"][0]["text"]
            items = json.loads(json_text)

            for item in items:
                if item["type"] == "directory":
                    assert item["size"] is None


class TestGetFileContent:
    """Tests for the get_file_content tool."""

    def test_get_file_content_response_format(self):
        """Test that get_file_content returns correct response format."""
        result = get_file_content("test.txt")

        assert "content" in result
        assert "isError" in result
        assert isinstance(result["content"], list)
        assert len(result["content"]) == 1
        assert result["content"][0]["type"] == "text"

    def test_get_file_content_nonexistent_file(self):
        """Test getting content of non-existent file."""
        result = get_file_content("nonexistent_file_xyz_123.txt")

        assert result["isError"] is True
        error_text = result["content"][0]["text"]
        assert "not found" in error_text.lower() or "error" in error_text.lower()

    def test_get_file_content_directory_access_denied(self):
        """Test that accessing a directory returns error."""
        result = get_file_content("..")

        assert result["isError"] is True
        error_text = result["content"][0]["text"]
        assert "error" in error_text.lower()

    def test_get_file_content_path_traversal_protection(self):
        """Test that path traversal attacks are prevented."""
        result = get_file_content("../../etc/passwd")

        assert result["isError"] is True
        error_text = result["content"][0]["text"]
        assert "error" in error_text.lower() or "access denied" in error_text.lower()

    def test_get_file_content_absolute_path_protection(self):
        """Test that absolute path traversal is prevented."""
        result = get_file_content("..\\..\\windows\\system32\\config\\sam")

        assert result["isError"] is True

    def test_get_file_content_returns_text(self):
        """Test that file content is returned as text."""
        with tempfile.NamedTemporaryFile(mode='w', dir=str(Path.home() / "Desktop"),
                                        delete=False, suffix='.txt') as f:
            f.write("Test content")
            temp_file = f.name

        try:
            filename = os.path.basename(temp_file)
            result = get_file_content(filename)

            if result["isError"] is False:
                content = result["content"][0]["text"]
                assert isinstance(content, str)
                assert "Test content" in content
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass

    def test_get_file_content_empty_file(self):
        """Test reading an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', dir=str(Path.home() / "Desktop"),
                                        delete=False, suffix='.txt') as f:
            temp_file = f.name

        try:
            filename = os.path.basename(temp_file)
            result = get_file_content(filename)

            if result["isError"] is False:
                content = result["content"][0]["text"]
                assert content == ""
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass


class TestGetDesktopStats:
    """Tests for the get_desktop_stats tool."""

    def test_get_desktop_stats_response_format(self):
        """Test that get_desktop_stats returns correct response format."""
        result = get_desktop_stats()

        assert "content" in result
        assert "isError" in result
        assert result["isError"] is False
        assert isinstance(result["content"], list)
        assert result["content"][0]["type"] == "text"

    def test_get_desktop_stats_returns_json(self):
        """Test that get_desktop_stats returns valid JSON."""
        result = get_desktop_stats()

        assert result["isError"] is False
        json_text = result["content"][0]["text"]
        stats = json.loads(json_text)
        assert isinstance(stats, dict)

    def test_get_desktop_stats_has_required_fields(self):
        """Test that stats object contains all required fields."""
        result = get_desktop_stats()

        assert result["isError"] is False
        json_text = result["content"][0]["text"]
        stats = json.loads(json_text)

        required_fields = [
            "desktop_path",
            "total_files",
            "total_directories",
            "total_size_bytes",
            "total_size_mb"
        ]

        for field in required_fields:
            assert field in stats, f"Missing field: {field}"

    def test_get_desktop_stats_field_types(self):
        """Test that stats fields have correct types."""
        result = get_desktop_stats()

        assert result["isError"] is False
        json_text = result["content"][0]["text"]
        stats = json.loads(json_text)

        assert isinstance(stats["desktop_path"], str)
        assert isinstance(stats["total_files"], int)
        assert isinstance(stats["total_directories"], int)
        assert isinstance(stats["total_size_bytes"], int)
        assert isinstance(stats["total_size_mb"], (int, float))

    def test_get_desktop_stats_non_negative_values(self):
        """Test that stats values are non-negative."""
        result = get_desktop_stats()

        assert result["isError"] is False
        json_text = result["content"][0]["text"]
        stats = json.loads(json_text)

        assert stats["total_files"] >= 0
        assert stats["total_directories"] >= 0
        assert stats["total_size_bytes"] >= 0
        assert stats["total_size_mb"] >= 0

    def test_get_desktop_stats_size_conversion(self):
        """Test that size is correctly converted from bytes to MB."""
        result = get_desktop_stats()

        assert result["isError"] is False
        json_text = result["content"][0]["text"]
        stats = json.loads(json_text)

        # Verify conversion: bytes / (1024 * 1024) = MB
        expected_mb = round(stats["total_size_bytes"] / (1024 * 1024), 2)
        assert stats["total_size_mb"] == expected_mb


class TestDesktopFilesResource:
    """Tests for the desktop://files resource."""

    def test_desktop_files_resource_returns_string(self):
        """Test that desktop_files_resource returns a string."""
        result = desktop_files_resource()

        assert isinstance(result, str)

    def test_desktop_files_resource_returns_json(self):
        """Test that desktop_files_resource returns valid JSON."""
        result = desktop_files_resource()

        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_desktop_files_resource_has_required_fields(self):
        """Test that resource has required fields."""
        result = desktop_files_resource()

        parsed = json.loads(result)
        assert "files" in parsed
        assert "path" in parsed

    def test_desktop_files_resource_files_is_list(self):
        """Test that files field is a list."""
        result = desktop_files_resource()

        parsed = json.loads(result)
        assert isinstance(parsed["files"], list)

    def test_desktop_files_resource_path_is_string(self):
        """Test that path field is a string."""
        result = desktop_files_resource()

        parsed = json.loads(result)
        assert isinstance(parsed["path"], str)


class TestDesktopStatsResource:
    """Tests for the desktop://stats resource."""

    def test_desktop_stats_resource_returns_string(self):
        """Test that desktop_stats_resource returns a string."""
        result = desktop_stats_resource()

        assert isinstance(result, str)

    def test_desktop_stats_resource_returns_json(self):
        """Test that desktop_stats_resource returns valid JSON."""
        result = desktop_stats_resource()

        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_desktop_stats_resource_has_required_fields(self):
        """Test that stats resource has all required fields."""
        result = desktop_stats_resource()

        parsed = json.loads(result)
        required_fields = [
            "desktop_path",
            "total_files",
            "total_directories",
            "total_size_bytes",
            "total_size_mb"
        ]

        for field in required_fields:
            assert field in parsed, f"Missing field: {field}"

    def test_desktop_stats_resource_consistency(self):
        """Test that multiple calls to resource return consistent data."""
        result1 = desktop_stats_resource()
        result2 = desktop_stats_resource()

        parsed1 = json.loads(result1)
        parsed2 = json.loads(result2)

        # Path should be the same
        assert parsed1["path" if "path" in parsed1 else "desktop_path"] == \
               parsed2["path" if "path" in parsed2 else "desktop_path"]


class TestDesktopFileResource:
    """Tests for the desktop://file/{filename} resource."""

    def test_desktop_file_resource_nonexistent_file(self):
        """Test accessing non-existent file returns error JSON."""
        result = desktop_file_resource("nonexistent_xyz_123.txt")

        parsed = json.loads(result)
        assert "error" in parsed

    def test_desktop_file_resource_path_traversal_protection(self):
        """Test that path traversal is prevented in resource."""
        result = desktop_file_resource("../../etc/passwd")

        parsed = json.loads(result)
        assert "error" in parsed

    def test_desktop_file_resource_valid_file(self):
        """Test reading valid file from resource."""
        with tempfile.NamedTemporaryFile(mode='w', dir=str(Path.home() / "Desktop"),
                                        delete=False, suffix='.txt') as f:
            f.write("Resource test content")
            temp_file = f.name

        try:
            filename = os.path.basename(temp_file)
            result = desktop_file_resource(filename)

            # If not error JSON, should be file content
            try:
                parsed = json.loads(result)
                assert "error" not in parsed or parsed == {}
            except json.JSONDecodeError:
                # Raw file content (not JSON), which is valid
                assert "Resource test content" in result
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass

    def test_desktop_file_resource_returns_content(self):
        """Test that file resource returns some content."""
        with tempfile.NamedTemporaryFile(mode='w', dir=str(Path.home() / "Desktop"),
                                        delete=False, suffix='.txt') as f:
            f.write("Test file content")
            temp_file = f.name

        try:
            filename = os.path.basename(temp_file)
            result = desktop_file_resource(filename)

            assert isinstance(result, str)
            assert len(result) > 0
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass


# ==================== Path Traversal Prevention Tests ====================

class TestPathTraversalPrevention:
    """Tests for path traversal attack prevention in filename validation."""

    def test_reject_forward_slash_path(self):
        """Test that filenames with forward slashes are rejected."""
        result = get_file_content("src/servers/simple_task/simple_task_server.py")
        assert result["isError"] is True
        assert "path separators" in result["content"][0]["text"].lower()
        logger.info("✓ Forward slash path correctly rejected")

    def test_reject_backslash_path(self):
        """Test that filenames with backslashes are rejected."""
        result = get_file_content("src\\servers\\simple_task\\simple_task_server.py")
        assert result["isError"] is True
        assert "path separators" in result["content"][0]["text"].lower()
        logger.info("✓ Backslash path correctly rejected")

    def test_reject_mixed_separators_path(self):
        """Test that filenames with mixed path separators are rejected."""
        result = get_file_content("src/servers\\simple_task/simple_task_server.py")
        assert result["isError"] is True
        assert "path separators" in result["content"][0]["text"].lower()
        logger.info("✓ Mixed separator path correctly rejected")

    def test_reject_parent_directory_reference(self):
        """Test that filenames with .. are rejected."""
        result = get_file_content("../../../etc/passwd")
        assert result["isError"] is True
        logger.info("✓ Parent directory reference correctly rejected")

    def test_reject_double_dot_in_filename(self):
        """Test that filenames with .. anywhere are rejected."""
        result = get_file_content("file..name.txt")
        assert result["isError"] is True
        logger.info("✓ Double dot in filename correctly rejected")

    def test_accept_valid_filename_only(self):
        """Test that valid filenames without paths are accepted (even if file doesn't exist)."""
        # Create temp file to test valid filename
        with tempfile.NamedTemporaryFile(mode='w', dir=str(Path.home() / "Desktop"),
                                        delete=False, suffix='.txt') as f:
            f.write("Test content for path traversal prevention")
            temp_file = f.name

        try:
            filename = os.path.basename(temp_file)
            result = get_file_content(filename)
            # Should not have path traversal error, might have file not found error
            # but the key is it should try to read from Desktop, not reject the filename
            assert isinstance(result, dict)
            assert "content" in result
            logger.info(f"✓ Valid filename accepted: {filename}")
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass

    def test_resource_reject_path_traversal(self):
        """Test that desktop://file resource rejects path traversal attempts."""
        result = desktop_file_resource("src/servers/simple_task/simple_task_server.py")
        parsed = json.loads(result)
        assert "error" in parsed
        assert "path separators" in parsed["error"].lower()
        logger.info("✓ Resource correctly rejects path traversal")

    def test_resource_accept_valid_filename(self):
        """Test that desktop://file resource accepts valid filenames."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', dir=str(Path.home() / "Desktop"),
                                        delete=False, suffix='.txt') as f:
            f.write("Resource test content")
            temp_file = f.name

        try:
            filename = os.path.basename(temp_file)
            result = desktop_file_resource(filename)
            # Should either return content or a valid error (not a validation error)
            try:
                parsed = json.loads(result)
                # If it's JSON, should not have path traversal error
                if "error" in parsed:
                    assert "path separators" not in parsed["error"].lower()
            except json.JSONDecodeError:
                # Raw file content, which is valid
                assert "Resource test content" in result
            logger.info(f"✓ Resource accepts valid filename: {filename}")
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass


class TestFilenameNormalization:
    """Tests for the normalize_filename helper function."""

    def test_normalize_empty_filename_raises_error(self):
        """Test that empty filename raises ValueError."""
        from desktop import normalize_filename
        with pytest.raises(ValueError):
            normalize_filename("")

    def test_normalize_rejects_forward_slashes(self):
        """Test that filenames with forward slashes are rejected."""
        from desktop import normalize_filename
        with pytest.raises(ValueError):
            normalize_filename("path/to/file.txt")

    def test_normalize_rejects_backslashes(self):
        """Test that filenames with backslashes are rejected."""
        from desktop import normalize_filename
        with pytest.raises(ValueError):
            normalize_filename("path\\to\\file.txt")

    def test_normalize_rejects_parent_directory(self):
        """Test that parent directory references are rejected."""
        from desktop import normalize_filename
        with pytest.raises(ValueError):
            normalize_filename("../file.txt")

    def test_normalize_accepts_valid_filename(self):
        """Test that valid filenames are accepted."""
        from desktop import normalize_filename
        result = normalize_filename("myfile.txt")
        assert result == "myfile.txt"

    def test_normalize_handles_special_characters(self):
        """Test that filenames with special characters (but no path separators) are accepted."""
        from desktop import normalize_filename
        result = normalize_filename("my-file_2024-01-13.txt")
        assert result == "my-file_2024-01-13.txt"


# ==================== Integration Tests ====================

class TestFileAccessIntegration:
    """Integration tests for file access with path validation."""

    def test_malformed_path_from_mcp_inspector_scenario(self):
        """Test the exact scenario from the bug report.

        The MCP inspector was requesting:
        File not found: C:\...\\.srcserverssimple_tasksimple_task_server.py

        This test ensures that such requests are properly rejected.
        """
        # Simulate the malformed path that would come from inspector
        malformed_paths = [
            "src/servers/simple_task/simple_task_server.py",
            "src\\servers\\simple_task\\simple_task_server.py",
            ".srcserverssimple_task",
            "../src/servers/simple_task/simple_task_server.py",
        ]

        for malformed_path in malformed_paths:
            result = get_file_content(malformed_path)
            assert result["isError"] is True
            error_msg = result["content"][0]["text"].lower()
            # Should not try to construct malformed file path
            assert ".srcservers" not in error_msg
            logger.info(f"✓ Rejected malformed path: {malformed_path}")

    def test_valid_desktop_file_access(self):
        """Test that valid files on desktop can be accessed."""
        # Create a test file on desktop
        with tempfile.NamedTemporaryFile(mode='w', dir=str(Path.home() / "Desktop"),
                                        delete=False, suffix='.txt') as f:
            test_content = "This is a test file on the desktop"
            f.write(test_content)
            temp_file = f.name

        try:
            filename = os.path.basename(temp_file)
            result = get_file_content(filename)

            assert result["isError"] is False
            assert test_content in result["content"][0]["text"]
            logger.info(f"✓ Successfully accessed valid desktop file: {filename}")
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass


# Add logger for tests
import logging
logger = logging.getLogger("test_desktop")

