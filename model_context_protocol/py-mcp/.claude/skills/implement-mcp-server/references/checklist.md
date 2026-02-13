# MCP Server Implementation - Checklists & Decision Trees

## Decision Tree: Choosing Server Implementation

```
┌─ Do you need HTTP endpoints (REST API)?
│  ├─ YES → Use StreamableHTTPSessionManager + Starlette
│  │        Keep --port option
│  │        Mount at /mcp path
│  │
│  └─ NO → Use stdio transport (FastMCP.run())
│           Omit --port option
│           Simpler, recommended for most cases
│
├─ Do you need pagination?
│  ├─ YES → Use cursor-based pagination
│  │        String format for cursors
│  │        Log warnings (not errors) for invalid cursors
│  │        Include nextCursor in response
│  │
│  └─ NO → Simple list endpoints
│           No pagination logic needed
│
├─ Do you need resource reading?
│  ├─ YES → Use @mcp.resource() decorator
│  │        Implement read_resource function
│  │        Return TextContent
│  │
│  └─ NO → Skip resource handlers
│
├─ Do you need prompt templates?
│  ├─ YES → Use @mcp.tool() for prompt retrieval
│  │        Return List[PromptMessage]
│  │        Support optional arguments
│  │
│  └─ NO → Skip prompt handlers
│
└─ Do you need authentication?
   ├─ YES → Use environment variables for keys
   │        Validate in tool implementation
   │        Return error for invalid auth
   │
   └─ NO → Public tools (skip auth)
```

## Implementation Checklist

### Phase 1: Project Setup
- [ ] Create server directory: `src/servers/my_server/`
- [ ] Create server file: `my_server.py`
- [ ] Create/update `__main__.py` entry point
- [ ] Add `.env` with `LOG_LEVEL=INFO`
- [ ] Verify imports: FastMCP, logging, dotenv, click, pydantic

### Phase 2: Basic Server Structure
- [ ] Import FastMCP and create server instance
- [ ] Configure logging with LOG_LEVEL environment variable
- [ ] Set up CLI command with click
- [ ] Add `--log-level` option to main()
- [ ] Implement main() to call `mcp.run()`
- [ ] Test server starts without errors: `python -m src.servers.my_server`

### Phase 3: Tool Implementation
For each tool to implement:
- [ ] Create Pydantic input model (BaseModel with fields)
- [ ] Create Pydantic output model
- [ ] Implement async function decorated with `@mcp.tool(name="...", description="...")`
- [ ] Add input validation in function signature
- [ ] Add logging at DEBUG, INFO, WARNING, ERROR levels
- [ ] Handle exceptions with try/except
- [ ] Return output model instance

### Phase 4: Pagination Support (If Needed)
- [ ] Add optional `cursor: Optional[str] = None` parameter to input model
- [ ] Add `limit: int = 10` parameter (or appropriate default)
- [ ] Add cursor parsing with try/except ValueError
- [ ] Log warning for invalid cursor format (not raise exception)
- [ ] Calculate offset from cursor or default to 0
- [ ] Generate `nextCursor` string if more items exist
- [ ] Include `nextCursor` in output model (Optional[str] = None)

### Phase 5: Resource Support (If Needed)
- [ ] Create resource handler function
- [ ] Decorate with `@mcp.resource(uri_pattern="...")`
- [ ] Implement resource reading logic
- [ ] Add logging for reads
- [ ] Return TextContent or error message
- [ ] Handle not-found cases gracefully

### Phase 6: Prompt Support (If Needed)
- [ ] Create helper function to build PromptMessage list
- [ ] Create `@mcp.tool()` handler for prompt retrieval
- [ ] Accept optional arguments in input model
- [ ] Build messages based on arguments
- [ ] Return proper output structure
- [ ] Log prompt retrieval and errors

### Phase 7: Logging Enhancement
- [ ] Add logger at module level: `logger = logging.getLogger("server-name")`
- [ ] Log server startup: `logger.info("Starting {name}")`
- [ ] Log each tool invocation: `logger.debug("Tool: {name}, args: {args}")`
- [ ] Log successful completions: `logger.info("Task completed")`
- [ ] Log errors with traceback: `logger.error("Error: {msg}", exc_info=True)`
- [ ] Log warnings for validation: `logger.warning("Invalid input: {reason}")`
- [ ] Log shutdown: `logger.info("Server stopped")`

