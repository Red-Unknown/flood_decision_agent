"""测试 rainfall MCP 工具"""

import asyncio
import sys
sys.path.insert(0, 'f:/college/sophomore/academic')

async def main():
    from flood_decision_agent.mcp.clients.base import MCPClientManager
    
    manager = MCPClientManager(auto_load_config=True)
    await manager.connect_all()
    
    rainfall = manager.clients.get('rainfall')
    result = await rainfall.call_tool('get_current_rainfall', {'city': '金坛'})
    print('RESULT:', result)

try:
    asyncio.run(main())
except Exception as e:
    print(f'Error: {e}')
