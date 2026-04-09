"""测试 MCP 连接（不需要 KIMI_API_KEY）"""
import asyncio
import sys
sys.path.insert(0, '.')

from flood_decision_agent.mcp.clients.base import MCPClientManager


async def test_mcp_connection():
    """测试 MCP 连接"""
    print("=== 测试 MCP 连接 ===\n")
    
    manager = MCPClientManager()
    manager.load_from_config("configs/mcp/servers.yaml")
    
    print(f"已加载 {len(manager.clients)} 个 MCP Server: {list(manager.clients.keys())}\n")
    
    print("开始连接 MCP 服务器...\n")
    
    connected = await manager.connect_all()
    
    print(f"\n连接结果: {connected}/{len(manager.clients)}")
    
    if connected > 0:
        print("\n✅ 连接成功的服务器:")
        for name, client in manager.clients.items():
            if client._connected:
                print(f"  - {name}: {len(client.tools)} 个工具")
                for tool in client.tools:
                    print(f"      * {tool.name}")
    else:
        print("\n❌ 没有服务器连接成功")
        print("请检查错误日志")


if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
