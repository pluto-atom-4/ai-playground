import logging
import os

import click
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, PromptMessage, Prompt, PromptArgument
from pydantic import BaseModel
from typing import List, Optional, Dict

load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("simple-prompt.server")

# Create FastMCP server instance
mcp = FastMCP("mcp-simple-prompt")


def create_messages(context: str | None = None, topic: str | None = None) -> list[PromptMessage]:
    """
    Create messages based on context and topic.

    :param context:
    :param topic:
    :return: TextContent with generated messages
    """
    messages: list[PromptMessage] = []

    # Add context if provided
    if context is None:
        messages.append(
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text", text=f"Here is some revvelant context: {context}"
                )
            )
        )

    # Add the main prompt
    prompt = "Please hemp me with"
    if topic is not None:
        prompt += f"the following topic: {topic}"
    else:
        prompt += "Whatever questions I may have."

    messages.append(PromptMessage(role="user", content=TextContent(type="text", text=prompt)))

    return messages


class ListPromptsOutput(BaseModel):
    prompts: List[Prompt]


@mcp.tool(name="list_prompts", description="List available prompts")
async def list_prompts() -> ListPromptsOutput:
    return ListPromptsOutput(
        prompts=[
            Prompt(
                name="simple",
                title="Simple Assistant Prompt",
                description="A simple prompt that can take optional context and topic arguments",
                arguments=[
                    PromptArgument(
                        name="context",
                        description="Additional context to consider",
                        required=False,
                    ),
                    PromptArgument(
                        name="topic",
                        description="Specific topic to focus on",
                        required=False,
                    ),
                ],
            )
        ]
    )


class GetPromptInput(BaseModel):
    name: str
    arguments: Optional[Dict[str, str]] = None


class GetPromptOutput(BaseModel):
    messages: List[PromptMessage]
    description: str


@mcp.tool(name="get_prompt", description="Retrieve a prompt by name and arguments")
async def get_prompt(prompt_input: GetPromptInput) -> GetPromptOutput:
    if prompt_input.name != "simple":
        raise ValueError(f"Unknown prompt: {prompt_input.name}")

    arguments = prompt_input.arguments or {}
    messages = create_messages(
        context=arguments.get("context"),
        topic=arguments.get("topic")
    )
    return GetPromptOutput(
        messages=messages,
        description="A simple prompt with optional context and topic arguments"
    )


@click.command()
@click.option("--port", default=8000, help="Port to listen on")
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Set logging level",
)
def main(log_level: str = "INFO", port: int = 8000) -> int:
    """
    # Update logging level if specified
    """
    logging.getLogger().setLevel(log_level.upper())
    logger.info(f"Set logging level to {log_level.upper()}")

    logger.info(f"Starting Simple Prompt MCP Server")

    try:
        mcp.run()
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user (CTRL+C)")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        return 1
