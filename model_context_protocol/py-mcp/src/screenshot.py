"""
FastMCP Screenshot Server

Give Claude a tool to capture and view screenshots.

Demonstrates using the Image type with FastMCP for visual tool support.
Follows FastMCP Server guidelines with proper logging, validation, and error handling.
"""

import io
import logging

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.types import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Create server with screenshot tool dependencies
mcp = FastMCP(
    "Screenshot Demo",
    dependencies=["pyautogui", "Pillow"]
)


@mcp.tool(
    name="take_screenshot",
    description="Take a screenshot of the user's screen and return it as an image. "
                "Use this tool anytime you need to see what's on the user's screen."
)
def take_screenshot() -> Image:
    """
    Capture a screenshot of the current screen and return it as a JPEG image.

    The screenshot is compressed with quality reduction to keep file size under ~1MB
    to ensure compatibility with Claude and other MCP clients.

    Returns:
        Image: A JPEG-formatted screenshot of the current screen

    Raises:
        ImportError: If required dependencies (pyautogui, Pillow) are not installed
        Exception: If screenshot capture fails
    """
    logger.info("take_screenshot called")

    try:
        import pyautogui
        from PIL import Image as PILImage
    except ImportError as e:
        logger.error(f"Failed to import required dependencies: {e}")
        raise ImportError(
            "Screenshot tool requires 'pyautogui' and 'Pillow' packages. "
            "Install with: pip install pyautogui Pillow"
        ) from e

    try:
        logger.info("Capturing screenshot...")

        # Capture the screen
        screenshot = pyautogui.screenshot()
        logger.info(f"Screenshot captured: {screenshot.size}")

        # Convert to RGB to ensure JPEG compatibility
        screenshot = screenshot.convert("RGB")

        # Compress to JPEG format with quality reduction
        # This keeps file size under ~1MB for Claude compatibility
        buffer = io.BytesIO()
        screenshot.save(
            buffer,
            format="JPEG",
            quality=60,
            optimize=True
        )

        image_data = buffer.getvalue()
        logger.info(f"Screenshot processed: {len(image_data)} bytes")

        return Image(data=image_data, format="jpeg")

    except Exception as e:
        logger.error(f"Failed to capture screenshot: {e}", exc_info=True)
        raise RuntimeError(f"Screenshot capture failed: {str(e)}") from e


if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    # Configure detailed logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    logger = logging.getLogger(__name__)

    # Create FastAPI app
    app = FastAPI(
        title="Screenshot Server",
        description="FastMCP Screenshot Server with HTTP API",
        version="1.0.0"
    )

    # Mount MCP server
    logger.info("=" * 80)
    logger.info("SCREENSHOT SERVER INITIALIZATION")
    logger.info("=" * 80)
    logger.info(f"Server Name: {mcp.name}")
    logger.info(f"Server Version: 1.0.0")
    logger.info(f"Tool Name: take_screenshot")
    logger.info(f"Tool Description: Capture and view screenshots")
    logger.info(f"Dependencies: {mcp.dependencies}")

    # REST API endpoints
    @app.get("/")
    async def root():
        """Service information endpoint"""
        logger.info("GET / - Service information requested")
        return {
            "version": "1.0.0",
            "description": "FastMCP Screenshot Server",
            "endpoints": [
                {"path": "/", "method": "GET", "description": "Service information"},
                {"path": "/health", "method": "GET", "description": "Health check"},
                {"path": "/screenshot", "method": "GET", "description": "Capture screenshot"},
            ]
        }

    @app.get("/health")
    async def health():
        """Health check endpoint"""
        logger.info("GET /health - Health check requested")
        return {"status": "healthy", "service": "screenshot-server"}

    @app.get("/screenshot")
    async def screenshot_endpoint():
        """Capture screenshot endpoint"""
        logger.info("GET /screenshot - Screenshot capture requested")
        try:
            result = take_screenshot()
            logger.info(f"Screenshot captured successfully: {len(result.data)} bytes")
            return {
                "status": "success",
                "format": result._format,
                "size": len(result.data),
                "data": result.data.hex()[:100] + "..." if len(result.data.hex()) > 100 else result.data.hex()
            }
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": str(e)}
            )

    # Start server
    logger.info("=" * 80)
    logger.info("STARTING SERVER")
    logger.info("=" * 80)
    logger.info(f"Host: 127.0.0.1")
    logger.info(f"Port: 8003")
    logger.info(f"URL: http://127.0.0.1:8003")
    logger.info(f"Docs: http://127.0.0.1:8003/docs")
    logger.info("=" * 80)

    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8003,
            log_level="info",
            access_log=True,
            use_colors=True
        )
    except Exception as e:
        logger.error(f"Server startup failed: {e}", exc_info=True)
        raise

