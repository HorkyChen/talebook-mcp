#!/usr/bin/env python3
"""
测试脚本 - 验证不同的HTTP端点
"""

import asyncio
import json
import time
import httpx

async def test_endpoint(url, method_name, description):
    """测试特定端点"""
    print(f"\n🧪 测试 {description}")
    print(f"   端点: {url}")

    request_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method_name
    }

    if method_name == "tools/call":
        request_data["params"] = {"name": "get_books_count"}

    try:
        start_time = time.time()

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json=request_data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )

        end_time = time.time()
        duration = end_time - start_time

        print(f"   状态码: {response.status_code}")
        print(f"   响应时间: {duration:.3f}s")
        print(f"   响应头: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()
            print(f"   响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
            print("   ✅ 成功")
        else:
            print(f"   ❌ 失败: {response.text}")

    except asyncio.TimeoutError:
        print("   ❌ 超时错误")
    except Exception as e:
        print(f"   ❌ 错误: {e}")

async def main():
    """主测试函数"""
    print("🔧 Talebook MCP 端点测试")
    print("=" * 50)

    base_url = "http://localhost:3001"

    # 检查服务器是否运行
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            health_response = await client.get(f"{base_url}/health")

        if health_response.status_code != 200:
            print("❌ 服务器未运行，请先启动: python multi_transport_server.py")
            return

        print("✅ 服务器运行中")

    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("请先启动服务器: python multi_transport_server.py")
        return

    # 测试不同端点
    endpoints = [
        ("/simple", "Simple HTTP"),
        ("/stream", "HTTP Stream (Fixed)"),
        ("/true-stream", "True HTTP Stream"),
        ("/poll", "Long Polling")
    ]

    for endpoint, description in endpoints:
        # 测试工具列表
        await test_endpoint(f"{base_url}{endpoint}", "tools/list", f"{description} - 列出工具")

        # 测试工具调用
        await test_endpoint(f"{base_url}{endpoint}", "tools/call", f"{description} - 调用工具")

    print("\n🏁 测试完成")

if __name__ == "__main__":
    asyncio.run(main())
