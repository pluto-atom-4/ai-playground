"""
Desktop MCP Server - Exposes desktop directory as a resource using FastMCP.

This server provides tools and resources to browse and interact with the desktop directory.
It follows the MCP server guidelines with:
- FastAPI for RESTful API endpoints
- Pydantic models for validation
- Comprehensive logging
- API key authentication
- RESTful endpoints for tools and resources
"""

import logging
import os
import json
import sys
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import click

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("mcp.desktop.server")

# Configuration
API_KEY = os.getenv("MCP_API_KEY", "default-api-key-change-me")
HOST = os.getenv("MCP_HOST", "127.0.0.1")
PORT = int(os.getenv("MCP_PORT", 8000))

# Get desktop directory
DESKTOP_PATH = Path.home() / "Desktop"

# Create an MCP server instance
mcp = FastMCP("DesktopServer", json_response=True)


# ==================== Helper Functions ====================

def normalize_filename(filename: str) -> str:
    """
    Normalize and validate filename to prevent path traversal attacks.

    - Extracts only the basename (filename without directory path)
    - Rejects filenames with path separators (/, \, ..)
    - Returns only the filename component

    Args:
        filename: The input filename which may contain path separators

    Returns:
        Normalized basename

    Raises:
        ValueError: If filename contains path traversal attempts
    """
    if not filename:
        raise ValueError("Filename cannot be empty")

    # Normalize path separators and extract basename
    # Convert backslashes to forward slashes for consistent handling
    normalized = filename.replace("\\", "/")

    # Extract basename (last component after any slashes)
    basename = Path(normalized).name

    # Check if the original filename contained path separators
    # If it did and basename is different, it means a path was provided
    if "/" in normalized or "\\" in filename:
        logger.warning(f"Path traversal attempt detected: {filename}")
        raise ValueError(f"Filename cannot contain path separators: {filename}")

    # Check for parent directory references
    if ".." in filename or basename != filename:
        logger.warning(f"Invalid filename with directory components: {filename}")
        raise ValueError(f"Filename cannot contain directory paths: {filename}")

    return basename


# ==================== MCP Tools ====================

@mcp.tool(
    name="list_desktop_files",
    description="List all files and directories on the desktop"
)
def list_desktop_files() -> Dict[str, Any]:
    """List all files and directories on the desktop."""
    logger.info(f"list_desktop_files called for path: {DESKTOP_PATH}")
    try:
        items = []
        if DESKTOP_PATH.exists():
            for item in sorted(DESKTOP_PATH.iterdir()):
                item_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "path": str(item),
                    "size": item.stat().st_size if item.is_file() else None,
                }
                items.append(item_info)

        logger.info(f"Found {len(items)} items on desktop")
        return {
            "content": [{"type": "text", "text": json.dumps(items, indent=2)}],
            "isError": False,
        }
    except Exception as e:
        logger.error(f"Error listing desktop files: {e}")
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True,
        }


@mcp.tool(
    name="get_file_content",
    description="Read the content of a file on the desktop",
)
def get_file_content(filename: str) -> Dict[str, Any]:
    """Read the content of a file on the desktop."""
    logger.info(f"get_file_content called for file: {filename}")
    try:
        # Normalize and validate filename to prevent path traversal
        normalized_filename = normalize_filename(filename)
        file_path = DESKTOP_PATH / normalized_filename

        # Security: Ensure the file is within desktop directory
        if not file_path.resolve().is_relative_to(DESKTOP_PATH.resolve()):
            logger.warning(f"Security: Attempted access outside desktop directory: {file_path}")
            return {
                "content": [{"type": "text", "text": "Error: Access denied - file outside desktop directory"}],
                "isError": True,
            }

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return {
                "content": [{"type": "text", "text": f"Error: File not found: {normalized_filename}"}],
                "isError": True,
            }

        if not file_path.is_file():
            return {
                "content": [{"type": "text", "text": f"Error: {normalized_filename} is not a file"}],
                "isError": True,
            }

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        logger.info(f"Successfully read file: {normalized_filename}")
        return {
            "content": [{"type": "text", "text": content}],
            "isError": False,
        }
    except ValueError as e:
        logger.warning(f"Invalid filename: {e}")
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True,
        }
    except Exception as e:
        logger.error(f"Error reading file {filename}: {e}")
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True,
        }


