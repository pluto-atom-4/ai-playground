"""
Simple MCP server demonstrating pagination for tools, resources, and prompts.

This example shows how to use the paginated decorators to handle large lists
of items that need to be split across multiple pages.
"""

import logging
import os
from typing import Any, List, Optional, Dict

import click
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, PromptMessage, Prompt, PromptArgument, Tool, Resource
from pydantic import BaseModel

load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("simple-pagination.server")

# Create FastMCP server instance
mcp = FastMCP("mcp-simple-pagination")


# Sample data - in real scenarios, this might come from a database
SAMPLE_TOOLS = [
    Tool(
        name=f"tool_{i}",
        description=f"This is sample tool number {i}",
        inputSchema={"type": "object", "properties": {"input": {"type": "string"}}},
    )
    for i in range(1, 26)  # 25 tools total
]

SAMPLE_RESOURCES = [
    Resource(
        uri=f"file:///path/to/resource_{i}.txt",
        name=f"resource_{i}",
        description=f"This is sample resource number {i}",
        mimeType="text/plain",
    )
    for i in range(1, 31)  # 30 resources total
]

SAMPLE_PROMPTS = [
    Prompt(
        name=f"prompt_{i}",
        description=f"This is sample prompt number {i}",
        arguments=[
            PromptArgument(name="arg1", description="First argument", required=True),
        ],
    )
    for i in range(1, 21)  # 20 prompts total
]


def paginate_list(items: List[Any], page_size: int, cursor: Optional[str]) -> tuple[List[Any], Optional[str]]:
    """
    Paginate a list of items based on cursor position.

    :param items: List of items to paginate
    :param page_size: Number of items per page
    :param cursor: Cursor indicating start position (as string integer)
    :return: Tuple of (page_items, next_cursor)
    """
    if cursor is None:
        start_idx = 0
    else:
        try:
            start_idx = int(cursor)
        except (ValueError, TypeError):
            logger.warning(f"Invalid cursor: {cursor}, resetting to 0")
            start_idx = 0

    page_items = items[start_idx : start_idx + page_size]

    next_cursor = None
    if start_idx + page_size < len(items):
        next_cursor = str(start_idx + page_size)

    logger.debug(f"Paginating {len(items)} items: start_idx={start_idx}, page_size={page_size}, has_more={next_cursor is not None}")
    return page_items, next_cursor


class ListToolsOutput(BaseModel):
    tools: List[Tool]
    next_cursor: Optional[str] = None


@mcp.tool(name="list_tools", description="List available tools with pagination (5 tools per page)")
async def list_tools(cursor: Optional[str] = None) -> ListToolsOutput:
    """List available tools with pagination support."""
    logger.info(f"list_tools called with cursor={cursor}")
    page_tools, next_cursor = paginate_list(SAMPLE_TOOLS, page_size=5, cursor=cursor)
    return ListToolsOutput(tools=page_tools, next_cursor=next_cursor)


class ListResourcesOutput(BaseModel):
    resources: List[Resource]
    next_cursor: Optional[str] = None


@mcp.tool(name="list_resources", description="List available resources with pagination (10 resources per page)")
async def list_resources(cursor: Optional[str] = None) -> ListResourcesOutput:
    """List available resources with pagination support."""
    logger.info(f"list_resources called with cursor={cursor}")
    page_resources, next_cursor = paginate_list(SAMPLE_RESOURCES, page_size=10, cursor=cursor)
    return ListResourcesOutput(resources=page_resources, next_cursor=next_cursor)


class ListPromptsOutput(BaseModel):
    prompts: List[Prompt]
    next_cursor: Optional[str] = None


@mcp.tool(name="list_prompts", description="List available prompts with pagination (7 prompts per page)")
async def list_prompts(cursor: Optional[str] = None) -> ListPromptsOutput:
    """List available prompts with pagination support."""
    logger.info(f"list_prompts called with cursor={cursor}")
    page_prompts, next_cursor = paginate_list(SAMPLE_PROMPTS, page_size=7, cursor=cursor)
    return ListPromptsOutput(prompts=page_prompts, next_cursor=next_cursor)


class CallToolInput(BaseModel):
    name: str
    arguments: Dict[str, Any]


class CallToolOutput(BaseModel):
    result: str


@mcp.tool(name="call_tool", description="Call a tool by name with arguments")
async def call_tool(tool_input: CallToolInput) -> CallToolOutput:
    """Invoke a tool by name."""
    logger.info(f"call_tool: {tool_input.name} with arguments: {tool_input.arguments}")

    tool = next((t for t in SAMPLE_TOOLS if t.name == tool_input.name), None)
    if not tool:
        logger.error(f"Unknown tool: {tool_input.name}")
        raise ValueError(f"Unknown tool: {tool_input.name}")

    result = f"Called tool '{tool_input.name}' with arguments: {tool_input.arguments}"
    return CallToolOutput(result=result)


class ReadResourceInput(BaseModel):
    uri: str


class ReadResourceOutput(BaseModel):
    content: str


@mcp.tool(name="read_resource", description="Read resource content by URI")
async def read_resource(resource_input: ReadResourceInput) -> ReadResourceOutput:
    """Read the content of a resource."""
    logger.info(f"read_resource: {resource_input.uri}")

    resource = next((r for r in SAMPLE_RESOURCES if r.uri == resource_input.uri), None)
    if not resource:
        logger.error(f"Unknown resource: {resource_input.uri}")
        raise ValueError(f"Unknown resource: {resource_input.uri}")

    content = f"Content of {resource.name}: This is sample content for the resource."
    return ReadResourceOutput(content=content)


class GetPromptInput(BaseModel):
    name: str
    arguments: Optional[Dict[str, str]] = None


class GetPromptOutput(BaseModel):
    description: str
    messages: List[PromptMessage]


@mcp.tool(name="get_prompt", description="Retrieve a prompt by name and arguments")
async def get_prompt(prompt_input: GetPromptInput) -> GetPromptOutput:
    """Get a prompt by name with optional arguments."""
    logger.info(f"get_prompt: {prompt_input.name} with arguments: {prompt_input.arguments}")

    prompt = next((p for p in SAMPLE_PROMPTS if p.name == prompt_input.name), None)
    if not prompt:
        logger.error(f"Unknown prompt: {prompt_input.name}")
        raise ValueError(f"Unknown prompt: {prompt_input.name}")

    message_text = f"This is the prompt '{prompt_input.name}'"
    if prompt_input.arguments:
        message_text += f" with arguments: {prompt_input.arguments}"

    return GetPromptOutput(
        description=prompt.description,
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=message_text),
            )
        ],
    )


@click.command()
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Set logging level",
)
def main(log_level: str = "INFO") -> int:
    """Start the Simple Pagination MCP Server."""
    logging.getLogger().setLevel(log_level.upper())
    logger.info(f"Set logging level to {log_level.upper()}")
    logger.info("Starting Simple Pagination MCP Server")

    try:
        mcp.run()
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user (CTRL+C)")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        return 1
