"""Simple Task Interactive Server entry point.

This module allows the server to be run as:
  python -m src.servers.simple_task_interactive

Also enables mcp-inspector discovery via:
  mcp-inspector "python -m src.servers.simple_task_interactive"
"""

import sys

from .simple_task_interactive import main

if __name__ == "__main__":
    sys.exit(main())
