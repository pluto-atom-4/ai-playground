"""Simple task server demonstrating MCP tasks over streamable HTTP."""

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import anyio
import click
import uvicorn
from dotenv import load_dotenv
from mcp import types
from mcp.server import Server
from mcp.server.lowlevel.server import RequestContext
from mcp.server.experimental.task_context import ServerTaskContext
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from pydantic import BaseModel
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
logger = logging.getLogger("simple-task-server")


# Input/Output Models
class LongRunningTaskInput(BaseModel):
    """Input for long_running_task"""
    pass


class LongRunningTaskOutput(BaseModel):
    """Output from long_running_task"""
    result: str
    status: str = "success"


server = Server(
    "simple-task-server",
)

# One-line setup: auto-registers get_task, get_task_result, list_tasks, cancel_task
server.experimental.enable_tasks()


@server.list_tools()
async def handle_list_tools(
    ctx: RequestContext, params: types.PaginatedRequestParams | None
) -> types.ListToolsResult:
    logger.debug("Listing available tools")
    return types.ListToolsResult(
        tools=[
            types.Tool(
                name="long_running_task",
                description="A task that takes a few seconds to complete with status updates",
                input_schema={"type": "object", "properties": {}},
                execution=types.ToolExecution(task_support=types.TASK_REQUIRED),
            )
        ]
    )


@server.call_tool()
async def handle_call_tool(
    ctx: RequestContext, params: types.CallToolRequestParams
) -> types.CallToolResult | types.CreateTaskResult:
    """Dispatch tool calls to their handlers."""
    logger.debug(f"Tool called: {params.name}")

    if params.name == "long_running_task":
        ctx.experimental.validate_task_mode(types.TASK_REQUIRED)

        async def work(task: ServerTaskContext) -> types.CallToolResult:
            logger.info("Long running task started")
            try:
                await task.update_status("Starting work...")
                await anyio.sleep(1)

                await task.update_status("Processing step 1...")
                await anyio.sleep(1)

                await task.update_status("Processing step 2...")
                await anyio.sleep(1)

                logger.info("Long running task completed successfully")
                return types.CallToolResult(
                    content=[types.TextContent(type="text", text="Task completed!")]
                )
            except Exception as e:
                logger.error(f"Task execution failed: {e}", exc_info=True)
                return types.CallToolResult(
                    content=[types.TextContent(type="text", text=f"Task failed: {str(e)}")],
                    is_error=True,
                )

        return await ctx.experimental.run_task(work)

    logger.warning(f"Unknown tool requested: {params.name}")
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=f"Unknown tool: {params.name}")],
        is_error=True,
    )


@click.command()
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Set logging level",
)
@click.option("--port", default=8000, help="Port to listen on")
def main(log_level: str = "INFO", port: int = 8000) -> int:
    """Start the simple task MCP server."""
    # Update logging level
    logging.getLogger().setLevel(log_level.upper())
    logger.info(f"Set logging level to {log_level.upper()}")
    logger.info(f"Starting Simple Task Server on http://localhost:{port}/mcp")

    try:
        session_manager = StreamableHTTPSessionManager(app=server)

        @asynccontextmanager
        async def app_lifespan(app: Starlette) -> AsyncIterator[None]:
            async with session_manager.run():
                yield

        starlette_app = Starlette(
            routes=[Mount("/mcp", app=session_manager.handle_request)],
            lifespan=app_lifespan,
        )

        uvicorn.run(starlette_app, host="127.0.0.1", port=port)
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user (CTRL+C)")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        return 1
