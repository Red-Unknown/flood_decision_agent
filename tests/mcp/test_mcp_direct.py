"""测试MCP rainfall工具"""
import asyncio
import sys
sys.path.insert(0, 'src')

from flood_decision_agent.mcp.clients.base import MCPClientManager

async def test_rainfall():
    config_path = "src/flood_decision_agent/mcp/configs/mcp_servers.json"
    manager = MCPClientManager(auto_load_config=False)
    manager.load_from_config(config_path)
    
    await manager.connect_all()
    
    # 测试 rainfall 服务的 get_current_rainfall
    result = await manager.call_tool(
        server_name="rainfall",
        tool_name="get_current_rainfall",
        arguments={"city": "金坛"}
    )
    print(f"rainfall get_current_rainfall result: {result}")
    
    # 测试 data_hub 服务的 get_rainfall_data
    result2 = await manager.call_tool(
        server_name="data_hub",
        tool_name="get_rainfall_data",
        arguments={"city": "金坛"}
    )
    print(f"data_hub get_rainfall_data result: {result2}")

if __name__ == "__main__":
    asyncio.run(test_rainfall())
