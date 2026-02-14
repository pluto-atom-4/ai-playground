"""Simple Task Server entry point.

This module allows the server to be run as:
  python -m src.servers.simple_task
"""

import sys
from src.servers.simple_task.simple_task_server import main

if __name__ == "__main__":
    sys.exit(main())
