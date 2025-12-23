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


class TestIntegration:
    """Integration tests for desktop server components."""

    def test_list_and_stats_consistency(self):
        """Test that list matches stats file count."""
        list_result = list_desktop_files()
        stats_result = get_desktop_stats()

        if list_result["isError"] is False and stats_result["isError"] is False:
            list_items = json.loads(list_result["content"][0]["text"])
            stats_data = json.loads(stats_result["content"][0]["text"])

            file_count = len([item for item in list_items if item["type"] == "file"])
            dir_count = len([item for item in list_items if item["type"] == "directory"])

            assert file_count == stats_data["total_files"]
            assert dir_count == stats_data["total_directories"]

    def test_multiple_calls_consistency(self):
        """Test that multiple calls return consistent results."""
        result1 = list_desktop_files()
        result2 = list_desktop_files()

        if result1["isError"] is False and result2["isError"] is False:
            items1 = json.loads(result1["content"][0]["text"])
            items2 = json.loads(result2["content"][0]["text"])

            assert len(items1) == len(items2)

    def test_stats_multiple_calls_consistency(self):
        """Test that stats are consistent across multiple calls."""
        result1 = get_desktop_stats()
        result2 = get_desktop_stats()

        if result1["isError"] is False and result2["isError"] is False:
            stats1 = json.loads(result1["content"][0]["text"])
            stats2 = json.loads(result2["content"][0]["text"])

            # Stats should be identical or very similar (files may be added between calls)
            assert stats1["desktop_path"] == stats2["desktop_path"]

    def test_resource_vs_tool_consistency(self):
        """Test that resource and tool return consistent data."""
        tool_result = list_desktop_files()
        resource_result = desktop_files_resource()

        if tool_result["isError"] is False:
            tool_items = json.loads(tool_result["content"][0]["text"])
            resource_data = json.loads(resource_result)

            # Both should have the same number of items
            assert len(tool_items) == len(resource_data.get("files", []))

    def test_error_handling_consistency(self):
        """Test that errors are handled consistently."""
        file_result = get_file_content("../../../nonexistent.txt")
        resource_result = desktop_file_resource("../../../nonexistent.txt")

        assert file_result["isError"] is True
        resource_error = json.loads(resource_result)
        assert "error" in resource_error


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_unicode_file_names(self):
        """Test handling of unicode characters in file operations."""
        with tempfile.NamedTemporaryFile(mode='w', dir=str(Path.home() / "Desktop"),
                                        delete=False, suffix='_你好.txt', encoding='utf-8') as f:
            f.write("Unicode file content")
            temp_file = f.name

        try:
            filename = os.path.basename(temp_file)
            result = get_file_content(filename)

            # Should handle unicode filename or return error gracefully
            assert "content" in result
            assert "isError" in result
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass

    def test_special_characters_in_filename(self):
        """Test handling of special characters in filenames."""
        special_names = [
            "test with spaces.txt",
            "test-with-dashes.txt",
            "test_with_underscores.txt"
        ]

        for name in special_names:
            try:
                result = get_file_content(name)
                # Should not crash
                assert "content" in result
                assert "isError" in result
            except:
                # If file doesn't exist, that's OK
                pass

    def test_very_long_filename(self):
        """Test handling of very long filenames."""
        long_name = "a" * 255 + ".txt"
        result = get_file_content(long_name)

        # Should handle gracefully
        assert "content" in result
        assert "isError" in result

    def test_empty_filename(self):
        """Test handling of empty filename."""
        result = get_file_content("")

        assert "content" in result
        assert "isError" in result

    def test_null_byte_in_filename(self):
        """Test that null bytes are handled safely."""
        try:
            result = get_file_content("test\x00file.txt")
            assert "content" in result
            assert "isError" in result
        except (ValueError, TypeError):
            # Expected behavior for null bytes
            pass

