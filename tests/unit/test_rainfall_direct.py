"""直接调用 rainfall MCP 工具查询金坛降雨情况"""

import asyncio
import os
import sys
from pathlib import Path

# 设置项目路径
sys.path.insert(0, str(Path(__file__).parent))

from flood_decision_agent.mcp.clients.base import MCPClientManager

async def main():
    print("=" * 60)
    print("调用 rainfall MCP 工具查询金坛降雨")
    print("=" * 60)
    
    # 创建 MCP 客户端管理器
    manager = MCPClientManager(auto_load_config=True)
    
    # 连接所有服务器
    print("\n[1] 连接 MCP 服务器...")
    connected = await manager.connect_all()
    print(f"    连接成功: {connected}/{len(manager.clients)}")
    
    # 获取 rainfall 客户端
    rainfall_client = manager.clients.get("rainfall")
    if not rainfall_client or not rainfall_client._connected:
        print("    ❌ rainfall 服务器未连接")
        return
    
    # 调用 get_current_rainfall 工具
    print("\n[2] 调用 get_current_rainfall 工具...")
    print("    参数: city='金坛'")
    try:
        result = await rainfall_client.call_tool(
            "get_current_rainfall",
            {"city": "金坛"}
        )
        print(f"\n    ✅ 返回结果:")
        print(f"    {result}")
    except Exception as e:
        print(f"    ❌ 工具调用失败: {e}")
    
    # 调用 get_rainfall_by_coords 工具
    print("\n[3] 调用 get_rainfall_by_coords 工具...")
    print("    参数: latitude=31.74, longitude=119.48 (金坛)")
    try:
        result = await rainfall_client.call_tool(
            "get_rainfall_by_coords",
            {"latitude": 31.74, "longitude": 119.48}
        )
        print(f"\n    ✅ 返回结果:")
        print(f"    {result}")
    except Exception as e:
        print(f"    ❌ 工具调用失败: {e}")
    
    # 获取 data_hub 客户端
    data_hub_client = manager.clients.get("data_hub")
    if data_hub_client and data_hub_client._connected:
        # 调用 get_rainfall_data 工具
        print("\n[4] 调用 data_hub.get_rainfall_data 工具...")
        print("    参数: location='金坛'")
        try:
            result = await data_hub_client.call_tool(
                "get_rainfall_data",
                {"location": "金坛"}
            )
            print(f"\n    ✅ 返回结果:")
            print(f"    {result}")
        except Exception as e:
            print(f"    ❌ 工具调用失败: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
