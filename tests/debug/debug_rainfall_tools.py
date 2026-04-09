"""调试 rainfall 工具"""

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
    print("调试 rainfall 工具详情")
    print("=" * 60)
    
    # 1. 创建 MCP 客户端管理器
    manager = MCPClientManager(auto_load_config=True)
    
    # 2. 连接所有服务器
    connected = await manager.connect_all()
    print(f"\n连接成功: {connected}/{len(manager.clients)}")
    
    # 3. 检查 rainfall 工具
    print("\n[rainfall 工具列表]:")
    rainfall_client = manager.clients.get("rainfall")
    if rainfall_client and rainfall_client._connected:
        tools = rainfall_client.tools
        for tool in tools:
            print(f"  - {tool.name}")
            print(f"    描述: {tool.description[:80] if tool.description else 'N/A'}...")
    else:
        print("  rainfall 未连接")
    
    # 4. 检查 data_hub 工具
    print("\n[data_hub 工具列表]:")
    data_hub_client = manager.clients.get("data_hub")
    if data_hub_client and data_hub_client._connected:
        tools = data_hub_client.tools
        for tool in tools:
            print(f"  - {tool.name}")
    else:
        print("  data_hub 未连接")
    
    # 5. 检查 decision_chain 工具
    print("\n[decision_chain 工具列表]:")
    decision_client = manager.clients.get("decision_chain")
    if decision_client and decision_client._connected:
        tools = decision_client.tools
        for tool in tools:
            print(f"  - {tool.name}")
    else:
        print("  decision_chain 未连接")

if __name__ == "__main__":
    asyncio.run(main())