### Phase 8: Error Handling
- [ ] Wrap tool logic in try/except
- [ ] Catch specific exceptions (ValueError, FileNotFoundError, etc.)
- [ ] Return error status in output model
- [ ] Log all errors with context
- [ ] Include exception info in error logs: `exc_info=True`
- [ ] Return user-friendly error messages
- [ ] Don't expose stack traces in responses

### Phase 9: Testing
- [ ] Create test file: `tests/test_my_server.py`
- [ ] Test each tool with valid inputs
- [ ] Test invalid input handling (validation errors)
- [ ] Test error cases (not found, invalid params, etc.)
- [ ] Test pagination cursor validation
- [ ] Test logging output (capture logs in pytest)
- [ ] Run tests: `pytest tests/test_my_server.py -v`

### Phase 10: CLI Configuration
- [ ] Remove `--port` option (unless HTTP transport needed)
- [ ] Add `--log-level` option with choices: DEBUG, INFO, WARNING, ERROR
- [ ] Update main() to accept log_level parameter
- [ ] Set logging level before starting server
- [ ] Log the configured level
- [ ] Handle SIGINT (Ctrl+C) gracefully
- [ ] Return exit code: 0 for success, 1 for error

### Phase 11: Entry Point Setup
- [ ] Create or update `__main__.py`
- [ ] Import main function from server module
- [ ] Call main() and pass exit code
- [ ] Test entry point: `python -m src.servers.my_server`

### Phase 12: Documentation
- [ ] Add docstrings to tool functions
- [ ] Document input parameters in Pydantic models
- [ ] Document output structure
- [ ] Create README for server
- [ ] Document pagination cursor format (if applicable)
- [ ] Document environment variables

### Phase 13: Final Validation
- [ ] Server starts without errors
- [ ] All tools execute successfully
- [ ] Pagination works with cursors
- [ ] Error handling graceful
- [ ] Logging appears at correct levels
- [ ] No `if __name__ == "__main__"` in server file
- [ ] __main__.py entry point works
- [ ] Tests pass: `pytest tests/test_my_server.py`

## Logging Configuration Checklist

### Initial Setup
- [ ] Import logging: `import logging`
- [ ] Load env: `load_dotenv()`
- [ ] Get LOG_LEVEL: `log_level = os.getenv("LOG_LEVEL", "INFO")`
- [ ] Configure: `logging.basicConfig(level=getattr(logging, log_level), ...)`
- [ ] Create logger: `logger = logging.getLogger("server-name")`

### Log Levels Usage
- [ ] **DEBUG** - Tool invocation details, parameter values, function flow
- [ ] **INFO** - Server startup, successful operations, important state changes
- [ ] **WARNING** - Invalid cursors, unexpected conditions, recoverable issues
- [ ] **ERROR** - Exceptions, failed operations, with `exc_info=True`

### Log Messages
- [ ] Server startup: `logger.info("Starting {ServerName} MCP Server")`
- [ ] Log level set: `logger.info("Set logging level to {LEVEL}")`
- [ ] Tool invoked: `logger.debug("Tool invoked: {name} with args: {args}")`
- [ ] Validation warning: `logger.warning("Invalid {field}: {value}")`
- [ ] Success: `logger.info("Successfully {action}")`
- [ ] Error: `logger.error("Failed to {action}: {error}", exc_info=True)`
- [ ] Shutdown: `logger.info("Server stopped by user (CTRL+C)")`

## Pagination Implementation Checklist

### Cursor Design
- [ ] Use string-based cursors (not numeric offsets exposed directly)
- [ ] Cursor format: string representation of offset (e.g., "10", "20")
- [ ] Make cursor opaque to client (implementation detail)
- [ ] Include cursor in request parameters: `cursor: Optional[str] = None`
- [ ] Return nextCursor in response: `nextCursor: Optional[str] = None`

### Cursor Validation
- [ ] Parse cursor with try/except ValueError
- [ ] Log warning (not error) for invalid format
- [ ] Default to offset 0 if cursor invalid
- [ ] Never raise exception for bad cursor
- [ ] Example: `logger.warning(f"Invalid cursor format: {cursor}")`

### Pagination Logic
- [ ] Calculate offset from cursor or use 0
- [ ] Fetch items from offset to offset+limit
- [ ] Generate next cursor only if more items exist
- [ ] Set nextCursor to None for last page
- [ ] Example: `nextCursor = str(offset + limit) if len(items) == limit else None`

### Response Structure
- [ ] Include items list in response
- [ ] Include nextCursor (Optional[str])
- [ ] Include totalCount if available (Optional[int])
- [ ] Include hasMost if helpful (Optional[bool])
- [ ] Consistent response structure across endpoints

## Refactoring Conversion Matrix

