"""
FastMCP Echo Server
"""

from mcp.server.fastmcp import FastMCP

# Create an MCP server instance
mcp = FastMCP("EchoServer", json_response=True)

@mcp.tool(
    name="echo",
    description="Echo a string back to the caller"
)
def echo_tool(message: str):
    return {
        "content": [{"type": "text", "text": message}],
        "isError": False,
    }

@mcp.resource("echo://static")
def echo_resource() -> str:
    return "Echo Resource Content"

@mcp.resource(
    "echo://{text}"
)
def echo_template(text: str) -> str:
    return f"Echoed: {text}"


@mcp.prompt("Echo")
def echo_prompt(text: str) -> str:
    return f"Echo Prompt: {text}"

if __name__ == "__main__":
    mcp.run()
