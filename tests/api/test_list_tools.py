"""检查 data_hub 工具列表"""

import asyncio
import os
import sys
from pathlib import Path

# 设置项目路径
sys.path.insert(0, str(Path(__file__).parent))

from flood_decision_agent.mcp.clients.base import MCPClientManager

async def main():
    print("=" * 60)
    print("检查 MCP 工具列表")
    print("=" * 60)
    
    # 创建 MCP 客户端管理器
    manager = MCPClientManager(auto_load_config=True)
    
    # 连接所有服务器
    await manager.connect_all()
    
    # 列出所有工具
    print("\n所有可用 MCP 工具:")
    for server_name, client in manager.clients.items():
        if client._connected:
            print(f"\n  {server_name}:")
            for tool in client.tools:
                print(f"    - {tool.name}")

if __name__ == "__main__":
    asyncio.run(main())
