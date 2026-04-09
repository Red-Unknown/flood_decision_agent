"""调试 MCP 连接状态"""

import os
import sys
import asyncio
from pathlib import Path

# 检查环境变量
if not os.environ.get("KIMI_API_KEY"):
    print("需要 kimi_api_key")
    sys.exit(1)

# 设置项目路径
sys.path.insert(0, str(Path(__file__).parent))

from flood_decision_agent.mcp.clients.base import MCPClientManager

async def main():
    print("=" * 60)
    print("调试 MCP 连接状态")
    print("=" * 60)
    
    # 1. 创建 MCP 客户端管理器
    print("\n[1] 创建 MCP 客户端管理器...")
    manager = MCPClientManager(auto_load_config=True)
    
    # 2. 连接所有服务器
    print("\n[2] 连接所有 MCP 服务器...")
    connected = await manager.connect_all()
    print(f"    连接成功: {connected}/{len(manager.clients)}")
    
    # 3. 检查每个客户端的状态
    print("\n[3] 检查客户端状态:")
    for name, client in manager.clients.items():
        is_connected = client._connected if hasattr(client, '_connected') else False
        tools_count = len(client.tools) if hasattr(client, 'tools') else 0
        print(f"    {name}:")
        print(f"      - 连接状态: {is_connected}")
        print(f"      - 工具数量: {tools_count}")
        
        # 尝试列出工具
        if is_connected and hasattr(client, 'list_tools'):
            try:
                tools = await asyncio.wait_for(client.list_tools(), timeout=5.0)
                print(f"      - 列出工具: {len(tools)} 个")
                for tool in tools[:3]:
                    print(f"        - {tool.name if hasattr(tool, 'name') else tool}")
            except Exception as e:
                print(f"      - 列出工具失败: {e}")
    
    # 4. 尝试列出所有工具
    print("\n[4] 尝试列出所有工具...")
    try:
        all_tools = manager.list_all_tools()
        print(f"    总工具数: {len(all_tools)}")
        for tool in all_tools[:10]:
            print(f"      - {tool.name if hasattr(tool, 'name') else tool}")
    except Exception as e:
        print(f"    列出工具失败: {e}")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
