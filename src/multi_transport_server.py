#!/usr/bin/env python3
"""
Talebook MCP Multi-Transport Server

支持多种流式HTTP传输协议的M        "transports": {
            "sse": "/sse",
            "websocket": "/ws",
            "simple_http": "/simple",
            "http_stream": "/stream",
            "long_polling": "/poll"
        },
- Server-Sent Events (SSE)
- WebSocket
- HTTP Chunked Transfer
- HTTP Long Polling
"""

import asyncio
import json
import logging
import uuid
from typing import Any, Sequence

import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent, InitializeResult
import httpx

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
    """Get the current count of books in the collection."""
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
    title="Talebook MCP Multi-Transport Server",
    description="MCP server supporting multiple streaming HTTP transports",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint with transport information."""
    return {
        "message": "Talebook MCP Multi-Transport Server",
        "status": "running",
        "transports": {
            "sse": "/sse",
            "websocket": "/ws",
            "http_stream": "/stream",
            "long_polling": "/poll"
        },
        "tools": ["get_books_count"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "server": "talebook-mcp"}

# 1. Server-Sent Events (SSE) Transport
@app.post("/sse")
async def handle_sse(request: Request):
    """Handle MCP over Server-Sent Events."""
    logger.info("New SSE connection from MCP client")
    try:
        transport = SseServerTransport("/sse")
        async with transport.connect_sse(request) as streams:
            logger.info("MCP server connected via SSE transport")
            await server.run(streams[0], streams[1], server.create_initialization_options())
    except Exception as e:
        logger.error(f"Error in SSE handler: {e}")
        raise

# 2. WebSocket Transport
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle MCP over WebSocket."""
    logger.info("New WebSocket connection from MCP client")
    await websocket.accept()

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            request_data = json.loads(data)
            logger.info(f"WebSocket request: {request_data}")

            # Process MCP request
            if request_data.get("method") in ["tools/list", "mcp:list-tools"]:
                tools = await list_tools()
                response = {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "result": {"tools": [{"name": t.name, "description": t.description} for t in tools]}
                }
            elif request_data.get("method") in ["tools/call", "mcp:call-tool"]:
                tool_name = request_data.get("params", {}).get("name")
                if tool_name == "get_books_count":
                    result = await get_books_count({})
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_data.get("id"),
                        "result": {"content": [{"type": "text", "text": result[0].text}]}
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_data.get("id"),
                        "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                    }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "error": {"code": -32601, "message": "Method not found"}
                }

            # Send response back to client
            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"Error in WebSocket handler: {e}")
        await websocket.close()

# 3. Simple HTTP Transport (No Streaming)
@app.post("/simple")
async def handle_simple_http(request: Request):
    """Handle MCP over simple HTTP (no streaming)."""
    logger.info("New simple HTTP request from MCP client")

    try:
        body = await request.body()
        if not body:
            return JSONResponse({"error": "No request body"}, status_code=400)

        request_data = json.loads(body)
        logger.info(f"Simple HTTP request: {request_data}")

        # Process MCP request
        if request_data.get("method") == "initialize":
            session_id = str(uuid.uuid4())
            logger.info(f"Initializing MCP session with ID: {session_id}")
            response = {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "result": {
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
            }
        elif request_data.get("method") in ["tools/list", "mcp:list-tools"]:
            tools = await list_tools()
            response = {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "result": {"tools": [{"name": t.name, "description": t.description} for t in tools]}
            }
        elif request_data.get("method") in ["tools/call", "mcp:call-tool"]:
            tool_name = request_data.get("params", {}).get("name")
            if tool_name == "get_books_count":
                result = await get_books_count({})
                response = {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "result": {"content": [{"type": "text", "text": result[0].text}]}
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {"code": -32601, "message": "Method not found"}
            }

        return JSONResponse(response)

    except Exception as e:
        logger.error(f"Error in simple HTTP handler: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)}
        }, status_code=500)

# 4. HTTP Chunked Streaming Transport
@app.post("/stream")
async def handle_http_stream(request: Request):
    """Handle MCP over HTTP streaming."""
    logger.info("New HTTP stream connection from MCP client")

    try:
        # Read request body
        body = await request.body()
        if not body:
            return JSONResponse({"error": "No request body"}, status_code=400)

        request_data = json.loads(body)
        logger.info(f"HTTP stream request: {request_data}")

        # Process MCP request
        if request_data.get("method") in ["tools/list", "mcp:list-tools"]:
            tools = await list_tools()
            response = {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "result": {"tools": [{"name": t.name, "description": t.description} for t in tools]}
            }
        elif request_data.get("method") in ["tools/call", "mcp:call-tool"]:
            tool_name = request_data.get("params", {}).get("name")
            if tool_name == "get_books_count":
                result = await get_books_count({})
                response = {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "result": {"content": [{"type": "text", "text": result[0].text}]}
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {"code": -32601, "message": "Method not found"}
            }

        # Return direct JSON response instead of streaming
        return JSONResponse(response)

    except Exception as e:
        logger.error(f"Error in HTTP stream handler: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)}
        }, status_code=500)

