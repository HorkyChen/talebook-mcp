#!/usr/bin/env python3
"""
Talebook MCP HTTP Server - Standalone

A standalone HTTP MCP server using Server-Sent Events (SSE).
Run this server separately and connect via HTTP from MCP clients.
"""

import asyncio
import logging
import uuid
from typing import Any, Sequence

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent, InitializeResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP Server
server = Server("talebook-mcp")

# Set initialization options with session ID
def create_initialization_options():
    """Create initialization options with session ID."""
    session_id = str(uuid.uuid4())
    logger.info(f"Creating MCP server with session ID: {session_id}")

    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "talebook-mcp",
            "version": "1.0.0"
        },
        "sessionId": session_id
    }

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
        books_count = 1
        result = f"Current books count: {books_count}"
        logger.info(f"Books count requested, returning: {books_count}")
        return [TextContent(type="text", text=result)]

    except Exception as e:
        error_msg = f"Error getting books count: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

# FastAPI app
app = FastAPI(
    title="Talebook MCP HTTP Server",
    description="Standalone MCP server for book management via HTTP/SSE",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint with server info."""
    return {
        "message": "Talebook MCP HTTP Server",
        "status": "running",
        "transport": "sse",
        "endpoints": {
            "sse": "/sse",
            "health": "/"
        },
        "tools": ["get_books_count"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "server": "talebook-mcp"}

@app.post("/sse")
async def handle_sse(request: Request):
    """Handle MCP over Server-Sent Events."""
    logger.info("New SSE connection from MCP client")

    try:
        transport = SseServerTransport("/sse")

        async with transport.connect_sse(request) as streams:
            logger.info("MCP server connected via SSE transport")
            await server.run(
                streams[0],
                streams[1],
                create_initialization_options()
            )

    except Exception as e:
        logger.error(f"Error in SSE handler: {e}")
        raise

@app.get("/info")
async def server_info():
    """Get server information."""
    tools = await list_tools()
    return {
        "server_name": "talebook-mcp",
        "transport": "sse",
        "available_tools": [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in tools
        ]
    }

def main():
    """Main function to run the standalone HTTP MCP server."""
    logger.info("🚀 Starting Talebook MCP HTTP Server")
    logger.info("📡 Server-Sent Events endpoint: http://localhost:3001/sse")
    logger.info("🔍 Health check: http://localhost:3001/health")
    logger.info("ℹ️  Server info: http://localhost:3001/info")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3001,
        log_level="info"
    )

if __name__ == "__main__":
    main()
