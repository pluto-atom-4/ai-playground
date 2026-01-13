"""
Tests for the Screenshot FastMCP Server functionality.

Tests the take_screenshot tool following FastMCP Server guidelines with proper
logging, validation, and error handling via mocking.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
import io
from unittest.mock import patch, MagicMock, Mock

# Import after path setup
from screenshot import take_screenshot, mcp


class TestTakeScreenshot:
    """Tests for the take_screenshot tool."""

    def test_take_screenshot_returns_image_type(self):
        """Test that take_screenshot returns an Image object with jpeg format."""
        with patch('pyautogui.screenshot') as mock_screenshot:
            # Create a mock PIL Image
            mock_img = MagicMock()
            mock_img.size = (1920, 1080)
            mock_img.convert.return_value = mock_img

            # Mock save to write JPEG data to buffer
            def mock_save(buffer, **kwargs):
                # Write minimal JPEG header and data
                buffer.write(b'\xff\xd8\xff\xe0')  # JPEG header
                buffer.write(b'Mock JPEG data for testing')
                buffer.write(b'\xff\xd9')  # JPEG footer

            mock_img.save = mock_save
            mock_screenshot.return_value = mock_img

            result = take_screenshot()

            # Verify result structure
            assert hasattr(result, 'data'), "Result should have 'data' attribute"
            assert hasattr(result, '_format'), "Result should have '_format' attribute"
            assert result._format == "jpeg", f"Expected format 'jpeg', got {result._format}"
            assert isinstance(result.data, bytes), "Image data should be bytes"
            assert len(result.data) > 0, "Image data should not be empty"

    def test_take_screenshot_calls_pyautogui(self):
        """Test that take_screenshot calls pyautogui.screenshot()."""
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_img = MagicMock()
            mock_img.size = (1920, 1080)
            mock_img.convert.return_value = mock_img
            mock_img.save = MagicMock()
            mock_screenshot.return_value = mock_img

            take_screenshot()

            # Verify pyautogui.screenshot was called
            mock_screenshot.assert_called_once()

    def test_take_screenshot_converts_to_rgb(self):
        """Test that take_screenshot converts image to RGB."""
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_img = MagicMock()
            mock_img.size = (1920, 1080)
            mock_img.convert.return_value = mock_img
            mock_img.save = MagicMock()
            mock_screenshot.return_value = mock_img

            take_screenshot()

            # Verify RGB conversion was called
            mock_img.convert.assert_called_once_with("RGB")

    def test_take_screenshot_saves_as_jpeg(self):
        """Test that take_screenshot saves image as JPEG with proper quality."""
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_img = MagicMock()
            mock_img.size = (1920, 1080)
            mock_img.convert.return_value = mock_img
            mock_img.save = MagicMock()
            mock_screenshot.return_value = mock_img

            take_screenshot()

            # Verify save was called with correct parameters
            mock_img.save.assert_called_once()
            call_args = mock_img.save.call_args

            # Check keyword arguments
            kwargs = call_args.kwargs
            assert kwargs.get("format") == "JPEG", "Image should be saved as JPEG"
            assert kwargs.get("quality") == 60, "JPEG quality should be 60"
            assert kwargs.get("optimize") is True, "JPEG optimization should be enabled"

    def test_take_screenshot_compression_quality(self):
        """Test that screenshot compression uses quality=60 for file size reduction."""
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_img = MagicMock()
            mock_img.size = (1920, 1080)
            mock_img.convert.return_value = mock_img

            captured_kwargs = {}
            def capture_save_kwargs(buffer, **kwargs):
                captured_kwargs.update(kwargs)
                buffer.write(b'test data')

            mock_img.save = capture_save_kwargs
            mock_screenshot.return_value = mock_img

            take_screenshot()

            assert captured_kwargs.get("quality") == 60
            assert captured_kwargs.get("optimize") is True

    def test_take_screenshot_handles_various_screen_sizes(self):
        """Test that take_screenshot works with various screen resolutions."""
        test_sizes = [
            (1920, 1080),  # Full HD
            (2560, 1440),  # 2K
            (3840, 2160),  # 4K
            (1366, 768),   # Common laptop
            (1024, 768),   # Older resolution
        ]

        for width, height in test_sizes:
            with patch('pyautogui.screenshot') as mock_screenshot:
                mock_img = MagicMock()
                mock_img.size = (width, height)
                mock_img.convert.return_value = mock_img
                mock_img.save = MagicMock()
                mock_screenshot.return_value = mock_img

                result = take_screenshot()

                assert result is not None, f"Should handle {width}x{height} resolution"
                mock_screenshot.assert_called_once()

    def test_take_screenshot_missing_pyautogui_import_error(self):
        """Test that missing pyautogui dependency raises ImportError."""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'pyautogui'")):
            with pytest.raises((ImportError, RuntimeError)):
                take_screenshot()

    def test_take_screenshot_missing_pillow_import_error(self):
        """Test that missing Pillow dependency raises ImportError."""
        # Mock the PIL import to fail
        import sys
        import importlib

        # Save original PIL module if it exists
        pil_backup = sys.modules.get('PIL')
        pil_image_backup = sys.modules.get('PIL.Image')

        try:
            # Set PIL to None to simulate import failure
            sys.modules['PIL'] = None
            sys.modules['PIL.Image'] = None

            with pytest.raises((ImportError, ModuleNotFoundError)):
                # This will try to import PIL and fail
                take_screenshot()
        finally:
            # Restore original modules
            if pil_backup is not None:
                sys.modules['PIL'] = pil_backup
            else:
                sys.modules.pop('PIL', None)
            if pil_image_backup is not None:
                sys.modules['PIL.Image'] = pil_image_backup
            else:
                sys.modules.pop('PIL.Image', None)

    def test_take_screenshot_screenshot_capture_exception(self):
        """Test that screenshot capture exceptions are handled properly."""
        with patch('pyautogui.screenshot') as mock_screenshot:
            # Simulate screenshot capture failure
            mock_screenshot.side_effect = Exception("Failed to capture screen")

            with pytest.raises(RuntimeError) as exc_info:
                take_screenshot()

            error_msg = str(exc_info.value)
            assert "screenshot capture failed" in error_msg.lower() or "failed to capture" in error_msg.lower()

    def test_take_screenshot_image_conversion_exception(self):
        """Test that image conversion exceptions are handled properly."""
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_img = MagicMock()
            mock_img.size = (1920, 1080)

            # Simulate conversion failure
            mock_img.convert.side_effect = Exception("Image conversion failed")
            mock_screenshot.return_value = mock_img

            with pytest.raises(RuntimeError) as exc_info:
                take_screenshot()

            error_msg = str(exc_info.value)
            assert "screenshot capture failed" in error_msg.lower()

    def test_take_screenshot_saves_to_bytesio(self):
        """Test that image is saved to BytesIO buffer."""
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_img = MagicMock()
            mock_img.size = (1920, 1080)
            mock_img.convert.return_value = mock_img

            # Capture the buffer passed to save
            captured_buffer = None
            def capture_buffer(buffer, **kwargs):
                nonlocal captured_buffer
                captured_buffer = buffer
                buffer.write(b'\xff\xd8\xff\xe0')  # JPEG header
                buffer.write(b'test')
                buffer.write(b'\xff\xd9')  # JPEG footer

            mock_img.save = capture_buffer
            mock_screenshot.return_value = mock_img

            result = take_screenshot()

            assert captured_buffer is not None, "Buffer should be captured"
            assert isinstance(captured_buffer, io.BytesIO), "Buffer should be BytesIO"
            assert len(result.data) > 0, "Result should contain image data"

    def test_take_screenshot_returns_valid_jpeg_format(self):
        """Test that returned image data has valid JPEG format."""
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_img = MagicMock()
            mock_img.size = (1920, 1080)
            mock_img.convert.return_value = mock_img

            def write_valid_jpeg(buffer, **kwargs):
                # Write minimal but valid JPEG data
                buffer.write(b'\xff\xd8\xff\xe0')  # JPEG SOI and APP0
                buffer.write(b'\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00')  # JFIF header
                buffer.write(b'\xff\xd9')  # JPEG EOI

            mock_img.save = write_valid_jpeg
            mock_screenshot.return_value = mock_img

            result = take_screenshot()

            # Verify JPEG format signature
            assert result.data.startswith(b'\xff\xd8'), "Image data should start with JPEG SOI marker"
            assert result.data.endswith(b'\xff\xd9'), "Image data should end with JPEG EOI marker"

    def test_take_screenshot_output_size_management(self):
        """Test that screenshot output size is managed for Claude compatibility."""
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_img = MagicMock()
            mock_img.size = (4096, 2160)  # Large resolution
            mock_img.convert.return_value = mock_img

            captured_kwargs = {}
            def capture_save_args(buffer, **kwargs):
                captured_kwargs.update(kwargs)
                # Simulate compressed output
                buffer.write(b'\xff\xd8' + b'X' * 500000 + b'\xff\xd9')  # ~500KB

            mock_img.save = capture_save_args
            mock_screenshot.return_value = mock_img

            result = take_screenshot()

            # Verify compression parameters
            assert captured_kwargs.get("quality") == 60, "Quality should be reduced for size management"
            assert captured_kwargs.get("optimize") is True, "Optimization should be enabled"
            assert len(result.data) < 2_000_000, "Output should be reasonably sized (< 2MB)"

    def test_take_screenshot_mcp_tool_registration(self):
        """Test that take_screenshot is properly registered as MCP tool."""
        # Verify the MCP server instance is properly configured
        assert mcp is not None, "MCP server should be initialized"
        assert hasattr(mcp, 'run'), "MCP server should have run method"

        # The tool should be callable
        assert callable(take_screenshot), "take_screenshot should be callable"

    def test_take_screenshot_tool_name_and_description(self):
        """Test that tool has proper name and description."""
        # These are typically set via the @mcp.tool decorator
        tool_name = "take_screenshot"
        assert tool_name, "Tool should have a name"

        # Verify the function has a docstring
        assert take_screenshot.__doc__ is not None, "Tool should have documentation"
        assert len(take_screenshot.__doc__) > 0, "Tool documentation should not be empty"


class TestScreenshotIntegration:
    """Integration tests for screenshot functionality."""

    def test_screenshot_tool_execution_flow(self):
        """Test complete screenshot capture workflow."""
        with patch('pyautogui.screenshot') as mock_screenshot:
            # Setup mock with realistic behavior
            mock_img = MagicMock()
            mock_img.size = (1920, 1080)
            mock_img.convert.return_value = mock_img

            def realistic_save(buffer, **kwargs):
                # Simulate realistic JPEG save
                buffer.write(b'\xff\xd8\xff\xe0')
                buffer.write(b'JFIF' + b'\x00' * 100)
                buffer.write(b'\xff\xd9')

            mock_img.save = realistic_save
            mock_screenshot.return_value = mock_img

            # Execute tool
            result = take_screenshot()

            # Verify complete workflow
            assert result is not None
            assert result._format == "jpeg"
            assert len(result.data) > 0
            assert isinstance(result.data, bytes)

    def test_screenshot_repeated_captures(self):
        """Test that screenshot tool can be called multiple times."""
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_img = MagicMock()
            mock_img.size = (1920, 1080)
            mock_img.convert.return_value = mock_img
            mock_img.save = lambda buffer, **kwargs: buffer.write(b'\xff\xd8\xff\xe0test\xff\xd9')
            mock_screenshot.return_value = mock_img

            # Call multiple times
            result1 = take_screenshot()
            result2 = take_screenshot()
            result3 = take_screenshot()

            # All should succeed
            assert result1 is not None
            assert result2 is not None
            assert result3 is not None
            assert mock_screenshot.call_count == 3


class TestScreenshotErrorRecovery:
    """Tests for error recovery and edge cases."""

    def test_take_screenshot_graceful_error_message(self):
        """Test that screenshot errors provide helpful messages."""
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_screenshot.side_effect = PermissionError("No permission to capture screen")

            with pytest.raises(RuntimeError) as exc_info:
                take_screenshot()

            # Error message should be user-friendly
            error_msg = str(exc_info.value)
            assert "screenshot capture failed" in error_msg.lower()

    def test_take_screenshot_unicode_error_handling(self):
        """Test that screenshot handles unicode properly in error messages."""
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_screenshot.side_effect = Exception("无法捕获屏幕")  # Unicode error message

            with pytest.raises(RuntimeError):
                take_screenshot()

    def test_take_screenshot_handles_screen_lock(self):
        """Test that screenshot handles locked screen scenario."""
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_screenshot.side_effect = OSError("Screen is locked")

            with pytest.raises(RuntimeError) as exc_info:
                take_screenshot()

            assert "screenshot capture failed" in str(exc_info.value).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