@mcp.tool(
    name="get_desktop_stats",
    description="Get statistics about the desktop directory"
)
def get_desktop_stats() -> Dict[str, Any]:
    """Get statistics about the desktop directory."""
    logger.info("get_desktop_stats called")
    try:
        total_files = 0
        total_dirs = 0
        total_size = 0

        if DESKTOP_PATH.exists():
            for item in DESKTOP_PATH.iterdir():
                if item.is_file():
                    total_files += 1
                    total_size += item.stat().st_size
                elif item.is_dir():
                    total_dirs += 1

        stats = {
            "desktop_path": str(DESKTOP_PATH),
            "total_files": total_files,
            "total_directories": total_dirs,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }

        logger.info(f"Desktop stats: {stats}")
        return {
            "content": [{"type": "text", "text": json.dumps(stats, indent=2)}],
            "isError": False,
        }
    except Exception as e:
        logger.error(f"Error getting desktop stats: {e}")
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True,
        }


# ==================== MCP Resources ====================

@mcp.resource("desktop://files")
def desktop_files_resource() -> str:
    """Resource listing all files on the desktop."""
    logger.info("desktop_files_resource called")
    try:
        items = []
        if DESKTOP_PATH.exists():
            for item in sorted(DESKTOP_PATH.iterdir()):
                items.append(item.name)
        return json.dumps({"files": items, "path": str(DESKTOP_PATH)}, indent=2)
    except Exception as e:
        logger.error(f"Error reading desktop files resource: {e}")
        return json.dumps({"error": str(e)})


@mcp.resource("desktop://stats")
def desktop_stats_resource() -> str:
    """Resource with desktop directory statistics."""
    logger.info("desktop_stats_resource called")
    try:
        total_files = 0
        total_dirs = 0
        total_size = 0

        if DESKTOP_PATH.exists():
            for item in DESKTOP_PATH.iterdir():
                if item.is_file():
                    total_files += 1
                    total_size += item.stat().st_size
                elif item.is_dir():
                    total_dirs += 1

        stats = {
            "desktop_path": str(DESKTOP_PATH),
            "total_files": total_files,
            "total_directories": total_dirs,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }
        return json.dumps(stats, indent=2)
    except Exception as e:
        logger.error(f"Error reading desktop stats resource: {e}")
        return json.dumps({"error": str(e)})


@mcp.resource("desktop://file/{filename}")
def desktop_file_resource(filename: str) -> str:
    """Resource to access a specific file on the desktop."""
    logger.info(f"desktop_file_resource called for: {filename}")
    try:
        # Normalize and validate filename to prevent path traversal
        normalized_filename = normalize_filename(filename)
        file_path = DESKTOP_PATH / normalized_filename

        # Security check
        if not file_path.resolve().is_relative_to(DESKTOP_PATH.resolve()):
            logger.warning(f"Security: Attempted access outside desktop: {file_path}")
            return json.dumps({"error": "Access denied - file outside desktop directory"})

        if not file_path.exists() or not file_path.is_file():
            return json.dumps({"error": f"File not found: {normalized_filename}"})

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        logger.info(f"Successfully read file resource: {normalized_filename}")
        return content
    except ValueError as e:
        logger.warning(f"Invalid filename in resource: {e}")
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"Error reading file resource {filename}: {e}")
        return json.dumps({"error": str(e)})


# ==================== FastAPI HTTP API ====================

app = FastAPI(
    title="Desktop MCP Server",
    version="1.0.0",
    description="MCP Server exposing the desktop directory as a resource"
)


# Request/Response models
class ListFilesResponse(BaseModel):
    """Response model for listing files."""
    files: List[Dict[str, Any]] = Field(..., description="List of files and directories")
    count: int = Field(..., description="Total count of items")


class FileContentRequest(BaseModel):
    """Request model for file content."""
    filename: str = Field(..., description="Name of the file to read")


