#!/usr/bin/env bash
# Script to run MCP Echo Server HTTP client tests
# Usage: ./scripts/test-mcp-client.sh [command] [options]
#
# Available commands:
#   list-tools       - List all available tools
#   basic            - Run basic test scenario
#   comprehensive    - Run comprehensive test scenario
#   echo-string      - Test echo_string tool
#   add-numbers      - Test add_numbers tool
#   string-length    - Test string_length tool
#   echo             - Test echo tool (echo server only)
#   curl-examples    - Show curl command examples
#
# Examples:
#   ./scripts/test-mcp-client.sh list-tools
#   ./scripts/test-mcp-client.sh basic
#   ./scripts/test-mcp-client.sh comprehensive
#   ./scripts/test-mcp-client.sh echo-string "Hello, World!"
#   ./scripts/test-mcp-client.sh add-numbers 5 3
#   ./scripts/test-mcp-client.sh string-length "hello world"

set -e

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project root
cd "$PROJECT_ROOT"

# Default values
COMMAND=${1:-basic}
SERVER_TYPE=${SERVER_TYPE:-demo}

echo "=========================================="
echo "MCP Echo Server HTTP Client"
echo "=========================================="
echo "Server Type: $SERVER_TYPE"
echo "Project Root: $PROJECT_ROOT"
echo "=========================================="
echo ""

# Function to run Python client
run_client() {
    python "clients/http_client.py" "$@"
}

case "$COMMAND" in
  list-tools)
    echo "📋 Listing available tools..."
    echo ""
    run_client --server-type "$SERVER_TYPE" --list-tools
    ;;
  basic)
    echo "🧪 Running basic test scenario..."
    echo ""
    run_client --server-type "$SERVER_TYPE" --scenario basic
    ;;
  comprehensive)
    echo "🧪 Running comprehensive test scenario..."
    echo ""
    run_client --server-type "$SERVER_TYPE" --scenario comprehensive
    ;;
  echo-string)
    MESSAGE=${2:-"Hello from client script"}
    echo "📤 Testing echo_string tool..."
    echo ""
    run_client --tool echo_string --message "$MESSAGE"
    ;;
  add-numbers)
    A=${2:-5}
    B=${3:-3}
    echo "📤 Testing add_numbers tool..."
    echo ""
    run_client --tool add_numbers --args "$A" "$B"
    ;;
  string-length)
    INPUT=${2:-"hello"}
    echo "📤 Testing get_string_length tool..."
    echo ""
    run_client --tool get_string_length --message "$INPUT"
    ;;
  echo)
    MESSAGE=${2:-"Hello from echo server"}
    echo "📤 Testing echo tool..."
    echo ""
    run_client --server-type echo --tool echo --message "$MESSAGE"
    ;;
  curl-examples)
    echo "📋 Showing curl command examples..."
    echo ""
    run_client --server-type "$SERVER_TYPE" --curl-examples
    ;;
  help|--help|-h)
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Available commands:"
    echo "  list-tools       - List all available tools"
    echo "  basic            - Run basic test scenario"
    echo "  comprehensive    - Run comprehensive test scenario"
    echo "  echo-string      - Test echo_string tool with optional message"
    echo "  add-numbers      - Test add_numbers tool with two numbers"
    echo "  string-length    - Test string_length tool with input string"
    echo "  echo             - Test echo tool (echo server only)"
    echo "  curl-examples    - Show curl command examples"
    echo "  help             - Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  SERVER_TYPE      - Server type to test (demo, echo). Default: demo"
    echo ""
    echo "Examples:"
    echo "  $0 list-tools"
    echo "  $0 basic"
    echo "  $0 comprehensive"
    echo "  $0 echo-string 'Hello, World!'"
    echo "  $0 add-numbers 5 3"
    echo "  $0 string-length 'hello world'"
    echo "  SERVER_TYPE=echo $0 echo 'Hello, Echo!'"
    echo "  SERVER_TYPE=echo $0 list-tools"
    echo ""
    ;;
  *)
    echo "❌ ERROR: Unknown command: $COMMAND"
    echo ""
    echo "Use '$0 help' for usage information"
    exit 1
    ;;
esac

