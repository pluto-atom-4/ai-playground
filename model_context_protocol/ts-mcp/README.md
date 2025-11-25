# MCP TypeScript Example

This project demonstrates how to use the Model Context Protocol (MCP) TypeScript SDK to build and run a simple streamable HTTP server locally without cloning the entire repository.

## Setup

### Prerequisites
- Node.js 18+
- pnpm

### Installation

All dependencies have been installed via `pnpm install`. The key packages are:

- `@modelcontextprotocol/sdk@^1.22.0` - MCP SDK
- `express@^5.0.1` - Web framework
- `cors@^2.8.5` - CORS middleware
- `zod@^3.23.8` - TypeScript-first schema validation
- `tsx@^4.16.5` - TypeScript execution for Node.js

## Project Structure

```
src/
├── index.ts                                      # Main entry point
└── simpleStreamableHttp/
    ├── simpleStreamableHttp.ts                   # MCP Server
    └── simpleStreamableHttpClient.ts             # MCP Client (for testing)
```

## Running the Examples

### Start the Server

```bash
cd ~/Documents/JetBrains/ai-playground/model_context_protocol/ts-mcp
pnpm server
```

This will start the MCP server on `http://localhost:3000` with:
- MCP endpoint: `http://localhost:3000/mcp`
- Health check: `http://localhost:3000/health`

### Run the Client (in another terminal)

```bash
cd ~/Documents/JetBrains/ai-playground/model_context_protocol/ts-mcp
pnpm client
```

This will connect to the running server and test the available tools:
- `greet` - A simple greeting tool
- `add` - Add two numbers together

### Watch Mode (for development)

```bash
cd ~/Documents/JetBrains/ai-playground/model_context_protocol/ts-mcp
pnpm server:watch
```

This will automatically restart the server when files change.

## Building

To compile TypeScript to JavaScript:

```bash
cd ~/Documents/JetBrains/ai-playground/model_context_protocol/ts-mcp
pnpm build
```

Output will be in the `dist/` directory.

## Example Tools

### Greet Tool
Accepts a name and returns a greeting message.

**Input:**
```json
{
  "name": "Alice"
}
```

**Output:**
```
Hello, Alice! 👋
```

### Add Tool
Accepts two numbers and returns their sum.

**Input:**
```json
{
  "a": 5,
  "b": 3
}
```

**Output:**
```
5 + 3 = 8
```

## Development

The `simpleStreamableHttp.ts` server demonstrates:
- Creating an MCP server with the SDK
- Registering multiple tools
- Using the StreamableHTTPServerTransport
- Setting up Express routes for the MCP endpoint
- Adding health check and status endpoints

You can extend this example by:
1. Adding more tools via `server.registerTool()`
2. Adding resources via `server.registerResource()`
3. Adding prompts via `server.registerPrompt()`
4. Implementing custom authentication/authorization

## References

- [MCP SDK Documentation](https://github.com/modelcontextprotocol/typescript-sdk)
- [MCP Examples](https://github.com/modelcontextprotocol/typescript-sdk/tree/main/src/examples)

