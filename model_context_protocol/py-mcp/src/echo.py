"""
FastMCP Echo Server with RESTful HTTP API
Exposes HTTP endpoints for tools, resources, and prompts
"""

import logging
import uvicorn
from typing import Any, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("mcp.echo.server")

# Create an MCP server instance
mcp = FastMCP("EchoServer", json_response=True)

@mcp.tool(
    name="echo",
    description="Echo a string back to the caller"
)
def echo_tool(message: str):
    logger.info(f"echo_tool called with message: {message}")
    return {
        "content": [{"type": "text", "text": message}],
        "isError": False,
    }

@mcp.resource("echo://static")
def echo_resource() -> str:
    logger.info("echo_resource called")
    return "Echo Resource Content"

@mcp.resource(
    "echo://{text}"
)
def echo_template(text: str) -> str:
    logger.info(f"echo_template called with text: {text}")
    return f"Echoed: {text}"


@mcp.prompt("Echo")
def echo_prompt(text: str) -> str:
    logger.info(f"echo_prompt called with text: {text}")
    return f"Echo Prompt: {text}"


# Create FastAPI app for HTTP API
app = FastAPI(title="MCP Echo Server", version="1.0.0")


# Request/Response models
class ToolArguments(BaseModel):
    message: str = None


class ToolRequest(BaseModel):
    arguments: Dict[str, Any] = {}


class ResourceRequest(BaseModel):
    uri: str


class PromptRequest(BaseModel):
    arguments: Dict[str, Any] = {}


@app.get("/api/info")
async def get_info():
    """Get server information and health status"""
    try:
        # Await the async methods to get the responses
        tools_response = await mcp.list_tools() if hasattr(mcp, 'list_tools') else None
        resources_response = await mcp.list_resource_templates() if hasattr(mcp, 'list_resource_templates') else None
        prompts_response = await mcp.list_prompts() if hasattr(mcp, 'list_prompts') else None

        return {
            "name": "Echo MCP Server",
            "version": "1.0.0",
            "status": "running",
            "tools": [
                {"name": t.name, "description": t.description}
                for t in (tools_response.tools if tools_response else [])
            ],
            "resources": [
                {"uri": r.uriTemplate}
                for r in (resources_response.resources if resources_response else [])
            ],
            "prompts": [
                {"name": p.name}
                for p in (prompts_response.prompts if prompts_response else [])
            ],
        }
    except Exception as e:
        logger.error(f"Error getting server info: {e}")
        return {
            "name": "Echo MCP Server",
            "version": "1.0.0",
            "status": "error",
            "error": str(e),
            "tools": [],
            "resources": [],
            "prompts": [],
        }


@app.get("/api/tools")
async def list_tools():
    """List all available tools"""
    try:
        # Await the async method
        tools_response = await mcp.list_tools()
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema if hasattr(tool, 'inputSchema') else {}
                }
                for tool in tools_response.tools
            ]
        }
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        return {"tools": []}


@app.post("/api/tools/{tool_name}")
async def call_tool(tool_name: str, request: ToolRequest):
    """Call a tool with arguments"""
    logger.info(f"Calling tool: {tool_name} with arguments: {request.arguments}")

    try:
        if tool_name == "echo":
            message = request.arguments.get("message", "")
            result = echo_tool(message)
            return result
        else:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True,
        }


@app.get("/api/resources")
async def list_resources():
    """List all available resources"""
    try:
        # Await the async method
        resources_response = await mcp.list_resource_templates()
        return {
            "resources": [
                {
                    "uri": resource.uriTemplate,
                    "name": resource.name if hasattr(resource, 'name') else resource.uriTemplate,
                    "description": resource.description if hasattr(resource, 'description') else ""
                }
                for resource in resources_response.resources
            ]
        }
    except Exception as e:
        logger.error(f"Error listing resources: {e}")
        return {"resources": []}


@app.get("/api/resources/{resource_path:path}")
async def get_resource(resource_path: str):
    """Get a resource by path"""
    logger.info(f"Getting resource: {resource_path}")

    try:
        # Handle static resource
        if resource_path == "echo/static":
            result = echo_resource()
            return {"content": result}

        # Handle template resource (echo/{text})
        elif resource_path.startswith("echo/"):
            text = resource_path[5:]  # Remove "echo/" prefix
            result = echo_template(text)
            return {"content": result}

        else:
            raise HTTPException(status_code=404, detail=f"Resource '{resource_path}' not found")
    except Exception as e:
        logger.error(f"Error getting resource {resource_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/prompts")
async def list_prompts():
    """List all available prompts"""
    try:
        # Await the async method
        prompts_response = await mcp.list_prompts()
        return {
            "prompts": [
                {
                    "name": prompt.name,
                    "description": prompt.description if hasattr(prompt, 'description') else "",
                    "arguments": prompt.arguments if hasattr(prompt, 'arguments') else []
                }
                for prompt in prompts_response.prompts
            ]
        }
    except Exception as e:
        logger.error(f"Error listing prompts: {e}")
        return {"prompts": []}


@app.post("/api/prompts/{prompt_name}")
async def call_prompt(prompt_name: str, request: PromptRequest):
    """Call a prompt with arguments"""
    logger.info(f"Calling prompt: {prompt_name} with arguments: {request.arguments}")

    try:
        if prompt_name == "Echo":
            text = request.arguments.get("text", "")
            result = echo_prompt(text)
            return {"content": result}
        else:
            raise HTTPException(status_code=404, detail=f"Prompt '{prompt_name}' not found")
    except Exception as e:
        logger.error(f"Error calling prompt {prompt_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint - API documentation"""
    return {
        "message": "MCP Echo Server API",
        "endpoints": {
            "GET /api/info": "Server information and health status",
            "GET /api/tools": "List all available tools",
            "POST /api/tools/{tool_name}": "Call a tool",
            "GET /api/resources": "List all available resources",
            "GET /api/resources/{path}": "Get a resource",
            "GET /api/prompts": "List all available prompts",
            "POST /api/prompts/{name}": "Call a prompt",
        }
    }


if __name__ == "__main__":
    logger.info("Starting Echo MCP server with HTTP API on http://127.0.0.1:8000")
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except KeyboardInterrupt:
        logger.info("Echo MCP server stopped by user (CTRL+C)")
        exit(0)