class FileContentResponse(BaseModel):
    """Response model for file content."""
    filename: str = Field(..., description="Name of the file")
    content: str = Field(..., description="File content")
    size: int = Field(..., description="File size in bytes")


class StatsResponse(BaseModel):
    """Response model for desktop statistics."""
    desktop_path: str = Field(..., description="Path to desktop directory")
    total_files: int = Field(..., description="Total number of files")
    total_directories: int = Field(..., description="Total number of directories")
    total_size_bytes: int = Field(..., description="Total size in bytes")
    total_size_mb: float = Field(..., description="Total size in megabytes")


# API Key validation
def validate_api_key(x_api_key: str = Header(...)) -> str:
    """Validate API key from request header."""
    if x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key[:10]}...")
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


@app.get("/", tags=["Info"])
async def root():
    """Get service information."""
    logger.info("GET / called")
    return {
        "name": "Desktop MCP Server",
        "version": "1.0.0",
        "description": "MCP Server exposing the desktop directory as a resource",
        "endpoints": {
            "info": "GET /api/info",
            "health": "GET /health",
            "tools": "GET /api/tools",
            "resources": "GET /api/resources",
            "list_files": "GET /api/desktop/files",
            "get_file": "POST /api/desktop/file",
            "get_stats": "GET /api/desktop/stats",
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    logger.info("GET /health called")
    return {
        "status": "healthy",
        "desktop_path": str(DESKTOP_PATH),
        "exists": DESKTOP_PATH.exists()
    }


@app.get("/api/info", tags=["Info"])
async def get_info(api_key: str = Depends(validate_api_key)):
    """Get server information and available endpoints."""
    logger.info("GET /api/info called")
    return {
        "name": "Desktop MCP Server",
        "version": "1.0.0",
        "status": "running",
        "desktop_path": str(DESKTOP_PATH),
        "tools": [
            {
                "name": "list_desktop_files",
                "description": "List all files and directories on the desktop"
            },
            {
                "name": "get_file_content",
                "description": "Read the content of a file on the desktop"
            },
            {
                "name": "get_desktop_stats",
                "description": "Get statistics about the desktop directory"
            },
        ],
        "resources": [
            {"uri": "desktop://files", "description": "List of desktop files"},
            {"uri": "desktop://stats", "description": "Desktop statistics"},
            {"uri": "desktop://file/{filename}", "description": "Access specific desktop file"},
        ]
    }


@app.get("/api/tools", tags=["Tools"])
async def list_tools(api_key: str = Depends(validate_api_key)):
    """Get list of available tools."""
    logger.info("GET /api/tools called")
    return {
        "tools": [
            {
                "name": "list_desktop_files",
                "description": "List all files and directories on the desktop"
            },
            {
                "name": "get_file_content",
                "description": "Read the content of a file on the desktop",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the file to read"
                        }
                    },
                    "required": ["filename"]
                }
            },
            {
                "name": "get_desktop_stats",
                "description": "Get statistics about the desktop directory"
            },
        ]
    }


@app.get("/api/resources", tags=["Resources"])
async def list_resources(api_key: str = Depends(validate_api_key)):
    """Get list of available resources."""
    logger.info("GET /api/resources called")
    return {
        "resources": [
            {
                "uri": "desktop://files",
                "description": "List of desktop files"
            },
            {
                "uri": "desktop://stats",
                "description": "Desktop statistics"
            },
            {
                "uri": "desktop://file/{filename}",
                "description": "Access specific desktop file"
            },
        ]
    }


@app.get("/api/desktop/files", response_model=ListFilesResponse, tags=["Desktop"])
async def list_desktop_files_endpoint(api_key: str = Depends(validate_api_key)):
    """List all files and directories on the desktop."""
    logger.info("GET /api/desktop/files called")
    try:
        items = []
        if DESKTOP_PATH.exists():
            for item in sorted(DESKTOP_PATH.iterdir()):
                item_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                }
                items.append(item_info)

        logger.info(f"Listed {len(items)} items from desktop")
        return ListFilesResponse(files=items, count=len(items))
    except Exception as e:
        logger.error(f"Error listing desktop files: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")


