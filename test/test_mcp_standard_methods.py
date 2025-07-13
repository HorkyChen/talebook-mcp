#!/usr/bin/env python3
"""
Test MCP-standard method names support

Test script to verify that all endpoints support both legacy and MCP-standard method names:
- "tools/list" and "mcp:list-tools"
- "tools/call" and "mcp:call-tool"
"""

import asyncio
import json
import logging
import httpx
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:3001"

async def test_simple_http():
    """Test simple HTTP endpoint with MCP-standard methods."""
    logger.info("Testing Simple HTTP endpoint with MCP-standard methods...")

    async with httpx.AsyncClient() as client:
        # Test mcp:list-tools
        list_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp:list-tools",
            "params": {}
        }

        response = await client.post(f"{BASE_URL}/simple", json=list_request)
        assert response.status_code == 200
        data = response.json()
        logger.info(f"mcp:list-tools response: {data}")
        assert "result" in data
        assert "tools" in data["result"]
        assert len(data["result"]["tools"]) > 0

        # Test mcp:call-tool
        call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "mcp:call-tool",
            "params": {
                "name": "get_books_count",
                "arguments": {}
            }
        }

        response = await client.post(f"{BASE_URL}/simple", json=call_request)
        assert response.status_code == 200
        data = response.json()
        logger.info(f"mcp:call-tool response: {data}")
        assert "result" in data
        assert "content" in data["result"]

    logger.info("✅ Simple HTTP endpoint MCP-standard methods test passed")

async def test_websocket():
    """Test WebSocket endpoint with MCP-standard methods."""
    logger.info("Testing WebSocket endpoint with MCP-standard methods...")

    uri = "ws://localhost:3001/ws"
    async with websockets.connect(uri) as websocket:
        # Test mcp:list-tools
        list_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp:list-tools",
            "params": {}
        }

        await websocket.send(json.dumps(list_request))
        response = await websocket.recv()
        data = json.loads(response)
        logger.info(f"mcp:list-tools response: {data}")
        assert "result" in data
        assert "tools" in data["result"]

        # Test mcp:call-tool
        call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "mcp:call-tool",
            "params": {
                "name": "get_books_count",
                "arguments": {}
            }
        }

        await websocket.send(json.dumps(call_request))
        response = await websocket.recv()
        data = json.loads(response)
        logger.info(f"mcp:call-tool response: {data}")
        assert "result" in data
        assert "content" in data["result"]

    logger.info("✅ WebSocket endpoint MCP-standard methods test passed")

async def test_http_stream():
    """Test HTTP Stream endpoint with MCP-standard methods."""
    logger.info("Testing HTTP Stream endpoint with MCP-standard methods...")

    async with httpx.AsyncClient() as client:
        # Test mcp:list-tools
        list_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp:list-tools",
            "params": {}
        }

        response = await client.post(f"{BASE_URL}/stream", json=list_request)
        assert response.status_code == 200
        data = response.json()
        logger.info(f"mcp:list-tools response: {data}")
        assert "result" in data
        assert "tools" in data["result"]

        # Test mcp:call-tool
        call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "mcp:call-tool",
            "params": {
                "name": "get_books_count",
                "arguments": {}
            }
        }

        response = await client.post(f"{BASE_URL}/stream", json=call_request)
        assert response.status_code == 200
        data = response.json()
        logger.info(f"mcp:call-tool response: {data}")
        assert "result" in data
        assert "content" in data["result"]

    logger.info("✅ HTTP Stream endpoint MCP-standard methods test passed")

async def test_long_polling():
    """Test Long Polling endpoint with MCP-standard methods."""
    logger.info("Testing Long Polling endpoint with MCP-standard methods...")

    async with httpx.AsyncClient() as client:
        # Test mcp:list-tools
        list_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp:list-tools",
            "params": {}
        }

        response = await client.post(f"{BASE_URL}/poll", json=list_request)
        assert response.status_code == 200
        data = response.json()
        logger.info(f"mcp:list-tools response: {data}")
        assert "result" in data
        assert "tools" in data["result"]

        # Test mcp:call-tool
        call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "mcp:call-tool",
            "params": {
                "name": "get_books_count",
                "arguments": {}
            }
        }

        response = await client.post(f"{BASE_URL}/poll", json=call_request)
        assert response.status_code == 200
        data = response.json()
        logger.info(f"mcp:call-tool response: {data}")
        assert "result" in data
        assert "content" in data["result"]

    logger.info("✅ Long Polling endpoint MCP-standard methods test passed")

async def main():
    """Run all tests."""
    logger.info("🚀 Starting MCP-standard method names tests...")

    try:
        await test_simple_http()
        await test_websocket()
        await test_http_stream()
        await test_long_polling()

        logger.info("🎉 All tests passed! MCP-standard method names are supported on all endpoints.")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
