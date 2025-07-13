#!/usr/bin/env python3
"""
Example script showing how to interact with the Talebook MCP Server
"""

import asyncio
import json
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server import server

async def demonstrate_mcp_server():
    """Demonstrate the MCP server functionality."""
    print("🔧 Talebook MCP Server Demo")
    print("=" * 40)

    # List available tools
    print("\n📋 Available Tools:")
    tools = await server._tool_handler()
    for tool in tools:
        print(f"  • {tool.name}: {tool.description}")

    # Call the get_books_count tool
    print("\n📚 Getting Books Count:")
    result = await server._call_tool_handler("get_books_count", {})
    print(f"  Result: {result[0].text}")

    print("\n✅ Demo completed!")

if __name__ == "__main__":
    asyncio.run(demonstrate_mcp_server())
