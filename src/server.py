#!/usr/bin/env python3
"""
Talebook MCP Server

A simple MCP server that provides book-related tools using FastAPI.
"""

import asyncio
import logging
from typing import Any, Sequence

import uvicorn
from fastapi import FastAPI
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP Server
server = Server("talebook-mcp")

# Tool definitions
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_books_count",
            description="Get the current count of books in the collection",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None = None) -> Sequence[TextContent]:
    """Handle tool calls."""
    if name == "get_books_count":
        return await get_books_count(arguments or {})
    else:
        raise ValueError(f"Unknown tool: {name}")

async def get_books_count(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """
    Get the current count of books in the collection.
    Returns 1 as default for this implementation.
    """
    try:
        # For now, return 1 as the default count
        # In a real implementation, this would query a database or file system
        books_count = 1

        result = f"Current books count: {books_count}"
        logger.info(f"Books count requested, returning: {books_count}")

        return [TextContent(type="text", text=result)]

    except Exception as e:
        error_msg = f"Error getting books count: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

# FastAPI app for HTTP interface (optional)
app = FastAPI(
    title="Talebook MCP Server",
    description="A simple MCP server for book management",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "Talebook MCP Server is running", "status": "healthy"}

@app.get("/tools")
async def get_tools():
    """Get available tools via HTTP."""
    tools = await list_tools()
    return {"tools": [{"name": tool.name, "description": tool.description} for tool in tools]}

@app.post("/tools/get_books_count")
async def http_get_books_count():
    """HTTP endpoint for getting books count."""
    result = await get_books_count({})
    return {"result": result[0].text if result else "No result"}

async def main():
    """Main function to run the MCP server."""
    # Run the MCP server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

def run_fastapi():
    """Run the FastAPI server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--fastapi":
        # Run FastAPI server
        logger.info("Starting FastAPI server on http://0.0.0.0:8000")
        run_fastapi()
    else:
        # Run MCP server with stdio
        logger.info("Starting MCP server with stdio transport")
        asyncio.run(main())
