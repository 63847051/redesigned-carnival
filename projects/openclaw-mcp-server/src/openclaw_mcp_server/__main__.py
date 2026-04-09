#!/usr/bin/env python3
"""
OpenClaw MCP Server - 主入口
"""

import asyncio
from openclaw_mcp_server import main

if __name__ == "__main__":
    asyncio.run(main())
