"""
Tests for the Icons Demo FastMCP Server implementation.

Comprehensive testing of tools, resources, and prompts with icon support.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from icons_demo import (
    demo_tool,
    transform_text,
    readme_resource,
    config_resource,
    prompt_with_icon,
    creative_writing,
    multi_icon_tool,
    icon_data,
    icon_data_uri,
)


class TestDemoTool:
    """Test cases for the demo_tool function."""

    def test_demo_tool_basic(self):
        """Test demo_tool echoes a basic message."""
        result = demo_tool("Hello World")
        assert result == "Hello World"

    def test_demo_tool_empty_string(self):
        """Test demo_tool handles empty string."""
        result = demo_tool("")
        assert result == ""

    def test_demo_tool_special_characters(self):
        """Test demo_tool handles special characters."""
        test_input = "Hello!@#$%^&*()"
        result = demo_tool(test_input)
        assert result == test_input

    def test_demo_tool_unicode(self):
        """Test demo_tool handles Unicode characters."""
        test_inputs = [
            "Hello 中文",
            "Japanese: 日本語",
            "Korean: 한국어",
            "Emoji: 🎉 🚀 ✨",
            "Mixed: Hello 世界 !@# 🌟"
        ]
        for test_input in test_inputs:
            result = demo_tool(test_input)
            assert result == test_input

    def test_demo_tool_long_message(self):
        """Test demo_tool handles long messages."""
        long_msg = "x" * 5000
        result = demo_tool(long_msg)
        assert result == long_msg

    def test_demo_tool_newlines(self):
        """Test demo_tool preserves newlines."""
        test_input = "Line 1\nLine 2\nLine 3"
        result = demo_tool(test_input)
        assert result == test_input

    def test_demo_tool_tabs(self):
        """Test demo_tool preserves tabs."""
        test_input = "Column1\tColumn2\tColumn3"
        result = demo_tool(test_input)
        assert result == test_input


class TestTransformText:
    """Test cases for the transform_text tool."""

    def test_transform_text_upper(self):
        """Test transform_text with upper operation."""
        result = transform_text("hello world", "upper")
        assert result == "HELLO WORLD"

    def test_transform_text_lower(self):
        """Test transform_text with lower operation."""
        result = transform_text("HELLO WORLD", "lower")
        assert result == "hello world"

    def test_transform_text_reverse(self):
        """Test transform_text with reverse operation."""
        result = transform_text("hello", "reverse")
        assert result == "olleh"

    def test_transform_text_title(self):
        """Test transform_text with title operation."""
        result = transform_text("hello world", "title")
        assert result == "Hello World"

    def test_transform_text_case_insensitive_operation(self):
        """Test transform_text accepts operation names case-insensitively."""
        result1 = transform_text("hello", "UPPER")
        result2 = transform_text("hello", "Upper")
        result3 = transform_text("hello", "upper")
        assert result1 == result2 == result3 == "HELLO"

    def test_transform_text_default_operation(self):
        """Test transform_text uses 'upper' as default operation."""
        result = transform_text("hello world")
        assert result == "HELLO WORLD"

    def test_transform_text_empty_string(self):
        """Test transform_text handles empty string."""
        result = transform_text("", "upper")
        assert result == ""

    def test_transform_text_unicode(self):
        """Test transform_text handles Unicode."""
        result = transform_text("hello 世界", "upper")
        assert "HELLO" in result

    def test_transform_text_invalid_operation(self):
        """Test transform_text raises error with invalid operation."""
        with pytest.raises(ValueError) as exc_info:
            transform_text("hello", "invalid")
        assert "Unknown operation" in str(exc_info.value)

    def test_transform_text_special_characters(self):
        """Test transform_text with special characters."""
        result = transform_text("hello!@#$%", "upper")
        assert result == "HELLO!@#$%"


class TestReadmeResource:
    """Test cases for the readme_resource function."""

    def test_readme_resource_returns_string(self):
        """Test readme_resource returns a string."""
        result = readme_resource()
        assert isinstance(result, str)

    def test_readme_resource_contains_header(self):
        """Test readme_resource contains expected header."""
        result = readme_resource()
        assert "Icons Demo Server" in result

    def test_readme_resource_contains_icon_mention(self):
        """Test readme_resource mentions icons."""
        result = readme_resource()
        assert "icon" in result.lower()

    def test_readme_resource_not_empty(self):
        """Test readme_resource is not empty."""
        result = readme_resource()
        assert len(result) > 0


class TestConfigResource:
    """Test cases for the config_resource function."""

    def test_config_resource_returns_string(self):
        """Test config_resource returns a string."""
        result = config_resource()
        assert isinstance(result, str)

    def test_config_resource_contains_server_name(self):
        """Test config_resource contains server name."""
        result = config_resource()
        assert "Icons Demo Server" in result

    def test_config_resource_contains_implementation(self):
        """Test config_resource contains implementation info."""
        result = config_resource()
        assert "FastMCP" in result

    def test_config_resource_contains_version(self):
        """Test config_resource contains version."""
        result = config_resource()
        assert "0.1.0" in result

    def test_config_resource_not_empty(self):
        """Test config_resource is not empty."""
        result = config_resource()
        assert len(result) > 0


class TestPromptWithIcon:
    """Test cases for the prompt_with_icon function."""

    def test_prompt_with_icon_basic(self):
        """Test prompt_with_icon basic functionality."""
        result = prompt_with_icon("test prompt")
        assert "test prompt" in result

    def test_prompt_with_icon_returns_string(self):
        """Test prompt_with_icon returns a string."""
        result = prompt_with_icon("test")
        assert isinstance(result, str)

    def test_prompt_with_icon_empty_text(self):
        """Test prompt_with_icon with empty text."""
        result = prompt_with_icon("")
        assert isinstance(result, str)

    def test_prompt_with_icon_unicode(self):
        """Test prompt_with_icon handles Unicode."""
        test_text = "中文 プロンプト"
        result = prompt_with_icon(test_text)
        assert test_text in result

    def test_prompt_with_icon_contains_processing(self):
        """Test prompt_with_icon mentions processing."""
        result = prompt_with_icon("test")
        assert "processing" in result.lower() or "prompt" in result.lower()


class TestCreativeWriting:
    """Test cases for the creative_writing prompt."""

    def test_creative_writing_returns_string(self):
        """Test creative_writing returns a string."""
        result = creative_writing("adventure")
        assert isinstance(result, str)

    def test_creative_writing_contains_theme(self):
        """Test creative_writing contains the theme."""
        result = creative_writing("adventure")
        assert "adventure" in result.lower()

    def test_creative_writing_contains_story(self):
        """Test creative_writing mentions story."""
        result = creative_writing("mystery")
        assert "story" in result.lower()

    def test_creative_writing_empty_theme(self):
        """Test creative_writing with empty theme."""
        result = creative_writing("")
        assert isinstance(result, str)

    def test_creative_writing_special_characters_in_theme(self):
        """Test creative_writing handles special characters in theme."""
        result = creative_writing("sci-fi & fantasy!")
        assert isinstance(result, str)

    def test_creative_writing_unicode_theme(self):
        """Test creative_writing handles Unicode theme."""
        result = creative_writing("中文故事")
        assert isinstance(result, str)

    def test_creative_writing_long_result(self):
        """Test creative_writing produces substantial output."""
        result = creative_writing("adventure")
        assert len(result) > 50  # Substantial prompt


class TestMultiIconTool:
    """Test cases for the multi_icon_tool function."""

    def test_multi_icon_tool_list_action(self):
        """Test multi_icon_tool with list action."""
        result = multi_icon_tool("list")
        assert "Listing resources" in result or "list" in result.lower()

    def test_multi_icon_tool_create_action(self):
        """Test multi_icon_tool with create action."""
        result = multi_icon_tool("create")
        assert "Creating" in result or "create" in result.lower()

    def test_multi_icon_tool_delete_action(self):
        """Test multi_icon_tool with delete action."""
        result = multi_icon_tool("delete")
        assert "Deleting" in result or "delete" in result.lower()

    def test_multi_icon_tool_update_action(self):
        """Test multi_icon_tool with update action."""
        result = multi_icon_tool("update")
        assert "Updating" in result or "update" in result.lower()

    def test_multi_icon_tool_case_insensitive(self):
        """Test multi_icon_tool is case insensitive."""
        result1 = multi_icon_tool("LIST")
        result2 = multi_icon_tool("list")
        result3 = multi_icon_tool("List")
        assert result1 == result2 == result3

    def test_multi_icon_tool_unknown_action(self):
        """Test multi_icon_tool with unknown action."""
        result = multi_icon_tool("unknown")
        assert "Unknown action" in result

    def test_multi_icon_tool_returns_string(self):
        """Test multi_icon_tool returns a string."""
        result = multi_icon_tool("list")
        assert isinstance(result, str)


class TestIconLoading:
    """Test cases for icon loading functionality."""

    def test_icon_data_exists_or_none(self):
        """Test icon_data is either loaded or None."""
        assert icon_data is None or hasattr(icon_data, 'src')

    def test_icon_data_uri_format_or_none(self):
        """Test icon_data_uri is either proper format or None."""
        if icon_data_uri:
            assert icon_data_uri.startswith("data:image/png;base64,")

    def test_icon_data_has_correct_mime_type(self):
        """Test icon_data has correct mime type if loaded."""
        if icon_data:
            assert icon_data.mimeType == "image/png"

    def test_icon_data_has_sizes(self):
        """Test icon_data has size information if loaded."""
        if icon_data:
            assert icon_data.sizes == ["64x64"]


class TestIntegration:
    """Integration tests for the complete icons demo server."""

    def test_all_tools_callable(self):
        """Test that all tools can be called without errors."""
        demo_tool("test")
        transform_text("test", "upper")
        multi_icon_tool("list")

    def test_all_resources_accessible(self):
        """Test that all resources can be accessed."""
        readme_resource()
        config_resource()

    def test_all_prompts_callable(self):
        """Test that all prompts can be called."""
        prompt_with_icon("test")
        creative_writing("adventure")

    def test_tools_resources_prompts_independent(self):
        """Test that tools, resources, and prompts work independently."""
        # Call tools
        tool_result = demo_tool("test")
        assert tool_result == "test"

        # Access resources
        readme = readme_resource()
        assert "Icons Demo Server" in readme

        # Call prompts
        prompt = prompt_with_icon("test")
        assert "test" in prompt

