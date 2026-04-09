"""测试 MCP 服务器连接"""
import asyncio
import sys
sys.path.insert(0, '.')

from flood_decision_agent.mcp.clients.base import MCPClientManager


async def test_mcp_connection():
    """测试 MCP 连接"""
    manager = MCPClientManager()
    manager.load_from_config("configs/mcp/servers.yaml")
    
    print(f"已加载 {len(manager.clients)} 个 MCP Server")
    
    for name in manager.clients:
        print(f"\n尝试连接: {name}")
        client = manager.clients[name]
        try:
            result = await client.connect()
            if result:
                print(f"  ✅ 连接成功, 工具数: {len(client.tools)}")
                for tool in client.tools:
                    print(f"     - {tool.name}")
            else:
                print(f"  ❌ 连接失败")
        except Exception as e:
            print(f"  ❌ 异常: {type(e).__name__}: {e}")
    
    print(f"\n总连接数: {len([c for c in manager.clients.values() if c._connected])}/{len(manager.clients)}")


if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