| Old Pattern | New Pattern | Example |
|------------|------------|---------|
| `@app.call_tool()` | `@mcp.tool()` | `@mcp.tool(name="search")` |
| Handler with dict args | Pydantic model input | `SearchInput` class |
| Print statements | logger calls | `logger.info("message")` |
| `--port` CLI option | Omit (or env var) | Remove from click.option |
| Raw dict return | Pydantic model output | `SearchOutput` class |
| Exception raises | Log and return error | `logger.error(...); return error_output` |
| `if __name__ == "__main__"` | Remove completely | Delete block, use __main__.py |
| Main app.run() | mcp.run() | Call inside main() |

## Common Migration Patterns

### Pattern 1: Simple Tool
```python
# Before
@app.call_tool()
def call_tool(name, arguments):
    if name == "search":
        return {"result": search_impl(arguments["query"])}

# After
@mcp.tool(name="search", description="Search items")
async def search(input_data: SearchInput) -> SearchOutput:
    logger.debug(f"Searching: {input_data.query}")
    result = search_impl(input_data.query)
    return SearchOutput(result=result)
```

### Pattern 2: List with Pagination
```python
# Before
@app.call_tool()
def call_tool(name, arguments):
    if name == "list":
        cursor = arguments.get("cursor")
        items = get_items(cursor)
        return {"items": items}

# After
@mcp.tool(name="list", description="List items")
async def list_items(input_data: ListInput) -> ListOutput:
    logger.debug(f"Listing with cursor: {input_data.cursor}")
    offset = parse_cursor(input_data.cursor)
    items = get_items(offset, input_data.limit)
    next_cursor = str(offset + input_data.limit) if len(items) == input_data.limit else None
    return ListOutput(items=items, nextCursor=next_cursor)
```

### Pattern 3: Error Handling
```python
# Before
def call_tool(name, arguments):
    try:
        # ...
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

# After
@mcp.tool(name="action")
async def action(input_data: ActionInput) -> ActionOutput:
    try:
        result = perform_action(input_data)
        logger.info("Action completed")
        return ActionOutput(result=result, status="success")
    except ValueError as e:
        logger.warning(f"Invalid input: {e}")
        return ActionOutput(result="", status="error")
    except Exception as e:
        logger.error(f"Action failed: {e}", exc_info=True)
        return ActionOutput(result="", status="error")
```

## Troubleshooting Checklist

### Server Won't Start
- [ ] Check `mcp.run()` is called in main()
- [ ] Verify FastMCP is imported correctly
- [ ] Check for syntax errors in file
- [ ] Verify LOG_LEVEL is set correctly
- [ ] Check stdin/stdout are available

### Tools Not Registered
- [ ] Verify `@mcp.tool()` decorator used (not `@app.call_tool()`)
- [ ] Check tool name and description provided
- [ ] Verify async function signature
- [ ] Check Pydantic models are imported
- [ ] Verify tool function is defined after mcp instance creation

### Pagination Not Working
- [ ] Check cursor parameter is Optional[str]
- [ ] Verify try/except around cursor parsing
- [ ] Check offset calculation is correct
- [ ] Verify nextCursor generation logic
- [ ] Test with mcp-inspector tool invocation

### Logging Not Appearing
- [ ] Check LOG_LEVEL env var is set
- [ ] Verify logging.basicConfig called before logger created
- [ ] Check logger name matches module name
- [ ] Verify log level is appropriate for message level
- [ ] Check logging format includes timestamp and level

### Tests Failing
- [ ] Check pytest can import module
- [ ] Verify @pytest.mark.asyncio for async tests
- [ ] Check Pydantic models are instantiated correctly
- [ ] Verify assert statements check actual output structure
- [ ] Use pytest -v -s to see detailed output

## Template Files Quick Links

1. **skill.md** - Complete skill guide with patterns and guidelines
2. **examples.md** - Code examples and templates for common patterns
3. **checklist.md** - This file, implementation checklists and decision trees

## Quick Start Command

```bash
# 1. Create server directory
mkdir -p src/servers/my_server

# 2. Create server file from template
# Copy from examples.md - Complete Server Template

# 3. Create __main__.py
# Copy from examples.md - __main__.py Template

# 4. Create test file
# Copy from examples.md - Testing Examples

# 5. Set up environment
echo "LOG_LEVEL=INFO" > .env

# 6. Run server
python -m src.servers.my_server --log-level DEBUG

# 7. Run tests (in another terminal)
pytest tests/test_my_server.py -v

# 8. Inspect with MCP Inspector
mcp-inspector
```

