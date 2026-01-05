from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

app = FastAPI()

@app.post("/echo", operation_id="echo_request")
async def echo_request(message: str):
    """Echoes back the received message."""
    return {"echo": message}

mcp = FastApiMCP(app, name="EchoService")
# Mount HTTP transport for MCP endpoints
mcp.mount_http()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
