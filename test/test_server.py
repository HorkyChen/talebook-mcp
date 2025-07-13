#!/usr/bin/env python3
"""
Test script for Talebook MCP Server
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server import get_books_count, list_tools

async def test_tools():
    """Test the available tools."""
    print("Testing Talebook MCP Server...")

    # Test list_tools
    print("\n1. Testing list_tools():")
    tools = await list_tools()
    for tool in tools:
        print(f"   - {tool.name}: {tool.description}")

    # Test get_books_count
    print("\n2. Testing get_books_count():")
    result = await get_books_count({})
    print(f"   Result: {result[0].text}")

    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_tools())