@app.post("/api/desktop/file", response_model=FileContentResponse, tags=["Desktop"])
async def get_file_endpoint(
    request: FileContentRequest,
    api_key: str = Depends(validate_api_key)
):
    """Read the content of a file on the desktop."""
    logger.info(f"POST /api/desktop/file called for: {request.filename}")
    try:
        # Normalize and validate filename to prevent path traversal
        normalized_filename = normalize_filename(request.filename)
        file_path = DESKTOP_PATH / normalized_filename

        # Security check
        if not file_path.resolve().is_relative_to(DESKTOP_PATH.resolve()):
            logger.warning(f"Security: Attempted access outside desktop: {file_path}")
            raise HTTPException(status_code=403, detail="Access denied - file outside desktop directory")

        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail=f"File not found: {normalized_filename}")

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        file_size = file_path.stat().st_size
        logger.info(f"Read file: {normalized_filename} ({file_size} bytes)")

        return FileContentResponse(
            filename=normalized_filename,
            content=content,
            size=file_size
        )
    except ValueError as e:
        logger.warning(f"Invalid filename in request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading file {request.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@app.get("/api/desktop/stats", response_model=StatsResponse, tags=["Desktop"])
async def get_stats_endpoint(api_key: str = Depends(validate_api_key)):
    """Get statistics about the desktop directory."""
    logger.info("GET /api/desktop/stats called")
    try:
        total_files = 0
        total_dirs = 0
        total_size = 0

        if DESKTOP_PATH.exists():
            for item in DESKTOP_PATH.iterdir():
                if item.is_file():
                    total_files += 1
                    total_size += item.stat().st_size
                elif item.is_dir():
                    total_dirs += 1

        logger.info(f"Desktop stats: {total_files} files, {total_dirs} dirs, {total_size} bytes")

        return StatsResponse(
            desktop_path=str(DESKTOP_PATH),
            total_files=total_files,
            total_directories=total_dirs,
            total_size_bytes=total_size,
            total_size_mb=round(total_size / (1024 * 1024), 2)
        )
    except Exception as e:
        logger.error(f"Error getting desktop stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


# ==================== Main ====================

@click.command()
@click.option(
    "--mode",
    type=click.Choice(["http", "stdio"], case_sensitive=False),
    default="stdio",
    help="Server mode: http (REST API) or stdio (MCP protocol, default)",
)
@click.option(
    "--host",
    default="127.0.0.1",
    help="Host for HTTP mode (default: 127.0.0.1)",
)
@click.option(
    "--port",
    type=int,
    default=8000,
    help="Port for HTTP mode (default: 8000)",
)
def main(mode: str = "stdio", host: str = "127.0.0.1", port: int = 8000) -> int:
    """Start the Desktop MCP Server in stdio or HTTP mode."""
    logger.info("=" * 80)
    logger.info("DESKTOP MCP SERVER STARTUP")
    logger.info("=" * 80)
    logger.info(f"Server: DesktopServer")
    logger.info(f"Desktop Path: {DESKTOP_PATH}")
    logger.info(f"Mode: {mode.upper()}")

    if mode.lower() == "stdio":
        # MCP Protocol Mode - for use with mcp dev inspector
        logger.info("Starting in MCP STDIO mode for MCP protocol communication")
        logger.info("This mode is used with: mcp dev src/desktop.py")
        logger.info("=" * 80)

        try:
            # Run MCP server over stdio (standard input/output)
            # This allows mcp dev inspector to communicate with the server
            asyncio.run(mcp.run_stdio())
            return 0
        except KeyboardInterrupt:
            logger.info("Desktop MCP Server stopped by user (CTRL+C)")
            return 0
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            return 1
    else:
        # HTTP Mode - for REST API
        logger.info(f"Starting in HTTP mode on {host}:{port}")
        logger.info("This mode is used with: uvicorn src.desktop:app")
        logger.info("=" * 80)

        try:
            uvicorn.run(
                app,
                host=host,
                port=port,
                log_level="info"
            )
            return 0
        except KeyboardInterrupt:
            logger.info("Desktop MCP Server stopped by user (CTRL+C)")
            return 0
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            return 1


if __name__ == "__main__":
    exit(main())

