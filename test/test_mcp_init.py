#!/usr/bin/env python3
"""
测试MCP初始化和session ID生成
"""

import asyncio
import json
import httpx

async def test_mcp_initialization():
    """测试完整的MCP初始化流程"""
    print("🔧 测试MCP初始化和Session ID生成")
    print("=" * 50)

    base_url = "http://localhost:3001"

    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. 测试初始化
        print("\n1. 🚀 测试MCP初始化")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        response = await client.post(f"{base_url}/simple", json=init_request)
        if response.status_code == 200:
            result = response.json()
            session_id = result.get("result", {}).get("sessionId")
            print(f"   ✅ 初始化成功")
            print(f"   📋 Session ID: {session_id}")
            print(f"   🔧 协议版本: {result.get('result', {}).get('protocolVersion')}")
            print(f"   🏷️  服务器信息: {result.get('result', {}).get('serverInfo')}")
        else:
            print(f"   ❌ 初始化失败: {response.text}")
            return

        # 2. 测试工具列表
        print("\n2. 📋 测试工具列表")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }

        response = await client.post(f"{base_url}/simple", json=tools_request)
        if response.status_code == 200:
            result = response.json()
            tools = result.get("result", {}).get("tools", [])
            print(f"   ✅ 获取工具列表成功")
            for tool in tools:
                print(f"   🔧 工具: {tool.get('name')} - {tool.get('description')}")
        else:
            print(f"   ❌ 获取工具列表失败: {response.text}")

        # 3. 测试工具调用
        print("\n3. 🛠️  测试工具调用")
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_books_count"
            }
        }

        response = await client.post(f"{base_url}/simple", json=call_request)
        if response.status_code == 200:
            result = response.json()
            content = result.get("result", {}).get("content", [])
            print(f"   ✅ 工具调用成功")
            for item in content:
                print(f"   📖 结果: {item.get('text')}")
        else:
            print(f"   ❌ 工具调用失败: {response.text}")

        # 4. 测试多次初始化获得不同session ID
        print("\n4. 🔄 测试多次初始化 (不同Session ID)")
        for i in range(3):
            response = await client.post(f"{base_url}/simple", json=init_request)
            if response.status_code == 200:
                result = response.json()
                session_id = result.get("result", {}).get("sessionId")
                print(f"   🆔 Session ID #{i+1}: {session_id}")
            else:
                print(f"   ❌ 初始化 #{i+1} 失败")

    print("\n🏁 测试完成!")

if __name__ == "__main__":
    asyncio.run(test_mcp_initialization())
