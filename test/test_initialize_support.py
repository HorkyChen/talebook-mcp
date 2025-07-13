#!/usr/bin/env python3
"""
Test Initialize Method Support

测试所有端点是否支持initialize方法
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

async def test_initialize_simple_http():
    """测试简单HTTP端点的initialize方法"""
    logger.info("Testing initialize method on Simple HTTP endpoint...")

    async with httpx.AsyncClient() as client:
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }

        response = await client.post(f"{BASE_URL}/simple", json=init_request)
        assert response.status_code == 200
        data = response.json()
        logger.info(f"Initialize response: {data}")
        assert "result" in data
        assert "sessionId" in data["result"]
        assert "protocolVersion" in data["result"]
        assert data["result"]["protocolVersion"] == "2024-11-05"

    logger.info("✅ Simple HTTP initialize test passed")

async def test_initialize_websocket():
    """测试WebSocket端点的initialize方法"""
    logger.info("Testing initialize method on WebSocket endpoint...")

    uri = "ws://localhost:3001/ws"
    async with websockets.connect(uri) as websocket:
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }

        await websocket.send(json.dumps(init_request))
        response = await websocket.recv()
        data = json.loads(response)
        logger.info(f"Initialize response: {data}")
        assert "result" in data
        assert "sessionId" in data["result"]
        assert "protocolVersion" in data["result"]
        assert data["result"]["protocolVersion"] == "2024-11-05"

    logger.info("✅ WebSocket initialize test passed")

async def test_initialize_http_stream():
    """测试HTTP Stream端点的initialize方法"""
    logger.info("Testing initialize method on HTTP Stream endpoint...")

    async with httpx.AsyncClient() as client:
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }

        response = await client.post(f"{BASE_URL}/stream", json=init_request)
        assert response.status_code == 200
        data = response.json()
        logger.info(f"Initialize response: {data}")
        assert "result" in data
        assert "sessionId" in data["result"]
        assert "protocolVersion" in data["result"]
        assert data["result"]["protocolVersion"] == "2024-11-05"

    logger.info("✅ HTTP Stream initialize test passed")

async def test_initialize_long_polling():
    """测试Long Polling端点的initialize方法"""
    logger.info("Testing initialize method on Long Polling endpoint...")

    async with httpx.AsyncClient() as client:
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }

        response = await client.post(f"{BASE_URL}/poll", json=init_request)
        assert response.status_code == 200
        data = response.json()
        logger.info(f"Initialize response: {data}")
        assert "result" in data
        assert "sessionId" in data["result"]
        assert "protocolVersion" in data["result"]
        assert data["result"]["protocolVersion"] == "2024-11-05"

    logger.info("✅ Long Polling initialize test passed")

async def test_mcp_standard_methods():
    """测试MCP标准方法名支持"""
    logger.info("Testing MCP standard method names...")

    async with httpx.AsyncClient() as client:
        # 测试 mcp:list-tools
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "mcp:list-tools",
            "params": {}
        }

        response = await client.post(f"{BASE_URL}/simple", json=list_request)
        assert response.status_code == 200
        data = response.json()
        logger.info(f"mcp:list-tools response: {data}")
        assert "result" in data
        assert "tools" in data["result"]

        # 测试 mcp:call-tool
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
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

    logger.info("✅ MCP standard methods test passed")

async def main():
    """运行所有测试"""
    logger.info("🚀 Starting initialize method tests...")

    try:
        await test_initialize_simple_http()
        await test_initialize_websocket()
        await test_initialize_http_stream()
        await test_initialize_long_polling()
        await test_mcp_standard_methods()

        logger.info("🎉 All tests passed! Initialize method and MCP standard methods are supported on all endpoints.")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