# 4.5. True HTTP Streaming Transport
@app.post("/true-stream")
async def handle_true_http_stream(request: Request):
    """Handle MCP over HTTP with proper streaming."""
    logger.info("New true HTTP stream connection from MCP client")

    async def generate_response():
        try:
            # Read request body
            body = await request.body()
            if not body:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error: No request body"}
                }
                yield json.dumps(error_response).encode()
                return

            request_data = json.loads(body)
            logger.info(f"True stream request: {request_data}")

            # Process MCP request
            if request_data.get("method") in ["tools/list", "mcp:list-tools"]:
                tools = await list_tools()
                response = {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "result": {"tools": [{"name": t.name, "description": t.description} for t in tools]}
                }
            elif request_data.get("method") in ["tools/call", "mcp:call-tool"]:
                tool_name = request_data.get("params", {}).get("name")
                if tool_name == "get_books_count":
                    result = await get_books_count({})
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_data.get("id"),
                        "result": {"content": [{"type": "text", "text": result[0].text}]}
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_data.get("id"),
                        "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                    }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "error": {"code": -32601, "message": "Method not found"}
                }

            # Send the response as a single chunk and close
            yield json.dumps(response).encode()

        except Exception as e:
            logger.error(f"Error in true stream handler: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)}
            }
            yield json.dumps(error_response).encode()

    return StreamingResponse(
        generate_response(),
        media_type="application/json",
        headers={
            "Connection": "close",  # 确保连接关闭
            "Cache-Control": "no-cache"
        }
    )

# 5. HTTP Long Polling Transport
polling_queues = {}

@app.post("/poll")
async def handle_long_polling(request: Request):
    """Handle MCP over HTTP long polling."""
    logger.info("New HTTP long polling connection from MCP client")

    try:
        body = await request.body()
        if not body:
            return JSONResponse({"error": "No request body"}, status_code=400)

        request_data = json.loads(body)
        logger.info(f"Long polling request: {request_data}")

        # Process MCP request immediately for this simple implementation
        if request_data.get("method") in ["tools/list", "mcp:list-tools"]:
            tools = await list_tools()
            response = {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "result": {"tools": [{"name": t.name, "description": t.description} for t in tools]}
            }
        elif request_data.get("method") in ["tools/call", "mcp:call-tool"]:
            tool_name = request_data.get("params", {}).get("name")
            if tool_name == "get_books_count":
                result = await get_books_count({})
                response = {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "result": {"content": [{"type": "text", "text": result[0].text}]}
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {"code": -32601, "message": "Method not found"}
            }

        return JSONResponse(response)

    except Exception as e:
        logger.error(f"Error in long polling handler: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)}
        }, status_code=500)

@app.get("/transports")
async def get_transports():
    """Get available transport methods."""
    return {
        "available_transports": [
            {
                "name": "sse",
                "endpoint": "/sse",
                "method": "POST",
                "description": "Server-Sent Events streaming"
            },
            {
                "name": "websocket",
                "endpoint": "/ws",
                "method": "WebSocket",
                "description": "WebSocket bidirectional streaming"
            },
            {
                "name": "simple-http",
                "endpoint": "/simple",
                "method": "POST",
                "description": "Simple HTTP (no streaming)"
            },
            {
                "name": "http-stream",
                "endpoint": "/stream",
                "method": "POST",
                "description": "HTTP JSON streaming"
            },
            {
                "name": "long-polling",
                "endpoint": "/poll",
                "method": "POST",
                "description": "HTTP long polling"
            }
        ]
    }

def main():
    """Main function to run the multi-transport HTTP MCP server."""
    logger.info("🚀 Starting Talebook MCP Multi-Transport Server")
    logger.info("📡 Server-Sent Events: http://localhost:3001/sse")
    logger.info("🔌 WebSocket: ws://localhost:3001/ws")
    logger.info("🌊 HTTP Stream: http://localhost:3001/stream")
    logger.info("🔄 Long Polling: http://localhost:3001/poll")
    logger.info("ℹ️  Transports info: http://localhost:3001/transports")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3001,
        log_level="info"
    )

if __name__ == "__main__":
    main()
