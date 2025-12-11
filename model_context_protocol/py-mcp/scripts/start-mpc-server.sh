#!/usr/bin/env bash
# Script to start the MCP server using FastMCP
# Usage: ./scripts/start-mpc-server.sh [server_type]

set -e

SERVER_TYPE=${1:-server}

case "$SERVER_TYPE" in
  server)
    echo "Starting FastMCP server..."
    python src/server.py
    ;;
  *)
    echo "Unknown server type: $SERVER_TYPE"
    echo "Valid types: fastmcp"
    exit 1
    ;;
esac

