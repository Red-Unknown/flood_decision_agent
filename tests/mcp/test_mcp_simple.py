"""简化版 MCP 测试"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flood_decision_agent.mcp.clients.base import MCPClientManager


async def test_document_server():
    """测试 Document Server"""
    print("=" * 60)
    print("测试 Document MCP Server")
    print("=" * 60)
    
    manager = MCPClientManager()
    
    # 注册 Document Server
    manager.register_server(
        name="document",
        command="python",
        args=["-m", "flood_decision_agent.mcp.servers.document_server"]
    )
    
    print("\n[1/3] 连接 Document Server...")
    try:
        connected = await asyncio.wait_for(
            manager.connect_all(),
            timeout=15.0
        )
        print(f"✓ 已连接 {connected} 个 Server")
    except asyncio.TimeoutError:
        print("✗ 连接超时")
        return
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return
    
    # 列出工具
    print("\n[2/3] 列出可用工具...")
    tools = manager.list_all_tools()
    print(f"找到 {len(tools)} 个工具:")
    for tool in tools:
        print(f"  - {tool.name}")
    
    # 测试创建文档
    print("\n[3/3] 创建示例文档...")
    try:
        result = await asyncio.wait_for(
            manager.call_tool(
                "document",
                "create_sample_docx",
                {"filename": "simple_test.docx", "title": "简单测试"}
            ),
            timeout=10.0
        )
        
        if result.get("success"):
            print(f"✓ 文档创建成功")
            print(f"  文件: {result.get('filepath')}")
        else:
            print(f"✗ 创建失败: {result.get('error')}")
    except Exception as e:
        print(f"✗ 调用失败: {e}")
    
    # 关闭
    print("\n关闭连接...")
    await manager.close_all()
    print("✓ 测试完成")


async def test_all_servers():
    """测试所有 Server"""
    print("\n" + "=" * 60)
    print("测试所有 MCP Servers")
    print("=" * 60)
    
    manager = MCPClientManager()
    
    # 注册所有 Server
    servers = [
        ("filesystem", "flood_decision_agent.mcp.servers.filesystem_server"),
        ("hydrology", "flood_decision_agent.mcp.servers.hydrology_server"),
        ("document", "flood_decision_agent.mcp.servers.document_server"),
    ]
    
    for name, module in servers:
        manager.register_server(
            name=name,
            command="python",
            args=["-m", module]
        )
    
    print(f"\n已注册 {len(servers)} 个 Server，开始连接...")
    
    try:
        connected = await asyncio.wait_for(
            manager.connect_all(),
            timeout=30.0
        )
        print(f"✓ 成功连接 {connected}/{len(servers)} 个 Server")
        
        # 列出所有工具
        tools = manager.list_all_tools()
        print(f"\n可用工具 ({len(tools)} 个):")
        for tool in tools:
            print(f"  [{tool.server_name}] {tool.name}")
        
    except asyncio.TimeoutError:
        print("✗ 连接超时")
    except Exception as e:
        print(f"✗ 连接失败: {e}")
    
    await manager.close_all()


async def main():
    print("MCP 服务简化测试")
    
    # 测试单个 Document Server
    await test_document_server()
    
    # 测试所有 Server
    await test_all_servers()
    
    print("\n" + "=" * 60)
    print("所有测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())