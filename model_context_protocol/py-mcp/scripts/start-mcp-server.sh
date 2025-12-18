#!/usr/bin/env bash
# Script to start the MCP server using FastMCP
# Usage: ./scripts/start-mpc-server.sh [server_type]
#
# Available server types:
#   demo           - Main demo server with echo_string, add_numbers, get_string_length tools
#   echo           - Echo server with echo tool, resources, and prompts
#   complex_inputs - Complex inputs server with Pydantic validation for shrimp tanks and aquariums
#
# Examples:
#   ./scripts/start-mpc-server.sh demo
#   ./scripts/start-mpc-server.sh echo
#   ./scripts/start-mpc-server.sh complex_inputs

set -e

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project root
cd "$PROJECT_ROOT"

# Default server type
SERVER_TYPE=${1:-demo}

echo "=========================================="
echo "MCP FastMCP Server Launcher"
echo "=========================================="
echo "Server Type: $SERVER_TYPE"
echo "Project Root: $PROJECT_ROOT"
echo "=========================================="
echo ""

case "$SERVER_TYPE" in
  demo)
    echo "Starting Demo FastMCP server..."
    echo "Available tools:"
    echo "  - echo_string: Echo a string back to the caller"
    echo "  - add_numbers: Add two numbers together"
    echo "  - get_string_length: Get the length of a string"
    echo ""
    echo "Press CTRL+C to stop the server."
    echo ""
    python src/server.py
    ;;
  echo)
    echo "Starting Echo FastMCP server..."
    echo "Available tools:"
    echo "  - echo: Echo a string back to the caller"
    echo ""
    echo "Available resources:"
    echo "  - echo://static: Static resource endpoint"
    echo "  - echo://{text}: Template resource endpoint"
    echo ""
    echo "Available prompts:"
    echo "  - Echo: Echo prompt functionality"
    echo ""
    echo "Press CTRL+C to stop the server."
    echo ""
    python src/echo.py
    ;;
  complex_inputs)
    echo "Starting Complex Inputs FastMCP server..."
    echo "Available tools:"
    echo "  - name_shrimp: List all shrimp names in a tank with optional extra names"
    echo "  - analyze_tank: Analyze shrimp tank and return statistics"
    echo "  - configure_aquarium: Configure a complete aquarium setup"
    echo "  - find_shrimp_by_species: Find shrimp of a specific species in the tank"
    echo ""
    echo "Demonstrates:"
    echo "  - Complex Pydantic models for validation"
    echo "  - Nested models (ShrimpTank, Shrimp, FishFood, AquariumSetup)"
    echo "  - Field validation (max_length, constraints, etc.)"
    echo ""
    echo "Press CTRL+C to stop the server."
    echo ""
    python src/complex_inputs.py
    ;;
  *)
    echo "ERROR: Unknown server type: $SERVER_TYPE"
    echo ""
    echo "Available server types:"
    echo "  - demo           : Main demo server with multiple tools"
    echo "  - echo           : Echo server with resources and prompts"
    echo "  - complex_inputs : Complex inputs with Pydantic validation"
    echo ""
    echo "Usage: $0 [server_type]"
    exit 1
    ;;
esac

