"""
Example FastMCP server that uses Unicode characters in various places to help test
Unicode handling in tools and inspectors.

This server demonstrates:
- Unicode support in tool descriptions and parameters
- Emoji and multi-script handling
- RESTful API endpoints with FastAPI integration
- Proper logging and error handling
"""

import logging
import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP()

# Initialize FastAPI app
app = FastAPI(
    title="Unicode Example MCP Server",
    description="Example MCP server demonstrating Unicode support with RESTful API",
    version="0.1.0",
)

# API Key from environment (required for protected endpoints)
API_KEY = os.getenv("MCP_API_KEY", "default-api-key")


# ============================================================================
# Pydantic Models for Request/Response Validation
# ============================================================================


class GreetingRequest(BaseModel):
    """Request model for greeting endpoint."""

    name: str = Field(default="世界", description="Name to greet (supports Unicode)")
    greeting: str = Field(default="Hola", description="Greeting text (supports Unicode)")


class GreetingResponse(BaseModel):
    """Response model for greeting endpoint."""

    message: str = Field(description="The greeting message with Unicode characters")


class EmojiCategoriesResponse(BaseModel):
    """Response model for emoji categories endpoint."""

    categories: list[str] = Field(description="List of emoji categories")


class MultilingualResponse(BaseModel):
    """Response model for multilingual endpoint."""

    languages: list[str] = Field(description="Hellos in different languages and scripts")


class ToolInfo(BaseModel):
    """Information about an available tool."""

    name: str
    description: str


class ToolsResponse(BaseModel):
    """Response model for tools list endpoint."""

    tools: list[ToolInfo] = Field(description="Available MCP tools")


# ============================================================================
# FastAPI Endpoints
# ============================================================================


@app.get("/", tags=["Info"])
async def root():
    """Returns service version, description, and available endpoints."""
    logger.info("Root endpoint accessed")
    return {
        "name": "Unicode Example MCP Server",
        "version": "0.1.0",
        "description": "Example MCP server demonstrating Unicode support",
        "endpoints": {
            "GET /": "This help message",
            "GET /health": "Health check",
            "GET /api/tools": "List available MCP tools",
            "POST /api/tools/hello_unicode": "Invoke hello_unicode tool",
            "POST /api/tools/list_emoji_categories": "Invoke list_emoji_categories tool",
            "POST /api/tools/multilingual_hello": "Invoke multilingual_hello tool",
        },
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    logger.info("Health check passed")
    return {"status": "healthy"}


@app.get("/api/tools", tags=["Tools"], response_model=ToolsResponse)
async def get_tools(x_api_key: Optional[str] = Header(None)):
    """Returns list of available tools with descriptions."""
    if x_api_key and x_api_key != API_KEY:
        logger.warning(f"Unauthorized API key access attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info("Tools list requested")
    tools = [
        ToolInfo(
            name="hello_unicode",
            description="🌟 A tool that uses various Unicode characters in its description: 漢字 🎉",
        ),
        ToolInfo(
            name="list_emoji_categories",
            description="🎨 Tool that returns a list of emoji categories",
        ),
        ToolInfo(
            name="multilingual_hello",
            description="🔤 Tool that returns text in different scripts",
        ),
    ]
    return ToolsResponse(tools=tools)


@app.post("/api/tools/hello_unicode", tags=["Tools"], response_model=GreetingResponse)
async def api_hello_unicode(request: GreetingRequest, x_api_key: Optional[str] = Header(None)):
    """Invoke hello_unicode tool via REST API."""
    if x_api_key and x_api_key != API_KEY:
        logger.warning(f"Unauthorized API key access attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        logger.info(f"hello_unicode called with name='{request.name}', greeting='{request.greeting}'")
        message = hello_unicode(name=request.name, greeting=request.greeting)
        return GreetingResponse(message=message)
    except Exception as e:
        logger.error(f"Error in hello_unicode: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post(
    "/api/tools/list_emoji_categories",
    tags=["Tools"],
    response_model=EmojiCategoriesResponse,
)
async def api_list_emoji_categories(x_api_key: Optional[str] = Header(None)):
    """Invoke list_emoji_categories tool via REST API."""
    if x_api_key and x_api_key != API_KEY:
        logger.warning(f"Unauthorized API key access attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        logger.info("list_emoji_categories called")
        categories = list_emoji_categories()
        return EmojiCategoriesResponse(categories=categories)
    except Exception as e:
        logger.error(f"Error in list_emoji_categories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post(
    "/api/tools/multilingual_hello", tags=["Tools"], response_model=MultilingualResponse
)
async def api_multilingual_hello(x_api_key: Optional[str] = Header(None)):
    """Invoke multilingual_hello tool via REST API."""
    if x_api_key and x_api_key != API_KEY:
        logger.warning(f"Unauthorized API key access attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        logger.info("multilingual_hello called")
        result = multilingual_hello()
        languages = result.split("\n")
        return MultilingualResponse(languages=languages)
    except Exception as e:
        logger.error(f"Error in multilingual_hello: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# MCP Tools
# ============================================================================


@mcp.tool(description="🌟 A tool that uses various Unicode characters in its description:       漢字 🎉")
def hello_unicode(name: str = "世界", greeting: str = "Hola") -> str:
    """
    A simple tool that demonstrates Unicode handling in:
    - Tool description (emojis, accents, CJK characters)
    - Parameter defaults (CJK characters)
    - Return values (Spanish punctuation, emojis)
    """
    return f"{greeting}, {name}! 👋"


@mcp.tool(description="🎨 Tool that returns a list of emoji categories")
def list_emoji_categories() -> list[str]:
    """Returns a list of emoji categories with emoji examples."""
    return [
        "😀 Smileys & Emotion",
        "👋 People & Body",
        "🐶 Animals & Nature",
        "🍎 Food & Drink",
        "⚽ Activities",
        "🌍 Travel & Places",
        "💡 Objects",
        "❤️ Symbols",
        "🚩 Flags",
    ]


@mcp.tool(description="🔤 Tool that returns text in different scripts")
def multilingual_hello() -> str:
    """Returns hello in different scripts and writing systems."""
    return "\n".join(
        [
            "English: Hello!",
            "Spanish: Hola!",
            "French: Bonjour!",
            "German: Gr Gott!",
            "Russian: Привет!",
            "Greek: Γεια σας!",
            "Hebrew: !שָׁלוֹם",
            "Arabic: !مرحبا",
            "Hindi: नमस्ते!",
            "Chinese: 你好!",
            "Japanese: こんにちは!",
            "Korean: 안녕하세요!",
            "Thai: สวัสดี!",
        ]
    )




if __name__ == "__main__":
    import sys

    # Check if running as HTTP server or MCP server
    if "--http" in sys.argv:
        # Run as HTTP server with Uvicorn
        host = os.getenv("MCP_HOST", "127.0.0.1")
        port = int(os.getenv("MCP_PORT", "8000"))
        log_level = os.getenv("MCP_LOG_LEVEL", "info").lower()

        logger.info(f"Starting HTTP server on {host}:{port} with log level {log_level}")
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=log_level,
        )
    else:
        # Run as MCP server
        logger.info("Starting MCP server")
        mcp.run()



