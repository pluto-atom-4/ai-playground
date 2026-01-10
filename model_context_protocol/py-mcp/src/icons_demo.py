"""
FastMCP Icons Demo Server

Demonstrates using icons with tools, resources, prompts, and implementation.
Follows FastMCP Server guidelines with proper logging, validation, and error handling.
"""

import base64
import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP, Icon

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Load the icon file and convert to data URI
icon_path = Path(__file__).parent.parent / "mcp.png"

if not icon_path.exists():
    logger.warning(f"Icon file not found at {icon_path}, continuing without icons")
    icon_data_uri = None
    icon_data = None
else:
    logger.info(f"Loading icon from {icon_path}")
    icon_data = base64.standard_b64encode(icon_path.read_bytes()).decode()
    icon_data_uri = f"data:image/png;base64,{icon_data}"
    icon_data = Icon(src=icon_data_uri, mimeType="image/png", sizes=["64x64"])
    logger.info("Icon loaded successfully")

# Create server with icons in implementation
mcp = FastMCP(
    "Icons Demo Server",
    website_url="https://github.com/modelcontextprotocol/python-sdk",
    icons=[icon_data] if icon_data else None
)


@mcp.tool(
    name="demo_tool",
    description="A demo tool with an icon that echoes back a message",
    icons=[icon_data] if icon_data else None
)
def demo_tool(message: str) -> str:
    """
    Echo a message back with icon support.

    Args:
        message: The message to echo

    Returns:
        The echoed message
    """
    logger.info(f"demo_tool called with message: {message}")
    if not message:
        logger.warning("Empty message provided to demo_tool")
    return message


@mcp.tool(
    name="transform_text",
    description="Transform text with various operations",
    icons=[icon_data] if icon_data else None
)
def transform_text(text: str, operation: str = "upper") -> str:
    """
    Transform text using specified operation.

    Args:
        text: The text to transform
        operation: The operation to perform (upper, lower, reverse, title)

    Returns:
        The transformed text
    """
    logger.info(f"transform_text called with operation: {operation}")

    operation_lower = operation.lower()
    if operation_lower == "upper":
        result = text.upper()
    elif operation_lower == "lower":
        result = text.lower()
    elif operation_lower == "reverse":
        result = text[::-1]
    elif operation_lower == "title":
        result = text.title()
    else:
        logger.error(f"Unknown operation: {operation}")
        raise ValueError(f"Unknown operation: {operation}. Use: upper, lower, reverse, title")

    logger.info(f"Text transformed successfully")
    return result


@mcp.resource(
    "demo://readme",
    description="A demo resource with an icon containing readme information",
    icons=[icon_data] if icon_data else None
)
def readme_resource() -> str:
    """
    Return readme resource with icon support.

    Returns:
        Readme content
    """
    logger.info("readme_resource accessed")
    content = """# Icons Demo Server

This resource demonstrates using icons with MCP resources.
Icons provide visual context for tools, resources, and prompts.
"""
    return content


@mcp.resource(
    "demo://config",
    description="Configuration resource displaying server info",
    icons=[icon_data] if icon_data else None
)
def config_resource() -> str:
    """
    Return configuration resource.

    Returns:
        Configuration information
    """
    logger.info("config_resource accessed")
    content = """# Server Configuration

Server Name: Icons Demo Server
Implementation: FastMCP
Version: 0.1.0
Icon Support: Enabled
"""
    return content


@mcp.prompt(
    "prompt_with_icon",
    description="A demo prompt with an icon",
    icons=[icon_data] if icon_data else None
)
def prompt_with_icon(text: str) -> str:
    """
    Process a prompt with icon support.

    Args:
        text: The prompt text

    Returns:
        Processed prompt
    """
    logger.info(f"prompt_with_icon called")
    return f"Processing prompt: {text}"


@mcp.prompt(
    "creative_writing",
    description="A creative writing prompt with icon",
    icons=[icon_data] if icon_data else None
)
def creative_writing(theme: str) -> str:
    """
    Generate a creative writing prompt based on theme.

    Args:
        theme: The theme for creative writing

    Returns:
        A creative writing prompt
    """
    logger.info(f"creative_writing called with theme: {theme}")
    prompt = f"""Please write a short story about: {theme}

Consider:
- Setting and atmosphere
- Character development
- Plot structure
- Emotional impact

Make it engaging and original."""
    return prompt


@mcp.tool(
    name="multi_icon_tool",
    description="A tool demonstrating multiple icons at different sizes",
    icons=[
        Icon(src=icon_data_uri, mimeType="image/png", sizes=["16x16"]) if icon_data_uri else None,
        Icon(src=icon_data_uri, mimeType="image/png", sizes=["32x32"]) if icon_data_uri else None,
        Icon(src=icon_data_uri, mimeType="image/png", sizes=["64x64"]) if icon_data_uri else None,
    ] if icon_data_uri else None
)
def multi_icon_tool(action: str) -> str:
    """
    Demonstrate multiple icon support at different sizes.

    Args:
        action: The action to perform

    Returns:
        Action result
    """
    logger.info(f"multi_icon_tool called with action: {action}")
    actions = {
        "list": "Listing resources...",
        "create": "Creating new resource...",
        "delete": "Deleting resource...",
        "update": "Updating resource...",
    }

    result = actions.get(action.lower(), "Unknown action")
    logger.info(f"Action '{action}' completed: {result}")
    return result


if __name__ == "__main__":
    logger.info("Starting Icons Demo Server")
    logger.info(f"Icon support: {'Enabled' if icon_data else 'Disabled'}")
    # Run the server
    mcp.run()

