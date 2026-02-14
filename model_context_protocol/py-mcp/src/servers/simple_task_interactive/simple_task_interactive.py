"""Simple interactive task server demonstrating elicitation and sampling.

This example shows the task API where:
- server.experimental.enable_tasks() sets up all infrastructure
- ctx.experimental.run_task() handles task lifecycle automatically
- ServerTaskContext.elicit() and ServerTaskContext.create_message() queue requests properly

Can be run as:
1. Over stdio (for mcp-inspector):
   mcp-inspector "python -m src.servers.simple_task_interactive"

2. Over HTTP:
   python -m src.servers.simple_task_interactive
"""

import logging
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import click
import uvicorn
from dotenv import load_dotenv
from mcp import types
from mcp.server import Server, ServerRequestContext
from mcp.server.experimental.task_context import ServerTaskContext
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("simple-task-interactive-server")


async def handle_list_tools(
    _ctx: ServerRequestContext, _params: types.PaginatedRequestParams | None
) -> types.ListToolsResult:
    """List available tools."""
    logger.debug("Listing tools")
    return types.ListToolsResult(
        tools=[
            types.Tool(
                name="confirm_delete",
                description="Asks for confirmation before deleting (demonstrates elicitation)",
                input_schema={
                    "type": "object",
                    "properties": {"filename": {"type": "string"}},
                },
                execution=types.ToolExecution(task_support=types.TASK_REQUIRED),
            ),
            types.Tool(
                name="write_haiku",
                description="Asks LLM to write a haiku (demonstrates sampling)",
                input_schema={"type": "object", "properties": {"topic": {"type": "string"}}},
                execution=types.ToolExecution(task_support=types.TASK_REQUIRED),
            ),
        ]
    )


async def handle_confirm_delete(ctx: ServerRequestContext, arguments: dict[str, Any]) -> types.CreateTaskResult:
    """Handle the confirm_delete tool - demonstrates elicitation."""
    logger.debug(f"confirm_delete handler called with arguments: {arguments}")
    ctx.experimental.validate_task_mode(types.TASK_REQUIRED)

    filename = arguments.get("filename", "unknown.txt")
    logger.info(f"Confirm delete requested for '{filename}'")

    async def work(task: ServerTaskContext) -> types.CallToolResult:
        logger.debug(f"Task {task.task_id} starting elicitation for file: {filename}")

        try:
            result = await task.elicit(
                message=f"Are you sure you want to delete '{filename}'?",
                requested_schema={
                    "type": "object",
                    "properties": {"confirm": {"type": "boolean"}},
                    "required": ["confirm"],
                },
            )

            logger.debug(f"Received elicitation response: action={result.action}")

            if result.action == "accept" and result.content:
                confirmed = result.content.get("confirm", False)
                text = f"Deleted '{filename}'" if confirmed else "Deletion cancelled"
            else:
                text = "Deletion cancelled"

            logger.info(f"Delete confirmation result: {text}")
            return types.CallToolResult(content=[types.TextContent(type="text", text=text)])
        except Exception as e:
            logger.error(f"Error in elicitation task: {e}", exc_info=True)
            error_text = f"Error during elicitation: {str(e)}"
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=error_text)],
                is_error=True,
            )

    return await ctx.experimental.run_task(work)


async def handle_write_haiku(ctx: ServerRequestContext, arguments: dict[str, Any]) -> types.CreateTaskResult:
    """Handle the write_haiku tool - demonstrates sampling."""
    logger.debug(f"write_haiku handler called with arguments: {arguments}")
    ctx.experimental.validate_task_mode(types.TASK_REQUIRED)

    topic = arguments.get("topic", "nature")
    logger.info(f"Write haiku requested for topic: {topic}")

    async def work(task: ServerTaskContext) -> types.CallToolResult:
        logger.debug(f"Task {task.task_id} starting sampling for topic: {topic}")

        try:
            result = await task.create_message(
                messages=[
                    types.SamplingMessage(
                        role="user",
                        content=types.TextContent(type="text", text=f"Write a haiku about {topic}"),
                    )
                ],
                max_tokens=50,
            )

            haiku = "No response"
            if isinstance(result.content, types.TextContent):
                haiku = result.content.text

            logger.info(f"Haiku generated (first 50 chars): {haiku[:50]}")
            return types.CallToolResult(content=[types.TextContent(type="text", text=f"Haiku:\n{haiku}")])
        except Exception as e:
            logger.error(f"Error in sampling task: {e}", exc_info=True)
            error_text = f"Error during sampling: {str(e)}"
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=error_text)],
                is_error=True,
            )

    return await ctx.experimental.run_task(work)


async def handle_call_tool(
    ctx: ServerRequestContext, params: types.CallToolRequestParams
) -> types.CallToolResult | types.CreateTaskResult:
    """Dispatch tool calls to their handlers."""
    logger.debug(f"Tool call: {params.name}")
    arguments = params.arguments or {}

    try:
        if params.name == "confirm_delete":
            return await handle_confirm_delete(ctx, arguments)
        elif params.name == "write_haiku":
            return await handle_write_haiku(ctx, arguments)
        else:
            logger.warning(f"Unknown tool requested: {params.name}")
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=f"Unknown tool: {params.name}")],
                is_error=True,
            )
    except Exception as e:
        logger.error(f"Error handling tool call: {e}", exc_info=True)
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Error: {str(e)}")],
            is_error=True,
        )


server = Server(
    "simple-task-interactive-server",
    on_list_tools=handle_list_tools,
    on_call_tool=handle_call_tool,
)

# Enable task support - this auto-registers all handlers
server.experimental.enable_tasks()
logger.debug("Task support enabled")


def create_app(session_manager: StreamableHTTPSessionManager) -> Starlette:
    """Create Starlette application with MCP mount."""
    @asynccontextmanager
    async def app_lifespan(_app: Starlette) -> AsyncIterator[None]:
        async with session_manager.run():
            yield

    return Starlette(
        routes=[Mount("/mcp", app=session_manager.handle_request)],
        lifespan=app_lifespan,
    )


@click.command()
@click.option("--port", default=8000, help="Port to listen on (HTTP mode)")
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Set logging level",
)
def main(port: int, log_level: str) -> int:
    """Start the simple task interactive MCP server.

    Supports two modes:
    1. Over stdio (for mcp-inspector):
       mcp-inspector "python -m src.servers.simple_task_interactive"

    2. Over HTTP:
       python -m src.servers.simple_task_interactive --port 8000
    """
    # Update logging level
    logging.getLogger().setLevel(log_level.upper())
    logger.info(f"Set logging level to {log_level.upper()}")
    logger.info("Starting Simple Task Interactive Server")

    try:
        # Auto-detect HTTP vs stdio mode
        # If stdout is a TTY (terminal), run HTTP server
        # Otherwise (piped/stdio), run MCP server
        if sys.stdout.isatty():
            logger.info(f"Running in HTTP mode on http://127.0.0.1:{port}/mcp")
            session_manager = StreamableHTTPSessionManager(app=server)
            starlette_app = create_app(session_manager)
            uvicorn.run(starlette_app, host="127.0.0.1", port=port)
        else:
            logger.info("Running in stdio mode for MCP protocol")
            server.run()

        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user (CTRL+C)")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
