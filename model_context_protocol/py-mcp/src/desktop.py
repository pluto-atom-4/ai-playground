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
from pathlib import Path
from typing import Any, Dict, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

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
        file_path = DESKTOP_PATH / filename

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
                "content": [{"type": "text", "text": f"Error: File not found: {filename}"}],
                "isError": True,
            }

        if not file_path.is_file():
            return {
                "content": [{"type": "text", "text": f"Error: {filename} is not a file"}],
                "isError": True,
            }

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        logger.info(f"Successfully read file: {filename}")
        return {
            "content": [{"type": "text", "text": content}],
            "isError": False,
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
        file_path = DESKTOP_PATH / filename

        # Security check
        if not file_path.resolve().is_relative_to(DESKTOP_PATH.resolve()):
            logger.warning(f"Security: Attempted access outside desktop: {file_path}")
            return json.dumps({"error": "Access denied - file outside desktop directory"})

        if not file_path.exists() or not file_path.is_file():
            return json.dumps({"error": f"File not found: {filename}"})

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        logger.info(f"Successfully read file resource: {filename}")
        return content
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
        file_path = DESKTOP_PATH / request.filename

        # Security check
        if not file_path.resolve().is_relative_to(DESKTOP_PATH.resolve()):
            logger.warning(f"Security: Attempted access outside desktop: {file_path}")
            raise HTTPException(status_code=403, detail="Access denied - file outside desktop directory")

        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail=f"File not found: {request.filename}")

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        file_size = file_path.stat().st_size
        logger.info(f"Read file: {request.filename} ({file_size} bytes)")

        return FileContentResponse(
            filename=request.filename,
            content=content,
            size=file_size
        )
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

if __name__ == "__main__":
    logger.info(f"Starting Desktop MCP Server on {HOST}:{PORT}")
    logger.info(f"Desktop path: {DESKTOP_PATH}")
    logger.info(f"Desktop exists: {DESKTOP_PATH.exists()}")

    try:
        uvicorn.run(
            app,
            host=HOST,
            port=PORT,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Desktop MCP Server stopped by user (CTRL+C)")
        exit(0)

